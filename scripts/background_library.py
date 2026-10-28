"""Trusted catalog access and canonical, self-contained background gallery."""
import importlib.util
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/'assets/runtime'


@lru_cache(maxsize=1)
def builder():
    # Only developer-owned Studio code is imported, never code from an input project.
    spec=importlib.util.spec_from_file_location('vibe_background_builder',RUNTIME/'build_runtime.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def catalog():return builder().entries_with_identity(RUNTIME)[1]

def library_version():return builder().catalog(RUNTIME)['libraryVersion']


def preset(preset_id,version=None):
    entry=next((e for e in catalog() if e['id']==preset_id),None)
    if not entry or version is not None and version!=entry['version']:raise ValueError('Unknown background template/version: '+str(preset_id))
    return entry


def verify_runtime(runtime=None):return builder().verify(runtime or RUNTIME)


def background_errors(probe,entry):
    """Per-style acceptance: a helix column is not a full-field bubble background."""
    qa=entry['qa'];errors=[]
    if not qa['dynamic']:return errors
    if probe['visiblePixels']<qa['minVisiblePixels'] or probe['changedPixels']<qa['minChangedPixels']:
        errors.append(('BACKGROUND','Selected template is not visibly rendered and moving'))
    for sample in probe['coverage']:
        if sample['coveredCells']<qa['minCoveredCells']:
            errors.append(('BACKGROUND_COVERAGE','Template does not cover its expected field: '+entry['id']))
        regions={x['name']:x['visiblePixels'] for x in sample.get('regions',[])}
        for region in qa['regions']:
            if regions.get(region['name'],0)<region['minPixels']:
                errors.append(('BACKGROUND_REGION','Template region is missing: '+entry['id']+'/'+region['name']))
    return errors


def gallery_html():
    verify_runtime()
    runtime=re.sub(r'(?m)^export ','',(RUNTIME/'scene.mjs').read_text(encoding='utf-8'))
    return GALLERY.replace('/*__BACKGROUND_RUNTIME__*/',runtime)


def gallery(out):
    out=Path(out).resolve();html=gallery_html();target=out/'index.html'
    if target.exists():
        if target.read_text(encoding='utf-8')!=html:raise ValueError('Gallery already exists with different content; choose a new version directory')
    else:
        if out.exists() and any(out.iterdir()):raise ValueError('Use a dedicated new gallery directory')
        out.mkdir(parents=True,exist_ok=True);target.write_text(html,encoding='utf-8')
    return target


def run(args):
    if args.check:print('Background bundle verified: '+verify_runtime())
    elif getattr(args,'audit',False):
        from scripts.background_audit import audit
        report=audit(args.out)
        print(json.dumps(dict(status=report['status'],errors=report['errors'],presets=len(report['presets']),screenshots=len(report['screenshots']),output=report['output']),ensure_ascii=False,indent=2))
        if report['status']!='automated_pass':raise SystemExit(1)
    elif args.gallery:print(gallery(args.out or ROOT/'previews/background-library-v2'))
    else:print(json.dumps([dict(id=e['id'],version=e['version'],label=e['label'],subjects=e['subjects']) for e in catalog()],ensure_ascii=False,indent=2))


GALLERY=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'">
<title>VIBE 背景模板库</title><style>
*{box-sizing:border-box}body{margin:0;background:#081512;color:#eef9f3;font:16px 'Microsoft YaHei',sans-serif}header{padding:16px;display:flex;gap:12px;flex-wrap:wrap;align-items:center;border-bottom:1px solid #28554b}h1{font-size:20px;margin:0}button,select,input[type=range]{min-height:44px}button,select{background:#153b32;color:#eef9f3;border:1px solid #447769;border-radius:8px;padding:8px}label{min-height:44px;display:flex;gap:8px;align-items:center}main{display:flex;justify-content:center;gap:28px;padding:20px;align-items:flex-start}canvas{display:block;width:min(380px,90vw);height:auto;border:1px solid #28554b;border-radius:8px}aside{max-width:390px}pre,textarea{white-space:pre-wrap;overflow-wrap:anywhere;font-size:14px}textarea{width:100%;height:92px;background:#102b24;color:#65efb5;border:1px solid #28554b;padding:12px}#error{color:#ffb89b}#time{width:160px}@media(max-width:740px){main{flex-direction:column;align-items:center}aside{width:100%}}
</style><header><h1>背景模板库</h1><select id="preset" aria-label="背景模板"></select><label><input id="overlay" type="checkbox" checked>叠加文字示例</label><button id="play" type="button">暂停</button><button id="reset" type="button">重置</button><input id="time" aria-label="预览进度" type="range" min="0" max="30" step="0.1"><span id="clock">00:00</span></header>
<main><canvas aria-label="背景动态预览"></canvas><aside><h2 id="name"></h2><p id="identity"></p><p id="subjects"></p><p>配方固定，制作时只选择模板。可暂停、拖动时间，或关闭文字检查背景本身。</p><label for="snippet">故事参数</label><textarea id="snippet" readonly></textarea><details><summary>固定配方与检查区域</summary><pre id="recipe"></pre></details><p id="error" role="alert"></p></aside></main>
<script>/*__BACKGROUND_RUNTIME__*/
const select=document.querySelector('#preset'),canvas=document.querySelector('canvas'),overlay=document.querySelector('#overlay'),slider=document.querySelector('#time'),button=document.querySelector('#play');
for(const e of BACKGROUND_CATALOG){const o=document.createElement('option');o.value=e.id;o.textContent=e.label;select.append(o);}
let renderer=null,playing=true,base=0,started=performance.now(),generation=0,currentTime=0;
function sampleNodes(){return [
{id:'panel',type:'rect',x:130,y:620,width:820,height:340,background:'#10332f',color:'#28554b',radius:24},
{id:'title',type:'text',x:130,y:220,width:820,height:90,text:'知识讲解 · 背景示例',size:48,color:'#65efb5',align:'center',verticalAlign:'center'},
{id:'heading',type:'text',x:130,y:440,width:820,height:92,text:'让背景衬托内容',size:58,color:'#eef9f3',align:'center',verticalAlign:'center'},
{id:'text',type:'text',x:170,y:690,width:740,height:180,text:'文字清晰\n画面有层次',size:52,color:'#eef9f3',align:'center',verticalAlign:'center'},
{id:'caption',type:'text',x:150,y:1570,width:780,height:74,text:'字幕可读性示例',size:46,color:'#65efb5',align:'center',verticalAlign:'center'}];}
async function prepare(){const run=++generation,e=getBackgroundPreset(select.value);renderer=null;document.querySelector('#error').textContent='';
 document.querySelector('#name').textContent=e.label;document.querySelector('#identity').textContent='模板 '+e.version+' · 背景库 '+BACKGROUND_LIBRARY_VERSION;document.querySelector('#subjects').textContent=e.subjects.length?'适用：'+e.subjects.join('、'):'纯色仅在明确选择时使用';
 document.querySelector('#snippet').value=JSON.stringify({backgroundPreset:e.id},null,2);document.querySelector('#recipe').textContent=JSON.stringify({recipe:e.recipe,qa:e.qa},null,2);
 const nodes=overlay.checked?sampleNodes():[{id:'empty',type:'rect',x:0,y:0,width:1,height:1,color:'#071d1b',background:'#071d1b'}];
 try{const scene={background:{color:'#071d1b',preset:e.id,templateVersion:e.version,recipeSha256:e.recipeSha256,particles:false,seed:8},scenes:[{id:'gallery',startUs:0,endUs:30000000,nodes}]},config={width:1080,height:1920,durationUs:30000000,assetBase:location.href,safeArea:false};const r=await prepareScene(canvas,scene,config);if(run!==generation)return;renderer=r;window.__galleryScene=scene;window.__galleryConfig=config;window.__galleryRenderer=r;base=0;started=performance.now();draw(0);window.__galleryReady=true;}catch(error){document.querySelector('#error').textContent=error.message;throw error;}}
function draw(seconds){currentTime=seconds;renderer?.renderAt(Math.min(29999999,Math.round(seconds*1e6)));slider.value=seconds;document.querySelector('#clock').textContent='00:'+String(Math.floor(seconds)).padStart(2,'0');}
function tick(){if(renderer&&playing)draw((base+(performance.now()-started)/1000)%30);requestAnimationFrame(tick);}
button.addEventListener('click',()=>{if(playing)base=currentTime;else started=performance.now();playing=!playing;button.textContent=playing?'暂停':'播放';});
slider.addEventListener('input',()=>{base=Number(slider.value);started=performance.now();draw(base);});document.querySelector('#reset').addEventListener('click',()=>{base=0;started=performance.now();draw(0);});
select.addEventListener('change',()=>{window.__galleryReady=false;prepare();});overlay.addEventListener('change',()=>{window.__galleryReady=false;prepare();});window.__gallerySeek=t=>{base=t;started=performance.now();draw(t);};window.__galleryReady=false;prepare();requestAnimationFrame(tick);
</script></html>'''
