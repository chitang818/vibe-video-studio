"""Inspectable stages. The Agent authors decisions; this runner validates and materializes them."""
import argparse
import copy
import difflib
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import uuid
import wave
from contextlib import contextmanager

from scripts.build_fast_project import asset_path,digest,build,preset_wave,editorial_subtitles,subtitles
from scripts.text_contract import strict_loads,validate_rows,clean,quote_at,number_tokens
from scripts.pipeline_contracts import check
from scripts.pipeline_scene import compile_scene,scene_document

ROOT=Path(__file__).resolve().parents[1]
STAGES=('intake','segment','direct','produce','assemble','review')

def read(path):return strict_loads(Path(path).read_text(encoding='utf-8-sig'))
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def fingerprint(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');os.replace(tmp,path)

def tool_identity():
    paths=['scripts/pipeline.py','scripts/pipeline_scene.py','scripts/pipeline_contracts.py','scripts/pipeline_svg.py','scripts/pipeline_inspect.py',
           'scripts/preview_template.py','scripts/build_fast_project.py','scripts/contracts.py','scripts/text_contract.py',
           'references/web-video-profile.json','references/web-video-workflow.md','assets/runtime/scene.mjs','assets/runtime/audio.mjs']
    paths += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'.agents/skills').glob('*/SKILL.md')]
    return {n:digest(ROOT/n) for n in sorted(paths) if (ROOT/n).is_file()}

@contextmanager
def locked(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True)
    lock=asset_path(root,'.pipeline.lock')
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise ValueError('Another pipeline operation is active; keep its lock and retry later')
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    try:yield root
    finally:lock.unlink()

def load_state(root):
    data=read(asset_path(root,'pipeline.json'))
    if data.get('version')!=1 or set(data)!={'version','stages','shots','requests'}:raise ValueError('Unsupported pipeline state')
    return data

def request(root,state,name,path):
    if path:
        value=read(path);check(name,value)
        namepath=f'requests/{name}-{uuid.uuid4().hex}.json';write(asset_path(root,namepath),value)
        state['requests'][name]=namepath
    if name not in state['requests']:raise ValueError(f'Missing {name} authoring input; use its stage Skill and --input, not an automatic template fallback')
    return read(asset_path(root,state['requests'][name]))

def output(root,entry):
    if not entry:return None
    return read(asset_path(root,entry['result']))

def valid_entry(root,entry,inputs):
    if not entry or entry.get('status')!='ready' or entry.get('inputFingerprint')!=fingerprint(inputs):return False
    try:return all(digest(asset_path(root,p))==h for p,h in entry['outputs'].items())
    except (OSError,ValueError):return False

def require(root,state,name):
    entry=state['stages'].get(name)
    inputs=stage_inputs(root,state,name)
    if not valid_entry(root,entry,inputs):raise ValueError(f'{name} is missing, changed or stale; rerun that stage first')
    return output(root,entry)

def source_inputs(root):
    return {str(p.relative_to(root)).replace('\\','/'):digest(p) for p in sorted((root/'sources').glob('*')) if p.is_file()}

def stage_inputs(root,state,name):
    tools=tool_identity()
    if name=='intake':return dict(sources=source_inputs(root),tools=tools)
    upstream={'segment':'intake','direct':'segment','produce':'direct','assemble':'produce','review':'assemble'}[name]
    prior=state['stages'].get(upstream,{})
    value=dict(upstream=prior.get('outputs'),upstreamValid=stage_status(root,state,upstream),tools=tools)
    key={'segment':'shots','direct':'briefs','produce':'implementation'}.get(name)
    if key and key in state['requests']:value['request']=read(asset_path(root,state['requests'][key]))
    if name in ('produce','assemble'):value['assets']=registry_inputs(root)
    if name=='produce':value['shotReceipts']={k:v.get('outputs') for k,v in state['shots'].items()}
    return value

