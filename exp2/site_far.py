"""Far-field terrain: NASA's 60 m LOLA (LDEM_60S_60MPP_ADJ, 100 km around the pole) used beyond the 5 m ground,
and to fill holes of the 5 m composite. Rays continue into it, so crater walls 10-90 km away shade the site."""
import math, numpy as np, rasterio
from numba import njit, prange
from scipy.ndimage import map_coordinates
def load_far(path='far_LDEM_60S_60MPP_ADJ.tif'):
    with rasterio.open(path) as r:
        a=r.read(1).astype(np.float32); b=r.bounds
    a=np.where(np.isfinite(a),a,-3000.0).astype(np.float32)
    return a,float(b.left),float(b.top),float((b.right-b.left)/a.shape[1])
def fill_holes(Cm,far,CX0,CY0,CELL):
    """Replace NaN in the composite by far-field heights (bilinear) so nothing is a hole."""
    a,fx0,fyt,fc=far; nr,nc=Cm.shape
    ii,jj=np.where(np.isnan(Cm)); x=CX0+(jj+0.5)*CELL; y=CY0-(ii+0.5)*CELL
    v=map_coordinates(a,[(fyt-y)/fc-0.5,(x-fx0)/fc-0.5],order=1,mode='nearest')
    out=Cm.copy(); out[ii,jj]=v; return out
@njit(parallel=True,fastmath=True)
def horizons3(G,gis,gjs,pxs,pys,K,cell,R,F,fx0,fyt,fc,dstep,dmax):
    nr,nc=G.shape;fr,fcn=F.shape;n=gis.shape[0];out=np.empty((K,n),np.float64)
    for p in prange(n):
        gi=gis[p];gj=gjs[p];z0=G[gi,gj]
        for k in range(K):
            a=2*math.pi*k/K;sa=math.sin(a);ca=math.cos(a);dj=sa;di=-ca;best=-1e9;s=1
            while s<max(nr,nc):
                fi=gi+di*s;fj=gj+dj*s
                if fi<0 or fi>=nr-1 or fj<0 or fj>=nc-1: break
                i0=int(fi);j0=int(fj);ai=fi-i0;aj=fj-j0
                z=G[i0,j0]*(1-ai)*(1-aj)+G[i0+1,j0]*ai*(1-aj)+G[i0,j0+1]*(1-ai)*aj+G[i0+1,j0+1]*ai*aj
                d=s*cell;t=(z-z0-d*d/(2*R))/d
                if t>best: best=t
                s+=1
            d=s*cell
            while d<dmax:
                x=pxs[p]+sa*d;y=pys[p]+ca*d
                fy=(fyt-y)/fc-0.5;fx=(x-fx0)/fc-0.5
                if fy<0 or fy>=fr-1 or fx<0 or fx>=fcn-1: break
                i0=int(fy);j0=int(fx);ai=fy-i0;aj=fx-j0
                z=F[i0,j0]*(1-ai)*(1-aj)+F[i0+1,j0]*ai*(1-aj)+F[i0,j0+1]*(1-ai)*aj+F[i0+1,j0+1]*ai*aj
                t=(z-z0-d*d/(2*R))/d
                if t>best: best=t
                d+=dstep
            out[k,p]=math.degrees(math.atan(best)) if best>-1e8 else -10.0
    return out
