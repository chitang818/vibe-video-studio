"""N0009 content authoring: constrained scene data, no custom player code."""
import sys,json,wave,re,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.components import compile_story
from scripts.text_contract import clean,quote_at
from scripts.build_fast_project import preset_wave
HERE=Path(__file__).parent
SOURCE=Path('C:/Users/chitang/Downloads/N0009_丛枝菌根作用与优势')
rows=json.loads((SOURCE/'N0009_char_timestamps.json').read_text(encoding='utf-8-sig'))
with wave.open(str(SOURCE/'N0009_voice.wav')) as w:duration=round(w.getnframes()/w.getframerate()*1e6)

# Each cut is an original spoken phrase, not a division of total duration.
shots=[
('回顾：菌剂与菌根','classification','上一期我们介绍了',[
 ('我们介绍了','真菌类菌剂的分类'),('和肥料类菌剂','肥料类菌剂中的菌根'),('基本特性','连接上期基本特性')]),
('这期看机制与应用','process','这一期我们着重讲一下',[
 ('着重讲一下','从吸收机制开始'),('养分吸收机制','看养分如何到达植物'),('是如何促进植物','再看实际应用优势')]),
('磷为何难被吸收','comparison','一、强化磷元素的吸收',[
 ('强化磷元素','磷素吸收是重点'),('被土壤颗粒固定','磷被土壤颗粒固定'),('移动性差','移动性差'),('难以被植物吸收','根系难以直接获取')]),
('菌丝延伸，磷素转运','process','丛枝菌根的根外菌丝可以延伸',[
 ('根外菌丝可以','菌丝向根外延伸'),('更大范围','扩大探索范围'),('难溶性磷','难溶性磷转运过程'),('提升植物磷素','提升植物磷素供应')]),
('氮素转运与微生物协同','exchange','二、辅助氮元素的吸收',[
 ('丛枝菌根的菌丝可以转运','菌丝转运无机氮'),('同时还能和土壤','与固氮微生物协同'),('帮助植物更高效','帮助植物获取氮素'),('减少氮肥的','减少氮肥流失浪费')]),
('不止大量元素','classification','三、帮助微量元素的吸收',[
 ('除了大量元素','还关注微量元素'),('土壤中的锌','锌、铜、铁等元素'),('减少作物缺素','减少缺素症状'),('在贫瘠土壤中','关注贫瘠土壤条件')]),
('菌丝向根外拓展','cross-section','丛枝菌根促进养分吸收的原因',[
 ('主要是菌丝拓展','拓展养分吸收面积'),('根外菌丝的总长度','根外菌丝继续延伸'),('数十倍甚至上百倍','根外菌丝扩大探索面')]),
('从根际走向周边土壤','process','让植物根系的养分吸收范围',[
 ('养分吸收范围','从根际附近开始'),('周边更大体积','延伸到周边土体'),('大幅提升了养分','提升养分获取能力')]),
('养分形态转化','process','同时，丛枝菌根共生过程中',[
 ('分泌一些有机酸','共生过程分泌有机酸'),('被固定的矿质养分','作用于固定矿质养分'),('可以吸收利用的形态','转为可吸收利用形态'),('提升土壤养分','提高养分利用率')]),
('根内丛枝：双向交换','exchange','根内形成的丛枝结构',[
 ('丛枝结构拥有','丛枝扩大交换界面'),('植物将光合作用','植物向真菌供碳'),('碳水化合物传递','传递碳水化合物'),('真菌将吸收的养分','真菌向植物供养分')]),
('从交换机制到应用','comparison','双向交换效率远高于',[
 ('远高于普通吸附交换','双向交换对照吸附交换'),('提升了养分交换','提升养分交换效率'),('实际的应用优势','进一步看实际应用')]),
('肥料利用与生产成本','process','首先是刚才讲到的',[
 ('促进养分的高效利用','促进养分高效利用'),('提升磷肥的利用率','提升磷肥利用率'),('减少化肥的施用量','减少化肥施用量'),('降低农业生产成本','降低生产成本')]),
('减少流失，关注水体','process','同时减少养分淋失',[
 ('减少养分淋失','减少养分淋失'),('水体富营养化','关注水体富营养化'),('生态效益突出','兼顾生态效益'),('土壤生态的改善','转向土壤生态改善')]),
('土壤生态的多个层面','classification','能够促进土壤团聚体形成',[
 ('土壤团聚体形成','促进团聚体形成'),('提升土壤固碳能力','提升土壤固碳能力'),('优化土壤微生物群落','优化微生物群落'),('构建土壤菌丝网络','构建菌丝网络')]),
('缠绕与粘合共同作用','cross-section','这些应用优势根本的原因',[
 ('菌丝的物理缠绕作用','菌丝形成物理缠绕'),('菌丝分泌的粘合物质','分泌粘合物质')]),
('微团聚体聚合','process','可以促进土壤微团聚体',[
 ('微团聚体聚合','微团聚体发生聚合'),('大团聚体','形成大团聚体'),('改善土壤的物理结构','改善土壤物理结构'),('降低土壤板结的风险','降低板结风险')]),
('根际群落的协同','comparison','同时会和根际的有益微生物',[
 ('有益微生物产生协同','根际微生物协同'),('促进有益微生物','有益微生物定殖繁殖'),('抑制有害微生物','抑制有害微生物生长'),('维持根际微生物群落','维持群落健康稳定')]),
('地下共同菌丝网络','ending','然后，丛枝菌根的菌丝',[
 ('连接不同植物','连接不同植物根系'),('地下共同菌丝网络','形成共同菌丝网络'),('转移分配','养分转移与分配'),('养分平衡','回扣农田养分平衡')]),
]
def spec(phrase):
 hits=[i for i in range(len(rows)) if quote_at(rows,i,phrase)]
 if len(hits)!=1:raise ValueError((phrase,len(hits)))
 return dict(quote=phrase,occurrence=1)
