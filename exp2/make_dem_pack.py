"""Make the two ground files the page embeds (dem16_site0X.b64 = 8 km at 5 m, 16-bit; demw_site0X.b64 = whole 16 km tile at 20 m, 16-bit).
Same lines as the end of site_pack2.py, without the hours-long maps.   Run inside the exp2 folder:   python make_dem_pack.py 01   and   python make_dem_pack.py 04"""
import sys, base64, numpy as np, rasterio
SITE = sys.argv[1]
P = {'01': dict(x0p=-15000.0, y0p=-8000.0, surf='Site01_final_adj_5mpp_surf.tif'),
     '04': dict(x0p=-5000.0, y0p=-3000.0, surf='Site04_final_adj_5mpp_surf.tif')}[SITE]
x0p, y0p = P['x0p'], P['y0p']
with rasterio.open(P['surf']) as s:
    z = s.read(1).astype(np.float64); b = s.bounds
r0 = int(round((b.top - y0p) / 5)); c0 = int(round((x0p - b.left) / 5)); crop = z[r0:r0 + 1600, c0:c0 + 1600]
q = lambda a, lo, hi: np.round((a - lo) / (hi - lo) * 65535).astype('<u2')
zmin, zmax = float(crop.min()), float(crop.max()); open('dem16_site%s.b64' % SITE, 'w').write(base64.b64encode(q(crop, zmin, zmax).tobytes()).decode())
zw = z.reshape(800, 4, 800, 4).mean(axis=(1, 3)); wmin, wmax = float(zw.min()), float(zw.max()); open('demw_site%s.b64' % SITE, 'w').write(base64.b64encode(q(zw, wmin, wmax).tobytes()).decode())
print('wrote dem16_site%s.b64 and demw_site%s.b64' % (SITE, SITE), zmin, zmax, wmin, wmax)
