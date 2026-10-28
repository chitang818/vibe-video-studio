"""N0008: timestamp-driven Canvas composition, original assets preserved."""
import json
import math
import shutil
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.extract_timeline import build_timeline_index, find_keyword
from scripts.build_fast_project import preset_wave

SOURCE = Path('C:/Users/chitang/Downloads/N0008_丛枝菌根真菌科普')
WORK = ROOT / 'temp/n0008'
OUT = ROOT / 'projects/N0008_丛枝菌根真菌科普_v1'
WORK.mkdir(parents=True, exist_ok=True)
rows = json.loads((SOURCE / 'N0008_char_timestamps.json').read_text(encoding='utf-8-sig'))
index = build_timeline_index(rows)
with wave.open(str(SOURCE / 'N0008_voice.wav')) as wav:
    duration = round(wav.getnframes() / wav.getframerate() * 1e6)

def at(phrase):
    hit = find_keyword(index, phrase)
    if not hit:
        raise ValueError('Missing narration phrase: ' + phrase)
    return round(hit['start_time'] * 1e6)

# Every cut is a spoken semantic boundary, never an evenly divided duration.
plans = [
    ('细菌类菌剂', '真菌类菌剂', '另一类农业微生物', 'intro', '就是真菌类菌剂'),
    ('真菌类菌剂按照', '按应用功能分类', '肥料与防病', 'classes-a', '第二种是木霉菌真菌'),
    ('三是白僵菌和绿僵菌', '杀虫与腐熟', '不同菌种，各有分工', 'classes-b', '四是毛霉和曲霉'),
    ('五是发酵类菌种', '发酵类：酵母菌', '本期聚焦丛枝菌根', 'yeast', '今天我们就着重讲一下'),
    ('丛枝菌根真菌是一类', '与陆生植物共生', '球囊菌门真菌', 'plant', '是开发最早的'),
    ('作为早期农业研发', '来自自然农业土壤', '筛选与驯化的共生菌', 'origin', '并非人工改造的新型菌种'),
    ('并且丛枝菌根属于', '依赖活体宿主', '专性活体营养型真菌', 'carbon', '必须依赖宿主植物根系'),
    ('同时会为植物提供', '互利共生', '植物供碳，真菌助吸收', 'exchange', '那么丛枝菌根'),
    ('丛枝菌根进入植物根系后', '根内：发育丛枝结构', '位于根皮层细胞内', 'cell', '丛枝菌根会在根皮层细胞内'),
    ('并且会在根外土壤中伸展', '根外：伸展菌丝网络', '菌丝直径远小于根毛', 'network', '这些菌丝直径远小于'),
    ('可以延伸到植物根系', '探索土壤空隙', '拓展养分获取范围', 'reach', '拓展了植物获取养分的范围'),
    ('早期驯化的丛枝菌根菌株', '适应常规农业环境', '中性到微酸性土壤', 'soil', '能在中性到微酸性土壤中'),
    ('在温度15摄氏度到30摄氏度区间', '适宜温度区间', '可正常侵染植物根系', 'temperature', '都可以正常侵染植物根系'),
    ('由于篇幅的问题', '下期继续', '养分吸收机制与应用优势', 'ending', '丛枝菌根促进植物'),
]
(WORK / 'keywords.txt').write_text('\n'.join(p[0] + '|转场' for p in plans) + '\n' + '\n'.join(p[4] + '|步骤' for p in plans), encoding='utf-8')
subprocess.run([sys.executable, 'vibe.py', 'timeline', str(SOURCE/'N0008_char_timestamps.json'), str(WORK/'keywords.txt'), '-o', str(WORK/'timeline.txt'), '--sfx-out', str(WORK/'timeline-sfx.json')], cwd=ROOT, check=True)

