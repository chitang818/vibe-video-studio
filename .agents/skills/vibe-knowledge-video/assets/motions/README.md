> 历史DOM/CSS资产；默认story v2不加载这些执行文件。当前主题/动效由编译器与共享Canvas实现，见[制作入口](../../../../../references/presentation-authoring.md)。不要直接复制到新网页。

# 动效库（motions）

> 动效是 **CSS keyframes / JS 片段**（不是图片视频）。
> 物理代码文件已归档在同目录下的 [motions.css](file:///assets/motions/motions.css)。
> 使用约定：同屏循环动效 ≤2 种；转场/入场一次性；关键数字用持续强调；动效不遮挡文字。

## 动效清单

| 分类 | 名称 | 效果说明 | 用法示例 |
|---|---|---|---|
| **入场类** | `wIn` | 上浮淡入（波次入场默认） | `animation: wIn .5s cubic-bezier(.22,1,.36,1) both;` |
| | `punchIn` | 大字弹入（开场钩子/标题） | `animation: punchIn .7s cubic-bezier(.22,1,.36,1) both;` |
| | `fadeUp` | 轻上移淡入（标签/副题） | `animation: fadeUp .45s ease both;` |
| | `pcardIn` | 卡片弹入（网格/数据卡） | `animation: pcardIn .5s ease both;` |
| | `ctaIn` | CTA 弹入 | `animation: ctaIn .5s cubic-bezier(.22,1,.36,1) both;` |
| | `barGrow` | 横条/进度条生长 | `animation: barGrow 1s ease both;` |
| **持续强调** | `breathe` | 呼吸缩放（关键数字/词条） | `animation: breathe 2s ease-in-out infinite;` |
| | `ctaPulse` | 结尾 CTA 脉冲 | `animation: ctaPulse 1.4s ease-in-out infinite;` |
| | `colonyPulse` | 圆点/菌落扩散脉冲 | `animation: colonyPulse 1.6s ease-in-out infinite;` |
| | `arrPulse` | 箭头/指示器脉冲 | `animation: arrPulse 1.2s ease-in-out infinite;` |
| **氛围类** | `floatY` | 主图形上下轻浮动 | `animation: floatY 3.2s ease-in-out infinite;` |
| | `slideX` | 水平滑动 | `animation: slideX 2.6s ease-in-out infinite;` |
| | `scanSpin` | 旋转扫描环 | `animation: scanSpin 6s linear infinite;` |
| | `shimmerX` | 标题流光扫过 | 伪元素 `animation: shimmerX 2.8s ease-in-out infinite;` |
| **转场类** | `flashAnim` | 场景切换闪光 | 全屏 overlay，`animation: flashAnim .4s ease-out both;` |

## 快速使用
在 HTML 中需要引入新动效时，可直接从 [motions.css](file:///assets/motions/motions.css) 中复制对应的 `@keyframes` 规则内联至页面 `<style>` 中。
