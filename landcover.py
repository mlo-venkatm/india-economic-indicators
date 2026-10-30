"""
Land-cover indicators from Dynamic World and Sentinel-2, computed server-side in
Google Earth Engine. Only summary tables leave Earth Engine; no rasters are downloaded.

Per region and year (one seasonal window per year):
- Hard class shares: pixel-area share of each Dynamic World label
- Soft shares: mean class probability for built / trees / crops
- Coverage: scene count and fraction of pixels with at least one valid observation
- NDVI: per-pixel median over cloud-masked scenes, summarised by regional median and mean

Per region (two persistent periods):
- Transitions between grouped classes (built, trees, water, open land), in hectares

Method and caveats: research/<pilot>/METHOD.md. Parameters: research/<pilot>/config.json.

Usage:
    export EE_PROJECT=<your-registered-earth-engine-project>
    python landcover.py --config research/bangalore_pilot/config.json
"""

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import ee
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DW_COLLECTION = 'GOOGLE/DYNAMICWORLD/V1'
S2_COLLECTION = 'COPERNICUS/S2_HARMONIZED'
CSP_COLLECTION = 'GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED'

# Dynamic World label indices, in band order
DW_CLASSES = ['water', 'trees', 'grass', 'flooded_vegetation', 'crops',
              'shrub_and_scrub', 'built', 'bare', 'snow_and_ice']

# Grouped classes for transitions. Dry-season composites label harvested or fallow
# farmland as bare/grass, so crops are merged with other open land (see METHOD.md).
GROUPS = {0: 'water', 1: 'trees', 2: 'open_land', 3: 'built', 4: 'snow_and_ice'}
DW_TO_GROUP = {
    'water': 0, 'trees': 1, 'grass': 2, 'flooded_vegetation': 2, 'crops': 2,
    'shrub_and_scrub': 2, 'built': 3, 'bare': 2, 'snow_and_ice': 4,
}

SOFT_SHARE_CLASSES = ['built', 'trees', 'crops']
MAX_PIXELS = 1e10
MAX_WORKERS = 6
RETRIES = 3


def init_ee():
    project = os.environ.get('EE_PROJECT')
    if not project:
        sys.exit('EE_PROJECT is not set. Export your registered Earth Engine project ID.')
    ee.Initialize(project=project)
    return project


def with_retries(fn, *args):
    """Call fn, retrying transient Earth Engine errors with exponential backoff."""
    for attempt in range(1, RETRIES + 1):
        try:
            return fn(*args)
        except ee.EEException as e:
            msg = str(e)
            transient = any(s in msg for s in ('Too many concurrent', 'timed out',
                                                'Internal error', '429', '503'))
            if not transient or attempt == RETRIES:
                raise
            time.sleep(2 ** attempt)


def region_geometry(bbox):
    west, south, east, north = bbox
    if not (west < east and south < north):
        raise ValueError(f'Invalid bbox (expected [west, south, east, north]): {bbox}')
    return ee.Geometry.Rectangle(bbox, proj='EPSG:4326', geodesic=False)


def season_dates(year, months):
    """Return (start, end) ISO dates covering contiguous months of one calendar year."""
    if months != list(range(months[0], months[-1] + 1)):
        raise ValueError(f'Window months must be contiguous within a year: {months}')
    start = f'{year}-{months[0]:02d}-01'
    end_month = months[-1] + 1
    end = f'{year + 1}-01-01' if end_month == 13 else f'{year}-{end_month:02d}-01'
    return start, end


def dw_composite(geom, start, end):
    """Mean class probabilities, argmax label, and per-pixel observation count."""
    dw = ee.ImageCollection(DW_COLLECTION).filterBounds(geom).filterDate(start, end)
    probs = dw.select(DW_CLASSES).mean()
    label = probs.toArray().arrayArgmax().arrayGet(0).rename('label').toInt()
    n_obs = dw.select('label').count().rename('n_obs')
    return dw, probs, label, n_obs


def to_group(label):
    return label.remap(list(range(len(DW_CLASSES))),
                       [DW_TO_GROUP[c] for c in DW_CLASSES]).rename('group')