story=dict(version=1,title='丛枝菌根作用与优势',authorId='n0009-generation-agent',scenes=[])
for i,(heading,kind,cut,stages) in enumerate(shots):
 story['scenes'].append(dict(id=f'shot-{i+1:02}',kind=kind,heading=heading,anchor=spec(cut),stages=[dict(text=label,anchor=spec(q)) for q,label in stages]))
scene,plan=compile_story(story,rows,duration)

# Protect technical terms; the original audio and transcript are never rewritten.
scene['protectedTerms']=['丛枝菌根','根外菌丝','根内','碳水化合物','微量元素','微生物','团聚体','富营养化','数十倍','上百倍']

# Bespoke biological paths, in local 620x330 coordinates, replace generic blocks.
def tube(points,width=9):
 # Piecewise polygon strips; every stroke remains inside declared geometry.
 parts=[]
 for (x,y),(a,b) in zip(points,points[1:]):
  length=math.hypot(a-x,b-y);dx=(b-y)/length*width/2;dy=(x-a)/length*width/2
  parts.append(f'M{x+dx:g} {y+dy:g} L{a+dx:g} {b+dy:g} L{a-dx:g} {b-dy:g} L{x-dx:g} {y-dy:g} Z')
 return ' '.join(parts)
def disk(x,y,r):return f'M{x-r:g} {y:g} A{r} {r} 0 1 0 {x+r:g} {y:g} A{r} {r} 0 1 0 {x-r:g} {y:g} Z'
def arrow(x,y,w=80,reverse=False):
 p=f'M{x} {y-8} H{x+w-22} V{y-23} L{x+w} {y} L{x+w-22} {y+23} V{y+8} H{x} Z'
 return p
root=tube([(306,20),(306,98),(270,145),(247,218),(211,290)],15)+tube([(306,98),(349,154),(375,235),(415,294)],14)+tube([(270,145),(203,167),(171,222)],10)+tube([(349,154),(427,182),(462,248)],10)
hyphae=[tube([(211,290),(123,258),(45,294)],6)+tube([(123,258),(90,195),(25,168)],5),tube([(247,218),(166,143),(62,108)],6)+tube([(166,143),(148,58),(76,32)],5),tube([(375,235),(485,273),(590,235)],6)+tube([(485,273),(525,317)],5),tube([(427,182),(511,115),(589,81)],6)+tube([(511,115),(492,38)],5)]
soil=' '.join(disk(x,y,r) for x,y,r in [(72,72,30),(129,212,28),(214,79,23),(400,71,29),(514,217,32),(567,138,22)])
clusters=[' '.join(disk(x+dx,y+dy,r) for dx,dy,r in [(-22,0,20),(16,-23,23),(23,19,22),(-13,30,18)]) for x,y in [(90,165),(300,165),(510,165)]]
microbes=[' '.join(disk(x+dx,y+dy,r) for dx,dy,r in [(-30,-30,20),(25,-20,25),(0,30,18)]) for x,y in [(115,150),(310,150),(505,150)]]
leaf='M306 70 C210 65 177 10 170 20 C168 115 220 143 306 140 Z M315 72 C380 0 448 30 455 20 C453 117 395 144 315 140 Z '+tube([(310,115),(310,300)],14)
cell='M30 30 H590 V300 H30 Z M48 48 V282 H572 V48 Z'
arbuscule=tube([(310,290),(310,200),(270,160),(225,100)],12)+tube([(310,200),(360,140),(405,90)],10)+tube([(270,160),(210,185),(140,135)],8)+tube([(360,140),(440,185),(500,145)],8)+tube([(270,160),(287,82)],7)

