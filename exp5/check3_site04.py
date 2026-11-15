import sys, json, numpy as np, rasterio
sys.path.insert(0,'../exp3')
import numba as nb
from scipy.ndimage import zoom, binary_dilation, binary_erosion
R=1737400.0
PH='../exp7/photos/photo_crop_site04_CM5.tif'   # same file as the old photo_crop_site04.tif (CM_005 photo cut to Site 04)
d=rasterio.open('../exp2/Site04_final_adj_5mpp_surf.tif'); z5=d.read(1).astype('float32')
print('dem bounds',d.bounds,'nan frac',float(np.isnan(z5).mean()))
z5=np.where(np.isnan(z5),-3000.0,z5)
H=z5.shape[0]; z10=z5.reshape(H//2,2,H//2,2).mean(axis=(1,3)).astype('float64')
x0,ytop=d.bounds.left,d.bounds.top
cx0=int((-8000-x0)/10); cx1=int((4000-x0)/10); cy0=int((ytop-(-2000))/10); cy1=int((ytop-(-14000))/10)
p=rasterio.open(PH).read(1).astype('float32')
pb=p.reshape(1200,5,1200,5)
ph10=pb.mean(axis=(1,3)); valid=(pb>0).all(axis=(1,3))
valid=binary_erosion(valid,iterations=3)
print('crop',cx0,cx1,cy0,cy1,ph10.shape,'valid share %.2f'%valid.mean())
from check3 import shade, sundir
def run(z,az,el): 
    sx,sy=sundir(az); return shade(z,sx,sy,np.tan(np.radians(el)),cy0,cy1,cx0,cx1,R,10.0,16000.0).astype(bool)
def agree(m,thr=15,mask=valid):
    pl=ph10>thr; return float((m==pl)[mask].mean())
def auc(m,mask=valid):
    a=ph10[m&mask]; b=ph10[(~m)&mask]
    if a.size<100 or b.size<100: return 0.0
    rng=np.random.default_rng(0); a=np.sort(rng.choice(a,min(40000,a.size))); b=rng.choice(b,min(40000,b.size))
    return float(1-np.searchsorted(a,b).mean()/a.size)
res={}
best=(0,0,0)
for az in range(0,360,10):
    m=run(z10,az,0.8); s=auc(m); print('az',az,'AUC %.3f lit %.2f'%(s,m[valid].mean()),flush=True)
    if s>best[0]: best=(s,az,0.8)
az0=best[1]; print('coarse best az',az0)
for az in range(az0-9,az0+10,3):
    m=run(z10,az,0.8); s=auc(m)
    if s>best[0]: best=(s,az,0.8)
print('fine best',best)
az1=best[1]
els=[0.0,0.2,0.4,0.6,0.8,1.0,1.3,1.6,2.0,2.5]
rows=[]
for el in els:
    m=run(z10,az1,el); rows.append((el,agree(m),auc(m))); print('el',el,'agree %.3f auc %.3f'%rows[-1][1:],flush=True)
bel=max(rows,key=lambda r:r[1])[0]
m=run(z10,az1,bel); pl=ph10>15
edge=binary_dilation(pl,iterations=10)&~binary_erosion(pl,iterations=10)
def coarse(z,f):
    n=z.shape[0]//f*f; zc=z[:n,:n].reshape(n//f,f,n//f,f).mean(axis=(1,3)); zz=zoom(zc,f,order=1)
    out=np.full_like(z,z.mean()); out[:zz.shape[0],:zz.shape[1]]=zz; return out
mc=run(coarse(z10,6),az1,bel)
out={'best_az':az1,'best_el':bel,'ours_agree':agree(m),'ours_auc':auc(m),'ours_edge':float((m==pl)[edge&valid].mean()),
     'c60_agree':agree(mc),'c60_edge':float((mc==pl)[edge&valid].mean()),'valid_share':float(valid.mean()),'edge_share':float((edge&valid).mean()),
     'photo_lit_share':float(pl[valid].mean()),'model_lit_share':float(m[valid].mean())}
# interior-only (drop 1.5 km west rim where shadow casters lie outside the DEM)
inter=valid.copy(); inter[:, :150]=False
out['ours_agree_interior']=agree(m,mask=inter); out['c60_agree_interior']=agree(mc,mask=inter)
out['rows']=rows
print(json.dumps(out,indent=1)); json.dump(out,open('check3_site04_results.json','w'))
np.save('c3s4_model.npy',m); np.save('c3s4_photo.npy',ph10); np.save('c3s4_valid.npy',valid)
