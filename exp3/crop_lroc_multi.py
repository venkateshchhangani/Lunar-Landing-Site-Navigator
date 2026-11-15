"""Crop a big LROC photo to the Site 01 or Site 04 area.
Usage (in the folder with the files):
    python crop_lroc_multi.py PHOTO.TIF Site04_final_adj_5mpp_surf.tif 04 photo_crop_site04_CM125.tif
The 1.9 GB photo is never loaded whole; only the window needed is read."""
import sys, numpy as np, rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from rasterio.enums import Resampling
photo_path, dem_path, site, out = sys.argv[1:5]
OUT_RES = 2.0
X0, X1, Y0, Y1 = {'04': (-8000.0, 4000.0, -14000.0, -2000.0), '01': (-15000.0, -5000.0, -17000.0, -7000.0)}[site]
with rasterio.open(dem_path) as d: dem_crs = d.crs
with rasterio.open(photo_path) as p:
    print("photo:", p.width, "x", p.height, p.res, p.crs)
    b = (X0, Y0, X1, Y1)
    if p.crs != dem_crs: b = transform_bounds(dem_crs, p.crs, *b)
    win = from_bounds(*b, transform=p.transform)
    ow = int(round((b[2] - b[0]) / OUT_RES)); oh = int(round((b[3] - b[1]) / OUT_RES))
    data = p.read(window=win, out_shape=(p.count, oh, ow), resampling=Resampling.average, boundless=True, fill_value=0)
    tr = rasterio.transform.from_bounds(b[0], b[1], b[2], b[3], ow, oh)
    prof = dict(driver="GTiff", height=oh, width=ow, count=p.count, dtype=data.dtype, crs=p.crs, transform=tr, compress="lzw")
    with rasterio.open(out, "w", **prof) as o: o.write(data)
print("wrote", out, ow, "x", oh, "non-empty %.0f%%" % (100 * float((data > 0).mean())))
