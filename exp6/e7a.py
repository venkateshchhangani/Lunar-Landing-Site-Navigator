import sys,time
from lib6 import *
C5=build5(); GR={5:C5,25:coarsen(C5,5),60:coarsen(C5,12)}
t=time.time()
for site,(x0,y0) in {'04':(-5000.0,-3000.0),'01':(-15000.0,-8000.0)}.items():
    gr,gc=np.meshgrid(np.arange(200),np.arange(200),indexing='ij')
    xs=(x0+(gc+0.5)*40).ravel(); ys=(y0-(gr+0.5)*40).ravel()
    for r in (5,25,60):
        H=hor_pts(GR[r],CX0,CY0,float(r),np.ascontiguousarray(xs),np.ascontiguousarray(ys),24,R_M,FAR[0],FAR[1],FAR[2],FAR[3],90.0,95000.0)
        H=np.maximum(H,FLOOR_DEG).T.reshape(200,200,24)
        np.save('hg_%s_%d.npy'%(site,r),H.astype(np.float32)); print(site,r,'done %.0fs'%(time.time()-t),flush=True)
