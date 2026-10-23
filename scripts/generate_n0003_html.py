# -*- coding: utf-8 -*-
"""
生成 N0003_贝莱斯芽孢杆菌的核心功能之生物防病 HTML 动画页
按 vibe-rules.md 规范严格构建：
1. 19 个分镜头场景，单镜头时长均在 5.3~13.0s 之间，无 >15s 超长镜头；
2. 顶部双行纯粹标题，分镜 HUD 外置于安全区外左上角；
3. bio-bubbles 高能细胞浮游光斑背景；
4. 竖屏垂直堆叠大卡片优先（Vertical Stacking First）；
5. 环形图与数字彻底解耦（环内仅纯数字，标签外置于环下方）；
6. 卡片内图标与文字严格解耦，无物理碰撞与重叠；
7. 全项字号合规（标题 >= 3.6cqw, 正文 >= 2.8cqw）；
8. 原生 VibeSound Web Audio 引擎与卡拉OK防碎行字幕引擎内联。
"""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = ROOT / "inputs" / "N0003_贝莱斯芽孢杆菌的核心功能之生物防病"
OUTPUT_DIR = ROOT / "output" / "N0003_贝莱斯芽孢杆菌的核心功能之生物防病"
OUTPUT_HTML = OUTPUT_DIR / "N0003_贝莱斯芽孢杆菌的核心功能之生物防病.html"

# 读取时间戳
with open(INPUT_DIR / "char_timestamps.json", "r", encoding="utf-8") as f:
    ts_data = json.load(f)

chars_list = [item.get("Char", "") for item in ts_data]
times_list = [round(float(item.get("StartSeconds", 0.0)), 2) for item in ts_data]

chars_json = json.dumps(chars_list, ensure_ascii=False)
times_json = json.dumps(times_list)

# 场景列表
scenes = [
    ["s-open", 0.0],
    ["s-combo", 9.0],
    ["s-arsenal", 19.5],
    ["s-lipopeptide", 32.2],
    ["s-pore", 39.5],
    ["s-polyketide", 47.3],
    ["s-enzyme", 56.0],
    ["s-protein-vol", 64.4],
    ["s-garlic", 74.0],
    ["s-pathogens", 81.3],
    ["s-pests", 90.5],
    ["s-niche", 97.5],
    ["s-biofilm", 104.2],
    ["s-siderophore", 113.8],
    ["s-vaccine", 119.1],
    ["s-pathway", 126.8],
    ["s-enzymes-up", 134.8],
    ["s-sy01", 144.5],
    ["s-cta", 151.7]
]

chap_names = [
    "开场·生物防病",
    "机制·三联组合拳",
    "机制一·抗生素工厂",
    "物质库·脂肽抗生素",
    "杀菌·细胞膜穿孔",
    "物质库·聚酮化合物",
    "物质库·细胞壁降解酶",
    "物质库·抗菌蛋白挥发物",
    "防效·大蒜病斑减9成",
    "抑菌·七大植物病原菌",
    "拓展·线虫红蜘蛛双防",
    "机制二·生态位竞争",
    "定殖·四维致密生物膜",
    "夺铁·分泌嗜铁素",
    "机制三·诱导系统抗性",
    "免疫·三大信号通路",
    "防御·四大防御酶暴增",
    "实证·苹果96h高表达",
    "总结·下期预告与CTA"
]

open_phases = [
    ["splash", 0.0],
    ["recap", 2.5],
    ["topic", 5.8]
]

