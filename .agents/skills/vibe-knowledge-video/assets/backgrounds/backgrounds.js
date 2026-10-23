// ========================================================
// VIBE Video Studio · 背景动效粒子预设库 (VibeBackgrounds)
// 5 款专为抖音竖屏 1080x1920 打造的高能、高辨识度背景动效引擎
// 100% 原生 Canvas 2D，零外部依赖，极速渲染
// ========================================================

var VibeBackgrounds = (function () {
  "use strict";

  // 色彩辅助解析
  function parseColor(c, defaultColor) {
    if (!c) return defaultColor || { r: 74, g: 222, b: 128 };
    if (typeof c === "object" && c.r !== undefined) return c;
    if (c.startsWith("#")) {
      var hex = c.replace("#", "");
      if (hex.length === 3) hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
      var num = parseInt(hex, 16);
      return { r: (num >> 16) & 255, g: (num >> 8) & 255, b: num & 255 };
    }
    // 默认绿色
    return { r: 74, g: 222, b: 128 };
  }

  // 1. 预设：深海/微生物浮游细胞光斑 (bio-bubbles) —— 生物、农业、显微科普首选
  function presetBioBubbles(cv, ctx, opt) {
    var W = cv.width, H = cv.height;
    var col = parseColor(opt.color, { r: 74, g: 222, b: 128 });
    var col2 = parseColor(opt.color2, { r: 56, g: 189, b: 248 }); // 辅助微青色
    var count = Math.floor(45 * (opt.density || 1.0));
    var speed = (opt.speed || 1.0);

    var orbs = [];
    for (var i = 0; i < count; i++) {
      var layer = Math.random(); // 景深: 0(远景小微粒) ~ 1(近景大光斑)
      var r = layer < 0.6 ? (Math.random() * 4 + 1.5) : (Math.random() * 26 + 10);
      var isCol2 = Math.random() < 0.35;
      orbs.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: r,
        baseR: r,
        layer: layer,
        color: isCol2 ? col2 : col,
        vy: -(Math.random() * 0.45 + 0.15) * speed * (0.6 + layer * 0.8),
        vx: (Math.random() - 0.5) * 0.25 * speed,
        alpha: layer < 0.6 ? (Math.random() * 0.4 + 0.2) : (Math.random() * 0.18 + 0.08),
        pulseSpeed: Math.random() * 0.03 + 0.015,
        pulseOffset: Math.random() * Math.PI * 2
      });
    }

    var frame = 0;
    return function draw() {
      ctx.clearRect(0, 0, W, H);
      frame++;

      for (var i = 0; i < orbs.length; i++) {
        var o = orbs[i];
        o.y += o.vy;
        o.x += o.vx + Math.sin(frame * 0.018 + o.pulseOffset) * 0.15;
        if (o.y < -o.r * 2) { o.y = H + o.r * 2; o.x = Math.random() * W; }
        if (o.x < -o.r * 2) o.x = W + o.r * 2;
        if (o.x > W + o.r * 2) o.x = -o.r * 2;

        var pulse = Math.sin(frame * o.pulseSpeed + o.pulseOffset) * 0.15 + 1.0;
        var curR = o.baseR * pulse;

        if (o.layer >= 0.6) {
          // 近景大光斑带柔焦径向渐变
          var grad = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, curR);
          var a = o.alpha * pulse;
          grad.addColorStop(0, "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + "," + a + ")");
          grad.addColorStop(0.5, "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + "," + (a * 0.4) + ")");
          grad.addColorStop(1, "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + ", 0)");
          ctx.beginPath();
          ctx.arc(o.x, o.y, curR, 0, Math.PI * 2);
          ctx.fillStyle = grad;
          ctx.fill();
        } else {
          // 远景微粒，清晰实心点
          ctx.beginPath();
          ctx.arc(o.x, o.y, curR, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(" + o.color.r + "," + o.color.g + "," + o.color.b + "," + o.alpha + ")";
          ctx.fill();
        }
      }
    };
  }

  // 2. 预设：科技星芒/神经元能量网 (constellation-v2) —— AI、技术机理、数据连接
  function presetConstellation(cv, ctx, opt) {
    var W = cv.width, H = cv.height;
    var col = parseColor(opt.color, { r: 74, g: 222, b: 128 });
    var count = Math.floor(58 * (opt.density || 1.0));
    var speed = (opt.speed || 1.0);
    var maxDist = 180 * 180;

    var pts = [];
    for (var i = 0; i < count; i++) {
      pts.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 2.8 + 1.2,
        vx: (Math.random() - 0.5) * 0.45 * speed,
        vy: (Math.random() - 0.5) * 0.45 * speed,
        a: Math.random() * 0.45 + 0.3
      });
    }

    // 沿连线流动的能量脉冲小光点
    var pulses = [];
    for (var k = 0; k < 6; k++) {
      pulses.push({ p1: 0, p2: 1, prog: Math.random(), speed: 0.015 * speed });
    }

    var frame = 0;
    return function draw() {
      ctx.clearRect(0, 0, W, H);
      frame++;

      // 更新节点
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;

        // 绘制发光节点
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + col.r + "," + col.g + "," + col.b + "," + p.a + ")";
        ctx.shadowColor = "rgba(" + col.r + "," + col.g + "," + col.b + ", 0.6)";
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // 绘制连线
      var activePairs = [];
      for (var i = 0; i < pts.length; i++) {
        for (var j = i + 1; j < pts.length; j++) {
          var p1 = pts[i], p2 = pts[j];
          var dx = p1.x - p2.x, dy = p1.y - p2.y;
          var d2 = dx * dx + dy * dy;
          if (d2 < maxDist) {
            var alpha = (1 - d2 / maxDist) * 0.22;
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = "rgba(" + col.r + "," + col.g + "," + col.b + "," + alpha + ")";
            ctx.lineWidth = 1.2;
            ctx.stroke();
            if (activePairs.length < 24) activePairs.push([p1, p2]);
          }
        }
      }

      // 能量穿梭光梭
      if (activePairs.length > 0) {
        for (var k = 0; k < pulses.length; k++) {
          var pulse = pulses[k];
          pulse.prog += pulse.speed;
          if (pulse.prog >= 1.0) {
            pulse.prog = 0;
            pulse.pairIdx = Math.floor(Math.random() * activePairs.length);
          }
          var pair = activePairs[pulse.pairIdx % activePairs.length];
          if (pair) {
            var qx = pair[0].x + (pair[1].x - pair[0].x) * pulse.prog;
            var qy = pair[0].y + (pair[1].y - pair[0].y) * pulse.prog;
            ctx.beginPath();
            ctx.arc(qx, qy, 2.2, 0, Math.PI * 2);
            ctx.fillStyle = "#ffffff";
            ctx.shadowColor = "rgba(" + col.r + "," + col.g + "," + col.b + ", 0.9)";
            ctx.shadowBlur = 10;
            ctx.fill();
            ctx.shadowBlur = 0;
          }
        }
      }
    };
  }

  // 3. 预设：螺旋基因流光/双螺旋光尘 (dna-spiral) —— 基因编辑、生化、生命科学
  function presetDnaSpiral(cv, ctx, opt) {
    var W = cv.width, H = cv.height;
    var col = parseColor(opt.color, { r: 56, g: 189, b: 248 }); // 主青色
    var col2 = parseColor(opt.color2, { r: 74, g: 222, b: 128 }); // 辅绿色
    var speed = (opt.speed || 1.0) * 0.022;

    var count = Math.floor(40 * (opt.density || 1.0));
    var sparks = [];
    for (var i = 0; i < count; i++) {
      sparks.push({
        t: (i / count) * Math.PI * 4,
        y: (i / count) * H,
        r: Math.random() * 2.5 + 1.2,
        twinkle: Math.random() * Math.PI * 2
      });
    }

    var frame = 0;
    return function draw() {
      ctx.clearRect(0, 0, W, H);
      frame++;
      var tOffset = frame * speed;
      var cx = W / 2;
      var amplitude = W * 0.28;

      for (var i = 0; i < sparks.length; i++) {
        var s = sparks[i];
        s.y -= 1.4 * (opt.speed || 1.0);
        if (s.y < 0) s.y = H;

        var ang = s.t + tOffset + (s.y / H) * Math.PI * 3;
        var x1 = cx + Math.sin(ang) * amplitude;
        var z1 = Math.cos(ang); // 景深
        var x2 = cx - Math.sin(ang) * amplitude;
        var z2 = -z1;

        // 梯级阶梯横向发光连接线
        if (i % 2 === 0 && Math.abs(z1) < 0.7) {
          ctx.beginPath();
          ctx.moveTo(x1, s.y);
          ctx.lineTo(x2, s.y);
          ctx.strokeStyle = "rgba(148, 163, 184, " + (0.12 * (1 - Math.abs(z1))) + ")";
          ctx.lineWidth = 1;
          ctx.stroke();
        }

        // 双螺旋两翼粒子点
        var alpha1 = (z1 * 0.4 + 0.55);
        var r1 = Math.max(1, s.r * (z1 * 0.35 + 1.0));
        ctx.beginPath();
        ctx.arc(x1, s.y, r1, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + col.r + "," + col.g + "," + col.b + "," + alpha1 + ")";
        ctx.fill();

        var alpha2 = (z2 * 0.4 + 0.55);
        var r2 = Math.max(1, s.r * (z2 * 0.35 + 1.0));
        ctx.beginPath();
        ctx.arc(x2, s.y, r2, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + col2.r + "," + col2.g + "," + col2.b + "," + alpha2 + ")";
        ctx.fill();
      }
    };
  }

  // 4. 预设：赛博透视网格 + 极光光柱 (cyber-grid) —— 工业生产、硬科技、数字盘点
  function presetCyberGrid(cv, ctx, opt) {
    var W = cv.width, H = cv.height;
    var col = parseColor(opt.color, { r: 74, g: 222, b: 128 });
    var horizonY = H * 0.65;
    var speed = (opt.speed || 1.0);

    var gridOffset = 0;
    var stars = [];
    for (var s = 0; s < 30; s++) {
      stars.push({
        x: Math.random() * W,
        y: Math.random() * horizonY,
        r: Math.random() * 1.8 + 0.8,
        a: Math.random() * 0.5 + 0.2
      });
    }

    return function draw() {
      ctx.clearRect(0, 0, W, H);
      gridOffset = (gridOffset + 1.2 * speed) % 50;

      // 上半部极光夜空星芒
      for (var i = 0; i < stars.length; i++) {
        var st = stars[i];
        ctx.beginPath();
        ctx.arc(st.x, st.y, st.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + col.r + "," + col.g + "," + col.b + "," + st.a + ")";
        ctx.fill();
      }

      // 地平线柔光扩散带 (Horizon Glow)
      var glowGrad = ctx.createLinearGradient(0, horizonY - 120, 0, horizonY + 80);
      glowGrad.addColorStop(0, "rgba(" + col.r + "," + col.g + "," + col.b + ", 0)");
      glowGrad.addColorStop(0.6, "rgba(" + col.r + "," + col.g + "," + col.b + ", 0.15)");
      glowGrad.addColorStop(1, "rgba(" + col.r + "," + col.g + "," + col.b + ", 0)");
      ctx.fillStyle = glowGrad;
      ctx.fillRect(0, horizonY - 120, W, 200);

      // 下半部 3D 透视辐射纵向线
      var cx = W / 2;
      ctx.lineWidth = 1;
      var numLines = 14;
      for (var l = -numLines; l <= numLines; l++) {
        var bottomX = cx + l * (W / 10);
        ctx.beginPath();
        ctx.moveTo(cx, horizonY);
        ctx.lineTo(bottomX, H);
        ctx.strokeStyle = "rgba(" + col.r + "," + col.g + "," + col.b + ", 0.12)";
        ctx.stroke();
      }

      // 3D 透视横向向前推进线 (对数深度分布)
      for (var z = 10; z < H - horizonY; z += 35) {
        var curY = horizonY + Math.pow((z + gridOffset) / (H - horizonY), 1.8) * (H - horizonY);
        if (curY > horizonY && curY <= H) {
          var lineAlpha = ((curY - horizonY) / (H - horizonY)) * 0.22;
          ctx.beginPath();
          ctx.moveTo(0, curY);
          ctx.lineTo(W, curY);
          ctx.strokeStyle = "rgba(" + col.r + "," + col.g + "," + col.b + "," + lineAlpha + ")";
          ctx.stroke();
        }
      }
    };
  }

  // 5. 预设：极光星尘漂移 (aurora-dust) —— 优雅高端纪录片质感
  function presetAuroraDust(cv, ctx, opt) {
    var W = cv.width, H = cv.height;
    var col = parseColor(opt.color, { r: 74, g: 222, b: 128 });
    var col2 = parseColor(opt.color2, { r: 56, g: 189, b: 248 });
    var speed = (opt.speed || 1.0);
    var count = Math.floor(50 * (opt.density || 1.0));

    var dusts = [];
    for (var i = 0; i < count; i++) {
      dusts.push({
        x: Math.random() * W,
        y: Math.random() * H,
        r: Math.random() * 2.2 + 0.8,
        vy: -(Math.random() * 0.6 + 0.2) * speed,
        vx: (Math.random() - 0.5) * 0.3 * speed,
        a: Math.random() * 0.5 + 0.25,
        twinkleSpeed: Math.random() * 0.04 + 0.02
      });
    }

    var frame = 0;
    return function draw() {
      ctx.clearRect(0, 0, W, H);
      frame++;

      // 双核大面积极光呼吸光球
      var a1 = Math.sin(frame * 0.012) * 0.04 + 0.09;
      var g1 = ctx.createRadialGradient(W * 0.3, H * 0.25, 0, W * 0.3, H * 0.25, W * 0.7);
      g1.addColorStop(0, "rgba(" + col.r + "," + col.g + "," + col.b + "," + a1 + ")");
      g1.addColorStop(1, "rgba(" + col.r + "," + col.g + "," + col.b + ", 0)");
      ctx.fillStyle = g1;
      ctx.fillRect(0, 0, W, H);

      var a2 = Math.cos(frame * 0.014) * 0.03 + 0.08;
      var g2 = ctx.createRadialGradient(W * 0.7, H * 0.6, 0, W * 0.7, H * 0.6, W * 0.8);
      g2.addColorStop(0, "rgba(" + col2.r + "," + col2.g + "," + col2.b + "," + a2 + ")");
      g2.addColorStop(1, "rgba(" + col2.r + "," + col2.g + "," + col2.b + ", 0)");
      ctx.fillStyle = g2;
      ctx.fillRect(0, 0, W, H);

      // 星尘粒子飘舞
      for (var i = 0; i < dusts.length; i++) {
        var d = dusts[i];
        d.y += d.vy;
        d.x += d.vx + Math.sin(frame * 0.02 + i) * 0.2;
        if (d.y < 0) { d.y = H; d.x = Math.random() * W; }
        if (d.x < 0) d.x = W;
        if (d.x > W) d.x = 0;

        var tw = Math.sin(frame * d.twinkleSpeed + i) * 0.3 + 0.7;
        ctx.beginPath();
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(" + col.r + "," + col.g + "," + col.b + "," + (d.a * tw) + ")";
        ctx.fill();
      }
    };
  }

  // 预设注册表
  var PRESETS = {
    "bio-bubbles": presetBioBubbles,      // 微生物浮游细胞光斑 (推荐)
    "constellation": presetConstellation, // 科技星芒神经元网络 (高能版)
    "dna-spiral": presetDnaSpiral,        // 双螺旋基因光尘流
    "cyber-grid": presetCyberGrid,        // 赛博透视网格与地平线
    "aurora-dust": presetAuroraDust       // 极光星尘漂移
  };

  var PRESET_NAMES = {
    "bio-bubbles": "深海细胞光斑 (Bio Bubbles · 农业生物首选)",
    "constellation": "神经元能量网 (Constellation V2 · 科技AI)",
    "dna-spiral": "双螺旋基因流 (DNA Spiral · 遗传育种)",
    "cyber-grid": "赛博地平网格 (Cyber Grid · 工业数码)",
    "aurora-dust": "极光星尘漂移 (Aurora Dust · 高端纪实)"
  };

  // 全局管理器状态
  var currentAnimId = null;
  var currentDrawFn = null;

  return {
    presets: PRESETS,
    presetNames: PRESET_NAMES,

    // 一键初始化使用指定预设
    use: function (canvasId, presetName, options) {
      options = options || {};
      var cv = typeof canvasId === "string" ? document.getElementById(canvasId) : canvasId;
      if (!cv) {
        console.warn("[VibeBackgrounds] 未找到目标 Canvas 元素:", canvasId);
        return;
      }

      var ctx = cv.getContext("2d");
      var factory = PRESETS[presetName] || PRESETS["bio-bubbles"];

      function resize() {
        cv.width = window.innerWidth;
        cv.height = window.innerHeight;
      }
      resize();

      currentDrawFn = factory(cv, ctx, options);

      if (currentAnimId) cancelAnimationFrame(currentAnimId);
      function loop() {
        if (currentDrawFn) currentDrawFn();
        currentAnimId = requestAnimationFrame(loop);
      }
      loop();

      window.removeEventListener("resize", cv._vibeResize || function () {});
      cv._vibeResize = function () {
        resize();
        currentDrawFn = factory(cv, ctx, options);
      };
      window.addEventListener("resize", cv._vibeResize);

      console.log("🌟 VIBE 背景预设已加载: [" + presetName + "] - " + (PRESET_NAMES[presetName] || ""));
      return this;
    },

    // 自动扫描页面带有 data-preset 的 canvas 进行挂载
    init: function () {
      var canvases = document.querySelectorAll("canvas[data-preset]");
      for (var i = 0; i < canvases.length; i++) {
        var cv = canvases[i];
        var p = cv.getAttribute("data-preset") || "bio-bubbles";
        var col = cv.getAttribute("data-color") || "#4ade80";
        var col2 = cv.getAttribute("data-color2") || "#38bdf8";
        var density = parseFloat(cv.getAttribute("data-density") || "1.0");
        var speed = parseFloat(cv.getAttribute("data-speed") || "1.0");
        this.use(cv, p, { color: col, color2: col2, density: density, speed: speed });
      }
    }
  };
})();

// 暴露全局 API
if (typeof window !== "undefined") {
  window.VibeBackgrounds = VibeBackgrounds;
}
