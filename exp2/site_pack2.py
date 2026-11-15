"""Build one site's data pack for the page.   python site_pack.py 01|04
Sun and Earth shares over 18.6 years on the 8 km page window (25 m cells, 320 x 320) from the composite 5 m ground (Site01 + Site04),
horizon floor -1.5 deg, compared with NASA's 60 m Sun and Earth maps; ground-error spread from NASA clones (Site01) or a calibrated assumed pattern (Site04)."""
import sys,glob,json,base64,time,os; sys.path.insert(0,'.')
from site_lib import *
from site_far import *
from scipy.ndimage import zoom
C3=json.load(open('../exp5/check3_site04_results_far.json'))
SITE=sys.argv[1]; t0=time.time()
def log(*a): print('[%4.0fs]'%(time.time()-t0),*a,flush=True)
P={'01':dict(x0p=-15000.0,y0p=-8000.0,wx0=-19000.0,wy0=-4000.0,surf='Site01_final_adj_5mpp_surf.tif',err='Site01_final_adj_5mpp_toterr.tif',name='Site 01 (connecting ridge)'),
   '04':dict(x0p=-5000.0,y0p=-3000.0,wx0=-9000.0,wy0=1000.0,surf='Site04_final_adj_5mpp_surf.tif',err='Site04_final_adj_5mpp_toterr.tif',name='Site 04 (Shackleton rim)')}[SITE]
N=320; x0p,y0p=P['x0p'],P['y0p']
Cm=composite('Site01_final_adj_5mpp_surf.tif','Site04_final_adj_5mpp_surf.tif'); FAR=load_far(); Cf=fill_holes(Cm,FAR,CX0,CY0,CELL)
g4=g25('Site04_final_adj_5mpp_surf.tif'); own4=np.zeros((640,640),bool); s01=np.zeros((840,1040),bool); s01[200:840,0:640]=True
own4=~s01[0:640,400:1040]&~np.isnan(g4)
ci0=int(round((CY0-y0p)/CELL)); cj0=int(round((x0p-CX0)/CELL))
ii,jj=np.meshgrid(np.arange(N),np.arange(N),indexing='ij'); gis=(ci0+ii).ravel().astype(np.int64); gjs=(cj0+jj).ravel().astype(np.int64)
px=(x0p+(jj+0.5)*CELL).ravel(); py=(y0p-(ii+0.5)*CELL).ravel()
lat,lon=C.xy_to_latlon(px,py); latr=lat*RAD; lonr=lon*RAD
ix_=jj.ravel();iy_=ii.ravel(); inner_=((ix_>=4)&(ix_<N-4)&(iy_>=4)&(iy_<N-4))
nasa=Nasa('AVGVISIB_85S_060M_201608.tiff','AVGVISIB_85S_060M_201608_EARTH.tiff')
nS=nasa.at('sun',px,py); nE=nasa.at('earth',px,py)
def run(Gc,step,sel=None):
    if sel is None: sel=np.arange(N*N)
    H=np.maximum(np.ascontiguousarray(horizons3(Gc,np.ascontiguousarray(gis[sel]),np.ascontiguousarray(gjs[sel]),np.ascontiguousarray(px[sel]),np.ascontiguousarray(py[sel]),K,CELL,R_M,FAR[0],FAR[1],FAR[2],FAR[3],90.0,95000.0)),FLOOR_DEG)
    return share2(H,np.ascontiguousarray(latr[sel]),np.ascontiguousarray(lonr[sel]),*ser(step),K,SUNR,EARTHR)
sun0,ear0,both0=run(Cf,4); log('baseline mean sun %.1f earth %.1f both %.1f'%(sun0.mean(),ear0.mean(),both0.mean()))
# ---- spread of the sunlit share under ground error: NASA's clones (paired by number across both sites)
N2=N//2; SEL=np.where(((ii%2==0)&(jj%2==0)).ravel())[0]
def up(v): return zoom(v.reshape(N2,N2),2,order=1).ravel()      # clone runs use every 2nd cell (50 m), then are smoothly filled in
def ldclones(pat):
    fs=sorted(glob.glob(pat)); return {int(f.split('_')[-2]):f for f in fs}