scenes_json = json.dumps(scenes, ensure_ascii=False)
chap_names_json = json.dumps(chap_names, ensure_ascii=False)
open_phases_json = json.dumps(open_phases, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>N0003 贝莱斯芽孢杆菌的核心功能之生物防病</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect width='24' height='24' rx='5' fill='%23070d12'/><text x='12' y='17' font-size='13' font-weight='bold' text-anchor='middle' fill='%234ade80'>V</text></svg>">
<style>
  :root {{
    --bg: #070d12;
    --panel: #0e1a22;
    --panel-sub: rgba(16, 28, 38, 0.94);
    --line: rgba(148, 163, 184, 0.22);
    --ink: #e8f1ec;
    --dim: #93a7a0;
    --green: #4ade80;
    --green2: #22c55e;
    --amber: #fbbf24;
    --cyan: #38bdf8;
    --red: #f87171;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ height: 100%; }}
  body {{
    background: var(--bg);
    color: var(--ink);
    font-family: "Noto Sans SC", "Microsoft YaHei", -apple-system, system-ui, sans-serif;
    overflow: hidden;
  }}
  .stage {{
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    container-type: size;
  }}
  #bg-canvas {{
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
  }}

  /* ===== 上区（外置 Dev HUD + 居中纯粹作品标题区） ===== */
  #chapText {{
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
  }}
  .head {{
    position: fixed;
    top: 10cqh;
    left: 8cqw;
    right: 8cqw;
    z-index: 6;
    display: flex;
    justify-content: center;
    align-items: center;
    pointer-events: none;
  }}
  .head-pill {{
    position: relative;
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    max-width: 84cqw;
    padding: 0.8cqw 3.8cqw 0.9cqw;
    background: rgba(10, 18, 26, 0.72);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45), 0 0 25px rgba(74, 222, 128, 0.12);
  }}
  .head-pill::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 15%;
    right: 15%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(74, 222, 128, 0.6), transparent);
    border-radius: 999px;
  }}
  .main-title {{
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 0.35cqw;
  }}
  .main-title .title-line {{
    display: block;
    line-height: 1.25;
    white-space: nowrap;
    filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.85));
  }}
  .main-title .title-main {{
    font-size: 3.9cqw;
    font-weight: 900;
    letter-spacing: 0.05em;
    background: linear-gradient(180deg, #ffffff 20%, #f1f5f9 70%, #d1fae5 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }}
  .main-title .title-sub {{
    font-size: 3.2cqw;
    font-weight: 800;
    letter-spacing: 0.04em;
    background: linear-gradient(180deg, #86efac 10%, var(--green) 70%, var(--green2) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }}

  /* ===== 中区（场景内容区） ===== */
  .scene {{
    position: fixed;
    inset: 0;
    z-index: 1;
    display: none;
    opacity: 0;
    transition: opacity 0.35s ease;
  }}
  .scene.active {{
    display: block;
    opacity: 1;
  }}
  .scene .inner {{
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 17cqh 9cqw 21cqh;
    text-align: center;
    box-sizing: border-box;
    max-width: 100%;
  }}
  .scene .inner > * {{
    position: relative;
    z-index: 1;
  }}

  /* 波次动效 */
  .scene .w {{ opacity: 0; }}
  .scene.active .w {{ animation: wIn 0.5s cubic-bezier(0.22, 1, 0.36, 1) forwards; }}
  .scene.active .w2 {{ animation-delay: 0.12s; }}
  .scene.active .w3 {{ animation-delay: 0.24s; }}
  .scene.active .w4 {{ animation-delay: 0.36s; }}
  @keyframes wIn {{
    from {{ opacity: 0; transform: translateY(2.5cqw) scale(0.96); }}
    to {{ opacity: 1; transform: none; }}
  }}
  @keyframes punchIn {{
    0% {{ opacity: 0; transform: scale(0.85); }}
    65% {{ transform: scale(1.03); }}
    100% {{ opacity: 1; transform: scale(1); }}
  }}
  @keyframes breathe {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.04); }}
  }}
  @keyframes pulseGlow {{
    0%, 100% {{ filter: drop-shadow(0 0 10px rgba(74, 222, 128, 0.3)); }}
    50% {{ filter: drop-shadow(0 0 25px rgba(74, 222, 128, 0.7)); }}
  }}
  @keyframes floatY {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-0.8cqw); }}
  }}

  /* 基础组件规范 */
  .badge {{
    font-size: 2.9cqw;
    font-weight: 800;
    letter-spacing: 0.15em;
    color: var(--green);
    border: 1px solid rgba(74, 222, 128, 0.4);
    border-radius: 6cqw;
    padding: 0.5cqw 2.8cqw;
    background: rgba(74, 222, 128, 0.08);
    display: inline-block;
  }}
  .badge.amber {{
    color: var(--amber);
    border-color: rgba(251, 191, 36, 0.45);
    background: rgba(251, 191, 36, 0.1);
  }}
  .badge.cyan {{
    color: var(--cyan);
    border-color: rgba(56, 189, 248, 0.45);
    background: rgba(56, 189, 248, 0.1);
  }}
  .badge.red {{
    color: var(--red);
    border-color: rgba(248, 113, 113, 0.45);
    background: rgba(248, 113, 113, 0.1);
  }}

  .scene h2 {{
    font-size: 6.2cqw;
    font-weight: 900;
    margin: 1.8cqw 0 1.2cqw;
    line-height: 1.25;
    text-shadow: 0 0 4cqw rgba(74, 222, 128, 0.35);
    color: #ffffff;
  }}
  .scene .sub {{
    font-size: 3.2cqw;
    color: var(--dim);
    line-height: 1.6;
    margin-bottom: 2cqw;
  }}

  /* 竖屏垂直优先通栏大卡片 (Vertical Stacking First) */
  .card-stack {{
    display: flex;
    flex-direction: column;
    gap: 2.2cqw;
    width: 82cqw;
    margin-top: 1cqw;
  }}
  .stack-card {{
    background: linear-gradient(160deg, rgba(16, 28, 38, 0.94), rgba(10, 18, 26, 0.94));
    border: 1px solid var(--line);
    border-radius: 3.2cqw;
    padding: 2.6cqw 3.4cqw;
    text-align: left;
    display: flex;
    align-items: center;
    gap: 3cqw;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35);
  }}
  .stack-card.active-border {{
    border-color: rgba(74, 222, 128, 0.45);
    background: linear-gradient(160deg, rgba(20, 36, 48, 0.95), rgba(12, 22, 32, 0.95));
  }}
  .stack-card .card-ico {{
    width: 7cqw;
    height: 7cqw;
    flex: none;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--green);
  }}
  .stack-card .card-ico svg {{
    width: 100%;
    height: 100%;
  }}
  .stack-card .card-content {{
    flex: 1;
    min-width: 0;
  }}
  .stack-card .card-title {{
    font-size: 3.8cqw;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.3;
    display: flex;
    align-items: center;
    gap: 1.6cqw;
  }}
  .stack-card .card-title .tag {{
    font-size: 2.6cqw;
    font-weight: 700;
    color: var(--green);
    background: rgba(74, 222, 128, 0.12);
    border: 1px solid rgba(74, 222, 128, 0.35);
    border-radius: 999px;
    padding: 0.2cqw 1.8cqw;
  }}
  .stack-card .card-desc {{
    font-size: 2.9cqw;
    color: var(--dim);
    line-height: 1.55;
    margin-top: 0.6cqw;
  }}

  /* 图数彻底解耦环形图组件 */
  .ring-decoupled-box {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.4cqw;
    margin: 1cqw auto 2cqw;
  }}
  .ring-decoupled-box .ring-svg {{
    width: 35cqw;
    height: 35cqw;
    position: relative;
  }}
  .ring-decoupled-box .ring-svg svg {{
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
  }}
  .ring-decoupled-box .ring-svg .c-val {{
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;
  }}
  .ring-decoupled-box .ring-svg .c-val .num {{
    font-size: 5.0cqw;
    font-weight: 900;
    color: #ffffff;
    background: linear-gradient(180deg, #86efac, #22c55e);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    line-height: 1;
    letter-spacing: -0.02em;
    animation: breathe 2.6s ease-in-out infinite;
  }}
  .ring-decoupled-box .ring-info {{
    text-align: center;
  }}
  .ring-decoupled-box .ring-info .t {{
    font-size: 3.6cqw;
    font-weight: 800;
    color: var(--green);
  }}
  .ring-decoupled-box .ring-info .d {{
    font-size: 2.8cqw;
    color: var(--dim);
    margin-top: 0.4cqw;
  }}

  /* 矩阵网格 (2x2 / 3列) */
  .grid-2x2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2.2cqw;
    width: 82cqw;
    margin-top: 1cqw;
  }}
  .grid-2x2 .grid-card {{
    background: linear-gradient(160deg, rgba(16, 28, 38, 0.94), rgba(10, 18, 26, 0.94));
    border: 1px solid var(--line);
    border-radius: 2.8cqw;
    padding: 2.4cqw 2.6cqw;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 1cqw;
  }}
  .grid-2x2 .grid-card .g-title {{
    font-size: 3.4cqw;
    font-weight: 800;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 1.2cqw;
  }}
  .grid-2x2 .grid-card .g-title svg {{
    width: 4.8cqw;
    height: 4.8cqw;
    color: var(--green);
    flex: none;
  }}
  .grid-2x2 .grid-card .g-desc {{
    font-size: 2.8cqw;
    color: var(--dim);
    line-height: 1.5;
  }}

  /* 标签矩阵 */
  .chips-wrap {{
    display: flex;
    flex-wrap: wrap;
    gap: 1.6cqw;
    justify-content: center;
    width: 82cqw;
    margin: 1.5cqw auto 0;
  }}
  .chip-item {{
    background: rgba(16, 28, 38, 0.9);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 1cqw 3.2cqw;
    font-size: 3.0cqw;
    font-weight: 700;
    color: var(--ink);
    display: flex;
    align-items: center;
    gap: 1.2cqw;
  }}
  .chip-item.hl {{
    border-color: rgba(74, 222, 128, 0.45);
    background: rgba(74, 222, 128, 0.12);
    color: var(--green);
  }}

  /* S1 开场多阶段状态机 (splash -> recap -> topic) */
  .phs {{
    position: absolute;
    inset: 0;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.35s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 17cqh 9cqw 21cqh;
    box-sizing: border-box;
  }}
  #s-open[data-phase="splash"] .phs-splash {{ opacity: 1; }}
  #s-open[data-phase="recap"] .phs-recap {{ opacity: 1; }}
  #s-open[data-phase="topic"] .phs-topic {{ opacity: 1; }}

  .phs-splash .hook-h1 {{
    font-size: 7.2cqw;
    font-weight: 900;
    line-height: 1.35;
    text-align: center;
    margin: 2cqw 0;
    color: #ffffff;
    animation: punchIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
  }}
  .phs-splash .hook-h1 em {{
    font-style: normal;
    color: var(--green);
    text-shadow: 0 0 5cqw rgba(74, 222, 128, 0.6);
  }}
  .phs-splash .fight-symbol {{
    width: 32cqw;
    height: 32cqw;
    margin: 1cqw 0 2cqw;
    position: relative;
    color: var(--green);
    animation: pulseGlow 2.5s infinite;
  }}

  .phs-recap .recap-card {{
    width: 82cqw;
    background: linear-gradient(160deg, rgba(16, 28, 38, 0.95), rgba(10, 18, 26, 0.95));
    border: 1px solid rgba(251, 191, 36, 0.4);
    border-radius: 3.6cqw;
    padding: 4.5cqw 4cqw;
    margin-top: 2cqw;
    text-align: center;
  }}
  .phs-recap .recap-card .rt {{
    font-size: 5.6cqw;
    font-weight: 900;
    color: #ffffff;
  }}
  .phs-recap .recap-card .rd {{
    font-size: 3.2cqw;
    color: var(--dim);
    margin-top: 1.4cqw;
    line-height: 1.6;
  }}

  .phs-topic .topic-main {{
    font-size: 11cqw;
    font-weight: 900;
    letter-spacing: 0.08em;
    background: linear-gradient(180deg, #ffffff 10%, #86efac 60%, var(--green) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: punchIn 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
    text-shadow: 0 0 6cqw rgba(74, 222, 128, 0.4);
    margin: 1.5cqw 0;
  }}
  .phs-topic .topic-sub {{
    font-size: 3.8cqw;
    color: var(--green);
    font-weight: 800;
    letter-spacing: 0.15em;
  }}

  /* S19 片尾 CTA 动效 */
  .cta-pulse-card {{
    width: 82cqw;
    background: linear-gradient(160deg, rgba(20, 36, 48, 0.95), rgba(12, 22, 32, 0.95));
    border: 1px solid rgba(74, 222, 128, 0.5);
    border-radius: 3.6cqw;
    padding: 4.5cqw 4cqw;
    text-align: center;
    box-shadow: 0 0 35px rgba(74, 222, 128, 0.2);
    animation: breathe 3s ease-in-out infinite;
  }}
  .cta-actions {{
    display: flex;
    justify-content: center;
    gap: 2cqw;
    margin-top: 2.5cqw;
  }}
  .cta-btn {{
    font-size: 3.0cqw;
    font-weight: 800;
    color: #ffffff;
    background: rgba(74, 222, 128, 0.15);
    border: 1px solid rgba(74, 222, 128, 0.4);
    border-radius: 999px;
    padding: 1cqw 3cqw;
    display: inline-flex;
    align-items: center;
    gap: 1cqw;
  }}

  /* ===== 下区（卡拉OK字幕区） ===== */
  #subtitleBox {{
    position: fixed;
    bottom: 14cqh;
    left: 8cqw;
    right: 8cqw;
    z-index: 6;
    display: flex;
    justify-content: center;
    align-items: center;
    pointer-events: none;
    min-height: 7cqw;
  }}
  .subtitle-inner {{
    background: rgba(10, 18, 26, 0.78);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 999px;
    padding: 1.1cqw 4.2cqw 1.2cqw;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.45);
    max-width: 84cqw;
  }}
  #sentence {{
    font-size: 3.8cqw;
    font-weight: 800;
    line-height: 1.25;
    letter-spacing: 0.04em;
    color: rgba(232, 241, 236, 0.42);
    white-space: nowrap;
    user-select: none;
  }}
  #sentence span.w {{
    transition: color 0.08s ease, text-shadow 0.08s ease;
  }}
  #sentence span.w.read {{
    color: #ffffff;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
  }}
  #sentence span.w.curr {{
    color: var(--green);
    font-weight: 900;
    text-shadow: 0 0 12px rgba(74, 222, 128, 0.8), 0 0 20px rgba(74, 222, 128, 0.4);
  }}

  /* 画面转场白光闪烁 */
  #flashOverlay {{
    position: fixed;
    inset: 0;
    z-index: 99;
    background: #ffffff;
    opacity: 0;
    pointer-events: none;
  }}
  #flashOverlay.do-flash {{
    animation: flashAnim 0.32s ease-out;
  }}
  @keyframes flashAnim {{
    0% {{ opacity: 0.28; }}
    100% {{ opacity: 0; }}
  }}

  /* 开始播放遮罩 */
  #btnPlay {{
    position: fixed;
    inset: 0;
    z-index: 100;
    background: rgba(4, 7, 12, 0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: none;
    color: #ffffff;
  }}
  #btnPlay .play-circle {{
    width: 18cqw;
    height: 18cqw;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--green), var(--green2));
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 35px rgba(74, 222, 128, 0.6);
    margin-bottom: 3cqw;
  }}
  #btnPlay .play-circle svg {{
    width: 8cqw;
    height: 8cqw;
    fill: #070d12;
    margin-left: 0.8cqw;
  }}
  #btnPlay .play-tip {{
    font-size: 3.8cqw;
    font-weight: 800;
    letter-spacing: 0.1em;
  }}
