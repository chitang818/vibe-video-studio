"""Browser evidence for Canvas projects; no changes to the shared renderer."""
import hashlib
import json
import re
import base64
import sys
import os
import importlib.metadata


AUDIO_PROBE = r'''(() => {
 const connect=AudioNode.prototype.connect, create=AudioContext.prototype.createMediaElementSource;
 window.__qualityMeters=[];
 function meter(source,kind){const a=source.context.createAnalyser();a.fftSize=2048;
   connect.call(source,a);window.__qualityMeters.push({kind,analyser:a});return a;}
 AudioNode.prototype.connect=function(target,...rest){
   if(target instanceof AudioDestinationNode){const a=meter(this,'output');return connect.call(a,target,...rest);}
   return connect.call(this,target,...rest);
 };
 AudioContext.prototype.createMediaElementSource=function(audio){const s=create.call(this,audio);meter(s,'voice');return s;};
 window.__qualityLevels=()=>window.__qualityMeters.map(m=>{const a=new Float32Array(m.analyser.fftSize);
   m.analyser.getFloatTimeDomainData(a);return {kind:m.kind,rms:Math.sqrt(a.reduce((s,v)=>s+v*v,0)/a.length)};});
})();'''


BACKGROUND_PROBE = r'''async (policy={}) => {
 policy=policy??{};
 const original=window.__vibe_scene,bg=original.background??{},main=document.querySelector('canvas');
 const source=document.createElement('canvas'),small=document.createElement('canvas');small.width=270;small.height=480;
 const c=small.getContext('2d',{willReadFrequently:true});c.fillStyle=bg.color??'#070d12';c.fillRect(0,0,270,480);
 const base=c.getImageData(0,0,1,1).data,columns=policy.columns??4,rows=policy.rows??6,minimum=policy.minPixelsPerCell??16;
 const duration=config.durationUs;
 const data={background:structuredClone(bg),scenes:[{id:'background-probe',startUs:0,endUs:duration,nodes:[{id:'probe',type:'rect',x:0,y:0,width:1,height:1,background:bg.color??'#070d12',color:bg.color??'#070d12'}]}]};
 const r=await prepareScene(source,data,{width:main.width,height:main.height,durationUs:duration,assetBase:config.assetBase,safeArea:false});
 const sample=t=>{r.renderAt(t);c.drawImage(source,0,0,270,480);return c.getImageData(0,0,270,480).data;};
 const first=sample(0),last=sample(Math.min(duration-1,4000000));let visiblePixels=0,changedPixels=0;
 for(let i=0;i<last.length;i+=4){
  if(Math.abs(first[i]-base[0])+Math.abs(first[i+1]-base[1])+Math.abs(first[i+2]-base[2])>12)visiblePixels++;
  if(Math.abs(first[i]-last[i])+Math.abs(first[i+1]-last[i+1])+Math.abs(first[i+2]-last[i+2])>12)changedPixels++;
 }
 const coverage=[];
 for(const t of [...new Set([0,Math.min(duration-1,4000000),Math.floor(duration/2)])]){
  const pixels=sample(t),counts=Array(columns*rows).fill(0),regions=(policy.regions??[]).map(x=>({name:x.name,visiblePixels:0}));
  for(let y=0;y<480;y++)for(let x=0;x<270;x++){
   const i=(y*270+x)*4;if(Math.abs(pixels[i]-base[0])+Math.abs(pixels[i+1]-base[1])+Math.abs(pixels[i+2]-base[2])>12){counts[Math.floor(y/(480/rows))*columns+Math.floor(x/(270/columns))]++;(policy.regions??[]).forEach((r,j)=>{const [a,b,w,h]=r.box;if(x>=a*270&&x<(a+w)*270&&y>=b*480&&y<(b+h)*480)regions[j].visiblePixels++;});}
  }
  coverage.push({timeUs:t,coveredCells:counts.filter(n=>n>=minimum).length,cellPixels:counts,regions});
 }
 return {preset:bg.preset??'legacy',visiblePixels,changedPixels,columns,rows,coverage};
}''';


