"""Apply editorial caption boundaries and finish the N0008 project assets."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'projects/N0008_丛枝菌根真菌科普_v1'
scene=json.loads((P/'scene.json').read_text(encoding='utf-8'))
rows=json.loads((P/'assets/char_timestamps.json').read_text(encoding='utf-8'))
# Fixed semantic windows, preserving every spoken character and original timing.
captions='''细菌类菌剂|和放线菌类菌剂之外的|还有一种菌剂|就是真菌类菌剂|真菌类菌剂|按照应用功能来区分呢|主要分为这么几类|一类是肥料类菌剂|像丛枝菌真菌|第二种是木霉菌真菌|属于防病生防菌剂|三是白僵菌和绿僵菌|属于杀虫生防菌剂|四是毛霉和曲霉|是腐熟剂的常用菌种|五是发酵类菌种|比如酵母菌|今天我们就着重讲一下|第一类丛枝菌根|丛枝菌根真菌是一类|可以和绝大多数陆生植物|形成共生关系的|球囊菌门真菌|是开发最早的|菌根类菌剂核心菌株|也是早期农业重点研究的|真菌类菌剂|作为早期农业|研发应用的菌剂品种|丛枝菌根|是从自然农业土壤中|筛选驯化得到的共生菌|并非人工改造的新型菌种|并且丛枝菌根属于|专性活体营养型真菌|必须依赖宿主植物根系|提供的碳水化合物|才能完成生长繁殖|同时会为植物|提供养分吸收帮助|是典型的互利共生关系|那么丛枝菌根|是如何与作物|形成共生关系呢|这还要从它的形态结构|和生长特性说起|丛枝菌根|进入植物根系后|丛枝菌根会在|根皮层细胞内|发育出独特的丛枝结构|并且会在根外土壤中伸展|长出大量菌丝|这些菌丝直径|远小于植物根毛|可以延伸到|植物根系无法到达的|土壤空隙中|拓展了植物|获取养分的范围|早期驯化的丛枝菌根菌株|对多数常规农业环境|有较好适应性|能在中性到微酸性土壤中|保持活性|在温度15摄氏度|到30摄氏度区间|都可以正常侵染植物根系|由于篇幅的问题|丛枝菌根促进植物的|养分吸收机制与应用优势|将放到下期内容介绍'''.split('|')
punct='，、：；。！？,.!?：'
chars=[r for r in rows if r['Char'].strip() and r['Char'] not in punct]
full=''.join(r['Char'] for r in chars)
assert ''.join(captions)==full, 'Editorial caption text must exactly match narration'
groups=[];pos=0
for caption in captions:
    group=chars[pos:pos+len(caption)];pos+=len(caption)
    groups.append(group)
units=[]
for i,g in enumerate(groups):
    start=round(g[0]['StartSeconds']*1e6)
    end=round(groups[i+1][0]['StartSeconds']*1e6) if i+1<len(groups) else round(g[-1]['EndSeconds']*1e6)
    rendered=[dict(text=r['Char'],startUs=round(r['StartSeconds']*1e6)) for r in g]
    # Sentence terminators belong only to the last window of their sentence.
    original_idx=next(j for j,r in enumerate(rows) if r is g[-1])
    for r in rows[original_idx+1:]:
        if r['Char'] not in punct:break
        if r['Char'] in '。！？':
            rendered[-1]['text']+=r['Char']
    units.append(dict(startUs=start,endUs=end,chars=rendered))
scene['subtitles']=units
for s in scene['scenes']:
    for n in s['nodes']:
        if n['type']=='path' and n['x']==190 and n['y']==650:
            n['y']=735
html=(P/'index.html').read_text(encoding='utf-8')
data=json.dumps(scene,ensure_ascii=False).replace('<','\\u003c')
a=html.index('const data=')+len('const data=');b=html.index(';const config=',a)
html=html[:a]+data+html[b:]
# Explicit anchoring keeps the player button accessible at all viewport sizes.
html=html.replace('</style>','button{left:8px} </style>')
(P/'index.html').write_text(html,encoding='utf-8')
(P/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=json.loads((P/'vibe.project.json').read_text(encoding='utf-8'))
for name in ['scene.json','index.html','script.txt','timeline.txt']:
    manifest['assetHashes'][name]=hashlib.sha256((P/name).read_bytes()).hexdigest()
(P/'vibe.project.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Finalized:',len(scene['scenes']),'scenes;',len(units),'semantic caption units')
