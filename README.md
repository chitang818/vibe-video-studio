# VIBE 知识视频量产项目（vibe-video-studio）

面向抖音「VIBE 知识大赏」类竖屏知识视频的**标准化量产车间**：任何 AI Agent 或开发者只要读取本工作区，就能按同一套标准、模板与工具链，把“文案 + 配音 + 字级时间戳”三件套素材批量制作为音画同步的知识视频（1080×1920 / 9:16 / 卡拉OK字幕 / 多场景动画 / 独立音效轨）。

## 核心特性
- **面向工程项目化架构**：不再割裂输入输出，一个作品就是一个自包含工程文件夹（HTML + WAV + 时间戳 + TXT + sfx.json），素材与网页同构一体。
- **外部文件夹就地赋能**：外部导入的工程文件夹，直接在原目录补齐网页与音效表，零冗余拷贝。
- **临时缓存彻底隔离**：设立专用 `temp/` 目录存放过程帧与切片，一键清理安全无忧，绝不误删工程资产。
- **与 WeMediaForge 天然无缝互通**：生成的独立工程文件夹可直接拖拽入桌面端 WeMediaForge【网页处理 - 网页转视频】，调用本地 GPU 硬件加速秒级生成 MP4！

---

## 目录结构

```
vibe-video-studio/
├── .gitignore               ← 版本控制忽略配置（排除 temp/ 缓存与运行临时切片）
├── requirements.txt         ← Python 依赖声明（Playwright 等）
├── vibe.py                  ← [统一 CLI] 命令行工具（doctor / timeline / pack / check / qa / audit / bg / preview / render / mux / verify / clean）
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
│   ├── icons/               ← 20 项通用 24×24 线性 SVG 图形库
│   ├── motions/             ← motions.css（14 种入场、强调、转场 Keyframes）
│   ├── themes/              ← themes.css（科技风、农科风、科普风 CSS 变量组）
│   └── sounds/              ← sfx_presets.json（音效配方与时间放置规则）
├── examples/                ← 官方示范案例库
│   └── N0001_star_strain/   ← 完整案例定稿参考（demo.html，314.5s）
├── references/              ← 深度技术参考
├── scripts/                 ← 底层 Python 工具脚本
│   ├── pack.py              ← 工程自包含归档与 WeMediaForge 就绪检查
│   ├── clean.py             ← temp/ 临时缓存专用安全清理脚本
│   ├── doctor.py            ← 环境诊断
│   ├── extract_timeline.py  ← 精确时间线提取
│   ├── playcheck.py         ← 场景与字幕切换验证
│   ├── qa_bounds.py         ← 四边安全区边界合规扫描
│   ├── audit.py             ← 全维度质量复核与图数碰撞检测门禁
│   ├── render.py            ← Playwright 逐帧无头截图录制
│   ├── mux.py               ← FFmpeg 音画合成与音效轨混音
│   └── verify.py            ← 交付验证
├── projects/                ← 【项目工程库】（零散素材自动建档汇总，素材与网页一体）
└── temp/                    ← 【临时缓存区】（过程帧、QA 探针截图与混流切片，随时一键清空）
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

### 2. 使用方式

#### 方式 A：外部文件夹导入（就地闭环，推荐）
1. 用户在外部准备好已有文件夹（如 `c:\Users\xxx\Desktop\N0001\`），内含音频、时间戳与文案；
2. AI 在该文件夹内**就地生成**配套动效网页及 `sfx.json`；
3. 将该文件夹整体拖入 **WeMediaForge 桌面端【基础工具箱 - 网页处理】**，调用本地 GPU 硬件加速极速导出 MP4。

#### 方式 B：零散文件导入（自动建档）
1. 提供散装的配音 WAV、时间戳 JSON 与文案正文；
2. 系统自动在 `projects/{作品编号}_{作品名称}/` 目录下归集建档并生成配套动效网页；
3. 同样可将生成的工程文件夹直接供 WeMediaForge 批量离线渲染。

### 3. 一键清空临时缓存
```bash
# 安全清空 temp/ 过程缓存与根目录中间文件（绝不触碰 projects/ 下的任何工程资产）
python vibe.py clean -y
```

---

## 给 AI 的入口提示词（可整段粘贴）

```markdown
请按当前 vibe-video-studio 项目流程制作一个 VIBE 知识视频。
1. 先读取 .agents/rules/vibe-rules.md 与 template/skeleton.html，严格遵守其中的 14 条铁律（音画同步、四边安全区+三区布局、断句防碎行与标点过滤规则、图案化表达）。
2. 若素材位于已有工程文件夹中，在原文件夹内就地生成配套的单文件动效 HTML（数据全内联）和 sfx.json；若素材零散，则归集建档到 projects/{作品编号}_{作品名称}/ 目录下。
3. 执行 `python vibe.py timeline <时间戳JSON> <关键词txt> --sfx-out <sfx.json路径>` 精确提取场景边界与音效时间点，严禁估算。
4. 执行 `python vibe.py audit <HTML路径>` 进行全维度质量复核与图数碰撞检测门禁，确保 100% 绿灯。
5. 执行 `python vibe.py pack <工程目录>` 检查工程完整性，确认其达到可直接拖入 WeMediaForge 渲染的【就绪】状态。
```
