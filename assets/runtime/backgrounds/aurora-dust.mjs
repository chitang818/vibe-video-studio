import {seeded} from './common.mjs';
export function drawAuroraDust(ctx,frame,recipe){
    const {t,seed,w,h,k,mod,glow}=frame;
        glow(w*(.28+.15*Math.sin(t*.12)),h*(.26+.06*Math.cos(t*.10)),w*.65,recipe.glowAlphaA,'82,162,220');
        glow(w*(.77+.12*Math.cos(t*.09)),h*(.62+.09*Math.sin(t*.11)),w*.70,recipe.glowAlphaB,'83,219,159');
        for(let i=0;i<recipe.dustCount;i++){const x=mod(seeded(seed,i,1)*w+t*(2+seeded(seed,i,3)*5)*k,w),y=mod(seeded(seed,i,2)*h-t*recipe.dustSpeed*k,h);glow(x,y,(2+seeded(seed,i,4)*4)*k,recipe.dustAlpha,'178,229,222');}
}
