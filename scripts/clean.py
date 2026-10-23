# -*- coding: utf-8 -*-
"""VIBE Video Studio 工作区清理与状态还原脚本
用法:
    python scripts/clean.py [选项]
    python vibe.py clean [选项]

选项:
    -y, --yes          免确认直接执行清理
    --keep-sample      保留 inputs/ 中的 N0000_quick_start 极速测试小样
    --dry-run          仅扫描展示待清理项目，不执行实际删除
    --only-output      仅清理 output/ 输出内容与临时缓存（保留 inputs/ 素材）
    --only-inputs      仅清理 inputs/ 输入素材
"""
import argparse
import os
import shutil
import stat
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
INPUTS_DIR = ROOT_DIR / "inputs"
OUTPUT_DIR = ROOT_DIR / "output"
TEMPLATE_DIR = ROOT_DIR / "template"

# 绝对受保护的目录与文件（绝不误删）
PROTECTED_PATHS = {
    ROOT_DIR / ".git",
    ROOT_DIR / ".agents",
    ROOT_DIR / "assets",
    ROOT_DIR / "examples",
    ROOT_DIR / "references",
    ROOT_DIR / "scripts",
    ROOT_DIR / "template",
    ROOT_DIR / "vibe.py",
    ROOT_DIR / "README.md",
    ROOT_DIR / "AGENTS.md",
    ROOT_DIR / "requirements.txt",
    ROOT_DIR / ".gitignore",
}

# 默认保留的文件（inputs 与 output 根部白名单）
SAFE_KEEP_FILES = {".gitkeep", "README.md"}


def format_size(size_bytes):
    """格式化字节数"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_dir_size(path):
    """计算目录总大小"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except Exception:
        pass
    return total


def remove_readonly(func, path, exc_info):
    """解决 Windows 下只读文件删除权限问题"""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def scan_clean_targets(keep_sample=False, only_output=False, only_inputs=False):
    """扫描出所有待清理的目标（目录与独立文件）"""
    targets_dirs = []
    targets_files = []

    # 1. 扫描 inputs 目录
    if not only_output and INPUTS_DIR.exists():
        for entry in os.scandir(INPUTS_DIR):
            p = Path(entry.path)
            if p.name in SAFE_KEEP_FILES:
                continue
            if keep_sample and p.name == "N0000_quick_start":
                continue
            if entry.is_dir():
                targets_dirs.append(p)
            elif entry.is_file():
                targets_files.append(p)

    # 2. 扫描 output 目录
    if not only_inputs and OUTPUT_DIR.exists():
        for entry in os.scandir(OUTPUT_DIR):
            p = Path(entry.path)
            if p.name in SAFE_KEEP_FILES:
                continue
            if entry.is_dir():
                targets_dirs.append(p)
            elif entry.is_file():
                targets_files.append(p)

    # 3. 扫描 Python 编译缓存 __pycache__
    if not only_inputs and not only_output:
        for p in ROOT_DIR.rglob("__pycache__"):
            if not any(prot in p.parents or prot == p for prot in [ROOT_DIR / ".git"]):
                targets_dirs.append(p)

    # 4. 扫描 template 目录中的质检临时文件
    if not only_inputs:
        if TEMPLATE_DIR.exists():
            for p in TEMPLATE_DIR.glob("_*.txt"):
                targets_files.append(p)

    # 5. 扫描根目录可能残留的独立临时文件
    temp_patterns = ["_*.mp4", "_*.wav", "_*.json", "_*.txt", "*_out.txt"]
    for pat in temp_patterns:
        for p in ROOT_DIR.glob(pat):
            if p.is_file() and p.name not in ["requirements.txt"]:
                targets_files.append(p)

    # 去重并排序
    targets_dirs = sorted(list(set(targets_dirs)))
    targets_files = sorted(list(set(targets_files)))

    return targets_dirs, targets_files


def ensure_gitkeep_and_readme():
    """确保 inputs/ 和 output/ 拥有标准初始文件"""
    # inputs
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep_in = INPUTS_DIR / ".gitkeep"
    if not gitkeep_in.exists():
        gitkeep_in.write_text("", encoding="utf-8")
    readme_in = INPUTS_DIR / "README.md"
    if not readme_in.exists():
        readme_in.write_text(
            "# 素材输入目录（inputs）\n\n"
            "- 每套作品一个子目录：`inputs/作品编号_作品名称/`\n"
            "- 放入三件套：`script.txt`（文案）、`voice.wav`（配音）、`char_timestamps.json`（字级时间戳）\n",
            encoding="utf-8",
        )

    # output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep_out = OUTPUT_DIR / ".gitkeep"
    if not gitkeep_out.exists():
        gitkeep_out.write_text("", encoding="utf-8")
    readme_out = OUTPUT_DIR / "README.md"
    if not readme_out.exists():
        readme_out.write_text(
            "# 输出目录（output）\n\n"
            "- 每套作品一个子目录：`output/作品编号_作品名称/`\n"
            "- 子目录内包含：`.html` 动画页、`.mp4` 成片视频、`_work/` 渲染中间帧缓存\n",
            encoding="utf-8",
        )