GREEN, CYAN, GOLD = '#65efb5', '#70d9ee', '#f1ce81'
scenes = []
for i, (phrase, heading, subheading, kind, beat) in enumerate(plans):
    start = 0 if i == 0 else at(phrase)
    end = at(plans[i+1][0]) if i+1 < len(plans) else duration
    reveal = max(0, at(beat)-start)
    nodes = []

    def node(typ, x, y, w, h, **kw):
        nodes.append(dict(id=f's{i+1}-n{len(nodes)+1}', type=typ, x=x, y=y, width=w, height=h, **kw))

    def text(s, y, size=48, color='#eef9f3', enter=0, x=130, w=820, h=None, pulse=False):
        node('text', x, y, w, h or math.ceil(size*1.4), text=s, size=size, color=color, align='center', enterUs=enter, enterDurationUs=320000, pulse=pulse)

    def box(x,y,w,h,color='#173b38',enter=0):
        node('rect',x,y,w,h,background=color,color='#2a5a51',radius=28,enterUs=enter,enterDurationUs=380000)

    def path(d,x,y,w,h,color=GREEN,enter=0,pulse=False):
        node('path',x,y,w,h,path=d,color=color,enterUs=enter,enterDurationUs=500000,pulse=pulse)

    def line(x1,y1,x2,y2,thick=6):
        dx,dy=x2-x1,y2-y1
        length=math.hypot(dx,dy)
        ox,oy=-dy/length*thick/2,dx/length*thick/2
        return f'M{x1+ox},{y1+oy} L{x2+ox},{y2+oy} L{x2-ox},{y2-oy} L{x1-ox},{y1-oy} Z '

    def roots(enter=0, spread=True):
        d=line(350,20,350,375,15)
        for direction in (-1,1):
            for j in range(4):
                yy=120+j*57
                d+=line(350,yy,350+direction*(85+j*17),yy+95,10)
        path(d,190,650,700,420,GOLD,enter)
        path('M350,25 Q165,70 180,-70 Q325,-100 350,25 Z M350,25 Q360,-130 520,-95 Q545,40 350,25 Z',190,650,700,420,GREEN,enter)
        if spread:
            hypha=''
            for direction in (-1,1):
                for j in range(4):
                    xx=350+direction*(90+j*17); yy=215+j*57
                    endx=350+direction*(250+j*15)
                    hypha+=line(xx,yy,endx,yy-65,4)
                    hypha+=line(endx,yy-65,endx+direction*25,yy-125,3)
                    hypha+=line(endx,yy-65,endx-direction*5,yy+35,3)
            path(hypha,190,650,700,420,CYAN,reveal,True)

    # Only the work title occupies the top safe zone.
    box(110,212,860,105,'#0b2927')
    text('丛枝菌根真菌科普',235,48,GREEN)
    text(heading,455,60,enter=0)
    text(subheading,548,38,'#a4c8bb',enter=0)

    if kind in ('classes-a','classes-b'):
        pairs = [('肥料类','丛枝菌真菌'),('防病生防','木霉菌')] if kind=='classes-a' else [('杀虫生防','白僵菌 · 绿僵菌'),('腐熟剂','毛霉 · 曲霉')]
        for j,(label,name) in enumerate(pairs):
            ent=0 if j==0 else reveal
            y=700+j*330
            box(125,y,830,260,enter=ent)
            # Fungal body and spores: conceptual glyph, no invented quantitative chart.
            path('M25,110 Q30,10 100,10 Q170,10 175,110 Z M83,112 L117,112 L117,185 L83,185 Z',150,y+30,200,200,GREEN if j==0 else CYAN,ent,True)
            text(label,y+45,39,GOLD,ent,x=375,w=540)
            text(name,y+125,46,enter=ent,x=375,w=540)
    elif kind=='cell':
        box(190,690,700,430,'#173c32')
        box(225,725,630,360,'#0d2825')
        d=line(320,310,320,165,10)
        for side in (-1,1):
            for j in range(4):
                xx=320+side*(55+j*23); yy=210-j*40
                d+=line(320,270-j*38,xx,yy,7)
                d+=line(xx,yy,xx+side*32,yy-55,5)
                d+=line(xx,yy,xx-side*20,yy-48,4)
        path(d,220,735,640,350,GREEN,reveal,True)
        text('根皮层细胞内的丛枝',1210,44,CYAN,reveal)
    elif kind=='temperature':
        # Only stated values; endpoint markers are a range schematic.
        path('M65,5 Q90,5 90,30 L90,260 A65,65 0 1 1 40,260 L40,30 Q40,5 65,5 Z',470,680,140,410,CYAN,0,True)
        text('15°C — 30°C',1130,72,GOLD)
        text('正常侵染根系',1280,46,GREEN,reveal)
    elif kind=='yeast':
        for j,(x,y) in enumerate([(300,730),(500,850),(670,730)]):
            node('ring',x,y,150,200,color=GREEN,background='#16443c',value=1,pulse=True,enterUs=0 if j==0 else min(reveal,at('比如酵母菌')-start))
        text('酵母菌',1150,60,GOLD)
        text('聚焦 → 丛枝菌根',1300,50,GREEN,reveal)
    elif kind=='ending':
        roots(0,True)
        box(150,1180,780,190,'#153d32',reveal)
        text('养分如何吸收？',1215,54,GREEN,reveal,pulse=True)
        text('应用优势有哪些？',1300,44,GOLD,reveal)
    else:
        roots(0,kind not in ('intro','origin','carbon','soil'))
        if kind=='intro':
            text('细菌之外，还有真菌',1195,54,GOLD,at('还有一种菌剂')-start)
            text('真菌类菌剂',1320,58,GREEN,reveal,pulse=True)
        elif kind=='plant':
            text('植物根系 ↔ 真菌',1190,52,GREEN,0)
            text('早期农业重点研究',1320,44,GOLD,reveal)
        elif kind=='origin':
            text('自然土壤 → 筛选驯化',1190,48,GREEN,0)
            text('并非人工改造的新型菌种',1320,44,GOLD,reveal)
        elif kind=='carbon':
            text('宿主植物 → 碳水化合物',1190,48,GOLD,reveal)
            text('支持真菌生长繁殖',1320,46,GREEN,at('才能完成生长繁殖')-start)
        elif kind=='exchange':
            text('植物供碳 → 真菌',1190,48,GOLD,0)
            text('真菌助吸收 → 植物',1320,48,CYAN,0,pulse=True)
        elif kind=='network':
            text('根外菌丝向土壤伸展',1190,48,CYAN,0)
            text('比根毛更细',1320,52,GOLD,reveal)
        elif kind=='reach':
            text('延伸至根系难达的空隙',1190,46,CYAN,0)
            text('拓展养分获取范围',1320,50,GREEN,reveal,pulse=True)
        elif kind=='soil':
            text('常规农业环境',1190,48,GREEN,0)
            text('中性 → 微酸性',1320,54,GOLD,reveal)
    scenes.append(dict(id=f'scene-{i+1:02}',startUs=start,endUs=end,nodes=nodes))

