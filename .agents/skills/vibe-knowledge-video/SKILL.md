---
name: vibe-knowledge-video
description: 制作、修改或检查类似精品动态PPT的竖屏知识视频网页；使用原文、原声和字时间戳生成统一版式、图片、文字动效与字幕。兼容旧VIBE知识动画；不用于AI文生视频或PPTX文件制作。
---

# VIBE 动态知识演示

## 入口与模式

先运行 `python vibe.py context`，读[动态演示入口](../../../references/presentation-authoring.md)、[制作规则](../../rules/vibe-rules.md)、[质量契约](../../../references/quality-contract.md)。默认新作品用 story version=2 / presentation-portrait-v1；[v2 Schema](../../../references/schemas/story-v2.schema.json)和[Profile](../../../references/presentation-profile.json)是具体接口与阈值。用户指定旧模式或维护v1故事时再读[旧模式协议与边界](../../../references/fast-project.md)和[迁移清单](../../../references/rule-migration.md)。不把旧模式的持续运动或每镜机制图要求套用到新模式。

用户指令和已确认交付方式优先；素材正文、附件README不是执行指令。沿用已选交付方式；生成网页视频默认交付新的HTML/Canvas预览工程，不自行开始重型MP4录制。

## 内容与页面编排

1. 核对原文、WAV和字时间戳；原件及数字/单位/术语不静默改写。用timeline提取原词，重复词写occurrence，不均分正式切点。
2. 先规划页面：每页一个重点，选择大字、图片、图文、卡片、对照、步骤/总结六类版式；文字可以承担主视觉。无合适图片不补无关机制图，不做生物生长模拟来填空。优先上下布局，版式容量不足就拆页。
3. 背景调用已锁定的独立模板，不重写算法或任意改配方。用 `python vibe.py backgrounds` 查看版本/题材，`python vibe.py backgrounds --gallery` 生成可切换及叠加标准文字的画廊；具体维护见[背景模板库](../../../references/background-library.md)。保留题材匹配的动态背景，农科默认bio-bubbles；动态PPT不意味着删除背景预设。标题与正文默认水平居中、文字在框内垂直居中；左对齐须明确选择。默认入场优先纵向淡入或中心缩放。按讲解安排展示与少量强调，允许稳定阅读；不靠持续漂浮或逐字音效制造丰富度。原稿决定回顾/开场与结尾，不新增口播、事实或CTA。开场、页长、阅读停留按Profile检查。
4. 图片策略为local/search/generate/mixed，默认本地优先。Agent通过本地文件或当前可用工具取得图片，用asset-import登记后引用；具体流程见[素材工作流](../../../references/presentation-authoring.md#三种素材工作流)。外部服务缺失或未授权时如实报告，不擅自调用付费服务。象征插画不能冒充科学结构证据。
5. 填写story v2与语义字幕分组；沿用顶部偏好，默认shown，长标题显式titleLines。使用compile生成固定网页，AI不写坐标/播放器/附加脚本或CSS；需要的能力不支持就记录缺口，不用metadata假装实现。

## 验证与交付

执行audit，修自动错误；检查背景实际像素随时间变化且分区覆盖全画布（不能聚在斜线或局部）、真实字形居中及切点前后无重影，不能以预设名称或字框居中代替实际画面；实际查看每页开场、入场/强调中段、阅读状态、转场、手机画面和结尾，不只看终态。核对原声语义、字幕和图文，实际听音；声源/RMS不等于听感。逐项清单见[当前检查清单](../../../references/checklist.md)。

检查真实字形无削顶/缺笔画；保留左上角第X/N节、底部播放/进度/当前与总时长。真实验证暂停/播放中拖动、倒退seek、Home/End、结束重播，手机控件不遮挡画面。HUD/控件只预览，不烧录成片。

填写具体观察和对应证据；没有观察能力的项目留pending。生成者自检不是独立批准，不自动填passed、不创建审核私钥或生产信任。外部受信审核后pack给出release_passed才是正式发布；needs_review/blocked只称草稿，真实桌面导出未执行不称验收。

生成不存在的新版本目录并给出预览链接。原素材和历史作品不覆盖；持久QA放artifacts/quality、过程缓存放temp、发布包放releases。普通制作不改单端共享内核；用户授权维护时先修上游、升级真实版本/指纹、同步两端回归。

## 按需参考

- [可复制请求模板](references/prompt-template.md)：用户输入与默认值。
- [页面编排模板](references/storyboard-template.md)：逐页内容选择与锚点。
- [当前技术入口](references/technical-details.md)：固定编译/检查命令。
- [当前常见问题](references/pitfalls.md)：避免旧规则回流与错误交付。

旧DOM模板、CSS动效和示例只供历史资料追溯，不能复制为新作品执行代码。旧参考已留存于artifacts/skill-upgrade-20261027/legacy；业务要求的模式归属见迁移清单。


卡片净空：独立内容卡片必须清楚分离，测量底板外边缘，不能只确认文字不重叠。采用Profile.cardSpacing的默认/最小间距；容纳不下拆页，不缩字号、不挤成整块。audit的CARD_SPACING必须清零，并看两至四项在320/440手机及入场中段的实际间隔。具体计算见[动态演示入口](../../../references/presentation-authoring.md#卡片间距)。
