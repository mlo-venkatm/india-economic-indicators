# Handoff: nighttime-lights-india (land-cover pilot)

## 🕒 Session Summary (2026-10-31)

- **Objective:** Turn Abhijit Vaidya's nighttime-lights repo into a personal, non-commercial research project. Build a land-cover indicator module (built-up, tree, open land, NDVI, transitions) and run a pilot.
- **Status:** ⚠️ In Progress. Bangalore pilot is complete and pushed. Building-footprint cross-check and the tree-loss spot-check are not started.

## 🛠️ Technical Context

### Repo and accounts
- **Working branch:** `land-cover-pilot`, pushed to `origin` = `mlo-venkatm/india-economic-indicators` (the user's fork). `upstream` = `abhijitvaidya/nighttime-lights-india`. Nothing has been pushed upstream.
- **GitHub CLI:** logged in as a collaborator account with write access to the fork. `gh pr create` defaults to upstream, so always pass `--repo mlo-venkatm/india-economic-indicators`.
- **Latest commit:** `d403e93` (map-verified regions). The branch is in sync with origin.

### Earth Engine
- **Project ID:** `indiaeconomicindicators` (the display name is "IndiaEconomicIndicators"). Registered for noncommercial use, Community tier, valid until 2028-04-30. No billing.
- **Use:** `export EE_PROJECT=indiaeconomicindicators` before running `landcover.py`.
- **Auth:** done with `venv/bin/earthengine authenticate --auth_mode=localhost`. The default gcloud mode is blocked by Google.
- **Account:** Earth Engine is authenticated as the project-owner Google account. If `ee.Initialize` fails with a permission error, re-run auth and pick that account.
- **Deleted:** duplicate project `india-econ-indicators`, in `DELETE_REQUESTED` state (30-day recovery).
- **Unrelated project:** an earlier registration attempt landed on an unrelated Cloud project by mistake. Its Earth Engine API has been disabled; the leftover registration may still need withdrawing there (owner's to-do, tracked privately).

### Environment
- Python venv at `venv/` (uv, Python 3.11). Installed: `requirements.txt` (includes `csaps` and `jupyter`), plus `earthengine-api` 1.7.50.
- **Run tools as** `venv/bin/...`, or `source venv/bin/activate` first. `jupyter` is not on the system PATH.

### Modified and added files
- `landcover.py` (new). Summarises Dynamic World and Sentinel-2 inside Earth Engine. Exports tables only. Entry point: `python landcover.py --config research/bangalore_pilot/config.json`.
- `research/bangalore_pilot/config.json`: six regions (growth: Whitefield, Sarjapur Road, Electronic City, Yelahanka–airport, Bannerghatta edge; reference: old core). Window Jan–Mar, 2016–2026. Baseline 2018–19, end 2025–26. `regions_status` says map-verified.
- `research/bangalore_pilot/METHOD.md`: method written before results, with a change log at the bottom.
- `research/bangalore_pilot/pilot.ipynb`: reads the outputs and draws four charts plus commentary. Built by a scratch script (not in repo). Re-execute with `venv/bin/jupyter nbconvert --to notebook --execute --inplace research/bangalore_pilot/pilot.ipynb`.
- `output/landcover/bangalore_pilot/`: `annual_indicators.csv`, `transitions.csv`, `transitions_summary.csv`, `provenance.json`, and PNGs (`built_share_timeseries`, `built_share_2018_2026`, `transitions`, `ndvi`).
- `findings.md` (new): F1 built-up rise (medium confidence), F2 open land to built and trees to built (medium/low), F3 NDVI tracks rainfall (low). Plus a leads section.
- `ideas.md`, `CLAUDE.md`: research principles and project rules. Updated `requirements.txt` (`csaps`, `jupyter`).

### Key decisions (and why)
- **Jan–Mar window, not Oct–Dec.** Bangalore's north-east monsoon makes Oct–Nov mostly cloudy (as few as 4 clear dates). Jan–Mar gives 15–20 clear dates a year from 2018. Coverage table is in `METHOD.md`.
- **2016–17 flagged as low-observation years** (Sentinel-2B launched March 2017). Shown, but excluded from transitions.
- **Transitions use grouped classes** (built, trees, water, open land). Crops are merged with grass, scrub, bare and flooded vegetation, because dry-season composites can't separate harvested farmland from bare ground.
- **Persistence rule:** a pixel counts only if its class is the same in both baseline years and both end years. Unstable share is reported (11–27% in growth areas), not hidden.
- **Sentinel-2 L1C (top-of-atmosphere), not L2A**, for NDVI, because L2A coverage over India is incomplete before late 2018. NDVI is consistent across years but not absolute surface reflectance.
- **Cloud Score+ threshold 0.6** for the NDVI mask.
- **Palette:** the validated categorical palette from the dataviz skill, with the first five slots (passes CVD and normal-vision floors; contrast WARN, so every series has a direct label or table).
- **Commercial-use constraint:** outputs go to Drive or are downloaded directly, not Cloud Storage. Earth Engine is non-commercial only.

### Known issues and caveats (carry into any write-up)
- Dynamic World label shares inflate built-up levels versus mean probabilities by roughly 20–30 pp. Quote **changes**, not levels.
- "Trees" means tree canopy (parks, plantations, orchards), not forest.
- Regions are rectangles, verified on a map by the user. Phrase results as "the area around X", not "X ward".
- The NDVI pattern tracks rainfall. Not usable as a land-use signal until rainfall is controlled for.
- `pilot.ipynb` was executed; re-run after any change to `landcover.py` or the config.
- The "Observations" section of the notebook was written by hand from the charts. If results change, update it.
- Several upstream issues are still open (`ntl_analyze.py`, `nighttime_lights.py`): no script generates `output/bias_corrected/`; the main pipeline uses raw radiance; the lit-pixel footprint varies monthly. Not touched, by design (see `CLAUDE.md` upstream-respect rule).

## 📋 To-Do List (Next Session)

- [ ] **User action:** withdraw the leftover Earth Engine registration on the unrelated project (Manage registration), if the option exists.
- [ ] **Decide and start the building-footprint cross-check** (Google Open Buildings temporal, or similar). It is the main gap for F1 confidence. Write the method in `METHOD.md` *before* running it.
- [ ] **Spot-check trees → built pixels** against high-resolution imagery. This is the most story-worthy and least certain finding (F2).
- [ ] **Open a PR (if wanted)** from `land-cover-pilot` to `mlo-venkatm/india-economic-indicators` `main`. Pass `--repo` explicitly.
- [ ] **Edge cases to test:**
  - Re-run `landcover.py` on a fresh environment to confirm it works from `requirements.txt`.
  - Check the 2016–17 low-observation years are still excluded from transitions.
  - The Sentinel-2 "linkCollection" join for the NDVI mask: confirm the scene count matches the cloud-masked count on at least one year.
- [ ] **Wait for Abhijit's reply** to the outreach email before proposing any upstream changes. Questions asked: site code, raw vs bias-corrected, his roadmap.
- [ ] **Later:** rainfall control for NDVI (e.g. CHIRPS); replace rectangles with ward or locality polygons; decide on the forest/mining pilot.

---

Project state saved to `handoff.md`. You can now safely run `/clear` to reset the context window and save tokens. In the next session, just tell me: "Read handoff.md and continue."

