# -*- coding: utf-8 -*-
import sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

html_path = "file:///" + "D:/003-AI_coding/0000chitang_coding/vibe-video-studio/output/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点.html"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    page.goto(html_path)
    page.click("#btnPlay")
    
    page.evaluate("""() => {
        const a = document.getElementById('voice');
        if (a) a.pause();
        window.syncTime(13.0);
    }""")
    
    res = page.evaluate("""() => {
        const active = document.querySelector('.scene.active');
        if (!active) return { error: 'no active scene' };
        
        const ar = active.getBoundingClientRect();
        const inner = active.querySelector('.inner');
        const ir = inner ? inner.getBoundingClientRect() : null;
        const stack = active.querySelector('.card-stack');
        const sr = stack ? stack.getBoundingClientRect() : null;
        
        const cards = Array.from(active.querySelectorAll('.card-item')).map(el => {
            const r = el.getBoundingClientRect();
            return {
                cls: el.className,
                rect: { left: r.left, right: r.right, top: r.top, bottom: r.bottom, width: r.width, height: r.height }
            };
        });
        
        return {
            activeId: active.id,
            activeRect: { left: ar.left, right: ar.right, top: ar.top, bottom: ar.bottom, width: ar.width, height: ar.height },
            innerRect: ir ? { left: ir.left, right: ir.right, top: ir.top, bottom: ir.bottom, width: ir.width, height: ir.height } : null,
            stackRect: sr ? { left: sr.left, right: sr.right, top: sr.top, bottom: sr.bottom, width: sr.width, height: sr.height } : null,
            cards: cards
        };
    }""")
    
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
    browser.close()
