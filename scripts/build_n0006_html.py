# -*- coding: utf-8 -*-
"""
生成 N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点.html
"""
import json
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

INPUT_DIR = "inputs/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点"
OUTPUT_DIR = "output/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点"
OUTPUT_HTML = os.path.join(OUTPUT_DIR, "N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点.html")

# 读取时间戳
with open(os.path.join(INPUT_DIR, "char_timestamps.json"), "r", encoding="utf-8") as f:
    timestamps = json.load(f)

# 24 场景时间戳定义
SCENES_DEF = [
    ("s-open", 0.00, "开篇导入 · 双引擎主题"),
    ("s-fzb42-intro", 11.92, "国际经典 · 元老 FZB42"),
    ("s-fzb42-factory", 26.50, "FZB42 · 次级代谢工厂"),
    ("s-fzb42-market", 39.91, "FZB42 · 欧美田间应用"),
    ("s-gb03-origin", 48.70, "国际经典 · 科迪亚克老兵"),
    ("s-gb03-mech", 59.26, "GB03 · 挥发物促生机理"),
    ("s-qst713-intro", 74.07, "国际经典 · 拜耳杀菌先锋"),
    ("s-qst713-crops", 87.31, "QST713 · 欧美有机农业标杆"),
    ("s-9912d-intro", 99.66, "国内早期 · 9912D杀菌剂"),
    ("s-9912d-crops", 111.66, "9912D · 四大典型病害防效"),
    ("s-rti301", 120.86, "国际前沿 · 欧盟新晋低风险"),
    ("s-cn-overview", 131.00, "中国力量 · 商业化多强进发"),
    ("s-14384", 139.92, "国内首登 · 14384双专利"),
    ("s-m173", 153.01, "青枯克星 · M173悬浮剂"),
    ("s-c17271", 163.26, "赤霉先锋 · C17271填补空白"),
    ("s-nbi6002", 173.54, "首创杀线虫 · NBI6002在华获批"),
    ("s-lmw2", 184.16, "全球首创杀螨 · LMW2红蜘蛛"),
    ("s-bj1", 195.19, "新有效成分 · BJ-1双重增效"),
    ("s-patent-overview", 207.59, "专利新势力 · 39314持续进化"),
    ("s-l271-sy01", 222.58, "高校双骄 · L271与SY01"),
    ("s-hn2-rjw55", 235.25, "橡胶炭疽HN2 & 盐湖RJW5-5"),
    ("s-rjw55-g1", 245.93, "新疆棉区卫士 & G-1跃升2.3倍"),
    ("s-wenjiang", 258.94, "量身定制 · 温江大蒜土著菌"),
    ("s-outro", 271.57, "全片收官 · 下期精彩预告"),
]

OPEN_PHASES_DEF = [
    ("splash", 0.00),
    ("topic", 5.72),
]

# SVG 图标库
ICONS = {
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "dna": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 15c6.667-6 13.333 0 20-6"/><path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993"/><path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993"/><path d="M17 6l-2.5-2.5"/><path d="M14 8l-1-1"/><path d="M7 18l2.5 2.5"/><path d="M3.5 14.5l.5.5"/><path d="M20 9.5l.5.5"/><path d="M6.5 12.5l1 1"/><path d="M16.5 10.5l1 1"/><path d="M10 16l-1-1"/></svg>',
    "award": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>',
    "flask": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><line x1="8.5" y1="2" x2="15.5" y2="2"/><path d="M8.5 14h7"/></svg>',
    "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "sprout": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4.1 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "zap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "target": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "leaf": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>',
    "trending": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
}

def make_card(icon_key, title, desc, delay_class="w3"):
    ico = ICONS.get(icon_key, ICONS["shield"])
    return f"""
      <div class="card-item w {delay_class}">
        <div class="card-ico">{ico}</div>
        <div class="card-body">
          <div class="card-t">{title}</div>
          <div class="card-d">{desc}</div>
        </div>
      </div>
    """

def make_ring(val_str, label, stroke_pct=85, grad="greenGrad"):
    offset = round(251.2 * (1 - stroke_pct / 100.0), 1)
    return f"""
      <div class="ring-decoupled w w2">
        <div class="ring-graphic">
          <svg viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(148,163,184,0.15)" stroke-width="8"/>
            <circle cx="50" cy="50" r="40" fill="none" stroke="url(#{grad})" stroke-width="8" stroke-dasharray="251.2" stroke-dashoffset="{offset}" stroke-linecap="round"/>
          </svg>
          <div class="ring-center-val breathe">{val_str}</div>
        </div>
        <div class="ring-desc">
          <div class="badge green">{label}</div>
        </div>
      </div>
    """

scenes_html = []

# S01: 开篇导入与双引擎主题
scenes_html.append(f"""
  <!-- S01: 开篇导入与双引擎主题 -->
  <div id="s-open" class="scene active" data-phase="splash">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:10%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.15),transparent 65%)"></div>
    </div>
    <div class="phs phs-splash">
      <div class="badge">上期回顾 · 进化脉络</div>
      <div class="hook-graphic breathe">
        {ICONS['dna']}
      </div>
      <div class="hook-title">人工驯化与<em>基因改造</em></div>
      <div class="sub">历经定向选育与驯化，从实验室迈向大田实战</div>
    </div>
    <div class="phs phs-topic">
      <div class="badge">本期重磅盘点</div>
      <div class="tp-title breathe">贝莱斯芽孢杆菌</div>
      <div class="card-stack" style="margin-top:2cqw;">
        <div class="card-item" style="border-color:rgba(74,222,128,0.35);">
          <div class="card-ico" style="color:var(--green);">{ICONS['globe']}</div>
          <div class="card-body">
            <div class="card-t">国外经典明星菌株</div>
            <div class="card-d">科研模式标杆与国际商业化先锋</div>
          </div>
        </div>
        <div class="card-item" style="border-color:rgba(56,189,248,0.35);">
          <div class="card-ico" style="color:var(--cyan);">{ICONS['target']}</div>
          <div class="card-body">
            <div class="card-t">中国商业化新势力</div>
            <div class="card-d">农药登记多强进发与自主研发前沿</div>
          </div>
        </div>
      </div>
    </div>
  </div>
""")

