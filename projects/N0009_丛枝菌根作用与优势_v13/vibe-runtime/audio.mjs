// Preview clock is outside the deterministic renderer. Export audio is mixed by the host.
export async function createPreviewPlayer(audio, renderer, config, track) {
    const events=track?.events??[], buffers=new Map(), active=new Map(), played=new Set();
    const decoder=new OfflineAudioContext(1,1,48000);
    for(const source of new Set(events.map(e=>e.source))){
        const response=await fetch(config.inlineSounds?.[source]??new URL(source,config.assetBase));
        if(!response.ok)throw Error('Preview sound asset missing');
        buffers.set(source,await decoder.decodeAudioData(await response.arrayBuffer()));
    }
    let context,master,voiceGain,running=false,anchor=0,timeUs=0,raf=0;
    function ensureAudio(){
        if(context)return;
        context=new AudioContext();master=context.createGain();master.connect(context.destination);
        if(config.voiceUrl){voiceGain=context.createGain();voiceGain.gain.value=config.voiceGain??1;context.createMediaElementSource(audio).connect(voiceGain).connect(master);}
    }
    function stopSounds(){for(const node of active.values()){try{node.stop();}catch{/* already ended */}}active.clear();played.clear();}
    function paint(){
        if(!running)return;
        timeUs=config.voiceUrl?Math.round(audio.currentTime*1e6):Math.round((performance.now()-anchor)*1000);
        if(timeUs>=config.durationUs){pause();return;}
        renderer.renderAt(timeUs);
        if(master)master.gain.value=config.fadeOut?Math.min(1,(config.durationUs-timeUs)/500000):1;
        if(config.sfxEnabled!==false)events.forEach((e,i)=>{
            const buffer=buffers.get(e.source), offset=(timeUs-e.timeUs)/1e6;
            if(played.has(i)||offset<0||offset>=buffer.duration)return;
            ensureAudio();const source=context.createBufferSource(),gain=context.createGain();
            source.buffer=buffer;gain.gain.value=(config.sfxGain??.7)*(e.gain??1);
            source.connect(gain).connect(master);source.start(0,offset);played.add(i);active.set(i,source);
            source.onended=()=>active.delete(i);
        });
        raf=requestAnimationFrame(paint);
    }
    function pause(){running=false;cancelAnimationFrame(raf);audio.pause();stopSounds();}
    async function toggle(){
        if(running){pause();return;}
        ensureAudio();await context.resume();
        if(timeUs>=config.durationUs)timeUs=0;
        if(config.voiceUrl){audio.currentTime=timeUs/1e6;await audio.play();}
        anchor=performance.now()-timeUs/1000;running=true;paint();
    }
    function seek(seconds){
        timeUs=Math.min(config.durationUs-1,Math.max(0,Math.round(seconds*1e6)));
        stopSounds();anchor=performance.now()-timeUs/1000;
        if(config.voiceUrl)audio.currentTime=timeUs/1e6;
        renderer.renderAt(timeUs);
    }
    function cancel(){pause();if(context)void context.close();}
    return {toggle,seek,cancel,pause};
}
