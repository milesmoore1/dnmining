# Separation-index beta table — provenance record

**What this is (language discipline — repeat everywhere it is used):**
a **feed-composition index using a physically-grounded ionic-radius selectivity
model under one stated extractant system.** It is **not** a separation-difficulty
measurement, **not** measured stage counts. One adjacent pair is SOURCED with
stated conditions; thirteen are FITTED from ionic radius; the three tetrad pairs
are flagged low confidence; Nd/Sm spans the absent Pm and is a two-element step.

---

## Step 0 — the three anchors are mutually incompatible (verified)

La(57) → Dy(66) is **9 atomic-number steps**.

| assumption | cumulative Dy/La | verdict |
|---|---|---|
| uniform β 1.2 (ORNL PC88A Nd/Pr) | 1.2⁹ = **5.2** | far too low |
| uniform β 1.5 (ORNL adjacent typical) | 1.5⁹ = **38** | not >1000 |
| coal-ash Dy/La > 1000 (Xie 2014) | requires avg β = 1000^(1/9) = **2.15** | different system |

The anchors imply average adjacent β of ≈1.2, ≈1.5, ≈2.15 — a ~1.8× spread in β,
~40× cumulative across the light→heavy span. They are from different extractants,
pH, and aqueous phases. **A single table cannot be assembled from these three
numbers; that is stated as a finding.**

## Step 1 — single-source table search

No freely accessible source gives a complete 15-element adjacent-pair β table for
one system at stated conditions. What was found:

| source | datum | conditions | access |
|---|---|---|---|
| Lyon thesis, U. Idaho (open) | **PC88A Nd/Pr β = 1.5–1.6** (lit "typical 1.5–1.6"; flowsheet avg 1.5–1.6) | 1 M PC88A in Isopar-L, O/A = 1, saponified, equilibrium-pH controlled, ~25 °C | full text |
| Xu et al., *Hydrometallurgy* 2013 (S0892687513003452) | P507 adjacent avg ~2.5; Tm/Er 3.34, Yb/Tm 3.56, Lu/Yb 1.78 | chloride; fine conditions not captured | snippet only (paywall) |
| PC88A chloride, eq-pH 2 | La-anchored (cumulative) Ce/La ~61, Nd/La ~72 | chloride | snippet |
| PNAS 2024, LanD (10.1073/pnas.2410926121) SI Table S10 | DEHPA vs PC88A vs DGA SF comparison | aqueous | **SI paywalled (403)** |
| Xie et al. 2014 via 2025 review (10.1080/19392699.2025.2551654) | **Dy/La > 1000** | coal-ash leachate, organophosphorus | the wide-separation anchor |

**Sourced, conditioned, single-system anchor = PC88A Nd/Pr β ≈ 1.5** (Lyon).
System-level averages differ by system (PC88A ≈ 1.5 vs P507/HDEHP ≈ 2.5), which is
exactly the inconsistency. → extrapolate from ionic radius (Step 2).

## Step 2 — extrapolation method

- **Ionic radii:** Shannon (1976), *Acta Cryst.* A32, 751 — effective ionic radii,
  Ln(III), **coordination number 8**. Y = 1.019 Å.
- **Fit:** log D linear in ionic radius (near-linear; adjacent Δr ≈ 0.014 Å),
  β(pair) = 10^(b·Δr), calibrated to one system.
- **Y placement:** by ionic radius, **between Dy (1.027) and Ho (1.015)** — not by
  atomic number.
- **Pm:** absent (radioactive; not in coal). **Nd→Sm is a two-element step**
  (Δr 0.030), not a true adjacent pair; its β is a 2-step product.
- **Tetrad modulation:** log Kd vs f-count has minima at f³/f⁴ (Nd–Sm), f⁷ (Gd–Tb),
  f¹⁰/f¹¹ (Ho–Er) (Peppard et al. 1969; Nugent 1970). A pure linear fit is
  systematically wrong there, so those pairs are **flagged least-reliable** rather
  than force-modeled.

Two calibrations (b = slope, log₁₀ D per Å):

| calibration | anchor | b | role |
|---|---|---|---|
| **A (primary)** | PC88A Nd/Pr = 1.5 (SOURCED) | 10.4 | industrial workhorse; conservative |
| **B (upper bound)** | coal-ash Dy/La = 1000 | 22.6 | high-selectivity organophosphorus |

## Step 3 — cumulative sanity check (both pass their own benchmark)

| span | β_A | β_B | published |
|---|---|---|---|
| Dy/La | 24 | 1000 | >1000 coal ash → **B by construction** |
| La/Lu | 79 | 13,400 | — |
| adjacent light pairs | 1.4–1.5 | 2.0–2.4 | actinide/lanthanide benchmark **1.3–1.5 → A** |

