import math, numpy as np, astronomy as A
RAD=math.pi/180; I=1.54242*RAD
def wrap(x): return (x+180)%360-180
def lonlat(v): return (math.degrees(math.atan2(v.y,v.x))%360, math.degrees(math.atan2(v.z,math.hypot(v.x,v.y))))
def selen(lon,lat,T):
    F=(93.2720993+483202.0175273*T-0.0034029*T*T)*RAD; Om=(125.0445479-1934.1362891*T+0.0020754*T*T)*RAD
    W=lon*RAD-Om; b=lat*RAD
    a=math.atan2(math.sin(W)*math.cos(b)*math.cos(I)-math.sin(b)*math.sin(I), math.cos(W)*math.cos(b))
    sb=-math.sin(W)*math.cos(b)*math.sin(I)-math.sin(b)*math.cos(I)
    return wrap(math.degrees(a-F)), math.degrees(math.asin(max(-1,min(1,sb))))
def state(t):
    T=t.tt/36525.0; rot=A.Rotation_EQJ_ECT(t)
    m=A.RotateVector(rot,A.GeoMoon(t)); s=A.RotateVector(rot,A.GeoVector(A.Body.Sun,t,True))
    ml=lonlat(m); e=selen(ml[0],ml[1],T)
    h=type('V',(),{})(); h.x,h.y,h.z=m.x-s.x,m.y-s.y,m.z-s.z; hl=lonlat(h); su=selen(hl[0],hl[1],T)
    return e,su
if __name__=='__main__':
    t=A.Time.Make(2026,10,24,12,0,0); print(state(t))
