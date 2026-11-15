"""Check that every file the project needs is in the right place.   Run in the Project folder:   python check_inputs.py
Prints OK / MISSING for each file, in the order you need them. Nothing is changed."""
import os, glob, sys
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
miss = 0
def need(path, why, optional=False):
    global miss
    ok = os.path.exists(path) and os.path.getsize(path) > 0
    tag = 'OK     ' if ok else ('(skip) ' if optional else 'MISSING')
    if not ok and not optional: miss += 1
    print('%s %-62s %s' % (tag, path, why))
def count(pattern, n, why):
    global miss
    k = len(glob.glob(pattern)); ok = k == n; miss += (not ok)
    print('%s %-62s %s (%d of %d)' % ('OK     ' if ok else 'MISSING', pattern, why, k, n))
print('--- A. quick rebuild of index.html (no big downloads) ---')
for f in ('app31.html', 'build25.py', 'physics.js', 'frag.glsl', 'far120.json', 'far120.b64', 'frows.json', 'strict_labels.json', 'moon_4096.jpg', 'earth_bm4096.jpg'):
    need('work/src/' + f, 'page source / picture')
need('work/src/node/node_modules/astronomy-engine/astronomy.browser.min.js', 'run: cd work\\src\\node  then  npm ci')
for s in ('01', '04'):
    for f in ('pack_site%s.js', 'meta_site%s.json', 'horg_site%s.b64', 'dem16_site%s.b64', 'demw_site%s.b64'):
        need('exp2/' + f % s, 'finished data pack for the page')
print('\n--- B. recompute everything from NASA data ---')
for s in ('01', '04'):
    need('exp2/Site%s_final_adj_5mpp_surf.tif' % s, 'NASA 5 m ground')
need('exp2/AVGVISIB_85S_060M_201608.tiff', 'NASA Sun map (Check 1)')
need('exp2/AVGVISIB_85S_060M_201608_EARTH.tiff', 'NASA Earth map (Check 1)')
need('exp2/far_LDEM_60S_60MPP_ADJ.tif', 'far terrain 60 m (cropped)')
count('exp4/clones/Site01_final_adj_5mpp_*_err.tif', 100, 'Site 01 alternative grounds (shrunk to 20 m)')
count('exp4/clones04/Site04_final_adj_5mpp_*_err.tif', 100, 'Site 04 alternative grounds (shrunk to 20 m)')
for s in ('01', '04'):
    for cm in ('5', '125', '335'):
        need('exp7/photos/photo_crop_site%s_CM%s.tif' % (s, cm), 'LROC photo cut to the site')
for cm in ('005', '125', '335'):
    need('exp7/ids/CM%s_IMAGES.TXT' % cm, 'list of source pictures of the photo')
print('\n--- optional ---')
for s in ('01', '04'): need('exp2/Site%s_final_adj_5mpp_toterr.tif' % s, 'NASA height-error map (early experiments only)', True)
need('exp2/far_LDEM_83S_10MPP_ADJ.tif', '10 m terrain, cross-check only', True)
need('exp2/eph.npz', 'made by exp\\ephem.py', True)
print('\n%s' % ('Everything required is in place.' if not miss else '%d required item(s) MISSING.' % miss))
