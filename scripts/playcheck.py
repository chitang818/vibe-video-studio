# -*- coding: utf-8 -*-
"""VIBE 通用：播放验证（场景切换/章节/字幕/开场相位）
用法: python playcheck.py <html路径> [额外探针时刻(逗号分隔)]
自动从页面读取 SCENES 表生成场景探针；额外时刻用于验证开场相位等。
"""
import time, os, io, sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

HTML = sys.argv[1] if len(sys.argv) > 1 else None
EXTRA = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else []
if not HTML:
    print('usage: playcheck.py <html路径> [探针时刻1,时刻2,...]')
    sys.exit(1)
if not HTML.startswith('file://'):
    HTML = 'file:///' + HTML.replace('\\', '/')

out = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(HTML)
    page.wait_for_load_state('load')
    time.sleep(1.0)
    page.click('#btnPlay')
    time.sleep(0.3)

    # 从页面读取场景表
    meta = page.evaluate("""(function(){
      var scenes = (typeof SCENES!=='undefined') ? SCENES : [];
      var chaps = (typeof CHAP_NAMES!=='undefined') ? CHAP_NAMES : [];
      var ret=[];
      for(var i=0;i<scenes.length;i++){
        ret.push({id:scenes[i][0], t:scenes[i][1], chap:chaps[i]||''});
      }
      return ret;
    })()""")
    probes = []
    for i, sc in enumerate(meta):
        probes.append((sc['t'] + 0.5, sc['id'], None, sc['chap']))
    for t in EXTRA:
        probes.append((t, None, None, None))

    for t, scene, phase, chap in sorted(probes):
        page.evaluate("(function(tt){ if(window.syncTime) window.syncTime(tt); var a=document.getElementById('voice'); try{ a.currentTime=tt; }catch(e){} })(%f)" % t)
        time.sleep(1.2)
        info = page.evaluate("""(function(){
          var sc=document.querySelector('.scene.active');
          var id=sc?sc.id:'none';
          var ct=document.getElementById('chapText');
          var sub=document.getElementById('sentence');
          var so=document.getElementById('s-open');
          var phase=so?so.getAttribute('data-phase'):null;
          return {id:id, chap:ct?ct.textContent:'', sub:sub?sub.textContent:'', phase:phase};
        })()""")
        ok_scene = (scene is None or info['id'] == scene)
        row = 't=%.1f expect=%s got=%s scene:%s chap:%s sub=%s phase:%s' % (
            t, scene or '-', info['id'], 'OK' if ok_scene else 'FAIL',
            info['chap'], info['sub'], info['phase'])
        print(row)
        out.append(row)
    browser.close()

io.open(os.path.join(os.path.dirname(HTML.replace('file:///', '')), '_playcheck.txt'),
        'w', encoding='utf-8').write('\n'.join(out))
