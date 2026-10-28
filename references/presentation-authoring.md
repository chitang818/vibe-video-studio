# 动态 PPT 制作入口（默认模式）

目标是清晰、有节奏的动态演示，不是植物生长模拟。默认使用 story version=2、teal-editorial 主题和 presentation-portrait-v1；version=1 继续使用旧知识动画规则，不自动迁移历史作品。

## 生产步骤

1. `python vibe.py context`，核对原文、音频和字时间戳。用户未选素材策略时使用 local。
2. 根据讲解编排页面，选 statement / hero-image / image-text / cards / comparison / steps。不要为了主视觉强画机制图。连续三页同版式会产生提醒，必要时可保留。
3. 图片通过 asset-import 导入作者目录；story.assets 引用返回的 id/source，可配置 focusX/focusY。图片页必须有图；纯文字页说明 imageNote。无合适本地图时优先选择文字版式，不默默搜图或付费生图。
4. 页面 anchor、items[].anchor 和可选 emphasis.anchor 使用真实原词，重复词写 occurrence。第一镜从0开始，之后每页必须提供切点 anchor。页长4–20秒，事件间隔及尾部阅读停留不超过10秒。开场仍需1秒和4秒内两次内容推进。
5. compile、audit、实际看图听音、独立签发、pack。自动通过为 needs_review，不是正式批准。

```powershell
python vibe.py compile --story <作者目录>/story.json --voice <原声.wav> --timestamps <原字时间.json> --script <原文.txt> --caption-groups <字幕意群.json> --out projects/<不存在的新版本目录>
python vibe.py audit projects/<新版本目录>
```

## 版式与参数

| layout | 容量 | 图片 |
|---|---|---|
| statement | 1–2个观点；首条大字 | 不接受 |
| hero-image | 1–2条短说明 | 必需 |
| image-text | 1–2条讲解 | 必需 |
| cards | 2–4条 | 不接受 |
| comparison | 2组简短内容，共同维度须实际核对 | 不接受 |
| steps | 2–4步骤或总结 | 不接受 |

所有版式由真实字形测量兜底；Schema文字上限不是一定放得下的承诺。超限拆页，不缩小或截断。图片支持 contain/cover，焦点0–1；imageZoom开启轻微推近。entrance 可选 fade-up/slide-left/slide-right/zoom；emphasis.kind 为 color/marker/underline，强调对象为该条文字，可将需强调的短语单列为一条。transition 为 fade/push（旧页在切点前160ms退出，新页在切点后240ms进入，不叠两页文字）。卡片底板与文字有90ms固定错峰，不编造新的字时间戳。没有自由坐标、CSS、执行脚本或自定义缓动。

```json
{"version":2,"title":"养分吸收","authorId":"maker","theme":"teal-editorial","assetPolicy":"local","scenes":[{"id":"opening","layout":"cards","heading":"本期关注两件事","imageNote":"要点本身构成主视觉，无需配图","items":[{"text":"吸收机制","anchor":{"quote":"吸收机制"},"entrance":"fade-up"},{"text":"应用优势","anchor":{"quote":"应用优势"},"emphasis":{"kind":"underline","anchor":{"quote":"应用优势"}}}]}]}
```

此片段只示范结构，锚点必须适配真实文案和时间。完整可运行实例为 projects/N0009_presentation_authoring_v2/story.json 与 showcase.json；原声素材位于原N0009工程。可重建作者目录：`python -m scripts.build_presentation_examples --out <不存在的新作者目录>`。

## 三种素材工作流

### 卡片间距

卡片、步骤及对照页的独立内容底板必须分离；间距测量底板外边缘，不能用文字框或圆角空白充数。1080px画宽下默认净空56px，静态及入场过程中至少32px（阈值统一见presentation-profile.json的cardSpacing）。编译器根据底板高度加净空计算步距，四项不得压缩到相连；容纳不下就拆页，不缩字号或裁正文。audit以CARD_SPACING阻断不足，允许底板内部包含自己的文字和步骤标记。手机320/440px及动效中段都须看图复核。

项目不保管API密钥，不代替Agent调用外部工具。以下三种都已接入同一导入、登记、编译与检查流程；外部服务是否可用由当前Agent环境决定。

### 本地

选择用户提供或项目原创图片，确认用途；导入并将返回引用加入story.assets：

```powershell
python vibe.py asset-import --source <本地.png> --root <作者目录> --id cover --kind local --origin "用户提供的图片" --license user-provided
```

项目内置 leaf/water/soil 是原创象征插画，不是显微照片或精确结构图。原始绘制代码和说明在项目内，可作为轻量配图，不承担科学证明。

### 搜图

用户选择 search 或 mixed 后，Agent使用可用检索工具找候选，读取原始页面核对作者、原图与许可，下载原图到temp；不能把搜索摘要当许可证明。许可不清晰则不导入，并报告缺图。

```powershell
python vibe.py asset-import --source <已下载原图.png> --root <作者目录> --id soil-photo --kind search --origin "https://原始来源页面" --license licensed
```

公有领域使用 public-domain；许可依据应保存在来源记录中。导入器验证登记一致性，不证明法律授权本身。加入story.assets，将assetPolicy设search或mixed，再compile。无检索工具时明确说明，不伪造已搜到图片。

### 生图

用户选择 generate 或 mixed 后，Agent按当前可用技能选择服务并满足首次付费/上传授权；生成后核对科学适切性，将提示词、服务、模型和任务凭据记为origin或工程内记录的引用，不保存密钥。

```powershell
python vibe.py asset-import --source <生成结果.png> --root <作者目录> --id illustration --kind generate --origin "服务、模型、任务ID、提示词记录位置" --license provider-terms
```

加入story.assets，设generate或mixed后compile。工具不可用时报告，不假称已生成；不能默认替换成其他服务。当前N0009只实际使用本地素材，搜图/生图的导入链路已用受控素材测试，外部服务没有实际调用。

## 验证与交付

检查原文数字/单位、字幕、字形、安全区、图片及其登记哈希、动效关键阶段、暂停/跳转/重播、手机控件、音频声源。允许稳定阅读，像素运动不再作为每两秒必须满足的指标。逐场复核构图、语义和节奏；实际听音前soundMix保持pending。保留外部受信审核和发布边界。

当前六版式整片与背景/对齐基准：projects/N0009_丛枝菌根作用与优势_v17/index.html。examples/presentation-showcase-v5为历史结构样片，不作为当前视觉验收依据。自动质量证据见各工程qa-summary.json及artifacts/quality。


## 背景与真实居中（runtime1.1.1）

backgroundPreset可选bio-bubbles/constellation/dna-spiral/cyber-grid/aurora-dust/solid，农科默认bio-bubbles，solid必须显式选择。五种风格均有时间/seed确定性绘制，不是只填名称。contentAlign默认center，左对齐须显式left；正文、标题使用真实字形水平/垂直居中。默认入场为纵向淡入或中心缩放，横滑只在明确选择时使用。背景不当作正文信息推进；QA独立检查背景实际像素变化与墨迹中心。


2026-10-28背景全屏覆盖修复（runtime1.1.2）：独立坐标随机流及三层分层网格抖动，修复光斑斜向聚集。bio-bubbles按4列×6行采样，多个时间点至少20/24区达到16个可见像素（270×480缩图），不只检查全局有运动。正文不变，历史网页保留。


当前背景由[固定模板库](background-library.md)维护；普通制作只选backgroundPreset，可选backgroundTemplateVersion，不直接改配方。使用backgrounds --gallery看实际效果，backgrounds --check校验模块/生成物，backgrounds --audit保存各风格独立证据。
