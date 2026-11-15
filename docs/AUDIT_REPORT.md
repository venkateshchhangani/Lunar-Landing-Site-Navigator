# AUDIT REPORT: Lunar Landing Site Navigator, frozen page index23

Auditor run of 10 to 11 Nov 2026 (UTC). Page audited: `index.html`, 34,995,006 bytes, SHA-256 `fab7a8f99469ed5e29a21786380359a2f430ed00e75d4651571e5727fe005957`. **The page was not edited.**

## Read this first

- **No wrong number was found.** Every number I could recompute matches the page.
- **The JPL Horizons check itself is still not done.** JPL hosts are blocked here. In its place I compared the page with JPL's DE421 ephemeris file read offline. That is JPL data, but it is my own calculation, not Horizons output.
- **The page shows the Earth about 0.23 degrees higher than it really is, at all six spots, all year.** This is the known Moon-centre simplification. It is inside your 0.30 limit, so it is a PASS, but it always errs the same way: it gives slightly too many Earth hours (0.25 to 0.37 h/day) and changes pass counts by 0 to 2.
- **Three real bugs, none in a number:** on windows 820 px wide or narrower the 3D view's control row is covered and cannot be tapped; a latitude above 90 in the "your sky" box stops unopened tabs from drawing; the Power tab silently swaps out-of-range inputs (panel area 0 gives the numbers for 2 m2).

**How this run was done.** The workspace already held scripts and result files from an earlier, interrupted attempt at this same audit, which I do not remember. I set all the old result files aside unread, wrote the thresholds below before running anything, read each old script before reusing it, and ran everything again. Every number in this report comes from this run.

## One-page summary

| Verdict | Count |
|---|---|
| PASS | 24 |
| NOTE | 10 |
| FAIL | 3 |
| NOT TESTED | 9 |

Thresholds were written to `THRESHOLDS.md` before the tests ran. The only results I had seen at that point were the page hash, the kit rebuild hash and one offline page load.

## Results table

