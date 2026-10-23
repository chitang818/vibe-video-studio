# VIBE Video Studio Agent Instructions (AGENTS.md)

> 本文件是本工作区的项目级通用 Agent 核心指令。任何 AI Agent 在当前工作区执行任务时均须自动遵守本规范。

---

## 1. 项目定位与核心认知
- **项目定义**：面向抖音竖屏（9:16，1080×1920）「VIBE 知识大赏」类知识科普视频的标准量产车间。
- **技术栈**：单文件自包含 HTML（原生 JS + CSS 动画，数据全内联）+ 字级时间戳 JSON + Playwright 逐帧录制 + FFmpeg 合成 MP4。
- **核心认知**：**不是 AI 文生视频**，而是精确对齐音画、字幕逐字高亮、信息密度高的代码可控渲染。
- **双模式交付支持**：
  - **模式 A（轻量模式）**：仅生成自包含 HTML 动画页并完成安全区 QA，提供秒级浏览器即时预览与卡点检查，支持直接交付或供外部本地渲染器（如 WeMediaForge）极速离线渲染；
  - **模式 B（完整模式）**：全自动完成 HTML 制作、Playwright 逐帧录制与 FFmpeg 混流，直接输出最终 MP4。

---

## 2. 规则与技能自动索引（SSOT）
- **业务制作硬性规则库**：
  详细排版布局、四边安全区数值推导、卡拉OK断句三原则、行末标点过滤及 14 条铁律请查阅：
  👉 [`.agents/rules/vibe-rules.md`](file:///.agents/rules/vibe-rules.md)（单一事实源）
- **视频量产技能流程与双模式规范**：
  前置交付模式决策、两阶段解耦执行流程（阶段 I：HTML构建与QA；阶段 II：逐帧录制与混音合成）请查阅：
  👉 [`.agents/skills/vibe-knowledge-video/SKILL.md`](file:///.agents/skills/vibe-knowledge-video/SKILL.md)

---

## 3. 交付物独立工程文件夹归档规范（WeMediaForge 协同标准）

为保障与桌面端渲染器（WeMediaForge）无缝对接、实现零配置拖拽即渲染，任何作品在完成网页制作后，**必须归集为自包含的独立工程文件夹**：

```
📁 {作品编号}_{作品名称}/   (例如: N0001_贝莱斯芽孢杆菌科普/)
├── 📄 {作品编号}_{作品名称}.html      (核心动效网页，数据全内联)
├── 🎵 {作品编号}_*.wav 或 voice.wav   (主口播音频，物理时间基准)
├── 📊 *_char_timestamps.json         (字级时间戳文件)
├── 📝 *.txt 或 script.txt             (文案正文脚本)
└── 🔔 sfx.json                       (毫秒级音效触发时刻表)
```

### 两种工程归档模式：
1. **就地赋能模式（In-Place Mode，首选推荐）**：
   若用户输入的素材本身已在一个工程文件夹内（如 `vibe测试/N0001/`），Agent 必须直接在该文件夹内**就地生成**配套的 `.html` 与 `sfx.json`，使其直接补齐为可独立渲染的工程包，严禁将文件散落到外部。
2. **零散建档归集模式（Projects Archive Mode）**：
   若用户输入的是散装文件（未组织在独立文件夹中），制作时必须自动在 `projects/{作品编号}_{作品名称}/` 下建档归集，将原始素材与生成的 `.html`、`sfx.json` 统一收拢在该独立文件夹中。

### 临时缓存隔离原则：
- 项目彻底废止 `inputs/` 与 `output/` 割裂目录；
- 录制过程帧序列、QA 探针截图与混音临时切片全部强制隔离至 `temp/` 目录；
- `python vibe.py clean` 专职清空 `temp/` 缓存，严禁触碰任何工程作品。

---

## 4. Agent 行为铁律与红线
1. **交付模式前置确认**：
   - 用户明确指定“仅生成网页/HTML”或“生成视频/MP4”时，遵照执行对应模式；
   - **用户未明确指定时，严禁直接启动耗时几分钟的逐帧录制与混流**，必须先主动询问用户偏好（推荐优先以模式 A 快速生成 HTML 即时预览）。
2. **音画 100% 同步**：所有场景边界、开场相位、数据强调与音效时刻必须从字级时间戳提取（使用 `python vibe.py timeline`），**严禁拍脑袋估算**。
3. **四边安全区红线**：
   - 顶部 ≥10cqh（刘海/状态栏）、底部 ≥14cqh（抖音底部 UI）、左右各 ≥8cqw（避让右侧互动栏与曲面圆角）。
   - 内容最大宽度 ≤84cqw 居中，中区内容高度 ≤54cqh。安全区外只允许背景，任何正文/图表/字幕严禁侵入安全区。
4. **数据全内联**：file:// 协议下禁止 fetch 本地外部文件，文案、时间戳、场景数据必须全部内联注入 HTML。
5. **交付完整性门禁**：交付 HTML 时必须同步输出 `sfx.json` 并归拢至独立工程目录，严禁只输出孤立的单个 HTML 文件导致丢失音频或音效配置。
6. **工具链统一调用**：
   - 环境诊断：`python vibe.py doctor`
   - 时间线与音效提取：`python vibe.py timeline <json> <txt> [-o <out.txt>] [--sfx-out <sfx.json>]`
   - 工程打包归档与检查：`python vibe.py pack <工程目录或HTML路径>`
   - 播放检查：`python vibe.py check <html_path>`
   - 安全区 QA：`python vibe.py qa <html_path>`
   - 全维度复核门禁：`python vibe.py audit <html_path>`
   - 背景画廊选型：`python vibe.py bg`
   - 快速预览：`python vibe.py preview <html_path>`
   - 逐帧录制：`python vibe.py render <html_path> <frames_dir> <duration>`
   - 混音合成：`python vibe.py mux <frames_dir> <voice_wav> <output_mp4> <duration>`
   - 成品验证：`python vibe.py verify <output_mp4>`
   - 一键流水线：`python vibe.py pipeline <html_path> <voice_wav> <output_mp4> <duration>`
   - 一键安全清理：`python vibe.py clean`（专职安全清空 temp/ 临时过程缓存，不伤任何工程资产）
