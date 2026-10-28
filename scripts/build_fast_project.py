"""Build protocol-1 VIBE projects. Standard library for packaging; Playwright for visual preflight.
This file is distributed to vibe-video-studio/scripts/build_fast_project.py by sync-studio.ps1.
"""
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import random
import re
import shutil
import struct
import tempfile
import wave
import sys
if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.text_contract import clean, normalized_tokens, strict_loads, validate_rows


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def runtime_root():
    script = Path(__file__).resolve()
    return script.parent.parent/'assets/runtime' if script.name == 'build_fast_project.py' else script.parent


def asset_path(root, relative):
    if not isinstance(relative, str) or not relative or any(c in relative for c in '\\:#?') or any(p in ('', '.', '..') for p in relative.split('/')):
        raise ValueError('Invalid asset path')
    unresolved = root / relative
    import stat
    for path in [unresolved,*unresolved.parents]:
        if path == root.parent: break
        if path.exists() and (path.is_symlink() or getattr(path.lstat(),'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024)):
            raise ValueError('Linked assets are not supported')
    result = unresolved.resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Asset escapes project root')
    return result


def subtitles(rows, duration_us, protected_terms=()):
    chars = []
    last = -1
    for row in rows:
        text = row['Char']
        start = round(float(row['StartSeconds']) * 1e6)
        end = round(float(row['EndSeconds']) * 1e6)
        if start < last or start < 0 or end < start or end > duration_us + 150000:
            raise ValueError('Invalid character timestamps')
        last = start
        if text and not text.isspace():
            chars.append(dict(text=text, startUs=start, endUs=min(end, duration_us)))
    if not chars:
        raise ValueError('Empty character timestamps')
    # Protect explicit technical terms and ASCII strain identifiers/numbers.
    full = ''.join(c['text'] for c in chars)
    protected = set()
    spans = [m.span() for m in re.finditer(r'[A-Za-z0-9][A-Za-z0-9_.%+-]*', full)]
    for term in protected_terms:
        spans += [m.span() for m in re.finditer(re.escape(term), full)]
    for start, end in spans:
        protected.update(range(start + 1, end))
    groups, current = [], []
    position = 0
    for index, c in enumerate(chars):
        current.append(c)
        position += len(c['text'])
        length = sum(len(x['text']) for x in current)
        boundary = c['text'] in '，、：；。！？'
        next_time = index+1 == len(chars) or chars[index+1]['startUs'] > c['startUs']
        if (boundary and length >= 4 or length >= 10) and position not in protected and next_time:
            groups.append(current)
            current = []
    if current:
        if groups and sum(len(c['text']) for c in current) < 4:
            groups[-1] += current
        else:
            groups.append(current)
    units = []
    for i, group in enumerate(groups):
        while group and group[-1]['text'] in '，、：；':
            group = group[:-1]
        if not group:
            continue
        start = group[0]['startUs']
        # Identical timestamp boundary belongs to the next unit; no overlapping captions.
        end = groups[i+1][0]['startUs'] if i+1 < len(groups) else min(duration_us, max(group[-1]['startUs']+1, group[-1]['endUs']))
        if end <= start:
            raise ValueError('Subtitle unit has zero duration')
        units.append(dict(startUs=start, endUs=end, chars=[dict(text=c['text'], startUs=c['startUs']) for c in group]))
    return units


def editorial_subtitles(rows, groups, duration_us):
    """Explicit semantic windows; preserve source punctuation and character timing."""
    if not isinstance(groups, list) or not groups or not all(isinstance(g, str) and g for g in groups):
        raise ValueError('Caption groups must be a nonempty array of strings')
    validate_rows(rows, duration_us)
    if ''.join(clean(g) for g in groups) != clean(''.join(r['Char'] for r in rows)):
        raise ValueError('Editorial captions do not exactly match original narration')
    from collections import Counter
    content_counts=Counter(i for _,i in normalized_tokens([(c,i) for i,r in enumerate(rows) for c in r['Char']]))
    units, pos = [], 0
    for text in groups:
        chars, count = [], 0
        while pos < len(rows) and count < len(clean(text)):
            row = rows[pos]; pos += 1
            count += content_counts[pos-1]
            if row['Char'].strip():
                chars.append(dict(text=row['Char'], startUs=round(row['StartSeconds']*1e6)))
        if count != len(clean(text)):
            raise ValueError('Caption group cannot split a timestamp row')
        while pos < len(rows) and not content_counts[pos]:
            row = rows[pos]; pos += 1
            if row['Char'].strip():
                chars.append(dict(text=row['Char'], startUs=round(row['StartSeconds']*1e6)))
        while chars and chars[-1]['text'] in '，、：；':
            chars.pop()
        if not chars:
            raise ValueError('Empty caption window')
        units.append(dict(startUs=chars[0]['startUs'], endUs=duration_us, chars=chars))
    for i,u in enumerate(units):
        if i+1<len(units):
            u['endUs']=units[i+1]['startUs']
        if u['chars'][-1]['startUs'] >= u['endUs']:
            raise ValueError('Caption boundaries cannot split identical timestamps')
    return units


def preset_wave(path, kind):
    durations = {'pop': .18, 'click': .08, 'ding': .5, 'whoosh': .45, 'chime': 1.2}
    if kind not in durations:
        raise ValueError('Unknown named sound preset')
    rate = 48000
    rng = random.Random(20261026)
    values = []
    filtered = 0.0
    # Materialize warm sound assets, independent of the unchanged shared audio runtime.
    alpha = 1 - math.exp(-2 * math.pi * 2400 / rate)
    for i in range(round(rate * durations[kind])):
        t = i / rate
        if kind == 'whoosh':
            v = (rng.random()*2-1)*math.sin(math.pi*t/durations[kind])**2*.12
        elif kind == 'chime':
            v = sum(math.sin(2*math.pi*f*t) for f in (523.25, 659.25, 783.99)) / 3 * math.exp(-t*4)*.2
        else:
            frequency = {'pop': 460, 'click': 1200, 'ding': 1046.5}[kind]
            v = math.sin(2*math.pi*frequency*t)*math.exp(-t*12)*.22
        filtered += alpha * (v-filtered)
        values.append(struct.pack('<h', round(filtered*32767)))
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(b''.join(values))


def verify(root):
    root = Path(root).resolve()
    manifest = strict_loads((root/'vibe.project.json').read_text(encoding='utf-8'))
    if manifest['schemaVersion'] != 1 or manifest['runtimeVersion'] != '1.2.0':
        raise ValueError('Unsupported project version')
    if manifest['runtimeSha256'] != digest(runtime_root()/'scene.mjs'):
        raise ValueError('Project runtime is outdated; rebuild using the current Studio runtime')
    for name, expected in manifest['assetHashes'].items():
        if digest(asset_path(root, name)) != expected:
            raise ValueError('Changed asset: ' + name)
    if digest(root/'vibe-runtime/scene.mjs') != manifest['runtimeSha256']:
        raise ValueError('Runtime fingerprint mismatch')
    return manifest


def audit(root):
    from playwright.sync_api import sync_playwright
    manifest = verify(root)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(viewport={'width': manifest['width'], 'height': manifest['height']}, device_scale_factor=1)
            page.goto((Path(root).resolve()/manifest['htmlFile']).as_uri())
            result = page.evaluate('''async()=>{await window.__vibe_ready;
                if(!window.__vibe_getLayout)throw Error('Missing deterministic renderer');
                return {ready:true,scenes:window.__vibe_scene.scenes.length};}''')
            if not result['ready']:
                raise ValueError('Visual audit failed')
        finally:
            browser.close()


def build(args):
    from scripts.background_library import verify_runtime
    verify_runtime(args.runtime.resolve())
    source = args.scene.resolve()
    target = args.out.resolve()
    runtime = args.runtime.resolve()
    if args.width != 1080 or args.height != 1920:
        raise ValueError('knowledge-portrait-v1 requires 1080x1920')
    if target.exists():
        raise ValueError('Output directory already exists; choose a new version directory')
    scene = strict_loads(source.read_text(encoding='utf-8-sig'))
    duration = args.duration_us
    if args.voice:
        with wave.open(str(args.voice), 'rb') as f:
            audio_duration = round(f.getnframes()/f.getframerate()*1e6)
        if duration is not None and abs(duration-audio_duration) > 150000:
            raise ValueError('Declared duration does not match voice')
        duration = audio_duration
    if not duration or duration <= 0 or duration > 7200e6:
        raise ValueError('A valid duration or WAV voice is required')
    if scene['scenes'][0]['startUs'] != 0 or scene['scenes'][-1]['endUs'] != duration:
        raise ValueError('Scene timeline must exactly match audio duration; inspect WAV frame duration first')
    if args.voice and not args.timestamps:
        raise ValueError('Voice requires original character timestamps')
    if args.timestamps:
        rows = strict_loads(args.timestamps.read_text(encoding='utf-8-sig'))
        validate_rows(rows, duration)
        groups = getattr(args, 'caption_groups', None)
        scene['subtitles'] = (editorial_subtitles(rows, strict_loads(groups.read_text(encoding='utf-8-sig')), duration)
            if groups else subtitles(rows, duration, scene.get('protectedTerms', [])))
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.vibe-build-', dir=target.parent))
    try:
        (staging/'vibe-runtime').mkdir()
        shutil.copyfile(runtime/'scene.mjs', staging/'vibe-runtime/scene.mjs')
        shutil.copyfile(runtime/'audio.mjs', staging/'vibe-runtime/audio.mjs')
        assets = set()
        def copy(name, original):
            destination = asset_path(staging, name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination); assets.add(name)
        for s in scene['scenes']:
            for n in s['nodes']:
                if n.get('type') == 'image':
                    copy(n['source'], asset_path(source.parent, n['source']))
        if (source.parent/'story.json').exists():copy('story.json',source.parent/'story.json')
        if (source.parent/'assets/media-registry.json').exists():
            copy('assets/media-registry.json',source.parent/'assets/media-registry.json')
        voice_file = timestamps_file = None
        if args.voice:
            voice_file = 'assets/voice.wav'; copy(voice_file, args.voice)
        if args.timestamps:
            timestamps_file = 'assets/char_timestamps.json'; copy(timestamps_file, args.timestamps)
        script_file = None
        if getattr(args, 'script', None):
            script_file = 'assets/script.txt'; copy(script_file, args.script)
        sound_track = {'version': 1, 'events': []}
        if args.sfx:
            sound_data = strict_loads(args.sfx.read_text(encoding='utf-8-sig'))
            if sound_data.get('version') == 1:
                sound_track = sound_data
                for e in sound_track['events']:
                    copy(e['source'], asset_path(args.sfx.parent, e['source']))
            else:
                for kind, times in sound_data.items():
                    name = 'assets/sounds/'+kind+'.wav'
                    path = asset_path(staging, name); path.parent.mkdir(parents=True, exist_ok=True)
                    preset_wave(path, kind); assets.add(name)
                    for t in times:
                        sound_track['events'].append(dict(timeUs=round(float(t)*1e6), source=name, gain=1))
        if len(sound_track['events']) > 512:
            raise ValueError('Too many sound events')
        for e in sound_track['events']:
            if not 0 <= e['timeUs'] < duration or not 0 <= e.get('gain', 1) <= 2:
                raise ValueError('Invalid sound timing or gain')
        (staging/'sfx.json').write_text(json.dumps(sound_track, ensure_ascii=False, indent=2), encoding='utf-8')
        (staging/'scene.json').write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding='utf-8')
        from scripts.preview_template import render_html
        html = render_html(staging, scene, args.width, args.height, duration, voice_file, sound_track, runtime, args.title)
        (staging/'index.html').write_text(html, encoding='utf-8')
        assets.update(['vibe-runtime/scene.mjs','vibe-runtime/audio.mjs','scene.json','index.html','sfx.json'])
        manifest = dict(schemaVersion=1, runtimeVersion='1.2.0', runtimeSha256=digest(runtime/'scene.mjs'), title=args.title,
            width=args.width, height=args.height, durationUs=duration, htmlFile='index.html', sceneFile='scene.json',
            voiceFile=voice_file, timestampsFile=timestamps_file, sfxFile='sfx.json',
            assetHashes={name:digest(staging/name) for name in sorted(assets)})
        (staging/'vibe.project.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        verify(staging)
        if not args.skip_browser_audit:
            audit(staging)
        staging.rename(target)
    except BaseException:
        if staging.resolve().parent != target.parent.resolve() or not staging.name.startswith('.vibe-build-'):
            raise RuntimeError('Refusing to clean a directory outside the build staging area')
        shutil.rmtree(staging)
        raise
    print('草稿工程已生成；技术预检不代表创意验收或正式交付。请填写 quality-plan.json，执行 audit、复核证据，再执行 pack。')
    print(str(target/'vibe.project.json'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scene', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--runtime', type=Path, default=runtime_root())
    p.add_argument('--title', required=True); p.add_argument('--width', type=int, default=1080); p.add_argument('--height', type=int, default=1920)
    p.add_argument('--duration-us', type=int); p.add_argument('--voice',type=Path); p.add_argument('--timestamps',type=Path);p.add_argument('--sfx',type=Path)
    p.add_argument('--script',type=Path); p.add_argument('--caption-groups',type=Path)
    p.add_argument('--skip-browser-audit',action='store_true',help='Only for controlled tests; not a visual acceptance result')
    build(p.parse_args())

if __name__=='__main__':
    main()
