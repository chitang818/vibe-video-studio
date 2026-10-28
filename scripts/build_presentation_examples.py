"""Reproducible local icons, six-layout showcase and N0009 v2 story authoring."""
import argparse
import json
from pathlib import Path
from PIL import Image,ImageDraw
from scripts.media_assets import import_image


def make_icons(root):
    """Original symbolic artwork, never presented as microscopy or biological evidence."""
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    for kind in ('leaf','water','soil'):
        im=Image.new('RGB',(1200,760),'#10332f');d=ImageDraw.Draw(im)
        for r in range(320,40,-8):
            d.ellipse((600-r,380-r,600+r,380+r),fill=(16,51+int((320-r)/15),47+int((320-r)/30)))
        if kind=='leaf':
            d.ellipse((400,165,780,585),fill='#65efb5');d.polygon([(460,530),(710,220),(685,410)],fill='#10332f')
            d.ellipse((235,350,455,545),fill='#ebc86d');d.ellipse((785,240,945,390),fill='#4dbb9a')
        elif kind=='water':
            d.polygon([(600,150),(440,390),(430,460),(465,540),(540,585),(660,585),(735,540),(770,460),(760,390)],fill='#70d9ee')
            d.arc((480,355,700,550),20,120,fill='#eef9f3',width=14)
            d.ellipse((290,290,330,330),fill='#65efb5');d.ellipse((880,480,940,540),fill='#ebc86d')
        else:
            for x,y,r,color in [(390,310,88,'#bf976d'),(570,260,72,'#e0bd86'),(740,330,105,'#b48b64'),(465,475,96,'#d3ad76'),(665,500,80,'#ebc86d'),(830,485,43,'#a57b56')]:d.ellipse((x-r,y-r,x+r,y+r),fill=color)
            for x,y in [(300,480),(830,220),(565,405),(900,420)]:d.ellipse((x-18,y-18,x+18,y+18),fill='#65efb5')
        im.save(root/(kind+'.png'))
    (root/'README.md').write_text('Original code-drawn symbolic illustrations by VIBE Studio. Permission: original project artwork. Not microscopy, quantitative data or a scientifically exact anatomical diagram. Rebuild: python -m scripts.build_presentation_examples --out <new-authoring-directory>.\n',encoding='utf-8')


def prepare(out):
    out=Path(out)
    if out.exists():raise ValueError('Choose a new authoring directory')
    out.mkdir(parents=True)
    library=Path('assets/presentation-library')
    if not library.exists():make_icons(library)
    entries=[]
    for kind in ('leaf','water','soil'):
        e=import_image(library/(kind+'.png'),out,kind,'local','VIBE original symbolic artwork; scripts/build_presentation_examples.py','original')
        entries.append({k:e[k] for k in ('id','source','focusX','focusY')})
    old=json.loads(Path('projects/N0009_丛枝菌根作用与优势_authoring/story.json').read_text(encoding='utf-8'))
    layouts=['cards','statement','steps','image-text','steps','cards','statement','hero-image','steps','comparison','statement','steps','image-text','cards','comparison','image-text','cards','statement']
    story=dict(version=2,title=old['title'],authorId='n0009-presentation-author',theme='teal-editorial',backgroundPreset='bio-bubbles',contentAlign='center',assetPolicy='local',assets=entries,scenes=[])
    for i,(s,layout) in enumerate(zip(old['scenes'],layouts)):
        stages=s['stages'];selected=stages if layout in ('cards','steps') else [stages[0],stages[-1]]
        if len(stages)==2:selected=stages
        items=[dict(text=x['text'],anchor=x['anchor'],entrance=('fade-up','zoom')[j%2]) for j,x in enumerate(selected)]
        # A single readable emphasis, anchored to existing narration, not per-word flashing.
        items[-1]['emphasis']=dict(kind=('color','marker','underline')[i%3],anchor=items[-1]['anchor'])
        page=dict(id=s['id'],layout=layout,heading=s['heading'],anchor=s['anchor'],items=items,transition='fade' if i%3 else 'push',imageNote='文字承担本页重点；不补无关机制图')
        if layout in ('hero-image','image-text'):
            page.update(image='water' if i==12 else 'soil' if i in (7,15) else 'leaf',imageFit='cover',imageZoom=True,imageNote='项目原创象征插画，不代表显微结构或定量证据')
        story['scenes'].append(page)
    replacements={'原稿倍数依据待核对':'菌丝拓展吸收范围','原稿对比：吸附交换':'双向交换效率更高','回扣农田养分平衡':'维持农田养分平衡'}
    for page in story['scenes']:
        for item in page['items']:item['text']=replacements.get(item['text'],item['text'])
    (out/'story.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Showcase uses six original semantic pages and the full original audio; each layout is represented.
    showcase=json.loads(json.dumps(story));names=['statement','hero-image','image-text','cards','comparison','steps']
    for i,page in enumerate(showcase['scenes']):
        layout=names[i%6];page['layout']=layout
        source=old['scenes'][i]['stages'];page['items']=[dict(text=x['text'],anchor=x['anchor']) for x in (source[:2] if i==0 else source if layout in ('cards','steps') else [source[0],source[-1]])]
        if layout in ('hero-image','image-text'):page.update(image=['leaf','water','soil'][i%3],imageFit='cover',imageZoom=True,imageNote='标准版式样片：原创象征插画')
        else:
            for key in ('image','imageFit','imageZoom'):page.pop(key,None)
            page['imageNote']='标准版式样片：文字主视觉'
    for page in showcase['scenes']:
        for item in page['items']:item['text']=replacements.get(item['text'],item['text'])
    (out/'showcase.json').write_text(json.dumps(showcase,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'README.md').write_text('story.json: N0009动态演示重制源。showcase.json: 六类版式轮换的完整原声样片。图片是代码绘制的象征插画，不是科学结构证据；仅使用本地来源，无搜图或生图外部调用。原稿长度与面积比较的疑点保留原声字幕，未增加定量图。\n',encoding='utf-8')
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);print(prepare(p.parse_args().out))
