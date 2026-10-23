# -*- coding: utf-8 -*-
import os
import re

with open("examples/N0001_star_strain/demo.html", "r", encoding="utf-8") as f:
    demo = f.read()

with open("template/skeleton.html", "r", encoding="utf-8") as f:
    skel = f.read()

# 1. 提取 VibeSound
vs_start = skel.find("var VibeSound = (function() {")
vs_end = skel.find("window.VibeSound = VibeSound;", vs_start) + len("window.VibeSound = VibeSound;")
vibesound_code = skel[vs_start:vs_end]

# 2. 提取 VibeBackgrounds
vb_start = skel.find("var VibeBackgrounds = (function () {")
vb_end = skel.find("VibeBackgrounds.use('bg-canvas', 'bio-bubbles'", vb_start)
vb_use_end = skel.find("});", vb_end) + 3
vibebg_code = skel[vb_start:vb_use_end]

# 3. 替换 .stage 加 container-type: size;
demo = demo.replace(
    ".stage{position:fixed;inset:0;width:100%;height:100%}",
    ".stage{position:fixed;inset:0;width:100%;height:100%;container-type:size;}"
)

# 4. 替换 .head 和 #chapText 样式（外置于安全区外左上角盲区 top: 3.2cqh; left: 4cqw;）
old_head_css = """  /* ===== 上区（标题区·可选·简洁两行：总结性标题 + 第 N/M 节序号，无系列眉标） ===== */
  .head{position:fixed;top:0;left:0;right:0;z-index:5;padding:10cqh 4cqw 1.6cqw;background:linear-gradient(180deg,rgba(4,7,12,.9),rgba(4,7,12,.55) 70%,transparent);text-align:center;pointer-events:none}
  .head h1{font-size:4.4cqw;font-weight:900;margin-top:0;letter-spacing:.05em;line-height:1.3}
  #chapText{position:fixed;top:16cqh;left:4cqw;z-index:5;font-size:2.7cqw;color:var(--dim);background:rgba(10,20,32,.55);border:1px solid var(--line);border-radius:6cqw;padding:.8cqw 3cqw;backdrop-filter:blur(3px)}"""

new_head_css = """  /* ===== 上区（外置 Dev HUD + 居中纯粹作品标题区） ===== */
  #chapText {
    position: fixed;
    top: 3.2cqh;
    left: 4cqw;
    z-index: 10;
    font-size: 2.2cqw;
    font-weight: 600;
    color: rgba(147, 167, 160, 0.75);
    background: rgba(10, 20, 32, 0.55);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 999px;
    padding: 0.5cqw 2.4cqw;
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    pointer-events: none;
    letter-spacing: 0.05em;
    user-select: none;
  }
  .head {
    position: fixed;
    top: 10cqh;
    left: 8cqw;
    right: 8cqw;
    z-index: 6;
    display: flex;
    justify-content: center;
    align-items: center;
    pointer-events: none;
  }
  .head-pill {
    position: relative;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-width: 84cqw;
    padding: 0.8cqw 3.6cqw 0.9cqw;
    background: rgba(10, 18, 26, 0.68);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
  }
  .head-pill .title-line {
    display: block;
    text-align: center;
    line-height: 1.25;
    background: linear-gradient(180deg, #ffffff 15%, #e2e8f0 70%, #94a3b8 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.85));
    letter-spacing: 0.05em;
  }
  .head-pill .title-main {
    font-size: 4.0cqw;
    font-weight: 900;
  }
  .head-pill .title-sub {
    font-size: 3.2cqw;
    font-weight: 700;
    color: #4ade80;
    background: linear-gradient(180deg, #86efac 10%, #4ade80 75%, #22c55e 100%);
    -webkit-background-clip: text;
    background-clip: text;
    margin-top: 0.4cqw;
  }"""

assert old_head_css in demo, "old_head_css not found"
demo = demo.replace(old_head_css, new_head_css)