| # | Test | How measured | Threshold | Result | Verdict |
|---|---|---|---|---|---|
| 1 | Frozen page size and hash | `stat`, `sha256sum` on the attached file | exact match | 34,995,006 bytes, `fab7a8f9...5957` | PASS |
| 2 | Part 1: Horizons, Sun and Earth from the lunar places | needs your export | Sun 0.10 / 0.30; Earth 0.30 / 0.50 | waiting for tables | NOT TESTED |
| 3 | Part 1: Horizons, Moon from DSS-14, 43, 63 | needs your export | 0.10 | waiting for tables | NOT TESTED |
| 4 | Part 1a: read the Horizons manual | one try each, manual page and API | n/a | both refused (host not on the allow-list); manual not read | NOT TESTED |
| 5 | 2a Sun elevation, page vs JPL DE421 at the true site | my own Python, 30 random 2028 times x 6 spots (180), then every hour of 2028 x 6 spots (52,704) | up to 0.10 | 180 samples: median 0.022, 95th 0.037, max 0.039. Full year: max 0.039 | PASS |
| 6 | 2a Sun azimuth | same | up to 0.10 | median 0.019, 95th 0.030, max 0.034 | PASS |
| 7 | 2a Earth elevation | same | up to 0.30 | median 0.235, 95th 0.254, max 0.261; page is **always higher**, mean +0.233. Stated limit 0.26: reached | PASS |
| 8 | 2a Earth azimuth | same | up to 0.30 | median 0.018, 95th 0.032, max 0.036 | PASS |
| 9 | 2b Horizon rule on the stored arrays | my own rule on 13 points x 9,504 hours x 6 spots, compared with the page's own flags | 0 mismatches | 0 Sun and 0 Earth mismatches in 741,312 point-hours each | PASS |
| 10 | 2b Floor at -1.5 degrees | minimum of all stored horizons | none below -1.5001 | minimum -1.5000 | PASS |
| 11 | 2b Curvature drop and the horizons themselves | would need NASA's 5 m ground | n/a | the 5 m ground is not in the kit; I did not rebuild horizons from the coarser ground in the page | NOT TESTED |
| 12 | 2c Pass counts (2028, 10 days, Sun 80 %, Earth 8 h) | my own code on the page's stated model, hour by hour | exactly 62/29/77 and 53/66/61 | Site 01 A/B/C 62/29/77; Site 04 A/B/C 53/66/61 | PASS |
| 13 | 2c and 1g Same counts with JPL DE421 and the true site (parallax in) | my own ephemeris, same horizons and rule | information | Site 01 60/29/76; Site 04 53/65/60. Earth hours over 2028 fall by 0.25 to 0.37 h/day | NOTE |
| 14 | 2d Calendar vs the Final answer rule | 500 random cells, then all 39,468 cells of six settings on both sites | 0 mismatches | 4 of 500. All at Earth limit 0 with 0 Earth hours: page says "fails", the rule gives "marginal". One exact tie in 2029 (Site 01 B, day 97, Sun exactly 80 %) reads 79.99999996 % and shows "marginal" not "passes". Default 2028 counts unaffected | NOTE |
| 15 | 2e Power, 20 random cases | my own version with a numerically integrated Sun disc | 0.5 % energy, 1 % battery | 20 random plus 7 fixed cases, 216 row comparisons: energy within 0.00004 %, battery within 0.09 Wh, 0 flag mismatches | PASS |
| 16 | 2e Power edge cases, inside the function | hand values | reproduced, no NaN | Sun on the horizon 0.5, below 0, facing away 0, load 0 gives battery 0, area 0 gives 30,000 Wh = 100 W x 240 h / 0.8 | PASS |
| 17 | 2f Comms, 12 cases (1, 2, 3 complexes; 6 and 20 degrees) | my own gating and gap count | link within 0.01 h/day, gap identical | all 12 identical to 3 decimals; gaps identical | PASS |
| 18 | 2f DSN Moon elevation, page (refraction removed) vs DE421 with skyfield's Earth rotation | 300 times x 3 antennas | up to 0.10 | median 0.0007, 95th 0.0013, max 0.0018. The page then adds refraction: 0.11 to 0.19 near 6 degrees | PASS |
| 19 | 2g Countdown | 20 random times x Sun and Earth vs a 1-minute scan | within 2 minutes | 40 comparisons, max 52 s, 0 wrong states, 0 short spells missed in this sample | PASS |
| 20 | 2h Real missions | my own DE421 values vs the page's "ours" | 0.10 deg, 0.1 h, 0.1 day; verdicts unchanged | all within limits; 7 of 7 Match and 5 Consistent reproduced | PASS |
| 21 | 3a Every number on every tab, both sites | text of 16 tab dumps with the clock frozen, against stored data and my runs | all traced | all recomputable numbers agree. Five items to know, listed below | NOTE |
| 22 | 3a Check 1 to 4 figures (correlations, clone spreads, photo percentages) | would need NASA maps, clones and photo crops | n/a | inputs not in the kit; compared with the notes only | NOT TESTED |
| 23 | 3b Trust labels of the six spots | badges on Overview, Final answer, Calendar | all Medium | Overview 3, Final answer 6, Calendar 8 badges per site, all Medium | PASS |
| 24 | 3b Other labels | same dump | n/a | Landing planner, Site 01, on 11 Nov 2026: its own "Spot 2" reads **Sunlight check: High**. It is a planner cell, not one of the six spots | NOTE |
| 25 | 3c Sources box vs THIRD_PARTY_NOTICES.md | line by line | all present | all 10 items present. Gaps listed below | NOTE |
| 26 | 3d "not checked / not validated / geometry only" | each claim against what I measured | still true | all still true | PASS |
| 27 | 3e Over-claiming words | search of all tab text | none | no "accurate", "better than", "real mission power" or "link budget" claim. Two sentences can mislead, listed below | NOTE |
| 28 | 4a Errors and offline | network blocked, every tab, both sites | 0 errors, 0 requests | 0 page errors, 0 console errors, 0 requests by the page. Only software-GL warnings | PASS |
| 29 | 4b Controls | both site switches, deep link, bad deep link, date box with OK, plus and minus 1 d and 1 h, Now, Next good view, Run time, Earth spin, time-lapse, Calendar buttons | each works | all work; Next good view lands with Sun and Earth up; Calendar opens Power, Comms and 3D with the right spot, date and stay | PASS |
| 30 | 4b Run time speed | clock movement in 1.5 s | information | slower than labelled here (1 day per second moved 0.3 to 0.4 day in 1.5 s). Software GL; check on Windows | NOTE |
| 31 | 4c "Your latitude" box, value above 90 or below -90 | typed 95 and -95 | no error | uncaught error on every click; tabs not yet opened stay blank until the latitude is corrected | **FAIL** |
| 32 | 4c Power inputs out of range | typed into the boxes | numbers belong to the boxes | area 0 shows the numbers for 2 m2; efficiency 0 uses 0.28, 0.9 uses 0.5; usable 0 uses 0.8; facing -90 uses 0; area 1000 uses 100. The box keeps the typed value and nothing says so | **FAIL** |
| 33 | 4c Other replaced inputs | same | value used is shown | load 0 becomes 100 W, battery -50 becomes 2,000 Wh, stay 0 becomes 10, stay 500 becomes 60, DSN mask 90 becomes 40 ("Minimum elevation used: 40 degrees"). Empty Sun or Earth box counts as 0 | NOTE |
| 34 | 4c Crash, NaN, Infinity | 91 edge inputs: dates 0001 to 2100, years 1900 to 3000, stays 1 and 60, Sun 0 and 100, battery 0, mask 0 and 90, empty, negative, text | none | no NaN, Infinity, undefined or null in any text | PASS |
| 35 | 4d Page width | 9 widths x 8 tabs | equals the window, except 701 to 820 | fits at 360, 390, 600, 700, 1024, 1280, 1920. At 701 the page is 820 or 821 wide; at 820 three tabs are 821 (documented) | PASS |
| 36 | 4d Covered controls | tap test of each 3D-view control | reachable | at 360 to 820 px the Stand at box, Face Sun, Face Earth, Face north, Next good view and Earth spin are covered by the Moon panel. Fine at 860 and wider. Same in index22 | **FAIL** |
| 37 | 4e Memory and speed | forced garbage collection; timers in the page | 50 MB; 5 s; 2 s | JS heap 5.2 MB after load; Calendar 2 years 0.5 to 0.6 s; Final answer 0.2 s; Power up to 0.11 s and Comms up to 0.07 s for 60 days; load about 6 s | PASS |
| 38 | 4f Real GPU, Windows | not possible here | n/a | all tests used software GL on Linux | NOT TESTED |
| 39 | 5 Clean rebuild | unzip in an empty folder, `npm ci`, `python3 build23.py` | same size and hash | 34,995,006 bytes, `fab7a8f9...5957` | PASS |
| 40 | 5 LICENSE, notices, pins | read the files | present and pinned | MIT, "Copyright (c) 2026 Venkatesh Chhangani"; THIRD_PARTY_NOTICES.md present; 7 Python packages pinned with `==`; astronomy-engine 2.1.19 pinned by package-lock.json | PASS |
| 41 | 5 Kit file count | `unzip -l` | matches notes | 238 files, 54,671,963 bytes. Notes say 243 in one place and 246 in another | NOTE |
| 42 | 6 Notes consistency | search and reading | no contradiction | fix list below | NOTE |
| 43 | 7 JPL DSN handbook reuse terms | WebFetch | n/a | not read (host refused) | NOT TESTED |
| 44 | 7 Blue Marble credit line | WebFetch | n/a | not read (host refused) | NOT TESTED |
| 45 | 7 NASA PGDA terms | WebFetch | n/a | not read (host refused) | NOT TESTED |
| 46 | 7 astronomy-engine licence | npm package and the header inside the page | MIT | package.json says MIT; the page carries "MIT License, Copyright (c) 2019-2023 Don Cross" with the permission text. The GitHub page was not reachable | PASS |

