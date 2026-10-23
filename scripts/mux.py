# -*- coding: utf-8 -*-
"""VIBE 通用：帧序列 + 人声 + 音效轨 → 最终 MP4
用法: python mux.py <帧目录> <人声wav> <输出mp4> <时长秒> [音效表json]
音效表 json 示例: {"whoosh":[26.66,58.39],"pop":[48.63],"ding":[92.1],"chime":[305.0]}
缺省音效表时使用推荐默认点（场景切换 whoosh、关键数字 pop、结尾 chime 前移 9s）。
"""
import io, json, os, subprocess, sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

FRAMES = sys.argv[1] if len(sys.argv) > 1 else None
VOICE = sys.argv[2] if len(sys.argv) > 2 else None
OUT_MP4 = sys.argv[3] if len(sys.argv) > 3 else None
DUR = float(sys.argv[4]) if len(sys.argv) > 4 else None
SFX_JSON = sys.argv[5] if len(sys.argv) > 5 else None

if not FRAMES or not VOICE or not OUT_MP4 or not DUR:
    print("usage: mux.py <帧目录> <人声wav> <输出mp4> <时长秒> [音效表json]")
    sys.exit(1)

VID = os.path.dirname(os.path.abspath(OUT_MP4))
os.makedirs(VID, exist_ok=True)
ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_SOUNDS = ROOT_DIR / "assets" / "sounds"


def run(cmd, tag):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(tag, "FAILED", r.returncode)
        print(r.stderr[-1500:])
        sys.exit(1)
    print(tag, "ok")


# 1) 无声视频轨
silent = os.path.join(VID, "_silent.mp4")
run(
    [
        "ffmpeg", "-y", "-framerate", "20",
        "-i", os.path.join(FRAMES, "f%05d.jpg"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-r", "20", silent,
    ],
    "video",
)

# 2) 音效素材（优先使用本地无损 wav，缺失则 FFmpeg lavfi 虚拟合成，零依赖）
pop = os.path.join(VID, "_pop.wav")
whoosh = os.path.join(VID, "_whoosh.wav")
ding = os.path.join(VID, "_ding.wav")
chime = os.path.join(VID, "_chime.wav")
click = os.path.join(VID, "_click.wav")

if (LOCAL_SOUNDS / "pop.wav").exists():
    pop = str(LOCAL_SOUNDS / "pop.wav")
else:
    run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "sine=frequency=987.77:duration=0.12",
            "-af", "afade=t=in:st=0:d=0.005,afade=t=out:st=0.06:d=0.06",
            "-ar", "44100", pop,
        ],
        "pop",
    )

if (LOCAL_SOUNDS / "whoosh.wav").exists():
    whoosh = str(LOCAL_SOUNDS / "whoosh.wav")
else:
    run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "anoisesrc=color=pink:duration=0.4:amplitude=0.45",
            "-af", "afade=t=in:st=0:d=0.12,afade=t=out:st=0.25:d=0.15,lowpass=f=2200,highpass=f=180",
            "-ar", "44100", whoosh,
        ],
        "whoosh",
    )

if (LOCAL_SOUNDS / "ding.wav").exists():
    ding = str(LOCAL_SOUNDS / "ding.wav")
else:
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "sine=frequency=1760:duration=0.6",
            "-f", "lavfi", "-i", "sine=frequency=2637:duration=0.6",
            "-filter_complex", "[0:a][1:a]amix=inputs=2:weights=1.0 0.4:normalize=0,afade=t=out:st=0.1:d=0.5",
            "-ar", "44100", ding,
        ],
        "ding",
    )

if (LOCAL_SOUNDS / "chime.wav").exists():
    chime = str(LOCAL_SOUNDS / "chime.wav")
else:
    run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "sine=frequency=659:duration=1.2",
            "-f", "lavfi", "-i", "sine=frequency=880:duration=1.2",
            "-f", "lavfi", "-i", "sine=frequency=1318:duration=1.2",
            "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:normalize=0,afade=t=out:st=0.7:d=0.5",
            "-ar", "44100", chime,
        ],
        "chime",
    )

if (LOCAL_SOUNDS / "click.wav").exists():
    click = str(LOCAL_SOUNDS / "click.wav")
else:
    run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "sine=frequency=1450:duration=0.05",
            "-af", "afade=t=out:st=0.01:d=0.04",
            "-ar", "44100", click,
        ],
        "click",
    )

# 3) 按时间戳拼接 sfx 轨（使用 filter_complex_script 杜绝长命令行超限）
if SFX_JSON and os.path.exists(SFX_JSON):
    tbl = json.load(io.open(SFX_JSON, encoding="utf-8"))
    WHOOSH_T = tbl.get("whoosh", [])
    POP_T = tbl.get("pop", [])
    DING_T = tbl.get("ding", [])
    CLICK_T = tbl.get("click", [])
    CHIME_T = tbl.get("chime", [])
else:
    WHOOSH_T, POP_T, DING_T, CLICK_T, CHIME_T = [], [], [], [], [max(0.0, DUR - 5.0)]

inputs, fc, idx = [], [], [0]


def add_sfx(f, times):
    for t in times:
        inputs.extend(["-i", f])
        ms = int(round(t * 1000))
        fc.append(f"[{idx[0]}:a]adelay={ms}|{ms}[s{idx[0]}];")
        idx[0] += 1


add_sfx(whoosh, WHOOSH_T)
add_sfx(pop, POP_T)
add_sfx(ding, DING_T)
add_sfx(click, CLICK_T)
add_sfx(chime, CHIME_T)

if idx[0] > 0:
    mix = "".join(f"[s{i}]" for i in range(idx[0]))
    fc.append(f"{mix}amix=inputs={idx[0]}:normalize=0,volume=0.22,lowpass=f=2800,apad=whole_dur={DUR:.2f}[sfx]")

    script_path = os.path.join(VID, "_sfx_filter.txt")
    with io.open(script_path, "w", encoding="utf-8") as sf:
        sf.write("\n".join(fc))

    run(
        ["ffmpeg", "-y"] + inputs + [
            "-filter_complex_script", script_path,
            "-map", "[sfx]", "-ar", "44100",
            os.path.join(VID, "_sfx.wav"),
        ],
        "sfx",
    )

    final_mix_script = os.path.join(VID, "_final_mix.txt")
    with io.open(final_mix_script, "w", encoding="utf-8") as fmf:
        fmf.write("[1:a][2:a]amix=inputs=2:duration=first:normalize=0[aout]")

    run(
        [
            "ffmpeg", "-y", "-i", silent, "-i", VOICE, "-i", os.path.join(VID, "_sfx.wav"),
            "-filter_complex_script", final_mix_script,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            OUT_MP4,
        ],
        "final",
    )
else:
    run(
        [
            "ffmpeg", "-y", "-i", silent, "-i", VOICE,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
            OUT_MP4,
        ],
        "final",
    )

print("FINAL", OUT_MP4, os.path.getsize(OUT_MP4) if os.path.exists(OUT_MP4) else "MISSING")