# S02: 国际经典 · 元老 FZB42
scenes_html.append(f"""
  <!-- S02: 国际经典 · 元老 FZB42 -->
  <div id="s-fzb42-intro" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge w">国际经典代表 · 01</div>
      <h2 class="w w2">生防菌元老 · FZB42</h2>
      <div class="card-stack">
        {make_card("flask", "德国 ABiTEP 公司研发", "2007年完成全基因组测序，奠定生防基因组研究基础", "w3")}
        {make_card("award", "世界公认模式菌株", "DSM 23117，全球开展机理探索与代谢分析的绝对基准", "w4")}
      </div>
    </div>
  </div>
""")

# S03: FZB42 · 次级代谢工厂
scenes_html.append(f"""
  <!-- S03: FZB42 · 次级代谢工厂 -->
  <div id="s-fzb42-factory" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:12%;transform:translateX(-50%);background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge w">次级代谢产物合成工厂</div>
      <h2 class="w w2">FZB42 抗菌物质矩阵</h2>
      {make_ring("13个", "次级代谢产物合成基因簇", 82, "greenGrad")}
      <div class="card-stack" style="margin-top:1.6cqw;">
        {make_card("shield", "合成多种广谱抗菌物质", "表面活性剂、芽孢霉素D、杆菌烯大环内酯协同拮抗", "w3")}
      </div>
    </div>
  </div>
""")

# S04: FZB42 · 欧美田间应用
scenes_html.append(f"""
  <!-- S04: FZB42 · 欧美田间应用 -->
  <div id="s-fzb42-market" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge w">商业落地与田间实效</div>
      <h2 class="w w2">商品名：Resveratrol</h2>
      <div class="card-stack">
        {make_card("sprout", "欧美大田与经济作物", "广泛用于玉米、蔬菜、马铃薯等作物的促生防病", "w3")}
        {make_card("star", "产业研究最深入代表", "全球商业化时间长、实战机理与安全数据最完备", "w4")}
      </div>
    </div>
  </div>
""")

# S05: 国际经典 · 科迪亚克老兵
scenes_html.append(f"""
  <!-- S05: 国际经典 · 科迪亚克老兵 -->
  <div id="s-gb03-origin" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(251,191,36,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge amber w">国际经典代表 · 02</div>
      <h2 class="w w2">科迪亚克老兵 · GB03</h2>
      <div class="card-stack">
        {make_card("leaf", "1971年澳大利亚麦田分离", "深根际原生态优质菌株，历经半个多世纪验证", "w3")}
        {make_card("target", "拜耳商业化开发", "商品名 Codiak（科迪亚克），享誉全球的经典品牌", "w4")}
      </div>
    </div>
  </div>
""")

# S06: GB03 · 挥发物促生机理
scenes_html.append(f"""
  <!-- S06: GB03 · 挥发物促生机理 -->
  <div id="s-gb03-mech" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:12%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge w">细菌挥发物调控模式</div>
      <h2 class="w w2">GB03 挥发促生先驱</h2>
      {make_ring("30+年", "全球商业化应用历史", 90, "greenGrad")}
      <div class="card-stack" style="margin-top:1.6cqw;">
        {make_card("zap", "高效挥发物促生机理", "释放 2,3-丁二醇等挥发物，全球最早芽孢种子处理剂", "w3")}
      </div>
    </div>
  </div>
""")

# S07: 国际经典 · 拜耳杀菌先锋 QST713
scenes_html.append(f"""
  <!-- S07: 国际经典 · 拜耳杀菌先锋 QST713 -->
  <div id="s-qst713-intro" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge w">国际经典代表 · 03</div>
      <h2 class="w w2">经典杀菌剂 · QST713</h2>
      <div class="card-stack">
        {make_card("shield", "Agracetus 研发 · 拜耳收购", "商品名 Serenade（赛利达田园卫士），全球旗舰产品", "w3")}
        {make_card("flask", "高产伊枯草菌素A等脂肽", "对多种叶面真菌和细菌病害展现卓越防效", "w4")}
      </div>
    </div>
  </div>
""")

# S08: QST713 · 欧美有机农业标杆
scenes_html.append(f"""
  <!-- S08: QST713 · 欧美有机农业标杆 -->
  <div id="s-qst713-crops" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge green w">经济作物防病标杆</div>
      <h2 class="w w2">欧美有机农业常用品种</h2>
      <div class="card-stack">
        {make_card("leaf", "经济作物三大真菌病害", "葡萄、草莓、蔬菜等：灰霉病、白粉病、霜霉病克星", "w3")}
        {make_card("award", "国际有机认证常青树", "低毒、无抗药性风险，欧美绿色农产品核心用药", "w4")}
      </div>
    </div>
  </div>
""")