# Each diagram is different in actual structure. Highlighted parts appear on spoken anchors.
art=[
 (root,[soil,*hyphae[:2]]),
 (root,[hyphae[0],hyphae[2],arrow(265,185)]),
 (soil,[disk(72,72,12),disk(214,79,12),tube([(300,50),(300,290)],14),root]),
 (root,hyphae),
 (root,[hyphae[0],microbes[2],arrow(445,182),hyphae[2]]),
 (root,[hyphae[0],disk(65,60,22)+disk(545,65,26)+disk(552,278,18),hyphae[2],hyphae[3]]),
 (root,hyphae[:3]),
 (root,[hyphae[0],hyphae[1]+hyphae[3],hyphae[2]]),
 (soil,[disk(310,165,24),arrow(230,165),disk(515,70,13)+disk(555,100,12),arrow(440,165)]),
 (cell,[arbuscule,arrow(62,90,120),'M535 220 H447 V205 L425 228 L447 251 V236 H535 Z',disk(525,88,23)]),
 (arbuscule,[arrow(72,90,100),arrow(430,230,100),leaf]),
 (leaf,[hyphae[0],disk(90,185,25)+disk(530,185,25),arrow(155,215,100),hyphae[2]]),
 (tube([(30,210),(110,190),(185,235),(270,222),(350,260),(440,247),(590,275)],12),[root,arrow(300,122,100),leaf,clusters[0]]),
 (root,[clusters[0],leaf,microbes[2],hyphae[3]]),
 (clusters[1],[tube([(210,25),(235,95),(225,235),(265,300)],10)+tube([(390,25),(365,95),(385,235),(345,300)],10),disk(190,150,12)+disk(425,165,14)]),
 (clusters[0],[clusters[1],clusters[2],tube([(130,120),(300,82),(510,120)],7),tube([(130,240),(300,278),(510,240)],7)]),
 (tube([(65,290),(65,220),(115,170),(115,30)],14)+tube([(550,290),(550,220),(505,170),(505,30)],14),[microbes[0],microbes[1],microbes[2],tube([(160,250),(300,290),(460,250)],7)]),
 (tube([(95,15),(95,115),(140,215),(200,295)],14)+tube([(520,15),(520,115),(475,215),(415,295)],14),[tube([(140,215),(230,180),(310,235)],7),tube([(310,235),(390,180),(475,215)],7),arrow(230,130,150),disk(310,235,24)]),
]
for i,(s,p) in enumerate(zip(scene['scenes'],plan['scenes'])):
 base,layers=art[i]
 s['nodes']=[n for n in s['nodes'] if n['id']!='diagram' and not n['id'].startswith('graphic-stage-')]
 # A deliberate 1.6s construction phase replaces generic breathing.
 s['nodes'].insert(3,dict(id='mechanism-base',type='path',x=230,y=650,width=620,height=330,path=base,color='#8db6a4',enterDurationUs=1600000))
 p['roles']['graphic']=['mechanism-base']
 for j,b in enumerate(p['beats']):
  gid=f'mechanism-layer-{j+1}'
  s['nodes'].append(dict(id=gid,type='path',x=230,y=650,width=620,height=330,path=layers[j],color=['#65efb5','#e8c778','#70d9ee','#d7a4e9'][j],enterUs=b['timeUs']-s['startUs'],enterDurationUs=min(1800000,s['endUs']-b['timeUs']-100000)))
  p['roles']['graphic'].append(gid);b['nodeIds']=[f'stage-{j+1}',gid]
  s['nodes'][next(k for k,n in enumerate(s['nodes']) if n['id']==f'stage-{j+1}')]['color']=['#65efb5','#e8c778','#70d9ee','#d7a4e9'][j]
 p['visualFamily']=['root-taxonomy','root-pathways','fixed-phosphorus','phosphorus-network','nitrogen-cooperation','trace-elements','hyphae-expansion','soil-volume','mineral-conversion','arbuscule-exchange','exchange-to-application','fertilizer-benefits','water-loss','soil-ecology','binding-mechanism','aggregation','microbial-cooperation','common-network'][i]
 p['visualIntent']='自定义根系/菌丝/土壤路径随原词逐层建立；'+shots[i][0]
plan['background']=dict(implementation='Shared deterministic seeded teal particles over #071d1b; no claimed bio-bubbles preset',rationale='深绿背景用于根际土壤主题，青绿/土金/浅蓝分别区分图解阶段；背景审美仍待复核')

