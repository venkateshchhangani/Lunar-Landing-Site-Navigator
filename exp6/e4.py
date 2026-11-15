import sys,time
from lib6 import *
site=sys.argv[1]
C5=build5(); GR={5:C5,25:coarsen(C5,5),60:coarsen(C5,12)}
W={'04':(-5000.0,-3000.0),'01':(-15000.0,-8000.0)}[site]   # top-left of the 8 km pack window
sp=20.0; n=400
jj,ii=np.meshgrid(np.arange(n),np.arange(n)); xs=(W[0]+(jj+0.5)*sp).ravel(); ys=(W[1]-(ii+0.5)*sp).ravel()
nasa=Nasa('AVGVISIB_85S_060M_201608.tiff','AVGVISIB_85S_060M_201608_EARTH.tiff')
out=dict(xs=xs,ys=ys,nS=nasa.at('sun',xs,ys),nE=nasa.at('earth',xs,ys))
t=time.time()
for r in (60,25,5):
    s,e,b,_=shares(GR[r],r,xs,ys); out['S%d'%r]=s;out['E%d'%r]=e;out['B%d'%r]=b; print('res',r,'done %.0fs'%(time.time()-t),flush=True)
np.savez('e4_site%s.npz'%site,**out)