A reproduces the industrial/actinide benchmark; B reproduces coal-ash wide
separation. They are different systems ~40× apart cumulatively — neither wrong.

## Step 4 — provenance table (calibration A primary; B in parentheses)

series order by ionic radius: La Ce Pr Nd Sm Eu Gd Tb Dy **Y** Ho Er Tm Yb Lu

| pair | β_A (β_B) | SOURCED / FITTED | conditions | confidence |
|---|---|---|---|---|
| Pr/Nd | 1.50 (2.42) | **SOURCED** — Lyon, lit 1.5–1.6 | 1 M PC88A/Isopar-L, O/A 1, saponified, eq-pH, ~25 °C | high |
| La/Ce | 1.50 (2.42) | FITTED (ionic radius, PC88A-anchored) | extrapolated, same system | medium |
| Ce/Pr | 1.50 (2.42) | FITTED | " | medium |
| Nd/Sm | 2.05 (4.75) | FITTED | " + **tetrad + Pm 2-step** | **low** |
| Sm/Eu | 1.36 (1.96) | FITTED | " | medium |
| Eu/Gd | 1.36 (1.96) | FITTED | " | medium |
| Gd/Tb | 1.36 (1.96) | FITTED | " + tetrad (f⁷) | **low** |
| Tb/Dy | 1.36 (1.96) | FITTED | " | medium |
| Dy/Y | 1.21 (1.52) | FITTED | " + Y-by-radius + tetrad | **low** |
| Y/Ho | 1.10 (1.23) | FITTED | " + Y-by-radius + tetrad | **low** |
| Ho/Er | 1.30 (1.77) | FITTED | " + tetrad (f¹⁰/f¹¹) | **low** |
| Er/Tm | 1.27 (1.68) | FITTED | " | medium |
| Tm/Yb | 1.24 (1.60) | FITTED | " | medium |
| Yb/Lu | 1.21 (1.52) | FITTED | " | medium |

**One pair SOURCED, thirteen FITTED** → per the taxonomy this is a
**feed-composition index using a physically-grounded selectivity model**, not a
separation-difficulty measurement.

## Index definition (value-weighted stage sum)

Series ordered by ionic radius; 14 adjacent cuts. Magnet elements = Nd, Pr, Dy, Tb.
For each sample and treatment:

- magnet value per element `V_m = conc_m · price_m`; total `V = Σ V_m`.
- for cut *c* between ordered positions (i, i+1): magnet-value fraction on the
  light side `f_L`, heavy side `f_R = 1 − f_L`; **cut load** `w_c = 2·f_L·f_R`
  (the fraction of magnet value that must be separated across cut *c*; maximal at a
  50/50 split, zero when all magnet value sits on one side).
- **value-normalized difficulty** (the metric that matters — separation capital per
  dollar of product): `D_norm = Σ_c w_c / ln(β_c)`
- **absolute difficulty** (proxy for separation capital): `D_abs = V · D_norm`

`1/ln(β)` preserves the logarithmic Fenske structure (stages ∝ 1/ln β); the
"fraction of value in sub-1.5-β pairs" shortcut is **not** used.

**Censoring flag** per sample: fraction of magnet value (hence of the index)
derived from below-detection (L-flagged) elements.

**Tests, in order:** (Step 5a) redundancy — correlate `D_norm` against (La/Yb)_N,
LREE/HREE, Seredin–Dai C_outl, and total magnet fraction; if |r| > ~0.9 with any,
it is a restatement of an existing ratio and we drop it. (Step 5b) beta sensitivity
+ system choice — basin-ranking stability across 0.8×/1.0×/1.2× **and** A↔B.
Blending analysis only if the index is not redundant.

---

## Step 5 results (n = 5,485 full-suite samples, all treatments, calibration A primary)

**5a — Redundancy (the deciding test): NOT redundant.** D_norm (JOINT, calib A) vs
existing geochem metrics:

| vs | Pearson | Spearman | Pearson(log) |
|---|---|---|---|
| (La/Yb)_N | +0.22 | +0.23 | +0.29 |
| LREE/HREE | +0.28 | +0.33 | +0.37 |
| Seredin C_outl | +0.08 | +0.20 | +0.15 |
| magnet mass fraction | +0.53 | +0.53 | +0.53 |

Strongest tie is magnet fraction (r≈0.53, ~28% shared variance); everything else
<0.4. **~70%+ of its variance is independent** of the ratios geochemists already
compute. **What it adds:** a *separation-spread* axis — how a sample's magnet value
straddles the low-β middle of the series (LREE magnets Nd/Pr vs HREE magnets
Tb/Dy), weighted logarithmically — distinct from "how much magnet" (fraction) or
"light/heavy tilt" ((La/Yb)_N). Kept.