# S09: 国内早期 · 9912D杀菌剂
scenes_html.append(f"""
  <!-- S09: 国内早期 · 9912D杀菌剂 -->
  <div id="s-9912d-intro" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(251,191,36,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge amber w">国际经典代表 · 04</div>
      <h2 class="w w2">国内早期先锋 · 9912D</h2>
      <div class="card-stack">
        {make_card("award", "国内科研单位自主分离", "2016年获农业部登记为新型生物杀菌剂", "w3")}
        {make_card("flask", "产生丰富抗菌脂肽", "强效抑制病原菌孢子萌发与菌丝生长", "w4")}
      </div>
    </div>
  </div>
""")

# S10: 9912D · 四大典型病害防效
scenes_html.append(f"""
  <!-- S10: 9912D · 四大典型病害防效 -->
  <div id="s-9912d-crops" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge w">大田实战检验</div>
      <h2 class="w w2">四大典型病害防效显著</h2>
      <div class="card-stack">
        {make_card("shield", "多作物病害广谱防控", "黄瓜番茄灰霉病、棉花枯萎病、苹果腐烂病", "w3")}
        {make_card("trending", "国内较早产业化推广", "见证中国贝莱斯芽孢杆菌自主商业化起步", "w4")}
      </div>
    </div>
  </div>
""")

# S11: 国际前沿 · 欧盟新晋低风险 RTI301
scenes_html.append(f"""
  <!-- S11: 国际前沿 · 欧盟新晋低风险 RTI301 -->
  <div id="s-rti301" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge cyan w">国际经典代表 · 05</div>
      <h2 class="w w2">欧盟新晋低风险 · RTI301</h2>
      <div class="card-stack">
        {make_card("award", "2025年获欧盟批准", "正式列入欧盟低风险活性物质清单（Low-Risk）", "w3")}
        {make_card("globe", "推动欧洲合规应用", "为欧洲严苛环保标准下的绿色农药提供崭新解法", "w4")}
      </div>
    </div>
  </div>
""")

# S12: 中国力量 · 商业化多强进发
scenes_html.append(f"""
  <!-- S12: 中国力量 · 商业化多强进发 -->
  <div id="s-cn-overview" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.15),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge green w">第二篇章 · 中国力量</div>
      <h2 class="w w2">中国已登记商业化新势力</h2>
      <div class="card-stack">
        {make_card("trending", "截至2026年格局大成", "中国贝莱斯芽孢杆菌农药登记已形成多强进发格局", "w3")}
        {make_card("target", "细分靶标与剂型创新", "杀菌、杀线虫、杀螨全方位突破，领跑生物农业", "w4")}
      </div>
    </div>
  </div>
""")

# S13: 国内首登 · 14384双专利
scenes_html.append(f"""
  <!-- S13: 国内首登 · 14384双专利 -->
  <div id="s-14384" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge w">中国商业化新势力 · 01</div>
      <h2 class="w w2">国内首登纪录 · 14384</h2>
      <div class="card-stack">
        {make_card("award", "四川百士东旺 · 西安展鹏", "国内首个贝莱斯芽孢杆菌农药正式登记", "w3")}
        {make_card("shield", "2021年9月中美双专利", "母药 + 可湿性粉剂 + 复合制剂，产品线最全", "w4")}
      </div>
    </div>
  </div>
""")

# S14: 青枯克星 · M173悬浮剂
scenes_html.append(f"""
  <!-- S14: 青枯克星 · M173悬浮剂 -->
  <div id="s-m173" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge cyan w">中国商业化新势力 · 02</div>
      <h2 class="w w2">番茄青枯病首登 · M173</h2>
      <div class="card-stack">
        {make_card("target", "湖南沐恩生物创制", "国内首个登记防治番茄青枯病，获美国发明专利", "w3")}
        {make_card("flask", "先进悬浮剂（SC）剂型", "对葡萄灰霉病防效突出，兼顾悬浮稳定性与附着力", "w4")}
      </div>
    </div>
  </div>
""")

# S15: 赤霉先锋 · C17271填补空白
scenes_html.append(f"""
  <!-- S15: 赤霉先锋 · C17271填补空白 -->
  <div id="s-c17271" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(251,191,36,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge amber w">中国商业化新势力 · 03</div>
      <h2 class="w w2">小麦赤霉病先锋 · C17271</h2>
      <div class="card-stack">
        {make_card("sprout", "浙江赛瑞可 · 泛亚生物", "国内首个登记防治小麦赤霉病，填补防控空白", "w3")}
        {make_card("zap", "5亿 CFU/g 可湿性粉剂", "保障口粮主产区绿色丰产，降低真菌毒素风险", "w4")}
      </div>
    </div>
  </div>
""")

# S16: 首创杀线虫 · NBI6002在华获批
scenes_html.append(f"""
  <!-- S16: 首创杀线虫 · NBI6002在华获批 -->
  <div id="s-nbi6002" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge green w">中国商业化新势力 · 04</div>
      <h2 class="w w2">首创杀线虫登记 · NBI6002</h2>
      <div class="card-stack">
        {make_card("globe", "澳大利亚纽发姆 · 巴斯夫", "2025年在华获批，首创细菌杀线虫剂登记", "w3")}
        {make_card("shield", "土传根结线虫克星", "强效穿透线虫卵壳，从根源压制土壤隐蔽线虫虫害", "w4")}
      </div>
    </div>
  </div>
""")