GEOMETRY = r'''() => {
 const scene=window.__vibe_scene,w=document.querySelector('canvas').width,h=document.querySelector('canvas').height;
 const layer=document.createElement('canvas'),pad=128,result=[];
 for(const s of scene.scenes) for(const n of s.nodes){
   const b={id:n.id,type:n.type,x:n.x,y:n.y,width:n.width,height:n.height};
   if(n.type==='path'){
     layer.width=Math.ceil(n.width)+pad*2;layer.height=Math.ceil(n.height)+pad*2;
     const c=layer.getContext('2d',{willReadFrequently:true});c.translate(pad,pad);c.fill(new Path2D(n.path));
     const pixels=c.getImageData(0,0,layer.width,layer.height).data;
     let x0=layer.width,y0=layer.height,x1=-1,y1=-1,paintedPixels=0;
     for(let y=0;y<layer.height;y++)for(let x=0;x<layer.width;x++)if(pixels[(y*layer.width+x)*4+3]){
       if(pixels[(y*layer.width+x)*4+3]>127)paintedPixels++;
       x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
     b.paintedPixels=paintedPixels;
     if(x1>=0){b.actual={x:n.x+x0-pad,y:n.y+y0-pad,width:x1-x0+1,height:y1-y0+1};
       b.outsideDeclared=x0<pad||y0<pad||x1>=pad+n.width||y1>=pad+n.height;
       b.clipped=x0===0||y0===0||x1===layer.width-1||y1===layer.height-1;}
   }
   if(n.type==='text'){
     const p=prepareTextLayer(n,w),pad=32,reference=document.createElement('canvas');
     const actual=window.__vibe_textRaster(s.id,n.id);
     reference.width=actual.width+pad*2;reference.height=actual.height+pad*2;
     const c=reference.getContext('2d',{willReadFrequently:true});c.font=p.font;c.textBaseline=p.textBaseline;c.fillStyle=n._color??n.color??'#e8f1ec';
     p.lines.forEach((line,i)=>c.fillText(line,pad+p.origins[i].x,pad+p.origins[i].y));
     const ref=c.getImageData(0,0,reference.width,reference.height).data;
     let x0=reference.width,y0=reference.height,x1=-1,y1=-1,mismatch=0;
     for(let y=0;y<reference.height;y++)for(let x=0;x<reference.width;x++)if(ref[(y*reference.width+x)*4+3]){
       x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y);}
     for(let y=0;y<actual.height;y++)for(let x=0;x<actual.width;x++)
       if(Math.abs(actual.data[(y*actual.width+x)*4+3]-ref[((y+pad)*reference.width+x+pad)*4+3])>1)mismatch++;
     b.lines=p.lines;b.inkRects=p.inkRects;b.glyphMismatchPixels=mismatch;
     b.glyphClipped=x0<pad||y0<pad||x1>=pad+actual.width||y1>=pad+actual.height||mismatch>0;
     if(x1>=0)b.actual={x:n.x+x0-pad,y:n.y+y0-pad,width:x1-x0+1,height:y1-y0+1};
   }
   result.push({sceneId:s.id,...b});
 }
 return result;
}'''


MOTION = r'''async plan => {
 const original=structuredClone(window.__vibe_scene),main=document.querySelector('canvas');
 const source=document.createElement('canvas'),small=document.createElement('canvas');small.width=270;small.height=480;
 const c=small.getContext('2d',{willReadFrequently:true}),result=[];
 for(const s of original.scenes){
   const p=plan.scenes?.find(p=>p.sceneId===s.id);if(!p)continue;
   const ids=[...(p.roles.content??[]),...(p.roles.graphic??[])];
   const nodes=s.nodes.filter(n=>ids.includes(n.id));if(!nodes.length)continue;
   const data={background:{color:'#071d1b',particles:false},scenes:[{id:s.id,startUs:0,endUs:s.endUs-s.startUs,nodes}]};
   const renderer=await prepareScene(source,data,{width:main.width,height:main.height,durationUs:s.endUs-s.startUs,assetBase:config.assetBase,inlineImages:config.inlineImages,safeArea:true});
   let previous=null,frozen=0,maxFrozen=0;
   for(let t=500000;t<s.endUs-s.startUs;t+=500000){
     renderer.renderAt(t);c.drawImage(source,0,0,270,480);const pixels=c.getImageData(0,0,270,480).data;
     let changed=0;if(previous)for(let i=0;i<pixels.length;i+=4)if(Math.abs(pixels[i]-previous[i])+Math.abs(pixels[i+1]-previous[i+1])+Math.abs(pixels[i+2]-previous[i+2])>12)changed++;
     frozen=previous&&changed<16?frozen+500000:0;maxFrozen=Math.max(maxFrozen,frozen);previous=pixels;
   }
   const events=[];
   if(plan.profile==='presentation-portrait-v1')for(const beat of p.beats){
     const selected=nodes.filter(n=>beat.nodeIds.includes(n.id));
     const eventRenderer=await prepareScene(source,{background:{color:'#071d1b',particles:false},scenes:[{id:s.id,startUs:0,endUs:s.endUs-s.startUs,nodes:selected}]},{width:main.width,height:main.height,durationUs:s.endUs-s.startUs,assetBase:config.assetBase,inlineImages:config.inlineImages,safeArea:true});
     const t=beat.timeUs-s.startUs;
     eventRenderer.renderAt(Math.max(0,t-1));c.drawImage(source,0,0,270,480);const before=c.getImageData(0,0,270,480).data;
     eventRenderer.renderAt(Math.min(s.endUs-s.startUs-1,t+600000));c.drawImage(source,0,0,270,480);const after=c.getImageData(0,0,270,480).data;
     let changed=0;for(let j=0;j<before.length;j+=4)if(Math.abs(before[j]-after[j])+Math.abs(before[j+1]-after[j+1])+Math.abs(before[j+2]-after[j+2])>12)changed++;
     events.push({timeUs:beat.timeUs,nodeIds:beat.nodeIds,changedPixels:changed});
   }
   result.push({sceneId:s.id,maxFrozenUs:maxFrozen,events});
 }
 return result;
}'''


