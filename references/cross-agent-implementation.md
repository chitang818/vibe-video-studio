# 标准化第二阶段实施记录

基于跨 Agent 审查的优先级实施，历史作品和运行时镜像保留。

## 已实施

- 保留小数点的文本/触发词/字幕身份比较、严格原字时间校验、数值与单位依据。
- 固定完整网页模板（含 CSP 与本地声音），拒绝附加脚本/样式；浏览器限制外部请求。
- 严格 Schema/Profile/角色/安全 ID，固定正式画幅与字幕字号，资产引用闭包和两端数量限制。
- 标准组件编译：流程、分类、交换、剖面、对比、真实数据条与结尾；图示仍需按具体主题复核。
- 元数据之外的主图形重复、透明/低对比/空图形、实际路径像素和正文动态采样；受限图文嵌入关系。
- 完整声音资产统计和静音检查、响度/越尾/削波候选提示；不把时钟或 RMS 当作人耳证明。
- 新旧检查入口分离；旧 pack 不再报告 READY；context 向任何具备终端能力的 Agent 输出同一能力清单。
- 快照/锁/runId/原子证据、独立签名与新版本发布包；密钥不生成在工作区、不自动建立生产信任。
- 锁定依赖、CI 配置、持久证据、受控三场景正例、Python/C# 发布契约测试。

## 跨项目补丁状态

此前自动审批因跨项目写入和导出可用性风险拒绝实施；2026-10-27 用户在了解该行为后明确授权更新，现已应用。

integrations/WeMediaForge/consumer-release.patch 已应用到同级 WeMediaForge，包含 VibeReleaseVerifier、正式渲染/工作流调用、原脚本字段兼容。集成目录副本供契约编译；真实桌面导出仍未验收。

## 生产前仍需配置

独立审核者及其密钥保管、外部公钥信任配置。未配置时 Studio 允许草稿与自动 QA，但不会将自报 passed 当作正式批准。

## 验证入口

```powershell
python vibe.py context
python vibe.py doctor
python -X utf8 -m unittest discover -s tests -v
python -X utf8 C:/Users/chitang/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/vibe-knowledge-video
```

测试中的密钥和签名均为临时合成 fixture，不属于生产信任；C# 测试覆盖真实格式签名包、缺凭证和证据修改，不代表真实 WinUI 导出验收。

## 最终验证（本轮）

- 统一入口 `python scripts/run_regressions.py`：56 项全部通过，0 失败、0 错误、0 跳过；包含 Python/C# 签名包互操作、缺凭证/证据篡改拒绝、全门禁自报通过负例、全部七种组件、跨哈希种子模板一致性、Windows 子进程 UTF-8 及时间线微秒/数值边界。
- [最终测试摘要](../artifacts/regressions/b6a01b2bfc0940a99281ec002126884a/summary.json) 与 [完整日志](../artifacts/regressions/b6a01b2bfc0940a99281ec002126884a/tests.log) 为本地持久证据。
- doctor、技能格式检查、文档链接与 diff 空白检查通过。共享 scene.mjs/audio.mjs 与旧作品副本哈希相同。
- 三场景标准组件示例自动检查通过，状态 needs_review；其配音是合成测试音，没有正式科学/听感批准。
- 上阶段消费端补丁可应用且独立契约通过；本阶段已获用户授权应用，实际回归结果见后续记录。真实桌面导出仍未执行。
- CI 配置已添加，未在托管平台实际运行；需要 Windows 字体基线与 .NET 10 SDK。没有生成/安装生产信任密钥。

独立签发端必须运行受控版本的工具链，不执行作者提交的任意脚本。签名只约束确切资产和受信身份；若作者同时能控制私钥、信任库或签发进程，无法提供强独立性。


## 消费端实际接入验证（2026-10-27）

- 已应用审核验证到实际 WeMediaForge 两个正式导出入口；草稿导入、预览保留，不生成生产信任。
- WeMediaForge 针对性单元回归 22/22 通过；证据为同级仓库 artifacts/vibe-release-20261027/results/vibe-release-final.trx。
- Studio 56/56 回归通过，ConsumerContract 此次直接编译实际 WeMediaForge 源码；[测试摘要](../artifacts/regressions/28d3f6979e8b4d3aa5fb23cfb9ef1fad/summary.json)。
- 全程序隔离编译未通过：文稿库页面第 285 行报 CS1061，编译时引用的 ViewModel 缺 SelectCopywritingByIdAsync。两文件有其他并行未提交修改，编译后源码中已出现该方法；本任务未修改该区域。不能据此声称整机编译/WinUI 导出通过。
- .mjs 固定 LF，检出后的 scene.mjs 恢复到 Git 原 blob 和 Studio 相同字节，未修改运行时逻辑或更改预期指纹。
- 最终状态摘要在同级 WeMediaForge 的 artifacts/vibe-release-20261027/integration-summary.json；真实桌面导入到成片发布未执行。