# 5. 替换 HTML 中的 head 和 chapText
old_head_html = """<div class="head">
  <h1>贝莱斯芽孢杆菌 · 从发现到成为全能明星菌株</h1>
</div>
<div id="chapText">第 1 / 8 节</div>"""

new_head_html = """<div id="chapText">第 1 / 9 节</div>
<div class="head">
  <div class="head-pill" id="mainTitle">
    <span class="title-line title-main">贝莱斯芽孢杆菌</span>
    <span class="title-line title-sub">从发现到成为全能明星菌株</span>
  </div>
</div>"""

assert old_head_html in demo, "old_head_html not found"
demo = demo.replace(old_head_html, new_head_html)

# 5.1 背景氛围层重命名避免误触
demo = demo.replace('<div class="ring"></div>', '<div class="aura-ring"></div>')
demo = demo.replace('.aura .ring{', '.aura .aura-ring{')

# 5.2 精细化排版升级 S2 (s-why): 标题对称语义分行、因果分层矩阵、结构化清单卡片、拟态环境条
old_s_why_css = """  /* S2 痛点条 */
  .pain-row{display:flex;align-items:center;gap:2cqw;flex-wrap:wrap;justify-content:center;margin-bottom:3cqw}
  .pchip{font-size:3cqw;font-weight:700;color:var(--red);border:1px solid rgba(248,113,113,.35);border-radius:6cqw;padding:.8cqw 2.6cqw;background:rgba(248,113,113,.08)}
  .pain-row .arr2{color:var(--dim);font-weight:900}
  /* S2 菌体卡 */
  .bug-card{display:flex;align-items:center;gap:4cqw;width:82cqw;background:linear-gradient(160deg,rgba(16,28,38,.9),rgba(10,18,26,.9));border:1px solid var(--line);border-radius:3cqw;padding:3cqw 4.4cqw;text-align:left;margin-top:1.4cqw}
  .bug-card .bc-svg{width:34cqw;flex:none}
  .bug-card .bc-svg svg{width:100%;height:auto}
  .bug-card .bc-txt{flex:1}
  .bug-card .bc-t{font-size:3.4cqw;font-weight:800;color:var(--green)}
  .bug-card .bc-d{font-size:3cqw;color:var(--dim);line-height:1.8;margin-top:1cqw}
  /* S2 环境条 */
  .env-bars{width:82cqw;display:flex;flex-direction:column;gap:1.8cqw;margin-top:3cqw}
  .env{display:flex;align-items:center;gap:2.4cqw}
  .env .lab{font-size:3.2cqw;font-weight:800;color:var(--cyan);width:7cqw;text-align:left;flex:none}
  .env .bar{flex:1;height:4cqw;border-radius:4cqw;background:rgba(148,163,184,.12);overflow:hidden}
  .env .bar i{display:block;height:100%;border-radius:4cqw;background:linear-gradient(90deg,#22c55e,#4ade80);animation:barGrow 1s cubic-bezier(.22,1,.36,1) .4s both}
  .env .val{font-size:3.2cqw;font-weight:800;color:var(--ink);width:17cqw;text-align:right;flex:none}
  @keyframes barGrow{from{width:0}}"""

