# 跨 Agent 制作与正式发布契约（v2）

本文件替代此前将可编辑 passed JSON 视作正式批准的流程。[制作规则](../.agents/rules/vibe-rules.md)定义内容要求，[机器 Profile](quality-profile.json)定义可执行阈值，[高速协议](fast-project.md)定义运行时兼容性。

## 固定生产链路

1. `python vibe.py context` 输出当前 Profile、组件和必读资料；按用户已选模式工作。
2. 核对原文案、原 WAV、原字时间戳。小数点、数字、单位不得在归一化时丢失；重复原词用 occurrence 明确第几次，不能把前面的标点当作词首。
3. 优先编写 story.json，使用 `compile` 将受限内容参数编译为节点和计划。Agent 不编写播放器、CSS 或网页执行代码。特殊图解可使用严格 schema 下的原始 scene.json，但须满足同样检查。
4. `audit/check/qa` 校验严格 Schema、Profile、资产、完整固定 HTML、字号、分镜、实际矢量、可见性、节奏和声音等。未经规范的数据不会进入浏览器执行。旧网页须显式 --legacy；不产生正式就绪身份。
5. 自动通过状态为 needs_review，退出码 0 仅代表自动阶段通过；失败状态 blocked，退出码 1。模板、数据或代码修改后重新审查。
6. 实际看图、核对原文与配音并听音后填写 quality-review.json。生成者自检记录不等于独立批准。
7. 独立受信审核者使用外部保管的密钥签发 release.attestation.json；签发入口会重新运行自动检查、核对当前复核和证据。正常制作 Agent 不生成密钥、不配置自己的公钥为受信、不代填独立批准。
8. `pack` 校验独立签名后输出尚不存在的新发布目录，包含资产、计划、复核、凭证和证据；只读输入快照、运行锁、runId 和原子提升防止检查中途修改/覆盖。目录不覆盖旧版本；文件变更会使签名或哈希失效。

## Schema 与制作 Profile

- story、scene、quality-plan 的发布定义位于 schemas/。当前检查器明确支持这些文件使用的 JSON Schema 关键字，未知字段、未知角色、重复 JSON key、非法 ID、布尔冒充数字和非有限值均拒绝。
- 当前默认Profile为presentation-portrait-v1，旧模式Profile为knowledge-portrait-v1，固定 1080×1920、字号和节拍阈值见 quality-profile.json。协议可支持更多尺寸，但不能因此冒称本 Profile 达标。无声工程目前仅支持技术草稿，专用正式无声 Profile 尚未实现。
- quality-plan version=1，必须声明 profile、authorId、background、facts 和逐场 scenes。roles 只能是 title/content/graphic/panel，每节点恰好一次；panel 必须是真正位于内容后方的 rect。
- beat 的绝对 timeUs/quote 必须对应原字并触发实际节点；不把粒子当信息。检查声明动效之外，还对无背景/无字幕的内容区做 0.5 秒像素采样。采样不等于全帧证明，语义仍须复核。
- intentionalOverlaps 只允许受控 ring-number 设计，必须两节点、理由及 design；不能通过任意角色或批量排除绕过检查。
- presentation独立内容底板按Profile.cardSpacing检查净空；CARD_SPACING同时检查终态和共享渲染器layoutAt返回的动画边界，不能以没有交叠或改节点名称放行相连卡片。
- facts 为含数字的文字节点提供 sceneId、nodeId、text、quote、timeUs。数字与单位须来自该原词；摄氏度/℃/°C 使用明确等价映射，不把 1.5 与 15 视作相同。
- visualFamily 声明之外，还检查实际主图形结构重复。透明、空图形、过小图形和低对比度不能作为主视觉。语义准确性不由相似度独自决定。

## 字幕与声音

`--caption-groups` 接受语义分组字符串数组，字时间来自原件。保留数值小数点、内部标点和句末标点，只去掉组尾断句标点；不能拆开数值、ASCII 标识和保护术语。与原稿/原时间戳不一致时直接报告，不静默修正原件。

原文案固定归档为 assets/script.txt 并登记哈希，避免给原高速清单添加导出端不认识的字段。兼容旧的 scriptFile 扩展只用于诊断/迁移。原声在 HTML 内嵌为同一 WAV 的字节；共享运行时保持原样。

浏览器检查播放时钟、声源与混音输出信号；完整 PCM 资产另有按秒 RMS/峰值统计、静音检测、音效相对响度及潜在削波/越尾提示。信号和统计不等于人耳听感；soundMix 仍需实际复核，缺能力就留 pending。

## 观察记录与受信批准

quality-review.json 保留逐项、逐场具体观察，不能自动填 passed。全局项目为 scientificMeaning/narrationSync/semanticCaptions/visualRhythm/backgroundQuality/mobileReadability/soundMix/ending；每场引用对应 run 的实际截图。记录绑定 inputFingerprint 与 evidenceDigest。

release.attestation.json 使用 version=1 的 RSA-PSS-SHA256 签名（RSA 至少 3072 位，PSS salt 32 字节）。载荷是明确的 UTF-8 JSON 原始字节，包含审核者身份、当前 manifest/计划/复核哈希、输入和证据指纹及 Profile；消费端直接验证签名字节，无需跨语言猜测 JSON 序列化方式。

VIBE_TRUST_STORE 指向工程之外的受控信任配置，格式如下；公钥 keyId 为 SPKI DER 的 SHA256。审核者与 authorId 必须不同。示例不生成密钥也不登记任何生产信任。

```json
{"version":1,"keys":{"<SPKI-SHA256>":{"reviewerId":"independent-reviewer","publicKeyPem":"<RSA PUBLIC KEY PEM>"}}}
```

