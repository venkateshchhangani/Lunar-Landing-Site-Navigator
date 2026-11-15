"""Stage A of the new pack: choose spots on STABLE ground and measure them as 100 m landing circles on the 5 m ground.
   python3 site_pack3.py 01|04
Writes spots3_site0X.json (spot numbers, 13 circle positions each, horizons) and layers3_site0X.npz (maps on the page's 320 x 320 grid)."""
import sys, os, json, base64, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib6 import *
from scipy.ndimage import convolve, zoom
SITE = sys.argv[1]; t0 = time.time()
def log(*a): print('[%4.0fs]' % (time.time() - t0), *a, flush=True)
W = {'04': (-5000.0, -3000.0), '01': (-15000.0, -8000.0)}[SITE]        # top-left of the 8 km window
RADIUS = 50.0            # landing circle radius, metres
STABLE = 8.0             # a spot may be chosen only if 5 m, 25 m and 60 m ground agree within this many points
SEP = 1000.0             # spots at least this far apart
OUT = os.path.dirname(os.path.abspath(__file__))
old = json.loads(open('pack_site%s_v3.js' % SITE).read().split('var PACK=')[1].rsplit(';', 1)[0])
dec = lambda b: np.frombuffer(base64.b64decode(b), np.uint8).reshape(320, 320).astype(float)
old_sd = dec(old['L']['spread']) / 255 * 12                        # one-cell clone spread (25 m ground), capped at 12
n = 400
D = np.load(os.path.join(EXP2, 'e4_site%s.npz' % SITE)); f = lambda k: D[k].reshape(n, n)
S = {r: f('S%d' % r) for r in (5, 25, 60)}; E = {r: f('E%d' % r) for r in (5, 25, 60)}; B5 = f('B5'); nS = f('nS'); nE = f('nE')
C5 = build5(); G20 = coarsen(C5, 4)
c0 = int(round((W[0] - CX0) / 20)); r0 = int(round((CY0 - W[1]) / 20)); Gw = G20[r0:r0 + n, c0:c0 + n].astype(np.float64)
gy, gx = np.gradient(Gw, 20.0); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
rc = RADIUS / 20.0; ri = int(np.ceil(rc)); yy, xx = np.mgrid[-ri:ri + 1, -ri:ri + 1]
K = ((yy ** 2 + xx ** 2) <= rc * rc + 1e-9).astype(float); K /= K.sum()
dm = lambda a: convolve(a, K, mode='nearest')
cS = {r: dm(S[r]) for r in S}; cE = {r: dm(E[r]) for r in E}; cB = dm(B5)
spS = np.maximum.reduce(list(cS.values())) - np.minimum.reduce(list(cS.values()))
spE = np.maximum.reduce(list(cE.values())) - np.minimum.reduce(list(cE.values()))
spread = np.maximum(spS, spE)
sd20 = zoom(old_sd, 1.25, order=1, grid_mode=True, mode='nearest')
valid = (nS > 1) & (nE > 1) & (slope <= 8); edge = np.zeros((n, n), bool); edge[8:-8, 8:-8] = True; valid &= edge
dsd = np.sqrt(np.clip(dm(S[5] ** 2) - dm(S[5]) ** 2, 0, None))
gapS = np.abs(cS[5] - dm(nS)); gapE = np.abs(cE[5] - dm(nE))
stable = valid & (spread <= STABLE) & (gapS <= 8) & (gapE <= 10) & (dsd <= 8)      # all three grounds agree, NASA agrees, and the circle itself is fairly even
log('window', SITE, 'valid cells', int(valid.sum()), 'stable', int(stable.sum()), 'median spread %.1f' % np.median(spread[valid]))
def far(ps, sep=SEP):
    ii, jj = np.mgrid[0:n, 0:n]; ok = np.ones((n, n), bool)
    for (i, j) in ps: ok &= ((ii - i) ** 2 + (jj - j) ** 2) * 400.0 >= sep * sep
    return ok