## Part 1: what the Earth difference means (1g)

I shifted the page's own Sun and Earth heights in a copy of the calculation and recounted. The delivered page was not touched.

| Spot | Page | Earth lowered 0.233 | Earth lowered 0.261 | Sun raised 0.039 | Sun lowered 0.039 | Earth h/day over 2028, page then lowered |
|---|---|---|---|---|---|---|
| Site 01 A | 62 | 61 | 61 | 64 | 60 | 11.65 then 11.39 |
| Site 01 B | 29 | 29 | 29 | 29 | 29 | 4.81 then 4.43 |
| Site 01 C | 77 | 76 | 76 | 77 | 77 | 14.19 then 13.95 |
| Site 04 A | 53 | 53 | 53 | 56 | 53 | 11.56 then 11.25 |
| Site 04 B | 66 | 65 | 65 | 67 | 66 | 14.44 then 14.18 |
| Site 04 C | 61 | 60 | 60 | 62 | 60 | 14.51 then 14.25 |

- Pass counts move by 0 to 3 of 366. The ranking of the spots does not change.
- Link hours in the Comms tab equal Earth hours when all three complexes are ticked at 6 degrees, so they fall by the same 0.25 to 0.4 h/day.
- The longest no-Earth spell at the worst circle point grows by about 7 hours where it is finite.
- At the three real landings the page reads the Earth 0.14, 0.22 and 0.27 degrees too high. The page says 0.13, 0.22, 0.28. The Sun is within 0.016 degrees.

