# Bangalore land-cover pilot — method

Written before results were computed (see `ideas.md`: method before results).
Any change after seeing results is logged at the bottom with a reason.

## Question
Between 2018–19 and 2025–26, what land did Bangalore's growth corridors convert,
and how fast did their built-up share rise relative to the mature core?

## Regions
Six rectangles in `config.json` — four growth corridors, one growth-vs-forest edge
(Bannerghatta), one mature reference core. Drawn from approximate coordinates, then
**verified on a map by the author (2026-10-30)** as covering the intended localities.
They are still rectangles, not official boundaries: results describe "the area around X",
not X's administrative area. Ward/locality polygons remain a later refinement.

## Data
| Purpose | Dataset | Notes |
|---|---|---|
| Land cover | `GOOGLE/DYNAMICWORLD/V1` (10 m) | Class probabilities per Sentinel-2 scene; only scenes < 35% cloud are included by Google |
| Vegetation | `COPERNICUS/S2_HARMONIZED` (L1C, top-of-atmosphere) | L1C chosen over L2A because L2A coverage over India is incomplete before late 2018; TOA NDVI is consistent across years but not absolute surface reflectance |
| Cloud mask | `GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED` | Keep pixels with `cs_cdf` ≥ 0.6 |

## Seasonal window: Jan–Mar
Chosen from a coverage check (distinct clear-sky Dynamic World dates over a Bangalore box):

| Year | Oct–Dec | Dec–Feb | Jan–Mar | Jan–Apr |
|---|---|---|---|---|
| 2016 | 7 | 5 | 4 | 6 |
| 2017 | 4 | 6 | 5 | 7 |
| 2018 | 13 | 12 | 15 | 20 |
| 2019 | 6 | 15 | 18 | 23 |
| 2020 | 8 | 12 | 15 | 19 |
| 2021 | 4 | 13 | 15 | 19 |
| 2022 | 6 | 18 | 20 | 26 |
| 2023 | 9 | 14 | 15 | 20 |
| 2024 | 6 | 12 | 15 | 20 |
| 2025 | 7 | 14 | 17 | 24 |

Oct–Dec (originally proposed) is unreliable in Bangalore: the north-east monsoon makes
Oct–Nov cloudy. Jan–Mar is consistently clear from 2018 (both Sentinel-2 satellites
operating). Jan–Apr has more dates but April is peak leaf-off/heat; Jan–Mar is the
compromise.

- **2016–2017 are low-observation years** (Sentinel-2B launched March 2017). They are
  computed and shown, flagged, and excluded from transitions.

## Per region, per year
1. **Composite:** mean of Dynamic World class probabilities over all Jan–Mar scenes;
   per-pixel label = class with highest mean probability.
2. **Hard shares:** area of each label / region area (pixel-area weighted).
3. **Soft shares:** mean probability of `built`, `trees`, `crops` over the region —
   a threshold-free robustness check on (2).
4. **Coverage:** number of scenes, and fraction of region pixels with ≥ 1 valid observation.
5. **NDVI:** per-pixel median NDVI over cloud-masked Jan–Mar scenes; report the regional
   median and mean.

## Transitions
- Classes grouped into: **built**, **trees**, **water**, **open land**
  (crops + grass + shrub_and_scrub + bare + flooded_vegetation), **snow** (unused).
  Reason: in the dry season, harvested/fallow farmland is labelled bare/grass, so
  "crops" alone is not stable across years.
- **Persistence rule:** a pixel's start class is counted only if it is the same in both
  2018 and 2019; its end class only if the same in both 2025 and 2026. Pixels failing
  either are reported as "unstable" (share reported, not hidden).
- Output: area (ha) for each from→to pair per region.

## Known caveats (carry into any write-up)
- Dynamic World per-pixel labels are noisy; claims are made at region level only.
- Dry-season composites understate cropland and can read deciduous trees as scrub.
- "Trees" includes parks, avenue trees, plantations, orchards — this is **tree canopy**,
  not forest.
- Rectangles mix land uses at their edges; the Bannerghatta box deliberately spans park
  and urban edge.
- No ground truth yet. Candidate checks: building footprints (Google Open Buildings
  temporal), BBMP/BDA layouts, property registration data.

## Changes after seeing results
- 2026-10-30: Old-core display label shortened for chart legibility (config `label`; the
  parks note moved to `notes`). Cosmetic only — no geometry or parameter changed; pipeline
  re-run so `provenance.json` matches the committed config.
- 2026-10-30: All six rectangles verified on a map by the author; `regions_status` updated.
  No coordinates changed. Pipeline re-run so provenance matches the config.
