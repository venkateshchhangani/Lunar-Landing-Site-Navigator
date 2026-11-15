"""Stage C: write the new pack_site0X.js, meta_site0X.json and horg_site0X.b64 (python3 -I finalize3.py)."""
import sys, os, json, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib6 import *
from scipy.ndimage import uniform_filter
OUT = os.path.dirname(os.path.abspath(__file__))
C3 = json.load(open(os.path.join(EXP2, '..', 'exp5', 'check3_site04_results_far.json')))
CL = np.load(os.path.join(OUT, 'clones3.npz')); CS, CE, CP = CL['S'], CL['E'], list(CL['P'])
b64 = lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
u8 = lambda a: np.clip(np.round(a * 2.55), 0, 255).astype(np.uint8)
dec = lambda b: np.frombuffer(base64.b64decode(b), np.uint8).reshape(320, 320).astype(float)
PHOTO = {'04': dict(spread_hi=(25, .830, .787), spread_lo=(8, .935, .919), top1=(.801, .780), allv=(.876, .853)),
         '01': dict(spread_hi=(20, .884, .792), spread_lo=(6, .972, .968), top1=(.857, .782), allv=(.967, .955))}
from scipy.ndimage import convolve
def overstat(site):
    W = {'04': (-5000.0, -3000.0), '01': (-15000.0, -8000.0)}[site]; n = 400
    D = np.load(os.path.join(EXP2, 'e4_site%s.npz' % site)); f = lambda k: D[k].reshape(n, n)
    rc = 2.5; ri = 3; yy, xx = np.mgrid[-ri:ri + 1, -ri:ri + 1]; K = ((yy ** 2 + xx ** 2) <= rc * rc + 1e-9).astype(float); K /= K.sum(); dm = lambda a: convolve(a, K, mode='nearest')
    cs = {r: dm(f('S%d' % r)) for r in (5, 25, 60)}; ce = {r: dm(f('E%d' % r)) for r in (5, 25, 60)}
    sp = np.maximum(np.maximum.reduce(list(cs.values())) - np.minimum.reduce(list(cs.values())), np.maximum.reduce(list(ce.values())) - np.minimum.reduce(list(ce.values())))
    C5 = build5(); G20 = coarsen(C5, 4); c0 = int(round((W[0] - CX0) / 20)); r0 = int(round((CY0 - W[1]) / 20)); Gw = G20[r0:r0 + n, c0:c0 + n].astype(np.float64)
    gy, gx = np.gradient(Gw, 20.0); slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    valid = (f('nS') > 1) & (slope <= 8); e = np.zeros((n, n), bool); e[8:-8, 8:-8] = True; valid &= e
    ps = uniform_filter(f('S25'), size=4, mode='nearest'); top = valid & (ps >= np.percentile(ps[valid], 99)); rest = valid & ~top
    return (float((ps[top] - cs[5][top]).mean()), float((ps[rest] - cs[5][rest]).mean()), float(np.median(sp[top])), float(np.median(sp[valid])))
OVER = {s_: overstat(s_) for s_ in ('01', '04')}
print('overstatement stats (top1 over, rest over, top1 median spread, all median spread):', OVER)
def photo_near(x, y):
    try:
        m = np.load(os.path.join(EXP2, '..', 'exp5', 'c3b_model.npy')); ph = np.load(os.path.join(EXP2, '..', 'exp5', 'c3s4_photo.npy')); va = np.load(os.path.join(EXP2, '..', 'exp5', 'c3s4_valid.npy'))
    except Exception: return None
    j = int((x + 8000) / 10); i = int((-2000 - y) / 10)
    if not (0 <= i < 1200 and 0 <= j < 1200): return None
    mk = np.zeros(va.shape, bool); mk[max(0, i - 50):i + 50, max(0, j - 50):j + 50] = True; mk &= va
    return float((m == (ph > 15))[mk].mean() * 100) if mk.sum() > 2500 else None
