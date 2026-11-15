"""Make the two pictures the page embeds. Run inside work/src.
   python make_images.py moon  lroc_color_16bit_srgb_8k.tif        ->  moon_4096.jpg   (NASA SVS CGI Moon Kit colour map)
   python make_images.py earth bluemarble_5400.jpg                 ->  earth_bm4096.jpg (NASA Blue Marble NG, topography + bathymetry)
Both are shrunk to 4096 x 2048. The JPEG quality is close to, but not identical with, the delivered files (not re-checked against NASA's originals)."""
import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
kind, src = sys.argv[1], sys.argv[2]
im = Image.open(src)
if kind == 'moon':
    if im.mode.startswith('I;16') or im.mode in ('I', 'RGB;16'):
        im = im.convert('RGB')
    arr = np.array(im)
    if arr.dtype == np.uint16: im = Image.fromarray((arr / 257.0).round().astype(np.uint8))
    im.convert('RGB').resize((4096, 2048), Image.LANCZOS).save('moon_4096.jpg', quality=85)
elif kind == 'earth':
    im.convert('RGB').resize((4096, 2048), Image.LANCZOS).save('earth_bm4096.jpg', quality=90)
else: raise SystemExit('use: moon or earth')
print('done')