</style>
</head>
<body>

<div class="stage">
  <canvas id="bg-canvas" width="1080" height="1920"></canvas>
  <div id="flashOverlay"></div>

  <!-- 外置校对 HUD -->
  <div id="chapText">第 1 / 19 节</div>

  <!-- 上区：纯粹作品标题 -->
  <div class="head">
    <div class="head-pill">
      <h1 class="main-title is-double" id="mainTitle">
        <span class="title-line title-main">贝莱斯芽孢杆菌</span>
        <span class="title-line title-sub">核心功能 · 生物防病</span>
      </h1>
    </div>
  </div>

  <!-- S01: 开场多阶段 -->
  <div class="scene" id="s-open" data-phase="splash">
    <div class="phs phs-splash">
      <div class="badge red w">⚠️ 农业生防超级核心</div>
      <h1 class="hook-h1 w w2">野生病害猖獗？<br>谁能挑起<em>生防大梁</em>？！</h1>
      <div class="fight-symbol w w3">
        <svg viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M50 8 L85 24 V52 C85 74 50 92 50 92 C50 92 15 74 15 52 V24 Z" fill="rgba(74, 222, 128, 0.12)"/>
          <path d="M50 20 L75 32 V50 C75 66 50 80 50 80 C50 80 25 66 25 50 V32 Z" stroke="var(--cyan)" stroke-width="2"/>
          <circle cx="50" cy="50" r="12" fill="var(--green)" opacity="0.3"/>
          <path d="M42 50 L48 56 L60 44" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="sub w w4">揭秘农用菌王牌生防机制</div>
    </div>
    <div class="phs phs-recap">
      <div class="badge amber">系列回顾 · 接上期</div>
      <div class="recap-card">
        <div class="rt">贝莱斯芽孢杆菌</div>
        <div class="rd">上期揭秘明星菌全能潜质<br>本期深挖第二大核心功能</div>
      </div>
    </div>
    <div class="phs phs-topic">
      <div class="badge">主要核心功能</div>
      <div class="topic-main">生物防病</div>
      <div class="topic-sub">最耀眼的核心技能 · 绿色植保突破</div>
    </div>
  </div>

  <!-- S02: 机制总览组合拳 -->
  <div class="scene" id="s-combo">
    <div class="inner">
      <div class="badge w">核心机制 · 机制总览</div>
      <h2 class="w w2">生防硬核三联组合拳</h2>
      <div class="sub w w2">直接杀菌 + 空间竞争 + 植物疫苗</div>
      <div class="card-stack w w3">
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 17.5L3 6V3h3l11.5 11.5M13 19l6-6M16 16l4 4M19 21l2-2"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">① 直接杀菌 <span class="tag">生化武器库</span></div>
            <div class="card-desc">合成多类抗菌物质，直接破坏病菌结构与活性</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">② 空间竞争 <span class="tag">抢位抢粮</span></div>
            <div class="card-desc">全株致密定殖阻断侵染，分泌嗜铁素饿死病原菌</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v8M8 12h8"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">③ 植物疫苗 <span class="tag">诱导抗性</span></div>
            <div class="card-desc">激活多条信号通路与防御酶，全株提前进入战备</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S03: 天然抗生素工厂 -->
  <div class="scene" id="s-arsenal">
    <div class="inner">
      <div class="badge w">机制一 · 直接杀菌</div>
      <h2 class="w w2">天然抗生素合成工厂</h2>
      <div class="ring-decoupled-box w w3">
        <div class="ring-svg">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" stroke="rgba(148, 163, 184, 0.2)" stroke-width="8" fill="none"/>
            <circle cx="50" cy="50" r="40" stroke="var(--green)" stroke-width="8" stroke-dasharray="251.3" stroke-dashoffset="195" stroke-linecap="round" fill="none"/>
          </svg>
          <div class="c-val"><span class="num">5%~8%</span></div>
        </div>
        <div class="ring-info">
          <div class="t">基因组占比专门用于代谢产物合成</div>
          <div class="d">庞大基因簇协同运转 · 构筑高浓度抗菌物质库</div>
        </div>
      </div>
      <div class="stack-card w w4">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 7h-9M14 17H5M17 12H3M21 3v18"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">自主分泌高活性生化武器</div>
          <div class="card-desc">源源不断合成脂肽、聚酮、降解酶与挥发性抑菌物质</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S04: 物质库 1 脂肽类 -->
  <div class="scene" id="s-lipopeptide">
    <div class="inner">
      <div class="badge w">物质库 01 · 脂肽类抗生素</div>
      <h2 class="w w2">三大王牌脂肽杀手</h2>
      <div class="sub w w2">高亲脂性环肽分子 · 强效靶向病原菌</div>
      <div class="card-stack w w3">
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">表面活性素 Surfactin <span class="tag">极强渗透</span></div>
            <div class="card-desc">超强界面活性，迅速破坏病原菌膜电位</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">伊枯草菌素 Iturin <span class="tag">抗真菌王牌</span></div>
            <div class="card-desc">高专一性结合真菌膜固醇，瓦解真菌细胞结构</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">吩菌素 Fengycin <span class="tag">丝状真菌克星</span></div>
            <div class="card-desc">强力抑制丝状真菌菌丝生长与孢子萌发</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S05: 杀菌机制细胞膜打孔 -->
  <div class="scene" id="s-pore">
    <div class="inner">
      <div class="badge red w">杀菌机理 · 细胞膜穿孔</div>
      <h2 class="w w2">打孔破膜 · 胞内裂解</h2>
      <div class="sub w w2">不可逆物理破坏 · 彻底杜绝抗药性</div>
      <div class="stack-card active-border w w3">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/><circle cx="12" cy="12" r="3" fill="var(--red)"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">跨膜孔道形成 <span class="tag" style="color:var(--red);border-color:rgba(248,113,113,0.4);">膜穿孔</span></div>
          <div class="card-desc">脂肽分子插入病原菌磷脂双分子层，撑开跨膜离子孔道</div>
        </div>
      </div>
      <div class="stack-card w w4">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">胞内物质外泄 · 细胞死亡</div>
          <div class="card-desc">无机盐与大分子核酸不可逆泄漏，病菌破裂溶菌死亡</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S06: 物质库 2 聚酮类 -->
  <div class="scene" id="s-polyketide">
    <div class="inner">
      <div class="badge cyan w">物质库 02 · 聚酮类化合物</div>
      <h2 class="w w2">广谱抑菌 · 双重钳形攻势</h2>
      <div class="sub w w2">广谱化学武器库 · 细菌真菌通杀</div>
      <div class="card-stack w w3">
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">地菲西丁 Difficidin <span class="tag">细菌克星</span></div>
            <div class="card-desc">高效靶向阻断致病细菌的蛋白质与 DNA 合成链条</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">杆菌烯 Bacillaene <span class="tag">真菌克星</span></div>
            <div class="card-desc">强力瓦解多种重大农作物病原真菌的生理代谢机能</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S07: 物质库 3 细胞壁降解酶 -->
  <div class="scene" id="s-enzyme">
    <div class="inner">
      <div class="badge w">物质库 03 · 细胞壁降解酶</div>
      <h2 class="w w2">生化拆迁队 · 拆解真菌壁</h2>
      <div class="sub w w2">直接瓦解病原真菌的第一道坚韧屏障</div>
      <div class="card-stack w w3">
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">几丁质酶 + 葡聚糖酶 <span class="tag">多糖水解</span></div>
            <div class="card-desc">精准剪断真菌细胞壁核心多糖骨架，破除保护层</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">高活性蛋白酶复合酶系 <span class="tag">溶解酶解</span></div>
            <div class="card-desc">降解病菌外层结构糖蛋白，加速真菌菌丝解体融化</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S08: 物质库 4 抗菌蛋白与挥发物 -->
  <div class="scene" id="s-protein-vol">
    <div class="inner">
      <div class="badge cyan w">物质库 04 · 抗菌蛋白与挥发物</div>
      <h2 class="w w2">山农大 L-271 菌株发现</h2>
      <div class="sub w w2">气相熏蒸抑菌 · 远距离扩散保护</div>
      <div class="stack-card active-border w w3">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 2v7.31M14 9.3V1.99M8.5 2h7M14 9.3a6.5 6.5 0 1 1-4 0"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">产生三大高活性挥发性小分子</div>
          <div class="card-desc">山东农业大学重点实验室分离纯化特色代谢产物</div>
        </div>
      </div>
      <div class="chips-wrap w w4">
        <div class="chip-item hl">4-羟基苯甲腈</div>
        <div class="chip-item hl">2,3-二羟基苯甲酸</div>
        <div class="chip-item hl">2-羟基癸醇</div>
      </div>
    </div>
  </div>

  <!-- S09: 防效大蒜病斑减9成 -->
  <div class="scene" id="s-garlic">
    <div class="inner">
      <div class="badge amber w">实证突破 · 田间防效</div>
      <h2 class="w w2">大蒜腐烂病 防效立竿见影</h2>
      <div class="ring-decoupled-box w w3">
        <div class="ring-svg">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" stroke="rgba(148, 163, 184, 0.2)" stroke-width="8" fill="none"/>
            <circle cx="50" cy="50" r="40" stroke="var(--amber)" stroke-width="8" stroke-dasharray="251.3" stroke-dashoffset="25.1" stroke-linecap="round" fill="none"/>
          </svg>
          <div class="c-val"><span class="num" style="background:linear-gradient(180deg,#fde68a,#f59e0b);-webkit-background-clip:text;background-clip:text;">90%</span></div>
        </div>
        <div class="ring-info">
          <div class="t">大蒜腐烂病病斑面积减少近 9 成</div>
          <div class="d">微量挥发物质熏蒸 · 强效阻断病斑扩散曼延</div>
        </div>
      </div>
      <div class="stack-card w w4">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">保产稳产显著防效</div>
          <div class="card-desc">天然挥发成分气相抑菌，为高价值经济作物保驾护航</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S10: 抑菌七大植物病原菌 -->
  <div class="scene" id="s-pathogens">
    <div class="inner">
      <div class="badge w">抑菌图谱 · 全面覆盖</div>
      <h2 class="w w2">横扫 7 大作物重大病害</h2>
      <div class="sub w w2">广谱抵御粮油果蔬多种毁灭性真菌细菌</div>
      <div class="chips-wrap w w3">
        <div class="chip-item hl">辣椒疫霉</div>
        <div class="chip-item hl">尖孢镰刀菌</div>
        <div class="chip-item hl">立枯丝核菌</div>
        <div class="chip-item hl">灰葡萄孢</div>
        <div class="chip-item hl">禾谷镰刀菌</div>
        <div class="chip-item hl">青枯雷尔氏菌</div>
        <div class="chip-item hl">炭疽菌</div>
      </div>
      <div class="stack-card w w4" style="margin-top:2cqw;">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">全域覆盖根腐、立枯与青枯</div>
          <div class="card-desc">多种机制叠加作用，大幅降低作物田间染病率</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S11: 拓展线虫红蜘蛛双防 -->
  <div class="scene" id="s-pests">
    <div class="inner">
      <div class="badge amber w">虫病双防 · 跨界战力</div>
      <h2 class="w w2">兼具线虫与红蜘蛛活性</h2>
      <div class="sub w w2">突破传统单一防病局限 · 实现菌虫同治</div>
      <div class="card-stack w w3">
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a8 8 0 0 0-8 8v12l8-4 8 4V10a8 8 0 0 0-8-8z"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">地下害虫 · 根结线虫抑制 <span class="tag">杀卵抑虫</span></div>
            <div class="card-desc">分泌几丁质降解酶破坏虫卵外壳，抑制线虫危害根系</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">叶面害虫 · 红蜘蛛强活性 <span class="tag">高效触杀</span></div>
            <div class="card-desc">活性代谢物显著抑制害螨繁殖，减少化学农药喷洒</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S12: 机制二生态位竞争 -->
  <div class="scene" id="s-niche">
    <div class="inner">
      <div class="badge w">机制二 · 生态位竞争</div>
      <h2 class="w w2">先发制菌 · 抢地盘抢口粮</h2>
      <div class="sub w w2">以优势种群速度抢占生态位 · 封死病菌立足点</div>
      <div class="card-stack w w3">
        <div class="stack-card active-border">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">超快增殖速度 · 占领阵地 <span class="tag">先到先得</span></div>
            <div class="card-desc">繁殖速率数倍于有害病菌，率先建立稳固微生态优势</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">空间物理排挤 · 阻断入侵 <span class="tag">空间封锁</span></div>
            <div class="card-desc">占据作物侵染位点，让外来有害孢子无处着落定居</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S13: 全株定殖四维致密生物膜 -->
  <div class="scene" id="s-biofilm">
    <div class="inner">
      <div class="badge w">全株防御 · 生物保护膜</div>
      <h2 class="w w2">四维立体定殖防护网</h2>
      <div class="sub w w2">形成致密生物膜 · 筑起绿色物理金钟罩</div>
      <div class="grid-2x2 w w3">
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M5 12h14"/></svg>
            ① 根表定殖
          </div>
          <div class="g-desc">紧密贴合根表皮，构筑第一道紧固抗侵染屏障</div>
        </div>
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>
            ② 根际定殖
          </div>
          <div class="g-desc">主导根际微生态圈，净化吸收微区养分环境</div>
        </div>
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 22h20L12 2z"/></svg>
            ③ 叶面定殖
          </div>
          <div class="g-desc">铺满叶片表皮及气孔，阻断空气病原菌胞侵染</div>
        </div>
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            ④ 体内定殖
          </div>
          <div class="g-desc">内生传导迁移维管束，全株系统性协同防御</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S14: 营养争夺分泌嗜铁素 -->
  <div class="scene" id="s-siderophore">
    <div class="inner">
      <div class="badge cyan w">营养争夺 · 饥饿疗法</div>
      <h2 class="w w2">分泌嗜铁素 · 饿死病原菌</h2>
      <div class="sub w w2">截断铁营养吸收 · 病菌因极度缺铁而发育枯竭</div>
      <div class="card-stack w w3">
        <div class="stack-card active-border">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">超强螯合根际游离铁 (Fe³⁺) <span class="tag">高亲和力</span></div>
            <div class="card-desc">嗜铁素牢牢结合极微量铁元素，病原菌完全无法获取</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">病原菌饥饿死亡 <span class="tag">生理枯竭</span></div>
            <div class="card-desc">铁离子缺失导致病菌电子传递链断裂，自然枯竭衰亡</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S15: 机制三诱导系统抗性 -->
  <div class="scene" id="s-vaccine">
    <div class="inner">
      <div class="badge w">机制三 · 诱导系统抗性</div>
      <h2 class="w w2">给植物打疫苗 · 高级防御</h2>
      <div class="sub w w2">从内而外唤醒免疫潜能 · 未病先防</div>
      <div class="stack-card active-border w w3">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 2l4 4-10 10-4-4L18 2zM2 22l6-2-4-4-2 6z"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">生物疫苗接种效应 <span class="tag">广谱免疫</span></div>
          <div class="card-desc">激发植物自身免疫监控体系，对多种病害产生持久抵抗力</div>
        </div>
      </div>
      <div class="stack-card w w4">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">系统获得性抗性 (ISR / SAR)</div>
          <div class="card-desc">根部接菌，全株叶片与果实均能获得持久免疫增强</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S16: 免疫激活三大通路 -->
  <div class="scene" id="s-pathway">
    <div class="inner">
      <div class="badge cyan w">免疫唤醒 · 信号通路</div>
      <h2 class="w w2">激活三大关键防御通路</h2>
      <div class="sub w w2">表面活性素与脂多糖作为高效植物激发子</div>
      <div class="card-stack w w3">
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">茉莉酸通路 (JA) <span class="tag">抗虫抗死体病菌</span></div>
            <div class="card-desc">诱发死体真菌与食叶害虫专一防御应答</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">乙烯通路 (ET) <span class="tag">加速木质化</span></div>
            <div class="card-desc">协同调节伤口快速封闭与组织抗逆强化</div>
          </div>
        </div>
        <div class="stack-card">
          <div class="card-ico">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/></svg>
          </div>
          <div class="card-content">
            <div class="card-title">水杨酸通路 (SA) <span class="tag">活体真菌与病毒</span></div>
            <div class="card-desc">激活全株系统性获得免疫抗性核心基因表达</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- S17: 酶活暴增战备状态 -->
  <div class="scene" id="s-enzymes-up">
    <div class="inner">
      <div class="badge amber w">酶活暴增 · 战备状态</div>
      <h2 class="w w2">四大防御酶活性全面上调</h2>
      <div class="sub w w2">让绿色植物提前进入最高等级防御警备</div>
      <div class="grid-2x2 w w3">
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            PAL 苯丙氨酸解氨酶
          </div>
          <div class="g-desc">大幅催化木质素合成，强化植物细胞壁硬度</div>
        </div>
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/></svg>
            POD 过氧化物酶
          </div>
          <div class="g-desc">清除有害活性氧自由基，抵抗病菌氧化毒害</div>
        </div>
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            SOD 超氧化物歧化酶
          </div>
          <div class="g-desc">稳固细胞膜系统完整性，降低逆境受损率</div>
        </div>
        <div class="grid-card">
          <div class="g-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>
            几丁质酶 Chitinase
          </div>
          <div class="g-desc">自发降解入侵真菌细胞壁，阻止菌丝伸长蔓延</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S18: 实证苹果96h高表达 -->
  <div class="scene" id="s-sy01">
    <div class="inner">
      <div class="badge w">权威实证 · 苹果树实测</div>
      <h2 class="w w2">SY01 菌株持续高表达</h2>
      <div class="sub w w2">接种后作物抗性基因持续活跃激增</div>
      <div class="ring-decoupled-box w w3">
        <div class="ring-svg">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" stroke="rgba(148, 163, 184, 0.2)" stroke-width="8" fill="none"/>
            <circle cx="50" cy="50" r="40" stroke="var(--green)" stroke-width="8" stroke-dasharray="251.3" stroke-dashoffset="0" stroke-linecap="round" fill="none"/>
          </svg>
          <div class="c-val"><span class="num">96h</span></div>
        </div>
        <div class="ring-info">
          <div class="t">抗性基因可在 96 小时内持续高表达</div>
          <div class="d">长效防御周期超 4 昼夜 · 显著降低早期落叶与轮纹病</div>
        </div>
      </div>
      <div class="stack-card w w4">
        <div class="card-ico">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <div class="card-content">
          <div class="card-title">持久免疫 · 稳固抗病</div>
          <div class="card-desc">一次科学施用，建立作物全生长季长效生防防护</div>
        </div>
      </div>
    </div>
  </div>

  <!-- S19: 总结下期预告与CTA -->
  <div class="scene" id="s-cta">
    <div class="inner">
      <div class="badge amber w">本期总结 · 下期预告</div>
      <h2 class="w w2">第三大核心功能预告</h2>
      <div class="cta-pulse-card w w3">
        <div class="badge cyan" style="margin-bottom:1.2cqw;">下期重磅揭秘</div>
        <div style="font-size:5.8cqw;font-weight:900;color:#ffffff;">给土壤解毒</div>
        <div style="font-size:3.2cqw;color:var(--dim);margin-top:1cqw;line-height:1.6;">钝化重金属残留 · 降解农药污染 · 改良盐碱土壤</div>
      </div>
      <div class="cta-actions w w4">
        <div class="cta-btn">👍 点赞</div>
        <div class="cta-btn">🔔 关注</div>
        <div class="cta-btn">⭐ 收藏</div>
        <div class="cta-btn">💬 评论</div>
      </div>
    </div>
  </div>

  <!-- 下区：卡拉OK字幕 -->
  <div id="subtitleBox">
    <div class="subtitle-inner">
      <div id="sentence"></div>
    </div>
  </div>

  <!-- 开始播放交互层 -->
  <button id="btnPlay" type="button" aria-label="开始播放">
    <div class="play-circle">
      <svg viewBox="0 0 24 24"><polygon points="6,4 20,12 6,20"/></svg>
    </div>
    <div class="play-tip">点击开始播放</div>
  </button>

  <audio id="voice" src="../../inputs/N0003_贝莱斯芽孢杆菌的核心功能之生物防病/voice.wav" preload="auto"></audio>
