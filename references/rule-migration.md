# DOM → Canvas 规则保留清单

本表核对规则是否有去向，不代表全部视觉能力已实现。基线为原版规则、旧 skeleton、checklist、technical-details、prompt-template 和 audit。[原规则快照](../artifacts/rule-migration-20261027/legacy-rules.md)及[Git/SHA256记录](../artifacts/rule-migration-20261027/baseline.json)可追溯。现行数值只认Profile；当前默认presentation Profile version=5、模板=6、编译组件=5；旧knowledge Profile version=4保留历史模式要求。

| 原要求 | 对照结果与处理 | 执行/验证位置 |
|---|---|---|
| 非AI文生视频、原声与原字驱动 | 保留，Canvas替代逐帧截图 | fast-project、builder、quality_gate |
| 字时间切点/入场/音效，不估算 | 保留整数微秒与原词身份 | text_contract、quality_gate |
| 全数据内联、无外链、本地播放 | 保留并加强，原声也内嵌 | preview_template、quality_browser |
| 左上角制作分镜HUD | 迁移遗漏，已恢复第X/N节；播放、前后seek和重播同步 | 模板3、HUD切点/手机检查 |
| HUD与主标题分开 | 恢复唯一例外；仅预览校对UI，不写入Canvas，不声称导出端烧录 | R4、质量契约 |
| 用户可关闭顶部且不留空区 | 迁移遗漏，已恢复titleMode=hidden，删除标题/底板并上移中区 | Schema、components、preservation |
| 长标题显式语义两行，无孤字 | 此前仅文档要求，现落实titleLines、完整身份和真实自动折行检查 | components、preservation、quality_browser |
| 作品标题区别于系列名/分镜标签 | 保留并加强，与清单作品名一致 | preservation.scene_checks |
| 标题渐变、光晕、磨砂 | 旧规则有要求，共享运行时仍有能力缺口；恢复明确记录，不以样式名称冒充实现 | R7、实际视觉复核，未改单端运行时镜像 |
| 四边安全区与三区 | 保留；旧资料51%/54%、5%/6%冲突，统一中区≤54%、净空≥6% | Profile、geometry |
| 环心纯数字、20px净空、字号5.2%–5.8% | 细节遗漏，已补检查；intentionalOverlaps不能豁免净空 | preservation、圆环负例 |
| 柱值/图数分区，不穿透 | 保留，不因角色被批量豁免 | quality_browser碰撞检查 |
| 竖屏纵向优先、术语不拆、图文主次 | R3/R4/R6保留，几何可查，意群和布局适切性需实际复核 | 字号/保护词/逐场观察 |
| 正文≤2行与多项纵向卡片 | 旧资料有冲突；原则保留两行讲解，分类/清单需精炼并逐场手机复核；不把四条文字自动认作图解合格 | R3、独立visual/mobile复核 |
| 6–14秒、3–4秒节拍、2秒静止 | 保留并加强，剔除字幕背景做像素运动采样，呼吸不是新信息 | static_checks、MOTION |
| 原稿决定开场，不强套回顾 | 短规则缺显式限制，已恢复；首推进≤1秒、第二次≤4秒，回顾须有原文依据 | R2、OPENING/HOOK |
| 2–3波入场、同屏循环≤2 | 入场保留；循环数量检查已补，错峰不能捏造原字时间 | R2、preservation |
| 可感知转场、旧场淡出/闪光/缩放 | 确定性新节点入场已实现；完整旧场跨镜淡出、flash/缩放未等价移植，不能宣称全部恢复 | R2、实际转场复核和能力缺口 |
| 图形化主视觉，不能整片换字 | 保留并加强图形重复/透明/空路径/低对比检测 | quality_gate、quality_browser |
| 官方5类背景、学科匹配 | 曾弱化为参考，已恢复制作目标与能力缺口；runtime1.1.1已恢复五种确定性视觉预设，背景实际像素运动单独检查；自填名称仍不算实现 | R7、backgroundQuality独立复核 |
| 原稿决定结尾，CTA有动作 | 保留；没有CTA不能加口播，有CTA需真实动作 | R9、ending逐项复核 |
| 音效白名单/限频/自动绑定 | 限频已存在；补未知名拒绝、每切点whoosh、末镜chime、越尾阻断；compile生成真实ding并选完整尾音锚点 | preservation.sound_checks、compile |
| 人声主导、低通暖化 | 配方低通与网页增益保留；外部素材频谱及主观听感未被完全自动证明 | preset_wave、PCM、soundMix待听音 |
| 数字/单位/术语原样 | 保留并加强十进制/单位边界；原稿术语疑点先确认，不能只改画面 | FACT/CAPTION/SOURCE |
| 暂停和重播清残留 | Canvas没有DOM active，但语义必须保留；已增真实暂停/结束/重播检查 | PLAYER/HUD |
| 编号名称文件、连字符ID | ID保留；明确迁移为固定index.html，编号名称在目录/清单/网页标签 | manifest、网页title、Schema |
| 自动修复、不能凭exit code交付 | 保留并区分自动与独立批准，needs_review不是正式通过 | quality_gate、reviewer、release |
| 自包含、缓存隔离、旧作不覆盖 | 保留；旧inputs/output/_work为废止路径，不回退破坏作品 | AGENTS、pack、clean |
| 预览/导出同步、MP4规格验证 | 素材和镜像指纹保留；实际MP4帧率/音轨/解码/WinUI需消费端验证，Studio不冒认验收 | ConsumerContract、消费端实际验收 |

