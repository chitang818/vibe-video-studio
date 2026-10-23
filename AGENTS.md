# VIBE Video Studio Agent Instructions (AGENTS.md)

> 本文件是本工作区的项目级通用 Agent 核心指令。任何 AI Agent 在当前工作区执行任务时均须自动遵守本规范。

---

## 1. 项目定位与核心认知
- **项目定义**：面向抖音竖屏（9:16，1080×1920）「VIBE 知识大赏」类知识科普视频的标准量产车间。
- **技术栈**：单文件自包含 HTML（原生 JS + CSS 动画，数据全内联）+ 字级时间戳 JSON + Playwright 逐帧录制 + FFmpeg 合成 MP4。
- **核心认知**：**不是 AI 文生视频**，而是精确对齐音画、字幕逐字高亮、信息密度高的代码可控渲染。
- **双模式交付支持**：
  - **模式 A（轻量模式）**：仅生成自包含 HTML 动画页并完成安全区 QA，提供秒级浏览器即时预览与卡点检查，支持直接交付或供外部本地渲染器使用；
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

## 3. Agent 行为铁律与红线
1. **交付模式前置确认**：
   - 用户明确指定“仅生成网页/HTML”或“生成视频/MP4”时，遵照执行对应模式；
   - **用户未明确指定时，严禁直接启动耗时几分钟的逐帧录制与混流**，必须先主动询问用户偏好（推荐优先以模式 A 快速生成 HTML 即时预览）。
2. **音画 100% 同步**：所有场景边界、开场相位、数据强调与音效时刻必须从字级时间戳提取（使用 `python vibe.py timeline`），**严禁拍脑袋估算**。
3. **四边安全区红线**：
   - 顶部 ≥10cqh（刘海/状态栏）、底部 ≥14cqh（抖音底部 UI）、左右各 ≥8cqw（避让右侧互动栏与曲面圆角）。
   - 内容最大宽度 ≤84cqw 居中，中区内容高度 ≤54cqh。安全区外只允许背景，任何正文/图表/字幕严禁侵入安全区。
4. **数据全内联**：file:// 协议下禁止 fetch 本地外部文件，文案、时间戳、场景数据必须全部内联注入 HTML。
5. **工具链统一调用**：
   - 环境诊断：`python vibe.py doctor`
   - 时间线提取：`python vibe.py timeline <json> <txt>`
   - 播放检查：`python vibe.py check <html_path>`
   - 安全区 QA：`python vibe.py qa <html_path>`
   - 全维度复核门禁：`python vibe.py audit <html_path>`
   - 背景画廊选型：`python vibe.py bg`
   - 快速预览：`python vibe.py preview <html_path>`
   - 逐帧录制：`python vibe.py render <html_path> <frames_dir> <duration>`
   - 混音合成：`python vibe.py mux <frames_dir> <voice_wav> <output_mp4> <duration>`
   - 成品验证：`python vibe.py verify <output_mp4>`
   - 一键流水线：`python vibe.py pipeline <html_path> <voice_wav> <output_mp4> <duration>`
   - 一键清理还原：`python vibe.py clean`（清理输入输出与临时文件，恢复原始纯净状态）
