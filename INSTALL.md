# INSTALL: build the Lunar Landing Site Navigator yourself

You do not need any background. Follow the steps in order, on Windows 10 or 11, in **Command Prompt**
(press the Windows key, type `cmd`, press Enter). Paste one block, press Enter, read the answer.

There are two ways to get the page:

| Way | What you get | Time | Needs |
|---|---|---|---|
| **A. Just open it** | The finished page `Lunar Landing Site Navigator.html` | 1 minute | Chrome or Edge |
| **B. Quick build** | The same page, rebuilt from the ready-made data packs in this repository | about 10 minutes | Python, Node.js |
| **C. Full build** | Everything recomputed from NASA's raw data | several hours, about 15 GB of downloads | B, plus the NASA files in Part 3 |

## A. Just open it

1. Download `Lunar Landing Site Navigator.html` (35 MB) from this repository.
2. Double-click it. It opens in Chrome or Edge. It works offline.
3. Optional check that you have the exact file:

```
certutil -hashfile "Lunar Landing Site Navigator.html" SHA256
```

The answer must be `dac8b3e64b4cf5223c2949a6f94855a8df25d19c84cb6b46f0520f6fc38db0e7`.
The file size is 34,998,820 bytes.

## B. Quick build (rebuild the tool file from this repository)

### B1. Install the programs (once)

```
winget install Python.Python.3.13
winget install OpenJS.NodeJS.LTS
winget install Git.Git
```

Close Command Prompt and open a new one, then check:

```
python --version
node --version
npm --version
git --version
```

Each prints a version number. If `python` opens the Microsoft Store instead, install Python from https://www.python.org/downloads/ and tick "Add python.exe to PATH".

### B2. Get the repository

```
cd %USERPROFILE%
git clone https://github.com/venkateshchhangani/Lunar-Landing-Site-Navigator.git
cd Lunar-Landing-Site-Navigator
```

(Or download the repository as a ZIP from GitHub, unzip it, and `cd` into the folder.)

### B3. Install the Python packages

```
python -m pip install -r requirements.txt
```

### B4. Install the sky-position library (astronomy-engine 2.1.19)

```
cd work\src\node
npm ci
cd ..\..\..
```

### B5. Check that every needed file is here

```
python check_inputs.py
```

For the quick build only section **A** of the report matters: every line must say OK. Lines saying `MISSING` in the later parts are the NASA raw files; they are needed only for the full build (C).

### B6. Build the page

```
cd work\src
python build25.py
```

It prints `34.998662 MB` and writes `index25.html` in `work\src`. Check it:

```
certutil -hashfile index25.html SHA256
```

The answer should be `dac8b3e64b4cf5223c2949a6f94855a8df25d19c84cb6b46f0520f6fc38db0e7`, the same as `Lunar Landing Site Navigator.html`. `build25.py` explicitly opens every text file it reads and writes with `encoding='utf-8'`, and writes `index25.html` with `newline='\n'`, so Windows's default encoding guesses and CRLF conversion don't change the result. This has been verified with a real build run on Windows (Python 3.11.9, Node 24.21.0), cold, from a fresh copy of this repository, with no `PYTHONUTF8` or other environment variable set — it reproduced this exact hash.

## What the quick build needs (all in this repository)

| File | What it is |
|---|---|
| `work/src/app31.html` | The page code before data is packed in |
| `work/src/physics.js` | Moon-geometry code (Sun, Earth, libration, horizon) |
| `work/src/frag.glsl` | The 3D shader |
| `work/src/build25.py` | Packs everything into one HTML file |
| `work/src/node/package.json`, `package-lock.json` | Pin astronomy-engine 2.1.19 (MIT, Don Cross), installed by `npm ci` |
| `work/src/far120.json`, `far120.b64`, `frows.json`, `strict_labels.json` | Ready data packs: far-terrain horizons, tables and trust labels |
| `work/src/moon_4096.jpg`, `earth_bm4096.jpg` | The Moon and Earth pictures (NASA CGI Moon Kit and Blue Marble) |
| `exp2/pack_site01.js`, `pack_site04.js`, `meta_site0X.json`, `dem16_site0X.b64`, `demw_site0X.b64`, `horg_site0X.b64` | Ready terrain and answer packs for Site 01 and Site 04 |

## C. Full build (recompute everything from NASA's raw data)

Do B1 to B4 first. Check disk space: about 15 GB free. The big downloads can be stopped and run again; `curl -C -` and `aria2c -c` carry on where they stopped.

I have not run Part C on Windows. The scripts and the order were run on Linux. The NASA servers were not reachable from my workspace, so the download addresses come from NASA's own listings and from the earlier downloads of the author; if one says "404", find the file on the NASA page named in Part 3.

### C1. Install the two extra tools

```
winget install aria2.aria2
```

(`curl.exe` and `tar.exe` are already in Windows 10 and 11.)

### C2. Download NASA's 5 m terrain for both sites (about 41 MB each)

