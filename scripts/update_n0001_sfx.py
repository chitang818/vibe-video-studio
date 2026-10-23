# -*- coding: utf-8 -*-
import os

with open('scripts/prepare_n0001_html.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos1 = text.find('new_scene_fn =')
pos2 = text.find('assert old_scene_fn in demo', pos1)

replacement = '''new_scene_fn = """var SFX_CUES = [
  { t: 0.05, sfx: 'whoosh' },
  { t: 2.20, sfx: 'whoosh' },
  { t: 8.04, sfx: 'pop' },
  { t: 14.82, sfx: 'pop' },
  { t: 17.86, sfx: 'ding' },
  { t: 26.66, sfx: 'whoosh' },
  { t: 34.20, sfx: 'pop' },
  { t: 45.00, sfx: 'pop' },
  { t: 50.50, sfx: 'pop' },
  { t: 58.39, sfx: 'whoosh' },
  { t: 65.20, sfx: 'pop' },
  { t: 71.80, sfx: 'ding' },
  { t: 77.93, sfx: 'whoosh' },
  { t: 86.50, sfx: 'pop' },
  { t: 98.20, sfx: 'pop' },
  { t: 106.51, sfx: 'whoosh' },
  { t: 118.40, sfx: 'ding' },
  { t: 135.20, sfx: 'pop' },
  { t: 153.41, sfx: 'whoosh' },
  { t: 170.50, sfx: 'ding' },
  { t: 195.20, sfx: 'pop' },
  { t: 216.71, sfx: 'whoosh' },
  { t: 224.20, sfx: 'pop' },
  { t: 235.55, sfx: 'whoosh' },
  { t: 248.30, sfx: 'pop' },
  { t: 262.50, sfx: 'pop' },
  { t: 275.29, sfx: 'whoosh' },
  { t: 282.00, sfx: 'chime' }
];

var lastCueTime = -0.5;
function checkSfxCues(t) {
  if (!window.VibeSound || window.__RECORDING__) return;
  if (t < lastCueTime) { lastCueTime = t - 0.2; }
  for (var i = 0; i < SFX_CUES.length; i++) {
    var cue = SFX_CUES[i];
    if (t >= cue.t && lastCueTime < cue.t && (t - cue.t) < 0.35) {
      VibeSound.play(cue.sfx);
    }
  }
  lastCueTime = t;
}

function setScene(idx){
  if(idx===curScene || idx<0 || idx>=SCENES.length) return;
  var prev=curScene;
  if(prev>=0 && prev<SCENES.length){
    var prevEl = document.getElementById(SCENES[prev][0]);
    if(prevEl) prevEl.classList.remove('active');
  }
  curScene=idx;
  var el=document.getElementById(SCENES[idx][0]);
  if(el) el.classList.add('active');
  var ct=document.getElementById('chapText');
  if(ct) ct.innerHTML='第 '+(idx+1)+' / '+SCENES.length+' 节';
  if(idx>0 && prev!==idx && flashEl){
    flashEl.classList.remove('go'); void flashEl.offsetWidth; flashEl.classList.add('go');
  }
}
var S1 = document.getElementById('s-open');
function setPhase(p){ if(S1 && S1.getAttribute('data-phase')!==p) S1.setAttribute('data-phase',p); }

function syncTime(t){
  var sc = sceneAt(t);
  if(sc !== curScene){
    setScene(sc);
    triggerSceneGfx(sc);
  }
  if(sc === 0){
    setPhase(t<2.20?'splash':(t<8.04?'topic':(t<14.82?'hook':(t<17.86?'promise':(t<24.74?'cta':'preview')))));
  }
  var idx = findCharIndex(t);
  if(idx !== curIdx){
    curIdx = idx;
    renderSubtitle(idx);
  }
  checkSfxCues(t);
  var dur = (audio && audio.duration && !isNaN(audio.duration)) ? audio.duration : 314.56;
  if(progFill) progFill.style.width = Math.min(100, (t / dur * 100)).toFixed(2) + '%';
}
window.syncTime = syncTime;
window.SCENES = SCENES;
window.CHAP_NAMES = CHAP_NAMES;

function startPlay(){
  if(state==='playing') return;
  if(window.VibeSound) {
    VibeSound.init();
    VibeSound.play('whoosh');
  }
  overlay.classList.add('hide');
  curScene=-1; curIdx=-1;
  lastCueTime = -0.5;
  syncTime(0);
  audio.currentTime=0;
  audio.play().then(function(){
    state='playing';
    flashEl.classList.remove('go'); void flashEl.offsetWidth; flashEl.classList.add('go');
    if(!rafId) loop();
  }).catch(function(e){
    console.warn("Audio play:", e);
  });
}
function endPlay(){
  state='ended';
  if(progFill) progFill.style.width='100%';
  btnReplay.classList.add('show');
}
function loop(){
  if(state!=='playing'){ rafId=0; return; }
  var t=audio.currentTime;
  var dur = (audio && audio.duration && !isNaN(audio.duration)) ? audio.duration : 314.56;
  if(audio.ended || t>=dur-0.05){ endPlay(); rafId=0; return; }
  syncTime(t);
  rafId=requestAnimationFrame(loop);
}"""\n\n'''

new_text = text[:pos1] + replacement + text[pos2:]
with open('scripts/prepare_n0001_html.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Updated scripts/prepare_n0001_html.py successfully!')