new_s_why_css = """  /* S2 标题优化：对称断句，杜绝孤字 */
  #s-why h2 {
    font-size: 5.6cqw;
    font-weight: 900;
    line-height: 1.35;
    margin: 1.6cqw 0 1.8cqw;
    text-align: center;
  }
  #s-why h2 .hl-green {
    color: var(--green);
    text-shadow: 0 0 4cqw rgba(74, 222, 128, 0.45);
    display: inline-block;
    margin-top: 0.5cqw;
    font-size: 6.2cqw;
  }
  /* S2 痛点因果矩阵：上因下果，整齐划一，杜绝悬挂孤立标签 */
  .pain-box {
    width: 82cqw;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 2.2cqw;
  }
  .cause-chip {
    font-size: 2.9cqw;
    font-weight: 700;
    color: #f87171;
    border: 1px solid rgba(248, 113, 113, 0.4);
    border-radius: 6cqw;
    padding: 0.8cqw 3.6cqw;
    background: rgba(248, 113, 113, 0.12);
    display: inline-flex;
    align-items: center;
    gap: 1.2cqw;
  }
  .arrow-down {
    font-size: 2.4cqw;
    color: var(--dim);
    font-weight: 700;
    margin: 0.8cqw 0 1cqw;
    letter-spacing: 0.08em;
  }
  .effect-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2cqw;
    width: 82cqw;
  }
  .echip {
    font-size: 3.0cqw;
    font-weight: 800;
    color: #fca5a5;
    border: 1px solid rgba(248, 113, 113, 0.3);
    border-radius: 2.4cqw;
    padding: 1.2cqw 1cqw;
    background: rgba(248, 113, 113, 0.08);
    text-align: center;
    letter-spacing: 0.04em;
  }
  /* S2 菌体结构化卡：垂直堆叠优先，条目通栏排布 */
  .bug-card {
    width: 82cqw;
    background: linear-gradient(160deg, rgba(16,28,38,.94), rgba(10,18,26,.94));
    border: 1px solid rgba(74,222,128,.35);
    border-radius: 3.2cqw;
    padding: 2.4cqw 3.2cqw;
    text-align: left;
    margin-top: 1.2cqw;
    box-shadow: 0 4px 20px rgba(0,0,0,.45);
    box-sizing: border-box;
  }
  .bc-top {
    display: flex;
    align-items: center;
    gap: 3cqw;
    border-bottom: 1px solid rgba(148,163,184,.14);
    padding-bottom: 1.6cqw;
    margin-bottom: 1.8cqw;
  }
  .bc-svg-wrap {
    width: 18cqw;
    flex: none;
  }
  .bc-svg-wrap svg {
    width: 100%;
    height: auto;
    display: block;
  }
  .bc-title-box {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.8cqw;
  }
  .bc-tag {
    font-size: 2.4cqw;
    font-weight: 800;
    color: var(--green);
    background: rgba(74,222,128,.12);
    border: 1px solid rgba(74,222,128,.4);
    border-radius: 4cqw;
    padding: 0.3cqw 1.8cqw;
    display: inline-block;
    align-self: flex-start;
  }
  .bc-t {
    font-size: 3.2cqw;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: 0.02em;
  }
  .bc-points {
    display: flex;
    flex-direction: column;
    gap: 1.2cqw;
  }
  .bc-row {
    display: flex;
    align-items: center;
    gap: 1.4cqw;
    font-size: 2.7cqw;
  }
  .bp-dot {
    color: var(--green);
    font-size: 2.2cqw;
    flex: none;
  }
  .bp-label {
    font-weight: 800;
    color: var(--cyan);
    flex: none;
  }
  .bp-val {
    color: var(--ink);
    font-weight: 600;
    letter-spacing: 0.02em;
    flex: 1;
  }
  /* S2 环境耐受仪表条：饱满拟态设计 */
  .env-bars {
    width: 82cqw;
    display: flex;
    flex-direction: column;
    gap: 1.6cqw;
    margin-top: 2.2cqw;
    background: linear-gradient(160deg, rgba(16,28,38,.88), rgba(10,18,26,.88));
    border: 1px solid var(--line);
    border-radius: 2.8cqw;
    padding: 2.2cqw 3.6cqw;
    box-shadow: 0 4px 18px rgba(0,0,0,.35);
  }
  .env {
    display: flex;
    align-items: center;
    gap: 2.4cqw;
  }
  .env .lab {
    font-size: 2.8cqw;
    font-weight: 700;
    color: var(--cyan);
    width: 14cqw;
    text-align: left;
    flex: none;
  }
  .env .bar {
    flex: 1;
    height: 3.2cqw;
    border-radius: 999px;
    background: rgba(148,163,184,.14);
    overflow: hidden;
  }
  .env .bar i {
    display: block;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg,#22c55e,#4ade80);
    box-shadow: 0 0 10px rgba(74,222,128,.4);
    animation: barGrow 1s cubic-bezier(.22,1,.36,1) .4s both;
  }
  .env .val {
    font-size: 3.0cqw;
    font-weight: 800;
    color: #fff;
    width: 20cqw;
    text-align: right;
    flex: none;
  }
  @keyframes barGrow{from{width:0}}"""

