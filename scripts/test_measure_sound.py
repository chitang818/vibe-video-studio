import sys
sys.stdout.reconfigure(encoding='utf-8')
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        js_code = """async () => {
            async function measure(type) {
                const sampleRate = 44100;
                const dur = type === 'chime' ? 1.5 : (type === 'whoosh' ? 0.45 : 0.25);
                const ac = new OfflineAudioContext(1, Math.floor(sampleRate * dur), sampleRate);
                const now = 0;
                
                if (type === 'pop') {
                    const osc = ac.createOscillator();
                    const gain = ac.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(560, now);
                    osc.frequency.exponentialRampToValueAtTime(240, now + 0.10);
                    gain.gain.setValueAtTime(0.001, now);
                    gain.gain.linearRampToValueAtTime(0.24, now + 0.004);
                    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.10);
                    osc.connect(gain);
                    gain.connect(ac.destination);
                    osc.start(now);
                    osc.stop(now + 0.10);
                } else if (type === 'whoosh') {
                    const durBuf = 0.45;
                    const buf = ac.createBuffer(1, Math.floor(sampleRate * durBuf), sampleRate);
                    const data = buf.getChannelData(0);
                    let b0 = 0, b1 = 0, b2 = 0;
                    for (let i = 0; i < data.length; i++) {
                        const white = Math.random() * 2 - 1;
                        b0 = 0.99765 * b0 + white * 0.0990460;
                        b1 = 0.96300 * b1 + white * 0.2965164;
                        b2 = 0.57000 * b2 + white * 1.0526913;
                        data[i] = (b0 + b1 + b2 + white * 0.1848) * 0.45; // 恢复合理底噪
                    }
                    const src = ac.createBufferSource();
                    src.buffer = buf;
                    const filter = ac.createBiquadFilter();
                    filter.type = 'lowpass';
                    filter.Q.value = 1.0;
                    filter.frequency.setValueAtTime(200, now);
                    filter.frequency.exponentialRampToValueAtTime(1100, now + 0.16);
                    filter.frequency.exponentialRampToValueAtTime(260, now + 0.42);
                    const gain = ac.createGain();
                    gain.gain.setValueAtTime(0.001, now);
                    gain.gain.linearRampToValueAtTime(0.15, now + 0.14);
                    gain.gain.linearRampToValueAtTime(0.0001, now + 0.42);
                    src.connect(filter);
                    filter.connect(gain);
                    gain.connect(ac.destination);
                    src.start(now);
                    src.stop(now + 0.42);
                } else if (type === 'ding') {
                    const filter = ac.createBiquadFilter();
                    filter.type = 'lowpass';
                    filter.frequency.value = 2200;
                    const masterGain = ac.createGain();
                    masterGain.gain.setValueAtTime(0.18, now);
                    filter.connect(masterGain);
                    masterGain.connect(ac.destination);
                    [1046.5, 1567.98].forEach((freq, i) => {
                        const osc = ac.createOscillator();
                        const gain = ac.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(freq, now);
                        const vol = i === 0 ? 0.8 : 0.4;
                        gain.gain.setValueAtTime(0.001, now);
                        gain.gain.linearRampToValueAtTime(vol, now + 0.005);
                        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.45);
                        osc.connect(gain);
                        gain.connect(filter);
                        osc.start(now);
                        osc.stop(now + 0.45);
                    });
                }
                
                const rendered = await ac.startRendering();
                const chData = rendered.getChannelData(0);
                let peak = 0;
                let sumSq = 0;
                for (let i = 0; i < chData.length; i++) {
                    const val = Math.abs(chData[i]);
                    if (val > peak) peak = val;
                    sumSq += val * val;
                }
                const rms = Math.sqrt(sumSq / chData.length);
                const peakDb = 20 * Math.log10(peak || 1e-6);
                const rmsDb = 20 * Math.log10(rms || 1e-6);
                return { peakDb: peakDb.toFixed(1), rmsDb: rmsDb.toFixed(1) };
            }
            
            return {
                pop: await measure('pop'),
                whoosh: await measure('whoosh'),
                ding: await measure('ding')
            };
        }"""
        stats = await page.evaluate(js_code)
        print('Tuned acoustic measurements:', stats)
        await browser.close()

asyncio.run(main())
