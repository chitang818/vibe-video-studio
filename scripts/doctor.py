# -*- coding: utf-8 -*-
"""VIBE 环境诊断与项目完整性检查工具
用法:
    python scripts/doctor.py
"""
import importlib.util
import os
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def check_python():
    v = sys.version_info
    ver_str = f"{v.major}.{v.minor}.{v.micro}"
    ok = v.major == 3 and v.minor >= 10
    msg = f"Python 版本: {ver_str} ({sys.executable})"
    return ok, msg, "建议使用 Python 3.10 或更高版本"


def check_ffmpeg():
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        return False, "FFmpeg: 未检测到", "请安装 FFmpeg 并将其 bin 目录添加至系统 PATH 环境变量"

    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        first_line = r.stdout.splitlines()[0] if r.stdout else "已安装"
        return True, f"FFmpeg: {first_line} ({ffmpeg_path})", ""
    except Exception as e:
        return False, f"FFmpeg 检测异常: {e}", "请检查 FFmpeg 是否损坏"


def check_ffprobe():
    ffprobe_path = shutil.which("ffprobe")
    if not ffprobe_path:
        return False, "FFprobe: 未检测到", "FFprobe 通常与 FFmpeg 一同提供，请确保其在 PATH 中"

    try:
        r = subprocess.run(["ffprobe", "-version"], capture_output=True, text=True, timeout=5)
        first_line = r.stdout.splitlines()[0] if r.stdout else "已安装"
        return True, f"FFprobe: {first_line} ({ffprobe_path})", ""
    except Exception as e:
        return False, f"FFprobe 检测异常: {e}", "请检查 FFprobe 是否正常"


def check_playwright():
    spec = importlib.util.find_spec("playwright")
    if not spec:
        return False, "Playwright Python 包: 未安装", "请执行: pip install -r requirements.txt"

    # 进一步检查 chromium 浏览器是否已下载
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            if os.path.exists(browser_path):
                return True, f"Playwright Chromium: 就绪 ({browser_path})", ""
            else:
                return False, "Playwright: 已安装但未安装浏览器内核", "请执行: playwright install chromium"
    except Exception as e:
        return False, f"Playwright 浏览器测试失败: {e}", "请执行: playwright install chromium"


def check_scripts():
    scripts_dir = PROJECT_ROOT / "scripts"
    fails = []
    successes = []
    for f in sorted(scripts_dir.glob("*.py")):
        try:
            py_compile.compile(str(f), doraise=True)
            successes.append(f.name)
        except Exception as e:
            fails.append((f.name, str(e)))

    if fails:
        err_msg = ", ".join([f"{name}: {err}" for name, err in fails])
        return False, f"脚本语法检查存在错误: {err_msg}", "请检查语法错误"
    return True, f"Python 工具脚本语法校验全部通过 ({len(successes)} 个文件)", ""


def check_structure():
    # 基础核心文件
    required_paths = [
        "README.md",
        "AGENTS.md",
        ".agents/rules/vibe-rules.md",
        ".agents/skills/vibe-knowledge-video/SKILL.md",
        "scripts",
        "inputs",
        "output",
    ]
    missing = []
    for p in required_paths:
        if not (PROJECT_ROOT / p).exists():
            missing.append(p)

    # 关键模板与资产：支持根目录或 Skill 封装目录自适应检测
    resource_checks = [
        ("skeleton.html 模板", ["template/skeleton.html", ".agents/skills/vibe-knowledge-video/templates/skeleton.html"]),
        ("motions.css 动效库", ["assets/motions/motions.css", ".agents/skills/vibe-knowledge-video/assets/motions/motions.css"]),
        ("themes.css 主题库", ["assets/themes/themes.css", ".agents/skills/vibe-knowledge-video/assets/themes/themes.css"]),
        ("sfx_presets.json 音效表", ["assets/sounds/sfx_presets.json", ".agents/skills/vibe-knowledge-video/assets/sounds/sfx_presets.json"]),
    ]
    for label, candidates in resource_checks:
        if not any((PROJECT_ROOT / c).exists() for c in candidates):
            missing.append(label)

    if missing:
        return False, f"项目关键目录/文件缺失: {', '.join(missing)}", "请确保项目文件完整"
    return True, "项目基础目录架构与资源资产完整", ""


def run_diagnostics():
    print("=" * 60)
    print(" VIBE Video Studio 运行环境与工程诊断")
    print(f" 工作根目录: {PROJECT_ROOT}")
    print("=" * 60)

    checks = [
        ("Python 解释器", check_python),
        ("FFmpeg 音视频编码器", check_ffmpeg),
        ("FFprobe 媒体探针", check_ffprobe),
        ("Playwright 无头录制环境", check_playwright),
        ("项目目录结构", check_structure),
        ("工具链脚本语法", check_scripts),
    ]

    all_pass = True
    for name, fn in checks:
        ok, msg, suggestion = fn()
        status_tag = "[ OK ]" if ok else "[FAIL]"
        print(f"\n{status_tag} {name}")
        print(f"       详情: {msg}")
        if not ok:
            all_pass = False
            if suggestion:
                print(f"       提示: {suggestion}")

    print("\n" + "=" * 60)
    if all_pass:
        print(" 全项检测通过！您的环境已具备完整的 VIBE 视频制作与渲染能力。")
    else:
        print(" 检测到部分环境或项目配置未就绪，请按上述提示修复。")
    print("=" * 60)
    return all_pass


if __name__ == '__main__':
    success = run_diagnostics()
    sys.exit(0 if success else 1)