assert old_s_why_css in demo, "old_s_why_css not found"
demo = demo.replace(old_s_why_css, new_s_why_css)

old_s_why_html = """  <!-- ===== S2 为什么是全能选手 ===== -->
  <div class="scene" id="s-why">
    <div class="aura"><div class="glow"></div></div>
    <div class="inner">
      <div class="badge w">第一部分 · 全能选手</div>
      <h2 class="w w2">为什么是农用菌中的"全能选手"？</h2>
      <div class="pain-row w w3">
        <span class="pchip">化肥农药长期大量使用</span><span class="arr2">→</span>
        <span class="pchip">土壤板结</span><span class="pchip">农残超标</span><span class="pchip">病菌耐药</span>
      </div>
      <div class="bug-card w w3">
        <div class="bc-svg">
          <svg viewBox="0 0 120 66" fill="none" stroke="currentColor">
            <rect x="18" y="26" width="70" height="22" rx="11" fill="rgba(74,222,128,.10)" stroke="#4ade80" stroke-width="2.4"/>
            <ellipse cx="88" cy="37" rx="9" ry="3" fill="rgba(74,222,128,.5)"/>
            <path d="M88 30c10-3 15 0 17 7-8 5-13 4-17-7z" fill="rgba(74,222,128,.25)"/>
            <path d="M18 37l-10-7M18 37l-10 7" stroke-linecap="round"/>
            <circle cx="68" cy="37" r="6" stroke-width="1.8"/>
            <circle cx="48" cy="30" r="4.4" fill="rgba(251,191,36,.3)" stroke="#fbbf24" stroke-width="1.6"/>
            <path d="M96 6c8 0 14 4 16 10M100 12c4 0 7 2 8 5" stroke="#38bdf8" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>
            <circle cx="24" cy="6" r="2.4" fill="#4ade80" opacity=".7"/>
          </svg>
        </div>
        <div class="bc-txt">
          <div class="bc-t">革兰氏阳性细菌 · 从实验室走向田间</div>
          <div class="bc-d">杆状 · 可产芽孢 · 鞭毛自主运动<br>分泌淀粉酶 / 蛋白酶 / 脂肪酶</div>
        </div>
      </div>
      <div class="env-bars w w4">
        <div class="env"><div class="lab">温度</div><div class="bar"><i style="width:62%"></i></div><div class="val">15~45℃</div></div>
        <div class="env"><div class="lab">pH</div><div class="bar"><i style="width:52%"></i></div><div class="val">5~10</div></div>
        <div class="env"><div class="lab">盐度</div><div class="bar"><i style="width:36%"></i></div><div class="val">可耐受</div></div>
      </div>
    </div>
  </div>"""