cl1=ldclones('../exp4/clones/Site01_final_adj_5mpp_*_err.tif'); cl4=ldclones('../exp4/clones04/Site04_final_adj_5mpp_*_err.tif')
with rasterio.open('Site01_final_adj_5mpp_surf.tif') as r: z20a=r.read(1).astype(np.float64).reshape(800,4,800,4).mean(axis=(1,3))
with rasterio.open('Site04_final_adj_5mpp_surf.tif') as r: z20b=r.read(1).astype(np.float64).reshape(800,4,800,4).mean(axis=(1,3))
ci_,cj_=np.meshgrid(np.arange(640),np.arange(640),indexing='ij')
cc1=((-19000+(cj_+0.5)*CELL)+19000)/20.0-0.5; rr1=(-4000-(-4000-(ci_+0.5)*CELL))/20.0-0.5
cc4=((-9000+(cj_+0.5)*CELL)+9000)/20.0-0.5;   rr4=(1000-(1000-(ci_+0.5)*CELL))/20.0-0.5
def dd_of(path,z20,cc,rr):
    with rasterio.open(path) as r: c=r.read(1).astype(np.float64)
    return map_coordinates(c-z20,[rr,cc],order=1,mode='nearest')
nums=sorted(set(cl1)|set(cl4))
if SITE=='04' and not cl4: nums=[]
S=[];EA=[]
for n in nums:
    Gk=Cf.copy()
    if n in cl1: Gk[200:840,0:640]+=dd_of(cl1[n],z20a,cc1,rr1)
    if n in cl4: Gk[0:640,400:1040]+=np.where(own4,dd_of(cl4[n],z20b,cc4,rr4),0.0)
    s_,e_,b_=run(Gk,12,SEL); S.append(s_);EA.append(e_); log('clone pair',n,'(Site01' if n in cl1 else '(',', Site04)' if n in cl4 else ')')
S=np.array(S);EA=np.array(EA); NCL=len(S)
var=up(S.var(axis=0,ddof=1)) if NCL>1 else np.zeros(N*N)
sunS=np.sqrt(np.clip(uniform_filter(var.reshape(N,N),size=3,mode='nearest'),0,None)).ravel()
rng_raw=up(S.max(axis=0)-S.min(axis=0)) if NCL>1 else np.zeros(N*N); earS=up(EA.std(axis=0,ddof=1)) if NCL>1 else np.zeros(N*N)
sd75=np.sqrt(np.clip(uniform_filter(var.reshape(N,N),size=3,mode='nearest'),0,None)).ravel()
NC1=sum(1 for n in nums if n in cl1); NC4=sum(1 for n in nums if n in cl4)
need=cl4 if SITE=='04' else cl1
if SITE=='04' and not cl4:
    # no Site 04 clones yet: an assumed pattern (100 m, NASA's height error) scaled by the factor measured at Site 01
    sg=g25(P['err']); acc=[]; rng2=np.random.default_rng(100)
    for r in range(12):
        f=gaussian_filter(rng2.standard_normal((640,640)),100/CELL,mode='wrap');f/=f.std()
        Gk=Cf.copy();Gk[0:640,400:1040]+=np.where(own4,sg*f,0.0); s_,_,_=run(Gk,12,SEL);acc.append(s_);log('  MC',r+1,'/12')
    cal=json.load(open('site01_spread_calibration.json'))['factor']; s100=up(np.array(acc).std(axis=0,ddof=1))*cal
    sunS=np.sqrt(np.clip(uniform_filter((s100**2).reshape(N,N),size=3,mode='nearest'),0,None)).ravel(); rng_raw=s100*2.3; sd75=s100*0.45; earS=s100*0.9
    NSP=0; spread_note='assumed pattern (100 m), scaled by the factor %.2f measured at Site 01 (no Site 04 clones loaded)'%cal; MEAS=False
else:
    NSP=len(nums); MEAS=True
    spread_note='measured on %d of NASA\'s clones for this site (%d Site 01 + %d Site 04 clones, paired by number)'%(NSP,NC1,NC4)
