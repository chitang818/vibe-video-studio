# 背景模板库（当前入口）

五种动态背景已独立为共享运行时的backgrounds/*.mjs模块，固定配方、题材和检查区域在catalog.json，版本锁在versions.lock.json；普通制作不要修改这些源码。

- `python vibe.py backgrounds` 查看当前模板。
- `python vibe.py backgrounds --check` 检查生成运行时与源模块一致。
- `python vibe.py backgrounds --gallery` 生成自包含画廊，单独看背景或叠加标准文字。
- story只填backgroundPreset，编译器绑定版本与配方指纹。

详见[背景模板库](../../../../../references/background-library.md)。同目录backgrounds.js保留历史DOM/rAF实现，不作为新工程执行代码；当前画廊与导出消费同一时间确定性Canvas运行时。