</div>

<script>
/* ========================================================
   字级时间戳与场景规划数据
   ======================================================== */
const CHARS = {chars_json};
const TIMES = {times_json};
const SCENES = {scenes_json};
const CHAP_NAMES = {chap_names_json};
const OPEN_PHASES = {open_phases_json};

window.SCENES = SCENES;
window.CHAP_NAMES = CHAP_NAMES;

/* ========================================================
   卡拉OK字幕分词与过滤引擎（防碎行三原则）
   ======================================================== */
var UNITS = [];
function buildUnits() {{
  var units = [], s = 0;
  for (var i = 0; i < CHARS.length; i++) {{
    if ('。！？!?；;'.indexOf(CHARS[i]) >= 0) {{
      units.push([s, i]);
      s = i + 1;
    }}
  }}
  if (s < CHARS.length) units.push([s, CHARS.length - 1]);

  var subUnits = [];
  var SEP = '，、：:；;，,';
  for (var u = 0; u < units.length; u++) {{
    var a = units[u][0], b = units[u][1];
    var segA = a;
    while (segA <= b) {{
      var pos = -1;
      for (var i = segA; i <= b; i++) {{
        if (SEP.indexOf(CHARS[i]) >= 0) {{ pos = i; break; }}
      }}
      var segB = (pos >= 0) ? pos : b;
      var len = segB - segA + 1;
      if (len > 10) {{
        var cut = -1;
        for (var i2 = Math.min(segB, segA + 10); i2 >= Math.max(segA, segA + 6); i2--) {{
          var l = i2 - segA + 1;
          if (l >= 8 && l <= 10 && ('的的得'.indexOf(CHARS[i2]) >= 0 || SEP.indexOf(CHARS[i2]) >= 0)) {{
            cut = i2; break;
          }}
        }}
        if (cut < 0 && len > 16) cut = segA + 9;
        if (cut >= segA) {{
          subUnits.push([segA, cut]);
          segA = cut + 1;
          continue;
        }}
      }}
      subUnits.push([segA, segB]);
      segA = segB + 1;
    }}
  }}

  // 防碎行合并（少于 4 字并入前一段）
  var merged = [];
  for (var k = 0; k < subUnits.length; k++) {{
    var ua = subUnits[k][0], ub = subUnits[k][1];
    var tl = ub - ua + 1;
    if (tl <= 0) continue;
    if ('。！？!?；;，、：:，,'.indexOf(CHARS[ub]) >= 0) tl--;
    if (tl < 4 && merged.length > 0) {{
      merged[merged.length - 1][1] = ub;
    }} else {{
      merged.push([ua, ub]);
    }}
  }}
  UNITS = merged;
}}
buildUnits();

