---
name: vibe-scene-production
description: 将视觉说明落实为素材与确定性动效，生成可独立播放和局部重做的网页镜头。
---

# vibe-scene-production

读取[统一工作流与阶段Schema](../../../references/web-video-workflow.md)，只负责本阶段，数值和共用边界不复制。

确认direct为ready，运行pipeline capabilities核对真实能力；为每镜编写implementation.json，记录family、reason和elements。元素选kind/slot/原词index/entrance，按类型填写text/assetId/tone/emphasis；可组合构图，禁止未知字段/脚本/CSS。需新增能力时报告缺口，不把所有缺图场景变成矩形框。

分别决定来源（用户/本地/搜图/生成/代码绘制）、格式（文字/SVG/普通/透明图片）和呈现方式，可同镜混合。由Agent调用当前可用工具取得资产，遵守费用/上传授权；统一asset-import记录原始来源/许可/hash并本地化。搜索摘要不是许可证明。透明图片核对alpha和边缘；SVG只支持静态受限子集转PNG，内部动画须拆层/原生节点，不冒称整SVG元素可动画。

执行pipeline produce --input，或--shot局部重做。查看单镜HTML、关键帧、来源偏移与技术检查；核对字形/净空/实际边界、图片/科学语义、信息与装饰、口播节奏和手机效果。完成产物才交组装，缺失/stale不能跳过。
