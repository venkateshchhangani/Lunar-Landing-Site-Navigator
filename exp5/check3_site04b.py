import sys, json, numpy as np, rasterio
sys.path.insert(0,'../exp3'); sys.path.insert(0,'../exp2')
from scipy.ndimage import zoom, binary_dilation, binary_erosion, map_coordinates, uniform_filter
from check3 import shade, sundir
import site_far as SF
R=1737400.0
PH='../exp7/photos/photo_crop_site04_CM5.tif'   # same file as the old photo_crop_site04.tif (CM_005 photo cut to Site 04)
far=SF.load_far('../exp2/far_LDEM_60S_60MPP_ADJ.tif'); fa,fx0,fyt,fc=far
# big 10 m grid: x -29000..21000, y -31000..19000 (50 km) filled from the 60 m far field, then 5 m tiles on top
X0,YT,NB=-29000.0,19000.0,5000
ii,jj=np.mgrid[0:NB,0:NB]; xs=X0+(jj+0.5)*10; ys=YT-(ii+0.5)*10
G=map_coordinates(fa,[(fyt-ys)/fc-0.5,(xs-fx0)/fc-0.5],order=1,mode='nearest').astype('float64')
def paste(path):
    with rasterio.open(path) as r: z=r.read(1).astype('float64'); b=r.bounds
    z10=z.reshape(z.shape[0]//2,2,z.shape[1]//2,2).mean(axis=(1,3)); ok=np.isfinite(z10)
    r0=int(round((YT-b.top)/10)); c0=int(round((b.left-X0)/10)); h,w=z10.shape
    sub=G[r0:r0+h,c0:c0+w]; sub[ok]=z10[ok]
paste('../exp2/Site01_final_adj_5mpp_surf.tif'); paste('../exp2/Site04_final_adj_5mpp_surf.tif')
cx0=int((-8000-X0)/10); cx1=int((4000-X0)/10); cy0=int((YT-(-2000))/10); cy1=int((YT-(-14000))/10)
p=rasterio.open(PH).read(1).astype('float32'); pb=p.reshape(1200,5,1200,5)
ph10=pb.mean(axis=(1,3)); valid=binary_erosion((pb>0).all(axis=(1,3)),iterations=3)
def run(z,az,el,dmax=30000.0):
    sx,sy=sundir(az); return shade(z,sx,sy,np.tan(np.radians(el)),cy0,cy1,cx0,cx1,R,10.0,dmax).astype(bool)
def agree(m,thr=15,mask=valid): return float((m==(ph10>thr))[mask].mean())
def auc(m,mask=valid):
    a=ph10[m&mask]; b=ph10[(~m)&mask]; rng=np.random.default_rng(0); a=np.sort(rng.choice(a,min(40000,a.size))); b=rng.choice(b,min(40000,b.size)); return float(1-np.searchsorted(a,b).mean()/a.size)
best=(0,0,0)
for az in range(340,376,4):
    for el in (-1.0,-0.6,-0.3,0.0,0.3,0.6,1.0,1.3):
        m=run(G,az%360,el); s=agree(m)
        if s>best[0]: best=(s,az%360,el)
print('best (agree,az,el)',best,flush=True)
_,az1,el1=best
pl=ph10>15; edge=binary_dilation(pl,iterations=10)&~binary_erosion(pl,iterations=10)
m=run(G,az1,el1)
def coarse(z,f):
    n=z.shape[0]//f*f; zc=z[:n,:n].reshape(n//f,f,n//f,f).mean(axis=(1,3)); zz=zoom(zc,f,order=1); out=np.full_like(z,z.mean()); out[:zz.shape[0],:zz.shape[1]]=zz; return out
mc=run(coarse(G,6),az1,el1)
out={'best_az':az1,'best_el':el1,'agree':agree(m),'auc':auc(m),'edge':float((m==pl)[edge&valid].mean()),'c60_agree':agree(mc),'c60_edge':float((mc==pl)[edge&valid].mean()),
 'photo_lit':float(pl[valid].mean()),'model_lit':float(m[valid].mean()),'all_dark_agree':float((~pl)[valid].mean()),'valid_share':float(valid.mean()),'edge_share':float((edge&valid).mean())}
# by region of the page window x -5000..3000
print(json.dumps(out,indent=1)); json.dump(out,open('check3_site04_results_far.json','w'))
np.save('c3b_model.npy',m)
# agreement within 500 m of this site's earlier spots (x,y)
for nm,(x,y) in dict(A=(-2637,-5962),B=(-2087,-3812),C=(-2762,-9137)).items():
    j=int((x+8000)/10); i=int((-2000-y)/10); mk=np.zeros_like(valid); mk[max(0,i-50):i+50,max(0,j-50):j+50]=True; mk&=valid
    print(nm,'valid px',int(mk.sum()),'agree %.3f'%agree(m,mask=mk) if mk.sum()>500 else 'not enough photo coverage')