后续迁移必须逐项更新本表。能自动证明的要求进入Schema/Profile/门禁并加负例；科学语义、视觉审美和听感保留具体观察。能力缺口不能以覆盖文档或填写模板名称掩盖；代码/规则变化后重新audit、复核与签发。LEGACY只标识旧执行路径，不表示可丢业务要求。


字形完整性补充：runtime-1.0.1与模板4修复top基线削顶，采用真实字形边界、2px缓存留白、字素簇换行；新增真实缓存与额外留白参考的像素检查(TEXT_CLIP)。真实字形取代仅靠估算行高的旧检查。修复从共享源同步，普通制作不得单改镜像。

播放器完整性补充：此前只验证内部seek和播放状态，遗漏底部可见进度条。模板5补进度拖动与时间显示，QA验证暂停/播放中拖动、Home/End、手机不越界和不覆盖Canvas。不能以存在内部接口代替可见控件。


## 动态PPT默认制作模式（2026-10-27）

新制作使用story v2与presentation-portrait-v1，保留v1故事旧语义。六类版式、固定主题、图片适配、入场/强调/转场和三种素材统一导入见[制作入口](presentation-authoring.md)。允许文字主视觉与阅读停留，不以每两秒运动或强制机制图验收；原件/数字、字形/字幕、安全区、声音与签名边界保留。共享运行时1.1.0由上游同步，固定模板6内联原始图片字节；历史作品不改写，当前消费兼容性升级不代表真实WinUI导出验收。


2026-10-28纠偏：动态PPT重构曾误将背景默认纯色、文字默认左对齐，违背原有视觉要求。runtime1.1.1恢复五种题材背景，编译器4默认真实水平/垂直居中；旧页切点前退出、新页切点后进入，无双页文字重影。旧素材/网页不覆盖。

背景覆盖进一步修复：旧seeded横纵坐标相关导致斜线聚集；1.1.2改独立随机流和分层全画布分布，增加多时间/多种子空间覆盖检查，保存旧实现负例。

背景库模块化：runtime1.2.0独立五款源码及配方/版本锁，编译绑定模板版本与配方SHA，40组画面与1.1.2基线逐像素一致。默认视觉不变；画廊和成片共享生成物，开发模块不随作品加载。
# 卡片净空补充（2026-10-28）

原检查只拦重叠，四项步距174px减170px底板只剩4px，手机上粘连。presentation Profile v5新增cardSpacing，编译器按底板高度+56px默认净空布局；静态和动效采样不足32px均由CARD_SPACING阻断。底板内文字/步骤标记仍是正常包含关系，不覆盖旧作品。

