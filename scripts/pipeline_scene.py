"""Composable semantic slots compiled to the unchanged shared Canvas protocol."""
from scripts.contracts import validate_document
from scripts.text_contract import clean
from scripts.background_library import preset

SLOTS={
 'heading':(130,430,820,100), 'hero':(150,650,780,240),
 'hero-art':(290,630,500,360),'hero-label':(150,1060,780,110),
 'left':(130,730,340,160),'right':(610,730,340,160),'connector':(500,775,80,60),
 'top-note':(150,590,780,90),'row-one':(150,650,780,130),
 'row-two':(150,870,780,130),'row-three':(150,1090,780,130),'row-four':(150,1310,780,130),
 'image-top':(150,600,780,420),'caption-one':(150,1090,780,110),'caption-two':(150,1300,780,110),
 'left-icon':(210,570,180,130),'right-icon':(690,570,180,130)}
COLORS=dict(light='#eef9f3',accent='#65efb5',gold='#ebc86d')

def compile_scene(shot,brief,implementation,style,rows,assets):
    start,end=shot['startUs'],shot['endUs']
    nodes=[];roles=dict(title=[],content=[],graphic=[],panel=[]);beats=[];facts=[]
    def add(role,n):nodes.append(n);roles[role].append(n['id'])
    lines=style.get('titleLines',[style['title']])
    if clean(''.join(lines))!=clean(style['title']) or len(clean(style['title']))>12 and len(lines)!=2:
        raise ValueError('Work title requires explicit semantic titleLines')
    for i,line in enumerate(lines):
        add('title',dict(id='work-title-'+str(i),type='text',x=130,y=220 if len(lines)==1 else 202+i*57,width=820,height=72 if len(lines)==1 else (57 if i==0 else 49),text=line,size=48 if len(lines)==1 else (42 if i==0 else 36),color=COLORS['accent'],align='center',verticalAlign='center'))
    ids={n['id'] for n in nodes}
    for e in implementation['elements']:
        if e['id'] in ids:raise ValueError('Duplicate element ID: '+e['id'])
        ids.add(e['id']);idx=e['index']
        if not shot['startIndex']<=idx<shot['endIndex']:raise ValueError('Element anchor outside shot: '+e['id'])
        time=round(rows[idx]['StartSeconds']*1e6)
        if not start<=time<end:raise ValueError('Element time outside shot')
        x,y,w,h=SLOTS[e['slot']];kind=e['kind']
        node=dict(id=e['id'],type={'panel':'rect','arrow':'path'}.get(kind,kind),x=x,y=y,width=w,height=h,enterUs=time-start,entrance=e['entrance'])
        color=COLORS[e.get('tone','light')]
        if kind=='text':
            if not e.get('text') or 'assetId' in e:raise ValueError('Text element needs text only')
            size=76 if e['slot']=='hero' else 54 if e['slot']=='heading' else 46
            node.update(text=e['text'],size=size,color=color,align='center',verticalAlign='center')
            if e.get('emphasis'):node['emphasis']=dict(kind=e['emphasis'],timeUs=time-start)
            role='content'
        elif kind=='image':
            if e.get('text') or e.get('emphasis') or e.get('assetId') not in assets:raise ValueError('Image requires a registered asset')
            node.update(source=assets[e['assetId']]['source'],fit='contain',radius=0)
            role='graphic'
        elif kind=='panel':
            if any(k in e for k in ('text','assetId','emphasis')):raise ValueError('Panel is a surface, not text or asset')
            node.update(background='#10332f',color='#28554b',radius=24);role='panel'
        else:
            if e['slot']!='connector' or any(k in e for k in ('text','assetId','emphasis')):raise ValueError('Arrow requires connector slot')
            node.update(path='M 0 22 L 48 22 L 48 0 L 80 30 L 48 60 L 48 38 L 0 38 Z',color=color);role='graphic'
        add(role,node)
        if kind!='panel':
            beat=next((b for b in shot['beats'] if b['index']==idx),None)
            if not beat:raise ValueError('Element needs a declared original-word beat: '+e['id'])
            beats.append(dict(timeUs=time,quote=beat['quote'],nodeIds=[e['id']],meaning=beat['purpose']))
            if kind=='text' and any(c.isdigit() for c in e['text']):facts.append(dict(sceneId=shot['id'],nodeId=e['id'],text=e['text'],quote=beat['quote'],timeUs=time))
    if not roles['content']:raise ValueError('Scene needs readable content')
    scene=dict(id=shot['id'],startUs=start,endUs=end,nodes=nodes,transition='fade')
    plan=dict(sceneId=shot['id'],purpose=shot['goal'],visualIntent=brief['composition'],visualFamily=implementation['family'],roles=roles,beats=sorted(beats,key=lambda b:b['timeUs']),intentionalOverlaps=[],imageNote=brief['rationale'])
    return scene,plan,facts

def scene_document(style,scenes):
    bg=preset(style['backgroundPreset'])
    doc=dict(titleMode='shown',background=dict(color='#071d1b',particles=False,seed=8,preset=bg['id'],templateVersion=bg['version'],recipeSha256=bg['recipeSha256']),subtitleSize=46,protectedTerms=style['protectedTerms'],scenes=scenes,subtitles=[])
    validate_document('scene',doc)
    return doc