def stage_status(root,state,name):
    entry=state['stages'].get(name)
    if not entry:return 'pending'
    if entry.get('status') in ('blocked','running'):return entry['status']
    try:return 'ready' if valid_entry(root,entry,stage_inputs(root,state,name)) else 'stale'
    except (ValueError,OSError,KeyError):return 'stale'

def registry_inputs(root):
    p=root/'assets/media-registry.json'
    if not p.exists():return {}
    entries=read(p)['assets']
    return {a['id']:dict(entry=a,actual=digest(asset_path(root,a['source']))) for a in entries}

def perform(root,state,name,operation):
    run=f'runs/{name}-{uuid.uuid4().hex}';directory=asset_path(root,run);directory.mkdir(parents=True)
    state['stages'][name]=dict(status='running',run=run)
    write(root/'pipeline.json',state)
    try:
        result=operation(directory)
        write(directory/'result.json',result)
        files={str(p.relative_to(root)).replace('\\','/'):digest(p) for p in directory.rglob('*') if p.is_file()}
        # For produce, calculate inputs only after all per-shot receipts have been updated.
        entry=dict(status='ready',run=run,result=run+'/result.json',outputs=files,inputFingerprint=fingerprint(stage_inputs(root,state,name)))
        state['stages'][name]=entry
    except Exception as exc:
        state['stages'][name]=dict(status='blocked',run=run,error=str(exc))
        write(directory/'failure.json',dict(stage=name,error=str(exc),remedy='Inspect stage inputs and rerun; completed runs and other shots remain available.'))
        raise
    finally:write(root/'pipeline.json',state)
    return result

def intake(args):
    root=Path(args.project).resolve()
    if root.exists():raise ValueError('Choose a new pipeline project directory')
    root.mkdir(parents=True);sources=root/'sources';sources.mkdir()
    for name,src in [('voice.wav',args.voice),('timestamps.json',args.timestamps),('script.txt',args.script),('style.json',args.style),('captions.json',args.captions)]:
        if src:shutil.copyfile(src,sources/name)
    state=dict(version=1,stages={},shots={},requests={})
    write(root/'pipeline.json',state)
    with locked(root):
        refresh(root,state)
        inspect(root,state)
    return root

