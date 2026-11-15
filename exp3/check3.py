import sys, numpy as np, rasterio, numba as nb, json
from rasterio.windows import from_bounds
DEM='../exp2/Site01_final_adj_5mpp_surf.tif'
PH='../exp7/photos/photo_crop_site01_CM5.tif'   # same file as the old photo_crop_site01.tif (CM_005 photo cut to Site 01)
R=1737400.0
d=rasterio.open(DEM)
z5=d.read(1).astype('float32')
nodata=d.nodata
H=z5.shape[0]; z10=z5.reshape(H//2,2,H//2,2).mean(axis=(1,3)).astype('float64')   # 10 m, full 16 km
x0,y_top=d.bounds.left,d.bounds.top      # -19000, -4000
# crop window in 10 m grid
cx0=int((-15000-x0)/10); cx1=int((-5000-x0)/10); cy0=int((y_top-(-7000))/10); cy1=int((y_top-(-17000))/10)
p=rasterio.open(PH).read(1).astype('float32')
ph10=p.reshape(1000,5,1000,5).mean(axis=(1,3))
print('crop in dem grid',cx0,cx1,cy0,cy1,ph10.shape)

@nb.njit(parallel=True,cache=True)
def shade(z,sx,sy,tanel,cy0,cy1,cx0,cx1,R,step,dmax):
    out=np.zeros((cy1-cy0,cx1-cx0),np.uint8)
    n=z.shape[0]
    for i in nb.prange(cy1-cy0):
        r=cy0+i
        for jj in range(cx1-cx0):
            c=cx0+jj
            z0=z[r,c]; lit=1
            # x increases with col, y increases UP the rows (row decreases)
            k=1
            while True:
                dd=k*step
                if dd>dmax: break
                fx=c+sx*dd/step; fy=r-sy*dd/step
                if fx<0 or fy<0 or fx>n-1.001 or fy>n-1.001: break
                ix=int(fx); iy=int(fy); ax=fx-ix; ay=fy-iy
                zz=(z[iy,ix]*(1-ax)+z[iy,ix+1]*ax)*(1-ay)+(z[iy+1,ix]*(1-ax)+z[iy+1,ix+1]*ax)*ay
                if (zz-z0)/dd-dd/(2*R)>tanel:
                    lit=0; break
                k+=1
            out[i,jj]=lit
    return out

def sundir(gaz):   # grid azimuth: measured from +y (north), toward +x
    a=np.radians(gaz); return np.sin(a),np.cos(a)

def score(m,ph):
    # compare lit mask with photo brightness: use rank-based separation
    lit=m.astype(bool)
    if lit.all() or (~lit).all(): return -1,0
    a=ph[lit]; b=ph[~lit]
    # AUC via ranks on a subsample
    rng=np.random.default_rng(0); ia=rng.choice(a.size,min(40000,a.size),replace=False); ib=rng.choice(b.size,min(40000,b.size),replace=False)
    A_=np.sort(a[ia]); B_=b[ib]
    auc=np.searchsorted(A_,B_,side='left').mean()/A_.size   # P(lit<shadow)
    return 1-auc, lit.mean()

if __name__=='__main__':
    mode=sys.argv[1]
    res=[]
    if mode=='az':
        for gaz in range(0,360,10):
            sx,sy=sundir(gaz)
            m=shade(z10,sx,sy,np.tan(np.radians(0.8)),cy0,cy1,cx0,cx1,R,10.0,16000.0)
            s,f=score(m,ph10); res.append((gaz,s,f)); print('az',gaz,'AUC %.3f lit %.2f'%(s,f),flush=True)
