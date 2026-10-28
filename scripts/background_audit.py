"""Bounded automated checks and screenshots for the fixed background gallery."""
import hashlib
import json
import uuid
from pathlib import Path
from playwright.sync_api import sync_playwright
from scripts.background_library import ROOT,catalog,gallery,verify_runtime,background_errors
from scripts.quality_browser import BACKGROUND_PROBE,GEOMETRY


def audit(out=None):
    out=Path(out or ROOT/'artifacts/background-library'/uuid.uuid4().hex).resolve()
    if out.exists():raise ValueError('Audit output must be a new directory')
    runtime_sha=verify_runtime();out.mkdir(parents=True)
    page_path=gallery(out/'gallery');frames=out/'frames';frames.mkdir()
    report=dict(status='blocked',toolSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),runtimeSha256=runtime_sha,output=str(out),scope='automated template/UI checks; visual approval remains separate',errors=[],presets=[],screenshots=[])
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page(viewport={'width':1100,'height':900})
        page.on('pageerror',lambda e:report['errors'].append(dict(rule='GALLERY',detail=str(e))))
        page.goto(page_path.as_uri());page.wait_for_function('window.__galleryReady===true');page.locator('#play').click()
        for entry in catalog():
            page.select_option('#preset',entry['id'])
            page.wait_for_function('id=>window.__galleryReady===true&&window.__galleryScene.background.preset===id',arg=entry['id'])
            page.evaluate('window.__vibe_scene=window.__galleryScene;window.config=window.__galleryConfig')
            probe=page.evaluate(BACKGROUND_PROBE,entry['qa']);issues=background_errors(probe,entry)
            for rule,detail in issues:report['errors'].append(dict(rule=rule,detail=detail,preset=entry['id']))
            page.evaluate('()=>{window.__vibe_textRaster=(s,n)=>window.__galleryRenderer.textRaster(s,n);}')
            geometry=page.evaluate(GEOMETRY)
            if any(g.get('glyphClipped') for g in geometry):report['errors'].append(dict(rule='TEXT_CLIP',preset=entry['id']))
            for overlay in (True,False):
                page.locator('#overlay').set_checked(overlay)
                page.wait_for_function('window.__galleryReady===true')
                for time in (0,4,15):
                    page.evaluate('t=>window.__gallerySeek(t)',time)
                    name=f"frames/{entry['id']}-{'overlay' if overlay else 'background'}-{time}.png"
                    target=out/name;page.locator('canvas').screenshot(path=str(target));report['screenshots'].append(dict(file=name,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
                page.evaluate('window.__gallerySeek(4)');first=page.locator('canvas').screenshot();page.evaluate('window.__gallerySeek(15)');page.evaluate('window.__gallerySeek(4)')
                if page.locator('canvas').screenshot()!=first:report['errors'].append(dict(rule='DETERMINISM',preset=entry['id']))
            page.locator('#overlay').check();page.wait_for_function('window.__galleryReady===true')
            report['presets'].append(dict(id=entry['id'],version=entry['version'],recipeSha256=entry['recipeSha256'],probe=probe))
        page.select_option('#preset','bio-bubbles');page.wait_for_function("window.__galleryReady&&window.__galleryScene.background.preset==='bio-bubbles'")
        page.evaluate('window.__gallerySeek(4)')
        for width in (320,440):
            page.set_viewport_size(dict(width=width,height=956))
            if not page.evaluate('document.documentElement.scrollWidth<=innerWidth'):report['errors'].append(dict(rule='GALLERY_LAYOUT',width=width))
            image=out/f'gallery-mobile-{width}.png';page.screenshot(path=str(image),full_page=True);report['screenshots'].append(dict(file=image.name,sha256=hashlib.sha256(image.read_bytes()).hexdigest()))
        browser.close()
    report['status']='blocked' if report['errors'] else 'automated_pass'
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