# S17: 全球首创杀螨 · LMW2红蜘蛛
scenes_html.append(f"""
  <!-- S17: 全球首创杀螨 · LMW2红蜘蛛 -->
  <div id="s-lmw2" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:12%;transform:translateX(-50%);background:radial-gradient(circle,rgba(248,113,113,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge red w">中国商业化新势力 · 05</div>
      <h2 class="w w2">全球首创细菌杀螨剂 · LMW2</h2>
      {make_ring("500亿", "每克超高含菌量母药", 92, "greenGrad")}
      <div class="card-stack" style="margin-top:1.6cqw;">
        {make_card("zap", "四川龙蟒福生 2026登记", "全球首创细菌杀螨剂，精准防治柑橘树红蜘蛛", "w3")}
      </div>
    </div>
  </div>
""")

# S18: 新有效成分 · BJ-1双重增效
scenes_html.append(f"""
  <!-- S18: 新有效成分 · BJ-1双重增效 -->
  <div id="s-bj1" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:12%;transform:translateX(-50%);background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge cyan w">中国商业化新势力 · 06</div>
      <h2 class="w w2">国家级新成分 · BJ-1</h2>
      <div class="duo-rings-decoupled w w2">
        <div class="ring-item">
          <div class="ring-graphic">
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(148,163,184,0.15)" stroke-width="8"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke="url(#greenGrad)" stroke-width="8" stroke-dasharray="251.2" stroke-dashoffset="150" stroke-linecap="round"/>
            </svg>
            <div class="ring-center-val breathe">+20%</div>
          </div>
          <div class="ring-lbl">番茄壮苗指数提高</div>
        </div>
        <div class="ring-item">
          <div class="ring-graphic">
            <svg viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(148,163,184,0.15)" stroke-width="8"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke="url(#cyanGrad)" stroke-width="8" stroke-dasharray="251.2" stroke-dashoffset="100" stroke-linecap="round"/>
            </svg>
            <div class="ring-center-val breathe">+40%</div>
          </div>
          <div class="ring-lbl">灰霉病综合防效</div>
        </div>
      </div>
      <div class="card-stack" style="margin-top:1.6cqw;">
        {make_card("award", "北京市农林科学院研发", "2025年列为7个新农药有效成分之一，水分散粒剂（WDG）", "w3")}
      </div>
    </div>
  </div>
""")

# S19: 专利新势力 · 39314持续进化
scenes_html.append(f"""
  <!-- S19: 专利新势力 · 39314持续进化 -->
  <div id="s-patent-overview" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge green w">第三篇章 · 研发前沿</div>
      <h2 class="w w2">研究与专利新势力 · 39314</h2>
      <div class="card-stack">
        {make_card("award", "远大产业控股创制", "2026年8月最新公开专利，产业端技术持续进化", "w3")}
        {make_card("shield", "更高抑菌活性 · 更宽抑菌谱", "次级代谢产物活性倍增，引领新一代生防菌剂潮流", "w4")}
      </div>
    </div>
  </div>
""")

# S20: 高校双骄 · L271与SY01
scenes_html.append(f"""
  <!-- S20: 高校双骄 · L271与SY01 -->
  <div id="s-l271-sy01" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(56,189,248,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge cyan w">高校自主研发矩阵 · 01</div>
      <h2 class="w w2">高校科研双骄 · L271 & SY01</h2>
      <div class="card-stack">
        {make_card("sprout", "山东农业大学 · L271", "从大蒜根际分离，对大蒜腐烂病展现特异防效", "w3")}
        {make_card("leaf", "塔里木大学 · SY01", "针对苹果树腐烂病，可产生三类核心高活性脂肽", "w4")}
      </div>
    </div>
  </div>
""")

# S21: 橡胶炭疽HN2 & 盐湖RJW5-5
scenes_html.append(f"""
  <!-- S21: 橡胶炭疽HN2 & 盐湖RJW5-5 -->
  <div id="s-hn2-rjw55" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(251,191,36,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge amber w">高校自主研发矩阵 · 02</div>
      <h2 class="w w2">特种环境突破 · HN-2 & RJW5-5</h2>
      <div class="card-stack">
        {make_card("shield", "海南大学 · HN-2", "热带作物攻坚：橡胶树炭疽病防控中表现优异", "w3")}
        {make_card("flask", "西大华特 · RJW5-5", "从山西运城盐湖极端环境分离筛选的专利菌株", "w4")}
      </div>
    </div>
  </div>
""")

# S22: 新疆棉区卫士 & G-1跃升2.3倍
scenes_html.append(f"""
  <!-- S22: 新疆棉区卫士 & G-1跃升2.3倍 -->
  <div id="s-rjw55-g1" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:12%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.12),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge green w">广谱防御与复合诱变</div>
      <h2 class="w w2">棉区卫士与诱变增效</h2>
      {make_ring("2.3倍", "山西农业大学 G-1 环脂肽产量跃升", 85, "greenGrad")}
      <div class="card-stack" style="margin-top:1.6cqw;">
        {make_card("shield", "RJW5-5 专为新疆棉区设计", "强力抑制棉花黄萎病、梨黑斑病等14种病原菌", "w3")}
      </div>
    </div>
  </div>
""")

# S23: 量身定制 · 温江大蒜土著菌
scenes_html.append(f"""
  <!-- S23: 量身定制 · 温江大蒜土著菌 -->
  <div id="s-wenjiang" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.15),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge green w">地理标志生态定制</div>
      <h2 class="w w2">温江大蒜土著菌株</h2>
      <div class="card-stack">
        {make_card("leaf", "成都市农林科学院刘记团队", "从温江大蒜田分离的本土菌，已获国家发明专利", "w3")}
        {make_card("award", "原产地绿色屏障", "针对温江大蒜量身定制，实现地理标志产品生态保护", "w4")}
      </div>
    </div>
  </div>
""")

