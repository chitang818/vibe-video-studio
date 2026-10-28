# 高速 Canvas 工程协议与制作边界

当前共享运行时为 protocol-1 / runtime-1.2.0；镜像不允许在 Studio 单端修改。新制作流程见 [质量契约](quality-contract.md)，数值以 [正式 Profile](quality-profile.json) 为准。旧 DOM/CSS 截图导出与 pack 就绪判断不适用。

- 原文案、配音和字时间戳保留原件。场景/节点/音效事件从原字锚定；时间统一整数微秒；场景连续覆盖完整 WAV 帧时长。
- 当前运行时节点为 text/rect/image/ring/bar/path。绘制按时间确定，随机固定 seed，字体与资源预先准备；不添加 DOM 动画、独立计时器或自定义执行脚本。
- 主体在横向 8%..92%、纵向 10%..78%，字幕在 82% 高度；所有 path 实际像素必须位于声明框。字框通过真实浏览器测量，不代表图形语义已合格。
- 图片与音效 source 必须是工程内登记哈希的相对路径；不使用外链/链接素材；图表 value/toValue 在 0..1，显示值/单位须有原文依据。
- sfx.json 为 version=1、events；每项 timeUs/source/gain，真实 WAV 存在、gain 在 0..2。旧配方转换必须物化采样，不在正式导出阶段补造缺失音效。
- 清单保持原 schemaVersion=1。原脚本使用固定 assets/script.txt 并登记 assetHashes，不给旧消费端增加未知必需字段。HTML 由完整固定模板生成，内嵌相同配音字节及数据，保持 file:// 播放。

优先编译结构化故事：

```powershell
python vibe.py context
python vibe.py compile --story story.json --voice voice.wav --timestamps timestamps.json --script script.txt --caption-groups captions.json --out projects/<新版本>
python vibe.py audit projects/<新版本>
# 真实看图听音并独立签发后
python vibe.py pack projects/<新版本> --out releases/<新版本>
```

复杂图解可使用 fast-build，但只产生技术预检草稿；必须按同一 Schema/Profile 补齐计划、自动检查和独立审核。工程目录和输出版本必须尚不存在，历史作品不覆盖。

发布目录包含 vibe.project.json、scene.json、index.html、vibe-runtime、assets、sfx.json、quality-plan、quality-review、release.attestation 和 quality-evidence。哈希/签名绑定实际内容；正式打包不接受自报 passed。

正式 MP4 在 WeMediaForge 网页处理页面导出。消费端已按用户授权接入[凭证验证](../integrations/WeMediaForge/README.md)，草稿预览保留；真实桌面导出仍未验收。共享运行时由上游维护；后续同步不得覆盖 Studio 制作层扩展，必须重新跑生产/消费契约测试。支持的导出帧率仍为 20/30/60 FPS；具体硬件编码器由浏览器实现。


制作校对分镜HUD已在固定网页模板3恢复：第X/N节在左上角显示，仅预览叠层，不烧录到Canvas导出。titleMode与titleLines是Studio场景/故事制作参数，不给protocol-1清单新增未知字段；导出仍消费已编译的真实节点。规则逐项去向见[迁移清单](rule-migration.md)。


文字绘制修复（runtime-1.0.1 / 模板4）：离屏文字缓存用alphabetic基线与actualBoundingBox度量安排四边2px安全留白，按完整字形检查宽高。按字素簇换行，字幕使用同样基线原则。QA从真实缓存读取像素，与带额外留白的独立绘制逐像素核对，发现缺笔画即TEXT_CLIP失败，不只估算行高。

共享内核修复须先维护上游源、升级版本与实际SHA256，再同步Studio镜像并做回归；普通制作不能单改镜像。同步脚本只同步运行时，不覆盖Studio的编译器/模板/门禁扩展。旧工程不覆盖，旧HTML仍可原样打开；导出端当前只接受新版本与新指纹，需生成新工程。

固定模板5提供完整进度/时间/播放控件，独立预留页面空间，不遮挡Canvas，也不烧录到成片；无需修改共享渲染内核或启动桌面软件。


## 动态PPT默认制作模式（2026-10-27）

新制作使用story v2与presentation-portrait-v1，保留v1故事旧语义。六类版式、固定主题、图片适配、入场/强调/转场和三种素材统一导入见[制作入口](presentation-authoring.md)。允许文字主视觉与阅读停留，不以每两秒运动或强制机制图验收；原件/数字、字形/字幕、安全区、声音与签名边界保留。共享运行时1.1.0由上游同步，固定模板6内联原始图片字节；历史作品不改写，当前消费兼容性升级不代表真实WinUI导出验收。


1.1.1：background.preset提供五种实际动态风格与显式solid；text.verticalAlign支持center/top，legacy默认top。转场采用切点前退出/切点后进入，避免重影；layoutAt与绘制共用转场位移。原帧计数/随机状态版背景只作视觉参考，不复制其计时机制。


2026-10-28背景全屏覆盖修复（runtime1.1.2）：独立坐标随机流及三层分层网格抖动，修复光斑斜向聚集。bio-bubbles按4列×6行采样，多个时间点至少20/24区达到16个可见像素（270×480缩图），不只检查全局有运动。正文不变，历史网页保留。


runtime1.2.0：背景源码独立模块与版本锁定配方，构建时内联为单个scene.mjs，网页和导出不加载模块文件。scene.background绑定templateVersion/recipeSha256；上游build_runtime.py生成并更新真实身份，同步脚本校验源/生成物一致后同步开发源和运行时。应用发布排除开发模块，作品仅需生成运行时。