外部审核流程可以在完成真实复核后运行：

```powershell
python -m scripts.reviewer --project <工程> --private-key <外部保管的审核私钥.pem> --reviewer-id <受信身份>
python vibe.py pack <工程> --out releases/<新版本目录>
```

**信任边界**：路径放在工程外不等于操作系统权限隔离。若生成 Agent 也能读取审核私钥、修改信任配置或控制消费端进程，就不能保证独立性。生产密钥与信任配置应由另一受控身份/独立代理服务/CI 保管；本工具不会自动建立这种外部身份，也不会为方便演示自我授权。

## 证据与环境

artifacts/quality/<工程路径哈希>/runs/<runId>/ 是持久运行证据，普通 clean 不清理它。每个 run 使用独立帧目录，最新 report.json 仅作索引；签发和发布绑定具体截图内容。发布包包含 quality-evidence/index.json，消费端可验证索引与逐张图片哈希。原始输入在审核前复制快照，结束及发布时重新检查，变更则阻塞。

依赖基线锁在 requirements.lock.txt，Python 需要 3.11+（当前已测 3.13）。报告记录浏览器/Playwright/Python/字体指纹。当前共享运行时固定 Microsoft YaHei，因此正式检查需要该字体基线；缺少时明确失败，不能自动接受系统替代字体。没有打包或再分发有版权的系统字体。

## 消费端状态与能力边界

2026-10-27 用户明确授权后，消费端正式导出和工作流已接入受信凭证验证，草稿仍可导入和预览。没有配置签发方会拒绝正式导出；本次不建立生产信任。integrations/WeMediaForge 保留源码契约副本与补丁记录，真实桌面导出尚未验收。

自动检查不证明科学事实、全帧碰撞、人耳听感或真实桌面导出。已签名仅证明指定受信审核者批准了这些确切资产，不证明审核者永不出错。跨 Agent 一致性由受限数据、固定组件、受信构建/验收和契约回归共同提高。


## 规则保留补充（模板3 / Profile version2）

[迁移清单](rule-migration.md)和[当前检查清单](checklist.md)跟踪每项旧业务要求。preview_template负责固定开发校对HUD，显示第X/N节；按真正竖屏容器定位，随播放、切点前后、倒退seek和结束重播更新。HUD是固定DOM校对UI，不写入Canvas，不作为导出成片已有HUD的证明，也不能授权其他正文越界。

story/scene允许titleMode=shown或hidden，默认shown；明确不要顶部时才使用hidden。story允许titleLines两行显式意群，合并后等于原title；长作品名超过12字必须两行，第二行至少4字。隐藏模式必须移除标题/底板并上移内容，不可用metadata掩盖实际节点。标题字区为画高10%–16.5%，文字总高度≤6%，与清单作品名一致、居中，无自动折行和拆术语。

音效只接受五款白名单语义名WAV；每个切点绑定whoosh，末镜完整chime，越尾阻断。原有ding最多3次与pop频率限制继续生效。圆环重叠许可继续只限纯数字，但须满足20px真实内环净空与数字字号要求。新增真实暂停/结束重播检查，原来的重复seek确定性检查不替代播放器状态验证。

共享内核尚未等价移植的官方背景、渐变光晕/磨砂标题和完整跨镜淡出/flash/缩放，是明确能力缺口；自动检查通过不证明这些旧效果已恢复，不能改metadata假装实现。版本和文档变化会使原审核指纹过期，旧作品保留，新版本重新audit。


## 字形完整性（runtime-1.0.1 / 模板4）

正文和标题离屏缓存采用实际字形边界与alphabetic基线，不再在top基线y=0直接绘字。真实缓存通过只读textRaster接口提供像素副本；QA另建额外留白参考，对比完整字形和缓存，越边或缺像素以TEXT_CLIP阻断。缓存宽高不足直接失败，不能用增加元数据高度或换字体掩盖。字素簇保持完整，多行、重音与上下伸笔画有真实浏览器回归。共享修复源与Studio镜像须逐字节相同，版本/指纹一起更新。


## 模板5预览控件

固定模板包含底部播放按钮、可拖动range进度条与当前/总时长；与共享播放器seek、原声音频和HUD共同更新。视频容器预留控件高度，控件不覆盖Canvas/字幕；QA在320×640和440×956检查44px触控范围，真实鼠标点击/拖动、键盘Home/End、暂停与播放状态、进度及声音时钟同步。控件只预览，不进入Canvas成片。


## 动态PPT默认制作模式（2026-10-27）

新制作使用story v2与presentation-portrait-v1，保留v1故事旧语义。六类版式、固定主题、图片适配、入场/强调/转场和三种素材统一导入见[制作入口](presentation-authoring.md)。允许文字主视觉与阅读停留，不以每两秒运动或强制机制图验收；原件/数字、字形/字幕、安全区、声音与签名边界保留。共享运行时1.1.0由上游同步，固定模板6内联原始图片字节；历史作品不改写，当前消费兼容性升级不代表真实WinUI导出验收。


背景/对齐门禁：runtime1.1.1支持五种时间确定性背景，presentation默认bio-bubbles；独立离屏采样通过真实renderAt检查背景可见性及变化，不能用metadata或正文运动替代。文字按真实墨迹检查水平和垂直中心，转场旧页只在切点前退出，不同时合成两页文字。

背景模板库检查：制作/审核前验证源模块与生成物、版本锁及配方身份。各模板固定qa在catalog.json；Profile指定库版本，源码及目录参与输入指纹。动态背景的运动、区域、空间分布分别采样，螺旋不套光斑的全屏要求。画廊自动报告不是正式作品凭证，旧批准不能用于新运行时。