# S24: 全片收官 · 下期精彩预告 CTA
scenes_html.append(f"""
  <!-- S24: 全片收官 · 下期精彩预告 CTA -->
  <div id="s-outro" class="scene">
    <div class="aura">
      <div class="glow" style="width:110cqw;height:110cqw;left:50%;top:15%;transform:translateX(-50%);background:radial-gradient(circle,rgba(74,222,128,0.2),transparent 65%)"></div>
    </div>
    <div class="inner">
      <div class="badge green w">全篇复盘总结</div>
      <h2 class="w w2">国内外优势菌株格局</h2>
      <div class="card-stack" style="margin-top:2cqw;">
        <div class="card-item w w3" style="text-align:center;justify-content:center;padding:3.6cqw 4cqw;">
          <div style="font-size:3.8cqw;font-weight:800;color:var(--green);line-height:1.6;">
            更多生物农业与前沿菌株科普<br>
            <span style="font-size:4.6cqw;color:#ffffff;display:inline-block;margin-top:1cqw;" class="breathe">我们下期见！</span>
          </div>
        </div>
      </div>
      <div class="cta-row w w4" style="display:flex;gap:2.4cqw;margin-top:3.6cqw;justify-content:center;">
        <div class="cta">点赞</div>
        <div class="cta">关注</div>
        <div class="cta">收藏</div>
        <div class="cta">转发</div>
      </div>
    </div>
  </div>
""")

all_scenes_joined = "\n".join(scenes_html)

# 自定义 CSS 强化
custom_css = """
  /* 竖屏大卡片流 (Card Stack) */
  .card-stack {
    display: flex;
    flex-direction: column;
    gap: 2.2cqw;
    width: 82cqw;
    align-items: center;
    margin-top: 1.2cqw;
  }
  .card-item {
    width: 100%;
    background: linear-gradient(145deg, rgba(16, 28, 38, 0.94), rgba(10, 18, 26, 0.94));
    border: 1px solid var(--line);
    border-radius: 3.2cqw;
    padding: 2.8cqw 3.8cqw;
    display: flex;
    align-items: center;
    gap: 3.2cqw;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
  }
  .card-ico {
    width: 6.8cqw;
    height: 6.8cqw;
    flex: none;
    color: var(--green);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .card-ico svg {
    width: 100%;
    height: 100%;
  }
  .card-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.8cqw;
    text-align: left;
  }
  .card-t {
    font-size: 3.8cqw;
    font-weight: 800;
    color: var(--green);
    letter-spacing: 0.02em;
    line-height: 1.3;
  }
  .card-d {
    font-size: 3.0cqw;
    font-weight: 500;
    color: var(--ink);
    line-height: 1.5;
    letter-spacing: 0.01em;
  }

  /* 解耦式环形数据组件（中心纯数字，图文字物理隔离） */
  .ring-decoupled {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4.5cqw;
    width: 82cqw;
    margin: 1.2cqw auto 0;
  }
  .ring-graphic {
    width: 22cqw;
    height: 22cqw;
    position: relative;
    flex: none;
  }
  .ring-graphic svg {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
  }
  .ring-center-val {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 5.2cqw;
    font-weight: 900;
    color: var(--green);
    letter-spacing: -0.02em;
  }
  .ring-desc {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 1cqw;
    text-align: left;
  }

  /* 双环解耦组件 */
  .duo-rings-decoupled {
    display: flex;
    justify-content: center;
    gap: 6cqw;
    width: 82cqw;
    margin: 1.2cqw auto 0;
  }
  .duo-rings-decoupled .ring-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.2cqw;
  }
  .duo-rings-decoupled .ring-graphic {
    width: 19cqw;
    height: 19cqw;
  }
  .duo-rings-decoupled .ring-center-val {
    font-size: 4.8cqw;
  }
  .duo-rings-decoupled .ring-lbl {
    font-size: 3.0cqw;
    font-weight: 700;
    color: var(--ink);
  }

  /* 结尾 CTA 按钮行 */
  .cta-row .cta {
    font-size: 3.2cqw;
    font-weight: 700;
    border: 1px solid var(--line);
    border-radius: 6cqw;
    padding: 1.3cqw 3.6cqw;
    background: rgba(148, 163, 184, 0.08);
    color: var(--ink);
    animation: ctaPulse 2s ease-in-out infinite;
  }
  @keyframes ctaPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.06); }
  }
"""

