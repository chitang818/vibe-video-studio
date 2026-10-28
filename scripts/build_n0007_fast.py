# -*- coding: utf-8 -*-
"""Builder script for N0007 高速 Canvas 工程
根据 references/fast-project.md 规范：
1. 连续覆盖 [0, 141943562] 微秒
2. 严格四边安全区约束 (横向 8%..92% 即 86.4..993.6, 纵向 10%..78% 即 192..1497.6)
3. 文本行高与尺寸精确计算，0 溢出
4. 包含丰富图表 (ring, bar, rect) 与递进动效 (enterUs, pulse, valueDurationUs)
5. 自动构建并执行浏览器 Playwright audit 门禁
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


ROOT_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = Path(r"c:\Users\chitang\Downloads\N0007_丛枝菌根菌剂对比")
VOICE_WAV = INPUT_DIR / "N0007_voice.wav"
TIMESTAMPS_JSON = INPUT_DIR / "N0007_char_timestamps.json"
OUT_PROJECT = ROOT_DIR / "projects" / "N0007_丛枝菌根菌剂对比"

with wave.open(str(VOICE_WAV), 'rb') as f:
    DURATION_US = round(f.getnframes() / f.getframerate() * 1e6)

print(f"音频精确微秒数: {DURATION_US}")

# 颜色设计调色板 (深海生物/高科技菌剂护航风格)
BG_HEADER = "#09222b"
BORDER_HEADER = "#14b8a6"
TAG_COLOR = "#2dd4bf"
TITLE_COLOR = "#ffffff"

CARD1_BG = "#0c1b22"
CARD1_BORDER = "#1b3846"
CARD1_BADGE_BG = "#134e4a"
CARD1_BADGE_COLOR = "#5eead4"
CARD1_TITLE_COLOR = "#f1f5f9"
CARD1_TEXT_COLOR = "#94a3b8"

CARD2_BG = "#08262a"
CARD2_BORDER = "#0f766e"
CARD2_BADGE_BG = "#065f46"
CARD2_BADGE_COLOR = "#34d399"
CARD2_TITLE_COLOR = "#6ee7b7"
CARD2_TEXT_COLOR = "#e2e8f0"

scenes_data = [
    {
        "id": "scene_01",
        "title": "丛枝菌根真菌 vs 早期真菌菌剂",
        "category": "VIBE 知识大赏 · 真菌菌剂深度剖析",
        "startUs": 0,
        "endUs": 10000000,
        "c1_badge": "前情回顾",
        "c1_title": "丛枝菌根促进养分吸收与应用优势",
        "c1_text": "· 建立共生菌根网络，根际养分吸收呈倍数提升\n· 促生增产与抗逆机制在现代生态农业发挥核心效能",
        "c1_type": "bar",
        "c1_val": 0.45,
        "c1_to_val": 0.88,
        "c2_badge": "本期焦点",
        "c2_title": "对比传统早期真菌：强在哪？局限在哪？",
        "c2_text": "· 深入比对毛霉、曲霉、酵母菌剂三大早期主力\n· 全面剖析专性共生、高磷钝化与起效周期的客观瓶颈",
        "c2_type": "ring",
        "c2_val": 0.35,
        "c2_to_val": 0.92,
    },
    {
        "id": "scene_02",
        "title": "第一维度对比 · 作用位点与安全性",
        "category": "优势对比 01 · 毛霉菌剂 vs 丛枝菌根",
        "startUs": 10000000,
        "endUs": 25400000,
        "c1_badge": "早期毛霉菌剂",
        "c1_title": "多用于土壤表面有机质分解",
        "c1_text": "· 作用位点局限于表层物料腐殖转化\n· 过量繁殖易导致根系微环境失衡甚至烧根\n· 无法直接与植物根细胞建立共生通道",
        "c1_type": "bar",
        "c1_val": 0.35,
        "c1_to_val": 0.35,
        "c2_badge": "丛枝菌根优势",
        "c2_title": "直达根系共生 · 安全促生更直接",
        "c2_text": "· 直接定植根系皮层，形成泡囊与丛枝吸收体\n· 养分吸收与促生增产途径极短、效果更直接\n· 不破坏根际微生态，生物安全性更高",
        "c2_type": "ring",
        "c2_val": 0.50,
        "c2_to_val": 0.96,
    },
    {
        "id": "scene_03",
        "title": "第二维度对比 · 代谢产物安全性",
        "category": "优势对比 02 · 曲霉菌剂 vs 丛枝菌根",
        "startUs": 25400000,
        "endUs": 40450000,
        "c1_badge": "早期曲霉菌剂",
        "c1_title": "腐熟有机物料 · 存潜在代谢风险",
        "c1_text": "· 擅长堆肥腐熟与大分子有机质降解\n· 部分曲霉在产孢与繁殖期可能产生微量有害代谢物\n· 对作物幼苗和作业人员存在潜在安全隐患",
        "c1_type": "bar",
        "c1_val": 0.40,
        "c1_to_val": 0.40,
        "c2_badge": "丛枝菌根优势",
        "c2_title": "专性互惠共生 · 零有害代谢物",
        "c2_text": "· 作为专性内生共生真菌，与寄主生命休戚与共\n· 绝不产生对作物或人体有害的代谢分泌物\n· 绿色有机食品生产首选，使用安全性更优",
        "c2_type": "ring",
        "c2_val": 0.60,
        "c2_to_val": 0.99,
    },
    {
        "id": "scene_04",
        "title": "第三维度对比 · 作用周期与土壤长效",
        "category": "优势对比 03 · 酵母菌剂 vs 丛枝菌根",
        "startUs": 40450000,
        "endUs": 54500000,
        "c1_badge": "早期酵母菌剂",
        "c1_title": "改善微环境 · 促生周期偏短",
        "c1_text": "· 主要依靠自身发酵代谢物短暂刺激根际\n· 在复杂土壤生境中存活定植难度大\n· 促生效应呈脉冲式衰退，需反复频繁补充",
        "c1_type": "bar",
        "c1_val": 0.28,
        "c1_to_val": 0.28,
        "c2_badge": "丛枝菌根优势",
        "c2_title": "长期共生共荣 · 持续改良土壤",
        "c2_text": "· 与植物全生长周期保持紧密长久共生\n· 菌丝分泌球囊霉素，胶结土壤形成稳定团粒结构\n· 持效期可跨越生长季，土壤改良与保肥效果显著",
        "c2_type": "bar",
        "c2_val": 0.30,
        "c2_to_val": 0.90,
    },
    {
        "id": "scene_05",
        "title": "生态广适与环境友好壁垒",
        "category": "综合生态优势 · 跨物种共生与土著低风险",
        "startUs": 54500000,
        "endUs": 81600000,
        "c1_badge": "广谱共生适配",
        "c1_title": "多数农作物无宿主特异性障碍",
        "c1_text": "· 覆盖粮食、蔬菜、果树等 80% 以上大田作物\n· 不会出现宿主特异性过强只能适配单一作物的困境\n· 推广普及门槛低，大面积农田适配性更宽",
        "c1_type": "ring",
        "c1_val": 0.40,
        "c1_to_val": 0.85,
    },
    {
        "id": "scene_06",
        "title": "应用局限一 · 专性共生生产瓶颈",
        "category": "客观认知 01 · 工业化离体培养难题",
        "startUs": 81600000,
        "endUs": 99100000,
        "c1_badge": "专性共生壁垒",
        "c1_title": "无法实现完全人工离体纯培养",
        "c1_text": "· 必须依赖宿主活体根系才能完成生命繁育循环\n· 无法像普通细菌或腐生菌一样用液体发酵罐快速扩产\n· 研发与规模化发酵门槛高，技术突破难度大",
        "c1_type": "bar",
        "c1_val": 0.05,
        "c1_to_val": 0.05,
        "c2_badge": "成本受限挑战",
        "c2_title": "依赖植物根系扩培 · 成本偏高",
        "c2_text": "· 依赖宿主植物盆栽或水培系统扩培孢子\n· 生产周期长、占地面积大、用工密集\n· 单位有效菌剂综合制造成本显著高于腐生菌剂",
        "c2_type": "ring",
        "c2_val": 0.50,
        "c2_to_val": 0.80,
    },
    {
        "id": "scene_07",
        "title": "应用局限二 · 环境受限与高磷钝化",
        "category": "客观认知 02 · 高肥土壤下的共生抑制",
        "startUs": 99100000,
        "endUs": 112000000,
        "c1_badge": "高肥抑制机制",
        "c1_title": "高肥高磷土壤促生功能弱化",
        "c1_text": "· 土壤有效磷过剩时，作物根系自给充足无需外援\n· 作物主动减少向共生真菌输送碳水化合物能量\n· 菌根共生侵染率大幅下降，促生增产效果不稳定",
        "c1_type": "ring",
        "c1_val": 0.80,
        "c1_to_val": 0.25,
        "c2_badge": "施用场景法则",
        "c2_title": "针对性选地施用 · 切忌盲目投入",
        "c2_text": "· 中低肥力、缺磷或退化板结土壤促生最为惊艳\n· 在高度过量化肥的温室大棚容易出现效果不显\n· 科学施肥应根据土壤测土配方精准协同",
        "c2_type": "bar",
        "c2_val": 0.30,
        "c2_to_val": 0.85,
    },
    {
        "id": "scene_08",
        "title": "应用局限三 · 菌株匹配要求高",
        "category": "客观认知 03 · 缺乏区域针对性驯化",
        "startUs": 112000000,
        "endUs": 125900000,
        "c1_badge": "生境特异分化",
        "c1_title": "不同菌株对作物与土壤差异悬殊",
        "c1_text": "· 菌株耐盐碱、耐旱耐低温等抗逆特性千差万别\n· 南方酸性红壤与北方干旱盐碱地需专属优势菌种\n· 缺乏针对性匹配时容易导致田间药效大打折扣",
        "c1_type": "bar",
        "c1_val": 0.35,
        "c1_to_val": 0.35,
        "c2_badge": "早期生产短板",
        "c2_title": "通用菌株未作区域驯化适配",
        "c2_text": "· 早期菌剂普遍采用单一或少数通用商业化菌株\n· 缺乏针对特定区域生态与主栽作物品种的深度驯化\n· 导致部分农业主产区实际田间反馈起伏较大",
        "c2_type": "ring",
        "c2_val": 0.20,
        "c2_to_val": 0.20,
    },
    {
        "id": "scene_09",
        "title": "应用局限四 · 菌丝网络构建较慢",
        "category": "客观认知 04 · 慢工出细活的生物网络",
        "startUs": 125900000,
        "endUs": 137450000,
        "c1_badge": "定植建立周期",
        "c1_title": "孢子萌发侵染与菌丝成网需数周",
        "c1_text": "· 孢子识别根系分泌物并萌发侵入根表需要窗口期\n· 建立稠密的外延菌丝吸收网络一般需数周时间显效\n· 幼苗定植初期外观上难以立即观察到剧烈长势变化",
        "c1_type": "bar",
        "c1_val": 0.20,
        "c1_to_val": 0.20,
        "c2_badge": "长效滋养定位",
        "c2_title": "与速效化肥差异大 · 强调前置施用",
        "c2_text": "· 无法像速效化肥或激素一样在数天内产生立竿见影表象\n· 更适宜在播种拌种、穴施或育苗基质期前置接种\n· 建立长久护航壁垒，实现中后期持续爆发增产",
        "c2_type": "ring",
        "c2_val": 0.40,
        "c2_to_val": 0.92,
    },
    {
        "id": "scene_10",
        "title": "客观认知与农业实践探讨",
        "category": "总结收束 · 科学认识生物菌剂",
        "startUs": 137450000,
        "endUs": DURATION_US,
        "c1_badge": "核心要点总结",
        "c1_title": "扬长避短：发挥菌根真菌最大威力",
        "c1_text": "· 优势：直接促生、纯净安全、长效护土、生态友好\n· 局限：扩培成本高、高磷易钝化、重匹配、起效慢",
        "c1_type": "ring",
        "c1_val": 0.50,
        "c1_to_val": 0.95,
        "c2_badge": "互动探讨",
        "c2_title": "您在种植中用过菌根真菌吗？",
        "c2_text": "· 您还了解丛枝菌根的哪些特质与应用经验？\n· 欢迎在评论区分享交流，共同探讨绿色农业黑科技！",
        "c2_type": "bar",
        "c2_val": 0.50,
        "c2_to_val": 1.0,
    }
]

# 组装符合规范的 scene.json
scenes = []
for s_idx, item in enumerate(scenes_data):
    sid = item["id"]
    nodes = []

    # 1. 顶部 Header Card (x=100, y=210, width=880, height=130)
    nodes.append({
        "id": f"{sid}_h_bg",
        "type": "rect",
        "x": 100,
        "y": 210,
        "width": 880,
        "height": 130,
        "radius": 20,
        "background": BG_HEADER,
        "color": BORDER_HEADER,
        "enterUs": 0,
        "enterDurationUs": 300000
    })
    nodes.append({
        "id": f"{sid}_h_tag",
        "type": "text",
        "x": 130,
        "y": 228,
        "width": 820,
        "height": 38,
        "size": 24,
        "bold": False,
        "color": TAG_COLOR,
        "text": item["category"],
        "enterUs": 50000,
        "enterDurationUs": 300000
    })
    nodes.append({
        "id": f"{sid}_h_title",
        "type": "text",
        "x": 130,
        "y": 268,
        "width": 820,
        "height": 56,
        "size": 36,
        "bold": True,
        "color": TITLE_COLOR,
        "text": item["title"],
        "enterUs": 100000,
        "enterDurationUs": 300000
    })

    # 检查是否有 Card 2（Scene 5 为两栏生态合并卡或双卡）
    has_card2 = "c2_title" in item

    if has_card2:
        # Card 1 (Upper Stack, y=365, height=500)
        c1_y = 365
        c1_h = 500
        nodes.append({
            "id": f"{sid}_c1_bg",
            "type": "rect",
            "x": 100,
            "y": c1_y,
            "width": 880,
            "height": c1_h,
            "radius": 24,
            "background": CARD1_BG,
            "color": CARD1_BORDER,
            "enterUs": 150000,
            "enterDurationUs": 400000
        })
        # Badge
        nodes.append({
            "id": f"{sid}_c1_badge_bg",
            "type": "rect",
            "x": 130,
            "y": c1_y + 30,
            "width": 200,
            "height": 44,
            "radius": 12,
            "background": CARD1_BADGE_BG,
            "color": CARD1_BADGE_COLOR,
            "enterUs": 200000,
            "enterDurationUs": 300000
        })
        nodes.append({
            "id": f"{sid}_c1_badge_txt",
            "type": "text",
            "x": 145,
            "y": c1_y + 36,
            "width": 170,
            "height": 34,
            "size": 22,
            "bold": True,
            "color": CARD1_BADGE_COLOR,
            "text": item["c1_badge"],
            "enterUs": 200000,
            "enterDurationUs": 300000
        })
        # Title
        nodes.append({
            "id": f"{sid}_c1_title",
            "type": "text",
            "x": 130,
            "y": c1_y + 90,
            "width": 820,
            "height": 56,
            "size": 34,
            "bold": True,
            "color": CARD1_TITLE_COLOR,
            "text": item["c1_title"],
            "enterUs": 250000,
            "enterDurationUs": 350000
        })
        # Text
        nodes.append({
            "id": f"{sid}_c1_desc",
            "type": "text",
            "x": 130,
            "y": c1_y + 155,
            "width": 820,
            "height": 200,
            "size": 28,
            "bold": False,
            "color": CARD1_TEXT_COLOR,
            "text": item["c1_text"],
            "enterUs": 300000,
            "enterDurationUs": 400000
        })
        # Chart in Card 1
        if item["c1_type"] == "bar":
            nodes.append({
                "id": f"{sid}_c1_chart",
                "type": "bar",
                "x": 130,
                "y": c1_y + 400,
                "width": 820,
                "height": 36,
                "background": "#1e293b",
                "color": "#38bdf8",
                "value": item["c1_val"],
                "toValue": item["c1_to_val"],
                "valueDurationUs": 800000,
                "enterUs": 400000,
                "enterDurationUs": 400000
            })
        else:
            nodes.append({
                "id": f"{sid}_c1_chart",
                "type": "ring",
                "x": 770,
                "y": c1_y + 350,
                "width": 110,
                "height": 110,
                "background": "#1e293b",
                "color": "#38bdf8",
                "value": item["c1_val"],
                "toValue": item["c1_to_val"],
                "valueDurationUs": 800000,
                "enterUs": 400000,
                "enterDurationUs": 400000
            })

        # Card 2 (Lower Stack, y=895, height=530)
        c2_y = 895
        c2_h = 530
        nodes.append({
            "id": f"{sid}_c2_bg",
            "type": "rect",
            "x": 100,
            "y": c2_y,
            "width": 880,
            "height": c2_h,
            "radius": 24,
            "background": CARD2_BG,
            "color": CARD2_BORDER,
            "enterUs": 500000,
            "enterDurationUs": 450000,
            "pulse": True
        })
        # Badge
        nodes.append({
            "id": f"{sid}_c2_badge_bg",
            "type": "rect",
            "x": 130,
            "y": c2_y + 30,
            "width": 200,
            "height": 44,
            "radius": 12,
            "background": CARD2_BADGE_BG,
            "color": CARD2_BADGE_COLOR,
            "enterUs": 550000,
            "enterDurationUs": 300000
        })
        nodes.append({
            "id": f"{sid}_c2_badge_txt",
            "type": "text",
            "x": 145,
            "y": c2_y + 36,
            "width": 170,
            "height": 34,
            "size": 22,
            "bold": True,
            "color": "#ffffff",
            "text": item["c2_badge"],
            "enterUs": 550000,
            "enterDurationUs": 300000
        })
        # Title
        nodes.append({
            "id": f"{sid}_c2_title",
            "type": "text",
            "x": 130,
            "y": c2_y + 90,
            "width": 820,
            "height": 56,
            "size": 34,
            "bold": True,
            "color": CARD2_TITLE_COLOR,
            "text": item["c2_title"],
            "enterUs": 600000,
            "enterDurationUs": 350000
        })
        # Text
        nodes.append({
            "id": f"{sid}_c2_desc",
            "type": "text",
            "x": 130,
            "y": c2_y + 155,
            "width": 820,
            "height": 220,
            "size": 28,
            "bold": False,
            "color": CARD2_TEXT_COLOR,
            "text": item["c2_text"],
            "enterUs": 650000,
            "enterDurationUs": 400000
        })
        # Chart in Card 2
        if item["c2_type"] == "bar":
            nodes.append({
                "id": f"{sid}_c2_chart",
                "type": "bar",
                "x": 130,
                "y": c2_y + 420,
                "width": 820,
                "height": 36,
                "background": "#064e3b",
                "color": "#34d399",
                "value": item["c2_val"],
                "toValue": item["c2_to_val"],
                "valueDurationUs": 900000,
                "enterUs": 700000,
                "enterDurationUs": 400000
            })
        else:
            nodes.append({
                "id": f"{sid}_c2_chart",
                "type": "ring",
                "x": 770,
                "y": c2_y + 370,
                "width": 110,
                "height": 110,
                "background": "#064e3b",
                "color": "#34d399",
                "value": item["c2_val"],
                "toValue": item["c2_to_val"],
                "valueDurationUs": 900000,
                "enterUs": 700000,
                "enterDurationUs": 400000
            })
    else:
        # Single Tall Showcase Card (for Scene 5: 生态广适与土著安全)
        c_y = 365
        c_h = 1060
        nodes.append({
            "id": f"{sid}_c_bg",
            "type": "rect",
            "x": 100,
            "y": c_y,
            "width": 880,
            "height": c_h,
            "radius": 24,
            "background": CARD2_BG,
            "color": CARD2_BORDER,
            "enterUs": 150000,
            "enterDurationUs": 400000,
            "pulse": True
        })
        # Part 1 Badge & Title
        nodes.append({
            "id": f"{sid}_c_b1_bg",
            "type": "rect",
            "x": 130,
            "y": c_y + 35,
            "width": 220,
            "height": 44,
            "radius": 12,
            "background": CARD2_BADGE_BG,
            "color": CARD2_BADGE_COLOR,
            "enterUs": 200000,
            "enterDurationUs": 300000
        })
        nodes.append({
            "id": f"{sid}_c_b1_txt",
            "type": "text",
            "x": 145,
            "y": c_y + 41,
            "width": 190,
            "height": 34,
            "size": 22,
            "bold": True,
            "color": "#ffffff",
            "text": "广适性壁垒",
            "enterUs": 200000,
            "enterDurationUs": 300000
        })
        nodes.append({
            "id": f"{sid}_c_t1",
            "type": "text",
            "x": 130,
            "y": c_y + 95,
            "width": 820,
            "height": 56,
            "size": 34,
            "bold": True,
            "color": CARD2_TITLE_COLOR,
            "text": "多数农作物无宿主特异性障碍",
            "enterUs": 250000,
            "enterDurationUs": 350000
        })
        nodes.append({
            "id": f"{sid}_c_d1",
            "type": "text",
            "x": 130,
            "y": c_y + 160,
            "width": 820,
            "height": 180,
            "size": 28,
            "bold": False,
            "color": CARD2_TEXT_COLOR,
            "text": "· 覆盖粮食、蔬菜、果树等 80% 以上大田作物\n· 不会出现宿主特异性过强只能适配少数作物的问题\n· 推广普及范围宽广，跨农田品种适应性极佳",
            "enterUs": 300000,
            "enterDurationUs": 400000
        })
        nodes.append({
            "id": f"{sid}_c_chart1",
            "type": "bar",
            "x": 130,
            "y": c_y + 370,
            "width": 820,
            "height": 36,
            "background": "#064e3b",
            "color": "#34d399",
            "value": 0.40,
            "toValue": 0.85,
            "valueDurationUs": 800000,
            "enterUs": 350000,
            "enterDurationUs": 400000
        })

        # Part 2 Badge & Title
        nodes.append({
            "id": f"{sid}_c_b2_bg",
            "type": "rect",
            "x": 130,
            "y": c_y + 460,
            "width": 220,
            "height": 44,
            "radius": 12,
            "background": "#075985",
            "color": "#38bdf8",
            "enterUs": 500000,
            "enterDurationUs": 300000
        })
        nodes.append({
            "id": f"{sid}_c_b2_txt",
            "type": "text",
            "x": 145,
            "y": c_y + 466,
            "width": 190,
            "height": 34,
            "size": 22,
            "bold": True,
            "color": "#ffffff",
            "text": "原生土著安全",
            "enterUs": 500000,
            "enterDurationUs": 300000
        })
        nodes.append({
            "id": f"{sid}_c_t2",
            "type": "text",
            "x": 130,
            "y": c_y + 520,
            "width": 820,
            "height": 56,
            "size": 34,
            "bold": True,
            "color": "#7dd3fc",
            "text": "本底土著真菌 · 零生态入侵风险",
            "enterUs": 550000,
            "enterDurationUs": 350000
        })
        nodes.append({
            "id": f"{sid}_c_d2",
            "type": "text",
            "x": 130,
            "y": c_y + 585,
            "width": 820,
            "height": 220,
            "size": 28,
            "bold": False,
            "color": CARD2_TEXT_COLOR,
            "text": "· 土壤原本天然存在的土著真菌，生命基石之一\n· 接种施用后绝不破坏和改变原有土壤生态基本结构\n· 外来物种入侵风险远低于外源引入的人工真菌品种\n· 对原生自然生态环境的冲击影响极小",
            "enterUs": 600000,
            "enterDurationUs": 400000
        })
        nodes.append({
            "id": f"{sid}_c_chart2",
            "type": "ring",
            "x": 750,
            "y": c_y + 860,
            "width": 140,
            "height": 140,
            "background": "#075985",
            "color": "#38bdf8",
            "value": 0.30,
            "toValue": 0.98,
            "valueDurationUs": 900000,
            "enterUs": 650000,
            "enterDurationUs": 400000
        })

    scenes.append({
        "id": sid,
        "startUs": item["startUs"],
        "endUs": item["endUs"],
        "nodes": nodes
    })

scene_project = {
    "background": {
        "color": "#061318",
        "particles": True,
        "seed": 20261026
    },
    "subtitleSize": 44,
    "scenes": scenes
}

temp_scene_file = ROOT_DIR / "temp" / "scene_n0007.json"
temp_scene_file.write_text(json.dumps(scene_project, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"✅ 已生成 scene.json: {temp_scene_file}")

# 组装 sfx.json
# scene 切换触发 whoosh；重点卡片入场触发 pop / ding；结尾 CTA 触发 chime
sfx_data = {
    "whoosh": [
        round(s["startUs"] / 1e6, 2) for s in scenes_data if s["startUs"] > 0
    ],
    "ding": [
        1.5, 15.5, 34.3, 49.1, 69.1, 87.4, 100.6, 119.2, 127.5
    ],
    "pop": [
        0.8, 11.2, 26.5, 41.5, 56.0, 83.0, 101.0, 113.5, 127.0
    ],
    "chime": [
        138.0
    ],
    "click": []
}

temp_sfx_file = ROOT_DIR / "temp" / "sfx_n0007.json"
temp_sfx_file.write_text(json.dumps(sfx_data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"✅ 已生成 sfx.json: {temp_sfx_file}")

# 调用 vibe fast-build
if OUT_PROJECT.exists():
    import shutil
    shutil.rmtree(OUT_PROJECT)
    print(f"清理已存在的旧目标目录: {OUT_PROJECT}")

cmd = [
    sys.executable,
    str(ROOT_DIR / "vibe.py"),
    "fast-build",
    "--scene", str(temp_scene_file),
    "--voice", str(VOICE_WAV),
    "--timestamps", str(TIMESTAMPS_JSON),
    "--sfx", str(temp_sfx_file),
    "--title", "N0007_丛枝菌根菌剂对比",
    "--out", str(OUT_PROJECT)
]

print("正在执行 fast-build...")
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
if res.returncode != 0:
    print("❌ fast-build 失败:")
    print(res.stderr)
    sys.exit(res.returncode)

print("🎉 fast-build 成功完成！")

# 再次执行 pack 进行最终安全校验
print("正在执行 pack 校验...")
pack_cmd = [
    sys.executable,
    str(ROOT_DIR / "vibe.py"),
    "pack",
    str(OUT_PROJECT)
]
res_pack = subprocess.run(pack_cmd, capture_output=True, text=True)
print(res_pack.stdout)
if res_pack.returncode != 0:
    print("❌ pack 校验失败:")
    print(res_pack.stderr)
    sys.exit(res_pack.returncode)

print("🚀 全部检查通过！工程已完全就绪！")
