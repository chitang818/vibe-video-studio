"""Studio authoring and release checks. Does not modify the shared runtime."""
import hashlib
import json
import math
import re
import wave
import os
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from collections import Counter
from pathlib import Path

from scripts.build_fast_project import asset_path, digest, verify
from scripts.text_contract import clean, normalized_tokens, strict_loads, validate_rows,quote_at,number_tokens
from scripts.contracts import validate_document, load_profile

ROOT = Path(__file__).resolve().parents[1]
REVIEW_CHECKS = ('scientificMeaning', 'narrationSync', 'semanticCaptions',
                 'visualRhythm', 'backgroundQuality', 'mobileReadability', 'soundMix', 'ending')
PUNCT = '，、：；。！？,.!?：;'


def read_json(path):
    return strict_loads(Path(path).read_text(encoding='utf-8-sig'))


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def contrast(left,right):
    def luminance(color):
        channels=[int(color[i:i+2],16)/255 for i in (1,3,5)]
        channels=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in channels]
        return sum(a*b for a,b in zip(channels,(.2126,.7152,.0722)))
    a,b=sorted((luminance(left),luminance(right)))
    return (b+.05)/(a+.05)


def input_fingerprint(root):
    """Bind reviews to actual files and policy/checker code, not claimed hashes only."""
    root = Path(root)
    manifest = read_json(root/'vibe.project.json')
    names = set(manifest['assetHashes']) | {'vibe.project.json', 'quality-plan.json'}
    files = {name: digest(asset_path(root, name)) for name in sorted(names) if asset_path(root, name).is_file()}
    for name in ('AGENTS.md', 'references/quality-contract.md', '.agents/rules/vibe-rules.md',
                 '.agents/skills/vibe-knowledge-video/SKILL.md', 'scripts/quality_gate.py',
                 'scripts/quality_browser.py', 'references/fast-project.md', 'scripts/build_fast_project.py', 'vibe.py',
                 'scripts/preview_template.py','scripts/text_contract.py','scripts/contracts.py',
                 'references/quality-profile.json','references/schemas/scene.schema.json','references/schemas/quality-plan.schema.json',
                 'scripts/release.py','scripts/components.py','scripts/audio_checks.py','scripts/reviewer.py','requirements.lock.txt','references/schemas/story.schema.json','references/schemas/manifest.schema.json','scripts/doctor.py','scripts/extract_timeline.py','scripts/preservation.py','references/rule-migration.md','references/checklist.md'):
        files['policy:'+name] = digest(ROOT/name)
    for name in ('scripts/presentation.py','scripts/media_assets.py','references/presentation-profile.json','references/schemas/story-v2.schema.json','references/schemas/media-registry.schema.json','references/presentation-authoring.md'):
        files['policy:'+name]=digest(ROOT/name)
    from scripts.background_library import builder
    for p in builder().source_paths(ROOT/'assets/runtime'):
        files['background-source:'+str(p.relative_to(ROOT))]=digest(p)
    for name in ('scripts/background_library.py','references/background-library.md'):
        files['policy:'+name]=digest(ROOT/name)
    return hashlib.sha256(canonical(files).encode()).hexdigest()


def card_panel_ids(nodes, roles):
    """Identify content surfaces by geometry/role, not an editable node ID."""
    texts=[nodes[n] for n in roles.get('content',[]) if n in nodes and nodes[n]['type']=='text']
    return {nid for nid in roles.get('panel',[]) if nid in nodes and nodes[nid]['type']=='rect'
            and any(nodes[nid]['x']<=t['x'] and nodes[nid]['y']<=t['y']
                    and nodes[nid]['x']+nodes[nid]['width']>=t['x']+t['width']
                    and nodes[nid]['y']+nodes[nid]['height']>=t['y']+t['height'] for t in texts)}


def card_spacing_failures(boxes, minimum):
    failures=[]
    ordered=sorted(boxes,key=lambda b:b['y'])
    for i,a in enumerate(ordered):
        for b in ordered[i+1:]:
            if min(a['x']+a['width'],b['x']+b['width'])<=max(a['x'],b['x']):continue
            gap=b['y']-a['y']-a['height']
            if gap<minimum-0.01:failures.append(f"{a['id']} / {b['id']}: {gap:.2f}px < {minimum}px")
    return failures


