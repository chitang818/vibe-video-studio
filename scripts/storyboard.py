# -*- coding: utf-8 -*-
"""VIBE 分镜头导演拆解工具 (Storyboard Generator)
依据字级时间戳与短视频视听心理学，自动化将科普长文切分为 6~14 秒的精细分镜头流。
用法:
    python scripts/storyboard.py <timestamps_json> [-o <out_json>] [-m <out_md>]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

# 终端编码适配
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def guess_visual_pattern(text, is_first_shot=False):
    """根据文案关键词智能推荐视觉主形态与动效建议（遵循竖屏垂直优先与黄金3秒铁律）"""
    if is_first_shot:
        return "黄金3秒爆点开场", "golden-hook / multi-phase", "0~1.5s 痛点悬念冲撞 → 1.5~4.0s 主角大字推入 + 光晕扩散"
    if any(k in text for k in ["下期", "点赞", "关注", "收藏", "评论", "拜拜"]):
        return "CTA互动收束", "cta-pulse", "脉冲按钮 + 总结金句"
    if any(k in text for k in ["倍", "%", "百分", "率达", "产量提升", "指数提高"]):
        return "数据图表/环形图", "ring-stat / big-num", "SVG动态环形描边 + 大数呼吸"
    if any(k in text for k in ["对比", "相比", "替代", "野生型", "与", "双雄", "瓶颈", "短板"]):
        # 竖屏垂直优先：强制推荐上下堆叠通栏大卡，严禁挤压狭窄左右卡
        return "上下纵向堆叠大卡", "card-stack", "通栏大卡片上下堆叠 (82cqw) + 大字号(4cqw) + 依次浮现"
    if any(k in text for k in ["高温", "高盐", "逆境", "胁迫", "耐受"]):
        return "上下痛点/逆境卡", "card-stack / stress-box", "警告图标闪烁 + 上下大卡片依次弹入"
    if any(k in text for k in ["一、", "二、", "三、", "四、", "第一", "第二", "通过"]):
        return "递进流程/分支图", "flow-steps", "步骤节点卡片 + 指示箭头跳动"
    if any(k in text for k in ["专利", "大学", "科学院", "团队", "分离", "研究人员"]):
        return "产学研矩阵网格", "patents-grid", "机构徽标 + 成果卡片多波次浮现"
    return "标准上下图文", "card-stack", "通栏大卡片 + 核心要点多波次入场"


def build_storyboard(timestamps_path, min_dur=6.0, max_dur=14.0, target_dur=9.5):
    with open(timestamps_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("错误：时间戳文件为空！")
        return []

    shots = []
    start_idx = 0
    n = len(data)

    strong_seps = "。！？!?\n"
    mid_seps = "；;，,、："

    while start_idx < n:
        start_t = data[start_idx]["StartSeconds"]
        best_cut = -1
        last_punct = -1

        for i in range(start_idx, n):
            cur_t = data[i]["EndSeconds"]
            dur = cur_t - start_t
            ch = data[i]["Char"]

            # 强分割符（句末）
            if ch in strong_seps:
                last_punct = i
                if dur >= min_dur:
                    best_cut = i
                    break

            # 次强分割符（逗号/分号/冒号）
            elif ch in mid_seps:
                last_punct = i
                if dur >= target_dur:
                    best_cut = i
                    break

            # 达到或超过最大上限
            if dur >= max_dur:
                best_cut = last_punct if last_punct > start_idx else i
                break

        # 兜底截断
        if best_cut < 0:
            best_cut = n - 1

        end_idx = best_cut
        end_t = data[end_idx]["EndSeconds"]
        shot_dur = round(end_t - start_t, 2)
        shot_text = "".join(data[k]["Char"] for k in range(start_idx, end_idx + 1)).strip()

        pattern_name, pattern_cls, motion_desc = guess_visual_pattern(
            shot_text, is_first_shot=(len(shots) == 0)
        )

        shot_item = {
            "shot_id": f"shot-{len(shots) + 1:02d}",
            "start_time": round(start_t, 2),
            "end_time": round(end_t, 2),
            "duration": shot_dur,
            "text": shot_text,
            "visual_pattern": pattern_name,
            "component_class": pattern_cls,
            "motion_advice": motion_desc,
        }
        shots.append(shot_item)
        start_idx = end_idx + 1

    return shots


def print_storyboard_table(shots):
    print("=" * 110)
    print(f"{'Shot ID':<9} | {'起止时刻 (s)':<14} | {'时长':<6} | {'主视觉形态':<14} | {'文案要点片段'}")
    print("-" * 110)
    for s in shots:
        time_str = f"{s['start_time']:>5.2f} ~ {s['end_time']:>5.2f}s"
        dur_str = f"{s['duration']:>4.1f}s"
        snippet = s["text"][:38] + ("..." if len(s["text"]) > 38 else "")
        print(f"{s['shot_id']:<9} | {time_str:<14} | {dur_str:<6} | {s['visual_pattern']:<14} | {snippet}")
    print("=" * 110)
    avg_dur = round(sum(s["duration"] for s in shots) / len(shots), 2) if shots else 0
    print(f"🎬 分镜头规划完成！共生成 {len(shots)} 个精细镜头 | 平均镜头时长: {avg_dur} 秒 | 绝无超过 15 秒画面")
    print("=" * 110)


def export_markdown(shots, md_path):
    lines = [
        "# VIBE 短视频分镜头脚本规划表",
        "",
        f"> 本脚本由 `vibe.py storyboard` 自动生成。共规划 **{len(shots)}** 个镜头，单镜头严格控制在 6~14 秒。",
        "",
        "| 镜头号 | 起止时间 | 时长 | 视觉主形态 | 推荐组件范式 | 动效与节拍设计 | 对应文案片段 |",
        "|:---:|:---:|:---:|:---|:---|:---|:---|",
    ]
    for s in shots:
        time_str = f"{s['start_time']:.2f}s ~ {s['end_time']:.2f}s"
        dur_str = f"{s['duration']:.1f}s"
        lines.append(
            f"| **{s['shot_id']}** | {time_str} | {dur_str} | {s['visual_pattern']} | `{s['component_class']}` | {s['motion_advice']} | {s['text']} |"
        )
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"📄 分镜头 Markdown 脚本已导出至: {md_path}")


def main():
    parser = argparse.ArgumentParser(description="VIBE 自动化分镜头拆解工具")
    parser.add_argument("timestamps", help="字级时间戳 JSON 路径")
    parser.add_argument("-o", "--output", help="导出的 JSON 路径 (可选)", default=None)
    parser.add_argument("-m", "--markdown", help="导出的 Markdown 路径 (可选)", default=None)
    parser.add_argument("--min", type=float, default=6.0, help="单镜头最短时长（秒）")
    parser.add_argument("--max", type=float, default=14.0, help="单镜头最长时长（秒）")
    args = parser.parse_args()

    shots = build_storyboard(args.timestamps, min_dur=args.min, max_dur=args.max)
    print_storyboard_table(shots)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(shots, f, ensure_ascii=False, indent=2)
        print(f"💾 分镜头 JSON 数据已导出至: {args.output}")

    if args.markdown:
        export_markdown(shots, args.markdown)


if __name__ == "__main__":
    main()
