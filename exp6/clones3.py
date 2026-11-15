"""Re-run NASA's 100 alternative grounds (clones) for the NEW spots: each clone's height errors added to the 5 m ground (Site 01 and Site 04 clone k together)."""
import sys, os, json, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib6 import *
from scipy.ndimage import zoom
t0=time.time(); OUT=os.path.dirname(os.path.abspath(__file__))
ang6=np.radians(np.arange(6)*60.0); offs=np.array([(0.0,0.0)]+[(25*np.sin(a),25*np.cos(a)) for a in ang6]+[(50*np.sin(a+np.radians(30)),50*np.cos(a+np.radians(30))) for a in ang6])
P=[]; 
for site in ('01','04'):
    for sp in json.load(open(os.path.join(OUT,'spots3_site%s.json'%site))): P.append((site,sp['n'],sp['x'],sp['y']))
xs=np.concatenate([x+offs[:,0] for (_,_,x,y) in P]); ys=np.concatenate([y+offs[:,1] for (_,_,x,y) in P])
C5=build5()
with rasterio.open('Site01_final_adj_5mpp_surf.tif') as r: z1=r.read(1).astype(np.float64)
with rasterio.open('Site04_final_adj_5mpp_surf.tif') as r: z4=r.read(1).astype(np.float64)
z20a=z1.reshape(800,4,800,4).mean(axis=(1,3)); z20b=z4.reshape(800,4,800,4).mean(axis=(1,3)); del z1,z4
own4=np.ones((3200,3200),bool); own4[1000:3200,0:1200]=False        # Site 04 ground that is not covered by Site 01
base=shares(C5,5,xs,ys,step=12)
cl1={int(f.split('_')[-2]):f for f in glob.glob(os.path.join(EXP2,'..','exp4','clones','Site01_final_adj_5mpp_*_err.tif'))}
cl4={int(f.split('_')[-2]):f for f in glob.glob(os.path.join(EXP2,'..','exp4','clones04','Site04_final_adj_5mpp_*_err.tif'))}
nums=sorted(set(cl1)&set(cl4)); print('clones',len(nums),flush=True)
S=[];E=[];Bo=[]
for n in nums:
    with rasterio.open(cl1[n]) as r: d1=r.read(1).astype(np.float64)-z20a
    with rasterio.open(cl4[n]) as r: d4=r.read(1).astype(np.float64)-z20b
    d1u=zoom(d1,4,order=1,grid_mode=True,mode='nearest'); d4u=zoom(d4,4,order=1,grid_mode=True,mode='nearest')
    Gk=C5.copy(); Gk[1000:4200,0:3200]+=d1u.astype(np.float32); Gk[0:3200,2000:5200]+=np.where(own4,d4u,0.0).astype(np.float32)
    s,e,b,_=shares(Gk,5,xs,ys,step=12); S.append(s);E.append(e);Bo.append(b)
    if n%10==0: print('clone',n,'%.0fs'%(time.time()-t0),flush=True)
np.savez(os.path.join(OUT,'clones3.npz'),S=np.array(S),E=np.array(E),B=np.array(Bo),base_s=base[0],base_e=base[1],base_b=base[2],P=np.array([f'{a}{b}' for a,b,_,_ in P]),nums=np.array(nums))
print('done %.0fs'%(time.time()-t0))
