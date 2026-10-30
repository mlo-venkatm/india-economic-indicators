# Findings log

Each entry: claim, evidence, caveats, confidence. Articles draw only from **medium** or
**high** confidence entries. Low-confidence entries are leads, not claims.

---

## F1 — Bangalore growth corridors' built-up share rose 11–26 pp (2018 → 2026)
- **Date:** 2026-10-30 · **Pilot:** `research/bangalore_pilot`
- **Claim:** In all five growth rectangles, Dynamic World built-up label share rose between
  Jan–Mar 2018 and Jan–Mar 2026: Sarjapur Road 40→66% (+26 pp), Yelahanka–airport corridor
  38→59% (+21), Whitefield 66→81% (+14), Bannerghatta edge 47→59% (+12), Electronic City
  79→90% (+11). The old-core reference stayed flat at 91%.
- **Evidence:** `output/landcover/bangalore_pilot/annual_indicators.csv`,
  `built_share_2018_2026.png`, `built_share_timeseries.png` (produced by `landcover.py`).
- **Supports it:** both measures (label share and mean probability) rise in every growth
  region; rises are near-monotonic year to year; the reference is flat.
- **Caveats:** provisional rectangles, not official localities; label share inflates levels
  (mean-probability levels are ~20–30 pp lower) — quote *changes*, not levels; no ground
  truth yet.
- **Confidence:** **medium** for direction and ranking; **low** for exact magnitudes.
- **To raise confidence:** official locality polygons; cross-check with Google Open Buildings
  temporal or another built-up product.

## F2 — Growth mostly consumed open land; tree loss to building is smaller but real
- **Date:** 2026-10-30 · **Pilot:** `research/bangalore_pilot`
- **Claim:** Between 2018–19 and 2025–26 (persistent pixels only), open land → built covered
  3.9–10.6% of each growth rectangle; trees → built 1.7–3.8%. Old-core equivalents: 0.2% and 0.3%.
- **Evidence:** `output/landcover/bangalore_pilot/transitions.csv`, `transitions.png`.
- **Caveats:** 11–27% of growth-region area fails the persistence rule, so these are lower
  bounds; "trees" is tree canopy (parks, plantations, orchards), not forest; "open land"
  merges crops/grass/scrub/bare because dry-season composites can't separate fallow farmland.
- **Confidence:** **medium** that open land is the dominant source; **low** for tree-loss
  magnitudes.
- **To raise confidence:** spot-check trees → built pixels against high-resolution imagery.

## F3 — Dry-season NDVI tracks rainfall, not land change (as computed)
- **Date:** 2026-10-30 · **Pilot:** `research/bangalore_pilot`
- **Claim:** Regional median NDVI moves together across all six regions (dips 2019 and 2024,
  peak 2021), including the stable old core.
- **Evidence:** `output/landcover/bangalore_pilot/ndvi.png`, `annual_indicators.csv`.
- **Caveats:** rainfall link is inferred, not tested.
- **Confidence:** **low** (it's a negative/methodological finding).
- **Next:** control for rainfall (e.g. CHIRPS) or use NDVI only within stable vegetated pixels.

## Leads (not claims)
- Small water → built areas (E-City 17 ha, Bannerghatta 11 ha) could be lake encroachment —
  or dry-season lake shrinkage. Near the noise floor; **do not report** without imagery checks.
