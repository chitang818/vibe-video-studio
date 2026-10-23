# -*- coding: utf-8 -*-
"""VIBE 通用：四边安全区 + 中区边界扫描
用法: python qa_bounds.py <html路径> [探针时刻(逗号分隔)]
边界常数（1080x1920）：顶10cqh=192 / 底14cqh=1651 / 左右8cqw=[86,994]；字幕底线<=1651
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
CLI_PROBES = [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 and sys.argv[2] else None
if not HTML:
    print('usage: qa_bounds.py <html路径> [时刻1,时刻2,...]')
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

    if CLI_PROBES is not None:
        probes = CLI_PROBES
    else:
        # 动态从页面 SCENES 提取各场景核心呈现时刻
        scene_times = page.evaluate("""(function(){
          var sc = (typeof SCENES !== 'undefined') ? SCENES : [];
          var pts = [];
          for (var i = 0; i < sc.length; i++) {
            pts.push(sc[i][1] + 0.6);
          }
          return pts;
        })()""")
        if scene_times and len(scene_times) > 0:
            probes = sorted(list(set(scene_times)))
        else:
            probes = [1, 5, 10, 15, 20, 25, 40, 65, 90, 120]

    for t in probes:
        page.evaluate("(function(tt){ if(window.syncTime) window.syncTime(tt); var a=document.getElementById('voice'); try{ a.currentTime=tt; }catch(e){} })(%f)" % t)
        time.sleep(0.5)
        probe = page.evaluate("""(function(){
          var sc=document.querySelector('.scene.active');
          var sid=sc?sc.id:'none';
          var so=document.getElementById('s-open');
          var activePhs=so?so.getAttribute('data-phase'):'';
          var res={viol:[]};
          var els=document.querySelectorAll('.scene.active *');
          for(var i=0;i<els.length;i++){
            var el=els[i], st=getComputedStyle(el);
            if(st.position==='fixed') continue;
            var cls=(el.className.baseVal||el.className||'').toString();
            if(/aura|glow|ring|inner|phs|scene|subtitle|overlay|progress|flash|canvas/i.test(cls)) continue;
            var phs=el.closest('.phs');
            if(phs && phs.className.indexOf('phs-'+activePhs)<0) continue;
            var r=el.getBoundingClientRect();
            if(r.width<5 || r.height<5 || r.right<1) continue;
            var vis=st.display!=='none' && st.visibility!=='hidden' && parseFloat(st.opacity)>0.05;
            if(!vis) continue;
            if(r.left<84 || r.right>996 || r.top<190 || r.bottom>1653){
              res.viol.push(el.tagName+'.'+cls.slice(0,18)+' L='+Math.round(r.left)+' R='+Math.round(r.right)+' T='+Math.round(r.top)+' B='+Math.round(r.bottom));
            }
          }
          return {sid:sid, viol:res.viol};
        })()""")
        status = ('OK' if len(probe['viol']) == 0 else 'FAIL')
        row = 't=%s %s viol=%d %s -> %s' % (t, probe['sid'], len(probe['viol']), status,
                                            ' | '.join(probe['viol'][:4]))
        print(row)
        out.append(row)
    browser.close()

io.open(os.path.join(os.path.dirname(HTML.replace('file:///', '')), '_qa_bounds.txt'),
        'w', encoding='utf-8').write('\n'.join(out))
