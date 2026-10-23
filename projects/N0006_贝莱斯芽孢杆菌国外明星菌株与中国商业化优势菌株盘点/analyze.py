import json
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

with open('inputs/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点/char_timestamps.json', 'r', encoding='utf-8') as f:
    ts = json.load(f)

sentences = []
cur_chars = []
cur_start = None

for item in ts:
    ch = item['Char']
    st = item['StartSeconds']
    et = item['EndSeconds']
    if cur_start is None:
        cur_start = st
    cur_chars.append(ch)
    if ch in ['。', '！', '？']:
        text = ''.join(cur_chars)
        sentences.append({'text': text.strip(), 'start': cur_start, 'end': et, 'dur': round(et - cur_start, 2)})
        cur_chars = []
        cur_start = None

if cur_chars:
    sentences.append({'text': ''.join(cur_chars).strip(), 'start': cur_start, 'end': ts[-1]['EndSeconds'], 'dur': round(ts[-1]['EndSeconds'] - cur_start, 2)})

with open('inputs/N0006_贝莱斯芽孢杆菌国外明星菌株与中国商业化优势菌株盘点/sentences_timeline.json', 'w', encoding='utf-8') as out:
    json.dump(sentences, out, ensure_ascii=False, indent=2)

print(f"Total sentences: {len(sentences)}")
for i, s in enumerate(sentences):
    t = s['text'].replace('\n', '')
    print(f"{i+1:2d} | [{s['start']:6.2f}s - {s['end']:6.2f}s | {s['dur']:5.2f}s] {t}")
