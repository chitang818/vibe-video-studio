// VIBE scene protocol 1 / runtime 1.2.0. Shared by preview and offline export.
export const VERSION = '1.2.0';
const types = new Set(['text', 'rect', 'image', 'ring', 'bar', 'path']);
const finite = v => typeof v === 'number' && Number.isFinite(v);
const integer = v => Number.isSafeInteger(v);
const fail = message => { throw new Error(message); };
export function frameTiming(index, fps, durationUs) {
    if (!integer(index) || index < 0 || ![20,30,60].includes(fps) || !integer(durationUs) || durationUs <= 0) fail('Invalid frame timing');
    const timeUs = Math.floor(index * 1e6 / fps);
    const end = Math.min(durationUs, Math.floor((index + 1) * 1e6 / fps));
    if (end <= timeUs) fail('Frame outside duration');
    return { timeUs, durationUs: end - timeUs };
}
export function particleAt(i, timeUs, width, height, seed) {
    function rand(salt) {
        let v = (seed ^ Math.imul(i + 1, 0x45d9f3b) ^ salt) >>> 0;
        v = Math.imul(v ^ (v >>> 16), 0x45d9f3b) >>> 0;
        return ((v ^ (v >>> 16)) >>> 0) / 4294967296;
    }
    const t = timeUs / 1e6, radius = 3 + rand(1) * 24, span = height + 2 * radius;
    return { x: rand(2) * width + Math.sin(t * .4 + rand(3) * 6.28) * 12,
        y: ((rand(4) * span - t * (8 + rand(5) * 20)) % span + span) % span - radius,
        radius, alpha: .08 + rand(6) * .16 };
}
/*__VIBE_BACKGROUND_BUNDLE__*/

// A cut never composites two readable pages. Outgoing content exits before its cut.
export function pageTransitionAt(scene,timeUs){
    let index=0;while(index+1<scene.scenes.length&&scene.scenes[index+1].startUs<=timeUs)index++;
    const s=scene.scenes[index],local=timeUs-s.startUs,next=scene.scenes[index+1];
    const smooth=p=>p*p*(3-2*p);let opacity=1,shift=0;
    if(index>0&&s.transition&&local<240000){const p=smooth(local/240000);opacity=p;shift=s.transition==='push'?16*(1-p):0;}
    else if(next?.transition&&local>s.endUs-s.startUs-160000){const p=smooth((local-(s.endUs-s.startUs-160000))/160000);opacity=1-p;shift=next.transition==='push'?-16*p:0;}
    return {sceneId:s.id,opacity,shift};
}

