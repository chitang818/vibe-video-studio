"""Executable requirements recovered from the DOM-to-Canvas migration."""
import math
from pathlib import Path
from scripts.text_contract import clean


def scene_checks(manifest, scene, plan, profile):
    errors=[]
    def fail(rule,detail,sid):errors.append(dict(rule=rule,detail=detail,sceneId=sid))
    width,height=manifest['width'],manifest['height']
    for shot,p in zip(scene['scenes'],plan['scenes']):
        nodes={n['id']:n for n in shot['nodes']};sid=shot['id']
        titles=[nodes[n] for n in p['roles'].get('title',[]) if n in nodes]
        content=[nodes[n] for n in p['roles'].get('content',[])+p['roles'].get('graphic',[]) if n in nodes]
        if sum(bool(n.get('pulse')) for n in shot['nodes'])>profile['maxDecorativeLoops']:fail('MOTION','At most two simultaneous decorative loops are allowed',sid)
        if scene.get('titleMode','shown')=='hidden':
            if titles or 'title-panel' in nodes:fail('TITLE','Hidden title mode must remove title and its panel',sid)
            if content and min(n['y'] for n in content)>height*.20:fail('TITLE','Hidden title mode must reclaim the empty title zone',sid)
        else:
            if any(n['type']!='text' for n in titles):fail('TITLE','Work title must be explicit text',sid)
            lines=[line for n in titles for line in n.get('text','').split('\n')]
            text=''.join(lines)
            if manifest.get('title') and clean(text)!=clean(manifest['title']):fail('TITLE','Top title differs from the work title',sid)
            if len(lines)>2 or len(lines)==2 and len(clean(lines[-1]))<4:fail('TITLE','Use at most two semantic title lines; no orphan tail',sid)
            if len(lines)==2 and len(titles)!=2:fail('TITLE','Use separate text nodes for the two semantic title lines',sid)
            if len(clean(text))>12 and len(lines)<2:fail('TITLE','Long work title needs explicit semantic lines',sid)
            for term in scene.get('protectedTerms',[]):
                if clean(term) in clean(text) and not any(clean(term) in clean(line) for line in lines):
                    fail('TITLE','Protected technical term split across title lines',sid)
            if titles and max(n['y']+n['height'] for n in titles)-min(n['y'] for n in titles)>height*.06:fail('TITLE','Work title exceeds its 6% height budget',sid)
            for index,n in enumerate(titles):
                style='short' if len(lines)==1 else ('longFirst' if index==0 else 'longSecond')
                low,high=profile['titleFonts'][style]
                if not width*low<=n.get('size',0)<=width*high:fail('TYPE','Work title size is outside its short/long hierarchy',sid)
                if n['y']<height*.10 or n['y']+n['height']>height*.165:fail('TITLE','Work title must occupy the 10%..16.5% title zone',sid)
                if abs(n['x']+n['width']/2-width/2)>1:fail('TITLE','Work title must be horizontally centered',sid)
        for pair in p.get('intentionalOverlaps',[]):
            members=[nodes[n] for n in pair.get('nodeIds',[]) if n in nodes]
            if len(members)!=2 or sorted(n['type'] for n in members)!=['ring','text']:continue
            ring=next(n for n in members if n['type']=='ring');text=next(n for n in members if n['type']=='text')
            radius=min(ring['width'],ring['height'])*.42
            inner=radius-max(2,radius*.12)/2
            corners=[(x,y) for x in (text['x'],text['x']+text['width']) for y in (text['y'],text['y']+text['height'])]
            extra=profile['ringNumberClearancePx']
            if any(math.hypot(x-ring['x']-ring['width']/2,y-ring['y']-ring['height']/2)+extra>inner for x,y in corners):
                fail('COLLISION','Ring number needs at least 20px clearance from its inner stroke',sid)
            low,high=profile['ringNumberFont']
            if not width*low<=text.get('size',0)<=width*high:fail('TYPE','Ring number size must be 5.2%..5.8% of width',sid)
    return errors


def sound_checks(scene,track,metrics,profile):
    errors=[];events=track['events']
    def fail(detail,sid=None):errors.append(dict(rule='SFX',detail=detail,sceneId=sid))
    for event in events:
        if Path(event['source']).suffix.lower()!='.wav' or Path(event['source']).stem not in profile['soundKinds']:
            fail('Sound must be a real WAV with a whitelisted semantic name')
        sound=metrics.get(event['source'])
        if sound and event['timeUs']+sound['durationUs']>scene['scenes'][-1]['endUs']:
            fail('Sound tail extends beyond the physical voice boundary')
    if not 1<=sum(Path(e['source']).stem=='ding' for e in events)<=3:
        fail('Choose one to three original-word highlights for ding')
    for shot in scene['scenes'][1:]:
        if not any(Path(e['source']).stem=='whoosh' and e['timeUs']==shot['startUs'] for e in events):
            fail('Every scene cut requires an anchored whoosh',shot['id'])
    last=scene['scenes'][-1]
    if not any(Path(e['source']).stem=='chime' and last['startUs']<=e['timeUs']<last['endUs'] for e in events):
        fail('Final scene requires an anchored chime',last['id'])
    return errors
