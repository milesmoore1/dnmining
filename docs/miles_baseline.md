# Miles's baseline — his pipeline, his numbers, visualized

This is the "before" document. It records Miles's pipeline exactly as committed at
`4aa37b5`, the numbers it produces when run end to end, and what the baseline
visualization (`web/miles_atlas.html`) shows. It describes his analysis on its own
terms. None of the register changes are applied. Only two non-analytical items are
present: the `.gitignore` data-ignore and the `util/modeling.py` `prepare_train_test`
alias (STEP 0c — the committed notebook does not import without it; it changes no
numbers).

## What his pipeline does

Source: `geodatabase_explorer.ipynb`, run cell for cell via `web/run_miles_pipeline.py`
(which calls only his `util/` modules with his `util/config.py`). Stages:

1. **Load** the NETL REE & Coal Open Geodatabase, layer `REE0009_Trace_Elements_Data`,
   and select his configured columns.
2. **Below-detection substitution** — `util/qualifiers.py`, `substitute="half"`:
   `L` (below detection) → detection limit × 0.5; `N` (not detected) → 0.
3. **Chondrite-normalized lanthanide fill** — `util/ree_interpolation.py`: fills
   missing Pr/Nd/Tb/Dy by interpolating the chondrite-normalized REE series within
   each sample (Y excluded, Ce input-only).
4. **Median-split binary label** — `util/data_preparation.py:add_priority_labels`:
   price-weighted value from Nd/Pr/Tb/Dy (+Y) using the hardcoded prices in
   `config.py`, then `qcut` into two classes (`low` / `high`, i.e. bottom vs top 50%).
5. **Join** the proximate/ultimate layer `REE0008_Proximate_Ultimate_Data` on `Sample_ID`.
6. **Random stratified split** (80/20, `random_state=42`) and **XGBoost** classifier
   (`binary:logistic`, 500 trees, depth 4, lr 0.05).
7. **Diagnostics** — `util/plotting.py`.

Value basis: **whole-coal**, using his **hardcoded** `PRICE_PER_KG`
(Nd 109.55, Pr 109.55, Tb 969.69, Dy 208.68, Y 34.82).

## The numbers it produces

Sample counts through the pipeline:

| Stage | Rows |
|---|---|
| Element layer loaded | 7,658 |
| After substitution + fill + label | 7,658 |
| Labeled (Nd/Pr/Tb/Dy present → a tier) | **5,605** |
| Merged with quality layer | 7,658 × 140 |
| Train / test | 4,484 / 1,121 |

Class balance (median split): low **2,803** · high **2,802** · unlabeled **2,053**.

Model performance on his random holdout:

| Metric | Value |
|---|---|
| Accuracy (test) | **0.855** |
| ROC AUC | **0.934** |
| Confusion matrix | `[[476, 85], [77, 483]]` (rows actual low/high, cols predicted low/high) |
| Precision / recall / F1 | ≈ 0.85–0.86 both classes |

Top features (XGBoost gain), including one-hot categorical dummies as his encoding produces them:

| Feature | Gain |
|---|---|
| V | 0.239 |
| Nb | 0.053 |
| Zr | 0.036 |
| TS | 0.034 |
| Carbon | 0.032 |
| Formation_FORT UNION | 0.027 |
| GSAsh_Dry | 0.024 |
| Sc | 0.022 |
| Thickness__in_ | 0.019 |
| Region_GREEN RIVER | 0.018 |

His diagnostic figures (produced by `util/plotting.py`) are saved to
`web/miles_diag_panel.png` (confusion / P-R-F1 / ROC / PR curves),
`web/miles_diag_proba.png` (predicted-probability distribution by actual class),
and `web/miles_diag_importance.png` (top-15 feature importances).

His stated caveat, verbatim from the notebook:

> "This score measures the existing random holdout, not performance in unseen regions."

## What the visualization shows

`web/miles_atlas.html` (self-contained Leaflet; data from `web/miles_data.json`,
which is `run_miles_pipeline.py`'s serialization of his classifier's output):

- **Map** of his 5,605 labeled, georeferenced samples, colored by **his target**:
  the XGBoost predicted probability of `high` (top-50% REE). One layer, one
  treatment (DL/2) — that is all his pipeline computes. Hexbin at low zoom (median
  P(high) per cell), individual points at high zoom. No interpolated surface.
- **Sidebar** shows his random-holdout metrics (accuracy 85.5%, AUC 0.934,
  confusion matrix, class balance) and his top feature importances.
