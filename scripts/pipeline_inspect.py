"""Read-only local production board; all user/source text is HTML escaped."""
import html
from pathlib import Path
from urllib.parse import quote

def render(root,state,statuses):
    from scripts.pipeline import output,read,asset_path,stage_status
    esc=lambda v:html.escape(str(v),quote=True)
    def link(path,label):return '<a href="'+quote(str(path).replace('\\','/'),safe='/')+'">'+esc(label)+'</a>'
    sections=['<h1>网页视频制作过程</h1><p>逐步查看原文、分镜、视觉设计、素材、单镜头和整片。ready只表示阶段数据就绪；审美、听感和正式批准另行记录。</p>']
    sections.append('<nav>'+''.join(f'<a href="#{name}">{name}: {esc(status)}</a>' for name,status in statuses.items())+'</nav>')
    labels=dict(intake='0 · 原始资料与对齐',segment='1 · 语义分镜',direct='2 · 视觉导演',produce='3 · 素材与单镜头',assemble='4 · 全片组装',review='5 · 检查与待复核')
    for name,status in statuses.items():
        entry=state['stages'].get(name,{})
        sections.append(f'<section id="{name}"><h2>{labels[name]} <small>{esc(status)}</small></h2>')
        if entry.get('error'):sections.append('<p class="error">'+esc(entry['error'])+'</p>')
        if entry.get('result'):
            sections.append(link(entry['result'],'阶段原始产物 JSON'))
            data=output(root,entry)
            if name=='intake':
                sections.append('<p>时长 '+str(round(data['durationUs']/1e6,2))+'秒；'+str(len(data['rows']))+'条原始识别记录。</p>')
                sections.append(' · '.join(link('sources/'+n,n) for n in ('script.txt','voice.wav','timestamps.json','style.json')))
                sections.append('<p>'+link(entry['run']+'/alignment.json','原文与识别差异')+' · '+link(entry['run']+'/waveform.json','音频峰值包络')+'</p>')
            elif name=='segment':
                for shot in data['shots']:
                    sections.append(f'<article><h3>{esc(shot["id"])} · {shot["startUs"]/1e6:.2f}–{shot["endUs"]/1e6:.2f}s</h3><p>{esc(shot["goal"])}</p><blockquote>{esc(shot["originalText"])}</blockquote><p>切点依据：{esc(shot["reason"])}</p><details><summary>口播事件</summary><pre>{esc(shot["beats"])}</pre></details></article>')
            elif name=='direct':
                for brief in data['briefs']:
                    sections.append('<p>'+link(entry['run']+'/'+brief['shotId']+'.svg',brief['shotId']+' 静态结构草图')+'</p>')
                    sections.append('<article><h3>'+esc(brief['shotId'])+' · '+esc(brief['focus'])+'</h3>'+''.join('<p><b>'+esc(k)+'</b> '+esc(brief[k])+'</p>' for k in ('composition','rationale','opening','development','ending','continuity'))+'<p>约束：'+esc(brief['constraints'])+'</p><p>素材请求：'+esc(brief['assetRequests'])+'</p></article>')
            elif name=='produce':
                sections.append('<p>本次制作：'+esc(data['produced'])+'；复用：'+esc(data['reused'])+'；待制作：'+esc(data['remaining'])+'</p><div class="grid">')
                for sid,receipt in state['shots'].items():
                    folder=Path(receipt['result']).parent.as_posix();frames=sorted(asset_path(root,folder).glob('frame-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
                    sections.append('<article><h3>'+esc(sid)+'</h3>'+link(folder+'/index.html','播放独立镜头')+' · '+link(receipt['result'],'场景与来源'))
                    if frames:sections.append('<img loading="lazy" alt="'+esc(sid)+' 关键帧" src="'+quote(frames[-1].relative_to(root).as_posix(),safe='/')+'">')
                    sections.append('</article>')
                sections.append('</div>')
                if (root/'assets/media-registry.json').exists():sections.append(link('assets/media-registry.json','真实素材来源登记'))
            elif name=='assemble':sections.append('<p>'+link(data['project']+'/index.html','播放完整网页视频')+' · '+link(entry['run']+'/timeline.json','全片时间轴')+'</p>')
            elif name=='review':sections.append('<pre>'+esc(data)+'</pre>')
            if data.get('warnings'):sections.append('<p>编排提示：'+esc(data['warnings'])+'</p>')
        else:sections.append('<p>等待本阶段输入。由对应Skill编排后提交，程序不会用默认卡片替代。</p>')
        if entry.get('run'):sections.append('<details><summary>运行记录与历史位置</summary><p>'+esc(entry['run'])+'</p><p>输入指纹：'+esc(entry.get('inputFingerprint','尚未完成'))+'</p></details>')
        history=sorted((root/'runs').glob(name+'-*/result.json'))
        if history:sections.append('<details><summary>历史产物 / A-B对照入口</summary>'+''.join('<p>'+link(p.relative_to(root).as_posix(),p.parent.name)+'</p>' for p in history)+'</details>')
        sections.append('</section>')
    sections.append('<footer>旧运行保存在runs/；可比较不同版本，不覆盖历史镜头。修改上游后执行inspect查看stale状态。外部搜图/生图可用性不由本页面虚构。</footer>')
    css='body{margin:auto;max-width:1100px;padding:20px;background:#081c1c;color:#edf8f2;font:16px/1.6 "Microsoft YaHei",sans-serif}a{color:#65efb5;overflow-wrap:anywhere}nav{display:flex;flex-wrap:wrap;gap:14px}section{margin:24px 0;padding:20px;border:1px solid #2b5550;border-radius:12px}article{margin:16px 0;padding:16px;border-left:3px solid #ebc86d;background:#102a27}small{font-size:14px;color:#ebc86d}pre,blockquote{white-space:pre-wrap;overflow-wrap:anywhere;margin:12px 0}img{width:100%;max-height:480px;object-fit:contain}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:20px}.error{color:#ffb4b4}footer{color:#abc1b6}*{box-sizing:border-box}'
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src file: data:; media-src file: data:; base-uri \'none\'"><title>制作过程</title><style>'+css+'</style>'+''.join(sections)+'</html>'
    (root/'index.html').write_text(page,encoding='utf-8')
