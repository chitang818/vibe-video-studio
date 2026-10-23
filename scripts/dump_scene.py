# -*- coding: utf-8 -*-
import sys
from playwright.sync_api import sync_playwright

html_path = "file:///" + "D:/003-AI_coding/0000chitang_coding/vibe-video-studio/output/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点.html"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    page.goto(html_path)
    
    # 直接在页面中给 s-fzb42-intro 加上 active 类并移除其他 active 类
    res = page.evaluate("""() => {
        document.querySelectorAll('.scene').forEach(el => el.classList.remove('active'));
        const sc = document.getElementById('s-fzb42-intro');
        sc.classList.add('active');
        
        const dump = (el) => {
            const r = el.getBoundingClientRect();
            const cs = window.getComputedStyle(el);
            return {
                tag: el.tagName,
                cls: el.className,
                top: r.top,
                bottom: r.bottom,
                height: r.height,
                marginTop: cs.marginTop,
                marginBottom: cs.marginBottom,
                paddingTop: cs.paddingTop,
                paddingBottom: cs.paddingBottom
            };
        };
        
        return {
            sc: dump(sc),
            inner: dump(sc.querySelector('.inner')),
            badge: dump(sc.querySelector('.badge')),
            h2: dump(sc.querySelector('h2')),
            stack: dump(sc.querySelector('.card-stack')),
            cards: Array.from(sc.querySelectorAll('.card-item')).map(dump)
        };
    }""")
    
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
    browser.close()
