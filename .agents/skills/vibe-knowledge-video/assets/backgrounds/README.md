# VIBE 视频背景粒子动效预设库 (VibeBackgrounds)

> **定位**：专为抖音 9:16（1080×1920）竖屏知识视频打造的 5 款模块化原生 Canvas 背景动效引擎，支持零外部依赖即插即用、秒级换肤。

---

## 1. 五大预设风格决策表

| 预设标识（ID） | 预设名称 | 视觉特征 | 推荐科普题材 |
| :--- | :--- | :--- | :--- |
| **`bio-bubbles`** | **深海/微生物细胞光斑（默认首选）** | 景深分层（远景微粒+中景柔球+近景呼吸大光斑），向上浮游 | **农业、微生物、植物病理、生物医药** |
| **`constellation`** | **神经元能量网络（高能增强版）** | 发光节点、高频连线、能量脉冲光点穿梭 | **AI科技、计算机算法、系统机理、物理** |
| **`dna-spiral`** | **双螺旋基因流光** | 连续旋转上升的双螺旋光柱，伴随闪烁星芒拖尾 | **基因编辑、CRISPR、遗传学、生命科学** |
| **`cyber-grid`** | **赛博透视网格与极光** | 3D 透视向前推进的地平线网格 + 极光能量扩散带 | **工业制造、商业盘点、硬科技、芯片** |
| **`aurora-dust`** | **极光星尘漂移** | 双核柔和极光流转 + 宇宙微尘闪烁 | **宏观历史、深度纪实、高端商业智库** |

---

## 2. 两种极简调用方式

### 方式 A：声明式属性自动挂载（推荐）
在 HTML 的 `<canvas>` 标签上声明 `data-preset`：
```html
<canvas id="bg-canvas" data-preset="bio-bubbles" data-color="#4ade80" data-color2="#38bdf8"></canvas>

<!-- 页面底部引入库即可自动扫描并运行 -->
<script src="../../assets/backgrounds/backgrounds.js"></script>
<script>
  VibeBackgrounds.init();
</script>
```

### 方式 B：JavaScript 动态切换 / 场景联动
```javascript
// 一键切换至双螺旋基因流
VibeBackgrounds.use('bg-canvas', 'dna-spiral', {
  color: '#38bdf8',  // 主色
  color2: '#4ade80', // 辅色
  density: 1.2,      // 粒子密度
  speed: 1.0         // 运动速度
});
```

---

## 3. 本地可视化画廊预览
在终端执行：
```bash
python vibe.py bg
```
或直接双击用浏览器打开 `output/background_gallery.html`，即可在 1080×1920 真实竖屏下实时切换 5 大预设并调试粒子参数！
