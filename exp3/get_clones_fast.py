"""Same as get_clones.py but downloads several files AT THE SAME TIME (NASA slows each single download).

Run from a folder (for example ss\\clones01):
    python ..\\get_clones_fast.py 01 6 100         <- Site 01, clones 6 to 100, 8 at a time
    python ..\\get_clones_fast.py 04 1 100         <- Site 04, clones 1 to 100, 8 at a time
Optional 4th number = how many at once (default 8):  python ..\\get_clones_fast.py 04 1 100 12
Each big file is shrunk to 20 m and deleted right away. If it stops, run the same line again: finished files are skipped.
Result: clones_small_Site01.zip (or Site04). Attach that zip.
"""
import os, sys, time, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
import rasterio
from rasterio.enums import Resampling

site, a, b = sys.argv[1].zfill(2), int(sys.argv[2]), int(sys.argv[3])
WORKERS = int(sys.argv[4]) if len(sys.argv) > 4 else 8
BASE = os.environ.get("CLONE_BASE", "https://pgda.gsfc.nasa.gov/data/LOLA_5mpp")
F = 4                                                    # 5 m -> 20 m
os.makedirs("small", exist_ok=True)

def one(n):
    name = "Site%s_final_adj_5mpp_%04d_err.tif" % (site, n)
    out = os.path.join("small", name)
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        print(name, "already done", flush=True); return name, True
    url = "%s/Site%s/Clones/%s" % (BASE, site, name)
    tmp = "big_%04d.tmp" % n
    for attempt in range(1, 6):
        try:
            print(name, "downloading (try %d)" % attempt, flush=True)
            urllib.request.urlretrieve(url, tmp)
            with rasterio.open(tmp) as r:
                h, w = r.height // F, r.width // F
                arr = r.read(1, out_shape=(h, w), resampling=Resampling.average).astype("float32")
                tr = r.transform * r.transform.scale(r.width / w, r.height / h)
                prof = dict(driver="GTiff", height=h, width=w, count=1, dtype="float32", crs=r.crs,
                            transform=tr, compress="lzw", nodata=r.nodata)
                with rasterio.open(out + ".part", "w", **prof) as o:
                    o.write(arr, 1)
            os.replace(out + ".part", out)
            os.remove(tmp)
            print(name, "finished", flush=True)
            return name, True
        except Exception as e:
            print("   problem with", name, ":", e, flush=True); time.sleep(5)
            if os.path.exists(tmp):
                try: os.remove(tmp)
                except OSError: pass
    return name, False

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    results = list(ex.map(one, range(a, b + 1)))
done = [n for n, ok in results if ok]
failed = [n for n, ok in results if not ok]
zname = "clones_small_Site%s.zip" % site
with zipfile.ZipFile(zname, "w", zipfile.ZIP_DEFLATED) as z:
    for f in done:
        z.write(os.path.join("small", f), f)
print("\nDONE: %s  (%.1f MB, %d files)" % (zname, os.path.getsize(zname) / 1e6, len(done)))
if failed:
    print("These failed, run the same command again:", ", ".join(failed))