**5b — Stability of the basin ranking (median D_norm, 15 basins n≥20):**

| perturbation | Spearman vs ref |
|---|---|
| uniform β-slope ×0.8 / ×1.0 / ×1.2 | +1.000 (algebraic — see below) |
| A ↔ B system choice (uniform) | +1.000 (algebraic) |
| per-cut independent ±20% jitter, N=500 | median 0.993, 5th pct 0.975, min 0.836 |
| tetrad low-confidence cuts ×0.6 / ×1.7 | 0.850 / 0.979 |
| heavy-side (Gd..Lu) selectivity ×0.5 | 0.986 |

Uniform β scaling (including A↔B) is **provably rank-invariant**: `D_norm = (1/[b·ln10])·Σ w_c/Δr_c`,
so any uniform slope change multiplies every sample's D_norm by the same constant.
The ranking depends only on the **relative β shape**, not the magnitude — so the
huge A-vs-B magnitude uncertainty does not move the ranking at all. Under
*non-uniform* stress the ranking still holds (Spearman ≥0.84, typically ≥0.97);
the only material mover is pushing the flagged tetrad pairs down hard (0.85).

**Per-sample (calibration A), D_norm medians by treatment:** FACE 6.93 · DL2 6.75 ·
MARGINAL 6.44 · JOINT 6.45 (treatment shifts the index ~7% via the heavy magnets).

**Censoring flag — the load-bearing caveat:** median **0.53** of each sample's
magnet value comes from **below-detection** elements, and **58% of samples draw
>50% of their magnet value from censored elements** (Dy is 87% censored and, with
Tb, carries most magnet value). The index is non-redundant and rank-stable to β,
but for a majority of samples it **rests on substituted, not measured, heavy-magnet
values** — treatment choice is the real sensitivity, not β.

**Hardest basins** (highest median D_norm): Northern Alaska, San Juan River, Texas,
Uinta, Wind River. **Easiest:** Cook Inlet-Susitna, Fort Union, Eastern, Central
Appalachian, Northern Appalachian.

**Reproducibility note:** MARGINAL/JOINT require `util/treatments.py`, currently
parked in the git stash; the Step-5 computation imported it from there. To make
this analysis standalone, that module (and `data/prices.csv`) must be restored.

---

## Summary — three statements (use these verbatim wherever the index appears)

1. **What it is.** A *feed-composition separation index* on a physically-grounded
   ionic-radius selectivity model under one stated extractant system (PC88A-anchored,
   calibration A). **Not** a separation-difficulty measurement, **not** stage counts.
   1 sourced β pair (PC88A Nd/Pr 1.5, with conditions), 13 fitted from Shannon CN-8
   radii; the three tetrad pairs are low-confidence; Nd/Sm spans the absent Pm.

2. **What it adds (kept, not redundant).** It correlates ≤0.53 with every metric
   geochemists already compute — magnet fraction r≈0.53, (La/Yb)_N/LREE-HREE/C_outl
   all <0.4 — so ~70%+ of its variance is independent. It captures a *separation-
   spread* axis: value concentrated at one end of the series separates cheaply;
   value straddling the low-β middle (Nd/Pr vs Tb/Dy) is expensive.

3. **How much to trust it.** The basin ranking is *algebraically invariant* to
   uniform β scaling and to the entire A↔B system choice (it depends only on the
   relative β shape); non-uniform per-cut ±20% holds Spearman 0.993 (min 0.836).
   BUT it rests on **substituted below-detection values for most samples** — median
   53% of magnet value is imputed and 58% of samples draw >50% from censored
   elements (Dy 87% censored). Treatment choice, not β, is the real sensitivity.
   Basin ranking is **PROVISIONAL**.

---

## Atlas integration (display only)

`web/sepindex_sidecar.py` → `web/sepindex.json` (5,485 records, 97.9% join to the
atlas samples; the 120 without a full REE suite are **null, never guessed**). The
index is a third colour mode in `web/miles_atlas_v2.html` — **Value | P(top-50%) |
Separation index** — coloured on a distinct ice ramp, **inverted so bright = cheap
feed**, with the imputation caveat and PROVISIONAL status stated in the legend and
below-detection samples (cmf>0.5) ringed at high zoom. The sample detail view puts
a per-cut contribution bar chart (hardest cut highlighted, element-pair labelled)
and the censored-magnet fraction directly beneath the spidergram, with the
explicit connection that spidergram *shape* drives separation difficulty. Basin
selection shows the D_norm distribution (basin vs national box) and the basin list
is ordered by median D_norm, flagged PROVISIONAL. No change to the index math, his
model, or any analytical module. (Requires the restored `util/treatments.py` +
`data/prices.csv`.)