def static_checks(manifest, scene, rows, plan):
    """Return explicit rule failures. Plan annotations never waive automatic failures."""
    issues = []
    def error(rule, detail, sid=None):
        issues.append(dict(rule=rule, detail=detail, sceneId=sid))

    w, h, duration = manifest['width'], manifest['height'], manifest['durationUs']
    profile = load_profile(plan.get('profile','knowledge-portrait-v1') if isinstance(plan,dict) else 'knowledge-portrait-v1')
    presentation=profile['id']=='presentation-portrait-v1'
    if (w,h)!=(profile['width'],profile['height']):
        error('PROFILE','knowledge-portrait-v1 requires 1080x1920')
    if not profile['subtitleMin']<=scene.get('subtitleSize',w*.04)<=profile['subtitleMax']:
        error('TYPE','Subtitle size outside production profile')
    for name,value in [('scene',scene),('quality-plan',plan)]:
        try: validate_document(name,value)
        except ValueError as exc: error('SCHEMA',str(exc))
    if any(e['rule']=='SCHEMA' for e in issues):
        if not isinstance(plan,dict):error('PLAN','Missing quality-plan.json')
        return issues
    first_heading=''.join(n.get('text','') for n in scene['scenes'][0]['nodes'] if n['id']=='heading')
    original_opening=''.join(r['Char'] for r in rows[:50])
    if '回顾' in first_heading and not any(word in original_opening for word in ('上一期','上期','回顾','接着讲','接上期')):
        error('OPENING','Recap opening is not supported by the original narration')
    scenes = scene.get('scenes', [])
    starts = {round(r['StartSeconds']*1e6) for r in rows}
    scene_ids = [s['id'] for s in scenes]
    if not isinstance(plan, dict) or plan.get('version') != 1:
        error('PLAN', 'Missing or unsupported quality-plan.json; author a storyboard before release')
        plan = {}
    background = plan.get('background', {})
    if not background.get('implementation') or not background.get('rationale'):
        error('BACKGROUND', 'Record actual background implementation and subject-specific rationale')
    planned = plan.get('scenes', [])
    if not isinstance(planned, list):
        error('PLAN', 'scenes must be an array'); planned = []
    if [p.get('sceneId') for p in planned] != scene_ids:
        error('PLAN', 'Plan must cover every scene exactly once, in order')
    plans = {p.get('sceneId'): p for p in planned}
    if presentation:
        from scripts.presentation import LAYOUTS
        if any(p.get('visualFamily') not in LAYOUTS or not p.get('imageNote') for p in planned):error('PLAN','Presentation pages need a real supported layout and an image decision')
    if presentation:
        if scene.get('background',{}).get('preset') not in ('bio-bubbles','constellation','dna-spiral','cyber-grid','aurora-dust','solid'):error('BACKGROUND','Select an implemented background preset; do not silently drop the background')
    if presentation:
        from scripts.background_library import preset as resolve_background,library_version
        if profile.get('backgroundLibraryVersion')!=library_version():error('PROFILE','Background library version differs from the production profile')
        bg=scene.get('background',{})
        try:
            spec=resolve_background(bg.get('preset'))
            if bg.get('templateVersion')!=spec['version'] or bg.get('recipeSha256')!=spec['recipeSha256']:error('BACKGROUND_IDENTITY','Background version/recipe must match its locked template')
        except ValueError as exc:error('BACKGROUND_IDENTITY',str(exc))
    families = []
    for s in scenes:
        sid, start, end = s['id'], s['startUs'], s['endUs']
        if not profile['shotMinUs'] <= end-start <= profile['shotMaxUs']:
            error('RHYTHM', f'Shot duration {(end-start)/1e6:.3f}s is outside 6..14s', sid)
        if start and start not in starts:
            error('SYNC', 'Scene cut is not an original character start', sid)
        nodes = {n['id']: n for n in s['nodes']}
        for n in nodes.values():
            emphasis=n.get('emphasis')
            if emphasis and (not presentation or start+emphasis['timeUs'] not in starts or emphasis['timeUs']<n.get('enterUs',0) or start+emphasis['timeUs']>=end):error('SYNC','Emphasis lacks a valid original-word anchor',sid)
        entries = sorted(set(n.get('enterUs', 0) for n in nodes.values()))
        if any(t < 0 or start+t >= end for t in entries):
            error('SYNC', 'Node enters outside its scene', sid)
        for n in nodes.values():
            if n.get('enterUs', 0) and start+n['enterUs'] not in starts:
                error('SYNC', f"Entry {n['id']} has no original character anchor", sid)
            if n['type'] == 'text' and n.get('size', w*.035) < w*profile['bodyMinRatio']:
                error('TYPE', f"Text {n['id']} is below 2.8% width", sid)
        p = plans.get(sid, {})
        if not p.get('purpose') or not p.get('visualIntent') or not p.get('visualFamily'):
            error('PLAN', 'Provide purpose, visualIntent and visualFamily', sid)
        if p.get('visualFamily'): families.append(p['visualFamily'])
        roles = p.get('roles', {})
        if set(roles)-set(profile['roles']):
            error('PLAN','Unknown node role',sid)
        role_ids = [n for values in roles.values() for n in values] if isinstance(roles, dict) and all(isinstance(v, list) for v in roles.values()) else []
        if sorted(role_ids) != sorted(nodes):
            error('PLAN', 'roles must assign every node exactly once', sid)
        if not presentation and not roles.get('graphic'):
            error('GRAPHIC', 'Every scene requires an explanatory main graphic', sid)
        if presentation:
            panel_ids=card_panel_ids(nodes,roles)
            for detail in card_spacing_failures([nodes[n] for n in panel_ids],profile['cardSpacing']['minimumGapPx']):
                error('CARD_SPACING',detail,sid)
            expected=plan.get('contentAlign','center')
            for nid in roles.get('content',[]):
                n=nodes.get(nid,{})
                if n.get('type')=='text' and (n.get('align')!=expected or n.get('verticalAlign')!='center'):error('ALIGNMENT','Presentation text must implement its declared horizontal and vertical alignment',sid)
        title_nodes = [nodes[n] for n in roles.get('title', []) if n in nodes]
        content_nodes = [nodes[n] for n in roles.get('content', [])+roles.get('graphic', []) if n in nodes]
        if not title_nodes and scene.get('titleMode','shown')!='hidden':
            error('LAYOUT', 'Work title role is required', sid)
        if title_nodes and content_nodes:
            title_bottom = max(n['y']+n['height'] for n in title_nodes)
            top = min(n['y'] for n in content_nodes)
            bottom = max(n['y']+n['height'] for n in content_nodes)
            if top-title_bottom < h*.06 or h*.82-bottom < h*.06 or bottom-top > h*.54:
                error('LAYOUT', 'Three-zone spacing/maximum content height violated', sid)
        if roles.get('graphic') and any(nodes.get(n, {}).get('type') not in ('path', 'ring', 'bar', 'image') for n in roles['graphic']):
            error('GRAPHIC', 'Main graphic must contain actual graphic nodes, not labels/panels', sid)
        # Count motion of content only. Background/panel/title activity cannot hide a static lesson.
        content_ids = set(roles.get('content', []) + roles.get('graphic', [])) if role_ids else set(nodes)
        intervals = []
        for nid in content_ids:
            n = nodes.get(nid, {})
            begin = n.get('enterUs', 0)
            finish = min(end-start, begin+(n.get('enterDurationUs') or 450000))
            if n.get('pulse'):
                finish = end-start
            if n.get('type') in ('ring', 'bar') and n.get('value', .5) != n.get('toValue', n.get('value', .5)):
                finish = max(finish, min(end-start, n.get('valueDurationUs') or end-start))
            intervals.append((begin,finish))
        covered = 0
        for begin,finish in sorted(intervals):
            if not presentation and begin-covered >= profile['maxStaticUs']:
                error('MOTION', 'Content is static for >=2s; particles/subtitles do not satisfy this rule', sid); break
            covered = max(covered,finish)
        else:
            if not presentation and end-start-covered >= profile['maxStaticUs']:
                error('MOTION', 'Content is static for >=2s after its last animation', sid)
        beats = p.get('beats', [])
        valid_beats = []
        if not isinstance(beats, list):
            error('PLAN', 'beats must be an array', sid); beats = []
        for beat in beats:
            t, quote, ids = beat.get('timeUs'), beat.get('quote', ''), beat.get('nodeIds', [])
            if not isinstance(t, int) or not start <= t < end or t not in starts or not quote or not clean(quote) or not ids or not beat.get('meaning'):
                error('BEAT', 'Beat needs a character timestamp, quote, nodeIds and meaning', sid); continue
            matching = [i for i, r in enumerate(rows) if round(r['StartSeconds']*1e6) == t]
            if not any(quote_at(rows,i,quote) for i in matching):
                error('BEAT', f'Quote does not match narration at {t}', sid)
            if any(nid not in nodes or (start+nodes[nid].get('enterUs',0)!=t and not (presentation and start+nodes[nid].get('emphasis',{}).get('timeUs',-start-1)==t)) for nid in ids):
                error('BEAT', 'Beat must trigger actual node entries at that time', sid)
            else:
                valid_beats.append(t-start)
        # Pulse and background motion do not count as new information beats.
        events = sorted(set([0, *valid_beats, end-start]))
        if any(b-a > profile['maxBeatGapUs'] for a, b in zip(events, events[1:])):
            error('RHYTHM', 'More than 4s without a planned, rendered information beat', sid)
        if sid == scene_ids[0]:
            first = sorted(set(t for t in valid_beats if t > 0))
            if len(first) < 2 or first[0] > profile['hookFirstUs'] or first[1] > profile['hookSecondUs']:
                error('HOOK', f"Opening needs two anchored advances: first <={profile['hookFirstUs']/1e6:g}s, second <={profile['hookSecondUs']/1e6:g}s", sid)
        for pair in p.get('intentionalOverlaps', []):
            if len(pair.get('nodeIds', [])) != 2 or any(n not in nodes for n in pair['nodeIds']) or len(pair.get('reason', '')) < 8:
                error('PLAN', 'Intentional overlap needs two real nodes and a specific explanation', sid)
            elif pair.get('design')!='ring-number' or sorted(nodes[n]['type'] for n in pair['nodeIds'])!=['ring','text']:
                error('COLLISION','Only a ring and its pure number may use intentional overlap',sid)
            elif not re.fullmatch(r'[0-9.＋+\-%％×x]+',next(nodes[n]['text'] for n in pair['nodeIds'] if nodes[n]['type']=='text')):
                error('COLLISION','Ring center must contain only numeric notation',sid)
    if not presentation and families and max(Counter(families).values()) > max(2, math.ceil(len(scenes)/2)):
        error('VARIETY', 'One declared visual family occupies more than half the shots; review actual repetition')
    actual_families=[]
    for s in scenes:
        p=plans.get(s['id'],{});ids=p.get('roles',{}).get('graphic',[])
        signature=[{k:n[k] for k in ('type','path','source','value','toValue') if k in n} for n in s['nodes'] if n['id'] in ids]
        actual_families.append(canonical(signature))
        main=[n for n in s['nodes'] if n['id'] in ids]
        if main and all(n['type'] in ('bar','ring') and max(n.get('value',.5),n.get('toValue',n.get('value',.5)))==0 for n in main):
            error('VISIBILITY','Empty charts alone cannot be the explanatory main graphic',s['id'])
        for n in s['nodes']:
            if n['type']=='rect' and n['id'] not in p.get('roles',{}).get('panel',[]):
                error('PLAN','Rectangles must have the panel role',s['id'])
            if n['id'] in p.get('roles',{}).get('panel',[]) and n['type']!='rect':
                error('PLAN','Panel role only accepts rectangles',s['id'])
            if n['type']!='rect':
                color=n.get('color','#e8f1ec')
                if not re.fullmatch(r'#[0-9a-fA-F]{6}',color):
                    error('VISIBILITY','Production content needs opaque six-digit colors',s['id'])
                else:
                    backdrop=scene.get('background',{}).get('color','#070d12')
                    for prior in s['nodes'][:s['nodes'].index(n)]:
                        if prior['type']=='rect' and prior['x']<=n['x'] and prior['y']<=n['y'] and prior['x']+prior['width']>=n['x']+n['width'] and prior['y']+prior['height']>=n['y']+n['height']:
                            backdrop=prior.get('background','#15323a')
                    if re.fullmatch(r'#[0-9a-fA-F]{6}',backdrop) and contrast(color,backdrop)<profile['minimumContrast']:
                        error('VISIBILITY','Content contrast is below profile minimum',s['id'])
            if n['type']=='text' and re.search(r'\d',n['text']):
                refs=[f for f in (plan or {}).get('facts',[]) if f['sceneId']==s['id'] and f['nodeId']==n['id']]
                if len(refs)!=1 or refs[0]['text']!=n['text']:
                    error('FACT','Numeric display needs one exact fact reference',s['id'])
                else:
                    f=refs[0];tokens=number_tokens
                    matches=[i for i,r in enumerate(rows) if round(r['StartSeconds']*1e6)==f['timeUs']]
                    if not any(quote_at(rows,i,f['quote']) for i in matches) or any(t not in tokens(f['quote']) for t in tokens(n['text'])):
                        error('FACT','Displayed number/unit is not supported by its original quote',s['id'])
    if not presentation and actual_families and max(Counter(actual_families).values())>max(2,math.ceil(len(scenes)/2)):
        error('VARIETY','Actual main graphics repeat in more than half the scenes')

    from scripts.preservation import scene_checks
    issues.extend(scene_checks(manifest,scene,plan,profile))
    units = scene.get('subtitles', [])
    spoken = normalized_tokens([(c,round(r['StartSeconds']*1e6)) for r in rows for c in r['Char']])
    displayed = normalized_tokens([(c,ch['startUs']) for u in units for ch in u['chars'] for c in ch['text']])
    if displayed != spoken:
        error('CAPTION', 'Subtitle text/timing differs from original character timestamps')
    ends={(c,round(r['StartSeconds']*1e6)):round(r['EndSeconds']*1e6) for r in rows for c in r['Char']}
    for i, u in enumerate(units):
        text = ''.join(c['text'] for c in u['chars'])
        length = len(clean(text))
        if length < 4 and i != 0 or length > 16:
            error('CAPTION', f'Invalid caption length {length}: {text}')
        if text.endswith(tuple('，、：；')):
            error('CAPTION', 'Trailing clause punctuation must be removed')
        if any(u['endUs']<ends.get((c,ch['startUs']),0) for ch in u['chars'] for c in clean(ch['text'])):
            error('CAPTION','Caption window ends before its last spoken character finishes')
    # Terms cannot cross caption boundaries; sentence ends and internal punctuation survive.
    marked=normalized_tokens([(c,i) for i,u in enumerate(units) for item in u['chars'] for c in item['text']])
    boundaries={i+1 for i in range(len(marked)-1) if marked[i][1]!=marked[i+1][1]}
    full = ''.join(c for c, _ in spoken)
    for match in re.finditer(r'[+-]?(?:\d+(?:\.\d+)?|\.\d+)(?:%|°C|摄氏度|倍)?|[A-Za-z][A-Za-z0-9_.%+-]*',full):
        if any(match.start()<x<match.end() for x in boundaries):
            error('CAPTION','Numeric value or ASCII identifier crosses a subtitle boundary')
    for term in scene.get('protectedTerms', []):
        for match in re.finditer(re.escape(clean(term)), full):
            if any(match.start() < x < match.end() for x in boundaries):
                error('CAPTION', 'Protected term split: '+term)
    # Compare punctuation within each unit against original rows by ordered character consumption.
    raw = [(c,round(r['StartSeconds']*1e6)) for r in rows for c in r['Char'] if not c.isspace()]
    kept=set(i for _,i in normalized_tokens([(c,i) for i,(c,_) in enumerate(raw)]))
    source_tokens=[(c,t,i in kept) for i,(c,t) in enumerate(raw)]
    source_pos = 0
    for u in units:
        out = ''.join(c['text'] for c in u['chars'])
        count = len(clean(out)); consumed = 0; original = ''
        while source_pos < len(source_tokens) and consumed < count:
            c, _, content = source_tokens[source_pos]; source_pos += 1; original += c
            consumed += content
        while source_pos < len(source_tokens) and not source_tokens[source_pos][2]:
            original += source_tokens[source_pos][0]; source_pos += 1
        original = original.rstrip('，、：；')
        if out != original:
            error('CAPTION', f'Punctuation differs: expected {original!r}, got {out!r}')
    return issues