# 制作完整 HTML
scenes_js = json.dumps([[sc[0], sc[1]] for sc in SCENES_DEF], ensure_ascii=False)
chaps_js = json.dumps([sc[2] for sc in SCENES_DEF], ensure_ascii=False)
open_phases_js = json.dumps(OPEN_PHASES_DEF, ensure_ascii=False)
timestamps_js = json.dumps(timestamps, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><rect width='24' height='24' rx='5' fill='%23070d12'/><text x='12' y='17' font-size='13' font-weight='bold' text-anchor='middle' fill='%234ade80'>V</text></svg>">
<style>
  :root {{
    --bg: #070d12;
    --panel: #0e1a22;
    --panel-sub: rgba(16, 28, 38, 0.92);
    --line: rgba(148, 163, 184, 0.18);
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

  /* 顶部作品标题区（纯粹展示作品标题，双行语义断句，无分镜胶囊） */
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
    padding: 0.8cqw 3.6cqw 0.9cqw;
    background: rgba(10, 18, 26, 0.68);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45), 0 0 25px rgba(74, 222, 128, 0.12), inset 0 1px 1px rgba(255, 255, 255, 0.15);
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
    line-height: 1.25;
  }}
  .title-line {{
    display: block;
    background: linear-gradient(180deg, #ffffff 10%, #dcfce7 65%, #86efac 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.95)) drop-shadow(0 0 16px rgba(74, 222, 128, 0.35));
    letter-spacing: 0.04em;
    white-space: nowrap;
  }}
  .title-main {{
    font-size: 3.8cqw;
    font-weight: 900;
  }}
  .title-sub {{
    font-size: 3.0cqw;
    font-weight: 700;
    margin-top: 0.5cqw;
    background: linear-gradient(180deg, #f1f5f9 20%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.9));
  }}

  /* 分镜开发辅助标识 HUD（外移至安全区外左上角盲区） */
  #chapText {{
    position: fixed;
    top: 3.2cqh;
    left: 4cqw;
    z-index: 15;
    font-size: 2.2cqw;
    font-weight: 700;
    color: rgba(148, 163, 184, 0.65);
    background: rgba(14, 26, 36, 0.6);
    padding: 0.4cqw 1.8cqw;
    border-radius: 999px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    backdrop-filter: blur(8px);
    pointer-events: none;
  }}

  /* 中区通用容器规范 */
  .aura {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 0;
  }}
  .aura .glow {{
    position: absolute;
    border-radius: 50%;
    filter: blur(8cqw);
  }}
  .scene {{
    position: fixed;
    top: 17cqh;
    bottom: 22cqh;
    left: 8cqw;
    right: 8cqw;
    max-height: 54cqh;
    z-index: 2;
    display: none;
    opacity: 0;
    transition: opacity 0.35s ease;
  }}
  .scene.active {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    opacity: 1;
  }}
  .scene .inner {{
    width: 82cqw;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }}

  /* 通用徽标与标题 */
  .badge {{
    display: inline-block;
    padding: 0.6cqw 2.4cqw;
    border-radius: 999px;
    font-size: 2.6cqw;
    font-weight: 800;
    letter-spacing: 0.08em;
    background: rgba(74, 222, 128, 0.12);
    border: 1px solid rgba(74, 222, 128, 0.4);
    color: var(--green);
    margin-bottom: 1cqw;
  }}
  .badge.cyan {{
    background: rgba(56, 189, 248, 0.12);
    border-color: rgba(56, 189, 248, 0.4);
    color: var(--cyan);
  }}
  .badge.amber {{
    background: rgba(251, 191, 36, 0.12);
    border-color: rgba(251, 191, 36, 0.4);
    color: var(--amber);
  }}
  .badge.red {{
    background: rgba(248, 113, 113, 0.12);
    border-color: rgba(248, 113, 113, 0.4);
    color: var(--red);
  }}
  h2 {{
    font-size: 4.0cqw;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 1.5cqw;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
  }}

  /* 开场专属样式 */
  #s-open .phs {{ display: none; flex-direction: column; align-items: center; text-align: center; width: 82cqw; }}
  #s-open[data-phase="splash"] .phs-splash {{ display: flex; }}
  #s-open[data-phase="topic"] .phs-topic {{ display: flex; }}
  .hook-graphic {{
    width: 14cqw;
    height: 14cqw;
    color: var(--green);
    margin: 1.5cqw 0;
  }}
  .hook-graphic svg {{ width: 100%; height: 100%; }}
  .hook-title {{
    font-size: 6.2cqw;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.3;
  }}
  .hook-title em {{ font-style: normal; color: var(--green); }}
  .tp-title {{
    font-size: 6.5cqw;
    font-weight: 900;
    color: var(--green);
    text-shadow: 0 0 20px rgba(74, 222, 128, 0.4);
  }}
  .sub {{
    font-size: 3.0cqw;
    color: var(--dim);
    margin-top: 1cqw;
  }}

  /* 呼吸动效与多波次入场 */
  .breathe {{ animation: breathe 2.2s ease-in-out infinite; }}
  @keyframes breathe {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.05); }}
  }}
  .w {{ opacity: 0; transform: translateY(2.5cqw); transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.2, 0.9, 0.3, 1); }}
  .scene.active .w {{ opacity: 1; transform: translateY(0); }}
  .scene.active .w2 {{ transition-delay: 0.1s; }}
  .scene.active .w3 {{ transition-delay: 0.2s; }}
  .scene.active .w4 {{ transition-delay: 0.3s; }}

  /* 下区字幕 */
  .sub-box {{
    position: fixed;
    bottom: 14%;
    left: 8cqw;
    right: 8cqw;
    z-index: 6;
    min-height: 6.5cqh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    pointer-events: none;
  }}
  .sub-text {{
    font-size: 4.4cqw;
    font-weight: 800;
    line-height: 1.4;
    letter-spacing: 0.05em;
    color: rgba(232, 241, 236, 0.35);
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.85);
    display: inline-block;
    max-width: 82cqw;
  }}
  .sub-text .w {{ display: inline; color: rgba(232, 241, 236, 0.35); transition: color 0.12s; }}
  .sub-text .w.read {{ color: #86efac; }}
  .sub-text .w.curr {{
    color: #ffffff;
    text-shadow: 0 0 1.5cqw #4ade80, 0 0 3cqw #22c55e;
  }}

  /* 转场与控制 */
  .flash {{
    position: fixed;
    inset: 0;
    background: #ffffff;
    opacity: 0;
    pointer-events: none;
    z-index: 10;
  }}
  .flash.do-flash {{ animation: flashAnim 0.38s ease-out forwards; }}
  @keyframes flashAnim {{ 0% {{ opacity: 0.85; }} 100% {{ opacity: 0; }} }}

  #btnPlay {{
    position: fixed;
    bottom: 4cqh;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9;
    background: rgba(14, 26, 34, 0.85);
    border: 1px solid var(--line);
    color: var(--green);
    font-size: 2.8cqw;
    padding: 1cqw 4cqw;
    border-radius: 4cqw;
    cursor: pointer;
  }}

  {custom_css}
