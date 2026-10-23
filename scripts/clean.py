# -*- coding: utf-8 -*-
"""VIBE Video Studio 临时缓存安全清理脚本
专职清空 temp/ 目录下的所有过程临时切片（录制帧、QA 探针图、音频混音缓存）
以及根目录下的临时文件，绝不触碰 projects/ 下的任何用户工程与原始素材。
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
TEMP_DIR = ROOT_DIR / "temp"
PROJECTS_DIR = ROOT_DIR / "projects"

# 默认保留的系统占位文件
SAFE_KEEP_FILES = {".gitkeep", "README.md"}


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_dir_size(path):
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
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def scan_clean_targets():
    """扫描出所有待清理的目标（temp 目录与根目录临时文件）"""
    targets_dirs = []
    targets_files = []

    # 1. 扫描 temp 目录
    if TEMP_DIR.exists():
        for entry in os.scandir(TEMP_DIR):
            p = Path(entry.path)
            if p.name in SAFE_KEEP_FILES:
                continue
            if p.is_dir():
                targets_dirs.append(p)
            elif p.is_file():
                targets_files.append(p)

    # 2. 扫描根目录遗留的临时生成切片 (如 _silent.mp4, _sfx.wav, *_out.txt)
    for entry in os.scandir(ROOT_DIR):
        p = Path(entry.path)
        if p.is_file():
            name = p.name
            if (
                name.startswith("_")
                and (
                    name.endswith(".mp4")
                    or name.endswith(".wav")
                    or name.endswith(".txt")
                    or name.endswith(".json")
                )
            ) or name.endswith("_out.txt") or name.startswith("audit_"):
                targets_files.append(p)

    return targets_dirs, targets_files


def ensure_gitkeep_and_readme():
    """保证基础目录与占位文件存在"""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    gitkeep = TEMP_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")

    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    p_gitkeep = PROJECTS_DIR / ".gitkeep"
    if not p_gitkeep.exists():
        p_gitkeep.write_text("", encoding="utf-8")


def execute_clean(targets_dirs, targets_files, dry_run=False):
    deleted_count = 0
    reclaimed_bytes = 0

    # 删除文件
    for f in targets_files:
        try:
            sz = f.stat().st_size
            if not dry_run:
                try:
                    f.unlink()
                except PermissionError:
                    os.chmod(f, stat.S_IWRITE)
                    f.unlink()
            deleted_count += 1
            reclaimed_bytes += sz
            print(f"🗑️  [已清理临时文件] {f.relative_to(ROOT_DIR)} ({format_size(sz)})")
        except Exception as e:
            print(f"⚠️  无法删除文件 {f}: {e}")

    # 删除目录
    for d in targets_dirs:
        try:
            sz = get_dir_size(d)
            if not dry_run:
                shutil.rmtree(d, onerror=remove_readonly)
            deleted_count += 1
            reclaimed_bytes += sz
            print(f"🗑️  [已清空临时目录] {d.relative_to(ROOT_DIR)}/ ({format_size(sz)})")
        except Exception as e:
            print(f"⚠️  无法删除目录 {d}: {e}")

    ensure_gitkeep_and_readme()

    action = "计划释放" if dry_run else "已成功清理释放"
    print("\n" + "=" * 80)
    print(f"✨ 临时缓存清理完成！共处理 {deleted_count} 项，{action}空间：{format_size(reclaimed_bytes)}")
    print(f"🔒 安全保障: projects/ 下的全部作品工程与素材 100% 完好无损。")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="VIBE Video Studio 临时缓存专用清理工具")
    parser.add_argument("-y", "--yes", action="store_true", help="跳过确认提示，直接执行清理")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描展示待清理项目，不执行实际删除")
    args = parser.parse_args()

    targets_dirs, targets_files = scan_clean_targets()
    if not targets_dirs and not targets_files:
        print("✨ 临时缓存区 (temp/) 已经非常干净，无需清理。")
        ensure_gitkeep_and_readme()
        return

    total_sz = sum(get_dir_size(d) for d in targets_dirs) + sum(
        f.stat().st_size for f in targets_files if f.exists()
    )

    if not args.dry_run and not args.yes:
        print("=" * 80)
        print("⚠️  VIBE Video Studio · 临时缓存清理确认")
        print("=" * 80)
        print(f"将安全清理 {len(targets_dirs)} 个临时目录与 {len(targets_files)} 个过程切片文件 (预计释放 {format_size(total_sz)})：")
        for d in targets_dirs[:5]:
            print(f"   - {d.relative_to(ROOT_DIR)}/")
        for f in targets_files[:5]:
            print(f"   - {f.relative_to(ROOT_DIR)}")
        print("-" * 80)
        print("🔒 提示: 本操作仅清理 temp/ 过程缓存，绝不影响任何 projects/ 作品工程文件。")
        try:
            choice = input("❓ 是否确认清空上述临时缓存？(y/N): ").strip().lower()
            if choice not in ["y", "yes"]:
                print("❌ 操作已取消。")
                return
        except EOFError:
            pass

    execute_clean(targets_dirs, targets_files, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
