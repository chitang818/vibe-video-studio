---
name: vibe-visual-direction
description: 为已拆分镜头设计画面、构图、视觉层级与展示过程，并输出可查看的静态结构草图。
---

# vibe-visual-direction

读取[统一工作流与阶段Schema](../../../references/web-video-workflow.md)，只负责本阶段，数值和共用边界不复制。

确认segment为ready，先确定style共用字体/色彩/背景与素材方向。逐镜保留观看目标和原文依据，扩展视觉表达，不扩写口播事实/科学结论/数字。

提交briefs.json：focus、composition、rationale、opening/development/ending、continuity、constraints、assetRequests与sketch。描述主次关系、焦点/留白、字幕避让、随口播变化及镜头间差异；不要只写“高级、丰富”。sketch用真实slot/label/form生成结构草图，明确不是最终素材。不机械轮换版式或强求平均模板数量。

执行pipeline direct --input并查看全部草图；通用视觉说明与搜图词/生图prompt/SVG说明分开。构图单调先改本阶段，避免等整片合成后补装饰。