```
cd exp2
curl.exe -L -C - -O https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site01/Site01_final_adj_5mpp_surf.tif
curl.exe -L -C - -O https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/Site04_final_adj_5mpp_surf.tif
```

Each file is about 41 MB. If a file is only a few KB, NASA sent an error page: delete it and try later.

### C3. Download NASA's illumination maps and convert them

```
curl.exe -L -C - -O https://imbrium.mit.edu/EXTRAS/ILLUMINATION/IMG/AVGVISIB_85S_060M_201608.IMG
curl.exe -L -C - -O https://imbrium.mit.edu/EXTRAS/ILLUMINATION/IMG/AVGVISIB_85S_060M_201608.LBL
curl.exe -L -C - -O https://imbrium.mit.edu/EXTRAS/ILLUMINATION/IMG/AVGVISIB_85S_060M_201608_EARTH.IMG
curl.exe -L -C - -O https://imbrium.mit.edu/EXTRAS/ILLUMINATION/IMG/AVGVISIB_85S_060M_201608_EARTH.LBL
python convert_illum.py
```

(You are still inside `exp2`.) This makes the two `.tiff` files the checks read.

### C4. Far terrain (cropped straight from NASA's server)

```
python ..\exp3\crop_far_terrain.py https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LDEM_60S_60MPP_ADJ.TIF
```

It prints `wrote far_LDEM_60S_60MPP_ADJ.tif ...`. If NASA's server refuses partial reads, download the whole 2.9 GB file with `aria2c -x16 -s16 -c <the address>` and crop it with the same script.

### C5. NASA's 100 alternative grounds for each site (the longest download)

```
cd ..\exp4\clones
python ..\..\exp3\get_clones_fast.py 01 1 100 12
move small\*_err.tif .
cd ..\clones04
python ..\..\exp3\get_clones_fast.py 04 1 100 12
move small\*_err.tif .
cd ..\..
```

### C6. The three LROC photographs and their image lists

```
mkdir lroc
cd lroc
aria2c -x16 -s16 -k1M -c -o NAC_POLE_SOUTH_CM_005_P892S2250.TIF https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/BROWSE/NAC_POLE/NAC_POLE_SOUTH_CM_005/NAC_POLE_SOUTH_CM_005_P892S2250.TIF
aria2c -x16 -s16 -k1M -c -o NAC_POLE_SOUTH_CM_125_P892S2250.TIF https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/BROWSE/NAC_POLE/NAC_POLE_SOUTH_CM_125/NAC_POLE_SOUTH_CM_125_P892S2250.TIF
aria2c -x16 -s16 -k1M -c -o NAC_POLE_SOUTH_CM_335_P892S2250.TIF https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/EXTRAS/BROWSE/NAC_POLE/NAC_POLE_SOUTH_CM_335/NAC_POLE_SOUTH_CM_335_P892S2250.TIF
cd ..
curl.exe -L -o exp7\ids\CM005_IMAGES.TXT https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/BDR/NAC_POLE/NAC_POLE_SOUTH_CM_005/NAC_POLE_SOUTH_CM_005_IMAGES.TXT
curl.exe -L -o exp7\ids\CM125_IMAGES.TXT https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/BDR/NAC_POLE/NAC_POLE_SOUTH_CM_125/NAC_POLE_SOUTH_CM_125_IMAGES.TXT
curl.exe -L -o exp7\ids\CM335_IMAGES.TXT https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/DATA/BDR/NAC_POLE/NAC_POLE_SOUTH_CM_335/NAC_POLE_SOUTH_CM_335_IMAGES.TXT
```

Each photo is about 1.9 GB. Each image list has one line per picture, starting with `M`. If you see HTML instead, the address changed: look in NASA's PDS folder in a browser and save the `_IMAGES.TXT` there.

### C7. Cut each photo down to each site (6 small files)

```
cd lroc
python ..\exp3\crop_lroc_multi.py NAC_POLE_SOUTH_CM_005_P892S2250.TIF ..\exp2\Site01_final_adj_5mpp_surf.tif 01 ..\exp7\photos\photo_crop_site01_CM5.tif
python ..\exp3\crop_lroc_multi.py NAC_POLE_SOUTH_CM_005_P892S2250.TIF ..\exp2\Site04_final_adj_5mpp_surf.tif 04 ..\exp7\photos\photo_crop_site04_CM5.tif
python ..\exp3\crop_lroc_multi.py NAC_POLE_SOUTH_CM_125_P892S2250.TIF ..\exp2\Site01_final_adj_5mpp_surf.tif 01 ..\exp7\photos\photo_crop_site01_CM125.tif
python ..\exp3\crop_lroc_multi.py NAC_POLE_SOUTH_CM_125_P892S2250.TIF ..\exp2\Site04_final_adj_5mpp_surf.tif 04 ..\exp7\photos\photo_crop_site04_CM125.tif
python ..\exp3\crop_lroc_multi.py NAC_POLE_SOUTH_CM_335_P892S2250.TIF ..\exp2\Site01_final_adj_5mpp_surf.tif 01 ..\exp7\photos\photo_crop_site01_CM335.tif
python ..\exp3\crop_lroc_multi.py NAC_POLE_SOUTH_CM_335_P892S2250.TIF ..\exp2\Site04_final_adj_5mpp_surf.tif 04 ..\exp7\photos\photo_crop_site04_CM335.tif
cd ..
rmdir /s /q lroc
```

