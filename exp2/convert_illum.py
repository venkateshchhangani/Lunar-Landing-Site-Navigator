"""Turn NASA's two illumination maps (PDS3 label + .IMG) into the GeoTIFFs the scripts read.
Put AVGVISIB_85S_060M_201608.LBL/.IMG and AVGVISIB_85S_060M_201608_EARTH.LBL/.IMG in this folder, then:  python convert_illum.py
Uses GDAL's PDS reader inside rasterio, so the .LBL must sit next to its .IMG. Result: the two .tiff files (int16, 60 m, scale 0.00004, no-data -32768).
NOT tested here with NASA's real label (NASA's servers are blocked from the build workspace). The delivered .tiff files carry the same PDS tags, so this is how they were most likely made.
If it fails, run `gdal_translate AVGVISIB_85S_060M_201608.LBL AVGVISIB_85S_060M_201608.tiff -of GTiff` instead (QGIS installs gdal_translate)."""
import rasterio, rasterio.shutil
for n in ('AVGVISIB_85S_060M_201608', 'AVGVISIB_85S_060M_201608_EARTH'):
    with rasterio.open(n + '.LBL') as r: print(n, r.shape, r.dtypes, r.res, r.bounds, r.nodata, r.scales)
    rasterio.shutil.copy(n + '.LBL', n + '.tiff', driver='GTiff')
    with rasterio.open(n + '.tiff') as r: print('  ->', n + '.tiff', r.shape, r.dtypes, r.scales, r.nodata)
