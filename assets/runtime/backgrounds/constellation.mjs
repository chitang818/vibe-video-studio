import {seeded} from './common.mjs';
export function drawConstellation(ctx,frame,recipe){
    const {t,seed,w,h,k,mod,glow}=frame;
        const points=Array.from({length:recipe.count},(_,i)=>({x:mod(seeded(seed,i,1)*w+t*(seeded(seed,i,3)-.5)*recipe.speedX*k,w),y:mod(seeded(seed,i,2)*h+t*(seeded(seed,i,4)-.5)*recipe.speedY*k,h)}));
        let pair=0;
        for(let i=0;i<points.length;i++)for(let j=i+1;j<points.length;j++){
            const a=points[i],b=points[j],d=Math.hypot(a.x-b.x,a.y-b.y);
            if(d>recipe.distance*k)continue;ctx.strokeStyle=`rgba(91,216,209,${(1-d/(recipe.distance*k))*recipe.lineAlpha})`;ctx.lineWidth=1.2*k;
            ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
            if(pair++%recipe.pulseEvery===0){const p=mod(t*recipe.pulseRate+seeded(seed,i+j,9),1);glow(a.x+(b.x-a.x)*p,a.y+(b.y-a.y)*p,recipe.pulseRadius*k,recipe.nodeAlpha,'143,230,245');}
        }
        for(const p of points)glow(p.x,p.y,recipe.nodeRadius*k,recipe.nodeAlpha,'94,219,214');
}