def landcover_stats(geom, year, months, scale):
    """Hard shares, soft shares and coverage for one region-year."""
    start, end = season_dates(year, months)
    dw, probs, label, n_obs = dw_composite(geom, start, end)

    area_by_label = ee.Image.pixelArea().addBands(label).reduceRegion(
        reducer=ee.Reducer.sum().group(groupField=1, groupName='label'),
        geometry=geom, scale=scale, maxPixels=MAX_PIXELS)
    soft = probs.select(SOFT_SHARE_CLASSES).reduceRegion(
        reducer=ee.Reducer.mean(), geometry=geom, scale=scale, maxPixels=MAX_PIXELS)
    valid_fraction = n_obs.gt(0).unmask(0).reduceRegion(
        reducer=ee.Reducer.mean(), geometry=geom, scale=scale, maxPixels=MAX_PIXELS)

    result = ee.Dictionary({
        'n_scenes': dw.size(),
        'groups': area_by_label.get('groups'),
        'soft': soft,
        'valid_fraction': valid_fraction.get('n_obs'),
    }).getInfo()

    out = {'n_scenes': result['n_scenes'], 'valid_fraction': result['valid_fraction']}
    groups = result['groups'] or []
    observed_m2 = sum(g['sum'] for g in groups)
    for cls in DW_CLASSES:
        out[f'share_{cls}'] = None
    if observed_m2 > 0:
        for cls in DW_CLASSES:
            out[f'share_{cls}'] = 0.0
        for g in groups:
            out[f'share_{DW_CLASSES[int(g["label"])]}'] = g['sum'] / observed_m2
    for cls in SOFT_SHARE_CLASSES:
        out[f'soft_{cls}'] = (result['soft'] or {}).get(cls)
    return out


def ndvi_stats(geom, year, months, scale, cs_threshold):
    """Regional median and mean of the per-pixel median NDVI (cloud-masked, TOA)."""
    start, end = season_dates(year, months)
    s2 = ee.ImageCollection(S2_COLLECTION).filterBounds(geom).filterDate(start, end)
    csp = ee.ImageCollection(CSP_COLLECTION).filterBounds(geom).filterDate(start, end)

    def masked_ndvi(img):
        clear = img.select('cs_cdf').gte(cs_threshold)
        return img.normalizedDifference(['B8', 'B4']).rename('ndvi').updateMask(clear)

    ndvi = s2.linkCollection(csp, ['cs_cdf']).map(masked_ndvi).median()
    stats = ndvi.reduceRegion(
        reducer=ee.Reducer.median().combine(ee.Reducer.mean(), sharedInputs=True),
        geometry=geom, scale=scale, maxPixels=MAX_PIXELS)
    result = ee.Dictionary({'n_scenes': s2.size(), 'stats': stats}).getInfo()
    stats = result['stats'] or {}
    return {'ndvi_n_scenes': result['n_scenes'],
            'ndvi_median': stats.get('ndvi_median'),
            'ndvi_mean': stats.get('ndvi_mean')}