## 规则保留修复（2026-10-27）

已逐项对照原规则、模板、清单、提示词、技术说明及旧audit，完整去向见[规则迁移清单](rule-migration.md)。补齐HUD、标题隐藏与语义分行、字号层级、圆环净空、循环数量、原稿开场、音效白名单/切点/收束/尾音、暂停和结束重播验证。context和技能统一路由到现行检查清单。历史技术数值冲突已明确处理，不以LEGACY标识丢业务规则。

本轮75项回归全部通过（含实际消费端源码互操作），[摘要](../artifacts/regressions/dccb3a3555a44f86b7f1700e4f25a5b1/summary.json)。N0009_v5自动检查0错误、0声音警告，303张证据；HUD相对真实竖屏坐标通过，已看首镜手机及第10镜完整画面。旧v4、原声与共享运行时保留；新旧scene.json哈希相同。

官方背景预设、标题渐变/光晕/磨砂、完整旧跨镜效果仍是共享运行时缺口，已恢复明确制作目标和未实现记录；不能据此宣称全部视觉效果已实现。HUD仅网页开发校对，不烧录成片。未建立生产信任、未执行真实桌面导出。


## 网页字形缓存修复（2026-10-27）

已复现48px微软雅黑在top/y=0缓存中丢失约4px字头，58px约5px。runtime-1.0.1改为真实字形度量的alphabetic基线和四边2px安全留白，容量不足失败，按字素簇换行，字幕同步基线。固定模板4暴露只读真实缓存像素副本，QA以独立留白参考做TEXT_CLIP检查，替代只估算行高。同步脚本不再覆盖Studio制作扩展。

84项回归全通过，[测试摘要](../artifacts/regressions/978ed6e617314fd0819bb89e70032a0b/summary.json)。N0009_v6自动检查0错误；全部文字缓存无笔画像素缺失，新旧同位置[截图对照](../artifacts/text-clipping-analysis/n0009-before-after.png)已查看。详细[修复摘要](../artifacts/text-clipping-analysis/fix-summary.json)。旧网页保留，原素材不改；新网页可直接打开，不依赖桌面软件。共享源与Studio镜像版本/字节一致，实际消费端源码互操作通过；没有声称WinUI整机导出验收或生成安装包。


## 模板5：底部进度控件补齐

固定模板加入可见播放/暂停、拖动进度条、当前/总时间与键盘Home/End。拖动期间不让播放帧刷新改写滑块位置，松手与声音时钟同步，暂停拖动不自动播放，播放中拖动保留状态；结束重播复位。预留独立控件空间与安全底边，不覆盖Canvas。仅预览层改动，没有修改共享运行时或桌面应用。

86项回归通过，[测试摘要](../artifacts/regressions/0dfc392da2484843b4a58f9fefdba2a4/summary.json)。N0009_v8整片自动0错误，320/440手机宽度与真实点击、拖动、键盘、原声时钟检查通过；已看手机截图。v7长片拖动检查未通过记录保留，v8调整手势保持及原子时钟取样后通过。原始作品和历史版本未覆盖，独立听感与审核仍待完成。


## 动态PPT默认制作模式（2026-10-27）

新制作使用story v2与presentation-portrait-v1，保留v1故事旧语义。六类版式、固定主题、图片适配、入场/强调/转场和三种素材统一导入见[制作入口](presentation-authoring.md)。允许文字主视觉与阅读停留，不以每两秒运动或强制机制图验收；原件/数字、字形/字幕、安全区、声音与签名边界保留。共享运行时1.1.0由上游同步，固定模板6内联原始图片字节；历史作品不改写，当前消费兼容性升级不代表真实WinUI导出验收。


### 动态PPT实施完成与验证范围

