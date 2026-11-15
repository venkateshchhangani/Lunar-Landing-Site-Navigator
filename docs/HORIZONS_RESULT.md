# JPL Horizons comparison: result

Run 14 Nov 2026 against the frozen page index24 (34,996,313 bytes, SHA-256 `437d338d438a32c739845c155db27e9c04b7fa19ea3adb2aefb22b9dd512eed5`, hash checked before the run). The page was not edited.

## Files
All 22 files of `horizons_out.zip` hold a table; none holds an error. `H01` has 78 rows, `H02` to `H22` have 12 rows each, exactly the times asked for.

## What the Horizons headers say
| Question | Header line found |
|---|---|
| Ephemeris | `{source: DE441}` |
| Moon frame for the lunar sites | `Center pole/equ : MEAN_ME (high precision)`, east longitude positive. This is the same mean-Earth frame as the LOLA ground |
| Moon radius | `Center radii : 1737.4, 1737.4, 1737.4 km` (a sphere; the page uses 1,737,400 m) |
| Site echo, Site 04 A | `Center geodetic : 206.12545, -89.826999, 1.637` (what was sent) |
| How azimuth is measured | "Azimuth is measured clockwise from north: North(0) -> East(90) -> South(180) -> West(270)" |
| Lunar sites | `Atmos refraction: NO (AIRLESS)`, columns `Azimuth_(a-app), Elevation_(a-app)` |
| Antennas | `Atmos refraction: YES (Earth refraction model)`, columns `(r-app)`, frame ITRF93, Earth radii 6378.137 / 6356.752 km |
| Time scale | UT (the header says times after 1962 are UTC) |

Every setting I had marked as unsure worked as assumed.

## Differences, page minus Horizons (degrees)
| Quantity | Places | n | Median | 95th | Max | Mean (signed) | Threshold | Verdict |
|---|---|---|---|---|---|---|---|---|
| Sun elevation | six polar spots | 72 | 0.018 | 0.035 | 0.039 | +0.009 | 0.10 / 0.30 | PASS |
| Sun elevation | Apollo 11, Chandrayaan-3, IM-2 | 36 | 0.010 | 0.032 | 0.034 | +0.002 | 0.10 / 0.30 | PASS |
| Sun azimuth | three mission sites | 36 | 0.014 | 0.026 | 0.147 | -0.001 | 0.10 / 0.30 | NOTE |
| Earth elevation | six polar spots | 72 | 0.232 | 0.259 | 0.261 | +0.234 | 0.30 / 0.50 | PASS |
| Earth elevation | three mission sites | 36 | 0.219 | 0.276 | 0.285 | +0.207 | 0.30 / 0.50 | PASS |
| Earth azimuth | three mission sites | 36 | 0.013 | 0.070 | 0.112 | +0.025 | 0.30 / 0.50 | PASS |
| Moon elevation, refracted | DSS-14, DSS-43, DSS-63 | 36 | 0.0004 | 0.0009 | 0.0011 | -0.0001 | 0.10 | PASS |

Not judged, as you asked (polar azimuth): Sun azimuth max 0.030, Earth azimuth max 0.028. There was no frame shift near the pole.

**The one NOTE.** It is a single sample: Apollo 11 with the Sun 83 degrees high. Near the zenith a tiny change of direction is a large change of compass azimuth. The real angle on the sky between the page's Sun and Horizons' Sun at that moment is 0.018 degrees. The other 35 mission samples are within 0.03 degrees. Nothing needs changing.

**Earth elevation.** The page is higher than Horizons in every one of the 108 samples. Per place (mean): Site 01 A/B/C 0.234, 0.234, 0.233; Site 04 A/B/C 0.234, 0.232, 0.235; Apollo 11 0.130; Chandrayaan-3 0.222; IM-2 0.270 (max 0.285). The page's own text says up to 0.26 for the six spots (measured max 0.261) and 0.13, 0.22, 0.28 for the three missions.

**Antennas.** The page's refraction and Horizons' refraction agree within 0.0011 degrees down to 5.4 degrees elevation.

**Moon sub-points (file H01, 78 times).** Page minus Horizons: sub-Earth latitude max 0.037, longitude 0.028; sub-solar latitude max 0.039, longitude 0.030.

**My stand-in was right.** My own DE421 calculation, used in the audit before these tables existed, differs from Horizons by at most 0.0003 degrees in all 216 comparisons. So the full-year numbers from that calculation stand.

## What this changes in the page's answers
- Sun: nothing material. A shift of 0.039 degrees moves a 2028 pass count by 0 to 3 of 366 (measured in the audit).
- Earth: the page shows about a quarter of an hour too much Earth view per day (0.25 to 0.37 h/day over 2028). With the true-site geometry the 2028 pass counts would be 60 / 29 / 76 (Site 01 A/B/C) and 53 / 65 / 60 (Site 04 A/B/C) against the page's 62 / 29 / 77 and 53 / 66 / 61. Link hours in the Comms tab fall by the same amount. The ranking of the spots does not change.
- Comms antenna geometry: no change.
- No page change is needed. index24 already states the 0.23 / 0.26 degree offset.

## Paragraph for the write-up (ready to paste)

"We compared the page with the NASA JPL Horizons system (ephemeris DE441, Moon frame MEAN_ME, lunar radius 1737.4 km, airless) at 12 times in 2028 for each of our six south-pole spots and at 12 times around the landing for Apollo 11, Chandrayaan-3 and IM-2: 108 Sun and 108 Earth directions. Sun elevation agrees within 0.04 degrees everywhere (median 0.02). At the three mission sites Sun azimuth agrees within 0.03 degrees in 35 of 36 samples; the one exception, 0.15 degrees, is the Sun 83 degrees high over Apollo 11, where the real angle on the sky is 0.02 degrees. Earth azimuth agrees within 0.11 degrees. The page's Earth elevation is higher than Horizons in every sample, by 0.23 degrees on average and 0.26 degrees at most at our six spots (up to 0.28 at IM-2), because the page treats the Earth as seen from the Moon's centre. For the Comms tab, the Moon's elevation at the Deep Space Network antennas DSS-14, DSS-43 and DSS-63 (36 samples, refraction on) agrees within 0.002 degrees. In terms of answers, the Earth offset means the page shows about a quarter of an hour too much Earth view per day (0.25 to 0.37 hours), and the 2028 pass counts would be 60, 29, 76 and 53, 65, 60 instead of 62, 29, 77 and 53, 66, 61. Those last figures come from our own calculation with JPL's DE421 ephemeris over every hour of 2028, which matches Horizons within 0.0003 degrees at all 216 test directions."

## Limits of this check
- 12 times per place, not every hour. The every-hour figures come from my DE421 calculation, tied to Horizons at the 216 test directions.
- It checks directions to the Sun, Earth and Moon. It does not check the terrain horizons, which need NASA's 5 m ground.
- Horizons used predicted Earth-orientation data for 2028 and assumes no new leap second.