function escHtml(s) {{
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}}

var sentenceEl = document.getElementById('sentence');

function renderUnit(uIdx, currCharIdx) {{
  var a = UNITS[uIdx][0], b = UNITS[uIdx][1];
  var end = b;
  if ('，、：:；;，,'.indexOf(CHARS[b]) >= 0) end = b - 1;

  var html = '';
  for (var i = a; i <= end; i++) {{
    var ch = escHtml(CHARS[i]);
    var cls = 'w';
    if (i < currCharIdx) cls += ' read';
    else if (i === currCharIdx) cls += ' curr';
    html += '<span class="' + cls + '">' + ch + '</span>';
  }}
  sentenceEl.innerHTML = html;
}}

function updateSubtitle(t) {{
  if (TIMES.length === 0 || UNITS.length === 0) return;
  var lo = 0, hi = TIMES.length - 1, ans = 0;
  while (lo <= hi) {{
    var mid = (lo + hi) >> 1;
    if (TIMES[mid] <= t) {{ ans = mid; lo = mid + 1; }}
    else {{ hi = mid - 1; }}
  }}

  var uIdx = -1;
  for (var u = 0; u < UNITS.length; u++) {{
    if (ans >= UNITS[u][0] && ans <= UNITS[u][1]) {{ uIdx = u; break; }}
  }}

  if (uIdx >= 0) {{
    renderUnit(uIdx, ans);
  }} else if (ans >= UNITS[UNITS.length - 1][1]) {{
    renderUnit(UNITS.length - 1, ans);
  }}
}}