def report_directory(root):
    identity = hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()[:16]
    return ROOT/'artifacts/quality'/identity


def validate_review(root, report):
    path = Path(root)/'quality-review.json'
    failures = []
    if not path.is_file():
        return [dict(rule='REVIEW', detail='Missing quality-review.json; visual/audio review remains pending')]
    review = read_json(path)
    if review.get('inputFingerprint') != report['inputFingerprint']:
        failures.append(dict(rule='REVIEW', detail='Review is stale: project, plan, policy or checker changed'))
    if review.get('evidenceDigest') != report.get('evidenceDigest'):
        failures.append(dict(rule='REVIEW', detail='Review does not match current screenshot evidence'))
    if review.get('version') != 1 or not review.get('reviewer') or review.get('status') != 'passed':
        failures.append(dict(rule='REVIEW', detail='Review must identify reviewer and explicitly pass'))
    for key in REVIEW_CHECKS:
        item = review.get('checks', {}).get(key, {})
        if item.get('status') != 'passed' or len(item.get('observations', '').strip()) < 12:
            failures.append(dict(rule='REVIEW', detail='Unreviewed criterion: '+key))
    expected = [s['id'] for s in read_json(Path(root)/'scene.json')['scenes']]
    checked = review.get('scenes', [])
    if [s.get('sceneId') for s in checked] != expected:
        failures.append(dict(rule='REVIEW', detail='Review must cover every scene exactly once in order'))
    evidence = {e['file']: e for e in report.get('screenshots', [])}
    for name, item in evidence.items():
        try:
            if digest(asset_path(Path(report.get('evidenceRoot',report_directory(root))), name)) != item['sha256']:
                raise ValueError('changed image')
        except (OSError, ValueError):
            failures.append(dict(rule='REVIEW', detail='Screenshot missing or changed: '+name))
    for item in checked:
        if item.get('status') != 'passed' or len(item.get('observations', '').strip()) < 12:
            failures.append(dict(rule='REVIEW', detail='Scene lacks an actual review', sceneId=item.get('sceneId')))
        links = item.get('evidence', [])
        if not links or any(name not in evidence or evidence[name]['sceneId'] != item.get('sceneId') for name in links):
            failures.append(dict(rule='REVIEW', detail='Scene must reference its own current screenshots', sceneId=item.get('sceneId')))
    return failures