### C8. The two pictures (only if you want to remake them)

```
cd work\src
curl.exe -L -o bluemarble_5400.jpg https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-topography-bathymetry/january/world.topo.bathy.200401.3x5400x2700.jpg
curl.exe -L -C - -o lroc_color_16bit_srgb_8k.tif https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_16bit_srgb_8k.tif
python make_images.py earth bluemarble_5400.jpg
python make_images.py moon lroc_color_16bit_srgb_8k.tif
cd ..\..
```

### C9. Check that every raw file is in place

```
python check_inputs.py
```

Every line must say OK except the ones marked `(skip)`.

### C10. Recompute everything (the long part, about 80 minutes on a 2-core test machine)

Run in this order, each block in the folder named.

```
cd exp
python ephem.py
copy eph.npz ..\exp2\eph.npz
cd ..\work\src
python make_far120.py ..\..\exp2\far_LDEM_60S_60MPP_ADJ.tif
python make_frows.py
cd ..\..\exp2
python make_dem_pack.py 01
python make_dem_pack.py 04
cd ..\exp5
python check3_site04.py
python check3_site04b.py
cd ..\exp2
python site_pack2.py 01
python site_pack2.py 04
python add_hor.py
copy pack_site01.js pack_site01_v3.js
copy pack_site04.js pack_site04_v3.js
copy meta_site01.json meta_site01_v3.json
copy meta_site04.json meta_site04_v3.json
cd ..\exp6
python e4.py 04
python e4.py 01
python e7a.py
python site_pack3.py 04
python site_pack3.py 01
python clones3.py
python -I finalize3.py
cd ..
```

`site_pack2.py` is the longest (about 23 minutes per site; you can run the two in two windows). After `finalize3.py` the finished `pack_site0X.js`, `meta_site0X.json` and `horg_site0X.b64` in `exp2` replace the ready-made ones.

### C11. Build the page

Do B6 again. A full rebuild may differ slightly from `Lunar Landing Site Navigator.html` if NASA changed a file; the page is then checked by its tests, not by its hash.

## Which program needs what

| Program | Version used | Why |
|---|---|---|
| Python | 3.13 | runs every script |
| numpy 2.5.3, scipy 1.18.1, numba 0.68.0, rasterio 1.5.2, pillow 12.3.0, matplotlib 3.11.2 | pinned in `requirements.txt` | maths, reading NASA GeoTIFF files, pictures |
| astronomy-engine | 2.1.19 (pinned in `package-lock.json`) | Sun, Moon and Earth positions, embedded in the page |
| Node.js and npm | current LTS | install astronomy-engine |
| aria2, curl | any | big downloads (full build only) |

## Resources used (where each file comes from)

| What | Address |
|---|---|
| LOLA 5 m terrain, Site 01 and Site 04, with the 100 alternative grounds | https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/ |
| LOLA far terrain (60 m) | https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/ |
| LOLA average illumination and Earth visibility maps | https://imbrium.mit.edu/EXTRAS/ILLUMINATION/IMG/ |
| LROC NAC south-pole mosaics | https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/LROLRC_2001/ |
| Moon colour map (CGI Moon Kit) | https://svs.gsfc.nasa.gov/4720 |
| Blue Marble Next Generation | https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-topography-bathymetry/ |
| DSN Telecommunications Link Design Handbook 810-005 | https://deepspace.jpl.nasa.gov/dsndocs/810-005/ |
| JPL Horizons (checking only) | https://ssd.jpl.nasa.gov/horizons/ |
| astronomy-engine | https://github.com/cosinekitty/astronomy |

## If something goes wrong

| What you see | Why | Fix |
|---|---|---|
| `python` opens the Microsoft Store | Python is not installed | install it from python.org and tick "Add to PATH" |
| `pip` cannot build `numba` or `rasterio` | No ready-made build for your Python | install Python 3.12 and repeat B3 |
| `build25.py` says file not found `astronomy.browser.min.js` | B4 skipped | run `npm ci` in `work\src\node` |
| `ModuleNotFoundError: site_lib` or similar | A script run from the wrong folder | run each script from the folder named above |
| A script says a `.npz` file is missing | An earlier step in C10 was skipped | run `python check_inputs.py` and redo that step |
| The hash differs | Line endings, or NASA data changed | open the page and check the eight tabs |
| A download stops | Network | run the same line again; `-C -` and `-c` resume |
