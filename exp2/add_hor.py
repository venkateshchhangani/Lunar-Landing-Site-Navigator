"""Add each spot's 24-direction horizon (degrees, floor -1.5) from the same far-field model as the pack, so the page's spot charts agree with the pack numbers."""
import sys,json,numpy as np; sys.path.insert(0,'.')
from site_lib import *; from site_far import *
Cm=composite('Site01_final_adj_5mpp_surf.tif','Site04_final_adj_5mpp_surf.tif'); FAR=load_far(); Cf=fill_holes(Cm,FAR,CX0,CY0,CELL)
for site in ('01','04'):
    txt=open('pack_site%s.js'%site).read(); pk=json.loads(txt.split('var PACK=')[1].rsplit(';',1)[0])
    for s in pk['spots']:
        gi=np.array([int(round((CY0-s['y'])/CELL-0.5))]);gj=np.array([int(round((s['x']-CX0)/CELL-0.5))])
        H=horizons3(Cf,gi,gj,np.array([s['x']]),np.array([s['y']]),24,CELL,R_M,FAR[0],FAR[1],FAR[2],FAR[3],90.0,95000.0)[:,0]
        s['horp']=[round(float(v),3) for v in np.maximum(H,FLOOR_DEG)]
    open('pack_site%s.js'%site,'w').write('var PACK='+json.dumps(pk)+';'); print(site,'ok',[round(max(s['horp']),2) for s in pk['spots']])
