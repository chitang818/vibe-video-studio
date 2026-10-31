---
name: vibe-shot-planning
description: 规划网页视频的语义分镜；将原文、原声音频和字时间戳绑定为可检查的镜头与口播事件。
---

# vibe-shot-planning

读取[统一工作流与阶段Schema](../../../references/web-video-workflow.md)，只负责本阶段，数值和共用边界不复制。

核对script/voice/timestamps原件，准备共用style，执行pipeline intake。检查alignment.json：识别错误不能静默改原文或伪造映射；异常保留原件并解决后继续。

读取source-map阶段结果，辨认重点、因果、对照、递进与转折；以观看目标拆镜，不按句号、固定秒数或关键词直接决定。镜头可含多个信息事件。提交shots.json(version1)，startIndex包含/endIndex不包含指原始时间戳行，必须无漏无重覆盖全部。beats(index/quote/purpose)绑定真实原词，重复词由索引消歧，不拆专名/数据。首镜从0，末镜覆盖完整原声；阅读与静音可延续镜头。

运行pipeline segment --input，查看shots.md、原文范围、切点理由、事件时间和建议警告。缺少明确依据先修分镜，不提前替所有镜头选卡片或图形。
