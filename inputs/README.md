# 素材输入目录（inputs）

- 每套作品一个子目录：`inputs/N000X/`，放三件套：
  - `script.txt`（文案，UTF-8）
  - `voice.wav`（配音，WAV 单声道即可）
  - `char_timestamps.json`（字级时间戳：每字含 StartSeconds/EndSeconds/DurationSeconds/IsVadBoundary）
- **可选 `manifest.txt`**（特殊风格覆盖，普通套数不需要）：
  ```
  模板=绿色农科风
  配色=green-farm
  音效=轻快
  顶部显示=否        # 默认显示
  ```
  不写 = 按 RULES §6 决策表由 AI 自动选择。
- 素材也可放任意路径（如桌面），对话时告知 AI 三件套路径即可，不强制拷入本目录。
- 命名规范：`inputs/作品编号_作品名称/`（如 `inputs/N0004_贝莱斯芽孢杆菌的产业化之路/`）。
