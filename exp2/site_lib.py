"""Shared pieces for building a site pack: composite ground (Site01 + Site04), horizons with a NASA-like floor, Sun/Earth shares."""
import sys, math, numpy as np, rasterio
sys.path.insert(0,'../work/src')
from numba import njit, prange
from scipy.ndimage import uniform_filter, median_filter, map_coordinates, gaussian_filter
import check1_illumination as C
RAD=math.pi/180; R_M=1737400.0; K=24; CELL=25.0; SUNR=0.267*RAD; EARTHR=0.9506*RAD
FLOOR_DEG=-1.5                           # horizon never dips below this (NASA's maps behave as if it cannot: see README Session 5)
CX0,CY0=-19000.0,1000.0                  # composite origin (top-left), 25 m cells, 1040 cols x 840 rows
E=np.load('eph.npz')
def g25(path,kind='mean'):
    with rasterio.open(path) as s: z=s.read(1).astype(np.float64)
    return uniform_filter(z,size=5,mode='nearest')[2::5,2::5]
def composite(f1,f4):
    g1=g25(f1); g4=g25(f4); Cm=np.full((840,1040),np.nan)
    Cm[200:840,0:640]=g1                                   # Site01: x -19000..-3000, y -4000..-20000
    sub=Cm[0:640,400:1040]; Cm[0:640,400:1040]=np.where(np.isnan(sub),g4,sub)   # Site04: x -9000..7000, y 1000..-15000
    return Cm
@njit(parallel=True,fastmath=True)
def horizons2(G,gis,gjs,K,cell,R):
    nr,nc=G.shape;n=gis.shape[0];out=np.empty((K,n),np.float64)
    for p in prange(n):
        gi=gis[p];gj=gjs[p];z0=G[gi,gj]
        for k in range(K):
            a=2*math.pi*k/K;dj=math.sin(a);di=-math.cos(a);best=-1e9
            for s in range(1,max(nr,nc)):
                fi=gi+di*s;fj=gj+dj*s
                if fi<0 or fi>=nr-1 or fj<0 or fj>=nc-1: break
                i0=int(fi);j0=int(fj);ai=fi-i0;aj=fj-j0
                z=G[i0,j0]*(1-ai)*(1-aj)+G[i0+1,j0]*ai*(1-aj)+G[i0,j0+1]*(1-ai)*aj+G[i0+1,j0+1]*ai*aj
                d=s*cell;t=(z-z0-d*d/(2*R))/d
                if t>best: best=t
            out[k,p]=math.degrees(math.atan(best)) if best>-1e8 else -10.0
    return out
@njit(parallel=True,fastmath=True)
def share2(H,latr,lonr,sdl,sdn,edl,edn,K,sunr,earr):
    Np=latr.shape[0];ns=sdl.shape[0];sun=np.zeros(Np);ear=np.zeros(Np);both=np.zeros(Np)
    for p in prange(Np):
        sp=math.sin(latr[p]);cp=math.cos(latr[p]);sl_=math.sin(lonr[p]);cl=math.cos(lonr[p]);cs=0;ce=0;cb=0
        for t in range(ns):
            d=sdl[t];L=sdn[t];cdl=cl*math.cos(L)+sl_*math.sin(L);sdlg=math.sin(L)*cl-math.cos(L)*sl_
            el=math.asin(max(-1.0,min(1.0,sp*math.sin(d)+cp*math.cos(d)*cdl)));az=math.atan2(math.cos(d)*sdlg,cp*math.sin(d)-sp*math.cos(d)*cdl)+lonr[p]
            f=(az/(2*math.pi))%1.0*K;k0=int(f)%K;k1=(k0+1)%K;w=f-int(f);h=(H[k0,p]*(1-w)+H[k1,p]*w)*math.pi/180
            lit=1 if el+sunr>h else 0
            d=edl[t];L=edn[t];cdl=cl*math.cos(L)+sl_*math.sin(L);sdlg=math.sin(L)*cl-math.cos(L)*sl_
            el=math.asin(max(-1.0,min(1.0,sp*math.sin(d)+cp*math.cos(d)*cdl)));az=math.atan2(math.cos(d)*sdlg,cp*math.sin(d)-sp*math.cos(d)*cdl)+lonr[p]
            f=(az/(2*math.pi))%1.0*K;k0=int(f)%K;k1=(k0+1)%K;w=f-int(f);h=(H[k0,p]*(1-w)+H[k1,p]*w)*math.pi/180
            ev=1 if el+earr>h else 0
            cs+=lit;ce+=ev;cb+=lit*ev
        sun[p]=cs/ns*100;ear[p]=ce/ns*100;both[p]=cb/ns*100
    return sun,ear,both
def ser(step): return [np.ascontiguousarray(E[k][::step]*RAD) for k in ('sl','sn','el','en')]
class Nasa:
    def __init__(s,sun_path,earth_path):
        s.maps={}
        for nm,pth in (('sun',sun_path),('earth',earth_path)):
            r=rasterio.open(pth);a=r.read(1).astype(np.float64);a[a<0]=0;a=a*0.00004*100
            s.maps[nm]=(median_filter(a,size=3),r.bounds.left,r.bounds.top)
    def at(s,nm,x,y):
        arr,l,t=s.maps[nm];return map_coordinates(arr,[(t-y)/60.0-0.5,(x-l)/60.0-0.5],order=1,mode='nearest')
