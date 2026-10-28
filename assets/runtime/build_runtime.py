"""Deterministic background-source bundler. Generated scene.mjs remains self-contained."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

MODULES={'bio-bubbles':'drawBioBubbles','constellation':'drawConstellation','dna-spiral':'drawDnaSpiral','cyber-grid':'drawCyberGrid','aurora-dust':'drawAuroraDust'}


def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def pairs(items):
    result={}
    for key,value in items:
        if key in result:raise ValueError('Duplicate catalog key: '+key)
        result[key]=value
    return result


def catalog(root):
    root=Path(root)
    data=json.loads((root/'backgrounds/catalog.json').read_text(encoding='utf-8'),object_pairs_hook=pairs)
    if set(data)!={'version','libraryVersion','presets'} or data['version']!=1 or not re.fullmatch(r'\d+\.\d+\.\d+',data['libraryVersion']):raise ValueError('Unsupported background library')
    if [x.get('id') for x in data['presets']]!=[*MODULES,'solid']:raise ValueError('Catalog must cover the fixed renderer modules in order')
    lock=json.loads((root/'backgrounds/versions.lock.json').read_text(encoding='utf-8'),object_pairs_hook=pairs)
    if set(lock)!={'version','templates'} or lock['version']!=1:raise ValueError('Invalid background version lock')
    for entry in data['presets']:
        if set(entry)!={'id','version','label','subjects','recipe','qa'} or not re.fullmatch(r'\d+\.\d+\.\d+',entry['version']) or not entry['label']:raise ValueError('Invalid preset identity')
        if not isinstance(entry['subjects'],list) or not all(isinstance(x,str) and x for x in entry['subjects']):raise ValueError('Invalid subject tags')
        keys=set(re.findall(r'recipe\.([A-Za-z]+)',(root/'backgrounds'/(entry['id']+'.mjs')).read_text(encoding='utf-8'))) if entry['id']!='solid' else set()
        if set(entry['recipe'])!=keys:raise ValueError('Recipe parameters must match actual renderer use: '+entry['id'])
        for key,value in entry['recipe'].items():
            if key in ('primary','secondary'):
                if not isinstance(value,str) or not re.fullmatch(r'\d{1,3},\d{1,3},\d{1,3}',value) or any(int(c)>255 for c in value.split(',')):raise ValueError('Invalid recipe colour')
            elif type(value) not in (int,float) or not math.isfinite(value) or not 0<value<=1024:raise ValueError('Invalid numeric recipe parameter')
            elif any(token in key.lower() for token in ('count','rows','cols','columns','every')) and (type(value)!=int or value>256):raise ValueError('Invalid particle/grid budget')
            elif any(token in key.lower() for token in ('alpha','opacity','amplitude','horizon')) and value>1:raise ValueError('Invalid fractional recipe parameter')
        qa=entry['qa']
        if set(qa)!={'dynamic','minVisiblePixels','minChangedPixels','columns','rows','minPixelsPerCell','minCoveredCells','regions'} or type(qa['dynamic'])!=bool:raise ValueError('Invalid per-preset QA')
        for key in ('columns','rows','minPixelsPerCell','minCoveredCells','minVisiblePixels','minChangedPixels'):
            if type(qa[key])!=int or qa[key]<0:raise ValueError('Invalid QA threshold')
        if not 1<=qa['columns']*qa['rows']<=64 or not 0<=qa['minCoveredCells']<=qa['columns']*qa['rows']:raise ValueError('Invalid QA coverage grid')
        if qa['dynamic']!=(entry['id']!='solid'):raise ValueError('Dynamic status does not match the renderer')
        if qa['dynamic'] and (min(qa['minVisiblePixels'],qa['minChangedPixels'],qa['minPixelsPerCell'])<16 or qa['minCoveredCells']<1):raise ValueError('Dynamic QA cannot be disabled')
        for region in qa['regions']:
            if set(region)!={'name','box','minPixels'} or not region['name'] or len(region['box'])!=4 or type(region['minPixels'])!=int or region['minPixels']<16:raise ValueError('Invalid QA region')
            x,y,w,h=region['box']
            if any(type(v) not in (int,float) or not math.isfinite(v) for v in (x,y,w,h)) or min(x,y)<0 or min(w,h)<=0 or x+w>1 or y+h>1:raise ValueError('QA region escapes canvas')
        expected=dict(recipeSha256=hashlib.sha256(canonical(entry['recipe']).encode()).hexdigest(),moduleSha256=hashlib.sha256((root/'backgrounds'/(entry['id']+'.mjs')).read_bytes()).hexdigest() if entry['id']!='solid' else hashlib.sha256(b'').hexdigest(),commonSha256=hashlib.sha256((root/'backgrounds/common.mjs').read_bytes()).hexdigest(),qaSha256=hashlib.sha256(canonical(entry['qa']).encode()).hexdigest())
        if lock['templates'].get(entry['id']+'@'+entry['version'])!=expected:raise ValueError('Background version lock mismatch; publish a new reviewed template version: '+entry['id'])
    return data


def entries_with_identity(root):
    data=catalog(root)
    return data,[dict(**e,recipeSha256=hashlib.sha256(canonical(e['recipe']).encode()).hexdigest()) for e in data['presets']]


def source_paths(root):
    root=Path(root)
    return [root/'build_runtime.py',root/'scene-core.mjs',root/'backgrounds/catalog.json',root/'backgrounds/versions.lock.json',root/'backgrounds/common.mjs',*[root/'backgrounds'/(name+'.mjs') for name in MODULES]]


def compile_runtime(root):
    root=Path(root);data,entries=entries_with_identity(root)
    digest=hashlib.sha256()
    for p in source_paths(root):digest.update(str(p.relative_to(root)).replace('\\','/').encode()+b'\0'+p.read_bytes()+b'\0')
    common=(root/'backgrounds/common.mjs').read_text(encoding='utf-8')
    modules='\n'.join(re.sub(r'(?m)^import [^\n]+\n','',(root/'backgrounds'/(name+'.mjs')).read_text(encoding='utf-8')) for name in MODULES)
    registry='''
function freezeBackground(value){if(value&&typeof value==='object'){Object.values(value).forEach(freezeBackground);Object.freeze(value);}return value;}
export const BACKGROUND_LIBRARY_VERSION=__LIBRARY_VALUE__;
export const BACKGROUND_CATALOG=freezeBackground(ENTRIES);
export const BACKGROUND_PRESETS=Object.freeze(BACKGROUND_CATALOG.map(e=>e.id));
export function getBackgroundPreset(id){const entry=BACKGROUND_CATALOG.find(e=>e.id===id);if(!entry)fail('Unknown background preset');return entry;}
const backgroundRenderers=RENDERERS;
export function drawBackground(ctx,bg,timeUs,w,h){
    const preset=bg?.preset;if(!preset)return;
    const entry=getBackgroundPreset(preset);if(preset==='solid')return;
    const frame=backgroundFrame(ctx,bg,timeUs,w,h);
    ctx.save();ctx.globalAlpha=1;backgroundRenderers[preset](ctx,frame,entry.recipe);ctx.restore();
}
'''.replace('__LIBRARY_VALUE__',json.dumps(data['libraryVersion'])).replace('ENTRIES',canonical(entries)).replace('RENDERERS','{'+','.join(json.dumps(k)+':'+v for k,v in MODULES.items())+'}')
    bundle='// @generated backgrounds source-sha256: '+digest.hexdigest()+'\n'+common+'\n'+modules+'\n'+registry
    core=(root/'scene-core.mjs').read_text(encoding='utf-8')
    if core.count('/*__VIBE_BACKGROUND_BUNDLE__*/')!=1:raise ValueError('Core needs exactly one background bundle insertion point')
    return core.replace('/*__VIBE_BACKGROUND_BUNDLE__*/',bundle).encode('utf-8')


def verify(root):
    root=Path(root)
    if (root/'scene.mjs').read_bytes()!=compile_runtime(root):raise ValueError('Generated runtime is stale; rebuild backgrounds upstream and synchronize identity/mirror')
    return hashlib.sha256((root/'scene.mjs').read_bytes()).hexdigest()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:print(verify(a.root))
    else:
        (a.root/'scene.mjs').write_bytes(compile_runtime(a.root));print(verify(a.root))