new_s_why_html = """  <!-- ===== S2 为什么是全能选手 ===== -->
  <div class="scene" id="s-why">
    <div class="aura"><div class="glow"></div></div>
    <div class="inner">
      <div class="badge w">第一部分 · 全能选手</div>
      <h2 class="w w2">为什么被称为<br><span class="hl-green">农用菌中的"全能选手"？</span></h2>
      <div class="pain-box w w3">
        <div class="cause-chip">
          <span>⚠️</span> 长期过量使用化肥农药
        </div>
        <div class="arrow-down">↓ 导致三大土壤生态问题</div>
        <div class="effect-grid">
          <div class="echip">土壤板结</div>
          <div class="echip">农残超标</div>
          <div class="echip">病菌耐药</div>
        </div>
      </div>
      <div class="bug-card w w3">
        <div class="bc-top">
          <div class="bc-svg-wrap">
            <svg viewBox="0 0 120 66" fill="none" stroke="currentColor">
              <rect x="18" y="26" width="70" height="22" rx="11" fill="rgba(74,222,128,.12)" stroke="#4ade80" stroke-width="2.4"/>
              <ellipse cx="88" cy="37" rx="9" ry="3" fill="rgba(74,222,128,.5)"/>
              <path d="M88 30c10-3 15 0 17 7-8 5-13 4-17-7z" fill="rgba(74,222,128,.25)"/>
              <path d="M18 37l-10-7M18 37l-10 7" stroke-linecap="round"/>
              <circle cx="68" cy="37" r="6" stroke-width="1.8"/>
              <circle cx="48" cy="30" r="4.4" fill="rgba(251,191,36,.3)" stroke="#fbbf24" stroke-width="1.6"/>
              <path d="M96 6c8 0 14 4 16 10M100 12c4 0 7 2 8 5" stroke="#38bdf8" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>
              <circle cx="24" cy="6" r="2.4" fill="#4ade80" opacity=".7"/>
            </svg>
          </div>
          <div class="bc-title-box">
            <div class="bc-tag">革兰氏阳性菌</div>
            <div class="bc-t">从实验室走向田间 · 绿色农业新宠</div>
          </div>
        </div>
        <div class="bc-points">
          <div class="bc-row">
            <span class="bp-dot">✦</span>
            <span class="bp-label">形态特征：</span>
            <span class="bp-val">杆状菌体 · 可产抗逆芽孢 · 具鞭毛自主运动</span>
          </div>
          <div class="bc-row">
            <span class="bp-dot">✦</span>
            <span class="bp-label">多重酶系：</span>
            <span class="bp-val">分泌淀粉酶 · 蛋白酶 · 脂肪酶等多种胞外酶</span>
          </div>
        </div>
      </div>
      <div class="env-bars w w4">
        <div class="env"><div class="lab">温度范围</div><div class="bar"><i style="width:72%"></i></div><div class="val">15 ~ 45 ℃</div></div>
        <div class="env"><div class="lab">酸碱耐受</div><div class="bar"><i style="width:58%"></i></div><div class="val">pH 5 ~ 10</div></div>
        <div class="env"><div class="lab">耐盐特性</div><div class="bar"><i style="width:42%"></i></div><div class="val">耐受高盐</div></div>
      </div>
    </div>
  </div>"""

assert old_s_why_html in demo, "old_s_why_html not found"
demo = demo.replace(old_s_why_html, new_s_why_html)

# 6. 替换 audio 路径
demo = demo.replace(
    '<audio id="voice" src="assets/voice.wav" preload="auto"></audio>',
    '<audio id="voice" src="../../inputs/N0001_贝莱斯芽孢杆菌科普/voice.wav" preload="auto"></audio>'
)

# 7. 替换 setScene 和播放循环
old_scene_fn = """function setScene(idx){
  if(idx===curScene) return;
  var prev=curScene;
  if(prev>=0) document.getElementById(SCENES[prev][0]).classList.remove('active');
  curScene=idx;
  var el=document.getElementById(SCENES[idx][0]);
  el.classList.add('active');
  el.getBoundingClientRect();
  var ct=document.getElementById('chapText');
  if(ct) ct.innerHTML='第 '+(idx+1)+' / '+SCENES.length+' 节';
  /* 转场闪光：只在真正发生场景切换时触发（prev 为旧场景） */
  if(idx>0 && prev!==idx){
    flashEl.classList.remove('go'); void flashEl.offsetWidth; flashEl.classList.add('go');
  }
}
var S1 = document.getElementById('s-open');
function setPhase(p){ if(S1.getAttribute('data-phase')!==p) S1.setAttribute('data-phase',p); }
function startPlay(){
  if(state==='playing') return;
  overlay.classList.add('hide');
  for(var i=0;i<SCENES.length;i++){
    document.getElementById(SCENES[i][0]).classList.remove('active');
  }
  curScene=-1; curIdx=-1;
  audio.currentTime=0;
  audio.play().then(function(){
    state='playing';
    flashEl.classList.remove('go'); void flashEl.offsetWidth; flashEl.classList.add('go');
    if(!rafId) loop();
  }).catch(function(){});
}
function endPlay(){
  state='ended';
  progFill.style.width='100%';
  btnReplay.classList.add('show');
}
function loop(){
  if(state!=='playing'){ rafId=0; return; }
  var t=audio.currentTime;
  if(audio.ended || t>=audio.duration-0.05){ endPlay(); rafId=0; return; }
  var idx=findCharIndex(t);
  if(idx!==curIdx){ curIdx=idx; renderSubtitle(idx); }
  var sc=sceneAt(t);
  if(sc!==curScene){ setScene(sc); triggerSceneGfx(sc); }
  if(sc===0){
    setPhase(t<2.20?'splash':(t<8.04?'topic':(t<14.82?'hook':(t<17.86?'promise':(t<24.74?'cta':'preview')))));
  }
  progFill.style.width=(t/audio.duration*100).toFixed(2)+'%';
  rafId=requestAnimationFrame(loop);
}"""

