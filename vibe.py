# -*- coding: utf-8 -*-
"""VIBE Video Studio 统一命令行工具 (vibe CLI)
提供一站式的环境诊断、时间线提取、播放与安全区 QA、逐帧录制、音画合成与成品校验。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "scripts"


def run_pack(args):
    from scripts.pack import scan_and_bundle
    success = scan_and_bundle(
        args.target,
        out_dir=args.out,
        voice_override=args.voice,
        timestamps_override=args.timestamps,
        sfx_override=args.sfx,
        script_override=args.script,
    )
    sys.exit(0 if success else 1)


def run_doctor(args):
    from scripts.doctor import run_diagnostics
    success = run_diagnostics()
    sys.exit(0 if success else 1)


def run_timeline(args):
    from scripts.extract_timeline import process_keywords
    process_keywords(args.timestamps, args.keywords, args.output, getattr(args, "sfx_out", None))


def run_playcheck(args):
    cmd = [sys.executable, str(SCRIPTS_DIR / "playcheck.py"), args.html]
    if args.extra:
        cmd.append(args.extra)
    subprocess.run(cmd, check=True)


def run_qa(args):
    cmd = [sys.executable, str(SCRIPTS_DIR / "qa_bounds.py"), args.html]
    if args.probes:
        cmd.append(args.probes)
    subprocess.run(cmd, check=True)


def run_audit(args):
    cmd = [sys.executable, str(SCRIPTS_DIR / "audit.py"), args.html]
    if args.probes:
        cmd.extend(["--probes", args.probes])
    subprocess.run(cmd, check=True)


def run_storyboard(args):
    cmd = [sys.executable, str(SCRIPTS_DIR / "storyboard.py"), args.timestamps]
    if args.output:
        cmd.extend(["-o", args.output])
    if args.markdown:
        cmd.extend(["-m", args.markdown])
    if args.min:
        cmd.extend(["--min", str(args.min)])
    if args.max:
        cmd.extend(["--max", str(args.max)])
    subprocess.run(cmd, check=True)


def run_preview(args):
    import webbrowser
    html_path = os.path.abspath(args.html)
    if not os.path.exists(html_path):
        print(f"❌ 错误：找不到 HTML 文件: {html_path}")
        sys.exit(1)
    file_url = Path(html_path).as_uri()
    print(f"🌐 正在使用默认浏览器打开预览:\n   {file_url}")
    print("💡 提示：在浏览器中按 F11 可进入全屏 9:16 沉浸式预览，空格键可随时暂停/播放。")
    webbrowser.open(file_url)


def run_bg(args):
    import webbrowser
    gallery_path = ROOT_DIR / "output" / "background_gallery.html"
    if not gallery_path.exists():
        gallery_path = ROOT_DIR / "template" / "background_gallery.html"
    if not gallery_path.exists():
        print(f"❌ 错误：找不到背景画廊文件: {gallery_path}")
        sys.exit(1)
    file_url = gallery_path.as_uri()
    print(f"🎨 正在打开 VIBE 背景动效画廊:\n   {file_url}")
    print("💡 提示：在画廊中可实时预览 5 种高品质粒子背景动效，一键切换颜色调色板并复制内联代码。")
    webbrowser.open(file_url)


def run_clean(args):
    from scripts.clean import (
        execute_clean,
        scan_clean_targets,
        ensure_gitkeep_and_readme,
        format_size,
        get_dir_size,
    )
    targets_dirs, targets_files = scan_clean_targets()
    if not targets_dirs and not targets_files:
        print("✨ 临时缓存区 (temp/) 已经是最原始纯净状态，无需清理。")
        ensure_gitkeep_and_readme()
        return

    if not args.dry_run and not args.yes:
        total_sz = sum(get_dir_size(d) for d in targets_dirs) + sum(
            f.stat().st_size for f in targets_files if f.exists()
        )
        print("=" * 80)
        print("⚠️  VIBE Video Studio · 临时缓存清理警示")
        print("=" * 80)
        print(f"即将安全清空 temp/ 目录下的过程切片与根目录临时文件 (预计释放 {format_size(total_sz)})：")
        for d in targets_dirs[:5]:
            print(f"   - {d.relative_to(ROOT_DIR)}/")
        for f in targets_files[:5]:
            print(f"   - {f.relative_to(ROOT_DIR)}")
        print("-" * 80)
        print("🔒 安全保障: 本操作仅清理 temp/ 过程缓存，projects/ 下全部作品工程完好无损。")
        try:
            choice = input("❓ 是否确认清空临时缓存？(y/N): ").strip().lower()
            if choice not in ["y", "yes"]:
                print("❌ 操作已取消，未做任何修改。")
                return
        except EOFError:
            pass

    execute_clean(targets_dirs, targets_files, dry_run=args.dry_run)


def run_render(args):
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "render.py"),
        args.html,
        args.out,
        str(args.duration),
        str(args.fps),
        str(args.start),
    ]
    if args.stop is not None:
        cmd.append(str(args.stop))
    subprocess.run(cmd, check=True)


def run_mux(args):
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "mux.py"),
        args.frames,
        args.voice,
        args.output,
        str(args.duration),
    ]
    if args.sfx:
        cmd.append(args.sfx)
    subprocess.run(cmd, check=True)


def run_verify(args):
    cmd = [sys.executable, str(SCRIPTS_DIR / "verify.py"), args.mp4]
    if args.frames:
        cmd.append(args.frames)
    subprocess.run(cmd, check=True)


def run_pipeline(args):
    html = os.path.abspath(args.html)
    voice = os.path.abspath(args.voice)
    output = os.path.abspath(args.output)
    dur = args.duration
    fps = args.fps

    out_dir = Path(output).parent
    frames_dir = ROOT_DIR / "temp" / "frames" / Path(html).stem
    frames_dir.mkdir(parents=True, exist_ok=True)

    print("\n[Step 1/5] 执行播放与场景推进检查 (check)...")
    subprocess.run([sys.executable, str(SCRIPTS_DIR / "playcheck.py"), html], check=True)

    print("\n[Step 2/5] 执行全维度质量复核与图数碰撞检测门禁 (audit)...")
    subprocess.run([sys.executable, str(SCRIPTS_DIR / "audit.py"), html], check=True)

    print(f"\n[Step 3/5] 执行 Playwright 逐帧无头截图录制 (render @ {fps}fps, {dur}s)...")
    subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / "render.py"),
            html, str(frames_dir), str(dur), str(fps), "0",
        ],
        check=True,
    )

    print("\n[Step 4/5] 执行 FFmpeg 音画合成与独立音效轨混音 (mux)...")
    mux_cmd = [
        sys.executable, str(SCRIPTS_DIR / "mux.py"),
        str(frames_dir), voice, output, str(dur),
    ]

    sfx_file = args.sfx
    if not sfx_file:
        candidate = Path(html).parent / "sfx.json"
        if candidate.exists():
            sfx_file = str(candidate)
        else:
            try:
                with io.open(html, "r", encoding="utf-8") as hf:
                    content = hf.read()
                m = re.search(r"var\s+SCENES\s*=\s*(\[[^;]+\]);", content)
                if m:
                    clean_arr = re.sub(r"'", '"', m.group(1))
                    raw_scenes = json.loads(clean_arr)
                    whoosh_times = [round(float(s[1]), 2) for s in raw_scenes[1:] if float(s[1]) > 0]
                    auto_sfx = {
                        "whoosh": whoosh_times,
                        "pop": [],
                        "ding": [],
                        "click": [],
                        "chime": [max(0.0, round(dur - 4.5, 2))]
                    }
                    auto_sfx_path = ROOT_DIR / "temp" / f"auto_sfx_{Path(html).stem}.json"
                    auto_sfx_path.parent.mkdir(parents=True, exist_ok=True)
                    with io.open(auto_sfx_path, "w", encoding="utf-8") as sf:
                        json.dump(auto_sfx, sf, indent=2)
                    sfx_file = str(auto_sfx_path)
                    print(f"  [Auto SFX] 从 HTML 自动提取 {len(whoosh_times)} 个场景切点，已自动挂载 whoosh / chime 音效")
            except Exception as e:
                pass

    if sfx_file:
        mux_cmd.append(sfx_file)
    subprocess.run(mux_cmd, check=True)

    print("\n[Step 5/5] 执行成片规格与音量探针验证 (verify)...")
    subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "verify.py"), output, str(frames_dir)],
        check=True,
    )
    print(f"\n🎉 流水线执行成功！最终成品视频已交付至: {output}")


def main():
    parser = argparse.ArgumentParser(
        prog="vibe",
        description="VIBE Video Studio 统一工具链 CLI：一站式搞定知识短视频录制与合成",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="可用子命令")

    # doctor
    p_doc = subparsers.add_parser("doctor", help="诊断运行环境（Python、Playwright、FFmpeg 等）")
    p_doc.set_defaults(func=run_doctor)

    # pack
    p_pack = subparsers.add_parser("pack", help="作品工程自包含归档与 WeMediaForge 导入就绪检查")
    p_pack.add_argument("target", help="工程目录路径或 HTML 文件路径")
    p_pack.add_argument("-o", "--out", help="输出归档目录（默认在原目录就地补齐整理）", default=None)
    p_pack.add_argument("--voice", help="指定主配音文件路径", default=None)
    p_pack.add_argument("--timestamps", help="指定字级时间戳 JSON 路径", default=None)
    p_pack.add_argument("--sfx", help="指定音效表 JSON 路径", default=None)
    p_pack.add_argument("--script", help="指定文案脚本 TXT 路径", default=None)
    p_pack.set_defaults(func=run_pack)

    # timeline
    p_time = subparsers.add_parser("timeline", help="从字级时间戳 JSON 精确提取关键句/词的时间点，并可自动生成 SFX 音效表")
    p_time.add_argument("timestamps", help="字级时间戳 JSON 文件路径")
    p_time.add_argument("keywords", help="关键词列表文件 (.txt)")
    p_time.add_argument("-o", "--output", help="结果输出路径 (可选)", default=None)
    p_time.add_argument("--sfx-out", help="音效表 JSON 输出路径 (可选，默认同级生成 sfx.json)", default=None)
    p_time.set_defaults(func=run_timeline)

    # storyboard
    p_sb = subparsers.add_parser("storyboard", help="短视频分镜头导演拆解（智能划分 6~14 秒高能镜头流）")
    p_sb.add_argument("timestamps", help="字级时间戳 JSON 文件路径")
    p_sb.add_argument("-o", "--output", help="导出的分镜头 JSON 文件路径 (可选)", default=None)
    p_sb.add_argument("-m", "--markdown", help="导出的分镜头 Markdown 表格路径 (可选)", default=None)
    p_sb.add_argument("--min", type=float, default=6.0, help="单镜头最短时长（默认 6.0 秒）")
    p_sb.add_argument("--max", type=float, default=14.0, help="单镜头最长时长（默认 14.0 秒）")
    p_sb.set_defaults(func=run_storyboard)

    # playcheck
    p_play = subparsers.add_parser("check", help="播放验证（检查场景切换、章节名与字幕推进）")
    p_play.add_argument("html", help="HTML 动画页文件路径")
    p_play.add_argument("--extra", help="额外探针时刻，逗号分隔 (如: 1.5,4.2)", default=None)
    p_play.set_defaults(func=run_playcheck)

    # qa
    p_qa = subparsers.add_parser("qa", help="四边安全区与三区边界合规扫描")
    p_qa.add_argument("html", help="HTML 动画页文件路径")
    p_qa.add_argument("--probes", help="探针检测时刻列表，逗号分隔", default=None)
    p_qa.set_defaults(func=run_qa)

    # audit (全维度质量复核与图数碰撞检测门禁)
    p_audit = subparsers.add_parser("audit", help="全维度质量复核与图数碰撞检测门禁 (安全区/图数解耦/字号/黄金3秒)")
    p_audit.add_argument("html", help="HTML 动画页文件路径")
    p_audit.add_argument("--probes", help="探针检测时刻列表，逗号分隔 (可选)", default=None)
    p_audit.set_defaults(func=run_audit)

    # preview
    p_prev = subparsers.add_parser("preview", help="使用系统默认浏览器打开 HTML 页面全屏预览")
    p_prev.add_argument("html", help="HTML 动画页文件路径")
    p_prev.set_defaults(func=run_preview)

    # bg (背景动效画廊交互预览)
    p_bg = subparsers.add_parser("bg", help="打开高品质背景动效交互画廊（生物光斑/双螺旋/赛博网格/极光等）")
    p_bg.set_defaults(func=run_bg)

    # render
    p_ren = subparsers.add_parser("render", help="Playwright 逐帧无头截图录制")
    p_ren.add_argument("html", help="HTML 动画页文件路径")
    p_ren.add_argument("out", help="输出图片帧目录 (如: output/.../_work/frames)")
    p_ren.add_argument("duration", type=float, help="成片总时长（秒）")
    p_ren.add_argument("--fps", type=float, default=20.0, help="录制帧率 (默认: 20)")
    p_ren.add_argument("--start", type=int, default=0, help="起始帧序号 (用于分段续跑)")
    p_ren.add_argument("--stop", type=int, default=None, help="截止帧序号 (可选)")
    p_ren.set_defaults(func=run_render)

    # mux
    p_mux = subparsers.add_parser("mux", help="合成 MP4 视频（视频轨 + 人声配音 + 音效轨 amix）")
    p_mux.add_argument("frames", help="图片帧目录")
    p_mux.add_argument("voice", help="配音 WAV 文件路径")
    p_mux.add_argument("output", help="最终 MP4 输出路径")
    p_mux.add_argument("duration", type=float, help="成片总时长（秒）")
    p_mux.add_argument("--sfx", help="音效表 JSON 路径 (可选)", default=None)
    p_mux.set_defaults(func=run_mux)

    # verify
    p_ver = subparsers.add_parser("verify", help="成片交付前质量与规格验证（ffprobe 规格与音量探针）")
    p_ver.add_argument("mp4", help="MP4 视频文件路径")
    p_ver.add_argument("--frames", help="对应的图片帧目录 (可选，用于比对帧数)", default=None)
    p_ver.set_defaults(func=run_verify)

    # pipeline
    p_pipe = subparsers.add_parser("pipeline", help="一键全流程交付流水线 (check -> qa -> render -> mux -> verify)")
    p_pipe.add_argument("html", help="HTML 动画页文件路径")
    p_pipe.add_argument("voice", help="配音 WAV 文件路径")
    p_pipe.add_argument("output", help="最终 MP4 输出路径")
    p_pipe.add_argument("duration", type=float, help="成片总时长（秒）")
    p_pipe.add_argument("--fps", type=float, default=20.0, help="录制帧率 (默认: 20)")
    p_pipe.add_argument("--sfx", help="音效表 JSON 路径 (可选)", default=None)
    p_pipe.set_defaults(func=run_pipeline)

    # clean
    p_clean = subparsers.add_parser("clean", help="一键安全清空 temp/ 临时过程缓存与根目录中间文件")
    p_clean.add_argument("-y", "--yes", action="store_true", help="跳过确认提示，直接执行清理")
    p_clean.add_argument("--dry-run", action="store_true", help="仅扫描展示待清理项目，不执行实际删除")
    p_clean.set_defaults(func=run_clean)

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