def refresh(root,state):
    sources=root/'sources'
    def operation(directory):
        style=check('style',read(sources/'style.json'))
        with wave.open(str(sources/'voice.wav')) as audio:
            duration=round(audio.getnframes()/audio.getframerate()*1e6)
            if audio.getcomptype()!='NONE':raise ValueError('Uncompressed WAV is required')
        rows=read(sources/'timestamps.json');validate_rows(rows,duration)
        script=(sources/'script.txt').read_text(encoding='utf-8-sig');recognized=''.join(r['Char'] for r in rows)
        match=clean(script)==clean(recognized) and number_tokens(script)==number_tokens(recognized)
        differences=[dict(operation=op,script=script[a:b],recognized=recognized[c:d]) for op,a,b,c,d in difflib.SequenceMatcher(None,script,recognized).get_opcodes() if op!='equal']
        write(directory/'alignment.json',dict(semanticMatch=match,differences=differences))
        if not match:raise ValueError('Script/recognition mismatch; inspect alignment.json and supply an explicit corrected mapping without rewriting originals')
        if (sources/'captions.json').exists():editorial_subtitles(rows,read(sources/'captions.json'),duration)
        with wave.open(str(sources/'voice.wav')) as audio:
            rate=audio.getframerate();width=audio.getsampwidth();channels=audio.getnchannels()
            # Normalized sample peak envelope for timeline inspection, not a listening approval.
            peaks=[]
            for _ in range(0,audio.getnframes(),max(1,rate//4)):
                block=audio.readframes(max(1,rate//4))
                if width==2:
                    import array
                    samples=array.array('h',block);peaks.append(round(max((abs(v) for v in samples),default=0)/32768,4))
            write(directory/'waveform.json',dict(intervalSeconds=.25,channels=channels,peaks=peaks,available=width==2))
        return dict(version=1,durationUs=duration,rows=rows,style=style,alignment='alignment.json',originalHashes=source_inputs(root))
    return perform(root,state,'intake',operation)

def segment(root,state,path=None):
    source=require(root,state,'intake');spec=request(root,state,'shots',path)
    def operation(directory):
        rows=source['rows'];cursor=0;ids=set();shots=[];warnings=[]
        for s in spec['shots']:
            if s['id'] in ids:raise ValueError('Duplicate shot ID')
            ids.add(s['id'])
            if s['startIndex']!=cursor or not cursor<s['endIndex']<=len(rows):raise ValueError('Shots must cover original rows exactly, without gaps or overlaps')
            for boundary in (s['startIndex'],s['endIndex']):
                if 0<boundary<len(rows):
                    before=''.join(r['Char'] for r in rows[:boundary]);after=''.join(r['Char'] for r in rows[boundary:])
                    if before and after and before[-1].isascii() and after[0].isascii() and (before[-1].isalnum() or before[-1]=='.') and (after[0].isalnum() or after[0]=='.'):raise ValueError('Shot splits an ASCII term/number')
                    for term in source['style']['protectedTerms']:
                        for k in range(1,len(term)):
                            if before.endswith(term[:k]) and after.startswith(term[k:]):raise ValueError('Shot splits protected term: '+term)
            begin=0 if cursor==0 else round(rows[cursor]['StartSeconds']*1e6)
            end=source['durationUs'] if s['endIndex']==len(rows) else round(rows[s['endIndex']]['StartSeconds']*1e6)
            if end<=begin:raise ValueError('Cut cannot split equal timestamp rows')
            seen=[]
            for beat in s['beats']:
                idx=beat['index']
                if not cursor<=idx<s['endIndex'] or not quote_at(rows,idx,beat['quote']):raise ValueError('Beat does not match the original word within this shot')
                seen.append(idx)
            if seen!=sorted(set(seen)):raise ValueError('Beats must be unique and ordered')
            if end-begin<4000000 or end-begin>20000000:warnings.append(dict(shotId=s['id'],detail='Duration outside suggested4–20s; review semantic pacing'))
            shots.append(dict(**s,startUs=begin,endUs=end,originalText=''.join(r['Char'] for r in rows[cursor:s['endIndex']])))
            cursor=s['endIndex']
        if cursor!=len(rows):raise ValueError('Shots leave original narration uncovered')
        lines=['# 分镜表','']+[f"- {s['id']} {s['startUs']/1e6:.2f}–{s['endUs']/1e6:.2f}s：{s['goal']}\n  原文：{s['originalText']}\n  依据：{s['reason']}" for s in shots]
        (directory/'shots.md').write_text('\n'.join(lines),encoding='utf-8')
        return dict(version=1,shots=shots,warnings=warnings)
    return perform(root,state,'segment',operation)

def direct(root,state,path=None):
    shots=require(root,state,'segment')['shots'];spec=request(root,state,'briefs',path)
    if [b['shotId'] for b in spec['briefs']]!=[s['id'] for s in shots]:raise ValueError('Briefs must cover every shot in original order')
    def operation(directory):
        from scripts.pipeline_scene import SLOTS
        for brief in spec['briefs']:
            svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="#071d1b"/>', '<text x="540" y="200" text-anchor="middle" fill="#ebc86d" font-size="30">结构草图 · 非最终素材</text>']
            for item in brief['sketch']:
                if item['slot'] not in SLOTS:raise ValueError('Unknown sketch slot: '+item['slot'])
                x,y,w,h=SLOTS[item['slot']]
                if item['form']!='text':svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="#10332f" stroke="#65efb5"/>')
                svg.append(f'<text x="{x+w/2}" y="{y+h/2}" text-anchor="middle" dominant-baseline="middle" fill="#eef9f3" font-family="Microsoft YaHei" font-size="36">{html.escape(item["label"])}</text>')
            svg.append('</svg>');(directory/(brief['shotId']+'.svg')).write_text(''.join(svg),encoding='utf-8')
        return dict(version=1,briefs=spec['briefs'],warnings=[dict(shotId=b['shotId'],detail='Repeated composition description; inspect actual structure') for i,b in enumerate(spec['briefs']) if i>=2 and b['composition']==spec['briefs'][i-1]['composition']==spec['briefs'][i-2]['composition']])
    return perform(root,state,'direct',operation)

def shot_inputs(source,shot,brief,spec,assets):
    wanted={e['assetId'] for e in spec['elements'] if e['kind']=='image' and 'assetId' in e}
    return dict(source=source['originalHashes'],style=source['style'],shot=shot,brief=brief,implementation=spec,assets={k:assets.get(k) for k in sorted(wanted)},tools=tool_identity())

def produce(root,state,path=None,only=None):
    source=require(root,state,'intake');shots=require(root,state,'segment')['shots'];briefs=require(root,state,'direct')['briefs']
    spec=request(root,state,'implementation',path)
    if [s['shotId'] for s in spec['scenes']]!=[s['id'] for s in shots]:raise ValueError('Implementation must cover every shot in original order')
    if only and only not in {s['id'] for s in shots}:raise ValueError('Unknown shot ID')
    assets=registry_inputs(root);entries={k:v['entry'] for k,v in assets.items()}
    if entries:
        from scripts.media_assets import validate_registry
        validate_registry(root,[dict(id=k,source=a['source']) for k,a in entries.items()],'mixed')
    def operation(directory):
        reused=[];made=[]
        for shot,brief,implementation in zip(shots,briefs,spec['scenes']):
            sid=shot['id'];inputs=shot_inputs(source,shot,brief,implementation,assets)
            old=state['shots'].get(sid)
            if valid_entry(root,old,inputs):reused.append(sid);continue
            if only and only!=sid:continue
            folder=directory/sid;folder.mkdir()
            scene,plan,facts=compile_scene(shot,brief,implementation,source['style'],source['rows'],entries)
            timeline=[scene]
            placeholder=lambda sid,a,b:dict(id=sid,startUs=a,endUs=b,transition='fade',nodes=[dict(id='empty',type='rect',x=110,y=194,width=1,height=1,background='#071d1b',color='#071d1b')])
            if shot['startUs']:timeline.insert(0,placeholder('before-window',0,shot['startUs']))
            if shot['endUs']<source['durationUs']:timeline.append(placeholder('after-window',shot['endUs'],source['durationUs']))
            doc=scene_document(source['style'],timeline)
            # Keep original global render time, captions, background and transitions in a cropped playback window.
            from scripts.preview_template import render_html
            localrows=[]
            for row in source['rows'][shot['startIndex']:shot['endIndex']]:
                row=copy.deepcopy(row)
                row['StartSeconds']-=shot['startUs']/1e6
                row['EndSeconds']=min(row['EndSeconds']-shot['startUs']/1e6,(shot['endUs']-shot['startUs'])/1e6)
                localrows.append(row)
            doc['subtitles']=editorial_subtitles(source['rows'],read(root/'sources/captions.json'),source['durationUs']) if (root/'sources/captions.json').exists() else subtitles(source['rows'],source['durationUs'],source['style']['protectedTerms'])
            with wave.open(str(root/'sources/voice.wav')) as audio:
                params=audio.getparams();a=round(shot['startUs']/1e6*audio.getframerate());b=round(shot['endUs']/1e6*audio.getframerate());audio.setpos(a);pcm=audio.readframes(b-a)
            with wave.open(str(folder/'voice.wav'),'wb') as audio:audio.setparams(params);audio.writeframes(pcm)
            for a in entries.values():
                dest=asset_path(folder,a['source']);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset_path(root,a['source']),dest)
            content=render_html(folder,doc,1080,1920,shot['endUs']-shot['startUs'],'voice.wav',dict(version=1,events=[]),ROOT/'assets/runtime',source['style']['title'],preview_window=dict(originUs=shot['startUs'],totalDurationUs=source['durationUs'],shotIndex=shots.index(shot),shotCount=len(shots)))
            (folder/'index.html').write_text(content,encoding='utf-8')
            write(folder/'result.json',dict(scene=scene,plan=plan,facts=facts,sourceSpan=[shot['startIndex'],shot['endIndex']],localPreviewOriginUs=shot['startUs']))
            preview_check(folder,doc,shot['endUs']-shot['startUs'],shot['id'])
            files={str(p.relative_to(root)).replace('\\','/'):digest(p) for p in folder.rglob('*') if p.is_file()}
            state['shots'][sid]=dict(status='ready',result=str((folder/'result.json').relative_to(root)).replace('\\','/'),outputs=files,inputFingerprint=fingerprint(inputs))
            write(root/'pipeline.json',state);made.append(sid)
        stale=[s['id'] for s,b,i in zip(shots,briefs,spec['scenes']) if not valid_entry(root,state['shots'].get(s['id']),shot_inputs(source,s,b,i,assets))]
        signatures={}
        for shot in shots:
            receipt=state['shots'].get(shot['id'])
            if receipt and receipt.get('result'):
                data=output(root,receipt)
                signature=canonical([(n['type'],n['x'],n['y'],n['width'],n['height']) for n in data['scene']['nodes'] if n['id'] in data['plan']['roles']['content']+data['plan']['roles']['graphic']])
                signatures.setdefault(signature,[]).append(shot['id'])
        warnings=[dict(shotIds=ids,detail='Actual composition geometry repeats; inspect rhythm rather than changing family labels') for ids in signatures.values() if len(ids)>=3]
        return dict(version=1,produced=made,reused=reused,remaining=stale,warnings=warnings)
    result=perform(root,state,'produce',operation)
    if result['remaining']:
        state['stages']['produce']['status']='blocked';state['stages']['produce']['error']='Pending/stale shots: '+', '.join(result['remaining']);write(root/'pipeline.json',state)
    return result

def preview_check(folder,doc,duration,shot_id=None):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        try:
            page=browser.new_page(viewport=dict(width=440,height=956));errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto((folder/'index.html').as_uri());page.evaluate('()=>window.__vibe_ready')
            from scripts.quality_browser import GEOMETRY
            geometry=page.evaluate(GEOMETRY)
            if any(g.get('glyphClipped') or g.get('outsideDeclared') or g.get('clipped') for g in geometry):raise ValueError('Single-shot text/vector geometry fails; inspect real glyphs and bounds')
            active=next(s for s in doc['scenes'] if s['id']==shot_id) if shot_id else doc['scenes'][0]
            samples=sorted({min(duration-1,t) for t in [600000,duration//2,duration-200000]+[n.get('enterUs',0)+600000 for n in active['nodes']]})
            hashes=[]
            for t in samples:
                page.evaluate('(t)=>window.__vibe_seekTo(t)',t/1e6)
                boxes=page.evaluate('(t)=>window.__vibe_getLayout(t)',t/1e6)
                nodes={n['id']:n for n in active['nodes']}
                for i,a in enumerate(boxes):
                    for b in boxes[i+1:]:
                        panel,other=(a,b) if nodes[a['id']]['type']=='rect' else (b,a)
                        if nodes[panel['id']]['type']=='rect' and panel['x']<=other['x'] and panel['y']<=other['y'] and panel['x']+panel['width']>=other['x']+other['width'] and panel['y']+panel['height']>=other['y']+other['height'] and list(nodes).index(panel['id'])<list(nodes).index(other['id']):continue
                        dx=min(a['x']+a['width'],b['x']+b['width'])-max(a['x'],b['x']);dy=min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y'])
                        if dx>2 and dy>2:raise ValueError('Single-shot overlap: '+a['id']+' / '+b['id'])
                hashes.append(page.locator('canvas').screenshot(path=str(folder/f'frame-{t}.png')))
            page.evaluate('(t)=>window.__vibe_seekTo(t)',samples[0]/1e6)
            if page.locator('canvas').screenshot()!=hashes[0]:raise ValueError('Single-shot seek is not deterministic')
            if errors:raise ValueError('; '.join(errors))
            write(folder/'preview-check.json',dict(status='automated_pass',sampleTimesUs=samples,scope='renderer preparation and sampled seek; composition, sound and independent review separate'))
        finally:browser.close()

def assemble(root,state):
    source=require(root,state,'intake');require(root,state,'segment');require(root,state,'direct')
    produced=require(root,state,'produce')
    if produced['remaining']:raise ValueError('Some shots are still missing/stale')
    shots=output(root,state['stages']['segment'])['shots'];briefs=output(root,state['stages']['direct'])['briefs'];spec=request(root,state,'implementation',None)
    assets=registry_inputs(root)
    for shot,brief,imp in zip(shots,briefs,spec['scenes']):
        if not valid_entry(root,state['shots'].get(shot['id']),shot_inputs(source,shot,brief,imp,assets)):raise ValueError('Stale shot: '+shot['id'])
    def operation(directory):
        pieces=[output(root,state['shots'][s['id']]) for s in shots]
        doc=scene_document(source['style'],[p['scene'] for p in pieces])
        work=directory/'source';work.mkdir()
        for a in assets.values():
            dest=asset_path(work,a['entry']['source']);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset_path(root,a['entry']['source']),dest)
        if assets:shutil.copyfile(root/'assets/media-registry.json',work/'assets/media-registry.json')
        write(work/'scene.json',doc)
        events=[]
        for kind in ('whoosh','chime','ding'):
            target=work/f'assets/sounds/{kind}.wav';target.parent.mkdir(parents=True,exist_ok=True);preset_wave(target,kind)
        for s in shots[1:]:events.append(dict(timeUs=s['startUs'],source='assets/sounds/whoosh.wav',gain=.5))
        ending=[b for b in pieces[-1]['plan']['beats'] if b['timeUs']+1200000<=source['durationUs']]
        if not ending:raise ValueError('Choose an ending word event with room for the chime tail')
        events.append(dict(timeUs=ending[-1]['timeUs'],source='assets/sounds/chime.wav',gain=.5))
        events.append(dict(timeUs=pieces[len(pieces)//2]['plan']['beats'][0]['timeUs'],source='assets/sounds/ding.wav',gain=.4))
        write(work/'sfx.json',dict(version=1,events=sorted(events,key=lambda e:e['timeUs'])))
        project=directory/'project'
        build(SimpleNamespace(scene=work/'scene.json',out=project,runtime=ROOT/'assets/runtime',title=source['style']['title'],width=1080,height=1920,duration_us=None,voice=root/'sources/voice.wav',timestamps=root/'sources/timestamps.json',script=root/'sources/script.txt',caption_groups=root/'sources/captions.json' if (root/'sources/captions.json').exists() else None,sfx=work/'sfx.json',skip_browser_audit=False))
        plan=dict(version=1,profile='web-video-v1',authorId=source['style']['authorId'],contentAlign='center',background=dict(implementation='Shared deterministic background template',rationale='共用风格约定：'+source['style']['backgroundPreset']),scenes=[p['plan'] for p in pieces],facts=[f for p in pieces for f in p['facts']])
        write(project/'quality-plan.json',plan)
        provenance=project/'assets/production-provenance.json'
        write(provenance,dict(version=1,stages={k:v.get('inputFingerprint') for k,v in state['stages'].items() if k!='assemble'},shotReceipts=state['shots']))
        manifest=read(project/'vibe.project.json');manifest['assetHashes']['assets/production-provenance.json']=digest(provenance);write(project/'vibe.project.json',manifest)
        from scripts.quality_gate import initialize
        initialize(project)
        write(directory/'timeline.json',dict(version=1,durationUs=source['durationUs'],shots=[dict(id=s['id'],startUs=s['startUs'],endUs=s['endUs']) for s in shots]))
        return dict(version=1,project=str(project.relative_to(root)).replace('\\','/'),status='needs_review',scope='Assembly uses exact produced scene descriptions; run review for complete automated gate')
    return perform(root,state,'assemble',operation)

def review(root,state):
    assembled=require(root,state,'assemble')
    def operation(directory):
        from scripts.quality_gate import run_gate
        report=run_gate(asset_path(root,assembled['project']))
        write(directory/'quality-report.json',report)
        if report['errors']:raise ValueError('Full-video audit errors; inspect this run quality-report.json')
        return dict(version=1,status=report['status'],errors=report['errors'],runId=report['runId'],inputFingerprint=report['inputFingerprint'],evidenceDigest=report['evidenceDigest'])
    return perform(root,state,'review',operation)

def inspect(root,state=None):
    from scripts.pipeline_inspect import render
    state=state or load_state(root)
    statuses={name:stage_status(root,state,name) for name in STAGES}
    render(root,state,statuses)
    return statuses

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('capabilities')
    p=sub.add_parser('compare');p.add_argument('project',type=Path);p.add_argument('--left',required=True);p.add_argument('--right',required=True)
    p=sub.add_parser('intake');p.add_argument('project',type=Path)
    for name in ('script','voice','timestamps','style'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--captions',type=Path)
    for name in STAGES[1:]+('inspect','run','refresh'):
        p=sub.add_parser(name);p.add_argument('project',type=Path)
        if name in ('segment','direct','produce'):p.add_argument('--input',type=Path)
        if name=='produce':p.add_argument('--shot')
        if name=='run':p.add_argument('--from',dest='from_stage',choices=STAGES,default='segment')
    args=parser.parse_args(argv)
    if args.action=='capabilities':
        from scripts.pipeline_scene import SLOTS
        print(json.dumps(dict(version=1,renderer='shared Canvas runtime1.2.0',elements=['text','panel','image','arrow'],slots=SLOTS,assetFormats=['PNG','JPEG','WebP','restricted static SVG -> PNG'],entrances=['fade-up','slide-left','slide-right','zoom'],externalSearch='Agent tool and permission dependent; not built into CLI',externalGenerate='Agent tool and permission dependent; not built into CLI'),ensure_ascii=False,indent=2));return
    if args.action=='intake':intake(args);print(str(args.project.resolve()/'index.html'));return
    with locked(args.project) as root:
        state=load_state(root)
        try:
            if args.action=='compare':
                left=read(asset_path(root,args.left));right=read(asset_path(root,args.right))
                diff='\n'.join(difflib.unified_diff(json.dumps(left,ensure_ascii=False,indent=2).splitlines(),json.dumps(right,ensure_ascii=False,indent=2).splitlines(),fromfile=args.left,tofile=args.right))
                target=root/'comparisons'/('compare-'+uuid.uuid4().hex+'.html');target.parent.mkdir(exist_ok=True)
                target.write_text('<!doctype html><meta charset="utf-8"><title>阶段差异</title><pre>'+html.escape(diff or 'No data differences')+'</pre>',encoding='utf-8')
                result=dict(comparison=str(target))
            elif args.action=='inspect':result=inspect(root,state)
            elif args.action=='run':
                result={}
                for name in STAGES[STAGES.index(args.from_stage):]:
                    if stage_status(root,state,name)=='ready':result[name]='reused';continue
                    result[name]=(refresh if name=='intake' else globals()[name])(root,state)
            else:result=globals()[args.action](root,state,getattr(args,'input',None),getattr(args,'shot',None)) if args.action=='produce' else globals()[args.action](root,state,getattr(args,'input',None)) if args.action in ('segment','direct') else globals()[args.action](root,state)
        finally:inspect(root,state)
    def compact_value(value):
        if isinstance(value,dict):return {k:(f'{len(v)} items; full data in stage result.json' if k in ('rows','shots','briefs') and isinstance(v,list) else compact_value(v)) for k,v in value.items()}
        return value
    compact=compact_value(result)
    print(json.dumps(compact,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
