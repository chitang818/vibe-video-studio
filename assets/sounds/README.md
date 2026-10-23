# 音效库（sounds）

> 音效不依赖外部大体积素材文件：`scripts/mux.py` 内置 **FFmpeg 合成配方**（零体积、随时可生成）。
> 成片必须有人声外的独立音效轨：转场 whoosh、数字强调 pop、结尾 chime，按时间戳拼接后 amix 混入（默认 volume=0.35）。
> 物理配置文件详见同目录下的 [sfx_presets.json](file:///assets/sounds/sfx_presets.json)。

## 合成配方速查

| 音效 | 机制 | 默认参数 | 用途 |
|---|---|---|---|
| **pop** | `sine=frequency=880:duration=0.15` + 极速淡入淡出 | 880Hz / 0.15s | 关键数字、核心词条、重音强调 |
| **whoosh** | `anoisesrc=color=pink:duration=0.45` + lowpass 2600 | 0.45s 软起软落 | 场景切换 / 转场 |
| **chime** | 659 + 880 + 1318 Hz 三音 amix + 结尾淡出 | 1.0s 大三和弦 | 结尾提示 / 收束 CTA |

## 音效点选取规则（从字级时间戳精确读取，严禁拍脑袋估算）
- **whoosh**：每个场景边界（SCENES 列表中各个场景切换的精确时刻）；
- **pop**：文案中关键数字、百分比、年份首次发音的时刻；
- **chime**：结尾 CTA 弹入时刻（或最后一句播完前 3~9 秒）。

## 命令行调用
```bash
python scripts/mux.py <帧目录> <人声wav> <输出mp4> <时长秒> [sfx.json]
```
`sfx.json` 格式：
```json
{"whoosh": [26.66, 58.39], "pop": [48.63, 162.47], "chime": [305.0]}
```
缺省音效表时，`mux.py` 会自动在结尾放一个 chime（总时长 - 9s 处）。