## Part 3: items to know

**Numbers (row 21)**
1. Final answer, "How we get the confidence label": the GAP column is the larger of the Sun gap and the Earth gap. Site 04 C reads "41 %, NASA 43 %, gap 6 pts" (the 6 is the Earth gap, 61 vs 56). It looks like an arithmetic slip to a reader. Not wrong.
2. Final answer file table says Haworth is "Not part of NASA's 5 m set". Your notes list Haworth among NASA's 27 sites. I could not open the NASA page to see which is right.
3. Overview Check 3, Site 01, prints "92 % right at the shadow edges (60 m: 89 %)". Your notes say never to quote "92 % vs 89 %". Site 04 prints 60 m at "95.0 %"; the notes table has 95.1.
4. Overview says "2.0 days after New Moon" at 12:00 UTC on 11 Nov 2026. New Moon was 9 Nov 07:03 UTC, so 2.2 days.
5. Checked and equal: all spot values, 5/25/60 m values, NASA values, labels by the stated rule, 1,098 and 4,386 combination counts, 668 passing cells (348 in 2028 plus 320 in 2029), Moon distance 403,280 km, Earth to Sun 148.1 million km, lit 5 %, First quarter 17 Nov.

**Sources (row 25)**
- The page does not give the astronomy-engine version (2.1.19).
- NASA's 100 clones and the Site 04 error map appear in the checks text but not in the Sources box.
- The kit's photo checks use mosaics CM_125 and CM_335 as well. Neither the page nor THIRD_PARTY_NOTICES.md lists them. The page itself shows only CM_005 results.
- "The team's code and text are to be released under an open-source licence" is older wording; the first line already says MIT.

**Wording (row 27)**
- "The Sun and Earth positions are real (astronomy-engine, about 1 arcminute)" (3D view and Overview). One arcminute is the library. The page's Earth height is off by up to 0.26 degrees (16 arcminutes) and its Sun by up to 0.04 degrees.
- Check 1b: "Earth may be visible more often than we say." The floor is cautious, but the Moon-centre simplification works the other way.

## Ranked list: real errors to decide on before the freeze

None of these changes a number. Each needs a rebuild and a new hash, so each is your decision. I have changed nothing.

