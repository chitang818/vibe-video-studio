# VIBE 知识视频量产项目（vibe-video-studio）

面向抖音「VIBE 知识大赏」类竖屏知识视频的**标准化量产车间**：任何 AI Agent（豆包工作模式、Cursor、Claude Desktop 等）或开发者只要读取本工作区，就能按同一套标准、模板与工具链，把“文案 + 配音 + 字级时间戳”三件套素材批量制作为音画同步的知识视频（1080×1920 / 9:16 / 卡拉OK字幕 / 多场景动画 / 独立音效轨）。

## 核心特性
- **音画 100% 同步**：以字级时间戳为唯一时钟驱动，杜绝估算漂移。
- **纯净单文件 HTML 动画**：原生 JS + CSS 动画驱动，数据全内联，支持浏览器随时打开预览与微调。
- **完备的短视频排版规范**：四边安全区（防平台遮挡）+ 三区弹性布局 + 卡拉OK防碎行断句。
- **一站式统一 CLI**：通过 `python vibe.py` 轻松完成环境诊断、时间线提取、QA 扫描、逐帧录制与混音合成。

---

## 目录结构

```
vibe-video-studio/
├── .gitignore               ← 版本控制忽略配置（排除渲染中间帧、视频产物）
├── requirements.txt         ← Python 依赖声明（Playwright 等）
├── vibe.py                  ← [统一 CLI] 命令行工具（doctor / timeline / check / qa / render / mux / verify / pipeline）
├── README.md                ← 本文件：快速上手说明 + 给 AI 的入口提示词
├── AGENTS.md                ← 项目级 Agent 最高指令与核心认知（自动挂载）
├── .agents/                 ← [Agent 标准体系] 智能体规则与技能中心
│   ├── rules/
│   │   └── vibe-rules.md    ← 制作规范单一事实源（SSOT：14条铁律 / 决策表 / 检查清单）
│   └── skills/
│       └── vibe-knowledge-video/   ← 独立技能总纲
├── template/
│   ├── skeleton.html        ← 通用骨架母版（机理科普核心：多阶段开场、SVG环形图、双列对比卡、卡拉OK断句引擎）
│   └── skeleton-timeline.html ← 演进特化模板（历史大事记核心：垂直推进时间轴、节点渐进高亮）
├── assets/                  ← 物理资产库
│   ├── icons/               ← 20 项通用 24×24 线性 SVG 图形库（互动/生化/逻辑/设备）
│   ├── motions/             ← motions.css（14 种入场、强调、转场 Keyframes）
│   ├── themes/              ← themes.css（科技风、农科风、科普风 CSS 变量组）
│   └── sounds/              ← sfx_presets.json（FFmpeg 音效配方与时间放置规则）
├── examples/                ← 官方示范案例库
│   └── N0001_star_strain/   ← N0001 完整案例定稿参考（demo.html，314.5s）
├── references/              ← 深度技术参考（technical-details / pitfalls / prompt-template / checklist）
├── scripts/                 ← 底层 Python 工具脚本
│   ├── doctor.py            ← 环境诊断（Python / FFmpeg / FFprobe / Playwright）
│   ├── extract_timeline.py  ← 精确时间线提取（修复标点偏移）
│   ├── playcheck.py         ← 场景与字幕切换验证
│   ├── qa_bounds.py         ← 四边安全区边界合规动态扫描
│   ├── render.py            ← Playwright 逐帧无头截图录制（瞬时 seek 预热）
│   ├── mux.py               ← FFmpeg 音画合成与独立音效轨混音（脚本保护规避超长）
│   ├── verify.py            ← 交付验证（媒体规格与音量探针）
│   └── clean.py             ← 工作区清理与状态还原（清空 inputs/output 恢复初始纯净状态）
├── clean.bat                ← [Windows 便捷入口] 双击一键清理还原工作区
├── inputs/                  ← 素材输入区（内置 N0000_quick_start 极速测试小样套件）
└── output/                  ← 作品交付区（HTML + MP4 + _work/ 缓存）
```

---

## 快速起步

### 1. 环境准备与诊断
```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt
playwright install chromium

# 2. 一键诊断运行环境
python vibe.py doctor
```

### 2. 使用方式（给用户）
1. 把素材放进 `inputs/`（每套一个子目录 `inputs/作品名/`，放 `script.txt` + `voice.wav` + `char_timestamps.json`；已内置 `inputs/N0000_quick_start/` 极速体验样例）；
2. 新建对话，让 AI「按 vibe-video-studio 项目流程处理这套素材」（粘贴下方“给 AI 的入口提示词”）；
3. AI 依据 `template/skeleton.html` 生成单文件 HTML 到 `output/{作品}/`，通过 `python vibe.py pipeline` 一键完成验证、录制与合成；
4. 用户随时双击打开 HTML 进行微调与确认。

### 3. 工作区清理与状态还原（可选）
当制作完成或需要将项目文件夹彻底重置为最原始空白状态时：
```bash
# 交互式确认清理（会列出所有待删除目录与释放空间）
python vibe.py clean
# 或在 Windows 下直接双击运行 clean.bat

# 免确认快速彻底清理：
python vibe.py clean -y

# 仅清空 output 目录（保留 inputs 素材）：
python vibe.py clean --only-output -y
```

---

## 给 AI 的入口提示词（可整段粘贴）

```markdown
请按当前 vibe-video-studio 项目流程制作一个 VIBE 知识视频。
1. 先读取 .agents/rules/vibe-rules.md 与 template/skeleton.html，严格遵守其中的 14 条铁律（音画同步、四边安全区+三区布局、断句防碎行与标点过滤规则、图案化表达）。
2. 素材路径：文案【{文案路径}】、配音【{配音WAV路径}】、字级时间戳【{时间戳JSON路径}】。
3. 执行 `python vibe.py timeline <时间戳JSON> <关键词txt>` 精确提取场景边界与音效时间点，严禁估算。
4. 以 template/skeleton.html 为基底修改生成单文件 HTML（数据全内联），输出到 output/{作品编号_作品名称}/ 子目录下。
5. 执行 `python vibe.py pipeline <html路径> <配音WAV路径> <输出MP4路径> <总时长秒>` 一键全自动完成 QA 扫描、逐帧录制、音效混音与规格校验。
6. 最终交付 HTML + MP4，并汇报验证结果。
```

---

## 批量生产与资产扩充
- **风格一致**：系列化视频可在 `manifest.txt` 或对话中指定主题（如“全部使用绿色农科风”）；
- **资产沉淀**：新设计的 SVG 图标或动效片段，请随手沉淀回 `assets/icons/` 或 `assets/motions/motions.css`，保持资产库日益充实。
