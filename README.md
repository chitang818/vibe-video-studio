# VIBE 知识动画标准化工作区

输入原文案、WAV 和字时间戳，产出固定 Canvas 网页与可供 WeMediaForge 使用的工程。Agent 优先编写结构化分镜，组件编译器负责排版、节点、动效和播放器。

新制作默认使用[分阶段网页视频工作流](references/web-video-workflow.md)：原件核验→语义分镜→视觉说明/草图→素材与单镜头→整片组装→检查。`python vibe.py pipeline --help`查看命令，过程入口保存在作者工程index.html。四个阶段Skill可逐步执行与指定镜头返工；不以PPT或六类版式限制表达。旧compile命令和历史作品保留。

[项目入口](AGENTS.md) · [制作技能](.agents/skills/vibe-knowledge-video/SKILL.md) · [规则](.agents/rules/vibe-rules.md) · [质量契约](references/quality-contract.md) · [机器 Profile](references/quality-profile.json) · [第二阶段实施状态](references/cross-agent-implementation.md)

## 统一流程

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python vibe.py context
python vibe.py doctor
python vibe.py compile --help
python vibe.py audit <工程>
# 实际看图听音复核，再由外部受信审核者签发凭证
python vibe.py pack <工程> --out releases/<新版本>
python -X utf8 -m unittest discover -s tests -v
```

需要持久日志和隔离的 C# 构建证据时，使用 `python scripts/run_regressions.py`。消费端契约测试需要 .NET 10 SDK；HTML 制作与浏览器 QA 本身不依赖 .NET。

[标准化示例](examples/standardized/README.md) 使用合成测试音展示三场景流程，不是已验收成片。支持 process/classification/exchange/cross-section/comparison/data/ending 组件；数据组件要求真实数值、单位和原词锚点。

## 状态与文件

- fast-build/compile：草稿；audit 自动通过为 needs_review，不代表独立创意审核。
- quality-review.json：实际观察记录；自行填 passed 不构成正式批准。
- release.attestation.json：外部受信签发方对确切资产、复核和证据的签名。
- pack：检查后生成新目录；没有信任配置/有效签名会拒绝正式发布。
- artifacts/quality/<路径哈希>/runs/<runId>：持久证据和逐次报告。
- releases/<新版本>：发布资产、凭证和证据索引，不能就地覆盖。

依赖锁在 requirements.lock.txt；正式字体基线为共享运行时要求的 Microsoft YaHei，报告记录字体和浏览器版本。未满足基线明确失败，不能静默替代。

WeMediaForge 正式导出与工作流已接入[凭证检查](integrations/WeMediaForge/README.md)，草稿导入和预览保留。没有执行真实 WinUI 端到端导出验收。旧 DOM 模板/提示词标为 LEGACY，只用于历史维护，不能通过旧 pack 获得 READY。

规则迁移与兼容取舍见[规则保留清单](references/rule-migration.md)，制作验收逐项使用[当前检查清单](references/checklist.md)。LEGACY仅废止旧技术路径，不能作为丢弃业务要求的理由。


## 动态PPT默认制作模式（2026-10-27）

新制作使用story v2与presentation-portrait-v1，保留v1故事旧语义。六类版式、固定主题、图片适配、入场/强调/转场和三种素材统一导入见[制作入口](references/presentation-authoring.md)。允许文字主视觉与阅读停留，不以每两秒运动或强制机制图验收；原件/数字、字形/字幕、安全区、声音与签名边界保留。共享运行时1.1.0由上游同步，固定模板6内联原始图片字节；历史作品不改写，当前消费兼容性升级不代表真实WinUI导出验收。