# Explicit semantic windows: punctuation is restored from original timestamps by the compiler.
caption_text='''上一期我们介绍了|真菌类菌剂|有哪些分类，|和肥料类菌剂的|丛枝菌根真菌的|基本特性。|这一期我们|着重讲一下|丛枝菌根|促进植物的|养分吸收机制|和应用优势。|丛枝菌根|是如何促进植物的|养分吸收呢？|一、强化磷元素的吸收。|土壤中的磷元素|容易被土壤颗粒固定，|移动性差，|难以被植物吸收。|丛枝菌根的|根外菌丝|可以延伸到|更大范围，|将土壤中的|难溶性磷溶解后|转运给植物，|提升植物|磷素供应水平。|二、辅助氮元素的吸收。|丛枝菌根的菌丝|可以转运|土壤中的无机氮，|同时还能和|土壤中的|固氮微生物|形成协同作用，|帮助植物|更高效获取|氮素养分，|减少氮肥的|流失浪费。|三、帮助微量元素的吸收。|除了大量元素，|根外菌丝|还可以帮助植物|吸收土壤中的|锌、铜、铁等|微量元素，|减少作物|缺素症状的发生，|在贫瘠土壤中，|这一效果|尤为明显。|丛枝菌根|促进养分吸收的原因，|主要是菌丝|拓展了吸收面积。|根外菌丝的总长度|可以达到|植物根表面积的|数十倍甚至上百倍，|让植物根系的|养分吸收范围，|从根际拓展到|周边更大体积的土壤，|大幅提升了|养分获取能力。|同时，丛枝菌根|共生过程中|会分泌一些|有机酸类物质，|能够溶解|土壤中被固定的|矿质养分，|将其转化为|植物可以|吸收利用的形态，|提升土壤养分的|利用率。|根内形成的|丛枝结构|拥有极大的|交换面积，|植物将光合作用|合成的碳水化合物|传递给真菌，|真菌将吸收的养分|传递给植物，|双向交换效率|远高于普通吸附交换，|提升了养分交换的|效率。|那么丛枝菌根|都有哪些|实际的应用优势呢？|首先是刚才讲到的，|促进养分的|高效利用。|比如可以提升|磷肥的利用率，|减少化肥的施用量，|降低农业生产成本，|同时减少|养分淋失带来的|水体富营养化等|环境问题，|生态效益突出。|再有就是|对土壤生态的|改善作用，|能够促进|土壤团聚体形成，|提升土壤固碳能力，|优化土壤微生物群落，|构建土壤菌丝网络等。|这些应用优势|根本的原因，|在于菌丝的|物理缠绕作用，|加上菌丝|分泌的粘合物质，|可以促进|土壤微团聚体|聚合形成大团聚体，|改善土壤的|物理结构，|降低土壤板结的风险。|同时会和根际的|有益微生物|产生协同作用，|促进有益微生物的|定殖繁殖，|抑制有害微生物的生长，|维持根际微生物群落的|健康稳定。|然后，丛枝菌根的|菌丝可以连接|不同植物的根系，|形成地下|共同菌丝网络，|实现养分在|不同植物之间的|转移分配，|维持农田生态系统的|养分平衡。'''
captions=caption_text.strip().split('|')
if clean(''.join(captions))!=clean(''.join(r['Char'] for r in rows)):raise ValueError('Caption source mismatch')
# Four-character minimum also applies to sentence tails; merge short tails semantically.
for short in ['利用率。','效率。','生长，维持根际']:
 if short in captions:
  k=captions.index(short)
  if len(clean(short))<4:captions[k-1]+=captions.pop(k)
events=[]
for sound in ['whoosh','click','ding','chime']:
 p=HERE/f'assets/sounds/{sound}.wav';p.parent.mkdir(parents=True,exist_ok=True);preset_wave(p,sound)
for s in scene['scenes'][1:]:events.append(dict(timeUs=s['startUs'],source='assets/sounds/whoosh.wav',gain=.5))
for p in plan['scenes']:
 # One muted step accent per shot, not one sound per word.
 events.append(dict(timeUs=p['beats'][0]['timeUs'],source='assets/sounds/click.wav',gain=.45))
for index in [8,13]:events.append(dict(timeUs=plan['scenes'][index]['beats'][0]['timeUs'],source='assets/sounds/ding.wav',gain=.4))
events.append(dict(timeUs=plan['scenes'][-1]['beats'][-2]['timeUs'],source='assets/sounds/chime.wav',gain=.4))
for name,data in [('story.json',story),('scene.json',scene),('quality-plan.json',plan),('captions.json',captions),('sfx.json',dict(version=1,events=sorted(events,key=lambda e:e['timeUs'])))]:
 (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'keywords.txt').write_text('\n'.join(q+' | 原词锚点' for _,_,cut,stages in shots for q in [cut]+[q for q,_ in stages]),encoding='utf-8')
for s,p in zip(scene['scenes'],plan['scenes']):print(s['id'],round(s['startUs']/1e6,3),round(s['endUs']/1e6,3),[(round(b['timeUs']/1e6,3),b['quote']) for b in p['beats']])
