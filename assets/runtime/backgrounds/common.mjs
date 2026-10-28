export function seeded(seed,i,salt=0){
    let v=(seed+Math.imul(i+1,0x9e3779b1)+Math.imul(salt+1,0x85ebca6b))>>>0;
    v=Math.imul(v^(v>>>16),0x7feb352d);v=Math.imul(v^(v>>>15),0x846ca68b);
    return ((v^(v>>>16))>>>0)/4294967296;
}

export function backgroundFrame(ctx,bg,timeUs,w,h){
    const t=timeUs/1e6,seed=bg.seed??8,k=w/1080,mod=(n,m)=>(n%m+m)%m;
    const glow=(x,y,r,a,rgb='74,222,165')=>{
        const g=ctx.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,`rgba(${rgb},${a})`);g.addColorStop(.45,`rgba(${rgb},${a*.4})`);g.addColorStop(1,`rgba(${rgb},0)`);
        ctx.fillStyle=g;ctx.fillRect(x-r,y-r,r*2,r*2);
    };
    return {t,seed,k,w,h,mod,glow};
}
