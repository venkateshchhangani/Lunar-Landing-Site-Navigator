"""Cut a small piece out of a big NASA terrain file (LDEM_60S_60MPP_ADJ.TIF or LDEM_83S_10MPP_ADJ.TIF).

Run in the folder that holds the big file:
    pip install rasterio
    python crop_far_terrain.py LDEM_60S_60MPP_ADJ.TIF                 (default: 100 km around the pole, 60 m pixels)
    python crop_far_terrain.py LDEM_83S_10MPP_ADJ.TIF 60 20           (60 km around the pole, 20 m pixels)
NO DOWNLOAD NEEDED: you can give it the web address instead of a file name, and it fetches only the part it needs
(a few hundred MB instead of 2.9 / 4.8 GB), e.g.
    python crop_far_terrain.py https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_60S_60MPP_ADJ.TIF
If the server does not allow partial reads it will say so; then download the whole file instead.
The two optional numbers are: half-width in km, then output pixel size in metres.
It reads only the part it needs, so it is quick and uses little memory.
Result: far_<file name>.tif . Attach that file.
"""
import os, sys
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling

src = sys.argv[1]
HALF = (float(sys.argv[2]) if len(sys.argv) > 2 else 100.0) * 1000.0
RES = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
out = "far_" + os.path.splitext(os.path.basename(src.split("?")[0]))[0] + ".tif"
env = rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF",
                   GDAL_HTTP_MAX_RETRY="6", GDAL_HTTP_RETRY_DELAY="4", CPL_VSIL_CURL_CHUNK_SIZE="4194304",
                   GDAL_HTTP_MULTIPLEX="YES", GDAL_HTTP_VERSION="2")
env.__enter__()
with rasterio.open(src) as r:
    print("file:", r.width, "x", r.height, "pixels,", r.res, "m/pixel, bounds", r.bounds)
    print("crs:", r.crs.to_string()[:200] if r.crs else None)
    print("dtype", r.dtypes[0], "nodata", r.nodata)
    n = int(round(2 * HALF / RES))
    win = from_bounds(-HALF, -HALF, HALF, HALF, transform=r.transform)
    data = r.read(1, window=win, out_shape=(n, n), resampling=Resampling.average, boundless=True,
                  fill_value=(np.nan if r.dtypes[0].startswith("float") else (r.nodata or 0))).astype("float32")
    tr = rasterio.transform.from_bounds(-HALF, -HALF, HALF, HALF, n, n)
    prof = dict(driver="GTiff", height=n, width=n, count=1, dtype="float32", crs=r.crs, transform=tr,
                compress="lzw", nodata=r.nodata)
    with rasterio.open(out, "w", **prof) as o:
        o.write(data, 1)
ok = np.isfinite(data) & (data != (r.nodata if r.nodata is not None else 1e30))
print("wrote", out, n, "x", n, "pixels at", RES, "m | usable pixels %.0f%%" % (100 * ok.mean()),
      "| height range", float(data[ok].min()), "to", float(data[ok].max()))
