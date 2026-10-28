import {seeded} from './common.mjs';
export function drawDnaSpiral(ctx,frame,recipe){
    const {t,seed,w,h,k,mod,glow}=frame;
        const rows=recipe.rows,span=h+100*k;
        for(let i=0;i<rows;i++){
            const y=mod(i/rows*span-t*recipe.speed*k,span)-50*k,angle=i*.50+t*recipe.rotationRate;
            const a=w*.5+Math.sin(angle)*w*recipe.amplitude,b=w*.5-Math.sin(angle)*w*recipe.amplitude;
            ctx.strokeStyle=`rgba(80,195,215,${recipe.lineAlpha})`;ctx.lineWidth=2*k;ctx.beginPath();ctx.moveTo(a,y);ctx.lineTo(b,y);ctx.stroke();
            glow(a,y,(7+3*(1+Math.cos(angle)))*k,recipe.glowAlpha,'74,222,165');glow(b,y,(7+3*(1-Math.cos(angle)))*k,recipe.glowAlpha,'86,190,233');
        }
}