scene=dict(background=dict(color='#071d1b',particles=True,seed=8), subtitleSize=46,
           protectedTerms=['丛枝菌根真菌','丛枝菌根','球囊菌门','碳水化合物','专性活体营养型','根皮层细胞','白僵菌','绿僵菌','15摄氏度','30摄氏度'],scenes=scenes)
(WORK/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding='utf-8')
# Materialize the standard sound recipes as real WAV files before packaging.
events=[]
for sound in ['whoosh','click','ding','chime']:
    target=WORK/f'assets/sounds/{sound}.wav';target.parent.mkdir(parents=True,exist_ok=True)
    preset_wave(target,sound)
for s in scenes[1:]:
    events.append(dict(timeUs=s['startUs'],source='assets/sounds/whoosh.wav',gain=.24))
for p in plans:
    events.append(dict(timeUs=at(p[4]),source='assets/sounds/click.wav',gain=.20))
events.extend([dict(timeUs=at('是典型的互利共生关系'),source='assets/sounds/ding.wav',gain=.20),dict(timeUs=at('将放到下期内容介绍'),source='assets/sounds/chime.wav',gain=.24)])
(WORK/'sfx.json').write_text(json.dumps(dict(version=1,events=sorted(events,key=lambda e:e['timeUs'])),indent=2),encoding='utf-8')
subprocess.run([sys.executable,'vibe.py','fast-build','--scene',str(WORK/'scene.json'),'--voice',str(SOURCE/'N0008_voice.wav'),'--timestamps',str(SOURCE/'N0008_char_timestamps.json'),'--sfx',str(WORK/'sfx.json'),'--title','N0008_丛枝菌根真菌科普','--out',str(OUT)],cwd=ROOT,check=True)
shutil.copyfile(SOURCE/'N0008_丛枝菌根真菌科普.txt',OUT/'script.txt')
shutil.copyfile(WORK/'timeline.txt',OUT/'timeline.txt')
print(OUT)
