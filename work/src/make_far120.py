"""Make far120.b64 + far120.json (the far terrain the page embeds: NASA 60 m terrain, 200 km wide, averaged 2 x 2 to 120 m, 16-bit).
Run inside work/src:   python make_far120.py ..\\..\\exp2\\far_LDEM_60S_60MPP_ADJ.tif
Checked against the file used for the delivered page: identical, every cell (the 2 x 2 average is done in 64-bit)."""
import json, base64, sys, numpy as np, rasterio
src = sys.argv[1]
r = rasterio.open(src); a = r.read(1).astype(np.float32); a = np.where(np.isfinite(a), a, -3000.0).astype(np.float32)
n = a.shape[0] // 2; b = a[:2 * n, :2 * n].reshape(n, 2, n, 2).mean(axis=(1, 3), dtype=np.float64)
zmin, zmax = float(b.min()), float(b.max()); u = np.round((b - zmin) / (zmax - zmin) * 65535).astype('<u2')
open('far120.b64', 'w').write(base64.b64encode(u.tobytes()).decode())
json.dump(dict(zmin=zmin, zmax=zmax, n=n, cell=float(r.res[0]) * 2), open('far120.json', 'w'))
print('far120 written', n, zmin, zmax)