def inspect_browser(root, manifest, scene, plan, output):
    from playwright.sync_api import sync_playwright
    from scripts.build_fast_project import digest
    errors, screenshots, console_errors = [], [], []
    frames = output/'frames'; frames.mkdir(exist_ok=True)

    def error(rule, detail, sid=None):
        errors.append(dict(rule=rule, detail=detail, sceneId=sid))

    # Inline renderer must be exactly the shared source. Preview wrapper may differ.
    html = (root/manifest['htmlFile']).read_text(encoding='utf-8')
    from scripts.preview_template import canonical_html
    if html != canonical_html(root,manifest):
        error('RUNTIME','Executable HTML differs from the complete canonical preview template; untrusted HTML was not executed')
        return dict(browserErrors=errors,screenshots=[])
    from scripts.contracts import validate_document
    try:
        validate_document('scene',scene);validate_document('quality-plan',plan)
    except ValueError as exc:
        return dict(browserErrors=[dict(rule='SCHEMA',detail=str(exc))],screenshots=[])

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={'width': manifest['width'], 'height': manifest['height']})
            def restrict(route):
                url=route.request.url
                if url.startswith(root.as_uri()+'/') or url.startswith('data:'):
                    route.continue_()
                else:
                    console_errors.append('Blocked external resource: '+url);route.abort()
            page.route('**/*',restrict)
            page.add_init_script(AUDIO_PROBE)
            page.on('pageerror', lambda e: console_errors.append(str(e)))
            page.on('console', lambda m: console_errors.append(m.text) if m.type == 'error' or 'CORS' in m.text or 'outputs zeroes' in m.text else None)
            page.goto((root/manifest['htmlFile']).as_uri(), timeout=20000)
            page.evaluate('''()=>Promise.race([window.__vibe_ready,new Promise((_,r)=>setTimeout(()=>r(Error('Readiness timeout')),15000))])''')
            actual = page.evaluate('window.__vibe_scene')
            preview = page.evaluate('({sounds:config.sounds,inlineSounds:config.inlineSounds})')
            track = json.loads((root/manifest['sfxFile']).read_text(encoding='utf-8-sig'))
            if preview['sounds'] != track:
                error('IDENTITY', 'Inline sounds differ from sfx.json')
            for source in {e['source'] for e in track['events']}:
                encoded = preview.get('inlineSounds', {}).get(source, '')
                if not encoded.startswith('data:audio/wav;base64,') or hashlib.sha256(base64.b64decode(encoded.split(',',1)[1], validate=True)).hexdigest()!=digest(root/source):
                    error('IDENTITY','Inline sound differs from source WAV: '+source)
            inline_images=page.evaluate('config.inlineImages??{}')
            for source in {n['source'] for sh in scene['scenes'] for n in sh['nodes'] if n['type']=='image'}:
                encoded=inline_images.get(source,'')
                if not encoded.startswith('data:image/') or hashlib.sha256(base64.b64decode(encoded.split(',',1)[1],validate=True)).hexdigest()!=digest(root/source):error('IDENTITY','Inline image differs from registered source: '+source)
            if manifest.get('voiceFile'):
                encoded = page.locator('audio').get_attribute('src') or ''
                if not encoded.startswith('data:audio/wav;base64,'):
                    error('AUDIO', 'file:// preview voice must embed the original WAV bytes')
                elif hashlib.sha256(base64.b64decode(encoded.split(',',1)[1],validate=True)).hexdigest()!=digest(root/manifest['voiceFile']):
                    error('IDENTITY','Inline voice differs from original WAV')
            def strip_private(v):
                if isinstance(v, dict): return {k:strip_private(x) for k,x in v.items() if not k.startswith('_')}
                if isinstance(v, list): return [strip_private(x) for x in v]
                return v
            if strip_private(actual) != scene:
                error('IDENTITY', 'Inline scene differs from scene.json')
            geometry = page.evaluate(GEOMETRY)
            from scripts.background_library import preset as background_preset,background_errors
            background_entry=background_preset(scene['background']['preset']) if scene.get('background',{}).get('preset') else None
            background=page.evaluate(BACKGROUND_PROBE,background_entry['qa'] if background_entry else {})
            if plan.get('profile')=='presentation-portrait-v1' and background_entry:
                for rule,detail in background_errors(background,background_entry):error(rule,detail)
            motion = page.evaluate(MOTION,plan)
            for sample in motion:
                for event in sample.get('events',[]):
                    if event['changedPixels']<16:error('EVENT','Planned presentation event has no visible change: '+str(event['timeUs']),sample['sceneId'])
                if plan.get('profile')!='presentation-portrait-v1' and sample['maxFrozenUs']>=2000000:
                    error('MOTION','Content pixels remain static for >=2s in the isolated 0.5s sampling',sample['sceneId'])
            plans = {p.get('sceneId'): p for p in plan.get('scenes', [])}
            for g in geometry:
                if plan.get('profile')=='presentation-portrait-v1' and g['type']=='text':
                    node=next(n for sh in scene['scenes'] if sh['id']==g['sceneId'] for n in sh['nodes'] if n['id']==g['id'])
                    ink=g.get('inkRects',[])
                    if node.get('align')=='center' and any(abs(b['x']+b['width']/2-node['width']/2)>1 for b in ink):error('ALIGNMENT','Actual line ink is not horizontally centred: '+g['id'],g['sceneId'])
                    if node.get('verticalAlign')=='center' and ink:
                        top=min(b['y'] for b in ink);bottom=max(b['y']+b['height'] for b in ink)
                        if abs((top+bottom)/2-node['height']/2)>1:error('ALIGNMENT','Actual ink block is not vertically centred: '+g['id'],g['sceneId'])
                if g.get('glyphClipped'):
                    error('TEXT_CLIP','Actual text cache loses glyph pixels: '+g['id'],g['sceneId'])
                if g.get('outsideDeclared') or g.get('clipped'):
                    error('GEOMETRY', 'Vector pixels escape declared box: '+g['id'], g['sceneId'])
                if g['type']=='path' and g.get('paintedPixels',0)<64:
                    error('VISIBILITY','Empty or imperceptible vector: '+g['id'],g['sceneId'])
                role=plans.get(g['sceneId'],{}).get('roles',{})
                if g['type']=='text' and g['id'] in role.get('title',[]):
                    node=next(n for s in scene['scenes'] if s['id']==g['sceneId'] for n in s['nodes'] if n['id']==g['id'])
                    if len(g['lines'])!=len(node['text'].split('\n')):
                        error('TITLE','Work title wrapped without explicit semantic lines',g['sceneId'])
            # Collision candidates include transformed boxes at every entry, midpoint and end.
            # Panel backgrounds are intentionally containing other nodes; all other overlaps need review.
            for s in scene['scenes']:
                nodes = {n['id']: n for n in s['nodes']}
                from scripts.quality_gate import card_panel_ids,card_spacing_failures
                from scripts.contracts import load_profile
                spacing=load_profile(plan.get('profile','knowledge-portrait-v1')).get('cardSpacing')
                card_ids=card_panel_ids(nodes,plans.get(s['id'],{}).get('roles',{})) if spacing else set()
                groups = plans.get(s['id'], {}).get('intentionalOverlaps', [])
                allowed = {frozenset(g.get('nodeIds', [])) for g in groups}
                times = {s['startUs'], s['endUs']-1, (s['startUs']+s['endUs'])//2}
                if s.get('transition'):times.update(min(s['endUs']-1,s['startUs']+d) for d in (50000,120000,240000))
                if s!=scene['scenes'][-1]:times.update(max(s['startUs'],s['endUs']-d) for d in (160000,80000))
                for n in s['nodes']:
                    t = s['startUs']+n.get('enterUs', 0)
                    if n.get('emphasis'):
                        et=s['startUs']+n['emphasis']['timeUs'];times.update([et,min(s['endUs']-1,et+175000),min(s['endUs']-1,et+350000)])
                    times.update([min(s['endUs']-1,t+225000),max(s['startUs'], t-1), min(s['endUs']-1, t+1), min(s['endUs']-1,t+500000)])
                seen = set()
                for t in sorted(times):
                    boxes = page.evaluate('(t)=>window.__vibe_getLayout(t)', t/1e6)
                    if spacing:
                        for detail in card_spacing_failures([b for b in boxes if b['id'] in card_ids],spacing['minimumGapPx']):
                            error('CARD_SPACING',f'{t}us: '+detail,s['id'])
                    for i,a in enumerate(boxes):
                        for b in boxes[i+1:]:
                            pair = frozenset((a['id'],b['id']))
                            if pair in seen or pair in allowed: continue
                            ta,tb=nodes[a['id']]['type'],nodes[b['id']]['type']
                            if ta=='rect' or tb=='rect':
                                rect,other=(a,b) if ta=='rect' else (b,a)
                                panel_ids=plans.get(s['id'],{}).get('roles',{}).get('panel',[])
                                contained=(rect['x']<=other['x'] and rect['y']<=other['y'] and rect['x']+rect['width']>=other['x']+other['width'] and rect['y']+rect['height']>=other['y']+other['height'])
                                if rect['id'] in panel_ids and contained and list(nodes).index(rect['id'])<list(nodes).index(other['id']):
                                    continue
                            elif 'text' not in (ta,tb):
                                continue
                            # Broad vector boxes may intentionally contain labels; never silently ignore them.
                            dx=min(a['x']+a['width'],b['x']+b['width'])-max(a['x'],b['x'])
                            dy=min(a['y']+a['height'],b['y']+b['height'])-max(a['y'],b['y'])
                            if dx>2 and dy>2:
                                seen.add(pair);error('COLLISION', f"Review overlap {a['id']} / {b['id']}",s['id'])
                # Ordered seek checks deterministic output including before/after cuts.
                captures = sorted(times)
                for t in captures:
                    page.evaluate('(t)=>window.__vibe_seekTo(t)',t/1e6)
                    expected='第 '+str(scene['scenes'].index(s)+1)+' / '+str(len(scene['scenes']))+' 节'
                    if page.locator('#chapText').inner_text()!=expected or page.locator('#chapText').get_attribute('data-scene-id')!=s['id']:
                        error('HUD','Counter does not match the current original-word scene boundary',s['id'])
                    name=f"frames/{s['id']}-{t}.png";path=output/name
                    page.locator('canvas').screenshot(path=str(path))
                    screenshots.append(dict(file=name,sha256=digest(path),sceneId=s['id'],timeUs=t,viewport='1080x1920'))
                t=min(s['endUs']-1,s['startUs']+800000)
                page.evaluate('(t)=>window.__vibe_seekTo(t)',t/1e6)
                first=page.locator('canvas').screenshot()
                page.evaluate('(t)=>window.__vibe_seekTo(t)',(s['endUs']-1)/1e6)
                page.evaluate('(t)=>window.__vibe_seekTo(t)',t/1e6)
                if page.locator('canvas').screenshot()!=first:
                    error('DETERMINISM','Repeated seek produced a different image',s['id'])
            page.set_viewport_size({'width':440,'height':956})
            for s in scene['scenes']:
                t=min(s['endUs']-1,s['startUs']+1000000)
                page.evaluate('(t)=>window.__vibe_seekTo(t)',t/1e6)
                name=f"frames/{s['id']}-mobile.png";page.screenshot(path=str(output/name))
                screenshots.append(dict(file=name,sha256=digest(output/name),sceneId=s['id'],timeUs=t,viewport='440x956'))
            button=page.locator('button');bounds=button.bounding_box()
            if not bounds or bounds['x']<0 or bounds['y']<0 or bounds['x']+bounds['width']>440 or bounds['y']+bounds['height']>956:
                error('PLAYER','Playback control is outside the mobile viewport')
            hud=page.evaluate('''()=>{const c=document.querySelector('canvas').getBoundingClientRect(),h=document.querySelector('#chapText').getBoundingClientRect();
                return {top:(h.top-c.top)/c.height,left:(h.left-c.left)/c.width,bottom:(h.bottom-c.top)/c.height,right:(h.right-c.left)/c.width,
                    font:parseFloat(getComputedStyle(document.querySelector('#chapText')).fontSize)/c.width};}''')
            from scripts.contracts import load_profile
            baseline=load_profile()['devHud']
            if abs(hud['top']-baseline['topRatio'])>.002 or abs(hud['left']-baseline['leftRatio'])>.002 or abs(hud['font']-baseline['fontRatio'])>.002 or hud['bottom']>=.10 or hud['right']>.40:
                error('HUD','Dev counter must stay in the top-left preview blind zone')
            # Probe both sides of every cut, including backwards seeks.
            for i,s in enumerate(scene['scenes'][1:],1):
                for t,expected_id in [(s['startUs'],s['id']),(s['startUs']-1,scene['scenes'][i-1]['id'])]:
                    page.evaluate('(t)=>window.__vibe_seekTo(t)',t/1e6)
                    if page.locator('#chapText').get_attribute('data-scene-id')!=expected_id:error('HUD','Counter changes on the wrong cut boundary')
            levels=[]
            if manifest.get('voiceFile'):
                rows=json.loads((root/manifest['timestampsFile']).read_text(encoding='utf-8-sig'))
                # Choose spoken character windows near the beginning and middle, not quiet padding.
                for row in [rows[min(5,len(rows)-1)],rows[len(rows)//2]]:
                    page.evaluate('(t)=>window.__vibe_seekTo(t)',float(row['StartSeconds']))
                    button.click(timeout=3000)
                    before=page.locator('audio').evaluate('(a)=>a.currentTime')
                    for _ in range(8):
                        page.wait_for_timeout(100);levels.extend(page.evaluate('window.__qualityLevels()'))
                    after=page.locator('audio').evaluate('(a)=>({time:a.currentTime,paused:a.paused,error:a.error?.message})')
                    button.click(timeout=3000)
                    if after['paused'] or after['time']<=before or after.get('error'):
                        error('AUDIO','Playback clock did not advance normally')
                for kind in ('voice','output'):
                    if max((l['rms'] for l in levels if l['kind']==kind),default=0)<=.0001:
                        error('AUDIO','No nonzero '+kind+' signal; currentTime alone is not audio proof')
                paused_before=page.locator('audio').evaluate('(a)=>a.currentTime')
                page.wait_for_timeout(150)
                if abs(page.locator('audio').evaluate('(a)=>a.currentTime')-paused_before)>.02:
                    error('PLAYER','Paused playback clock continues to advance')
                page.evaluate('(t)=>window.__vibe_seekTo(t)',manifest['durationUs']/1e6-.08)
                button.click(timeout=3000);page.wait_for_timeout(400)
                if not page.locator('audio').evaluate('(a)=>a.paused'):error('PLAYER','Voice did not stop at the end')
                button.click(timeout=3000);page.wait_for_timeout(200)
                replay=page.locator('audio').evaluate('(a)=>({time:a.currentTime,paused:a.paused})')
                if replay['paused'] or not 0<replay['time']<1 or page.locator('#chapText').get_attribute('data-scene-id')!=scene['scenes'][0]['id']:
                    error('PLAYER','Replay did not reset the first scene, captions and voice clock')
                button.click(timeout=3000)
            progress_checks=[]
            slider=page.locator('#seek')
            if slider.count()!=1 or page.locator('#time').count()!=1:
                error('PLAYER','Visible progress slider and elapsed/total time are required')
            else:
                for width,height in [(320,640),(440,956)]:
                    page.set_viewport_size(dict(width=width,height=height))
                    boxes={key:page.locator(key).bounding_box() for key in ('#controls','#seek','#time','button','canvas')}
                    for key in ('#controls','#seek','#time','button'):
                        b=boxes[key]
                        if not b or b['width']<=0 or b['height']<=0 or b['x']<0 or b['y']<0 or b['x']+b['width']>width+.5 or b['y']+b['height']>height+.5:
                            error('PLAYER','Progress controls escape the mobile viewport: '+key)
                    if boxes['#controls']['y']<boxes['canvas']['y']+boxes['canvas']['height']:
                        error('PLAYER','Progress controls cover the video canvas/subtitles')
                    if boxes['#seek']['height']<44 or boxes['button']['height']<44:
                        error('PLAYER','Playback controls need a 44px touch target')
                    progress_checks.append(dict(viewport=f'{width}x{height}',boxes=boxes))
                duration=manifest['durationUs']/1e6
                if abs(float(slider.get_attribute('max'))-duration)>.001:error('PLAYER','Progress duration differs from the WAV clock')
                page.evaluate('window.__vibe_seekTo(0)')
                bar=slider.bounding_box();cy=bar['y']+bar['height']/2
                page.mouse.click(bar['x']+bar['width']/2,cy)
                selected=float(slider.input_value())
                if abs(selected-duration/2)>.1 or (manifest.get('voiceFile') and abs(page.locator('audio').evaluate('(a)=>a.currentTime')-selected)>.05):
                    error('PLAYER','Clicking progress does not seek both picture and voice to the selected time')
                page.wait_for_timeout(150)
                if manifest.get('voiceFile') and (not page.locator('audio').evaluate('(a)=>a.paused') or abs(page.locator('audio').evaluate('(a)=>a.currentTime')-selected)>.05):
                    error('PLAYER','Paused seeking unexpectedly starts or advances voice')
                slider.focus();slider.press('End')
                if float(slider.input_value())<duration-.05 or page.locator('#chapText').get_attribute('data-scene-id')!=scene['scenes'][-1]['id']:
                    error('PLAYER','Keyboard End does not reach the final scene')
                slider.press('Home')
                if float(slider.input_value())!=0 or not page.locator('#time').inner_text().startswith('00:00'):
                    error('PLAYER','Keyboard Home does not reset the time display')
                if manifest.get('voiceFile'):
                    button.click(timeout=3000);page.wait_for_timeout(150)
                    bar=slider.bounding_box();cy=bar['y']+bar['height']/2
                    page.mouse.move(bar['x']+bar['width']/2,cy);page.mouse.down()
                    page.mouse.move(bar['x']+bar['width']*.25,cy,steps=4);page.mouse.up();page.wait_for_timeout(100)
                    try:
                        page.wait_for_function('''()=>{const a=document.querySelector('audio'),v=Number(document.querySelector('#seek').value);
                            return !a.paused&&Math.abs(a.currentTime-v)<.08;}''',timeout=1500)
                    except Exception:
                        error('PLAYER','Progress and voice did not converge after dragging')
                    state=page.evaluate('''()=>({value:Number(document.querySelector('#seek').value),time:document.querySelector('audio').currentTime,paused:document.querySelector('audio').paused})''')
                    selected=state['value'];clock=state
                    if clock['paused'] or abs(clock['time']-selected)>.08 or abs(selected-duration*.25)>duration*.06+.3:
                        error('PLAYER',f'Dragging progress loses position/state: value={selected:.3f}, clock={clock["time"]:.3f}, paused={clock["paused"]}')
                    button.click(timeout=3000)
                page.evaluate('window.__vibe_seekTo(0)')
            for msg in console_errors:
                error('BROWSER',msg)
            from pathlib import Path
            font=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts/msyh.ttc'
            environment=dict(python=sys.version,platform=sys.platform,playwright=importlib.metadata.version('playwright'),browser=browser.version,
                fontSha256=digest(font) if font.is_file() else None,fontFamily='Microsoft YaHei')
            if not font.is_file():error('ENVIRONMENT','Production font baseline is unavailable; do not silently accept a system fallback')
            return dict(browserErrors=errors,screenshots=screenshots,audioLevels=levels,environment=environment,observedMotion=motion,backgroundProbe=background,
                        geometry=geometry,browserVersion=browser.version,devHud=hud,progressControls=progress_checks,
                        limitations=['Screenshots are sampled, not every frame.',
                         'Signal probes do not prove speaker hardware or subjective listening quality.',
                         'Collision candidates use declared transformed boxes; intentional overlaps need explicit review.',
                         'Semantic meaning, narration fit and visual quality require recorded review.'])
        finally:
            browser.close()
