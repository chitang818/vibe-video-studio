import {seeded} from './common.mjs';
export function drawCyberGrid(ctx,frame,recipe){
    const {t,seed,w,h,k,mod,glow}=frame;
        const horizon=h*recipe.horizon;
        glow(w*(.3+.08*Math.sin(t*.13)),h*.27,w*.48,recipe.glowAlpha,'69,156,225');
        glow(w*.78,h*.35,w*.35,.10,'76,222,180');
        ctx.lineWidth=1.3*k;ctx.strokeStyle=`rgba(71,206,184,${recipe.lineAlpha})`;
        for(let i=-recipe.columns;i<=recipe.columns;i++){ctx.beginPath();ctx.moveTo(w*.5,horizon);ctx.lineTo(w*.5+i*w*.15,h);ctx.stroke();}
        for(let i=0;i<recipe.rows;i++){const z=mod(i/recipe.rows+t*recipe.speed,1),y=horizon+z*z*(h-horizon);ctx.strokeStyle=`rgba(71,206,184,${.04+recipe.depthAlpha*z})`;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}
}
