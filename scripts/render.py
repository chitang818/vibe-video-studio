# -*- coding: utf-8 -*-
"""VIBE 通用：HTML → 逐帧截图（playwright）
用法: python render.py <html路径> <输出帧目录> <时长秒> [fps=20] [start=0] [stop=全片]
     start>0 时支持瞬时 seek 预热，保障分段渲染效率与稳定性。
"""
import io, time, os, sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HTML = sys.argv[1] if len(sys.argv) > 1 else None
OUT = sys.argv[2] if len(sys.argv) > 2 else None
DUR = float(sys.argv[3]) if len(sys.argv) > 3 else None
FPS = float(sys.argv[4]) if len(sys.argv) > 4 else 20.0
START = int(sys.argv[5]) if len(sys.argv) > 5 else 0
STOP = int(sys.argv[6]) if len(sys.argv) > 6 else None
if not HTML or not OUT or not DUR:
    print('usage: render.py <html路径> <输出帧目录> <时长秒> [fps] [start] [stop]')
    sys.exit(1)
if not HTML.startswith('file://'):
    HTML = 'file:///' + HTML.replace('\\', '/')

log = []
os.makedirs(OUT, exist_ok=True)
t0 = time.time()

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(HTML)
    page.wait_for_load_state('load')
    time.sleep(1.0)
    page.click('#btnPlay')
    time.sleep(0.3)
    log.append('clicked')

    if START > 0:
        target = START / FPS
        pre_t = max(0.0, target - 0.5)
        page.evaluate("""(function(tPre, tFinal){
            var a = document.getElementById('voice');
            if (a) { try { a.currentTime = tPre; } catch(e){} }
            if (window.syncTime) window.syncTime(tPre);
        })(%f, %f)""" % (pre_t, target))
        time.sleep(0.15)
        page.evaluate("""(function(tFinal){
            var a = document.getElementById('voice');
            if (a) { try { a.currentTime = tFinal; } catch(e){} }
            if (window.syncTime) window.syncTime(tFinal);
        })(%f)""" % target)
        time.sleep(0.15)
        log.append('fast prewarm to %.2fs' % target)

    def snap(i):
        path = os.path.join(OUT, 'f%05d.jpg' % i)
        for attempt in range(4):
            try:
                page.screenshot(path=path, type='jpeg', quality=85)
                return
            except PermissionError:
                time.sleep(0.3)
        page.screenshot(path=path, type='jpeg', quality=85)

    n = int(DUR * FPS)
    if STOP is not None:
        n = min(n, STOP)
    for i in range(START, n):
        t = i / FPS
        page.evaluate("(function(tt){ if(window.syncTime) window.syncTime(tt); var a=document.getElementById('voice'); try{ a.currentTime=tt; }catch(e){} })(%f)" % t)
        if i % 4 == 0:
            time.sleep(0.03)
        snap(i)
        if i % 200 == 0:
            log.append('frame %d / %d @ %.0fs' % (i, n, time.time() - t0))
    browser.close()

log.append('done in %.1fs' % (time.time() - t0))
io.open(os.path.join(OUT, '_render_log.txt'), 'w', encoding='utf-8').write('\n'.join(log))
print('OK')
