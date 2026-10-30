# CLAUDE.md

## What this project is

A **personal, non-commercial research project** extending Abhijit Vaidya's
nighttime-lights-india (MIT). Findings may eventually become a long-form article for a
serious publication (e.g. Swarajya). Every piece of code is written as if a skeptical
editor, a domain expert, and a politically motivated critic will all scrutinise it.

Read `ideas.md` for principles, process, and the idea backlog.

## Two hats — keep them separate

- **Research (code, data, methods):** rigorous, reproducible, conservative claims.
- **Magazine (narrative):** only built on findings that survived the research process.
  Never tune a method to make a better story.

## Rules for writing code here

### Claims and labels
- Name variables, columns, chart titles, and axis labels by what is actually measured:
  `radiance_sum`, `tree_canopy_share`, `built_share` — never `gdp`, `forest`,
  `development`.
- Every chart states data source, time window, region definition, and units.
- Any reported % change states the baseline and comparison periods explicitly.

### Reproducibility
- Every output (CSV, PNG, figure) must be regenerable by a committed script or notebook.
  Never commit outputs without the code that produced them.
- Pin parameters (thresholds, date windows, seasons, region polygons) in config or at
  the top of the script — no magic numbers buried in functions.
- Record data provenance: dataset ID/version, retrieval date, and source for every
  external input. Official statistics also record their release/vintage.
- Pin dependencies in `requirements.txt` (including ones upstream missed, e.g. `csaps`).

### Method discipline
- Validation data never feeds the thing it validates.
- Prefer growth rates / within-region change over cross-region levels.
- Correlations on trending series: use differences or growth rates, report n, and
  don't present r on ~10 levels as validation.
- Land cover: same-season composites (post-monsoon, Oct–Dec) year to year; require
  2-year persistence before calling a transition; report area-level shares, not pixels.
- Surface data-quality caveats in outputs (cloud-free obs, LED effects, deciduous
  seasonality, plantations counted as tree cover).

### Data and compute
- 10 m data (Dynamic World, Sentinel-2) is aggregated **server-side in Earth Engine**;
  export tables, not rasters. Do not commit large rasters.
- Earth Engine is used under **non-commercial** terms. Flag anything that would change
  that (paid publication terms, monetisation).
- The GEE project ID comes from an environment variable, never hardcoded.

### Upstream respect
- New work lives in new modules/notebooks; avoid restructuring upstream files
  (`ntl_analyze.py`, `nighttime_lights.py`, `correlate_official_data.py`, `notebook.ipynb`).
- Bug fixes to upstream files go in small, separate commits so they can be offered back
  as PRs.
- Credit the original author and xKDR in anything published.

### Findings log
- When an analysis produces a notable result, record it in `findings.md`: claim,
  evidence (script + output), caveats, confidence (low/medium/high). Articles draw only
  from entries marked medium or high.

## Git
- Work happens on feature branches in the user's fork; `upstream` is
  `abhijitvaidya/nighttime-lights-india`.
- Don't push to or open PRs against upstream without the user's explicit go-ahead.
