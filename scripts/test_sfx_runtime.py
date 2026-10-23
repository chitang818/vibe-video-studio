import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 拦截 console 消息与 play 调用
        called_sfx = []
        await page.expose_function('logSfx', lambda sfx, t: called_sfx.append((sfx, round(t, 2))))
        
        await page.goto('file:///d:/003-AI_coding/0000chitang_coding/vibe-video-studio/output/N0001_贝莱斯芽孢杆菌科普/N0001_贝莱斯芽孢杆菌科普.html')
        await page.wait_for_timeout(300)
        
        # 劫持 VibeSound.play 用于观察真实触发情况
        await page.evaluate('''() => {
            const origPlay = window.VibeSound.play;
            window.VibeSound.play = function(type) {
                const t = (window.audio && window.audio.currentTime) || 0;
                window.logSfx(type, t);
                origPlay.call(window.VibeSound, type);
            };
        }''')
        
        # 模拟点击播放按钮
        await page.click('#btnPlay')
        print("Clicked play button...")
        
        # 推进前 20 秒
        for step_t in [0.05, 1.0, 2.25, 5.0, 8.1, 12.0, 15.0, 18.0]:
            await page.evaluate(f'window.syncTime({step_t})')
            await page.wait_for_timeout(50)
            
        print("Triggered SFX events in first 20 seconds:", called_sfx)
        await browser.close()

asyncio.run(main())
