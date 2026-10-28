# 消费端审核验证已接入

2026-10-27 用户明确授权后，consumer-release.patch 已应用到同级 WeMediaForge 工作区。正式渲染服务与工作流执行器调用 VibeReleaseVerifier；草稿导入和预览不要求凭证。未配置工程外的 VIBE_TRUST_STORE 时，正式导出被拒绝。

补丁保留为实施记录；此处源码是独立 ConsumerContract 的契约副本，不代表安装包。实际消费端另补充取消令牌的入口检查。没有创建生产密钥、修改生产信任或改动共享运行时逻辑。

ConsumerContract 可通过 MSBuild 参数 WeMediaForgeRoot 指向实际仓库源码；Python 回归设置 VIBE_CONSUMER_REPO 后使用该模式。真实 WinUI 导出仍待验收。
