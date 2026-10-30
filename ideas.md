# Initial Ideas

Personal, non-commercial research project extending Abhijit Vaidya's
[nighttime-lights-india](https://github.com/abhijitvaidya/nighttime-lights-india).
Possible eventual output: a long-form piece for a serious publication (e.g. Swarajya).
Too early to commit to that — but the work should be good enough that it could.

## Core principles

1. **Measure what you say, say what you measure.** "Nighttime radiance", not "GDP".
   "Tree canopy cover", not "forest". Every number carries its exact definition.
2. **Reproducible or it didn't happen.** Every chart and figure regenerates from code
   plus pinned inputs. No hand-edited outputs, no committed results without the script
   that made them.
3. **Validation stays separate from measurement.** A series used to build an index can
   never be used to validate it.
4. **Changes over levels.** Compare growth within a place over time; be wary of
   comparing absolute levels across places, sensors, or adjacent pixels.
5. **Aggregate before claiming.** Pixel-level classifications are noisy; publish
   area-level shares and trends.
6. **Caveats travel with findings.** Cloud cover, LED retrofits, deciduous seasonality,
   plantations-vs-forest, saturation in bright cores — stated next to the result, not in
   a footnote.
7. **Politically neutral by method.** Several regions (J&K, Ayodhya, forests, mining)
   are contested. Decide the method before looking at the result; report what the
   data shows regardless of which side it favours.
8. **Respect upstream.** Credit the original work; keep our additions separate so bug
   fixes can be offered back cleanly.

## Process

1. **Question first.** Each analysis starts from a specific, answerable question
   ("What did Pune's periphery convert from, 2016–2024?"), not from a dataset.
2. **Pilot small.** 2–3 contrasting regions before scaling to many.
3. **Method before results.** Write down the method (data, window, thresholds,
   comparison) before running it. Changes after seeing results get noted and justified.
4. **Sanity-check against ground truth** where any exists (ISFR forest cover, property
   registrations, building footprints, vehicle registrations, district credit).
5. **Log findings** with claim, evidence, caveats, and confidence — the raw material
   for any eventual article.
6. **Scale only what holds up.**

## Ideas

### Land-cover module (current focus)
One Dynamic World pipeline producing, per region and year (same post-monsoon window):
- **Built-up share** — physical urban expansion / construction
- **Tree share** — canopy cover (+ Hansen Global Forest Change for loss back to 2001)
- **Crop share** + **NDVI** — agricultural extent and condition
- **Transitions** — crop→built, tree→built, tree→crop/bare, with a 2-year persistence rule

Computed server-side in Earth Engine; export tables, not 10 m rasters.

**Pilot regions:** Bangalore growth corridors (Whitefield, Sarjapur Road, Electronic City,
Yelahanka–airport, Bannerghatta edge) vs the old core — see `research/bangalore_pilot/`. Later: one
forest/mining district, optionally Leh (already has NTL results).

### Sub-city nighttime lights
Neighbourhood/corridor scale (≥ ~5 km², 25+ pixels) using real ward/locality
polygons, fractional pixel weighting, fixed lit-pixel mask. Growing periphery vs a
mature core as reference.

### Growth vs footprint
Combine NTL (activity) with land-cover transitions (what land was consumed).

### Before/after studies
Airports, expressways, metro lines, SEZs — treated area vs comparable control.

### Later / maybe
- NO₂ (Sentinel-5P) for industrial clusters
- Sentinel-1 radar for monsoon-proof construction detection
- District-level ground truth: VAHAN vehicle registrations, RBI district credit
- Daily Black Marble for events (Diwali, outages, cyclone recovery)

## Known issues inherited from upstream
- Bias-corrected outputs have no generating script in the repo
- `csaps` missing from `requirements.txt`
- Main pipeline uses raw radiance (no zero-cloud-free-observation recoding)
- Lit-pixel footprint varies month to month (`sum` over `data > 0`)
- Article 370 / COVID periods hardcoded for every region
- GSDP validation: Pearson r on levels, ~10 points, city bbox vs state GDP
