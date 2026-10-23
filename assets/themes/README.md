# 配色主题库（themes）

> 主题 = 一组 CSS 变量（`:root` 层），**换风格只换变量、不重写结构**。
> 物理样式文件已归档在同目录下的 [themes.css](file:///assets/themes/themes.css)。
> 命名规范：`--bg/--panel/--line/--ink/--dim/--green/--green2/--amber/--cyan/--red`。

## 主题方案

### 1. 深色科技风（Dark Tech，模板默认）
- **基调**：深蓝黑底 + 荧光绿/青色/金色发光
- **适用**：历史起源、菌种分类演进、硬核科技概念、机制流程

### 2. 绿色农科风（Green Farm）
- **基调**：墨绿底 + 叶绿金强调 + 偏暖自然色调
- **适用**：生物防病、促生壮苗、土壤修复、田间施用

### 3. 简约科普风（Clean Science）
- **基调**：米白浅底 + 墨绿/暖金高对比
- **适用**：数据对比卡、比例统计、大众浅显科普

## 使用约定
1. 所有颜色引用走 CSS 变量或 `currentColor`，**严禁硬编码色值**；
2. 深色主题的发光（text-shadow / box-shadow glow）在浅色主题下应减弱或关闭；
3. 需要更换风格时，直接从 [themes.css](file:///assets/themes/themes.css) 复制变量组替换目标 HTML 的 `:root` 即可。
