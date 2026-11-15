# builds sun/earth sub-points every 3 h for 18.6 years from 2020 (same as build_pack.py)
import sys,numpy as np
sys.path.insert(0,'../work/src')
import astronomy as A, phys
steps=int(18.6*365.25*8)
base=A.Time.Make(2020,1,1,0,0,0)
sl=np.empty(steps);sn=np.empty(steps);el=np.empty(steps);en=np.empty(steps)
for i in range(steps):
    e,s=phys.state(base.AddDays(i/8.0));sl[i],sn[i]=s[1],s[0];el[i],en[i]=e[1],e[0]
np.savez('eph.npz',sl=sl,sn=sn,el=el,en=en);print(steps)