log('spread ready; mean %.2f'%sunS.mean(), spread_note)
# ---- compare with NASA
S3=lambda a: uniform_filter(a.reshape(N,N),size=3,mode='nearest').ravel()
sunA=S3(sun0); earA=S3(ear0)
ix=jj.ravel();iy=ii.ravel(); inner=((ix>=4)&(ix<N-4)&(iy>=4)&(iy<N-4)); edgekm=(np.minimum.reduce([ix,iy,N-1-ix,N-1-iy])*CELL/1000)
def stat(m,a,b):
    dd=a[m]-b[m];return dict(n=int(m.sum()),corr=float(np.corrcoef(a[m],b[m])[0,1]),bias=float(dd.mean()),rms=float(np.sqrt((dd**2).mean())),w5=float((abs(dd)<=5).mean()*100),w10=float((abs(dd)<=10).mean()*100))
okS=inner&(nS>1); okE=inner&(nE>1)
SS=stat(okS,sunA,nS); SR=stat(okS&(edgekm<1),sunA,nS); SC=stat(okS&(edgekm>=1),sunA,nS); ES=stat(okE,earA,nE)
log('Sun',SS);log('Earth',ES)
# ---- ground window and slope
Gt=Cf[ci0:ci0+N,cj0:cj0+N]; zref=float(Gt.mean()); gy,gx=np.gradient(Gt,CELL); slope=np.degrees(np.arctan(np.hypot(gx,gy))).ravel()
mask=okS&okE&(slope<=8)
dist=lambda p,q: math.hypot(p%N-q%N,p//N-q//N)
far=lambda ps:(np.array([min(dist(p,q) for q in ps) for p in range(N*N)])>=40) if ps else np.ones(N*N,bool)
A=int(np.argmax(np.where(mask,sunA,-1)))
B=int(np.argmax(np.where(mask&far([A]),sunA-2*sunS,-1e9)))
Cc=int(np.argmax(np.where(mask&far([A,B]),both0,-1e9)))
def loc(arr,p): a=arr.reshape(N,N);return float(a[max(0,p//N-2):p//N+3,max(0,p%N-2):p%N+3].mean())
def trust(p):
    ds=abs(sunA[p]-loc(nS,p)); de=abs(earA[p]-loc(nE,p)); df=max(ds,de); sd=sunS[p]
    return ('High' if sd<=2 and df<=5 else ('Medium' if sd<=5 and df<=10 else 'Low')),ds,de
spots=[]
for name,p,why in (('A',A,'Most sunlight on flat ground'),('B',B,'Most sunlight you can rely on'),('C',Cc,'Best Sun and Earth together')):
    t,ds,de=trust(p)
    spots.append(dict(n=name,why=why,ix=int(p%N),iy=int(p//N),x=float(px[p]),y=float(py[p]),lat=float(lat[p]),lon=float(lon[p]),elev=float(Gt.ravel()[p]),slope=float(slope[p]),sun=float(sunA[p]),sd100=float(sunS[p]),nasa=loc(nS,p),diff=float(ds),earth=float(earA[p]),nasaE=loc(nE,p),diffE=float(de),both=float(both0[p]),rng=float(rng_raw[p]),trust=t)); log(spots[-1])
# ---- text
def photo_near(x,y):
    try:
        m=np.load('../exp5/c3b_model.npy'); ph=np.load('../exp5/c3s4_photo.npy'); va=np.load('../exp5/c3s4_valid.npy')
    except Exception: return None
    j=int((x+8000)/10); i=int((-2000-y)/10)
    if not(0<=i<1200 and 0<=j<1200): return None
    mk=np.zeros(va.shape,bool); mk[max(0,i-50):i+50,max(0,j-50):j+50]=True; mk&=va
    return float((m==(ph>15))[mk].mean()*100) if mk.sum()>2500 else None
for sp in spots: sp['photo']=photo_near(sp['x'],sp['y']) if SITE=='04' else None
nb_=len(nums)
ev1=("<b>Check 1, against NASA's sunlight map:</b> we compare our sunlit share (averaged over about 75 m, the size of NASA's pixels) with NASA's value at every point of this 8 km area. "
 "They correlate at <b>%.2f</b>; <b>%.0f%%</b> of the ground is within 10 points of NASA and %.0f%% within 5. On average ours is %+.1f points from NASA's. "
 "Shadows are cast by NASA's 5 m ground over both Site 01 and Site 04 together (about 26 km across), and beyond that by NASA's 60 m terrain out to about 95 km, so far crater walls (such as Shackleton's) shade the ground as they should. The outer 1 km of the map runs %+.1f points from NASA's (inside it: %+.1f).")%(SS['corr'],SS['w10'],SS['w5'],SS['bias'],SR['bias'],SC['bias'])
ev1e=("<b>Check 1b, against NASA's Earth-visibility map:</b> at first our Earth numbers ran about 15 points above NASA's. NASA's two maps behave as if the horizon can never dip below about 1.5 degrees under level (its Earth map never exceeds 58%%, its Sun map 88%%). With the same limit in our model, Earth correlates at <b>%.2f</b>, <b>%.0f%%</b> of the ground is within 10 points and %.0f%% within 5 (mean difference %+.1f). "
 "This limit is also the cautious choice for a lander: from a summit the true horizon can dip lower, so Earth may be visible more often than we say.")%(ES['corr'],ES['w10'],ES['w5'],ES['bias'])
if MEAS:
    ev2=("<b>Check 2, if NASA's ground heights are slightly wrong:</b> we re-ran the full 18.6-year sunlight on %d of NASA's alternative grounds (the clones, %d for Site 01 and %d for Site 04, applied together). At one 25 m spot the sunlit share moves by about ±%.1f points on average (±%.1f at the least stable 10%% of ground). "
     "Spots on a ridge edge swing most: across the clones the sunlit share at A moves %.0f points (highest minus lowest), at B %.0f, at C %.0f.")%(NSP,NC1,NC4,sunS[inner].mean(),np.percentile(sunS[inner],90),*[spots[k]['rng'] for k in range(3)])
else:
    ev2=("<b>Check 2, if NASA's ground heights are slightly wrong:</b> NASA's clones for this site are not loaded yet, so this uses an assumed error pattern (about 100 m long, NASA's own height error) scaled to match what the real clones showed at Site 01. At one 25 m spot the sunlit share moves by about ±%.1f points on average (±%.1f at the least stable 10%% of ground).")%(sunS[inner].mean(),np.percentile(sunS[inner],90))
if SITE=='01':
    ev3="<b>Check 3, a real spacecraft photo (LROC, Sun 0 to 10 degrees from the pole direction):</b> we cast shadows on our 5 m ground and compare with the photo over 10 km x 10 km that contains all three spots. Best fit Sun height 1.3 degrees; <b>98%</b> of the ground is lit or dark as in the photo (ground made 60 m coarse, like NASA's public map: 97.7%), and <b>92%</b> right at the shadow edges (60 m: 89%). Caveats: the photo is a mosaic of pictures taken at different times, the Sun height was fitted, and the photo is geo-located with LOLA, so this tests shadows, not heights."
    pill3,cls3='done · 98% match','ok'
    conf3=" The photo check (98% of the ground matches, 92% right at the shadow edges) is shown but does not change the label yet, because the photo mosaic mixes pictures taken at different times."
else:
    ev3=("<b>Check 3, a real spacecraft photo (LROC, Sun 0 to 10 degrees from the pole direction):</b> we cast shadows on our 5 m ground (and NASA's 60 m terrain beyond it) and compare with the photo. It covers only the western two-thirds (%.0f%%) of a 12 km x 12 km square around this site; the east, including Shackleton's floor, is missing from it. Best fit Sun height %.1f degrees, Sun direction %d degrees from the pole's north; <b>%.0f%%</b> of the covered ground is lit or dark as in the photo (a model that says everything is dark would score %.0f%%; with ground made 60 m coarse: %.1f%%), and <b>%.0f%%</b> right at the shadow edges (60 m: %.0f%%). %s Same caveats as Site 01: the photo mixes pictures taken at different times, the Sun height was fitted, and it tests shadows, not heights.")%(C3['valid_share']*100,C3['best_el'],C3['best_az'],C3['agree']*100,C3['all_dark_agree']*100,C3['c60_agree']*100,C3['edge']*100,C3['c60_edge']*100,'Within 500 m of the three spots: '+', '.join('%s %s'%(q['n'],('%.0f%%'%q['photo']) if q['photo'] is not None else 'outside the photo') for q in spots)+'.')
    pill3,cls3='done · %.0f%% match'%(C3['agree']*100),'ok'
    conf3=" The photo check (%.0f%% of the covered ground matches, %.0f%% right at the shadow edges) is shown but does not change the label yet; the photo does not cover the east of this area."%(C3['agree']*100,C3['edge']*100)
if MEAS: pill2='%d NASA clones'%NSP; ban2="Check 2 (if the ground heights are slightly wrong) is done with %d of NASA's alternative grounds. "%NSP
else: pill2='assumed pattern'; ban2="Check 2 (if the ground heights are slightly wrong) uses an assumed error pattern for this site, because its clones are not loaded yet. "
ban3="Check 3 (against a real spacecraft photo) is done for the shadows (see Overview)."
trustleg="Trust: High = changes by 2 points or less under ground error and within 5 points of NASA's Sun and Earth maps. Medium = 5 and 10. Low = anything worse."
b64=lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
u8=lambda a: np.clip(np.round(a*2.55),0,255).astype(np.uint8)
pack=dict(N=N,site=SITE,name=P['name'],L=dict(sun=b64(u8(sunA)),spread=b64(np.clip(np.round(sunS/12*255),0,255).astype(np.uint8)),nasa=b64(u8(np.where(nS>0,nS,0))),earth=b64(u8(earA)),both=b64(u8(both0)),nasaE=b64(u8(np.where(nE>0,nE,0)))),
  spots=spots,ban=ban2+ban3,pill2=pill2,meas=MEAS,pill3=pill3,cls3=cls3,conf3=conf3,ev1=ev1,ev1e=ev1e,ev2=ev2,ev3=ev3,trustleg=trustleg,stats=dict(sun=SS,sun_rim=SR,sun_core=SC,earth=ES),spread=spread_note)
open('pack_site%s.js'%SITE,'w').write('var PACK='+json.dumps(pack)+';')
# ---- page ground files
with rasterio.open(P['surf']) as s: z=s.read(1).astype(np.float64); b=s.bounds
r0=int(round((b.top-y0p)/5)); c0=int(round((x0p-b.left)/5)); crop=z[r0:r0+1600,c0:c0+1600]
q=lambda a,lo,hi: np.round((a-lo)/(hi-lo)*65535).astype('<u2')
zmin,zmax=float(crop.min()),float(crop.max()); open('dem16_site%s.b64'%SITE,'w').write(base64.b64encode(q(crop,zmin,zmax).tobytes()).decode())
zw=z.reshape(800,4,800,4).mean(axis=(1,3)); wmin,wmax=float(zw.min()),float(zw.max()); open('demw_site%s.b64'%SITE,'w').write(base64.b64encode(q(zw,wmin,wmax).tobytes()).decode())
meta=dict(site=SITE,name=P['name'],cx0=x0p,cy0=y0p,wx0=P['wx0'],wy0=P['wy0'],zmin=zmin,zmax=zmax,wzmin=wmin,wzmax=wmax,
          spots=[dict(n=s['n'],why=s['why'],x=s['x'],y=s['y'],lat=s['lat'],lon=s['lon']) for s in spots],center=dict(lat=float(lat.mean()),lon=float(np.degrees(np.arctan2(np.mean(np.sin(lonr)),np.mean(np.cos(lonr)))))))
json.dump(meta,open('meta_site%s.json'%SITE,'w')); json.dump(spots,open('spots_site%s.json'%SITE,'w'))
log('done')