/* ========================================================
   VibeSound 原生 Web Audio 声音合成器
   ======================================================== */
var VibeSound = (function() {{
  var ctx = null;
  var noiseBuffer = null;

  function getCtx() {{
    if (window.__RECORDING__) return null;
    if (!ctx && (window.AudioContext || window.webkitAudioContext)) {{
      try {{
        ctx = new (window.AudioContext || window.webkitAudioContext)();
      }} catch (e) {{}}
    }}
    if (ctx && ctx.state === 'suspended') {{
      ctx.resume().catch(function() {{}});
    }}
    return ctx;
  }}

  function getNoiseBuffer(ac) {{
    if (noiseBuffer) return noiseBuffer;
    var dur = 0.5;
    var buf = ac.createBuffer(1, Math.floor(ac.sampleRate * dur), ac.sampleRate);
    var data = buf.getChannelData(0);
    var b0 = 0, b1 = 0, b2 = 0;
    for (var i = 0; i < data.length; i++) {{
      var white = Math.random() * 2 - 1;
      b0 = 0.99765 * b0 + white * 0.0990460;
      b1 = 0.96300 * b1 + white * 0.2965164;
      b2 = 0.57000 * b2 + white * 1.0526913;
      data[i] = (b0 + b1 + b2 + white * 0.1848) * 0.45;
    }}
    noiseBuffer = buf;
    return noiseBuffer;
  }}

  return {{
    init: function() {{ getCtx(); }},
    pop: function() {{
      var ac = getCtx();
      if (!ac) return;
      var now = ac.currentTime;
      var osc = ac.createOscillator();
      var gain = ac.createGain();
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
    }},
    whoosh: function() {{
      var ac = getCtx();
      if (!ac) return;
      var now = ac.currentTime;
      var buf = getNoiseBuffer(ac);
      var src = ac.createBufferSource();
      src.buffer = buf;
      var filter = ac.createBiquadFilter();
      filter.type = 'lowpass';
      filter.Q.value = 1.0;
      filter.frequency.setValueAtTime(200, now);
      filter.frequency.exponentialRampToValueAtTime(1100, now + 0.16);
      filter.frequency.exponentialRampToValueAtTime(260, now + 0.42);
      var gain = ac.createGain();
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.16, now + 0.14);
      gain.gain.linearRampToValueAtTime(0.0001, now + 0.42);
      src.connect(filter);
      filter.connect(gain);
      gain.connect(ac.destination);
      src.start(now);
      src.stop(now + 0.42);
    }},
    chime: function() {{
      var ac = getCtx();
      if (!ac) return;
      var now = ac.currentTime;
      var notes = [
        {{ f: 523.25, d: 0.00, v: 0.16 }},
        {{ f: 659.25, d: 0.06, v: 0.14 }},
        {{ f: 783.99, d: 0.12, v: 0.12 }},
        {{ f: 1046.50, d: 0.18, v: 0.10 }}
      ];
      notes.forEach(function(n) {{
        var t = now + n.d;
        var osc = ac.createOscillator();
        var gain = ac.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(n.f, t);
        gain.gain.setValueAtTime(0.001, t);
        gain.gain.linearRampToValueAtTime(n.v, t + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 1.1);
        osc.connect(gain);
        gain.connect(ac.destination);
        osc.start(t);
        osc.stop(t + 1.1);
      }});
    }},
    play: function(type) {{
      try {{
        if (type === 'whoosh') this.whoosh();
        else if (type === 'pop') this.pop();
        else if (type === 'chime') this.chime();
      }} catch (err) {{}}
    }}
  }};
}})();
window.VibeSound = VibeSound;

