# 分阶段网页视频制作

当前默认创作入口为`vibe pipeline`，模式web-video-v1。原story v1/v2、compile及历史工程继续支持；六种版式仍可维护旧稿，不是新制作的上限。先运行context，读取总Skill和本阶段Skill。

## 契约与能力

scripts/pipeline_contracts.py是严格输入Schema源，可用其SCHEMAS生成JSON Schema查看。Agent负责语义与视觉设计，程序验证/执行，不在CLI里假装内置了LLM导演。缺输入阻断，不调用关键词分类器或默认矩形卡片代替。

输入是WAV、原文、字时间戳；识别与原文语义/数字不一致时intake保存alignment.json并阻断，保持原件，当前不提供自动纠错模型。标点/空格差异单独显示。sources保留原始字节。未来可显式增加对齐映射，当前缺失映射不能继续。

```powershell
python vibe.py pipeline capabilities
python vibe.py pipeline intake projects/<新作者目录> --script script.txt --voice voice.wav --timestamps timestamps.json --style style.json --captions captions.json
python vibe.py pipeline segment projects/<作者目录> --input shots.json
python vibe.py pipeline direct projects/<作者目录> --input briefs.json
python vibe.py asset-import --root projects/<作者目录> --source image.png --id subject --kind local --origin 用户素材 --license user-provided
python vibe.py pipeline produce projects/<作者目录> --input implementation.json
python vibe.py pipeline produce projects/<作者目录> --shot shot-five
python vibe.py pipeline assemble projects/<作者目录>
python vibe.py pipeline review projects/<作者目录>
python vibe.py pipeline inspect projects/<作者目录>
python vibe.py pipeline run projects/<作者目录> --from produce
python vibe.py pipeline refresh projects/<作者目录>
python vibe.py pipeline compare projects/<作者目录> --left runs/<旧阶段>/result.json --right runs/<新阶段>/result.json
```

`run`仅复用ready阶段或使用已提交请求重跑；不会自行生成缺失创作稿。produce --shot只制作指定镜头、复用其余有效镜头；存在缺失/stale镜头时全片组装阻断，不能把局部成功当整片完成。命令加锁，产物保存在新run目录，失败记录failure.json并保留其他镜头。改工具、风格、原件、输入稿或产物后inspect显示stale；不得只改状态绕过依赖。过程页面为只读，不含编辑后端。

## 风格与分镜

工具或sources发生变化后，用refresh重新核验已有原件，或run --from intake从头恢复；不会覆盖sources原件。

style：version=1、title、authorId、backgroundPreset、protectedTerms，可选titleLines。背景来自固定模板库，solid仅显式选择；顶部标题、字幕安全区、HUD和控件保留。

shots：version=1、shots数组。每镜id、startIndex（包含）、endIndex（不包含）、goal、relation、reason、beats。index指原始timestamps行，非原文字节偏移。relation可选focus/parallel/contrast/cause/sequence/spatial/summary。beats逐项index、quote、purpose。所有镜头恰好覆盖原始记录，原音时间连续；首镜从0开始，末镜延续到物理音频结束。重复词用行索引明确身份；quote仍真实匹配。保护术语和ASCII数字不可从中切开。4–20秒是编排提示，新Profile另保留1–120秒物理预算、20秒事件间隔硬上限；不能将建议范围当语义拆镜算法。

## 视觉说明与单镜头

briefs：version=1、briefs数组。逐项shotId、focus、composition、rationale、opening、development、ending、continuity、constraints、assetRequests、sketch。sketch是slot/label/form(text/image/shape)结构草图，非最终素材；direct生成SVG关键帧，先看构图再投入素材。视觉说明扩展画面表达，不编造事实/数字或改口播。全片统一风格，允许局部构图与重点变化，不机械轮换模板。

implementation：version=1、scenes数组。逐项shotId、reason、family、elements。每个元素id、kind、slot、index、entrance，按类型提供text/assetId/tone/emphasis。kind=text/panel/image/arrow；slot及实际能力见capabilities。可组合文字主视觉、两侧关系、序列、图文分层等，不能填写任意脚本/CSS/坐标。family描述真实构图，程序根据实际结构给重复提示而不强制平均使用组件。空间不够须拆镜/重设计，不缩到最低字号或截断。

素材来源、格式和呈现方式独立选择，同镜头可混合。本地、搜图、生成工具取得素材后统一asset-import；外部工具/费用/上传授权按所在Agent环境，不宣称CLI内置服务。透明PNG/WebP保留alpha；SVG静态子集栅格化为PNG，原SVG及hash留存。子集禁止script、外链、foreignObject、滤镜/样式和SVG文字，文字用原生节点保证字形。整张SVG移动不是内部元素动画；内部动画需分层导入/拆原生节点。导入后检查解码、分辨率、透明边缘、裁切、真实来源/许可。

produce生成独立HTML、截取原声及来源偏移、场景JSON、关键帧和确定性seek采样结果。该采样是技术检查，不是独立视觉/听感批准。assemble复用同一scene数据、图片和共享运行时，不拼iframe或重复执行导演逻辑；整片原声仍用完整原件。production-provenance.json进入资产哈希，保留制作来源。

## 分层检查与交付

单镜预览是局部播放窗口：声音截取原声，画面仍按原全局时间绘制背景、字幕和场景转场，记录originUs；不会将背景时钟重置为0。用像素比较核对单镜局部时刻与整片对应时刻。

不以“场景有动静”判断好看；核对表达关系、视觉层级、全片重复与节奏。技术保留原文/数字/字幕保真、字形、真实边界/间距、背景、声音、手机320/440、暂停/跳转/重播和产物哈希。检查各动效与转场起点/中段/终点；静态阅读允许，装饰不代替信息。

review执行现有完整门禁，新Profile允许组合构图；自动0错误仍是needs_review。逐镜语义、素材适切性、审美与听感须有实际观察；未执行则pending。独立受信凭证和pack正式发布边界保持，不创建制作Agent自信任密钥，不改WeMediaForge发布行为。
