"""Canonical preview shell. Agents author scene data; executable HTML is generated only here."""
import base64
import json
import re
from html import escape

TEMPLATE_VERSION = 6


def render_html(root, scene, width, height, duration, voice_file, sound_track, runtime, title='VIBE', preview_window=None):
    js = (runtime/'scene.mjs').read_text(encoding='utf-8')
    js = re.sub(r'(?m)^export ', '', js)
    js += '\n' + re.sub(r'(?m)^export ', '', (runtime/'audio.mjs').read_text(encoding='utf-8'))
    data = json.dumps(scene, ensure_ascii=False).replace('<', '\\u003c')
    inline_sounds = {name:'data:audio/wav;base64,'+base64.b64encode((root/name).read_bytes()).decode('ascii')
        for name in sorted(set(e['source'] for e in sound_track['events']))}
    import mimetypes
    inline_images={n['source']:'data:'+mimetypes.guess_type(n['source'])[0]+';base64,'+base64.b64encode((root/n['source']).read_bytes()).decode('ascii') for sh in scene['scenes'] for n in sh['nodes'] if n['type']=='image'}
    settings = json.dumps(dict(width=width, height=height, durationUs=duration, assetBase='', safeArea=True,
        voiceUrl=voice_file, sounds=sound_track, inlineSounds=inline_sounds, inlineImages=inline_images, sfxGain=.08, fadeOut=True)).replace('<', '\\u003c')
    player = '''const data=SCENE_DATA;const config=PROJECT_CONFIG;config.assetBase=new URL('./',location.href).href;
window.__vibe_scene=data;window.__vibe_ready=prepareScene(document.querySelector('canvas'),data,config).then(async r=>{
const hud=document.querySelector('#chapText');
const progress=document.querySelector('#seek'),timeLabel=document.querySelector('#time'),button=document.querySelector('button'),audio=document.querySelector('audio');
let playing=false,completed=false,scrubbing=false;
function formatTime(seconds){seconds=Math.max(0,Math.floor(seconds));const h=Math.floor(seconds/3600),m=Math.floor(seconds%3600/60),s=seconds%60;
return (config.durationUs>=3600000000?String(h).padStart(2,'0')+':':'')+String(m).padStart(2,'0')+':'+String(s).padStart(2,'0');}
function updateProgress(t){const seconds=Math.max(0,Math.min(config.durationUs,t))/1e6;if(!scrubbing)progress.value=seconds;
timeLabel.textContent=formatTime(seconds)+' / '+formatTime(config.durationUs/1e6);progress.setAttribute('aria-valuetext',timeLabel.textContent);}
function updateButton(){button.textContent=completed?'重播':playing?'暂停':'播放';button.setAttribute('aria-pressed',String(playing));}
function updateHud(t){let lo=0,hi=data.scenes.length-1;while(lo<hi){const m=Math.ceil((lo+hi)/2);if(data.scenes[m].startUs<=t)lo=m;else hi=m-1;}
hud.textContent='第 '+(lo+1)+' / '+data.scenes.length+' 节';hud.dataset.sceneId=data.scenes[lo].id;updateProgress(t);}
const previewRenderer={renderAt(t){r.renderAt(t);updateHud(t);}};
const player=await createPreviewPlayer(document.querySelector('audio'),previewRenderer,config,config.sounds);updateHud(0);
function seekTo(t){completed=false;player.seek(t);updateButton();}
window.__vibe_seekTo=seekTo;
window.__vibe_getLayout=t=>r.layoutAt(Math.round(t*1e6));
window.__vibe_textRaster=(sceneId,nodeId)=>r.textRaster(sceneId,nodeId);
progress.max=config.durationUs/1e6;progress.disabled=false;button.disabled=false;updateButton();
progress.addEventListener('input',()=>seekTo(Number(progress.value)));
progress.addEventListener('pointerdown',()=>{scrubbing=true;});
function finishScrub(){if(!scrubbing)return;scrubbing=false;updateProgress(config.voiceUrl?audio.currentTime*1e6:Number(progress.value)*1e6);}
window.addEventListener('pointerup',finishScrub);window.addEventListener('pointercancel',finishScrub);
audio.addEventListener('play',()=>{playing=!audio.paused;updateButton();});audio.addEventListener('pause',()=>{playing=!audio.paused;updateButton();});
for(const event of ['timeupdate','seeked'])audio.addEventListener(event,()=>{if(!completed)updateProgress(audio.currentTime*1e6);});
audio.addEventListener('ended',()=>{completed=true;player.pause();updateProgress(config.durationUs);updateButton();});
button.onclick=async()=>{try{if(completed){completed=false;player.seek(0);}await player.toggle();playing=config.voiceUrl?!audio.paused:!playing;updateButton();}catch(e){document.querySelector('output').textContent=e.message;}};
document.addEventListener('keydown',e=>{if(e.code==='Space'&&!e.repeat&&!(e.target instanceof HTMLInputElement)){e.preventDefault();button.click();}});
return true;});window.__vibe_ready.catch(e=>{document.querySelector('output').textContent=e.message;});'''
    if preview_window:
        origin=preview_window['originUs'];total=preview_window['totalDurationUs']
        if type(origin)!=int or type(total)!=int or not 0<=origin<origin+duration<=total:raise ValueError('Invalid single-shot preview window')
        player=player.replace("prepareScene(document.querySelector('canvas'),data,config)",f"prepareScene(document.querySelector('canvas'),data,{{...config,durationUs:{total}}})")
        player=player.replace('r.renderAt(t);updateHud(t);',f'r.renderAt(t+{origin});updateHud(t);')
        player=player.replace('function updateHud(t){',f'function updateHud(t){{t+={origin};')
        player=player.replace('updateProgress(t);}',f'updateProgress(t-{origin});}}')
        player=player.replace('r.layoutAt(Math.round(t*1e6))',f'r.layoutAt(Math.round(t*1e6)+{origin})')
        player=player.replace("hud.textContent='第 '+(lo+1)+' / '+data.scenes.length+' 节';",f"hud.textContent='第 {preview_window['shotIndex']+1} / {preview_window['shotCount']} 节';")
        player=player.replace('return true;});','seekTo(0);return true;});')
    player = player.replace('SCENE_DATA', data).replace('PROJECT_CONFIG', settings)
    # Local file media routed into Web Audio can be CORS-silenced in Chromium.
    # Keep the WAV for host export; embed the exact same bytes for file:// preview.
    audio_src = '' if voice_file is None else ' src="data:audio/wav;base64,'+base64.b64encode((root/voice_file).read_bytes()).decode('ascii')+'"'
    style='html,body{margin:0;background:#070d12;overflow:hidden;width:100%;height:100%}body{display:grid;place-items:center}#stage{position:relative;container-type:size;width:min(100vw,calc(100vh * WIDTH / HEIGHT));height:min(100vh,calc(100vw * HEIGHT / WIDTH))}canvas{display:block;width:100%;height:100%}#chapText{position:absolute;top:3.2cqh;left:4cqw;z-index:1;font:600 2.2cqw "Microsoft YaHei";color:rgba(147,167,160,.75);background:rgba(10,20,32,.55);border:1px solid rgba(148,163,184,.2);border-radius:999px;padding:.5cqw 2.4cqw;pointer-events:none;user-select:none}button,audio,output{position:fixed;bottom:8px;z-index:2}button{left:8px;min-height:44px;padding:8px 16px;font-size:16px}audio{left:180px}output{color:#ffb4b4;bottom:60px;left:8px}'
    style=style.replace('WIDTH',str(width)).replace('HEIGHT',str(height))
    style=style.replace('body{display:grid;place-items:center}','body{display:grid;place-items:center;box-sizing:border-box;padding-bottom:76px}')
    style=style.replace('100vh * '+str(width),'(100vh - 76px) * '+str(width)).replace('height:min(100vh,','height:min(calc(100vh - 76px),')
    style=style.replace('padding-bottom:76px','padding-bottom:calc(76px + env(safe-area-inset-bottom))').replace('100vh - 76px','100vh - 76px - env(safe-area-inset-bottom)')
    style+='audio{display:none}#controls{box-sizing:border-box;position:fixed;z-index:3;bottom:max(8px,env(safe-area-inset-bottom));left:50%;transform:translateX(-50%);width:min(calc(100vw - 16px),640px);display:flex;align-items:center;gap:8px;padding:8px;background:rgba(10,25,28,.96);border:1px solid #31534b;border-radius:12px;color:#e8f1ec}#controls button{position:static;min-height:44px;min-width:72px;flex:none;padding:6px 12px;font:600 14px "Microsoft YaHei";border:0;border-radius:7px;background:#65efb5;color:#071d1b}#seek{flex:1;min-width:48px;width:0;height:44px;margin:0;accent-color:#65efb5;cursor:pointer}#time{flex:none;white-space:nowrap;font:12px monospace;font-variant-numeric:tabular-nums}output{bottom:84px;max-width:calc(100vw - 16px)}'
    from scripts.contracts import load_profile
    hud=load_profile()['devHud']
    style=style.replace('top:3.2cqh',f"top:{hud['topRatio']*100:g}cqh").replace('left:4cqw',f"left:{hud['leftRatio']*100:g}cqw").replace('600 2.2cqw',f"600 {hud['fontRatio']*100:g}cqw")
    html = '<!doctype html><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; script-src &#39;unsafe-inline&#39;; style-src &#39;unsafe-inline&#39;; media-src data:; img-src file: data:; connect-src data:; font-src file: data:; base-uri &#39;none&#39;"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+style+'</style><div id="stage"><canvas></canvas><span id="chapText" aria-label="制作校对分镜指示" data-preview-only="true"></span></div><div id="controls" role="group" aria-label="播放控制" data-preview-only="true"><button disabled aria-label="播放或暂停" aria-pressed="false">播放</button><input id="seek" type="range" min="0" value="0" step="0.01" disabled aria-label="播放进度"><span id="time">00:00 / 00:00</span></div><audio'+audio_src+'></audio><output role="status"></output><script>'+js+'\n'+player+'</script>'
    return html


def canonical_html(root, manifest):
    from scripts.text_contract import strict_loads
    return render_html(root, strict_loads((root/manifest["sceneFile"]).read_text(encoding="utf-8-sig")),
        manifest["width"],manifest["height"],manifest["durationUs"],manifest.get("voiceFile"),
        strict_loads((root/manifest["sfxFile"]).read_text(encoding="utf-8-sig")),root/"vibe-runtime",manifest['title'])
