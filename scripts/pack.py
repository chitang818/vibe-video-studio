# -*- coding: utf-8 -*-
"""VIBE Video Studio 工程归档与 WeMediaForge 对接打包工具
支持两种归档行为：
1. 外部工程目录：就地补齐整理动效 HTML 与 sfx.json，零拷贝即开即用；
2. 零散素材文件：自动汇总归拢至 projects/{作品编号}_{作品名称}/ 独立工程包；
最终形成齐备 5 核心文件的标准工程，供 WeMediaForge 直接拖拽导入渲染。
"""
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT_DIR / "projects"
TEMP_DIR = ROOT_DIR / "temp"


def scan_and_bundle(target_path, out_dir=None, voice_override=None, timestamps_override=None, sfx_override=None, script_override=None):
    target = Path(target_path).resolve()
    if not target.exists():
        print(f"❌ 错误：指定的目标路径不存在: {target}")
        sys.exit(1)

    work_dir = target if target.is_dir() else target.parent
    html_file = None

    if target.is_file() and target.suffix.lower() in [".html", ".htm"]:
        html_file = target
    else:
        # 在目录下查找 HTML
        html_candidates = list(work_dir.glob("*.html")) + list(work_dir.glob("*.htm"))
        html_candidates = [h for h in html_candidates if not h.name.lower().startswith("background_gallery")]
        if html_candidates:
            html_file = html_candidates[0]

    # 1. 寻找或确定作品编号与标题
    work_prefix = "N0001"
    title = work_dir.name
    prefix_match = re.match(r"^([a-zA-Z]\d{3,5})[_-]?(.*)$", work_dir.name)
    if prefix_match:
        work_prefix = prefix_match.group(1)
        if prefix_match.group(2):
            title = prefix_match.group(2)
    elif html_file:
        m = re.match(r"^([a-zA-Z]\d{3,5})[_-]?(.*)\.html?$", html_file.name, re.IGNORECASE)
        if m:
            work_prefix = m.group(1)
            title = m.group(2)

    # 2. 嗅探音频
    voice_file = Path(voice_override) if voice_override and Path(voice_override).exists() else None
    if not voice_file:
        wavs = list(work_dir.glob("*.wav")) + list(work_dir.glob("*.mp3"))
        wavs = [w for w in wavs if not w.name.startswith("_") and w.name not in ["whoosh.wav", "pop.wav", "ding.wav", "chime.wav", "click.wav"]]
        if wavs:
            voice_file = wavs[0]

    # 3. 嗅探时间戳
    timestamps_file = Path(timestamps_override) if timestamps_override and Path(timestamps_override).exists() else None
    if not timestamps_file:
        ts = list(work_dir.glob("*timestamp*.json")) + list(work_dir.glob("timeline.json"))
        if ts:
            timestamps_file = ts[0]

    # 4. 嗅探文案正文
    script_file = Path(script_override) if script_override and Path(script_override).exists() else None
    if not script_file:
        txts = [t for t in work_dir.glob("*.txt") if not t.name.endswith("_out.txt") and not t.name.startswith("audit_")]
        if txts:
            script_file = txts[0]

    # 5. 嗅探或生成 sfx.json
    sfx_file = Path(sfx_override) if sfx_override and Path(sfx_override).exists() else None
    if not sfx_file:
        sfx_candidate = work_dir / "sfx.json"
        if sfx_candidate.exists():
            sfx_file = sfx_candidate
        elif html_file and html_file.exists():
            # 自动从 HTML 提取场景切点推导
            try:
                content = html_file.read_text(encoding="utf-8")
                m = re.search(r"var\s+SCENES\s*=\s*(\[[^;]+\]);", content)
                if m:
                    clean_arr = re.sub(r"'", '"', m.group(1))
                    scenes = json.loads(clean_arr)
                    whoosh_times = [round(float(s[1]), 2) for s in scenes[1:] if float(s[1]) > 0]
                    auto_sfx = {
                        "whoosh": whoosh_times,
                        "pop": [],
                        "ding": [],
                        "click": [],
                        "chime": []
                    }
                    sfx_candidate.write_text(json.dumps(auto_sfx, indent=2, ensure_ascii=False), encoding="utf-8")
                    sfx_file = sfx_candidate
                    print(f"  [Auto SFX] 已自动从 HTML 场景切点推导并生成: {sfx_file.name}")
            except Exception:
                pass

    # 6. 确定目标归档目录
    # 若传入的是零散文件（目标是个孤立文件），且未指定 out_dir，自动在 projects/ 下建档
    if out_dir:
        dest_dir = Path(out_dir).resolve()
    elif target.is_file() and not work_dir.is_relative_to(PROJECTS_DIR):
        folder_name = f"{work_prefix}_{title}" if not title.startswith(work_prefix) else title
        dest_dir = PROJECTS_DIR / folder_name
    else:
        dest_dir = work_dir

    is_same_dir = (dest_dir == work_dir)

    if not is_same_dir:
        dest_dir.mkdir(parents=True, exist_ok=True)
        print(f"📦 正在归拢零散素材并建档至: {dest_dir.relative_to(ROOT_DIR) if dest_dir.is_relative_to(ROOT_DIR) else dest_dir}")
        if html_file and html_file.exists() and html_file.parent != dest_dir:
            shutil.copy2(html_file, dest_dir / html_file.name)
            html_file = dest_dir / html_file.name
        if voice_file and voice_file.exists() and voice_file.parent != dest_dir:
            shutil.copy2(voice_file, dest_dir / voice_file.name)
            voice_file = dest_dir / voice_file.name
        if timestamps_file and timestamps_file.exists() and timestamps_file.parent != dest_dir:
            shutil.copy2(timestamps_file, dest_dir / timestamps_file.name)
            timestamps_file = dest_dir / timestamps_file.name
        if script_file and script_file.exists() and script_file.parent != dest_dir:
            shutil.copy2(script_file, dest_dir / script_file.name)
            script_file = dest_dir / script_file.name
        if sfx_file and sfx_file.exists() and sfx_file.parent != dest_dir:
            shutil.copy2(sfx_file, dest_dir / sfx_file.name)
            sfx_file = dest_dir / sfx_file.name

    # 7. 打印工程归档诊断报告
    is_ready = (html_file is not None and html_file.exists())

    print("\n" + "=" * 80)
    print(f"📦 VIBE Video Studio · 作品工程自包含归档看板")
    print("=" * 80)
    print(f"📁 工程目录: {dest_dir}")
    print(f"🏷️ 作品标识: [{work_prefix}] {title}")
    print("-" * 80)
    print(f"  {'✅' if html_file else '❌'} [HTML 网页] : {html_file.name if html_file else '缺失 (必须具备自包含网页)'}")
    print(f"  {'✅' if voice_file else '⚠️'} [口播配音] : {voice_file.name if voice_file else '缺失 (无声视频模式)'}")
    print(f"  {'✅' if timestamps_file else '⚠️'} [字级时间戳] : {timestamps_file.name if timestamps_file else '未归档'}")
    print(f"  {'✅' if script_file else '⚠️'} [文案脚本] : {script_file.name if script_file else '未归档'}")
    print(f"  {'✅' if sfx_file else '⚠️'} [音效时刻表] : {sfx_file.name if sfx_file else '未归档'}")
    print("-" * 80)

    if is_ready:
        print("🎉 状态: 【就绪 (READY)】")
        print("💡 使用方式: 可直接将上述工程目录整体拖拽至 WeMediaForge【基础工具箱 - 网页处理】")
        print("   或选中多个作品文件夹批量导入，即可调用本地 GPU 硬件加速秒级生成高清视频！")
    else:
        print("⚠️ 状态: 【未就绪 (NOT READY)】缺失 HTML 网页文件，请先执行网页构建。")
    print("=" * 80 + "\n")

    return is_ready


def main():
    if len(sys.argv) < 2:
        print("用法: python pack.py <工程目录或HTML路径> [--out <输出归档目录>] [--voice <wav>] [--timestamps <json>] [--sfx <sfx.json>]")
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description="VIBE 作品工程自包含归档与 WeMediaForge 对接工具")
    parser.add_argument("target", help="工程目录路径或 HTML 文件路径")
    parser.add_argument("--out", "-o", help="输出归档目录（默认：外部文件夹就地整理；零散文件自动归入 projects/）", default=None)
    parser.add_argument("--voice", help="指定主配音文件路径", default=None)
    parser.add_argument("--timestamps", help="指定字级时间戳 JSON 路径", default=None)
    parser.add_argument("--sfx", help="指定音效表 JSON 路径", default=None)
    parser.add_argument("--script", help="指定文案脚本 TXT 路径", default=None)
    args = parser.parse_args()

    success = scan_and_bundle(
        args.target,
        out_dir=args.out,
        voice_override=args.voice,
        timestamps_override=args.timestamps,
        sfx_override=args.sfx,
        script_override=args.script,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