export function validateScene(scene, config) {
    const { width, height, durationUs } = config;
    if (![width,height,durationUs].every(integer) || width < 64 || height < 64 || width > 3840 || height > 3840 || width % 2 || height % 2 || durationUs <= 0 || durationUs > 7200e6) fail('Invalid project size or duration');
    if (!Array.isArray(scene.scenes) || !scene.scenes.length || scene.scenes.length > 1000) fail('Invalid scene list');
    if(scene.background?.preset!==undefined){
        const preset=getBackgroundPreset(scene.background.preset);
        if(scene.background.templateVersion!==undefined&&scene.background.templateVersion!==preset.version)fail('Background template version mismatch');
        if(scene.background.recipeSha256!==undefined&&scene.background.recipeSha256!==preset.recipeSha256)fail('Background recipe identity mismatch');
    }
    let end = 0;
    let cachedPixels = 0;
    if (scene.subtitleSize !== undefined && (!finite(scene.subtitleSize) || scene.subtitleSize < 8 || scene.subtitleSize > width)) fail('Invalid subtitle size');
    const ids = new Set();
    for (const s of scene.scenes) {
        if (!s.id || ids.has(s.id) || s.startUs !== end || !integer(s.endUs) || s.endUs <= s.startUs || s.endUs > durationUs) fail('Scene timeline must cover the project without gaps or overlaps');
        ids.add(s.id); end = s.endUs;
        if (!Array.isArray(s.nodes) || !s.nodes.length || s.nodes.length > 500) fail('Invalid nodes');
        if(s.transition!==undefined&&!['fade','push'].includes(s.transition))fail('Unknown transition');
        const nodeIds = new Set();
        for (const n of s.nodes) {
            if (!types.has(n.type) || !n.id || nodeIds.has(n.id) || ![n.x,n.y,n.width,n.height].every(finite) || n.width <= 0 || n.height <= 0) fail('Invalid node geometry/type/identity');
            nodeIds.add(n.id);
            if(n.width>width || n.height>height)fail('Node exceeds project dimensions');
            if(n.type==='text')cachedPixels+=Math.ceil(n.width)*Math.ceil(n.height);
            if(cachedPixels>64000000)fail('Text cache exceeds 256 MB budget; simplify the project');
            if (n.size !== undefined && (!finite(n.size) || n.size < 8 || n.size > width)) fail('Invalid font size');
            for (const key of ['enterUs','enterDurationUs','valueDurationUs']) if (n[key] !== undefined && (!integer(n[key]) || n[key] < 0)) fail('Invalid animation time');
            for (const key of ['value','toValue']) if (n[key] !== undefined && (!finite(n[key]) || n[key] < 0 || n[key] > 1)) fail('Chart values must be in 0..1');
            if(n.enterDelayUs!==undefined&&(!integer(n.enterDelayUs)||n.enterDelayUs<0||n.enterDelayUs>120000))fail('Invalid group stagger');
            if(n.entrance!==undefined&&!['fade-up','slide-left','slide-right','zoom'].includes(n.entrance))fail('Unknown entrance');
            if(n.emphasis && (n.type!=='text'||!['color','marker','underline'].includes(n.emphasis.kind)||!integer(n.emphasis.timeUs)||n.emphasis.timeUs<(n.enterUs??0)||n.emphasis.timeUs>=s.endUs-s.startUs))fail('Invalid emphasis');
            if(n.fit!==undefined&&(n.type!=='image'||!['contain','cover'].includes(n.fit)))fail('Invalid image fit');
            for(const k of ['focusX','focusY'])if(n[k]!==undefined&&(!finite(n[k])||n[k]<0||n[k]>1))fail('Invalid image focus');
            if(n.imageZoom!==undefined&&(n.type!=='image'||typeof n.imageZoom!=='boolean'))fail('Invalid image zoom');
            if(n.verticalAlign!==undefined&&(n.type!=='text'||!['top','center'].includes(n.verticalAlign)))fail('Invalid vertical text alignment');
            if (n.type === 'text' && (typeof n.text !== 'string' || n.text.length > 2000)) fail('Invalid text');
            if (n.type === 'image' && typeof n.source !== 'string') fail('Missing image asset');
            if (n.type === 'path' && (typeof n.path !== 'string' || n.path.length > 20000)) fail('Invalid vector path');
        }
    }
    if (end !== durationUs) fail('Scene duration does not match manifest');
    let captionEnd = 0;
    for (const u of scene.subtitles || []) {
        if (!integer(u.startUs) || !integer(u.endUs) || u.startUs < captionEnd || u.endUs <= u.startUs || u.endUs > durationUs || !Array.isArray(u.chars) || !u.chars.length || u.chars.length > 32) fail('Invalid caption unit');
        let previous = u.startUs;
        for (const c of u.chars) {
            if (typeof c.text !== 'string' || !c.text.length || !integer(c.startUs) || c.startUs < previous || c.startUs >= u.endUs) fail('Invalid character timing');
            previous = c.startUs;
        }
        captionEnd = u.endUs;
    }
}
// Cache geometry follows actual ink metrics, not the font's nominal "top" baseline.
export function prepareTextLayer(node, projectWidth) {
    const canvas=document.createElement('canvas');
    canvas.width=Math.ceil(node.width);canvas.height=Math.ceil(node.height);
    const c=canvas.getContext('2d'),size=node.size??projectWidth*.035,pad=2;
    c.font=`${node.bold===false?400:700} ${size}px "Microsoft YaHei"`;
    c.textBaseline='alphabetic';c.fillStyle=node._color??node.color??'#e8f1ec';
    let line='';const lines=[];
    const graphemes=new Intl.Segmenter('zh',{granularity:'grapheme'}).segment(node.text.replace(/\r\n?/g,'\n'));
    for(const {segment:ch} of graphemes){
        if(ch==='\n'){lines.push(line);line='';continue;}
        if(line&&c.measureText(line+ch).width+pad*2>node.width){lines.push(line);line='';}line+=ch;
    }
    lines.push(line);
    const metrics=lines.map(t=>c.measureText(t));
    const ascent=Math.max(0,...metrics.map(m=>m.actualBoundingBoxAscent));
    const descent=Math.max(0,...metrics.map(m=>m.actualBoundingBoxDescent));
    const lineHeight=Math.max(size*1.35,Math.ceil(ascent+descent)+pad*2);
    const inkHeight=(lines.length-1)*lineHeight+Math.ceil(ascent)+Math.ceil(descent);
    const firstBaseline=Math.ceil(ascent)+(node.verticalAlign==='center'?Math.max(pad,(node.height-inkHeight)/2):pad);
    if((lines.length-1)*lineHeight+firstBaseline+Math.ceil(descent)+pad>node.height)
        fail(`Text ink overflows node ${node.id}`);
    const origins=metrics.map((m,i)=>{
        const inkWidth=m.actualBoundingBoxLeft+m.actualBoundingBoxRight;
        if(Math.max(m.width,inkWidth)+pad*2>node.width)fail(`Text ink overflows node ${node.id}`);
        return {x:node.align==='center'?(node.width-inkWidth)/2+m.actualBoundingBoxLeft:pad+m.actualBoundingBoxLeft,
            y:firstBaseline+i*lineHeight};
    });
    origins.forEach((o,i)=>c.fillText(lines[i],o.x,o.y));
    const inkRects=metrics.map((m,i)=>({x:origins[i].x-m.actualBoundingBoxLeft,y:origins[i].y-m.actualBoundingBoxAscent,width:m.actualBoundingBoxLeft+m.actualBoundingBoxRight,height:m.actualBoundingBoxAscent+m.actualBoundingBoxDescent}));
    return {canvas,lines,origins,inkRects,font:c.font,textBaseline:c.textBaseline,lineHeight};
}
export async function prepareScene(canvas, scene, config) {
    validateScene(scene, config);
    canvas.width = config.width; canvas.height = config.height;
    await document.fonts.load('700 48px "Microsoft YaHei"');
    await document.fonts.ready;
    const ctx = canvas.getContext('2d', { alpha: false });
    const cache = new Map(), bounds = new Map(), textGeometry=new Map();
    let imagePixels=0;
    const color = (value, fallback) => {
        const c = value ?? fallback;
        if (!CSS.supports('color', c)) fail('Invalid color');
        return c;
    };
    const base = config.assetBase;
    for (const s of scene.scenes) for (const n of s.nodes) {
        const key = s.id + '/' + n.id;
        n._color = color(n.color, '#e8f1ec');
        n._background = color(n.background, '#15323a');
        if (n.type === 'image') {
            const image = new Image(); image.src = config.inlineImages?.[n.source]??new URL(n.source, base).href;
            await image.decode(); imagePixels+=image.naturalWidth*image.naturalHeight;
            if(imagePixels>32000000)fail('Decoded images exceed 128 MB budget; resize source images');
            cache.set(key, image);
        } else if (n.type === 'path') {
            cache.set(key, new Path2D(n.path));
        } else if (n.type === 'text') {
            const prepared=prepareTextLayer(n,config.width);cache.set(key,prepared.canvas);textGeometry.set(key,prepared.inkRects);
            if(n.emphasis?.kind==='color')cache.set(key+'/accent',prepareTextLayer({...n,_color:'#65efb5'},config.width).canvas);
        }
        bounds.set(key, { id: n.id, x: n.x, y: n.y, width: n.width, height: n.height });
    }
    // Prepare subtitles once, then only change the highlight at export time.
    const captions = (scene.subtitles || []).map(u => {
        const size = scene.subtitleSize ?? config.width * .04;
        ctx.font = `700 ${size}px "Microsoft YaHei"`;
        ctx.textBaseline='alphabetic';
        const advances = u.chars.map(c => ctx.measureText(c.text).width);
        const ascent=Math.max(...u.chars.map(c=>ctx.measureText(c.text).actualBoundingBoxAscent));
        const width = advances.reduce((a,b) => a+b, 0);
        if (width > config.width * .84) fail('Subtitle exceeds safe width; split the unit');
        return { ...u, size, advances, width, baseline:Math.ceil(ascent)+2 };
    });
    function findScene(timeUs) {
        let low = 0, high = scene.scenes.length - 1;
        while (low < high) { const mid = Math.ceil((low+high)/2); if (scene.scenes[mid].startUs <= timeUs) low=mid; else high=mid-1; }
        return scene.scenes[low];
    }
    function transform(n,local) {
        const p=Math.min(1,Math.max(0,(local-(n.enterUs??0)-(n.enterDelayUs??0))/(n.enterDurationUs||450000)));
        const e=1-Math.pow(1-p,3), kind=n.entrance??'fade-up';
        return {alpha:p,dx:kind==='slide-left'?(1-e)*28:kind==='slide-right'?-(1-e)*28:0,
            dy:kind==='fade-up'?(1-e)*24:0,scale:(kind==='zoom'?.96+.04*e:1)*(n.pulse?1+.025*Math.sin(local/1e6*3):1)};
    }
    function layoutAt(timeUs) {
        const s=findScene(timeUs),local=timeUs-s.startUs,transition=pageTransitionAt(scene,timeUs);
        return s.nodes.filter(n=>local>=(n.enterUs??0)+(n.enterDelayUs??0)).map(n=>{
            const b=bounds.get(s.id+'/'+n.id),v=transform(n,local);
            return {...b,x:b.x-b.width*(v.scale-1)/2+v.dx+transition.shift,y:b.y-b.height*(v.scale-1)/2+v.dy,
                width:b.width*v.scale,height:b.height*v.scale};
        });
    }
    if (config.safeArea) for (const s of scene.scenes) {
        const times = [s.startUs,s.endUs-1,...s.nodes.flatMap(n=>[1,225000,450000].map(d=>Math.min(s.endUs-1,s.startUs+(n.enterUs??0)+(n.enterDelayUs??0)+d)))];
        for (const t of times) for (const b of layoutAt(t))
            if (b.x < config.width*.08 || b.x+b.width > config.width*.92 || b.y < config.height*.10 || b.y+b.height > config.height*.78)
                fail(`Node outside safe content area: ${b.id}`);
    }
    function renderAt(timeUs) {
        if (!integer(timeUs) || timeUs < 0 || timeUs >= config.durationUs) fail('Time outside project');
        const { width:w, height:h } = config;
        ctx.globalAlpha = 1; ctx.fillStyle = color(scene.background?.color, '#070d12'); ctx.fillRect(0,0,w,h);
        drawBackground(ctx,scene.background,timeUs,w,h);
        if (!scene.background?.preset && scene.background?.particles !== false) for (let i=0;i<60;i++) {
            const p = particleAt(i,timeUs,w,h,scene.background?.seed??1);
            const g = ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.radius);
            g.addColorStop(0,`rgba(74,222,180,${p.alpha})`);g.addColorStop(1,'rgba(74,222,180,0)');
            ctx.fillStyle=g;ctx.fillRect(p.x-p.radius,p.y-p.radius,p.radius*2,p.radius*2);
        }
        function drawPage(s,local,opacity=1,shift=0){
        ctx.save();ctx.beginPath();ctx.rect(w*.08,h*.10,w*.84,h*.68);ctx.clip();ctx.translate(shift,0);
        for (const n of s.nodes) {
            const tr=transform(n,local),progress=tr.alpha;
            if (!progress) continue;
            ctx.save();ctx.globalAlpha=progress*opacity;
            const scale=tr.scale;
            ctx.translate(n.x+n.width/2+tr.dx,n.y+n.height/2+tr.dy);ctx.scale(scale,scale);ctx.translate(-n.width/2,-n.height/2);
            const cached=cache.get(s.id+'/'+n.id);
            const value=n.value??.5, target=n.toValue??value;
            const v=value+(target-value)*Math.min(1,local/(n.valueDurationUs||s.endUs-s.startUs));
            if (n.type==='text') {
                const emphasis=n.emphasis?Math.min(1,Math.max(0,(local-n.emphasis.timeUs)/350000)):0;
                if(n.emphasis?.kind==='marker'&&emphasis){ctx.fillStyle='#28554b';for(const r of textGeometry.get(s.id+'/'+n.id))ctx.fillRect(Math.max(0,r.x-2),Math.max(0,r.y-2),Math.min(n.width,r.width+4)*emphasis,Math.min(n.height,r.height+4));}
                ctx.drawImage(cached,0,0);
                if(n.emphasis?.kind==='color'&&emphasis){ctx.globalAlpha=progress*opacity*emphasis;ctx.drawImage(cache.get(s.id+'/'+n.id+'/accent'),0,0);}
                if(n.emphasis?.kind==='underline'&&emphasis){ctx.fillStyle='#ebc86d';for(const r of textGeometry.get(s.id+'/'+n.id))ctx.fillRect(r.x,Math.min(n.height-4,r.y+r.height+2),r.width*emphasis,4);}
            }
            if (n.type==='image') {
                ctx.save();ctx.beginPath();ctx.roundRect(0,0,n.width,n.height,Math.min(n.radius??0,n.width/2,n.height/2));ctx.clip();
                const fit=n.fit??'contain',factor=fit==='cover'?Math.max:Math.min;
                const zoom=n.imageZoom?1+.04*Math.min(1,Math.max(0,local/(s.endUs-s.startUs))):1;
                const ratio=factor(n.width/cached.width,n.height/cached.height)*zoom;
                const dw=cached.width*ratio,dh=cached.height*ratio;
                ctx.drawImage(cached,(n.width-dw)*(n.focusX??.5),(n.height-dh)*(n.focusY??.5),dw,dh);ctx.restore();
            }
            if (n.type==='rect') {
                ctx.fillStyle=n._background;ctx.strokeStyle=n._color;ctx.lineWidth=1;
                ctx.beginPath();ctx.roundRect(0,0,n.width,n.height,Math.min(n.radius??16,n.width/2,n.height/2));ctx.fill();ctx.stroke();
            }
            if (n.type==='ring') {
                const r=Math.min(n.width,n.height)*.42;
                ctx.lineWidth=Math.max(2,r*.12);ctx.strokeStyle=n._background;
                ctx.beginPath();ctx.arc(n.width/2,n.height/2,r,0,Math.PI*2);ctx.stroke();
                ctx.strokeStyle=n._color;ctx.beginPath();ctx.arc(n.width/2,n.height/2,r,-Math.PI/2,-Math.PI/2+v*Math.PI*2);ctx.stroke();
            }
            if (n.type==='bar') {ctx.fillStyle=n._background;ctx.fillRect(0,0,n.width,n.height);ctx.fillStyle=n._color;ctx.fillRect(0,0,n.width*v,n.height);}
            if (n.type==='path') {ctx.fillStyle=n._color;ctx.fill(cached);}
            ctx.restore();
        }
        ctx.restore();}
        const s=findScene(timeUs),transition=pageTransitionAt(scene,timeUs);
        drawPage(s,timeUs-s.startUs,transition.opacity,transition.shift);
        const u=captions.find(u => timeUs>=u.startUs && timeUs<u.endUs);
        if (u) {
            ctx.font=`700 ${u.size}px "Microsoft YaHei"`;ctx.textBaseline='alphabetic';
            let x=(w-u.width)/2;
            u.chars.forEach((c,i)=>{ctx.fillStyle=timeUs>=c.startUs?'#4ade80':'#e8f1ec';ctx.fillText(c.text,x,h*.82+u.baseline);x+=u.advances[i];});
        }
    }
    renderAt(0);
    function textRaster(sceneId,nodeId) {
        const layer=cache.get(sceneId+'/'+nodeId);
        if(!layer || typeof layer.getContext!=='function')fail('Unknown text raster');
        return layer.getContext('2d').getImageData(0,0,layer.width,layer.height);
    }
    return { renderAt, layoutAt, textRaster };
}