- **Click panel**: Sample ID, county/state/basin, predicted class and probability,
  whether the sample was in his train or test fold, actual tier, his whole-coal value
  at his hardcoded prices, bed / rank / ash / thickness, his top feature values for
  that sample, and the DL/2-substituted element values.
- **Caption** carries his random-split numbers, labeled as his, with his own
  notebook caveat that this does not measure performance in unseen regions.
- Basemap: keyless Esri World Terrain with OpenStreetMap alternate; coal-province
  outlines from the geodatabase. Basemap and outlines are display only.

Verified in a real browser (`web/miles_verify.py`, Playwright/Chromium): zero
console errors, zero page errors, basemap tiles painted, data features rendered,
sidebar metrics populated, and the click panel populating on selection. Screenshots:
`web/miles_shot_national.png`, `web/miles_shot_points.png`, `web/miles_panel.png`.

## How to reproduce

```
cd ~/DNHacks/teammate-basin-map
.venv/bin/python web/run_miles_pipeline.py     # runs his pipeline, writes web/miles_data.json
cd web && python3 -m http.server               # then open http://localhost:8000/miles_atlas.html
```

## Geoscience analysis panels (display-only sidecar)

> Note: this rationale belongs in CHANGES.md, which is currently parked in the
> git stash ("register changes 1-5 + atlas, parked"). Recorded here for now;
> fold into CHANGES.md when that stash is restored.

A geoscience analysis view was added to `web/miles_atlas_3d.html` (slide-over,
opened from the click panel). **This is a DISPLAY read, not an analytical change.**
It reads the same geodatabase Miles's pipeline already reads, pulling the REE
columns and `_Q` qualifier flags his export happens to drop. His model, features,
target, split, metrics and `miles_data.json` are untouched; the panels are a
display layer over his samples.

- **`web/geochem_sidecar.py` → `web/geochem.json`** (new; does not modify
  `run_miles_pipeline.py` or any `util/` module). Keyed strictly on `Sample_ID`.
  **Join rate: 5,605 / 5,605 of his atlas samples (100%), 0 duplicate IDs, 0
  unmatched.** Exports all 16 REY + Sc with `_Q` flags and ash.
  - **FACE** = value as stored in the source geodatabase (COALQUAL); for an
    L-flagged element that stored value IS the detection limit, not a measurement.
    Read directly — not reconstructed by doubling DL/2.
  - **DL/2** = Miles's substitution, computed via his own `util/qualifiers.py`
    (imported, not modified), so the comparison is faithful to his pipeline.
- **Eu, Er, Tm, Yb, Lu** are present in the source but not in Miles's model
  feature/target set, so they appear in these geochemistry panels and not in his
  predictions. Stated neutrally in the UI — a fact about his export scope.
- Per-element national censoring rates (Pr 83.1%, Gd 70.2%, Dy 87.2%, Ho 93.7%,
  Er 80.9%, Tm 99.3%, …) are printed under each element on the spider axis, so a
  geochemist sees which points are detection limits rather than measurements.

Panels (D3 v7): (1) chondrite-normalized spidergram (McDonough & Sun 1995 CI,
log axis, whole-coal basis) with FACE (dashed) vs DL/2 (solid), open symbols for
censored elements, UCC and world-hard-coal reference lines; (2) geochemical
indices (Eu/Eu*, Ce/Ce*, (La/Yb)N, (La/Sm)N, (Gd/Yb)N, LREE/HREE, ΣREE+Y,
Seredin type, C_outl) under FACE vs DL/2 with censored-derived values flagged;
(3) provenance ternary + bivariate context vs the 5,605-sample population;
(4) population percentile box plots. His model output, tier, value and sidebar
metrics remain alongside.

Reference constants used (not sample data): McDonough & Sun 1995 (chondrite),
Rudnick & Gao 2003 (UCC), Ketris & Yudovich 2009 (world hard coal),
Seredin & Dai 2012 (indices). Verified in-browser (`web/miles_verify_geo.py`):
all four panels render, spider shows the FACE-vs-DL/2 sawtooth at the censored
elements, indices compute for both treatments, zero console errors.

## Mine locations & basin boundaries (display-only sidecar)

> As with the geochem panels, this rationale belongs in CHANGES.md (parked in the
> stash); recorded here meanwhile. Display layers only — his pipeline, model, and
> miles_data.json are untouched.

`web/mines_basins_sidecar.py` writes three display artifacts:

- **`web/mines.json` — MSHA coal mines.** Source: MSHA Mines dataset
  (arlweb.msha.gov OpenGovernmentData, pipe-delimited `Mines.txt`), filtered to
  `COAL_METAL_IND='C'` and valid US coordinates → **23,338 mines**
  (Abandoned 13,575 / Abandoned-and-Sealed 8,537 / Active 581 / other 645;
  Surface 10,953 / Underground 9,619 / Facility 2,766). Fields: name, operator,
  controller, status, type, commodity, employees, county, state, nearest town,
  lat/lon. **Mine identity is MSHA and joined SPATIALLY — never taken from
  COALQUAL's Mine/PowerPlant field.**
  - Rendered as a toggleable deck.gl **`HeatmapLayer` density surface** (not
    markers), weighted by employee count where present (weight 1 otherwise), on a
    **warm amber ramp** deliberately distinct from the viridis sample scale, at low
    opacity so terrain and coal-field outlines read through. **Shown at all zooms** —
    a smooth field is informative, not noisy, so the Appalachian belt, Illinois
    Basin and western fields light up at national zoom as a map of where coal has
    been mined. Strict layer order: terrain → coal-field outlines → **mine density**
    → samples (always on top, brightest). Optional filter: all mines /
    abandoned+sealed / active only (the abandoned surface is the sunk-cost
    landscape). Per-mine hover is dropped (individual mines aren't drawn); identity
    is still available via the nearest-mine list below. (The earlier
    marker/`ScatterplotLayer` version is superseded.)
  - **Nearest-mine context in the click panel:** for a selected sample the nearest
    MSHA coal mines within 25 km (name, operator, status, distance, bearing),
    computed **client-side** (haversine over the loaded layer).
- **`web/basins.geojson` — named analysis-basin extents.** The 24 analysis basins
  live on the sample `Region` field; the geodatabase polygon layers (632 assessed
  basins, 602 coal fields, 6 provinces) **carry no name attribute**, so named
  boundaries are derived as the **convex hull of each Region's samples** (23 hulls
  with ≥3 samples), labelled at the centroid. A **basin selector** flies the
  camera to a basin's extent and shows per-basin stats (n, mean P(high), median
  value) computed from his samples. Stated in the UI as sample-extent hulls, not
  official boundaries.
- **`web/coalfields2.geojson` — geodatabase coal fields (REE0159), 602 polygons,
  simplified, unnamed** — drawn as faint context outlines. These do **not** match
  the 24 analysis Regions one-to-one; the named basin layer above is the
  analysis-aligned set. (USGS OFR 2012-1205 was not needed: the analysis basins
  are the `Region` attribute, not any polygon set, and MRDS was not needed — the
  MSHA layer is rich in abandoned sites: 22k of 23k.)

Verified in-browser (`web/miles_verify_mines.py`): 23,338 mines load; counts per
state reported (KY 9,141 / WV 4,871 / PA 3,328 / VA 2,418 …); mines gated off at
national, on at zoom ≥ 6; hover fires on a marker; nearest-mine list populates;
basin selector flies to Powder River; boundaries + labels draw; zero console errors.

## Visual overhaul — miles_atlas_v2.html (design only)

`web/miles_atlas_v2.html` is a design-only reskin of `miles_atlas_3d.html`
(kept as the working fallback). No data, model, or analytical module changed;
same `miles_data.json` / `geochem.json` / `mines.json` / `basins.geojson`.
Vanilla + deck.gl (no React). Changes: (1) **Esri World Imagery + reference is the
default basemap at every zoom**, darkened via a CSS filter on the MapLibre canvas
(brightness 0.72 / saturate 0.92) with terrain exaggeration on throughout; Gray
terrain kept as an option. (2) **Dark glass UI** — one collapsible controls panel
(gear) + a slim stats panel (essentials; confusion/class-balance behind a "Model
details" disclosure), Inter/system-ui, uppercase letterspaced labels. (3) **Hexagons
glow** — green→gold ramp, high-specular material, opacity 0.9, elevationScale 120k,
staggered rise on load. (4) **Click = full-screen takeover** — geoscience panels
left (spidergram as the hero), his model/geology/nearest-mines right, headline with
animated FACE→DL/2 for Eu/Eu* and Ce/Ce*; Esc / ✕ / click-outside close; ←/→ step
to the nearest neighbouring sample. (5) **Mine density** dimmed to a pale amber
ground glow (~0.3). (6) **Motion** — slow idle rotation at national view (stops on
interaction), eased camera moves. Verified (`web/miles_verify_v2.py`): imagery
default + tiles painting, detail opens/closes, arrow-key nav, all four geoscience
panels render, layer order intact, zero console errors.