默认story v2，六类版式、teal-editorial、入场/强调/图片适配与双场淡化/短距推移，runtime1.1.0，模板6，组件3。新Profile允许文字主视觉与阅读停留；三种Agent取得素材统一asset-import。技能及prompt/storyboard/technical/pitfalls已重写，原件存artifacts/skill-upgrade-20261027；skill验证与相对引用检查通过。

110项回归0失败/0跳过，含实际消费端源码契约，证据artifacts/regressions/811ab253967a4afdb04e72c10e4fa2d6。N0009_v13自动检查0错误/384截图/69事件，六版式样片examples/presentation-showcase-v5为0错误/318截图/48事件；报告和联系表见artifacts/presentation-upgrade/final/summary.json。原文/WAV/时间戳与下载目录逐字节相同。已看18页入场/中段/终态及手机代表截图，未完成实际听感、独立批准或真实WinUI导出。搜图/生图外部工具没有实际调用；其统一导入链路已用受控素材验证。草稿不冒称正式发布。


### 2026-10-28 背景、真实居中与转场视觉纠偏

重构曾错误地关闭预设背景、采用左对齐和顶部墨迹布局；前后两页推移叠加产生重影。runtime1.1.1将五种背景按时间/seed确定性移植，presentation默认bio-bubbles，solid显式选；编译器4默认水平/垂直居中及纵向/中心入场，步骤标记与文字同中心。旧页切点前160ms退出，新页切点后240ms进入，单次只绘制当前页。

118项回归0失败/0跳过，含实际消费端源码契约：artifacts/regressions/ac3979f766f84d3fbabf514a9640109a。N0009_v15在最终规则快照下自动0错误，472截图；实际背景采样6768可见/10101变化像素。最新报告artifacts/quality/4f864d18fbb04ead/runs/117f7ac01d964b519e06a5c68b8c9c44/report.json。截图、五背景对照与修复记录在artifacts/visual-restoration-20261028。Skill/规则同步通过权限审核，未改生产信任。独立批准、听感及真实桌面导出仍未完成；历史作品保留。


### 2026-10-28 背景空间分布修复（runtime1.1.2）

seeded小盐值X/Y流相关，seed8原相关系数0.6865导致斜向聚集。改独立混合流（同样本相关系数-0.0211）及近/中/远三层分层抖动，纵向周期包裹保留跨边缘尾部。增加4×6分区覆盖检查与局部运动负例，Profile version3要求bio至少20/24区可见。不同种子与0/4/30/80/159秒测试通过。

121项回归0失败/0跳过：artifacts/regressions/c046270ef41a4836920f4e782daad811。N0009_v16整片自动0错误/472截图，三个实际背景采样均24/24区覆盖；英文入口previews/n0009-v16/index.html已验证播放，与工程HTML字节一致。详情及前后分布、负例日志和截图：artifacts/background-coverage-20261028。Skill/上游/镜像已按权限审核同步，原声原文时间戳不变，未创建独立批准、未做实际听感或WinUI导出验收。


### 2026-10-28 固定背景模板库（runtime1.2.0）

五款动态背景与显式纯色独立源模块、固定配方、版本锁及按模板形态检查已落地。确定性构建单文件scene.mjs，上游与Studio字节一致；Skill/规则/入口/编译/质量门禁/同步命令同步。背景画廊支持切换、叠加文字、暂停、跳转、重置；普通制作只选择预设。

135项回归0失败/0跳过，含实际消费端源码契约。40帧背景基线和N0009四帧整页像素一致；六模板自动检查0错误，38张截图含320/440手机画廊。N0009_v17整片自动0错误，报告仍needs_review。持久证据见artifacts/background-library/summary.json。保留历史作品，未代填独立审核，未声称实际听感、WinUI/MSIX构建或真实桌面导出通过。


### 2026-10-28 卡片净空门禁（Profile v5）

四项步距174px仅留下4px底板净空，原碰撞检查未拦截。改为底板高度+56px步距，静态及入场采样最少32px；Skill/规则/清单/质量契约同步。几何与角色识别内容底板，改名称不能绕过，底板内文字与标记仍允许包含。两至四项、全部入场及小间距负例纳入回归。

138项回归0失败/0跳过，N0009_v18自动0错误；查看全部10个卡片页联系表与问题页320/440手机截图。原声/原文/时间戳字节不变，原版本保留。证据artifacts/card-spacing-20261028/summary.json。未修改共享运行时或生产授权，未代填独立批准、听感或桌面导出。
