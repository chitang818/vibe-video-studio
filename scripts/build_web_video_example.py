"""Authored N0009 migration fixture. Not an automatic director for arbitrary scripts."""
import argparse
from pathlib import Path
from types import SimpleNamespace
from scripts import pipeline as p
from scripts.text_contract import quote_at
from scripts.media_assets import import_image

def prepare(out):
    old=p.ROOT/'projects/N0009_丛枝菌根作用与优势_v18'
    story=p.read(old/'story.json');rows=p.read(old/'assets/char_timestamps.json')
    requests=out.parent/(out.name+'-authoring')
    if requests.exists():raise ValueError('Choose an unused authoring directory')
    requests.mkdir(parents=True)
    style=dict(version=1,title=story['title'],authorId='n0009-web-director',backgroundPreset='bio-bubbles',protectedTerms=['丛枝菌根','微团聚体'])
    p.write(requests/'style.json',style)
    # Preserve semantic cuts from the verified original-word N0009 storyboard; no duration slicing.
    def anchor(a):
        hits=[i for i in range(len(rows)) if quote_at(rows,i,a['quote'])]
        return hits[a.get('occurrence',1)-1]
    starts=[0]+[anchor(s['anchor']) for s in story['scenes'][1:]]
    relations=['parallel','focus','sequence','spatial','cause','parallel','focus','spatial','cause','contrast','focus','sequence','cause','parallel','parallel','spatial','parallel','summary']
    descriptions=[
      ('回顾定位','无底板文字建立三个回顾层级','先定位菌剂与菌根，再承接基本特性'),
      ('重点表达','大字主视觉与短解释；不使用内容底板','以阅读层级突出本镜观点'),
      ('难吸收问题','四个独立文字节拍纵向展开，无矩形底板','困难与成因按原声顺序展开'),
      ('外部配图','一张本地象征插画与两条短说明','图片帮助建立视觉变化，不冒充显微证据'),
      ('氮素运输','左右运输关系与上下补充信息','明确运输至植物，不画真菌给固氮菌供氮的错误箭头'),
      ('微量元素','左右短标签与上下作用说明','并列信息采用空间分组'),
      ('范围重点','核心观点放大，下方保留短结论','原声倍数不转成无依据定量面积图'),
      ('土壤配图','本地土壤示意图片置上，两条短说明置下','象征插画仅表示土壤语境'),
      ('形态转化','固定养分与可利用形态两端，箭头连接','有机酸在上方解释，利用率结论位于下方'),
      ('交换界面','两段文字以主次层级解释交换界面','保留原文核心，不虚构双向运输图的细节'),
      ('应用转折','大字观点加短承接语','从机制过渡到应用，减少画面承载'),
      ('应用收益','四条无底板文字顺序展示','每条收益对应真实口播，不编造节省比例'),
      ('透明图混合','透明水滴SVG栅格图配原生文字与轻入场','素材背景透明，与动态底层自然融合'),
      ('生态层面','两组空间标签及底部结论','将生态层面的并列关系分组'),
      ('共同作用','左右呈现物理缠绕与粘合作用','并列共同作用，不误画单向因果'),
      ('团聚体示意','透明SVG土粒簇与两条解释文字','静态概念示意，不模拟真实聚合或显微结构'),
      ('群落协同','两组作用标签和两条结论','区分促进有益与抑制有害，不使用统一卡片'),
      ('结尾回扣','大字连接观点与农田平衡结语','结尾跟随原声，不新增CTA')]
    shots=[];briefs=[];implementations=[]
    for i,s in enumerate(story['scenes']):
        beats=[dict(index=anchor(it['anchor']),quote=it['anchor']['quote'],purpose='展示原声对应信息：'+it['text']) for it in s['items']]
        shot=dict(id=s['id'],startIndex=starts[i],endIndex=starts[i+1] if i+1<len(starts) else len(rows),goal=s['heading'],relation=relations[i],reason='沿用核验过的语义边界；本段围绕“'+s['heading']+'”形成独立观看目标',beats=beats)
        family,composition,rationale=descriptions[i]
        def text(j,slot,value=None,entrance='fade-up',tone='light'):
            return dict(id='point-'+str(j+1),kind='text',slot=slot,index=beats[j]['index'],text=value or s['items'][j]['text'],entrance=entrance,tone=tone)
        elements=[dict(id='heading',kind='text',slot='heading',index=beats[0]['index'],text=s['heading'],entrance='fade-up')]
        if i in (3,7):
            elements += [dict(id='illustration',kind='image',slot='image-top',index=beats[0]['index'],assetId='local-leaf' if i==3 else 'local-soil',entrance='zoom'),text(0,'caption-one'),text(1,'caption-two',entrance='slide-left',tone='accent')]
        elif i in (12,15):
            elements += [dict(id='transparent-subject',kind='image',slot='hero-art',index=beats[0]['index'],assetId='water-cutout' if i==12 else 'soil-cutout',entrance='zoom'),text(0,'caption-one'),text(1,'caption-two',entrance='slide-right',tone='accent')]
        elif i in (4,8):
            elements += [text(0,'top-note'),text(1,'left',value='菌丝转运无机氮' if i==4 else '固定矿质养分',entrance='slide-right'),text(2,'right',value='植物获得氮素' if i==4 else '可吸收利用形态',entrance='slide-left',tone='accent'),dict(id='relationship-arrow',kind='arrow',slot='connector',index=beats[2]['index'],entrance='fade-up',tone='gold'),text(3,'caption-two',tone='gold')]
            if i==4:
                elements[1]=text(1,'top-note')
                elements[2]=text(0,'left',entrance='slide-right')
        elif i in (5,13,16):
            elements += [text(0,'left',entrance='slide-right'),text(1,'right',entrance='slide-left',tone='accent'),text(2,'caption-one'),text(3,'caption-two',tone='gold')]
        elif i in (2,11):
            elements += [text(j,slot,entrance='slide-left' if j in (1,3) else 'fade-up',tone='gold' if j==3 else 'light') for j,slot in enumerate(('row-one','row-two','row-three','row-four'))]
        elif i==14:
            elements += [text(0,'left',entrance='slide-right'),text(1,'right',entrance='slide-left',tone='gold')]
        elif len(s['items'])==3:
            elements += [text(j,slot,tone='accent' if j==2 else 'light') for j,slot in enumerate(('row-one','row-two','row-three'))]
        else:
            elements += [text(0,'hero',entrance='zoom'),text(1,'hero-label',tone='accent')]
        sketch=[dict(slot=e['slot'],label=e.get('text',e.get('assetId','关系箭头')),form='text' if e['kind']=='text' else 'image' if e['kind']=='image' else 'shape') for e in elements]
        brief=dict(shotId=s['id'],focus='理解“'+s['heading']+'”的核心信息',composition=composition,rationale=rationale,opening='按原文事件进入章节重点，保留标题及题材背景',development='各元素随对应原词依次呈现；重点与辅助信息使用不同层级',ending='保留结论供阅读并自然衔接下一段原声',continuity='继承青绿主题、金色辅助强调和共用字幕位置；本镜构图服务内容关系',constraints=['不新增原文以外的数据、结论或口播','象征素材不能充当显微结构证据'],assetRequests=[e['assetId'] for e in elements if e['kind']=='image'],sketch=sketch)
        # Asset requests are descriptions rather than opaque names.
        brief['assetRequests']=['取得并登记本镜素材：'+a for a in brief['assetRequests']]
        shots.append(shot);briefs.append(brief);implementations.append(dict(shotId=s['id'],reason=rationale,family=family,elements=elements))
    for name,data in [('shots',dict(version=1,shots=shots)),('briefs',dict(version=1,briefs=briefs)),('implementation',dict(version=1,scenes=implementations))]:p.write(requests/(name+'.json'),data)
    p.intake(SimpleNamespace(project=out,voice=old/'assets/voice.wav',timestamps=old/'assets/char_timestamps.json',script=old/'assets/script.txt',style=requests/'style.json',captions=p.ROOT/'projects/N0009_丛枝菌根作用与优势_authoring/captions.json'))
    with p.locked(out):
        state=p.load_state(out);p.segment(out,state,requests/'shots.json');p.direct(out,state,requests/'briefs.json')
        for asset_id,path in [('local-leaf',old/'assets/images/leaf.png'),('local-soil',old/'assets/images/soil.png')]:
            import_image(path,out,asset_id,'local','VIBE original symbolic artwork from preserved N0009 assets','original')
        water='<svg xmlns="http://www.w3.org/2000/svg" width="800" height="640"><path d="M400 40 C350 150 160 310 160 420 C160 660 640 660 640 420 C640 310 450 150 400 40 Z" fill="#70d9ee"/><path d="M250 420 C250 505 320 555 400 555" fill="none" stroke="#eef9f3" stroke-width="20" stroke-linecap="round"/></svg>'
        soil='<svg xmlns="http://www.w3.org/2000/svg" width="800" height="640">'+''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x,y,r,c in [(250,220,110,'#bf976d'),(470,200,90,'#e0bd86'),(600,360,120,'#b48b64'),(350,440,130,'#d3ad76'),(190,420,70,'#ebc86d')])+'</svg>'
        for aid,svg in [('water-cutout',water),('soil-cutout',soil)]:
            path=requests/(aid+'.svg');path.write_text(svg,encoding='utf-8');import_image(path,out,aid,'local','Original code-drawn conceptual SVG; transparent; not microscopy','original')
        p.inspect(out,state)
    return requests

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();print(prepare(args.out.resolve()))