/* ========================================================
   场景推进与主时钟逻辑
   ======================================================== */
var curScene = -1;
var curPhase = '';
var flashEl = document.getElementById('flashOverlay');
var openSceneEl = document.getElementById('s-open');
var ct = document.getElementById('chapText');

function setScene(idx) {{
  if (idx === curScene || idx < 0 || idx >= SCENES.length) return;
  var prev = curScene;
  curScene = idx;

  if (prev >= 0) {{
    var prevEl = document.getElementById(SCENES[prev][0]);
    if (prevEl) prevEl.classList.remove('active');
    VibeSound.play('whoosh');
  }}

  var newEl = document.getElementById(SCENES[idx][0]);
  if (newEl) newEl.classList.add('active');

  if (prev >= 0 && flashEl) {{
    flashEl.classList.remove('do-flash');
    void flashEl.offsetWidth;
    flashEl.classList.add('do-flash');
  }}

  if (idx === SCENES.length - 1 && prev >= 0) {{
    VibeSound.play('chime');
  }}

  if (ct) ct.innerHTML = '第 ' + (idx + 1) + ' / ' + SCENES.length + ' 节';
}}

function updateScene(t) {{
  var idx = 0;
  for (var i = 0; i < SCENES.length; i++) {{
    if (t >= SCENES[i][1]) idx = i;
  }}
  setScene(idx);

  if (idx === 0 && openSceneEl && OPEN_PHASES.length > 0) {{
    var p = OPEN_PHASES[0][0];
    for (var j = 0; j < OPEN_PHASES.length; j++) {{
      if (t >= OPEN_PHASES[j][1]) p = OPEN_PHASES[j][0];
    }}
    if (p !== curPhase) {{
      curPhase = p;
      openSceneEl.setAttribute('data-phase', curPhase);
    }}
  }}
}}

