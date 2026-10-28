import {seeded} from './common.mjs';
export function drawBioBubbles(ctx,frame,recipe){
    const {t,seed,w,h,k,mod,glow}=frame;
        // Stratified layers cover the whole canvas; independent random streams add natural jitter.
        for(let i=0;i<recipe.farCount+recipe.midCount+recipe.nearCount;i++){
            const near=i>=recipe.farCount+recipe.midCount,mid=i>=recipe.farCount&&!near,index=near?i-recipe.farCount-recipe.midCount:mid?i-recipe.farCount:i;
            const cols=near?recipe.nearCols:mid?recipe.midCols:recipe.farCols,rows=near?recipe.nearRows:mid?recipe.midRows:recipe.farRows;
            const radius=(near?recipe.nearRadius+seeded(seed,i,4)*recipe.nearRadiusRange:mid?recipe.midRadius+seeded(seed,i,4)*recipe.midRadiusRange:recipe.farRadius+seeded(seed,i,4)*recipe.farRadiusRange)*k;
            const phase=seeded(seed,i,7)*Math.PI*2;
            const x=(index%cols+.3+.4*seeded(seed,i,1))*w/cols+Math.sin(t*.17+phase)*(near?14:8)*k;
            const y=mod((Math.floor(index/cols)+.3+.4*seeded(seed,i,2))*h/rows-t*(near?recipe.nearSpeed:mid?recipe.midSpeed:recipe.farSpeed)*k,h);
            const r=radius*(1+recipe.pulseAmount*Math.sin(t*.65+phase));
            const paint=yy=>{
                if(near||mid)glow(x,yy,r,near?recipe.nearOpacity:recipe.midOpacity,i%3?recipe.primary:recipe.secondary);
                else{ctx.fillStyle='rgba(112,231,192,.30)';ctx.beginPath();ctx.arc(x,yy,r,0,Math.PI*2);ctx.fill();}
            };
            paint(y);if(y<r)paint(y+h);if(y>h-r)paint(y-h);
        }
}