for SITE in ('01', '04'):
    old = json.loads(open(os.path.join(EXP2, 'pack_site%s_v3.js' % SITE)).read().split('var PACK=')[1].rsplit(';', 1)[0])
    meta = json.load(open(os.path.join(EXP2, 'meta_site%s_v3.json' % SITE)))
    spots = json.load(open(os.path.join(OUT, 'spots3_site%s.json' % SITE))); LY = np.load(os.path.join(OUT, 'layers3_site%s.npz' % SITE))
    N = 320; x0p, y0p = (-5000.0, -3000.0) if SITE == '04' else (-15000.0, -8000.0)
    sun, ear, both, res = LY['sun'], LY['earth'], LY['both'], LY['res']
    nS = dec(old['L']['nasa']) / 2.55; nE = dec(old['L']['nasaE']) / 2.55; sdl = dec(old['L']['spread']) / 255 * 12
    # ---- Check 1 numbers on the new layers
    ix, iy = np.meshgrid(np.arange(N), np.arange(N)); inner = (ix >= 4) & (ix < N - 4) & (iy >= 4) & (iy < N - 4); edgekm = np.minimum.reduce([ix, iy, N - 1 - ix, N - 1 - iy]) * 25 / 1000
    def stat(m, a, b):
        d = a[m] - b[m]; return dict(n=int(m.sum()), corr=float(np.corrcoef(a[m], b[m])[0, 1]), bias=float(d.mean()), rms=float(np.sqrt((d ** 2).mean())), w5=float((abs(d) <= 5).mean() * 100), w10=float((abs(d) <= 10).mean() * 100))
    okS = inner & (nS > 1); okE = inner & (nE > 1)
    SS = stat(okS, sun, nS); SR = stat(okS & (edgekm < 1), sun, nS); SC = stat(okS & (edgekm >= 1), sun, nS); ES = stat(okE, ear, nE)
    # ---- spots
    out = []
    for sp in spots:
        k = CP.index('%s%s' % (SITE, sp['n'])); sl = slice(k * 13, (k + 1) * 13)
        cm = CS[:, sl].mean(axis=1); ce = CE[:, sl].mean(axis=1)
        sp['cmin'] = sp.pop('lo', sp.get('cmin')); sp['cmax'] = sp.pop('hi', sp.get('cmax'))
        sp['sd100'] = float(cm.std(ddof=1)); sp['rng'] = float(cm.max() - cm.min()); sp['sd_centre'] = float(CS[:, sl.start].std(ddof=1)); sp['sdE'] = float(ce.std(ddof=1))
        df = max(sp['diff'], sp['diffE'])
        sp['trust'] = 'High' if (sp['sd100'] <= 2 and df <= 5 and sp['res'] <= 6) else ('Medium' if (sp['sd100'] <= 5 and df <= 10 and sp['res'] <= 12) else 'Low')
        sp['photo'] = photo_near(sp['x'], sp['y']) if SITE == '04' else None
        sp['ix'] = int((sp['x'] - x0p) // 25); sp['iy'] = int((y0p - sp['y']) // 25)
        out.append(sp)
        print(SITE, sp['n'], 'sun %.1f (5/25/60 m: %.1f/%.1f/%.1f) NASA %.1f | earth %.1f vs %.1f | both %.1f | res %.1f | sd %.2f rng %.1f | trust %s | photo %s' % (sp['sun'], sp['r5'], sp['r25'], sp['r60'], sp['nasa'], sp['earth'], sp['nasaE'], sp['both'], sp['res'], sp['sd100'], sp['rng'], sp['trust'], sp['photo']))
    valid = LY['valid']; stableL = LY['stable']
    medres = float(np.median(res[valid])); shareStable = float(stableL.sum() / max(1, valid.sum()) * 100)
    P4 = PHOTO[SITE]
    ev1 = ("<b>Check 1, against NASA's sunlight map:</b> we average our sunlit share over a 100 m wide landing circle on NASA's 5 m ground and compare it with NASA's value at every point of this 8 km area. "
           "They correlate at <b>%.2f</b>; <b>%.0f%%</b> of the ground is within 10 points of NASA and %.0f%% within 5. On average ours is %+.1f points from NASA's. "
           "Shadows are cast by NASA's 5 m ground over both Site 01 and Site 04 together (about 26 km across), and beyond that by NASA's 60 m terrain out to about 95 km, so far crater walls (such as Shackleton's) shade the ground as they should. The outer 1 km of the map runs %+.1f points from NASA's (inside it: %+.1f).") % (SS['corr'], SS['w10'], SS['w5'], SS['bias'], SR['bias'], SC['bias'])
    ev1e = ("<b>Check 1b, against NASA's Earth-visibility map:</b> NASA's two maps behave as if the horizon can never dip below about 1.5 degrees under level (its Earth map never exceeds 58%%, its Sun map 88%%), so we use the same limit. "
            "Earth (again averaged over the 100 m circle) correlates with NASA's at <b>%.2f</b>, <b>%.0f%%</b> of the ground is within 10 points and %.0f%% within 5 (mean difference %+.1f). "
            "This limit is also the cautious choice for a lander: from a summit the true horizon can dip lower, so Earth may be visible more often than we say.") % (ES['corr'], ES['w10'], ES['w5'], ES['bias'])
    head = old['ev2'].split(' Spots on a ridge edge')[0]
    head = head.replace('At one 25 m spot the sunlit share', 'At a single 25 m cell the sunlit share')
    ev2 = (head.replace('%', '%%') + " For the three recommended spots, averaged over their 100 m landing circle, the share moves much less: ±%.1f, ±%.1f and ±%.1f points (highest minus lowest across the clones: %.0f, %.0f and %.0f). A single point at the centre moves more (±%.1f, ±%.1f, ±%.1f), which is one more reason to judge a landing circle rather than one point. The map colours and the planner use the single-cell figure, which is the cautious one.") % (
        *[out[q]['sd100'] for q in range(3)], *[out[q]['rng'] for q in range(3)], *[out[q]['sd_centre'] for q in range(3)])
    if SITE == '01':
        ev3 = old['ev3']
    else:
        ev3 = ("<b>Check 3, a real spacecraft photo (LROC, Sun 0 to 10 degrees from the pole direction):</b> we cast shadows on our 5 m ground (and NASA's 60 m terrain beyond it) and compare with the photo. It covers only the western two-thirds (%.0f%%) of a 12 km x 12 km square around this site; the east, including Shackleton's floor, is missing from it. Best fit Sun height %.1f degrees, Sun direction %d degrees from the pole's north; <b>%.0f%%</b> of the covered ground is lit or dark as in the photo (a model that says everything is dark would score %.0f%%; with ground made 60 m coarse: %.1f%%), and <b>%.0f%%</b> right at the shadow edges (60 m: %.0f%%). %s Same caveats as Site 01: the photo mixes pictures taken at different times, the Sun height was fitted, and it tests shadows, not heights.") % (
            C3['valid_share'] * 100, C3['best_el'], C3['best_az'], C3['agree'] * 100, C3['all_dark_agree'] * 100, C3['c60_agree'] * 100, C3['edge'] * 100, C3['c60_edge'] * 100,
            'Within 500 m of the three spots: ' + ', '.join('%s %s' % (q['n'], ('%.0f%%' % q['photo']) if q['photo'] is not None else 'outside the photo') for q in out) + '.')
    ev4 = ("<b>Check 4, does the answer depend on how fine the ground is?</b> We ran the same 18.6-year calculation on three versions of NASA's ground: the 5 m ground, the same ground blurred to 25 m, and blurred to 60 m (the size NASA's own public maps use). "
           "Over this window they typically differ by %.0f points (median), but at the places that look best on a coarse map the typical difference is %.0f points, because the small ridges that coarse ground smooths away are what block a low Sun. "
           "On the earlier version of this page, the best-looking 1%% of ground read on average <b>%.0f points</b> higher than a 100 m landing circle on the 5 m ground (other ground: %.0f points higher). "
           "So we now (1) judge every place as a 100 m landing circle, not one point, (2) recommend only places where the three versions agree within 8 points and also agree with NASA (%.0f%% of the usable ground here), and (3) lower the trust label when they differ by more than 6 (Medium up to 12, Low above). "
           "The real photo supports the finer ground where it matters: within 60 m of cells where the three versions differ by %d points or more, the 5 m ground matches the photo %.1f%% of the time against %.1f%% for the 60 m ground; where they agree within %d points the photo matches %.1f%% (60 m: %.1f%%). "
           "Caveats: one Sun direction per photo, overlapping circles, and a photo tests shadows rather than hours of sunlight, so this supports the choice but does not prove it.") % (
        OVER[SITE][3], OVER[SITE][2], OVER[SITE][0], OVER[SITE][1], shareStable, P4['spread_hi'][0], P4['spread_hi'][1] * 100, P4['spread_hi'][2] * 100, P4['spread_lo'][0], P4['spread_lo'][1] * 100, P4['spread_lo'][2] * 100)
    trustleg = "Trust: High = changes by 2 points or less under ground error, is within 5 points of NASA's Sun and Earth maps, and the 5, 25 and 60 m grounds agree within 6 points. Medium = 5, 10 and 12. Low = anything worse."
    nb = 100
    ban = ("Check 2 (if the ground heights are slightly wrong) is done with %d of NASA's alternative grounds. Check 3 (against a real spacecraft photo) is done for the shadows (see Overview). Check 4 (does the answer depend on how fine the ground is?) is done on 5, 25 and 60 m ground. Numbers are averages over a 100 m wide landing circle.") % nb
    if SITE == '01':
        conf3 = old['conf3']; pill3, cls3 = old['pill3'], old['cls3']
    else:
        pill3, cls3 = 'done · %.0f%% match' % (C3['agree'] * 100), 'ok'
        conf3 = " The photo check (%.0f%% of the covered ground matches, %.0f%% right at the shadow edges) is shown but does not change the label yet; the photo does not cover the east of this area." % (C3['agree'] * 100, C3['edge'] * 100)
    L = dict(sun=b64(u8(sun)), spread=old['L']['spread'], nasa=old['L']['nasa'], earth=b64(u8(ear)), both=b64(u8(both)), nasaE=old['L']['nasaE'], res=b64(np.clip(np.round(res / 40 * 255), 0, 255).astype(np.uint8)))
    pack = dict(N=N, site=SITE, name=old['name'], L=L, spots=out, ban=ban, pill2='%d NASA clones' % nb, meas=True, pill3=pill3, cls3=cls3, conf3=conf3,
                ev1=ev1, ev1e=ev1e, ev2=ev2, ev3=ev3, ev4=ev4, trustleg=trustleg, stats=dict(sun=SS, sun_rim=SR, sun_core=SC, earth=ES),
                spread='measured on 100 of NASA\'s clones for this site (Site 01 and Site 04 clones paired by number); spots judged as 100 m circles')
    open(os.path.join(EXP2, 'pack_site%s.js' % SITE), 'w').write('var PACK=' + json.dumps(pack) + ';')
    meta['spots'] = [dict(n=s['n'], why=s['why'], x=s['x'], y=s['y'], lat=s['lat'], lon=s['lon']) for s in out]
    json.dump(meta, open(os.path.join(EXP2, 'meta_site%s.json' % SITE), 'w'))
    H = np.load(os.path.join(EXP2, 'hg_%s_5.npy' % SITE)); q = np.clip(np.round(H * 1000), -32000, 32000).astype('<i2')
    open(os.path.join(EXP2, 'horg_site%s.b64' % SITE), 'w').write(base64.b64encode(q.tobytes()).decode())
    print(SITE, 'Check1 sun', {k: round(v, 2) for k, v in SS.items()}, '| earth', {k: round(v, 2) for k, v in ES.items()}, '| median res %.1f stable share %.0f%%' % (medres, shareStable))