</style>
</head>
<body>
<div class="stage">
  <canvas id="bg-canvas"></canvas>
  <div id="flashOverlay" class="flash"></div>

  <!-- 顶部作品标题 -->
  <div class="head">
    <div class="head-pill">
      <h1 id="mainTitle" class="main-title">
        <span class="title-line title-main">贝莱斯芽孢杆菌</span>
        <span class="title-line title-sub">国外明星菌株与中国商业化优势菌株盘点</span>
      </h1>
    </div>
  </div>

  <!-- 分镜开发辅助标识 HUD（安全区外盲区） -->
  <div id="chapText">第 1 / 24 节</div>

  <!-- 中区：多场景轮播 -->
  {all_scenes_joined}

  <!-- 下区：卡拉OK字幕区 -->
  <div class="sub-box">
    <div id="subText" class="sub-text"></div>
  </div>

  <button id="btnPlay">▶ 点击播放预览</button>
  <audio id="voice" src="../../inputs/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点/voice.wav" preload="auto"></audio>
</div>

<script>
// ==================== 音效引擎 ====================
var VibeSound = (function() {{
  var ctx = null;
  var noiseBuffer = null;
  function getCtx() {{
    if (!ctx) {{
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
      data[i] = (b0 + b1 + b2 + white * 0.1848) * 0.15;
    }}
    noiseBuffer = buf;
    return noiseBuffer;
  }}
  return {{
    init: function() {{ getCtx(); }},
    pop: function() {{
      var ac = getCtx(); if (!ac) return;
      var now = ac.currentTime;
      var osc = ac.createOscillator(); var gain = ac.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(1100, now);
      osc.frequency.exponentialRampToValueAtTime(320, now + 0.1);
      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.35, now + 0.004);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.12);
      osc.connect(gain); gain.connect(ac.destination);
      osc.start(now); osc.stop(now + 0.12);
    }},
    whoosh: function() {{
      var ac = getCtx(); if (!ac) return;
      var now = ac.currentTime;
      var buf = getNoiseBuffer(ac);
      var src = ac.createBufferSource(); src.buffer = buf;
      var filter = ac.createBiquadFilter(); filter.type = 'bandpass'; filter.Q.value = 1.2;
      filter.frequency.setValueAtTime(300, now);
      filter.frequency.exponentialRampToValueAtTime(2200, now + 0.15);
      filter.frequency.exponentialRampToValueAtTime(380, now + 0.35);
      var gain = ac.createGain(); gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.32, now + 0.14);
      gain.gain.linearRampToValueAtTime(0.0001, now + 0.35);
      src.connect(filter); filter.connect(gain); gain.connect(ac.destination);
      src.start(now); src.stop(now + 0.35);
    }},
    chime: function() {{
      var ac = getCtx(); if (!ac) return;
      var now = ac.currentTime;
      var notes = [
        {{ f: 659.25, d: 0.00, v: 0.28 }},
        {{ f: 880.00, d: 0.04, v: 0.25 }},
        {{ f: 1108.73, d: 0.08, v: 0.22 }},
        {{ f: 1318.51, d: 0.12, v: 0.20 }}
      ];
      notes.forEach(function(n) {{
        var t = now + n.d;
        var osc = ac.createOscillator(); var gain = ac.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(n.f, t);
        gain.gain.setValueAtTime(0.001, t);
        gain.gain.linearRampToValueAtTime(n.v, t + 0.005);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.95);
        osc.connect(gain); gain.connect(ac.destination);
        osc.start(t); osc.stop(t + 0.95);
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

// ==================== 数据与时间线 ====================
var SCENES = {scenes_js};
var CHAP_NAMES = {chaps_js};
var OPEN_PHASES = {open_phases_js};
var TIMESTAMPS = {timestamps_js};

window.SCENES = SCENES;
window.CHAP_NAMES = CHAP_NAMES;

var curScene = -1;
var curPhase = '';
var flashEl = document.getElementById('flashOverlay');
var openSceneEl = document.getElementById('s-open');
var chapTextEl = document.getElementById('chapText');

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

  if (chapTextEl) {{
    chapTextEl.textContent = '第 ' + (idx + 1) + ' / ' + SCENES.length + ' 节 · ' + CHAP_NAMES[idx];
  }}
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

// ==================== 字幕引擎（固定窗口不滚动 + 逐字高亮） ====================
var subUnits = [];
var curUnitIdx = -1;
var subTextEl = document.getElementById('subText');

function buildSubUnits(ts) {{
  var units = [];
  var curChars = [];
  var puncts = ['，', '。', '！', '？', '；', '、', '：', '\\n'];
  var endPuncts = ['。', '！', '？'];

  for (var i = 0; i < ts.length; i++) {{
    var c = ts[i];
    curChars.push({{ ch: c.Char, st: c.StartSeconds, et: c.EndSeconds, origIdx: i }});
    var isEndPunct = endPuncts.indexOf(c.Char) >= 0;
    var isPunct = puncts.indexOf(c.Char) >= 0;
    var isLong = curChars.length >= 10;
    if (isEndPunct || (isPunct && curChars.length >= 4) || isLong) {{
      var renderChars = curChars.filter(function(x) {{ return x.ch.trim().length > 0; }});
      if (renderChars.length > 0) {{
        units.push({{
          start: curChars[0].st,
          end: curChars[curChars.length - 1].et,
          chars: curChars.slice()
        }});
      }}
      curChars = [];
    }}
  }}
  if (curChars.length > 0) {{
    units.push({{
      start: curChars[0].st,
      end: curChars[curChars.length - 1].et,
      chars: curChars.slice()
    }});
  }}

  // 合并过短单元 (<4字)
  var merged = [];
  for (var j = 0; j < units.length; j++) {{
    var u = units[j];
    if (merged.length > 0 && u.chars.length < 4) {{
      var prev = merged[merged.length - 1];
      prev.chars = prev.chars.concat(u.chars);
      prev.end = u.end;
    }} else {{
      merged.push(u);
    }}
  }}
  return merged;
}}

subUnits = buildSubUnits(TIMESTAMPS);

function renderUnitDom(unit) {{
  var html = '';
  for (var i = 0; i < unit.chars.length; i++) {{
    var item = unit.chars[i];
    html += '<span class="w" id="w-' + i + '">' + item.ch + '</span>';
  }}
  subTextEl.innerHTML = html;
}}

function updateSubtitle(t) {{
  var idx = -1;
  for (var i = 0; i < subUnits.length; i++) {{
    if (t >= subUnits[i].start && t <= subUnits[i].end + 0.3) {{
      idx = i;
      break;
    }}
  }}

  if (idx !== curUnitIdx) {{
    curUnitIdx = idx;
    if (curUnitIdx >= 0) {{
      renderUnitDom(subUnits[curUnitIdx]);
    }} else {{
      subTextEl.innerHTML = '';
    }}
  }}

  if (curUnitIdx >= 0) {{
    var unit = subUnits[curUnitIdx];
    for (var k = 0; k < unit.chars.length; k++) {{
      var el = document.getElementById('w-' + k);
      if (!el) continue;
      var c = unit.chars[k];
      if (t >= c.et) {{
        el.className = 'w read';
      }} else if (t >= c.st) {{
        el.className = 'w curr';
      }} else {{
        el.className = 'w';
      }}
    }}
  }}
}}

// ==================== 主时钟与 Playwright 暴露 ====================
var audio = document.getElementById('voice');
var btnPlay = document.getElementById('btnPlay');

function syncTime(t) {{
  updateScene(t);
  updateSubtitle(t);
}}
window.syncTime = syncTime;

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
  audio.play().catch(function(e) {{}});
}}

btnPlay.addEventListener('click', startPlay);
audio.addEventListener('play', function() {{ requestAnimationFrame(tick); }});
audio.addEventListener('seeked', function() {{ syncTime(audio.currentTime); }});
audio.addEventListener('timeupdate', function() {{ syncTime(audio.currentTime); }});

// ==================== 高能背景粒子引擎 (bio-bubbles) ====================
var VibeBackgrounds = (function() {{
  function init(canvas, presetName) {{
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var w = canvas.width = 1080;
    var h = canvas.height = 1920;

    var bubbles = [];
    var count = 38;
    for (var i = 0; i < count; i++) {{
      bubbles.push({{
        x: Math.random() * w,
        y: Math.random() * h,
        r: 12 + Math.random() * 42,
        vy: -(0.4 + Math.random() * 1.2),
        vx: (Math.random() - 0.5) * 0.4,
        alpha: 0.08 + Math.random() * 0.22,
        phase: Math.random() * Math.PI * 2
      }});
    }}

    function draw() {{
      ctx.clearRect(0, 0, w, h);

      // 径向深色背景微光
      var bgGrad = ctx.createRadialGradient(w/2, h*0.4, 100, w/2, h*0.4, 900);
      bgGrad.addColorStop(0, '#0c1a24');
      bgGrad.addColorStop(1, '#070d12');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      for (var j = 0; j < bubbles.length; j++) {{
        var b = bubbles[j];
        b.y += b.vy;
        b.x += Math.sin(b.phase) * 0.5 + b.vx;
        b.phase += 0.02;

        if (b.y + b.r < 0) {{
          b.y = h + b.r;
          b.x = Math.random() * w;
        }}

        var grad = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
        grad.addColorStop(0, 'rgba(74, 222, 128, ' + (b.alpha * 1.5) + ')');
        grad.addColorStop(0.6, 'rgba(34, 197, 94, ' + (b.alpha * 0.8) + ')');
        grad.addColorStop(1, 'rgba(74, 222, 128, 0)');

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();
      }}
      requestAnimationFrame(draw);
    }}
    draw();
  }}
  return {{ init: init }};
}})();

window.addEventListener('DOMContentLoaded', function() {{
  var canvas = document.getElementById('bg-canvas');
  if (canvas) VibeBackgrounds.init(canvas, 'bio-bubbles');
  syncTime(0);
}});
syncTime(0);
</script>
</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ HTML 成功生成: {OUTPUT_HTML} (文件大小: {len(html_content)} 字符)")