def _run_gate(root, release=False, browser=True, output=None, project_identity=None):
    root = Path(root).resolve()
    report = dict(version=2, project=str(project_identity or root), status='blocked', scope='automated checks; semantic/visual/listening review is separate',
                  errors=[], screenshots=[], reviewCriteria={key:'pending' for key in REVIEW_CHECKS},
                  capabilityNotes=['Chapter HUD is preview-only and is not burned into Canvas exports.',
                    'Official background presets, title glow/gradient/frost and full cross-scene effects are not established by automatic passage; record actual capability gaps in review.'])
    output = output or report_directory(root); output.mkdir(parents=True, exist_ok=True)
    report['evidenceRoot']=str(output)
    try:
        from scripts.doctor import check_dependencies
        compatible,message,_=check_dependencies()
        if not compatible:raise ValueError('Dependency baseline mismatch: '+message)
        from scripts.background_library import verify_runtime
        verify_runtime()
        manifest = verify(root)
        validate_document('manifest',manifest)
        # Verify the whole shared runtime, not just the scene.mjs entry point.
        for name in ('scene.mjs', 'audio.mjs'):
            if digest(root/'vibe-runtime'/name) != digest(ROOT/'assets/runtime'/name):
                raise ValueError('Shared runtime mismatch: '+name)
        required = {manifest[k] for k in ('htmlFile', 'sceneFile', 'sfxFile')}
        required.update(manifest[k] for k in ('voiceFile', 'timestampsFile') if manifest.get(k))
        if not required.issubset(manifest['assetHashes']):
            raise ValueError('Manifest does not hash all required assets')
        script_file=manifest.get('scriptFile') or 'assets/script.txt'
        if manifest.get('voiceFile') and script_file not in manifest['assetHashes']:
            report['errors'].append(dict(rule='SOURCE',detail='Original narration script must be packaged and hashed via --script'))
        track = read_json(asset_path(root, manifest['sfxFile']))
        if track.get('version') != 1 or not isinstance(track.get('events'), list):
            raise ValueError('Invalid sound track')
        for e in track['events']:
            if e['source'] not in manifest['assetHashes']:
                raise ValueError('Sound asset is not hashed: '+e['source'])
            if not isinstance(e['timeUs'], int) or not 0 <= e['timeUs'] < manifest['durationUs'] or not 0 <= e.get('gain',1) <= 2:
                raise ValueError('Invalid sound event timing/gain')
        scene = read_json(asset_path(root, manifest['sceneFile']))
        plan = read_json(root/'quality-plan.json') if (root/'quality-plan.json').exists() else None
        profile=load_profile(plan.get('profile','knowledge-portrait-v1') if isinstance(plan,dict) else 'knowledge-portrait-v1')
        if len(manifest['assetHashes'])>profile['maxAssets'] or len(track['events'])>profile['maxSoundEvents'] or len({e['source'] for e in track['events']})>profile['maxSounds']:
            raise ValueError('Asset/sound counts exceed the shared production contract')
        for shot in scene.get('scenes',[]):
            for node in shot.get('nodes',[]):
                if node.get('type')=='image':
                    asset_path(root,node['source'])
                    if node['source'] not in manifest['assetHashes']:
                        raise ValueError('Image source is not packaged and hashed: '+node['source'])
        rows = read_json(asset_path(root, manifest['timestampsFile'])) if manifest.get('timestampsFile') else []
        if manifest.get('voiceFile'):
            validate_rows(rows, manifest['durationUs'])
            if not track['events']:
                report['errors'].append(dict(rule='SFX',detail='Voiced production requires a real, anchored sound-effect track'))
        source_starts = {round(r['StartSeconds']*1e6) for r in rows}
        if script_file in manifest['assetHashes']:
            script = asset_path(root, script_file).read_text(encoding='utf-8-sig')
            original=''.join(r['Char'] for r in rows)
            if clean(script) != clean(original) or number_tokens(script)!=number_tokens(original):
                report['errors'].append(dict(rule='SOURCE',detail='Script and character timestamp text differ; resolve the discrepancy without silently rewriting originals'))
        if rows and any(e['timeUs'] not in source_starts for e in track['events']):
            report['errors'].append(dict(rule='SYNC',detail='Sound trigger has no original character anchor'))
        ding = [e for e in track['events'] if Path(e['source']).stem == 'ding']
        if len(ding)>3:
            report['errors'].append(dict(rule='SFX',detail='More than three ding highlights'))
        for shot in scene.get('scenes', []):
            pops = sorted(e['timeUs'] for e in track['events'] if Path(e['source']).stem == 'pop' and shot['startUs']<=e['timeUs']<shot['endUs'])
            if len(pops)>3 or any(b-a<600000 for a,b in zip(pops,pops[1:])):
                report['errors'].append(dict(rule='SFX',detail='pop frequency exceeds limits',sceneId=shot['id']))
        plan = read_json(root/'quality-plan.json') if (root/'quality-plan.json').exists() else None
        if manifest.get('voiceFile'):
            with wave.open(str(asset_path(root, manifest['voiceFile']))) as wav:
                if round(wav.getnframes()/wav.getframerate()*1e6) != manifest['durationUs']:
                    raise ValueError('WAV and manifest duration differ')
        report['inputFingerprint'] = input_fingerprint(root)
        report['profile']=profile['id']
        if profile['id']=='presentation-portrait-v1':
            report['compositionWarnings']=[dict(sceneId=b['sceneId'],detail='Three consecutive pages use the same layout; review pacing') for a,b,c in zip(plan['scenes'],plan['scenes'][1:],plan['scenes'][2:]) if a['visualFamily']==b['visualFamily']==c['visualFamily']]
            report['capabilityNotes']=['Dynamic presentation; reading holds are intentional. Chapter HUD and controls are preview-only. External image acquisition and subjective listening need actual evidence.']
            if any(n['type']=='image' for sh in scene['scenes'] for n in sh['nodes']):
                from scripts.media_assets import validate_registry
                if 'assets/media-registry.json' not in manifest['assetHashes']:raise ValueError('Media provenance is not hashed')
                registry=read_json(root/'assets/media-registry.json')
                refs=[dict(id=a['id'],source=a['source']) for a in registry['assets']]
                validate_registry(root,refs,'mixed')
                registered={a['source'] for a in refs}
                if any(n['source'] not in registered for sh in scene['scenes'] for n in sh['nodes'] if n['type']=='image'):raise ValueError('Unregistered scene image')
        report['errors'].extend(static_checks(manifest, scene, rows, plan))
        from scripts.audio_checks import inspect_audio
        audio_result,audio_errors=inspect_audio(root,manifest,track)
        report.update(audio_result);report['errors'].extend(audio_errors)
        from scripts.preservation import sound_checks
        if manifest.get('voiceFile'):
            report['errors'].extend(sound_checks(scene,track,report['audioAssets'],profile))
        if browser:
            from scripts.quality_browser import inspect_browser
            report.update(inspect_browser(root, manifest, scene, plan or {}, output))
            report['errors'] = report.pop('browserErrors', []) + report['errors']
        else:
            report['errors'].append(dict(rule='BROWSER', detail='Browser checks skipped; diagnostic only, cannot release'))
        report['evidenceDigest'] = hashlib.sha256(canonical(report['screenshots']).encode()).hexdigest()
        if release:
            review_errors = validate_review(root, report)
            report['errors'].extend(review_errors)
            if not review_errors:
                try:
                    from scripts.release import verify_approval
                    verify_approval(root,report)
                except Exception as exc:
                    report['errors'].append(dict(rule='APPROVAL',detail='Trusted independent approval required: '+str(exc)))
                report['reviewCriteria'] = {key:'recorded_pass' for key in REVIEW_CHECKS}
        report['status'] = 'blocked' if report['errors'] else ('release_passed' if release else 'needs_review')
    except Exception as exc:
        report['errors'].append(dict(rule='EXECUTION', detail=str(exc)))
    (output/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def run_gate(root, release=False, browser=True):
    root=Path(root).resolve()
    base=report_directory(root);base.mkdir(parents=True,exist_ok=True)
    lock=base/'active.lock'
    try:
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        return dict(version=2,status='blocked',errors=[dict(rule='CONCURRENT',detail='Another audit is active; do not overwrite its evidence')],screenshots=[])
    os.write(fd,str(os.getpid()).encode());os.close(fd)
    run=base/'runs'/uuid.uuid4().hex;run.mkdir(parents=True)
    try:
        before=input_fingerprint(root)
        with tempfile.TemporaryDirectory(prefix='vibe-audit-') as task_dir:
            snapshot=Path(task_dir)/'project';snapshot.mkdir()
            manifest=read_json(root/'vibe.project.json')
            names=set(manifest['assetHashes'])|{'vibe.project.json','quality-plan.json','quality-review.json','release.attestation.json'}
            for name in names:
                source=asset_path(root,name)
                if source.is_file():
                    destination=snapshot/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
            if input_fingerprint(snapshot)!=before:
                raise ValueError('Source changed while taking its audit snapshot')
            report=_run_gate(snapshot,release,browser,run,root)
        if input_fingerprint(root)!=before:
            report['errors'].append(dict(rule='CONCURRENT',detail='Source changed during audit; evidence cannot approve it'))
            report['status']='blocked'
        report['runId']=run.name
    except Exception as exc:
        report=dict(version=2,project=str(root),status='blocked',errors=[dict(rule='EXECUTION',detail=str(exc))],screenshots=[],evidenceRoot=str(run),runId=run.name)
    encoded=json.dumps(report,ensure_ascii=False,indent=2)
    try:
        (run/'report.json').write_text(encoded,encoding='utf-8')
        pending=base/(run.name+'.json');pending.write_text(encoded,encoding='utf-8');os.replace(pending,base/'report.json')
    finally:
        lock.unlink(missing_ok=True)
    print(f"Quality status: {report['status']}; errors: {len(report['errors'])}; report: {run/'report.json'}")
    for issue in report['errors'][:20]:
        print(f"  [{issue['rule']}] {issue.get('sceneId', '')}: {issue['detail']}")
    return report


def initialize(root):
    """Create incomplete authoring/review templates, never fabricate approval."""
    root = Path(root).resolve(); scene = read_json(root/'scene.json')
    plan_path = root/'quality-plan.json'
    if not plan_path.exists():
        plan = dict(version=1, profile='knowledge-portrait-v1',authorId='',facts=[],background=dict(implementation='', rationale=''), scenes=[dict(
            sceneId=s['id'], purpose='', visualIntent='', visualFamily='',
            roles=dict(title=[], content=[], graphic=[], panel=[]), beats=[], intentionalOverlaps=[])
            for s in scene['scenes']])
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    review_path = root/'quality-review.json'
    if not review_path.exists():
        report_path = report_directory(root)/'report.json'
        report = read_json(report_path) if report_path.exists() else {}
        review = dict(version=1, status='pending', reviewer='', inputFingerprint=report.get('inputFingerprint', ''),
            evidenceDigest=report.get('evidenceDigest', ''), checks={key:dict(status='pending', observations='') for key in REVIEW_CHECKS},
            scenes=[dict(sceneId=s['id'], status='pending', observations='', evidence=[]) for s in scene['scenes']])
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Templates created where missing; no existing files overwritten. Fill plan, run audit, inspect evidence, then complete review.')