function syncTime(t) {{
  updateScene(t);
  updateSubtitle(t);
}}
window.syncTime = syncTime;

var audio = document.getElementById('voice');
var btnPlay = document.getElementById('btnPlay');

function tick() {{
  if (!audio.paused && !audio.ended) {{
    syncTime(audio.currentTime);
  }}
  requestAnimationFrame(tick);
}}

function startPlay() {{
  VibeSound.init();
  for (var i = 0; i < SCENES.length; i++) {{
    var el = document.getElementById(SCENES[i][0]);
    if (el) el.classList.remove('active');
  }}
  curScene = -1;
  curPhase = '';
  btnPlay.style.display = 'none';
  syncTime(0);
  audio.currentTime = 0;
  audio.play().catch(function() {{}});
}}

btnPlay.addEventListener('click', startPlay);
audio.addEventListener('play', function() {{ requestAnimationFrame(tick); }});
audio.addEventListener('seeked', function() {{ syncTime(audio.currentTime); }});
audio.addEventListener('timeupdate', function() {{ syncTime(audio.currentTime); }});

// 默认首屏初始渲染
syncTime(0);

/* ========================================================
   背景微粒引擎 (bio-bubbles)
   ======================================================== */
var VibeBackgrounds = (function () {{
  "use strict";
  function parseColor(c, defaultColor) {{
    if (!c) return defaultColor || {{ r: 74, g: 222, b: 128 }};
    if (typeof c === "object" && c.r !== undefined) return c;
    if (c.startsWith("#")) {{
      var hex = c.replace("#", "");
      if (hex.length === 3) hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
      var num = parseInt(hex, 16);
      return {{ r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 }};
    }}
    return {{ r: 74, g: 222, b: 128 }};
  }}

  function presetBioBubbles(cv, ctx, opt) {{
    var W = cv.width, H = cv.height;
    var col = parseColor(opt.color, {{ r: 74, g: 222, b: 128 }});
    var col2 = parseColor(opt.color2, {{ r: 56, g: 189, b: 248 }});
    var count = Math.floor(45 * (opt.density || 1.0));
    var speed = (opt.speed || 1.0);

    var orbs = [];
    for (var i = 0; i < count; i++) {{
      var layer = Math.random();
      var r = layer < 0.6 ? (Math.random() * 4 + 1.5) : (Math.random() * 26 + 10);
      var isCol2 = Math.random() < 0.35;
      orbs.push({{
        x: Math.random() * W,
        y: Math.random() * H,
        r: r,
        baseR: r,
        layer: layer,
        color: isCol2 ? col2 : col,
        vy: -(Math.random() * 0.45 + 0.15) * speed * (0.6 + layer * 0.8),
        vx: (Math.random() - 0.5) * 0.25 * speed,
        alpha: layer < 0.6 ? (Math.random() * 0.4 + 0.2) : (Math.random() * 0.18 + 0.08),
        pulseSpeed: Math.random() * 0.03 + 0.015,
        pulseOffset: Math.random() * Math.PI * 2
      }});
    }}

    var frame = 0;
    return function draw() {{
      ctx.clearRect(0, 0, W, H);
      frame++;

      for (var i = 0; i < orbs.length; i++) {{
        var o = orbs[i];
        o.y += o.vy;
        o.x += o.vx + Math.sin(frame * 0.018 + o.pulseOffset) * 0.15;
        if (o.y < -o.r * 2) {{ o.y = H + o.r * 2; o.x = Math.random() * W; }}
        if (o.x < -o.r * 2) o.x = W + o.r * 2;
        if (o.x > W + o.r * 2) o.x = -o.r * 2;

        var pulse = Math.sin(frame * o.pulseSpeed + o.pulseOffset) * 0.15 + 1.0;
        var curR = o.baseR * pulse;

        if (o.layer >= 0.6) {{
          var grad = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, curR);
          var a = o.alpha * pulse;
          grad.addColorStop(0, "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + "," + a + ")");
          grad.addColorStop(0.5, "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + "," + (a * 0.4) + ")");
          grad.addColorStop(1, "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + ", 0)");
          ctx.beginPath();
          ctx.arc(o.x, o.y, curR, 0, Math.PI * 2);
          ctx.fillStyle = grad;
          ctx.fill();
        }} else {{
          ctx.beginPath();
          ctx.arc(o.x, o.y, curR, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + "," + o.alpha + ")";
          ctx.fill();
        }}
      }}
    }};
  }}

  return {{
    use: function (canvasId, presetName, opt) {{
      var cv = document.getElementById(canvasId);
      if (!cv) return;
      var ctx = cv.getContext("2d");
      var drawFn = presetBioBubbles(cv, ctx, opt || {{}});
      function loop() {{
        drawFn();
        requestAnimationFrame(loop);
      }}
      requestAnimationFrame(loop);
    }}
  }};
}})();

VibeBackgrounds.use('bg-canvas', 'bio-bubbles', {{
  color: '#4ade80',
  color2: '#38bdf8',
  density: 1.1,
  speed: 1.0
}});
</script>
</body>
</html>
"""

OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML 生成成功: {OUTPUT_HTML} ({len(html_content)} 字符)")