def transitions(geom, baseline_years, end_years, months, scale):
    """Area (ha) of grouped-class transitions between two persistent periods."""
    groups = {}
    for y in list(baseline_years) + list(end_years):
        _, _, label, _ = dw_composite(geom, *season_dates(y, months))
        groups[y] = to_group(label)

    b0, b1 = (groups[y] for y in baseline_years)
    e0, e1 = (groups[y] for y in end_years)
    observed = b0.mask().And(b1.mask()).And(e0.mask()).And(e1.mask())
    stable = b0.eq(b1).And(e0.eq(e1))
    code = b0.multiply(10).add(e0).updateMask(observed).updateMask(stable).rename('code')

    area = ee.Image.pixelArea()
    by_code = area.addBands(code).reduceRegion(
        reducer=ee.Reducer.sum().group(groupField=1, groupName='code'),
        geometry=geom, scale=scale, maxPixels=MAX_PIXELS)
    observed_area = area.updateMask(observed).reduceRegion(
        reducer=ee.Reducer.sum(), geometry=geom, scale=scale, maxPixels=MAX_PIXELS)

    result = ee.Dictionary({'groups': by_code.get('groups'),
                            'observed_m2': observed_area.get('area')}).getInfo()
    rows = []
    stable_m2 = 0.0
    for g in result['groups'] or []:
        code_val = int(g['code'])
        stable_m2 += g['sum']
        rows.append({'from_class': GROUPS[code_val // 10], 'to_class': GROUPS[code_val % 10],
                     'area_ha': g['sum'] / 1e4})
    observed_m2 = result['observed_m2'] or 0.0
    summary = {'observed_ha': observed_m2 / 1e4, 'stable_ha': stable_m2 / 1e4,
               'unstable_share': (1 - stable_m2 / observed_m2) if observed_m2 else None}
    return rows, summary


def run(config_path):
    with open(config_path) as f:
        raw = f.read()
    cfg = json.loads(raw)
    project = init_ee()

    out_dir = os.path.join(BASE_DIR, 'output', 'landcover', cfg['name'])
    os.makedirs(out_dir, exist_ok=True)

    months = cfg['window']['months']
    years = cfg['window']['years']
    low_obs = set(cfg['window'].get('low_observation_years', []))
    scale = cfg['scale_m']
    cs_thr = cfg['cloud_score_plus_threshold']
    regions = cfg['regions']

    def region_year(job):
        rkey, year = job
        geom = region_geometry(regions[rkey]['bbox'])
        lc = with_retries(landcover_stats, geom, year, months, scale)
        nd = with_retries(ndvi_stats, geom, year, months, scale, cs_thr)
        print(f'  {rkey} {year}: {lc["n_scenes"]} DW scenes, built {lc["share_built"]}')
        return rkey, year, {**lc, **nd}

    jobs = [(r, y) for r in regions for y in years]
    print(f'Computing {len(jobs)} region-years on project {project} ...')
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        annual = list(pool.map(region_year, jobs))

    retrieved_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    rows = []
    for rkey, year, stats in annual:
        for indicator, value in stats.items():
            rows.append({
                'region_id': rkey, 'region_label': regions[rkey]['label'],
                'region_role': regions[rkey]['role'], 'year': year,
                'window': cfg['window']['label'], 'indicator': indicator, 'value': value,
                'low_observation_year': year in low_obs,
                'source': S2_COLLECTION if indicator.startswith('ndvi') else DW_COLLECTION,
                'retrieved_at': retrieved_at,
            })
    annual_df = pd.DataFrame(rows).sort_values(['region_id', 'year', 'indicator'])
    annual_df.to_csv(os.path.join(out_dir, 'annual_indicators.csv'), index=False)

    print('Computing transitions ...')
    t_rows, t_summary = [], []
    base_y = cfg['transitions']['baseline_years']
    end_y = cfg['transitions']['end_years']
    for rkey, r in regions.items():
        geom = region_geometry(r['bbox'])
        rows_r, summary = with_retries(transitions, geom, base_y, end_y, months, scale)
        for row in rows_r:
            t_rows.append({'region_id': rkey, 'region_label': r['label'], **row})
        t_summary.append({'region_id': rkey, 'region_label': r['label'],
                          'area_km2': geom.area(maxError=1).getInfo() / 1e6, **summary})
    period = f'{base_y[0]}-{base_y[1]} -> {end_y[0]}-{end_y[1]}'
    t_df = pd.DataFrame(t_rows).assign(period=period)
    t_df.to_csv(os.path.join(out_dir, 'transitions.csv'), index=False)
    pd.DataFrame(t_summary).assign(period=period).to_csv(
        os.path.join(out_dir, 'transitions_summary.csv'), index=False)

    provenance = {
        'config_path': os.path.relpath(config_path, BASE_DIR),
        'config_sha256': hashlib.sha256(raw.encode()).hexdigest(),
        'retrieved_at': retrieved_at,
        'earthengine_api_version': ee.__version__,
        'datasets': [DW_COLLECTION, S2_COLLECTION, CSP_COLLECTION],
    }
    with open(os.path.join(out_dir, 'provenance.json'), 'w') as f:
        json.dump(provenance, f, indent=2)
    print(f'Outputs written to {os.path.relpath(out_dir, BASE_DIR)}')


def main():
    parser = argparse.ArgumentParser(description='Land-cover indicators via Earth Engine')
    parser.add_argument('--config', required=True, help='Path to pilot config JSON')
    run(parser.parse_args().config)


if __name__ == '__main__':
    main()