1. **Controls covered at 820 px and narrower (row 36).** Evidence: tap test at 360, 390, 600, 700, 701, 760, 820 px shows the Stand at box and five buttons covered; 860 px and wider are fine; index22 behaves the same. Cause: in the stacked layout the first grid row is squeezed to 302 px while its content is 533 to 622 px, so the side panel sits on top. Proposed fix: in the existing `@media (max-width:820px)` block add `.view{grid-auto-rows:max-content}`. Tested only on an in-memory copy, 3D tab, 390 and 820 px: all controls reachable, page width unchanged. Other tabs not retested with it.
2. **Latitude box (row 31).** Evidence: typing 95 gives "Latitude 95 is out of range. Must be -90..+90." on every click; Calendar and Power opened afterwards show 480 and 370 characters instead of about 2,800 and 4,400. Typing a valid latitude restores everything. Cause: `setView` and `refresh` call `hud()` before `viewStart()`, and the sky box passes the raw latitude to the library. Proposed fix: clamp the latitude to -90..90 where the sky box reads it.
3. **Power inputs (row 32).** Evidence: area 0 leaves "129 Wh/day flat, 18,539 tracking", identical to 2 m2. Cause: `pwParams` replaces a value below the minimum with the default and one above the maximum with the maximum, without writing it back. Proposed fix: write the value used back into each box. The Comms tab already prints the value it used.

If you do not rebuild: demo the 3D view on a window wider than 860 px, do not type in the latitude box, and keep Power inputs inside their ranges (area 0.1 to 100, efficiency 0.05 to 0.5, facing 0 to 360, usable 0.1 to 1).

## Part 6: exact line fixes for the notes (not applied)

HANDOFF_FULL.md
- Line 1: "(sessions 1 to 11)" should read "(sessions 1 to 13, final page index23)".
- Line 4: delete "(8 days left)".
- Line 23 (A3): add at the start "[SUPERSEDED: the chain now ends app29, build23, index23]". It still says build14 makes `index.html`.
- Line 29: "53 MB, 243 files" and line 287 "246 files": measured 238 files, 54.7 MB.
- Line 72: the [superseded] tag sits on the Labels item. Only its last sentence (header overflow, 679 px) is superseded.
- Line 95: "Header tabs: 3D view, Landing planner, Overview, Final answer, Real missions" lists five. The page has eight.
- Line 106: "(the old header overflow of the whole page remains)": fixed up to 700 px in index23.
- Line 161: "our Earth corr 0.983, Sun 0.948 at Site 01": the page says 0.98 and 0.93. Mark as old.
- Line 223: "no watts, panel angle, battery": the Power tab now exists.
- Line 232: tagged superseded, but its first half (Earth parallax not applied) is still true.
- Lines 266 and 277: both addenda start "Final page chain" for index18 and index20. Write "[Intermediate chain, superseded]", as the alignment file does.
- Line 283: tagged superseded, but the Site 04 A worst-point explanation in it is still current.
- Line 117: "up to 0.26 deg in general": I measured up to 0.261 at the six spots and 0.27 at IM-2. Write "up to about 0.28".

CHALLENGE_FULL_AND_COVERAGE.md
- Line 76: the label is said to rest on "checks against real LROC photographs". The page says the photo check does not change the label. Replace with "and agreement between 5, 25 and 60 m ground; LROC photos are a separate check".
- Line 117: broken sentence "fits at 390 px but the fixed for phones". Write "Phone width fixed up to 700 px in index23; at 701 to 820 px the page is still 821 px wide."
- Section 6 and the 3-minute pitch say six photo checks. The page shows one photo per site. Say "six in our notes, one per site on the page".

CHALLENGE_ALIGNMENT_AND_NEXT_STEPS.md
- Line 13: heading names old hashes 06d8d8e1 and 930de841. Final is fab7a8f9.
- Line 113: says not to use "92% vs 89%", yet the page prints it for Site 01 shadow edges. Say which use is meant.

KIT_NOTE_LABEL_OVERRIDE.md
- Lines 18 to 22: "current chain" and "index20 (current ...)" should be marked superseded.

All four: add the three bugs above and the "Earth about 0.23 degrees too high" finding to the honest limits. Pass counts (62/29/77, 53/66/61), Check 1 correlations (0.93/0.98, 0.97/0.97), the final hash and the 701 to 820 px limit are consistent wherever they are marked current.

Word Knowledge Guide: I only searched its text for key numbers (index23, 62/29/77, 0.93/0.98/0.97, eight tabs: present). It was not read in full. It does not mention the 701 to 820 px limit.

## Part 7: credits

