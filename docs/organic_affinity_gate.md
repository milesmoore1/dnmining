# Organic-affinity extractability proxy — VALIDATION GATE FAILED, method not used

Method (Gluskoter et al. 1977; Finkelman 1981; intercept statement per Int. J.
Coal Geol. Mukah study 2011): regress element concentration on ash yield within a
group; the **intercept at zero ash = organically associated fraction**; organic
affinity = intercept / mean concentration.

**Step 2 (the gate) was run first and the literature rank pattern does NOT
reproduce on COALQUAL. Per the plan, we stop — Steps 1/3/4 (per-element REY
affinities, censoring interaction, extractability mapping) were NOT computed.**

## What the gate showed
Prior: in **lower-rank** coal, B, Be, Ca, Mo, S, Sr, U associate with the
**organic** fraction; in bituminous coal most sit with mineral matter. COALQUAL
measures Be, Ca, Mo, Sr, U, S (=total sulfur); B is not in the trace file.
Detected-only regressions (censored points excluded — the cleanest case):

**Pooled by rank** — low-rank mean affinity 0.58 vs bituminous 0.55 (no separation).

**By rank×basin (the intended grouping)** — low-rank basins (Fort Union, Powder
River, Green River) vs bituminous basins (Central/Northern/Southern Appalachian):

| element | low-rank aff | bitum aff | verdict |
|---|---|---|---|
| Ca | 0.87 | 0.46 | ✓ as expected |
| Sr | 0.95 | 0.53 | ✓ as expected |
| S  | 1.00 | 1.00 | ≈ (no rank discrimination) |
| Be | 0.16 | 0.76 | ✗ **reversed + negative intercept** |
| Mo | 0.01 | 0.69 | ✗ **reversed + negative intercept** |
| U  | 0.00 | 0.31 | ✗ **reversed + negative intercept** |

**Only 2 of 6 validation elements (Ca, Sr) reproduce the prior. Three (Be, Mo, U)
are reversed AND produce negative intercepts** — the documented failure mode of the
model (Klika & Kolomaznik on negative c0,i) — and these are among the very elements
the prior predicts to be organic in low-rank coal.

## Why it fails (diagnosis)
- **Median R² = 0.069** across 36 rank×basin element groups. The intercept method
  requires a usable concentration–ash linear trend; on COALQUAL whole-coal data there
  essentially isn't one. The classic method works on well-sampled single seams with
  float-sink fractions, not a pooled national composite database with many
  seams/labs/depositional settings per group.
- With slope ≈ 0 the affinity metric degenerates to ≈1 (spurious "organic" for Ca/Sr/S
  regardless of true mode); with slight negative slope it gives negative intercepts
  (Be/Mo/U → clipped to 0, "mineral") — landing opposite to the prior.
- This is **not** a censoring artifact: it fails on detected-only data. (Censoring
  would only make it worse, which is consistent with — but not the cause of — the failure.)

## Decision
- **Method not adopted.** No organic-affinity numbers are assigned to the REY/Sc/basket
  elements; no extractability estimate is derived from it.
- The direct measurement of mode of occurrence is **float-sink density separation**;
  the intercept regression is an indirect proxy that does not hold on this dataset.
- Recovery-factor calibration therefore continues to rest on the documented lignite
  weak-acid anchor (Laudal) and the single S-K 1300 process anchor (Ramaco, n=1,
  a caustic-leach *process* recovery — a different quantity), per
  `docs/recovery_calibration_sk1300.md`. It is not supplemented by this proxy.

---

## Salvage attempt — Step 2 gate re-run grouped by NAMED BED (one attempt, decision rule fixed in advance)

Rationale: rank×basin pools dozens of unrelated seams; the method assumes a
homogeneous population (classically a single well-sampled seam). Bed is the
homogeneity unit. Detected-only, beds with n≥20 for the element (same clean
comparison as the rank×basin run).

**1. R² at bed level (vs rank×basin baseline 0.069):** overall **median bed R² =
0.108** (n=411 element-beds) — a marginal lift, still far below usable. Per element
(qualifying beds, median R²): Be 70 beds/0.097 · Ca 72/0.062 · Mo 63/0.097 ·
Sr 72/0.089 · U 65/**0.260** · S 69/0.108. Only U clears 0.2.

**2. Negative intercepts:** **49/411 = 12%** of element-beds (the low-rank beds for
Be/Mo/U still fail); rank×basin had 3 of 6 elements negative in the low-rank groups.

**3. Rank pattern — still 2/6 reproduce** (low-rank beds vs bituminous beds, median
affinity): Ca 0.96 vs 0.54 ✓ · Sr 0.89 vs 0.62 ✓ · Be 0.18 vs 0.69 ✗ · Mo 0.21 vs
0.61 ✗ · U 0.08 vs 0.33 ✗ · S 1.00 vs 1.00 ≈. (Low-rank named beds are few — nb=5–8 —
since most named beds meeting n≥20 are Appalachian bituminous.)

**4. Degeneracy:** reduced but present — **29/411 = 7%** of element-beds pile at
affinity ≈1.00 with a ~flat slope (|r|<0.15).

**DECISION (pre-committed rule): median bed R² = 0.108 (< 0.2) AND 2/6 (< 4)
validation elements reproduce → the method is DEAD on COALQUAL.** Bed grouping did
improve R² over rank×basin (0.069 → 0.108), so grouping was part of the earlier
problem — but not the whole of it: the ash–concentration linearity remains too weak
and the diagnostic elements (Be, Mo, U) still fail with negative intercepts. Steps 1,
3, 4 were NOT run; **no organic-affinity values computed for the REY, Sc, or basket
elements.** Final: mode of occurrence on COALQUAL needs the direct measurement
(float-sink density separation); this intercept proxy does not hold here at any
grouping tried (rank×basin or named bed).
