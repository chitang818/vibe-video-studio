"""Semantic dynamic-presentation compiler; all geometry and effects belong here."""
from scripts.contracts import validate_document, load_profile
from scripts.text_contract import clean, quote_at, validate_rows

PROFILE = 'presentation-portrait-v1'
LAYOUTS = ('statement', 'hero-image', 'image-text', 'cards', 'comparison', 'steps')
ENTRANCES = ('fade-up', 'slide-left', 'slide-right', 'zoom')
THEME = dict(background='#071d1b', surface='#10332f', text='#eef9f3', accent='#65efb5', gold='#ebc86d')


def compile_presentation(story, rows, duration):
    profile=load_profile(PROFILE)
    validate_document('story-v2', story)
    validate_rows(rows, duration)
    def anchor(spec):
        hits=[round(r['StartSeconds']*1e6) for i,r in enumerate(rows) if quote_at(rows,i,spec['quote'])]
        occurrence=spec.get('occurrence',1)
        if not hits or not 1<=occurrence<=len(hits) or len(hits)>1 and 'occurrence' not in spec:
            raise ValueError('Missing or ambiguous original quote: '+spec['quote'])
        return hits[occurrence-1]
    lines=story.get('titleLines',[story['title']])
    if clean(''.join(lines))!=clean(story['title']) or len(lines)==2 and len(clean(lines[1]))<4:
        raise ValueError('Title lines must preserve the work title without an orphan tail')
    shown=story.get('titleMode','shown')=='shown'
    if shown and len(clean(story['title']))>12 and len(lines)!=2:raise ValueError('Long title requires titleLines')
    starts=[0]+[anchor(s['anchor']) for s in story['scenes'][1:]]
    preset=story.get('backgroundPreset','bio-bubbles');content_align=story.get('contentAlign','center')
    from scripts.background_library import preset as resolve_background
    background=resolve_background(preset,story.get('backgroundTemplateVersion'))
    scene=dict(titleMode=story.get('titleMode','shown'),background=dict(color=THEME['background'],particles=False,seed=8,preset=preset,templateVersion=background['version'],recipeSha256=background['recipeSha256']),subtitleSize=46,protectedTerms=story.get('protectedTerms',[]),scenes=[],subtitles=[])
    plan=dict(version=1,profile=PROFILE,authorId=story['authorId'],contentAlign=content_align,facts=[],background=dict(implementation='deterministic preset: '+preset,rationale='保留题材动态背景；内容允许阅读停留，不强制机制图'),scenes=[])
    assets={a['id']:a for a in story.get('assets',[])}
    if len(assets)!=len(story.get('assets',[])):raise ValueError('Duplicate asset IDs')
    for i,s in enumerate(story['scenes']):
        start,end=starts[i],starts[i+1] if i+1<len(starts) else duration
        if not 4000000<=end-start<=20000000:raise ValueError('Presentation page must be 4..20s; split at an original phrase')
        layout=s['layout'];items=s['items'];count=len(items)
        if layout in ('cards','steps') and not 2<=count<=4 or layout=='comparison' and count!=2 or layout=='statement' and not 1<=count<=2 or layout in ('hero-image','image-text') and not 1<=count<=2:
            raise ValueError('Layout capacity exceeded; split the page: '+s['id'])
        if layout in ('hero-image','image-text') and not s.get('image'):raise ValueError('Image layout requires a registered image')
        if s.get('image') and layout not in ('hero-image','image-text'):raise ValueError('Selected layout does not accept an image')
        nodes=[];roles=dict(title=[],content=[],graphic=[],panel=[]);beats=[]
        def add(role,typ,nid,x,y,w,h,**attrs):
            if typ=='text':attrs.setdefault('verticalAlign','center')
            n=dict(id=nid,type=typ,x=x,y=y,width=w,height=h,**attrs)
            if role!='title' and not nid.startswith('title') and not shown:n['y']-=220
            nodes.append(n);roles[role].append(nid);return n
        if shown:
            add('panel','rect','title-panel',110,194,860,122,background='#0b2927',color='#265c50',radius=20)
            for j,line in enumerate(lines):
                add('title','text','title-'+str(j+1),130,220 if len(lines)==1 else 202+j*57,820,72 if len(lines)==1 else (57 if j==0 else 49),text=line,size=48 if len(lines)==1 else (42 if j==0 else 36),color=THEME['accent'],align='center')
        add('content','text','heading',130,440,820,92,text=s['heading'],size=58,color=THEME['text'],align=content_align)
        # Accent rule lives above the content, never across its glyphs.
        add('panel','rect','section-rule',496 if content_align=='center' else 132,553,88,5,background=THEME['accent'],color=THEME['accent'],radius=2)
        if s.get('image'):
            a=assets.get(s['image'])
            if not a:raise ValueError('Unknown image asset: '+s['image'])
            add('graphic','image','picture',132,610,816,500 if layout=='hero-image' else 420,source=a['source'],fit=s.get('imageFit','cover'),focusX=a.get('focusX',.5),focusY=a.get('focusY',.5),imageZoom=s.get('imageZoom',False),radius=24,entrance='zoom')
        for j,item in enumerate(items):
            t=anchor(item['anchor'])
            if not start<t<end:raise ValueError('Item anchor must be strictly inside its page')
            if j and t<=beats[-1]['timeUs']:raise ValueError('Items must follow original narration order')
            text=item['text'];nid=f'item-{j+1}';effect=item.get('entrance',('fade-up','zoom')[j%2])
            size=52;align=content_align;x=172;w=736
            if layout=='statement':
                y=680+j*285;h=220;size=82 if j==0 else 48;align='center';x=150;w=780
            elif layout in ('hero-image','image-text'):
                y=(1160 if layout=='hero-image' else 1080)+j*130;h=106;size=46
            else:
                h=110;gap=h+60+profile['cardSpacing']['preferredGapPx'];y=650+j*gap
                if layout=='comparison':gap=330;y=690+j*gap;h=170
                add('panel','rect',f'card-{j+1}',130,y-30,820,h+60,background=THEME['surface'],color='#28554b',radius=24,enterUs=t-start,entrance=effect)
                if layout=='steps':
                    x=200;w=680
                    # Bullets have no invented numerical meaning.
                    add('panel','rect',f'bullet-{j+1}',160,y+35,8,40,background=THEME['gold'],color=THEME['gold'],radius=3,enterUs=t-start,entrance=effect)
            n=add('content','text',nid,x,y,w,h,text=text,size=size,color=THEME['gold'] if layout=='comparison' and j else THEME['text'],align=align,enterUs=t-start,entrance=effect,enterDelayUs=90000 if layout in ('cards','comparison','steps') else 0)
            if 'emphasis' in item:
                e=item['emphasis'];et=anchor(e['anchor'])
                if not t<=et<end:raise ValueError('Emphasis must follow its entry and remain inside the page')
                n['emphasis']=dict(kind=e['kind'],timeUs=et-start)
            beats.append(dict(timeUs=t,quote=item['anchor']['quote'],nodeIds=[nid],meaning='展示讲解内容：'+text))
            if any(c.isdigit() for c in text):plan['facts'].append(dict(sceneId=s['id'],nodeId=nid,text=text,quote=item['anchor']['quote'],timeUs=t))
            if 'emphasis' in n:
                beats.append(dict(timeUs=start+n['emphasis']['timeUs'],quote=item['emphasis']['anchor']['quote'],nodeIds=[nid],meaning='强调已展示内容：'+text))
        beats.sort(key=lambda b:b['timeUs'])
        scene['scenes'].append(dict(id=s['id'],startUs=start,endUs=end,nodes=nodes,transition=s.get('transition','fade')))
        plan['scenes'].append(dict(sceneId=s['id'],purpose=s['heading'],visualIntent='动态演示版式：'+layout,visualFamily=layout,roles=roles,beats=beats,intentionalOverlaps=[],imageNote=s.get('imageNote','已登记图片' if s.get('image') else '本页采用文字版式，无需机制图')))
    return scene,plan