def execute_clean(targets_dirs, targets_files, dry_run=False):
    """执行实际清理删除操作"""
    total_bytes = 0

    print("=" * 86)
    print("🧹 VIBE Video Studio · 工作区清理与状态还原")
    print(f"工作区根目录: {ROOT_DIR}")
    print("=" * 86)

    if not targets_dirs and not targets_files:
        print("✨ 工作区非常纯净，没有需要清理的输入、输出或临时缓存文件！")
        ensure_gitkeep_and_readme()
        print("=" * 86)
        return

    print("📋 扫描到以下待清理项目：\n")

    if targets_dirs:
        print(f"📁 待清理目录 ({len(targets_dirs)} 个):")
        for d in targets_dirs:
            sz = get_dir_size(d)
            total_bytes += sz
            rel = d.relative_to(ROOT_DIR)
            print(f"   🗑️  [DIR]  {rel}  ({format_size(sz)})")

    if targets_files:
        print(f"\n📄 待清理文件 ({len(targets_files)} 个):")
        for f in targets_files:
            try:
                sz = f.stat().st_size
            except Exception:
                sz = 0
            total_bytes += sz
            rel = f.relative_to(ROOT_DIR)
            print(f"   🗑️  [FILE] {rel}  ({format_size(sz)})")

    print("\n" + "-" * 86)
    print(f"📊 预估将清理: {len(targets_dirs)} 个目录，{len(targets_files)} 个文件，释放空间约 {format_size(total_bytes)}")
    print("-" * 86)

    if dry_run:
        print("🔍 [DRY-RUN 模式] 仅扫描预览，未执行任何物理删除。")
        print("=" * 86)
        return

    # 执行删除
    del_dirs_count = 0
    del_files_count = 0

    for f in targets_files:
        try:
            if f.exists():
                os.chmod(f, stat.S_IWRITE)
                f.unlink(missing_ok=True)
                del_files_count += 1
        except Exception as e:
            print(f"   ⚠️ 删除文件失败: {f.name} ({e})")

    for d in targets_dirs:
        try:
            if d.exists():
                shutil.rmtree(d, onerror=remove_readonly)
                del_dirs_count += 1
        except Exception as e:
            print(f"   ⚠️ 删除目录失败: {d.name} ({e})")

    # 重新确保 inputs 和 output 的基石文件完好
    ensure_gitkeep_and_readme()

    print("\n✅ 清理完成！")
    print(f"🎉 成功移除 {del_dirs_count} 个目录和 {del_files_count} 个文件，释放空间 {format_size(total_bytes)}。")
    print("🌟 整个工作区已完全恢复到最原始纯净状态！")
    print("=" * 86)


def main():
    parser = argparse.ArgumentParser(
        description="清理输入和输出内容，将 VIBE Video Studio 恢复到最原始纯净状态"
    )
    parser.add_argument("-y", "--yes", action="store_true", help="跳过确认提示，直接执行清理")
    parser.add_argument("--keep-sample", action="store_true", help="保留 inputs/N0000_quick_start 极速测试小样")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描展示待清理项目，不执行实际删除")
    parser.add_argument("--only-output", action="store_true", help="仅清理 output/ 输出内容与临时缓存")
    parser.add_argument("--only-inputs", action="store_true", help="仅清理 inputs/ 输入素材")

    args = parser.parse_args()

    targets_dirs, targets_files = scan_clean_targets(
        keep_sample=args.keep_sample,
        only_output=args.only_output,
        only_inputs=args.only_inputs,
    )

    if not targets_dirs and not targets_files:
        print("✨ 工作区已经是最原始纯净状态，无需清理。")
        ensure_gitkeep_and_readme()
        return

    # 若非 dry-run 且未指定 -y，进行用户确认
    if not args.dry_run and not args.yes:
        total_sz = sum(get_dir_size(d) for d in targets_dirs) + sum(
            f.stat().st_size for f in targets_files if f.exists()
        )
        print("=" * 86)
        print("⚠️  VIBE Video Studio · 清理还原操作警示")
        print("=" * 86)
        print(f"即将永久清理 {len(targets_dirs)} 个目录和 {len(targets_files)} 个文件 (预计释放 {format_size(total_sz)})：")
        for d in targets_dirs[:10]:
            print(f"   - {d.relative_to(ROOT_DIR)}")
        if len(targets_dirs) > 10:
            print(f"   - ... 及另外 {len(targets_dirs) - 10} 个目录")
        for f in targets_files[:5]:
            print(f"   - {f.relative_to(ROOT_DIR)}")
        if len(targets_files) > 5:
            print(f"   - ... 及另外 {len(targets_files) - 5} 个文件")
        print("-" * 86)
        try:
            choice = input("❓ 是否确认删除上述输入/输出内容并将工作区恢复到最原始状态？(y/N): ").strip().lower()
            if choice not in ["y", "yes"]:
                print("❌ 操作已取消，未做任何修改。")
                return
        except EOFError:
            pass

    execute_clean(targets_dirs, targets_files, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
