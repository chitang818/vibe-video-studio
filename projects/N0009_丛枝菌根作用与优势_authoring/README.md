# N0009 制作源数据

最终待复核预览位于同级 N0009_丛枝菌根作用与优势_v4。此前 v1/v2/v3 是本次制作的过程版本，保留不覆盖。

story.json：语义分镜与原词锚点；timeline.txt：统一 timeline 工具提取结果；captions.json：144 组人工语义断句；scene.json：最终细化图解数据；quality-plan.json：同门禁下的制作计划；sfx.json 与 assets/sounds：真实物化音效。

prepare.py 是标准组件起稿的初始制作配方；随后依据真实截图逐项细化的最终数据是 scene.json，精修摘要在 final-refinements.json。重新制作应使用最终 scene.json 和 captions.json 调用固定 builder，不将初稿配方当作最终精修成品。原素材在 Downloads 的输入目录，未修改。
