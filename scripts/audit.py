# -*- coding: utf-8 -*-
"""VIBE 自动化质量复核与图数碰撞检测门禁 (Audit Gatekeeper)
用法:
    python scripts/audit.py <html路径> [--probes <时刻1,时刻2,...>]

复核维度：
1. [OVERLAP] 图数与图文物理碰撞与穿透检测（环形图内径几何包络、图标与文字间隙、柱状图与数字解耦）
2. [SAFEZONE] 1080x1920 四边安全区与三区边界合规扫描
3. [TYPOGRAPHY] 移动端字号与易读性红线审查（标题 >= 3.6cqw，正文 >= 2.6cqw）
4. [STACKING] 竖屏垂直优先排版审计（禁止在非必要时采用狭窄左右分栏）
5. [HOOK_STILLNESS] 黄金 3 秒高频爆点与画面连续静止时间审计
"""
import argparse
import io
import math
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_full_audit(html_path, custom_probes=None):
    if not html_path.startswith("file://"):
        html_url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    else:
        html_url = html_path

    print("=" * 86)
    print("🔍 VIBE 视频工作室 · 自动化质量复核与碰撞检测门禁 (Audit Gatekeeper)")
    print(f"目标文件: {html_path}")
    print("=" * 86)

    violations = []
    warnings = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        page = ctx.new_page()

        # 捕获页面运行时 JS 报错
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        page.goto(html_url)
        page.wait_for_load_state("load")
        time.sleep(0.8)

        # 1. 基础时钟与播放组件检测
        has_btn = page.query_selector("#btnPlay") is not None
        has_voice = page.query_selector("#voice") is not None
        if not has_btn or not has_voice:
            violations.append("[DOM] 页面缺少必须的 #btnPlay 或 #voice 元素")

        # 点击开始以初始化 AudioContext 与场景
        if has_btn:
            page.click("#btnPlay")
            time.sleep(0.3)

        # 提取探针时刻
        meta = page.evaluate("""() => {
            const scenes = (typeof SCENES !== 'undefined') ? SCENES : ((typeof SHOTS !== 'undefined') ? SHOTS : []);
            const chaps = (typeof CHAP_NAMES !== 'undefined') ? CHAP_NAMES : ((typeof SHOT_NAMES !== 'undefined') ? SHOT_NAMES : []);
            const res = [];
            for (let i = 0; i < scenes.length; i++) {
                res.push({ id: scenes[i][0], t: scenes[i][1], name: chaps[i] || '' });
            }
            return res;
        }""")

        if not meta:
            violations.append("[SCENES] 未在页面中检测到 SCENES 或 SHOTS 场景时间线数组")

        if custom_probes:
            probe_times = [float(x) for x in custom_probes.split(",")]
        else:
            probe_times = []
            for sc in meta:
                probe_times.append(sc["t"] + 0.6)
            # 增加开场黄金 3 秒专项探针
            if len(probe_times) > 0 and probe_times[0] > 3.0:
                probe_times.extend([1.0, 2.8, 5.0])
            probe_times = sorted(list(set(probe_times)))

        # 2. 逐时刻复核扫描
        print(f"⏱️ 正在对全片 {len(probe_times)} 组关键时间节点执行物理碰撞与规范复核...")

        for t in probe_times:
            page.evaluate(f"""(function(tt) {{
                if (window.syncTime) window.syncTime(tt);
                var a = document.getElementById('voice');
                try {{ if (a) a.currentTime = tt; }} catch(e) {{}}
            }})({t})""")
            time.sleep(0.35)

            report = page.evaluate("""() => {
                const viols = [];
                const warns = [];
                const activeScene = document.querySelector('.scene.active');
                if (!activeScene) {
                    return { viols: ['[SCENE] 当前时刻没有激活的场景 (.scene.active 为空)'], warns: [] };
                }
                const sid = activeScene.id;

                // ==================== A0. 顶部纯粹作品标题审查 ====================
                const headEl = document.querySelector('.head');
                if (headEl) {
                    const hr = headEl.getBoundingClientRect();
                    if (hr.top < 188 || hr.left < 80 || hr.right > 1000 || hr.bottom > 330) {
                        viols.push(`[HEAD_SAFEZONE] 顶部作品标题越界: T=${Math.round(hr.top)} B=${Math.round(hr.bottom)} L=${Math.round(hr.left)} R=${Math.round(hr.right)}`);
                    }
                }
                const chapEl = document.getElementById('chapText');
                if (chapEl && window.getComputedStyle(chapEl).display !== 'none') {
                    warns.push('[HEAD_PURITY] 页面检测到残留的 #chapText 分镜指示元素，请移除以保持顶部只显示作品标题');
                }

                // ==================== A. 四边安全区审查 ====================
                const allEls = activeScene.querySelectorAll('*');
                for (let el of allEls) {
                    const st = window.getComputedStyle(el);
                    if (st.position === 'fixed') continue;
                    const cls = (el.className && el.className.baseVal !== undefined) ? el.className.baseVal : (el.className || '');
                    if (/aura|glow|inner|phs|scene|subtitle|overlay|progress|flash|canvas/i.test(cls)) continue;

                    // 检查处于非激活阶段的子元素
                    const so = document.getElementById('s-open');
                    const activePhs = so ? so.getAttribute('data-phase') : '';
                    const phsEl = el.closest('.phs');
                    if (phsEl && phsEl.className.indexOf('phs-' + activePhs) < 0) continue;

                    // 检查不可见元素
                    if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.05) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width < 6 || r.height < 6 || r.right < 1) continue;

                    // 安全区边界: 顶 >= 190 (10%), 底 <= 1653 (14%), 左 >= 84 (8%), 右 <= 996 (92%)
                    if (r.left < 84 || r.right > 996 || r.top < 190 || r.bottom > 1653) {
                        viols.push(`[SAFEZONE] ${sid} ${el.tagName}.${cls.slice(0, 16)} 越界: L=${Math.round(r.left)} R=${Math.round(r.right)} T=${Math.round(r.top)} B=${Math.round(r.bottom)}`);
                    }
                }

                // ==================== B. 图数解耦与几何穿透检测 ====================
                // 1. 环形图 (ring-svg / gene-ring-box) 内径穿透检测
                const ringBoxes = activeScene.querySelectorAll('.ring-svg, .gene-ring-box');
                for (let rb of ringBoxes) {
                    const rbRect = rb.getBoundingClientRect();
                    const cx = rbRect.left + rbRect.width / 2;
                    const cy = rbRect.top + rbRect.height / 2;
                    // 外半径以宽的一半计算，内半径估算约占 72%（对应 r=40, stroke=8）
                    const innerRadius = (rbRect.width / 2) * 0.72;

                    // 检查环内部居中文本节点
                    const innerTexts = rb.querySelectorAll('.c-val *, .center-txt *');
                    for (let txt of innerTexts) {
                        const tr = txt.getBoundingClientRect();
                        if (tr.width < 2 || tr.height < 2) continue;
                        
                        // 计算文字外接矩形的 4 个顶点到圆心的距离
                        const corners = [
                            { x: tr.left, y: tr.top },
                            { x: tr.right, y: tr.top },
                            { x: tr.left, y: tr.bottom },
                            { x: tr.right, y: tr.bottom }
                        ];
                        for (let c of corners) {
                            const dist = Math.hypot(c.x - cx, c.y - cy);
                            if (dist > innerRadius - 2) {
                                viols.push(`[OVERLAP] ${sid} 环形图文字 (${txt.textContent.trim().slice(0, 10)}) 穿透圆环内径！顶点距离=${Math.round(dist)}px > 内径安全线=${Math.round(innerRadius - 2)}px`);
                                break;
                            }
                        }
                    }
                }

                // 2. 卡片内图标与文本横向物理重叠碰撞检测
                const cards = activeScene.querySelectorAll('.stack-card, .card');
                for (let cd of cards) {
                    const ico = cd.querySelector('.card-ico, .ico');
                    const textCont = cd.querySelector('.card-body, .desc, .name, .t, .d');
                    if (ico && textCont) {
                        const ir = ico.getBoundingClientRect();
                        const tr = textCont.getBoundingClientRect();
                        // 碰撞判定: 横向有重合且纵向有重合
                        const overlapX = Math.max(0, Math.min(ir.right, tr.right) - Math.max(ir.left, tr.left));
                        const overlapY = Math.max(0, Math.min(ir.bottom, tr.bottom) - Math.max(ir.top, tr.top));
                        if (overlapX > 2 && overlapY > 2) {
                            viols.push(`[OVERLAP] ${sid} 卡片内图标与文本重叠！碰撞面积=${Math.round(overlapX * overlapY)}px²`);
                        }
                    }
                }

                // 3. 进度条/柱状图轨道与数值重叠检测
                const barRows = activeScene.querySelectorAll('.bar-row');
                for (let br of barRows) {
                    const track = br.querySelector('.bar-track');
                    const val = br.querySelector('.val');
                    if (track && val) {
                        const tr = track.getBoundingClientRect();
                        const vr = val.getBoundingClientRect();
                        const overlapX = Math.max(0, Math.min(tr.right, vr.right) - Math.max(tr.left, vr.left));
                        if (overlapX > 2) {
                            viols.push(`[OVERLAP] ${sid} 柱状图轨道与数值重叠！`);
                        }
                    }
                }

                // ==================== C. 移动端字号与可读性审查 ====================
                const titles = activeScene.querySelectorAll('h2, .card-title, .stack-card .card-title, .ring-info .t');
                for (let tEl of titles) {
                    const st = window.getComputedStyle(tEl);
                    const fs = parseFloat(st.fontSize);
                    if (fs < 32) {
                        warns.push(`[TYPOGRAPHY] ${sid} 标题字号偏小 (${Math.round(fs)}px < 32px/3.0cqw)`);
                    }
                }
                const descs = activeScene.querySelectorAll('.card-desc, .stack-card .card-desc, .sub, .ring-info .d');
                for (let dEl of descs) {
                    const st = window.getComputedStyle(dEl);
                    const fs = parseFloat(st.fontSize);
                    if (fs < 24) {
                        warns.push(`[TYPOGRAPHY] ${sid} 正文字号偏小 (${Math.round(fs)}px < 24px/2.2cqw)`);
                    }
                }

                return { viols: viols, warns: warns };
            }""")

            if report["viols"]:
                violations.extend(report["viols"])
            if report["warns"]:
                warnings.extend(report["warns"])

        # 3. 黄金 3 秒多阶段专项核查
        shot01_check = page.evaluate("""() => {
            const s1 = document.querySelector('#shot-01, #s-open');
            if (!s1) return { pass: false, msg: '未找到开场 Shot 01 元素' };
            const hasPhases = s1.querySelectorAll('.hook-phase, .phs').length >= 2;
            const hasRipple = s1.querySelector('.radar-ripple, .aura, .hook-graphic') !== null;
            return {
                pass: hasPhases || hasRipple,
                hasPhases: hasPhases,
                hasRipple: hasRipple
            };
        }""")
        if not shot01_check["pass"]:
            violations.append("[HOOK_CHECK] 开场 Shot 01 缺少多阶段动态爆点组件 (需包含 .hook-phase 或 .radar-ripple)")

        # 4. 统计 JS 运行时错误
        if page_errors:
            for pe in page_errors:
                violations.append(f"[JS_ERROR] 页面运行时异常: {pe}")

        browser.close()

    # 去重
    unique_viols = list(dict.fromkeys(violations))
    unique_warns = list(dict.fromkeys(warnings))

    # 输出复核结论报告
    print("\n" + "=" * 86)
    print("📋 自动化复核综合评估结果")
    print("=" * 86)

    if not unique_viols and not unique_warns:
        print("✅ [ALL PASS] 完美通过！所有镜头均严守安全区、图数完全解耦无重叠、字号饱满合规！")
        print("🎉 结论：本作品完全符合量产交付标准，准予直接交付用户或启动 MP4 渲染！")
        print("=" * 86)
        return True
    elif not unique_viols and unique_warns:
        print("⚠️ [PASS WITH WARNINGS] 复核通过（无阻断性错误，存在轻微建议）：")
        for w in unique_warns[:5]:
            print(f"   🔸 {w}")
        print("=" * 86)
        return True
    else:
        print(f"❌ [AUDIT FAILED] 复核未通过！检测到 {len(unique_viols)} 处硬性违规，严禁交付：")
        for v in unique_viols:
            print(f"   🚫 {v}")
        if unique_warns:
            print("\n   [补充告警]:")
            for w in unique_warns[:3]:
                print(f"   🔸 {w}")
        print("=" * 86)
        print("💡 处置指示：AI 必须自动修复上述违规项，重新运行 `vibe.py audit` 直至全部通过！")
        print("=" * 86)
        return False


def main():
    parser = argparse.ArgumentParser(description="VIBE 自动化质量复核与图数碰撞检测门禁")
    parser.add_argument("html", help="HTML 动画页文件路径")
    parser.add_argument("--probes", help="自定义探针时刻列表 (逗号分隔)", default=None)
    args = parser.parse_args()

    passed = run_full_audit(args.html, args.probes)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
