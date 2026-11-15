# Lunar Landing Site Navigator

NASA Space Apps Challenge 2026. Team: HERMES POLARIS (Venkatesh Chhangani).

One offline web page that shows the Sun, the Earth, power and radio windows
for landing spots at the Moon's south pole, in plain words.

AI Assistance (Claude, by Anthropic) used for comparing it for validation of
actual data. A full list of AI tools used on this project is provided as a
separate document with this submission. Data sources, physics and
verification are the team's own; see "How it was checked" below and
`THIRD PARTY NOTICES.md`.

## How to run the tool (30 seconds)

1. Click the file **Lunar Landing Site Navigator.html** in the list above.
2. Click the **download icon** (Download raw file) at the top right of the file view.
3. Open the downloaded file in Chrome, Edge or Firefox. It is one file and works offline, with no install and no internet needed.

Demo deck (7 slides): https://docs.google.com/presentation/d/1t-ev6i6ErL7YIrNG3gZPH8swWYC6LuJR/edit?usp=sharing

Check you have the exact file:

- Size: 34,998,820 bytes
- SHA-256: `dac8b3e64b4cf5223c2949a6f94855a8df25d19c84cb6b46f0520f6fc38db0e7`
- Windows: `certutil -hashfile "Lunar Landing Site Navigator.html" SHA256`

Without a graphics card the 3D view is slower but works.

## Build it yourself

Step-by-step instructions for a beginner, a 10-minute quick build and a full
rebuild from NASA's raw data, with every download address, are in
[INSTALL.md](INSTALL.md).

## The eight tabs

- **3D view:** Sun and Earth above the real terrain horizon on any date, with a countdown to sunset
- **Landing planner:** a map of the site to explore
- **Overview:** sunlight share, Earth view and a trust label (High, Medium, Low) for each spot
- **Final answer** and **Calendar:** which start dates work for a stay of N days, for six spots at once
- **Power:** a first estimate of solar energy per day and battery size (geometry only)
- **Comms:** hours Earth is in view while a Deep Space Network station can see the Moon (geometry only)
- **Real missions:** Apollo 11, Chandrayaan-3 and IM-2 as a check

It covers two of NASA's south-pole candidate sites (Site 01 and Site 04), three spots each,
on NASA LOLA 5 m terrain.

## How it was checked

- NASA LOLA illumination maps, NASA's 100 alternative grounds per site, LROC photographs
- Published values for three real landings: 7 of 7 within the stated margins
- NASA JPL Horizons at 12 times for each of nine places: Sun elevation within 0.04 degrees
- An independent audit recomputed the pass counts and got the same numbers
  (reports in `docs/`)

## Honest limits

- The Earth is drawn about 0.23 degrees too high (the page says so)
- Two sites of NASA's 27; no custom coordinates
- Power and Comms are geometry only; thermal conditions are not modelled
- Terrain horizons are checked only against NASA's maps and photographs
- The Landing planner's map is not drawn on windows 820 px wide or narrower
- Not yet tried with real mission planners or teachers
- We do not claim to beat NASA's maps or tools. NASA does not endorse this project.

## What is in this repository

| File or folder | What it holds |
|---|---|
| `Lunar Landing Site Navigator.html` | The finished tool. The whole project in one file: the Moon view, planner, calendar, power and comms tabs, the data and the physics. |
| `README.md` | This page. |
| `INSTALL.md` | Beginner steps to rebuild the page (quick build and full build). |
| `LICENSE` | MIT licence. |
| `THIRD PARTY NOTICES.md` | Every NASA data set, library and credit, with links. |
| `requirements.txt` | Python packages with exact versions. |
| `check_inputs.py` | Prints OK or MISSING for each input file, so a newcomer sees what to download. |
| `.gitignore`, `.gitattributes` | Git settings (files to skip, line endings). |
| `docs/` | `HORIZONS_RESULT.md` (comparison with JPL Horizons) and `AUDIT_REPORT.md` (independent recount of the numbers). They were written for earlier saved versions of the page (index23 and index24), so their file hashes differ from the current `index.html`. |
| `work/src/` | The build. `app31.html` (page layout), `physics.js` (Sun, Earth and horizon maths), `frag.glsl` (Moon shader), `build25.py` (joins everything into `index.html`), `make_far120.py`, `make_frows.py`, `make_images.py` (make the data files), `check1_illumination.py` (our sunlight model against NASA's illumination map), `phys.py` (Python version of the geometry), `far120.b64` and `far120.json` (far terrain), `frows.json` and `strict_labels.json` (table rows and trust-label rules), `earth_bm4096.jpg` and `moon_4096.jpg` (pictures), `node/` (astronomy-engine library list). |
| `exp2/` | Scripts and ready data for the two landing sites: ground height, horizon and sunlight packs (`dem16`, `demw`, `horg`, `meta`, `pack` files for sites 01 and 04). |
| `exp/`, `exp3/`, `exp5/`, `exp6/` | Scripts for experiments, cross-checks against NASA photos and terrain, and the final re-measurement of the spots. |
| `exp4/`, `exp7/` | Empty folders kept by a `.gitkeep` file. The NASA raw files are not stored here; `INSTALL.md` says where to download them. |

## Credits

Data: NASA LRO/LOLA (PGDA), NASA LROC / Arizona State University, NASA Scientific
Visualization Studio (CGI Moon Kit), NASA Earth Observatory (Blue Marble), NASA JPL
(Horizons, Deep Space Network handbook). Library: astronomy-engine 2.1.19 by Don Cross (MIT).
Formulas: Jean Meeus, *Astronomical Algorithms*, ch. 53; solar constant from Kopp and Lean (2011).
Full list: `THIRD PARTY NOTICES.md`.

## Licence

Code and text: MIT licence, Copyright (c) 2026 Venkatesh Chhangani.
