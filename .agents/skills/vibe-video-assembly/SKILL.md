---
name: vibe-video-assembly
description: 将已制作镜头按原声音频组装为完整网页视频，执行全片检查并保留真实审核边界。
---

# vibe-video-assembly

读取[统一工作流与阶段Schema](../../../references/web-video-workflow.md)，只负责本阶段，数值和共用边界不复制。

先pipeline inspect，确认所有镜头有效。assemble消费已生成场景描述，不重新调用导演或手写新播放器，不拼iframe；单镜局部时间映射回完整原声时间轴。原声/脚本/识别结果保持原件，背景/字幕/控件使用共享固定实现。

执行pipeline assemble、pipeline review；查看制作过程入口、整片、原文对照、素材及全部镜头联系表。实际核对起点/入场中段/转场/结尾，320/440手机、暂停/倒退seek/重播、实际声源/听感。检查跨镜构图/动效重复，不能用自动0错误证明好看。

问题定位到分镜/视觉导演/场景制作/组装，保留具体观察与证据；上游改后从受影响阶段重跑。自动通过状态仍needs_review。独立签名、pack和正式发布边界按质量契约；不创建制作Agent自信任密钥，不代填独立批准，不声称未执行的WeMediaForge桌面验收。
