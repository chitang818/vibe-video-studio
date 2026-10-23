# -*- coding: utf-8 -*-
"""VIBE 通用：交付验证（ffprobe 规格 + 音效抽点 + 帧数）
用法: python verify.py <mp4路径> [帧目录]
"""
import os, subprocess, io, json, sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

MP4 = sys.argv[1] if len(sys.argv) > 1 else None
FRAMES = sys.argv[2] if len(sys.argv) > 2 else None
if not MP4:
    print('usage: verify.py <mp4路径> [帧目录]')
    sys.exit(1)
VID = os.path.dirname(os.path.abspath(MP4))

out = []
probe = ['ffprobe','-v','error','-print_format','json','-show_format','-show_streams', MP4]
r = subprocess.run(probe, capture_output=True, text=True, encoding='utf-8', errors='replace')
io.open(os.path.join(VID, '_probe.json'), 'w', encoding='utf-8').write(r.stdout)
d = json.loads(r.stdout)
for s in d['streams']:
    out.append('stream: codec=%s type=%s res=%sx%s fps=%s dur=%s' % (
        s.get('codec_name'), s.get('codec_type'), s.get('width','-'), s.get('height','-'),
        s.get('avg_frame_rate','-'), s.get('duration','-')))
out.append('format: dur=%s size=%s' % (d['format']['duration'], d['format']['size']))

def vol(t0, t1):
    cmd = ['ffmpeg','-ss',str(t0),'-t',str(t1),'-i',MP4,'-map','0:a','-af','volumedetect','-f','null','-']
    rr = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    for line in rr.stderr.splitlines():
        if 'mean_volume' in line:
            return line.strip()
    return 'no-mean'

if FRAMES:
    frames = [f for f in os.listdir(FRAMES) if f.startswith('f') and f.endswith('.jpg')]
    out.append('frames=%d' % len(frames))
    n = len(frames)
    if n > 0:
        out.append('vol@mid: ' + str(vol(n / 2.0 / 20.0, 1.0)))
        out.append('vol@end-1: ' + str(vol((n - 20) / 20.0, 1.0)))

txt = '\n'.join(out)
io.open(os.path.join(VID, '_verify.txt'), 'w', encoding='utf-8').write(txt)
print(txt)
