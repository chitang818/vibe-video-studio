"""Generate clearly synthetic demo inputs; this is not a real voiceover or product signoff."""
import argparse
import json
import math
import struct
import wave
from pathlib import Path


def make(out):
    out=Path(out)
    if out.exists():raise ValueError('Demo output must be a new directory')
    out.mkdir(parents=True)
    groups=[['植物根系吸收养分','细小菌丝向外延伸','探索根系难达的空隙','帮助植物获取养分'],
        ['宿主提供碳水化合物','真菌帮助吸收养分','双方建立共生关系','共同适应周围环境'],
        ['真菌进入植物根系','在根皮层细胞内部','形成特殊丛枝结构','根外菌丝继续延伸']]
    kinds=['process','exchange','cross-section'];headings=['根系与菌丝网络','植物与真菌交换','观察根内丛枝结构']
    rows=[];shots=[];captions=[];text=''
    for i,parts in enumerate(groups):
        segment='，'.join(parts)+'。';offset=len(text);text+=segment;captions.extend(parts)
        quote=parts[0]
        stages=[]
        for label,phrase in [(parts[0],parts[0][4:]),(parts[1],parts[1]),(parts[2],parts[2])]:
            # Every event refers to an actual quote in these deliberately synthetic timestamps.
            position=offset+segment.index(phrase)
            occurrence=sum(text.startswith(phrase,k) for k in range(position+1))
            stages.append(dict(text=label,anchor=dict(quote=phrase,occurrence=occurrence)))
        occurrence=sum(text.startswith(quote,k) for k in range(offset+1))
        shots.append(dict(id=f'demo-{i+1}',kind=kinds[i],heading=headings[i],anchor=dict(quote=quote,occurrence=occurrence),stages=stages))
    for i,c in enumerate(text):rows.append(dict(Char=c,StartSeconds=i*.2,EndSeconds=(i+1)*.2))
    for name,value in [('timestamps.json',rows),('captions.json',captions),('story.json',dict(version=1,title='菌根共生机制演示',authorId='synthetic-demo',scenes=shots))]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'script.txt').write_text(text,encoding='utf-8')
    with wave.open(str(out/'voice.wav'),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(16000)
        wav.writeframes(b''.join(struct.pack('<h',round(2500*math.sin(i/16000*math.tau*220))) for i in range(round(len(text)*.2*16000))))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    print(make(p.parse_args().out))
