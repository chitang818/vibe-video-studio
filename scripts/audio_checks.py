"""PCM asset diagnostics over the complete files; does not rewrite or normalize audio."""
import array
import math
import wave
from scripts.build_fast_project import asset_path


def wave_metrics(path):
    with wave.open(str(path)) as wav:
        rate,channels,width=wav.getframerate(),wav.getnchannels(),wav.getsampwidth()
        if width not in (1,2,3,4) or wav.getcomptype()!='NONE':
            raise ValueError('Unsupported PCM audio format')
        frames=wav.getnframes();denom=2**(width*8-1);windows=[];total_square=0;total_count=0
        while data:=wav.readframes(rate):
            if width==1:values=[(v-128)/128 for v in data]
            elif width in (2,4):
                raw=array.array('h' if width==2 else 'i');raw.frombytes(data);values=[v/denom for v in raw]
            else:values=[int.from_bytes(data[i:i+3],'little',signed=True)/denom for i in range(0,len(data),3)]
            square=sum(v*v for v in values);peak=max(map(abs,values),default=0)
            windows.append(dict(rms=math.sqrt(square/max(1,len(values))),peak=peak))
            total_square+=square;total_count+=len(values)
    return dict(durationUs=round(frames/rate*1e6),rms=math.sqrt(total_square/max(1,total_count)),
        peak=max((w['peak'] for w in windows),default=0),windows=windows,rate=rate,channels=channels)


def inspect_audio(root,manifest,track):
    metrics={};issues=[];warnings=[]
    names={e['source'] for e in track['events']}
    if manifest.get('voiceFile'):names.add(manifest['voiceFile'])
    for name in names:
        metrics[name]=wave_metrics(asset_path(root,name))
        if metrics[name]['rms']<=.00001:
            issues.append(dict(rule='AUDIO',detail='Silent audio asset: '+name))
    for event in track['events']:
        sound=metrics[event['source']]
        if event['timeUs']+sound['durationUs']>manifest['durationUs']:
            warnings.append('Sound reaches beyond the final physical WAV boundary: '+event['source'])
        voice=metrics.get(manifest.get('voiceFile'))
        if voice:
            second=min(len(voice['windows'])-1,event['timeUs']//1000000)
            nearby=voice['windows'][second]
            rms=sound['rms']*.08*event.get('gain',1)
            delta=20*math.log10(max(rms,1e-12)/max(nearby['rms'],1e-12))
            if delta>-12:warnings.append(f'SFX may compete with voice ({delta:.1f}dB): '+event['source'])
            if nearby['peak']+sound['peak']*.08*event.get('gain',1)>1:
                warnings.append('Potential mix clipping requires actual listening: '+event['source'])
    return dict(audioAssets=metrics,audioWarnings=sorted(set(warnings))),issues