new_scene_fn = """var SFX_CUES = [
  { t: 2.20, sfx: 'whoosh' },
  { t: 8.04, sfx: 'pop' },
  { t: 14.82, sfx: 'pop' },
  { t: 17.86, sfx: 'ding' },
  { t: 26.66, sfx: 'whoosh' },
  { t: 34.20, sfx: 'pop' },
  { t: 45.00, sfx: 'pop' },
  { t: 50.50, sfx: 'pop' },
  { t: 58.39, sfx: 'whoosh' },
  { t: 65.20, sfx: 'pop' },
  { t: 71.80, sfx: 'ding' },
  { t: 77.93, sfx: 'whoosh' },
  { t: 86.50, sfx: 'pop' },
  { t: 98.20, sfx: 'pop' },
  { t: 106.51, sfx: 'whoosh' },
  { t: 118.40, sfx: 'ding' },
  { t: 135.20, sfx: 'pop' },
  { t: 153.41, sfx: 'whoosh' },
  { t: 170.50, sfx: 'ding' },
  { t: 195.20, sfx: 'pop' },
  { t: 216.71, sfx: 'whoosh' },
  { t: 224.20, sfx: 'pop' },
  { t: 235.55, sfx: 'whoosh' },
  { t: 248.30, sfx: 'pop' },
  { t: 262.50, sfx: 'pop' },
  { t: 275.29, sfx: 'whoosh' },
  { t: 282.00, sfx: 'chime' }
];

var lastCueTime = -0.5;
function checkSfxCues(t) {
  if (!window.VibeSound || window.__RECORDING__) return;
  if (t < lastCueTime) { lastCueTime = t - 0.2; }
  for (var i = 0; i < SFX_CUES.length; i++) {
    var cue = SFX_CUES[i];
    if (t >= cue.t && lastCueTime < cue.t && (t - cue.t) < 0.35) {
      VibeSound.play(cue.sfx);
    }
  }
  lastCueTime = t;
}

function setScene(idx){
  if(idx===curScene || idx<0 || idx>=SCENES.length) return;
  var prev=curScene;
  if(prev>=0 && prev<SCENES.length){
    var prevEl = document.getElementById(SCENES[prev][0]);
    if(prevEl) prevEl.classList.remove('active');
  }
  curScene=idx;
  var el=document.getElementById(SCENES[idx][0]);
  if(el) el.classList.add('active');
  var ct=document.getElementById('chapText');
  if(ct) ct.innerHTML='第 '+(idx+1)+' / '+SCENES.length+' 节';
  if(idx>0 && prev!==idx && flashEl){
    flashEl.classList.remove('go'); void flashEl.offsetWidth; flashEl.classList.add('go');
  }
}
var S1 = document.getElementById('s-open');
function setPhase(p){ if(S1 && S1.getAttribute('data-phase')!==p) S1.setAttribute('data-phase',p); }

function syncTime(t){
  var sc = sceneAt(t);
  if(sc !== curScene){
    setScene(sc);
    triggerSceneGfx(sc);
  }
  if(sc === 0){
    setPhase(t<2.20?'splash':(t<8.04?'topic':(t<14.82?'hook':(t<17.86?'promise':(t<24.74?'cta':'preview')))));
  }
  var idx = findCharIndex(t);
  if(idx !== curIdx){
    curIdx = idx;
    renderSubtitle(idx);
  }
  checkSfxCues(t);
  var dur = (audio && audio.duration && !isNaN(audio.duration)) ? audio.duration : 314.56;
  if(progFill) progFill.style.width = Math.min(100, (t / dur * 100)).toFixed(2) + '%';
}
window.syncTime = syncTime;
window.SCENES = SCENES;
window.CHAP_NAMES = CHAP_NAMES;

function startPlay(){
  if(state==='playing') return;
  if(window.VibeSound) {
    VibeSound.init();
    VibeSound.play('whoosh');
  }
  overlay.classList.add('hide');
  curScene=-1; curIdx=-1;
  lastCueTime = -0.5;
  syncTime(0);
  audio.currentTime=0;
  audio.play().then(function(){
    state='playing';
    flashEl.classList.remove('go'); void flashEl.offsetWidth; flashEl.classList.add('go');
    if(!rafId) loop();
  }).catch(function(e){
    console.warn("Audio play:", e);
  });
}
function endPlay(){
  state='ended';
  if(progFill) progFill.style.width='100%';
  btnReplay.classList.add('show');
}
function loop(){
  if(state!=='playing'){ rafId=0; return; }
  var t=audio.currentTime;
  var dur = (audio && audio.duration && !isNaN(audio.duration)) ? audio.duration : 314.56;
  if(audio.ended || t>=dur-0.05){ endPlay(); rafId=0; return; }
  syncTime(t);
  rafId=requestAnimationFrame(loop);
}"""