| Source | Read? | What I can say |
|---|---|---|
| JPL DSN handbook 810-005 terms | not read | the page says "JPL publishes the handbook for public use". I could not confirm that sentence. If you cannot confirm it either, safer wording: "Source: NASA JPL, DSN Telecommunications Link Design Handbook 810-005, Module 301. Only published numbers are used. No endorsement is implied." |
| NASA Earth Observatory Blue Marble credit | not read | the page credits "NASA Earth Observatory (Reto Stockli)". Exact wording unverified |
| NASA PGDA terms for LOLA data | not read | the page credits NASA LOLA, LRO, PGDA, Mazarico, Barker and colleagues |
| astronomy-engine | read locally | MIT, "Copyright (c) 2019-2023 Don Cross"; header is inside the page |

## Honest limits to say aloud in the pitch

1. "Our Sun and Earth directions were compared with JPL's DE421 ephemeris: the Sun agrees within 0.04 degrees. Our Earth is drawn about 0.23 degrees too high, up to 0.26, because we treat it as seen from the Moon's centre. That adds about a quarter of an hour of Earth view per day and moves a pass count by 0 to 2 out of 366." Add the Horizons result when you have it.
2. Two candidate areas of NASA's 27; no custom coordinates.
3. Power and Comms are geometry only. Power is not checked against any mission's power data. Comms does not say an antenna is free or what data rate is possible.
4. Horizon floor of -1.5 degrees; horizons in 24 directions; the countdown can miss spells under 30 minutes.
5. The trust label is Medium for all six spots. The Landing planner can show High for one of its own cells.
6. Real missions use a flat horizon; two of three sources are secondary.
7. Thermal conditions are not modelled. No ground truth exists on the Moon.
8. Tested with software graphics on Linux only. On windows narrower than 860 px the 3D view's buttons are covered.

## Horizons paragraph for the write-up

**Use now (before the Horizons tables):**

"We compared the page's Sun and Earth directions with an independent calculation from NASA JPL's DE421 ephemeris, including the Moon's physical libration and the true position of each site. Over every hour of 2028 at all six spots (52,704 comparisons) the Sun's elevation agrees within 0.04 degrees and its azimuth within 0.03 degrees. The Earth's azimuth agrees within 0.04 degrees. The Earth's elevation on the page is higher than the JPL-based value by 0.23 degrees on average and 0.26 degrees at most, because the page treats the Earth as seen from the Moon's centre. With the JPL-based geometry the 2028 pass counts become 60, 29, 76 (Site 01) and 53, 65, 60 (Site 04) against the page's 62, 29, 77 and 53, 66, 61, and Earth-in-view time is 0.25 to 0.37 hours per day lower. The Moon's elevation at the three Deep Space Network antennas agrees within 0.002 degrees before refraction. This is our own calculation from a JPL ephemeris file. It is not output of the JPL Horizons system, which we had not yet queried."

**Use after the tables arrive (fill the brackets from my comparison run):**

"We compared the page with the JPL Horizons system at [N] times for [9] lunar places and [36] antenna times. Sun elevation: median [..], 95th percentile [..], maximum [..] degrees. Sun azimuth: [..]. Earth elevation: [..], the page being higher because it treats the Earth as seen from the Moon's centre. Earth azimuth: [..]. Moon elevation at DSS-14, DSS-43 and DSS-63: [..]. In terms of answers this changes pass counts by [..] of 366 and Earth-in-view time by [..] hours per day."

## Things only you can do

1. The Windows test on the exact file: `certutil -hashfile index.html SHA256`, then every tab on both sites and the 3D view. Also try a narrow window, and time "1 day per second".
2. The Horizons export: `powershell -ExecutionPolicy Bypass -File get_horizons.ps1` (see HORIZONS_STEPS.md), then attach `horizons_out.zip`.
3. Reading the Space Apps submission form.
4. Opening the three credit pages I could not read (DSN handbook, Blue Marble, PGDA) and the PGDA site list (Haworth).

## Files

Scripts are in `audit_evidence.zip` under `scripts/`, raw outputs under `out/`, 65 screenshots under `shots/`.
