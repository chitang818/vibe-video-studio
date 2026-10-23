import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        called_sfx = []
        await page.expose_function('logSfx', lambda sfx, t: called_sfx.append((sfx, round(t, 2))))
        
        await page.goto('file:///d:/003-AI_coding/0000chitang_coding/vibe-video-studio/output/N0001_贝莱斯芽孢杆菌科普/N0001_贝莱斯芽孢杆菌科普.html')
        await page.wait_for_timeout(300)
        
        await page.evaluate('''() => {
            const origPlay = window.VibeSound.play;
            window.VibeSound.play = function(type) {
                const t = (window.audio && window.audio.currentTime) || 0;
                window.logSfx(type, t);
                origPlay.call(window.VibeSound, type);
            };
        }''')
        
        # 点击开始播放，自然播放 3.0 秒
        await page.click('#btnPlay')
        await page.wait_for_timeout(3000)
        
        print("Natural playback first 3 seconds SFX:", called_sfx)
        await browser.close()

asyncio.run(main())
