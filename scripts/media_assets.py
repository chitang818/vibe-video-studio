"""Import agent-acquired local/search/generated images without provider credentials."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from PIL import Image
from scripts.text_contract import strict_loads
from scripts.contracts import validate_document


def inspect_image(path):
    with Image.open(path) as im:
        if im.format not in ('PNG','JPEG','WEBP'):raise ValueError('Use PNG, JPEG or WebP images')
        if getattr(im,'n_frames',1)!=1:raise ValueError('Animated images are not deterministic slide assets')
        width,height=im.size
        if min(width,height)<256 or width*height>16000000:raise ValueError('Image must be >=256px each side and <=16 megapixels')
        im.verify()
    with Image.open(path) as im:im.load()
    return width,height


def import_image(source, root, asset_id, kind='local', origin='', license_status='', focus=(.5,.5)):
    root=Path(root).resolve();source=Path(source).resolve()
    if not re.fullmatch('[A-Za-z][A-Za-z0-9-]{0,63}',asset_id):raise ValueError('Invalid asset ID')
    if kind not in ('local','search','generate'):raise ValueError('Unknown acquisition kind')
    if not origin or not license_status:raise ValueError('Record source/generation provenance and license status')
    if kind=='search' and not origin.startswith('https://'):raise ValueError('Search assets require the original HTTPS page')
    if license_status not in ('user-provided','original','licensed','public-domain','provider-terms'):raise ValueError('Unresolved image permission')
    if kind=='search' and license_status not in ('licensed','public-domain'):raise ValueError('Search license must be resolved')
    if len(focus)!=2 or any(type(v) not in (int,float) or not 0<=v<=1 for v in focus):raise ValueError('Invalid image focus')
    width,height=inspect_image(source)
    from scripts.build_fast_project import asset_path
    registry=asset_path(root,'assets/media-registry.json')
    data=strict_loads(registry.read_text(encoding='utf-8')) if registry.exists() else dict(version=1,assets=[])
    validate_document('media-registry',data)
    if any(a['id']==asset_id for a in data['assets']):raise ValueError('Asset ID already registered; use a new ID')
    suffix=source.suffix.lower()
    if suffix not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('Invalid image extension')
    relative=f'assets/images/{asset_id}{suffix}';target=asset_path(root,relative)
    if target.exists():raise ValueError('Refusing to overwrite an asset')
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    entry=dict(id=asset_id,source=relative,kind=kind,origin=origin,licenseStatus=license_status,width=width,height=height,
        sha256=hashlib.sha256(target.read_bytes()).hexdigest(),focusX=focus[0],focusY=focus[1])
    data['assets'].append(entry);registry.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return entry


def validate_registry(root,assets,policy='local'):
    from scripts.build_fast_project import asset_path
    root=Path(root)
    if not assets:return []
    registry=asset_path(root,'assets/media-registry.json')
    data=strict_loads(registry.read_text(encoding='utf-8'))
    validate_document('media-registry',data)
    if set(data)!={'version','assets'} or data['version']!=1:raise ValueError('Invalid media registry')
    entries={a['id']:a for a in data['assets']}
    if len(entries)!=len(data['assets']):raise ValueError('Duplicate registered asset IDs')
    selected=[]
    for a in assets:
        e=entries.get(a['id'])
        if not e or e['source']!=a['source']:raise ValueError('Asset reference is not registered')
        if e['kind'] not in ('local','search','generate') or not e['origin'] or e['licenseStatus'] not in ('user-provided','original','licensed','public-domain','provider-terms'):raise ValueError('Unresolved provenance')
        if e['kind']=='search' and (not e['origin'].startswith('https://') or e['licenseStatus'] not in ('licensed','public-domain')):raise ValueError('Unresolved search permission')
        if policy!='mixed' and e['kind']!=policy:raise ValueError('Asset conflicts with selected acquisition policy')
        path=asset_path(root,e['source']);dims=inspect_image(path)
        if dims!=(e['width'],e['height']) or hashlib.sha256(path.read_bytes()).hexdigest()!=e['sha256']:raise ValueError('Registered image changed')
        selected.append(e)
    return selected


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--root',type=Path,required=True)
    p.add_argument('--id',required=True);p.add_argument('--kind',choices=['local','search','generate'],default='local')
    p.add_argument('--origin',required=True);p.add_argument('--license',required=True)
    p.add_argument('--focus-x',type=float,default=.5);p.add_argument('--focus-y',type=float,default=.5)
    a=p.parse_args();print(json.dumps(import_image(a.source,a.root,a.id,a.kind,a.origin,a.license,(a.focus_x,a.focus_y)),ensure_ascii=False))


if __name__=='__main__':main()
