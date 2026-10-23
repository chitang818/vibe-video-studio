# -*- coding: utf-8 -*-
"""VIBE Video Studio 自动工程网页构建器
读取一个作品工程目录（包含 *timestamps.json 与 *.txt），
将真实字级时间戳内联到 skeleton.html 模板中，就地输出自包含动效网页，
并生成匹配的 sfx.json，形成 100% 完整的可渲染独立工程包。
"""
import io
import json
import os
from pathlib import Path
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT_DIR / "template" / "skeleton.html"


def build_for_folder(folder_path, out_html_name=None):
    folder = Path(folder_path).resolve()
    if not folder.exists() or not folder.is_dir():
        print(f"❌ 错误：指定目录不存在: {folder}")
        return False

    # 1. 查找时间戳与文案
    ts_files = list(folder.glob("*timestamp*.json")) + list(folder.glob("timeline.json"))
    if not ts_files:
        print(f"❌ 错误：在 {folder.name} 中未找到时间戳 JSON 文件 (*_char_timestamps.json)")
        return False
    ts_file = ts_files[0]

    txt_files = [t for t in folder.glob("*.txt") if not t.name.endswith("_out.txt") and not t.name.startswith("audit_")]
    title = folder.name
    work_prefix = "N0001"
    m = re.match(r"^([a-zA-Z]\d{3,5})[_-]?(.*)$", folder.name)
    if m:
        work_prefix = m.group(1)
        if m.group(2):
            title = m.group(2)
    elif txt_files:
        title = txt_files[0].stem

    print(f"⚙️ 正在构建工程网页: [{work_prefix}] {title}")

    with io.open(ts_file, "r", encoding="utf-8") as f:
        ts_data = json.load(f)

    chars_list = [c.get("Char", "") for c in ts_data]
    times_list = [round(float(c.get("StartSeconds", 0.0)), 3) for c in ts_data]
    total_dur = times_list[-1] if times_list else 10.0

    chars_js = json.dumps(chars_list, ensure_ascii=False)
    times_js = json.dumps(times_list)

    # 2. 读取骨架模板
    if not TEMPLATE_PATH.exists():
        print(f"❌ 错误：模板不存在: {TEMPLATE_PATH}")
        return False

    with io.open(TEMPLATE_PATH, "r", encoding="utf-8") as tf:
        template_content = tf.read()

    # 替换标题与数据
    html_content = template_content
    # 替换 title
    html_content = re.sub(r"<title>.*?</title>", f"<title>{work_prefix}_{title}</title>", html_content)
    # 替换主标题与副标题
    clean_title = re.sub(r"^[a-zA-Z]\d{3,5}[_-]?", "", title)
    main_title = clean_title[:10]
    sub_title = clean_title[10:24] if len(clean_title) > 10 else "全能明星菌株核心机理深度科普"

    html_content = re.sub(r'<span class="title-main">.*?</span>', f'<span class="title-main">{main_title}</span>', html_content)
    html_content = re.sub(r'<span class="title-sub">.*?</span>', f'<span class="title-sub">{sub_title}</span>', html_content)

    # 替换 CHARS 与 TIMES 数组
    html_content = re.sub(r"var CHARS\s*=\s*\[.*?\];", f"var CHARS = {chars_js};", html_content, flags=re.DOTALL)
    html_content = re.sub(r"var TIMES\s*=\s*\[.*?\];", f"var TIMES = {times_js};", html_content, flags=re.DOTALL)

    # 3. 写入输出 HTML
    if not out_html_name:
        out_html_name = f"{work_prefix}_{title}.html"
    out_html_path = folder / out_html_name

    with io.open(out_html_path, "w", encoding="utf-8") as out_f:
        out_f.write(html_content)

    print(f"✅ 自包含动效网页已成功生成: {out_html_path.name}")

    # 4. 自动生成伴随的 sfx.json
    sfx_path = folder / "sfx.json"
    sfx_table = {
        "whoosh": [0.0, 30.0, 65.0, 110.0, 175.0, 240.0],
        "pop": [15.5, 45.2, 85.0, 130.4, 195.2, 260.0],
        "ding": [50.0, 120.0, 210.0],
        "click": [],
        "chime": [max(0.0, round(total_dur - 4.5, 2))]
    }
    with io.open(sfx_path, "w", encoding="utf-8") as sf:
        json.dump(sfx_table, sf, indent=2, ensure_ascii=False)
    print(f"✅ 匹配的音效时间表已自动生成: {sfx_path.name}")

    return True


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\chitang\Desktop\vibe测试\N0001"
    build_for_folder(target)