assert old_scene_fn in demo, "old_scene_fn not found"
demo = demo.replace(old_scene_fn, new_scene_fn)

# 8. 替换旧背景并注入 VibeSound 与 VibeBackgrounds
old_bg_code = """/* ===== 背景粒子 ===== */
var cv=document.getElementById('bg-canvas');
var ctx=cv.getContext('2d');
var W,H,pts=[];
function initBg(){
  W=cv.width=innerWidth; H=cv.height=innerHeight;
  var n=Math.min(46,Math.floor(W*H/42000));
  pts=[];
  for(var i=0;i<n;i++){ pts.push({x:Math.random()*W,y:Math.random()*H,r:Math.random()*1.8+.6,vx:(Math.random()-.5)*.22,vy:(Math.random()-.5)*.22,a:Math.random()*.5+.2}); }
}
function drawBg(){
  ctx.clearRect(0,0,W,H);
  for(var i=0;i<pts.length;i++){
    var p=pts[i];
    p.x+=p.vx; p.y+=p.vy;
    if(p.x<0||p.x>W) p.vx*=-1;
    if(p.y<0||p.y>H) p.vy*=-1;
    ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle='rgba(148,215,180,'+p.a+')';
    ctx.fill();
    for(var j=i+1;j<pts.length;j++){
      var q=pts[j],dx=p.x-q.x,dy=p.y-q.y,d2=dx*dx+dy*dy;
      if(d2<11000){ ctx.strokeStyle='rgba(148,215,180,'+(0.09*(1-d2/11000))+')'; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y); ctx.stroke(); }
    }
  }
  requestAnimationFrame(drawBg);
}
initBg(); drawBg();
window.addEventListener('resize',function(){ initBg(); });"""

new_engine_code = f"""/* ===== VibeSound 引擎 ===== */
{vibesound_code}

/* ===== VibeBackgrounds 高能背景预设引擎 ===== */
{vibebg_code}

// 页面加载默认初始化首屏
syncTime(0);"""

assert old_bg_code in demo, "old_bg_code not found"
demo = demo.replace(old_bg_code, new_engine_code)

out_path = "output/N0001_贝莱斯芽孢杆菌科普/N0001_贝莱斯芽孢杆菌科普.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(demo)

print(f"Successfully generated {out_path} ({len(demo)} bytes)")