def argm(sc, mask): p = np.unravel_index(np.argmax(np.where(mask, sc, -1e9)), sc.shape); return (int(p[0]), int(p[1]))
A = argm(cS[5], stable)
Bp = argm(cS[5] - 2 * sd20, stable & (cE[5] >= 20) & far([A]))        # needs some Earth in view too, or it is of little use for radio
Cp = argm(cB, stable & far([A, Bp]))
WHY = {'A': 'Most sunlight on flat, stable ground', 'B': 'Most sunlight you can rely on (Earth in view too)', 'C': 'Best Sun and Earth together'}
# ---- 13 positions of the landing circle: centre, 6 at 25 m, 6 at 50 m (offset 30 degrees)
ang6 = np.radians(np.arange(6) * 60.0); offs = [(0.0, 0.0)] + [(25 * np.sin(a), 25 * np.cos(a)) for a in ang6] + [(50 * np.sin(a + np.radians(30)), 50 * np.cos(a + np.radians(30))) for a in ang6]
offs = np.array(offs)
nasa = Nasa('AVGVISIB_85S_060M_201608.tiff', 'AVGVISIB_85S_060M_201608_EARTH.tiff')
GR = {5: C5, 25: coarsen(C5, 5), 60: coarsen(C5, 12)}
from site_far import horizons3
spots = []
for nm, (i, j) in zip('ABC', (A, Bp, Cp)):
    x = W[0] + (j + 0.5) * 20.0; y = W[1] - (i + 0.5) * 20.0
    xs = x + offs[:, 0]; ys = y + offs[:, 1]
    R_ = {}
    for r in (5, 25, 60):
        s, e, b, H = shares(GR[r], r, xs, ys); R_[r] = (s, e, b, H)
    s5, e5, b5, H5 = R_[5]
    nsm = float(nasa.at('sun', xs, ys).mean()); nem = float(nasa.at('earth', xs, ys).mean())
    lat, lon = C.xy_to_latlon(np.array([x]), np.array([y]))
    zc = float(map_coordinates(C5, [[(CY0 - y) / 5 - 0.5], [(x - CX0) / 5 - 0.5]], order=1)[0])
    sp = dict(n=nm, why=WHY[nm], x=float(x), y=float(y), lat=float(lat[0]), lon=float(lon[0]), elev=zc, slope=float(slope[i, j]),
              sun=float(s5.mean()), sun_c=float(s5[0]), lo=float(s5.min()), hi=float(s5.max()),
              r5=float(s5.mean()), r25=float(R_[25][0].mean()), r60=float(R_[60][0].mean()),
              e5=float(e5.mean()), e25=float(R_[25][1].mean()), e60=float(R_[60][1].mean()),
              earth=float(e5.mean()), both=float(b5.mean()), nasa=nsm, nasaE=nem,
              ix=int((x - W[0]) // 25), iy=int((W[1] - y) // 25), sd_cell=float(sd20[i, j]),
              horp=[round(float(v), 3) for v in H5[:, 0]], horc=[[round(float(v), 3) for v in H5[:, k]] for k in range(13)])
    sp['res'] = max(max(sp['r5'], sp['r25'], sp['r60']) - min(sp['r5'], sp['r25'], sp['r60']), max(sp['e5'], sp['e25'], sp['e60']) - min(sp['e5'], sp['e25'], sp['e60']))
    sp['diff'] = abs(sp['sun'] - nsm); sp['diffE'] = abs(sp['earth'] - nem)
    spots.append(sp)
    log(nm, 'at (%.0f,%.0f)' % (x, y), 'sun %.1f (centre %.1f, circle %.1f..%.1f) | 5/25/60 m: %.1f/%.1f/%.1f | NASA %.1f | earth %.1f vs %.1f | both %.1f | res %.1f' % (sp['sun'], sp['sun_c'], sp['lo'], sp['hi'], sp['r5'], sp['r25'], sp['r60'], nsm, sp['earth'], nem, sp['both'], sp['res']))
json.dump(spots, open(os.path.join(OUT, 'spots3_site%s.json' % SITE), 'w'))
# ---- layers on the page's 320 x 320 grid
z = lambda a: zoom(a, 0.8, order=1, grid_mode=True, mode='nearest')
np.savez(os.path.join(OUT, 'layers3_site%s.npz' % SITE), sun=z(cS[5]), earth=z(cE[5]), both=z(cB), res=z(spread),
         sun25=z(cS[25]), sun60=z(cS[60]), earth25=z(cE[25]), earth60=z(cE[60]), valid=z(valid.astype(float)) > 0.5, stable=z(stable.astype(float)) > 0.5)
log('layers saved')
