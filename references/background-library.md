# 固定背景模板库

普通制作只选择背景，不改算法、配方或页面脚本。五款动态模板及显式纯色保留；默认农科使用bio-bubbles。源代码各自独立，成片仍使用同一份自包含scene.mjs。

## 使用

```powershell
python vibe.py backgrounds
python vibe.py backgrounds --check
python vibe.py backgrounds --audit
python vibe.py backgrounds --gallery --out previews/background-library-v2
```

`bg`是生成当前画廊的兼容入口，不再打开历史DOM背景库。画廊支持切换模板、叠加/隐藏标准标题卡片与字幕示例、播放/暂停、拖动与重置时间；不允许即时修改配方。整个页面内联运行时和目录，file://不请求外链。

故事使用：

```json
{"backgroundPreset":"bio-bubbles"}
```

可选`backgroundTemplateVersion`指定当前可用版本；不支持的版本直接报错。编译器将实际`templateVersion`及`recipeSha256`写入scene.background，固定模板、预览和导出共同消费；未知配方参数不是扩展点。旧网页保留其内联渲染器，当前模板调整不会改写历史作品。

| 模板 | 默认版本 | 题材 | 自身检查形态 |
|---|---|---|---|
| bio-bubbles | 1.0.0 | 农业、生物、微生物 | 4×6全画布分区，至少20区可见 |
| constellation | 1.0.0 | AI、计算机、技术 | 四象限分布、节点/连线可见及运动 |
| dna-spiral | 1.0.0 | 遗传、基因、生命科学 | 纵向六段及左右两链区域可见 |
| cyber-grid | 1.0.0 | 工业、制造、芯片 | 下部透视网格与上部柔光区域 |
| aurora-dust | 1.0.0 | 历史、宇宙、商业 | 四象限柔光/星尘及实际运动 |
| solid | 1.0.0 | 明确要求纯色 | 不要求动态 |

数字阈值只维护在共享目录的catalog.json各模板qa配方；不能用光斑的全屏分布要求判定螺旋柱，也不能以metadata名称替代实际renderAt像素检查。亮度和文字叠加仍需看图复核，自动检查不证明审美或科学语义。

## 源码与构建

上游`WeMediaForge/src/WeMediaForge/Assets/VibeRuntime/`拥有开发源码：

- `backgrounds/<预设>.mjs`：五款独立绘制函数，统一接收ctx、时间/尺寸/seed上下文及固定recipe。
- `backgrounds/common.mjs`：确定性随机流、时间和柔光原语。
- `backgrounds/catalog.json`：标签、题材、固定数值/颜色及各款检查区域。
- `backgrounds/versions.lock.json`：模板ID@版本对应配方、模块、公共原语和QA指纹。
- `scene-core.mjs`、`build_runtime.py`：统一构建为scene.mjs，浏览器不加载源模块或JSON。

Studio在assets/runtime镜像同一组开发源码；应用发布及作品只消费生成运行时，不附带开发模块的加载请求。JSON/MJS/Python源码固定LF，避免Git换行转换使源指纹失效。

维护步骤：修改上游独立模块/配方 → 新增模板版本与版本锁（不覆盖旧版本记录） → 同步提升运行时版本 → `python <上游运行时>/build_runtime.py`生成 → 更新实际运行时SHA与兼容版本 → 同步两端 → 运行`backgrounds --check`、像素基线、模块专项、画廊与生产/消费回归。原文件变化后需重新审核，不复用凭证。

普通制作不执行上述维护，不改单端镜像、不伪造SHA。校验发现源/生成物不一致、版本锁不匹配或未知模板/版本时停止，不自动退回其他背景。

## 本轮视觉基线

模板库1.0.0从runtime1.1.2的已交付效果拆分；五款×两种seed×四个时间点，共40组画面逐像素一致。冻结回归样本只用于测试，不作为可编辑的生产源码。变更视觉效果需要升版并重新查看背景本身和叠加内容，不能默默更新基准图来消除差异。

`--audit --out <新目录>`独立运行六款模板的区域、运动、真实文字缓存、反复seek与手机画廊检查，保存背景/叠加文字在0/4/15秒截图。报告automated_pass仅代表工具检查，不是独立审美批准。
