"""Versioned composition compiler. No author-supplied coordinates, CSS or JavaScript."""
import json
from pathlib import Path
from scripts.text_contract import clean,strict_loads,validate_rows,quote_at
from scripts.contracts import validate_document,load_profile

COMPONENT_VERSION=5
KINDS=('process','classification','exchange','cross-section','comparison','data','ending')


def compile_story(story, rows, duration):
    if story.get('version')==2:
        from scripts.presentation import compile_presentation
        return compile_presentation(story,rows,duration)
    validate_rows(rows,duration)
    validate_document("story",story)
    allowed={'version','title','authorId','scenes','titleMode','titleLines'}
    if set(story)-allowed or story['version']!=1 or not story['authorId']:
        raise ValueError('Story requires version, title, authorId and scenes')
    lines=story.get('titleLines',[story['title']])
    if clean(''.join(lines))!=clean(story['title']) or len(lines)==2 and len(clean(lines[1]))<4:
        raise ValueError('Semantic title lines must preserve the title without an orphan tail')
    if story.get('titleMode','shown')=='shown' and len(clean(story['title']))>12 and len(lines)!=2:
        raise ValueError('Long work title requires two explicit semantic titleLines')
    def anchor(spec):
        if set(spec)-{'quote','occurrence'} or not spec.get('quote') or not clean(spec['quote']):
            raise ValueError('Anchor needs quote and optional occurrence')
        hits=[round(r['StartSeconds']*1e6) for i,r in enumerate(rows)
              if quote_at(rows,i,spec['quote'])]
        occurrence=spec.get('occurrence',1)
        if type(occurrence)!=int or not 1<=occurrence<=len(hits):
            raise ValueError('Missing or ambiguous anchor occurrence: '+spec['quote'])
        if len(hits)>1 and 'occurrence' not in spec:
            raise ValueError('Repeated quote requires an explicit occurrence: '+spec['quote'])
        return hits[occurrence-1]
    shots=story['scenes']
    if not isinstance(shots,list) or not shots:
        raise ValueError('Story requires scenes')
    starts=[0]+[anchor(s['anchor']) for s in shots[1:]]
    scene=dict(titleMode=story.get('titleMode','shown'),background=dict(color='#071d1b',particles=True,seed=8),subtitleSize=46,protectedTerms=[],scenes=[])
    plan=dict(version=1,profile='knowledge-portrait-v1',authorId=story['authorId'],facts=[],
        background=dict(implementation='shared deterministic bio-colored particles',rationale='深色农科配色；背景质量仍需实际视觉复核'),scenes=[])
    # Shapes are filled polygons with declared geometry and no off-box coordinates.
    shapes={
      'process':'M30 90 H170 V175 H30 Z M235 90 H375 V175 H235 Z M440 90 H580 V175 H440 Z M180 125 H205 V110 L230 135 L205 160 V145 H180 Z M385 125 H410 V110 L435 135 L410 160 V145 H385 Z',
      'classification':'M85 20 H535 V70 H85 Z M310 70 H320 V120 H520 V130 H120 V120 H310 Z M70 150 H230 V270 H70 Z M390 150 H550 V270 H390 Z',
      'exchange':'M30 100 H195 V230 H30 Z M425 100 H590 V230 H425 Z M215 110 H375 V90 L410 125 L375 160 V140 H215 Z M405 205 H245 V185 L210 220 L245 255 V235 H405 Z',
      'cross-section':'M35 25 H585 V300 H35 Z M70 60 V265 H550 V60 Z M305 245 H315 V135 H305 Z M305 170 L220 90 L212 98 L305 185 Z M315 170 L400 90 L408 98 L315 185 Z M305 210 L170 145 L164 155 L305 222 Z M315 210 L450 145 L456 155 L315 222 Z',
      'comparison':'M55 45 H260 V285 H55 Z M360 45 H565 V285 H360 Z M295 65 H325 V115 H295 Z M295 150 H325 V200 H295 Z M295 235 H325 V285 H295 Z',
      'data':'M20 5 V320 H600 V310 H30 V5 Z',
      'ending':'M80 65 H540 V255 H80 Z M120 100 V220 H500 V100 Z M240 125 L365 165 L240 200 Z'}
    for i,s in enumerate(shots):
        if set(s)-{'id','kind','heading','anchor','stages'} or s.get('kind') not in KINDS:
            raise ValueError('Unknown story field/component')
        start,end=starts[i],starts[i+1] if i+1<len(starts) else duration
        if not 6000000<=end-start<=14000000:
            raise ValueError('Semantic shot must be 6..14s; adjust original quote boundaries')
        if not 2<=len(s['stages'])<=4:
            raise ValueError('Each component needs 2..4 information stages')
        nodes=[];roles=dict(title=[],content=[],graphic=[],panel=[]);beats=[]
        def node(role,typ,nid,x,y,w,h,**attrs):
            nodes.append(dict(id=nid,type=typ,x=x,y=y,width=w,height=h,**attrs));roles[role].append(nid)
        if scene['titleMode']=='shown':
            if len(lines)==1:
                node('panel','rect','title-panel',110,212,860,105,background='#0b2927',color='#265c50',radius=20)
                node('title','text','title',130,235,820,72,text=lines[0],size=48,color='#65efb5',align='center')
            else:
                node('panel','rect','title-panel',110,194,860,122,background='#0b2927',color='#265c50',radius=20)
                node('title','text','title-line-one',130,202,820,57,text=lines[0],size=42,color='#eef9f3',align='center')
                node('title','text','title-line-two',130,259,820,49,text=lines[1],size=36,color='#65efb5',align='center')
        node('content','text','heading',120,440,840,90,text=s['heading'],size=58,color='#eef9f3',align='center')
        node('graphic','path','diagram',230,650,620,330,path=shapes[s['kind']],color='#70d9ee',pulse=True)
        for j,stage in enumerate(s['stages']):
            fields={'text','anchor','value','unit'} if s['kind']=='data' else {'text','anchor'}
            if set(stage)!=fields:
                raise ValueError('Stage fields do not match the selected component')
            t=anchor(stage['anchor']);nid=f'stage-{j+1}'
            if not start<t<end:
                raise ValueError('Stage anchor must be inside the shot')
            node('content','text',nid,140,1050+j*95,800,74,text=stage['text'],size=48,color='#65efb5',align='center',enterUs=t-start)
            gid=f'graphic-stage-{j+1}'
            if s['kind']=='data':
                values=[x['value'] for x in s['stages']]
                if any(type(v) not in (int,float) or v<0 for v in values) or max(values)<=0:
                    raise ValueError('Data values must be finite, nonnegative with a positive scale')
                import math
                if not all(math.isfinite(v) for v in values):raise ValueError('Non-finite chart data')
                rendered=f"{stage['value']:g}"+stage['unit']
                if rendered not in stage['text'] or rendered not in stage['anchor']['quote']:
                    raise ValueError('Chart value and unit must appear verbatim in text and its source quote')
                node('graphic','bar',gid,280,680+j*65,500,34,value=stage['value']/max(values),color='#65efb5',background='#183b35',enterUs=t-start)
            else:
                x=45+j*140
                node('graphic','path',gid,230,650,620,330,path=f'M{x} 285 H{x+95} V300 H{x} Z',color='#65efb5',enterUs=t-start)
            beats.append(dict(timeUs=t,quote=stage['anchor']['quote'],nodeIds=[nid,gid],meaning='讲解推进：'+stage['text']))
            if any(c.isdigit() for c in stage['text']):
                plan['facts'].append(dict(sceneId=s['id'],nodeId=nid,text=stage['text'],quote=stage['anchor']['quote'],timeUs=t))
        if scene['titleMode']=='hidden':
            for n in nodes:n['y']-=220
        scene['scenes'].append(dict(id=s['id'],startUs=start,endUs=end,nodes=nodes))
        plan['scenes'].append(dict(sceneId=s['id'],purpose='解释本镜内容：'+s['heading'],visualIntent='使用标准组件解释：'+s['heading'],
            visualFamily=s['kind'],roles=roles,beats=beats,intentionalOverlaps=[]))
    return scene,plan
