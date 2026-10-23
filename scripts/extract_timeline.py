# -*- coding: utf-8 -*-
"""VIBE 工具链：从字级时间戳 JSON 提取关键句/词的时间点
用法:
    python scripts/extract_timeline.py <char_timestamps.json> <keywords.txt> [-o output.txt]
keywords.txt 格式（每行）：
    关键词|标签
    或单纯写 关键词
输出：
    控制台打印 + 输出到文本文件
"""
import argparse
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
SFX_PRESETS_PATH = ROOT_DIR / "assets" / "sounds" / "sfx_presets.json"

STRIP_RE = re.compile(r'[^\w\s%~\-\u4e00-\u9fff]', re.UNICODE)


def clean_text(s: str) -> str:
    return STRIP_RE.sub('', s)


def build_timeline_index(timestamp_items):
    """
    构建映射表：记录清洗后字符到原始时间戳列表下标的严格映射，
    彻底解决因过滤标点符号导致的下标偏移问题。
    """
    chars = [item.get('Char', '') for item in timestamp_items]
    times = [float(item.get('StartSeconds', 0.0)) for item in timestamp_items]
    end_times = [float(item.get('EndSeconds', item.get('StartSeconds', 0.0))) for item in timestamp_items]

    clean_chars = []
    orig_indices = []

    for orig_idx, ch in enumerate(chars):
        cleaned_ch = clean_text(ch)
        for c in cleaned_ch:
            clean_chars.append(c)
            orig_indices.append(orig_idx)

    text_clean = ''.join(clean_chars)
    return {
        'chars': chars,
        'times': times,
        'end_times': end_times,
        'text_clean': text_clean,
        'orig_indices': orig_indices,
    }


def find_keyword(index_data, keyword: str):
    cleaned_kw = clean_text(keyword)
    if not cleaned_kw:
        return None

    text_clean = index_data['text_clean']
    pos = text_clean.find(cleaned_kw)
    if pos < 0:
        return None

    raw_start_idx = index_data['orig_indices'][pos]
    raw_end_idx = index_data['orig_indices'][pos + len(cleaned_kw) - 1]

    start_time = index_data['times'][raw_start_idx]
    end_time = index_data['end_times'][raw_end_idx]

    return {
        'start_idx': raw_start_idx,
        'end_idx': raw_end_idx,
        'start_time': start_time,
        'end_time': end_time,
        'matched_char': index_data['chars'][raw_start_idx],
    }


def load_sfx_presets():
    """从单一事实源 assets/sounds/sfx_presets.json 加载音效语义映射表与节流规则"""
    default_table = {
        "whoosh": {"tags": ["whoosh", "转场", "场景", "切幕", "阶段", "节", "然而", "但是", "随后", "过渡"], "min_interval": 2.5},
        "pop": {"tags": ["pop", "数字", "数据", "百分比", "年份", "倍数", "增长", "暴跌", "万", "亿", "元", "%", "比重", "金额"], "min_interval": 0.6},
        "ding": {"tags": ["ding", "重点", "核心", "顿悟", "秘密", "关键", "结论", "反差", "真相", "本质", "突破", "致命", "痛点"], "min_interval": 3.0},
        "chime": {"tags": ["chime", "结尾", "总结", "关注", "cta", "下期见", "收束", "点赞", "收藏", "预告", "复盘"], "min_interval": 10.0},
        "click": {"tags": ["click", "点击", "触控", "步骤", "清单", "游标", "打字", "脉冲"], "min_interval": 0.15},
    }
    if SFX_PRESETS_PATH.exists():
        try:
            with io.open(SFX_PRESETS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            presets = data.get("presets", {})
            for name, meta in presets.items():
                tags = meta.get("semantic_tags", [])
                interval = meta.get("constraints", {}).get("min_interval_sec", 0.5)
                default_table[name] = {"tags": tags, "min_interval": interval}
        except Exception:
            pass
    return default_table


def process_keywords(ts_path: str, kw_path: str, out_path: str = None, sfx_path: str = None):
    if not os.path.exists(ts_path):
        raise FileNotFoundError(f"时间戳文件不存在: {ts_path}")
    if not os.path.exists(kw_path):
        raise FileNotFoundError(f"关键词文件不存在: {kw_path}")

    with io.open(ts_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    index_data = build_timeline_index(data)
    out_lines = []

    sfx_config = load_sfx_presets()
    raw_sfx_hits = {k: [] for k in sfx_config}

    with io.open(kw_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '|' in line:
                parts = line.split('|', 1)
                key, tag = parts[0].strip(), parts[1].strip()
            else:
                key, tag = line, line

            res = find_keyword(index_data, key)
            if res:
                t = round(res['start_time'], 2)
                row = f"{tag} | {key} | t={t:.2f}s (end={res['end_time']:.2f}s) | idx={res['start_idx']}"
                
                # 语义特征智能匹配
                tag_lower = tag.lower()
                key_lower = key.lower()
                matched_sound = None

                for sound_name, sound_info in sfx_config.items():
                    if any(w in tag_lower or w in key_lower for w in sound_info["tags"]):
                        matched_sound = sound_name
                        break

                if not matched_sound and (re.search(r'\d', key) or any(w in tag_lower for w in ['数字', '数据', '年份'])):
                    matched_sound = "pop"

                if matched_sound:
                    raw_sfx_hits[matched_sound].append(t)
            else:
                row = f"{tag} | {key} | NOT FOUND"
            print(row)
            out_lines.append(row)

    if not out_path:
        out_path = kw_path + '_out.txt'

    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))
    print(f"\n结果已写入: {out_path}")

    # 若指定了 sfx 输出路径或同级自动生成
    if not sfx_path:
        base_dir = os.path.dirname(os.path.abspath(out_path))
        sfx_path = os.path.join(base_dir, "sfx.json")

    # 节流与去重过滤 (Throttling)
    sfx_table = {}
    for sound_name, hits in raw_sfx_hits.items():
        hits = sorted(list(set(hits)))
        min_intv = sfx_config.get(sound_name, {}).get("min_interval", 0.5)
        filtered = []
        last_t = -999.0
        for h in hits:
            if h - last_t >= min_intv:
                filtered.append(h)
                last_t = h
        sfx_table[sound_name] = filtered

    has_sfx = any(len(v) > 0 for v in sfx_table.values())
    if has_sfx or sfx_path:
        with io.open(sfx_path, 'w', encoding='utf-8') as sf:
            json.dump(sfx_table, sf, indent=2, ensure_ascii=False)
        print(f"音效时间表已自动导出 (带节流保护): {sfx_path}")

    return out_lines


def main():
    parser = argparse.ArgumentParser(description="从字级时间戳 JSON 中精确提取关键句与关键词的发音时间点，并可自动生成 SFX 音效表")
    parser.add_argument("timestamps", help="字级时间戳 JSON 文件路径 (如 char_timestamps.json)")
    parser.add_argument("keywords", help="关键词列表文件 (每行: 关键词|标签 或 纯关键词)")
    parser.add_argument("-o", "--output", help="输出文件路径 (默认: <keywords>_out.txt)", default=None)
    parser.add_argument("--sfx-out", help="音效表 JSON 输出路径 (默认在输出目录生成 sfx.json)", default=None)
    args = parser.parse_args()

    process_keywords(args.timestamps, args.keywords, args.output, args.sfx_out)


if __name__ == '__main__':
    main()
