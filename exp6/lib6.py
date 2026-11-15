"""Experiment tools: Sun/Earth share at ANY point (not tied to the 25 m grid), at any ground resolution, any number of horizon directions."""
import sys, os, math, numpy as np, rasterio
_B=os.path.dirname(os.path.abspath(__file__)); EXP2=os.path.join(_B,'..','exp2'); sys.path.insert(0,EXP2); os.chdir(EXP2)   # site_lib loads eph.npz from cwd
from site_lib import *
from site_far import load_far
from numba import njit, prange
from scipy.ndimage import map_coordinates
FAR=load_far()
def build5():
    """5 m composite (same layout as the 25 m one: origin (-19000, 1000), 5200 cols x 4200 rows), holes filled from 60 m far terrain."""
    p=os.path.join(_B,'c5.npy')
    if os.path.exists(p): return np.load(p)
    with rasterio.open('Site01_final_adj_5mpp_surf.tif') as s: g1=s.read(1).astype(np.float32)
    with rasterio.open('Site04_final_adj_5mpp_surf.tif') as s: g4=s.read(1).astype(np.float32)
    C5=np.full((4200,5200),np.nan,np.float32); C5[1000:4200,0:3200]=g1
    sub=C5[0:3200,2000:5200]; C5[0:3200,2000:5200]=np.where(np.isnan(sub),g4,sub)
    a,fx0,fyt,fc=FAR; ii,jj=np.where(np.isnan(C5))
    for lo in range(0,len(ii),2_000_000):
        i=ii[lo:lo+2_000_000];j=jj[lo:lo+2_000_000]; x=-19000+(j+0.5)*5.0; y=1000-(i+0.5)*5.0
        C5[i,j]=map_coordinates(a,[(fyt-y)/fc-0.5,(x-fx0)/fc-0.5],order=1,mode='nearest')
    np.save(p,C5); return C5
def coarsen(C5,f):
    h,w=C5.shape; return C5[:h//f*f,:w//f*f].reshape(h//f,f,w//f,f).mean(axis=(1,3)).astype(np.float32)
@njit(parallel=True,fastmath=True)
def hor_pts(G,gx0,gyt,cell,xs,ys,K,R,F,fx0,fyt,fc,dstep,dmax):
    nr,nc=G.shape;fr,fcn=F.shape;n=xs.shape[0];out=np.empty((K,n),np.float64)
    for p in prange(n):
        x0=xs[p];y0=ys[p]
        fi=(gyt-y0)/cell-0.5;fj=(x0-gx0)/cell-0.5
        if fi<0 or fi>=nr-1 or fj<0 or fj>=nc-1:
            z0=0.0
        else:
            i0=int(fi);j0=int(fj);ai=fi-i0;aj=fj-j0
            z0=G[i0,j0]*(1-ai)*(1-aj)+G[i0+1,j0]*ai*(1-aj)+G[i0,j0+1]*(1-ai)*aj+G[i0+1,j0+1]*ai*aj
        for k in range(K):
            a=2*math.pi*k/K;sa=math.sin(a);ca=math.cos(a);best=-1e9;d=cell
            while True:
                x=x0+sa*d;y=y0+ca*d
                fi=(gyt-y)/cell-0.5;fj=(x-gx0)/cell-0.5
                if fi<0 or fi>=nr-1 or fj<0 or fj>=nc-1: break
                i0=int(fi);j0=int(fj);ai=fi-i0;aj=fj-j0
                z=G[i0,j0]*(1-ai)*(1-aj)+G[i0+1,j0]*ai*(1-aj)+G[i0,j0+1]*(1-ai)*aj+G[i0+1,j0+1]*ai*aj
                t=(z-z0-d*d/(2*R))/d
                if t>best: best=t
                d+=cell
            while d<dmax:
                x=x0+sa*d;y=y0+ca*d
                fy=(fyt-y)/fc-0.5;fx=(x-fx0)/fc-0.5
                if fy<0 or fy>=fr-1 or fx<0 or fx>=fcn-1: break
                i0=int(fy);j0=int(fx);ai=fy-i0;aj=fx-j0
                z=F[i0,j0]*(1-ai)*(1-aj)+F[i0+1,j0]*ai*(1-aj)+F[i0,j0+1]*(1-ai)*aj+F[i0+1,j0+1]*ai*aj
                t=(z-z0-d*d/(2*R))/d
                if t>best: best=t
                d+=dstep
            out[k,p]=math.degrees(math.atan(best)) if best>-1e8 else -10.0
    return out
def shares(G,cell,xs,ys,K=24,floor=FLOOR_DEG,step=4,earth=True):
    xs=np.ascontiguousarray(xs,np.float64);ys=np.ascontiguousarray(ys,np.float64)
    H=hor_pts(G,CX0,CY0,float(cell),xs,ys,K,R_M,FAR[0],FAR[1],FAR[2],FAR[3],90.0,95000.0)
    if floor is not None: H=np.maximum(H,floor)
    lat,lon=C.xy_to_latlon(xs,ys)
    s,e,b=share2(np.ascontiguousarray(H),lat*RAD,lon*RAD,*ser(step),K,SUNR,EARTHR)
    return s,e,b,H
