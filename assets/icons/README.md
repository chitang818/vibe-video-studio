# 图形库（icons）

> 全部为**内联 SVG**（file:// 禁止外链图片/字体）。
> 统一风格：线性描边、`fill="none" stroke="currentColor"`、`stroke-width="1.8"`、`stroke-linecap="round"`、`stroke-linejoin="round"`、24×24 viewBox。
> 颜色用 CSS 变量/currentColor 继承主题，禁止硬编码色值。

## 已归档通用 SVG 资产文件（20 项）

### 1. 基础与数据
- `chart.svg` —— 柱状/图表（数据/增产/对比）
- `check.svg` —— 对勾/徽章（认证/成功/合规）
- `play.svg` —— 播放三角（按钮/启动）
- `clock.svg` —— 时钟（时间/时效/周期）
- `zap.svg` —— 能量闪电（激活/高效/催化）

### 2. 生化与科研
- `shield.svg` —— 盾牌（防御/防病/保护）
- `sprout.svg` —— 幼苗/发芽（促生/农业/生长）
- `dna.svg` —— DNA 双螺旋（基因/遗传/品种）
- `bacteria.svg` —— 细菌/杆菌体（益生菌/微生物）
- `virus.svg` —— 病毒/病原体（病害/靶向杀灭）
- `flask.svg` —— 化学烧杯（次级代谢产物/生化反应）
- `microscope.svg` —— 显微镜（科研/微观机理）
- `target.svg` —— 靶心（靶向作用/精准机制）
- `alert.svg` —— 警告三角（病害痛点/预警）
- `factory.svg` —— 代谢工厂（天然抗生素合成中心）

### 3. 互动与收束（CTA 四维引导）
- `heart.svg` —— 点赞（互动/认可）
- `user-plus.svg` —— 关注（长效留存）
- `star.svg` —— 收藏（干货价值）
- `message.svg` —— 评论（话题讨论）
- `share.svg` —— 分享/转发（社交裂变）

## 使用方式
1. 直接用文本编辑器打开本目录下的 `.svg` 文件，复制其 `<svg>...</svg>` 代码粘贴进 HTML 场景中；
2. 概念图标保持统一笔触（stroke-width 1.8，圆头端点），不混用粗细；
3. 大尺寸复杂图（如长杆菌体 120×66）允许更细笔触与多元素组合，但仍用 currentColor + 主题色；
4. 图标可配描边动画：`stroke-dasharray` + `stroke-dashoffset` 过渡画线。
