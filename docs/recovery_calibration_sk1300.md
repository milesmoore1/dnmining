# Recovery-factor calibration from S-K 1300 filings (EDGAR)

**Purpose:** calibrate/validate the rank-conditioned recovery factors in
`util/recovery.py` against legally-required metallurgical-recovery disclosure
(17 CFR 229.1300, TRS Section 10). **This is a VALIDATION set, not training —
n is single digits for coal.** Recoveries are deposit-level composites, not
per-sample; they are **not** joined to COALQUAL samples.

## Method
EDGAR full-text search (`efts.sec.gov/LATEST/search-index`) + Archives fetch,
User-Agent set per SEC policy. "Technical Report Summary" + "rare earth" → 729
filings; screened for coal-hosted host material.

## n by host material (honest count)
| host material | count | which |
|---|---|---|
| **coal / coal-associated (S-K 1300 TRS, Section 10 met table)** | **1** | Ramaco Brook Mine |
| coal refuse (no full TRS met table — 10-Q/8-K only) | (1, not counted) | American Resources Corp (AREC) |
| hard-rock / carbonatite / rhyolite / clay (context, **not** coal) | many | MP Materials, Texas Mineral Resources (Round Top), Rare Earths Americas, Critical Metals, American Lithium, Enertopia, … |

**The coal validation set is n = 1 (Ramaco Brook Mine).** Any calibration claim
for coal rests on that single deposit and must say so. American Resources
processes coal refuse but its EDGAR filings are 10-Q/8-K, not an S-K 1300 TRS
with a Section 10 recovery table, so it is not a validation point here.

## Extraction, per filing
### Ramaco Resources — Brook Mine, Sheridan Co., Wyoming  (CIK 1687187; accession 0001213900-25-088773, EX-96.1, 2025)
- **Host:** critical-mineral oxides (CMOs = TREO + Sc, Ga, Ge) in **subbituminous
  (Powder River Basin) coal and associated claystone/partings.**
- **Head grade:** average **498 ppm CMO, ash-basis** (95.4% of the deposit
  exceeds 300 ppm, ash-basis); Ga+Ge average 48 ppm, Sc average 40 ppm; Th 19 /
  U 8 ppm. **Basis explicitly ash** ("all … CMO grades are on an ash-basis").
- **Recovery:** multi-stage leach bench tests **"yielded recoveries of REEs into
  the low 90s"** (%); per the Fluor PEA a **caustic (alkaline) leach** produced
  the highest extraction efficiencies, "all REEs exceeding [~90%]".
- **Process route:** caustic/alkaline multi-stage leach + flotation; conceptual
  Fluor flowsheet + mass balance.
- **Measured on:** laboratory **bench** testing (leach + flotation) with
  full-scale figures **projected** in the PEA — conceptual, not demonstrated at
  pilot/commercial scale.

### MP Materials — Mountain Pass, California  (CIK 1801368; accession 0001801368-26-000008, EX-96.1)
- **Host:** hard-rock **bastnaesite carbonatite** (not coal, not ash basis).
- **Head grade:** mineralized material ~**2.15% TREO (whole-rock)**; rougher
  concentrate 43.64% TREO, cleaner concentrate 60% TREO.
- **Recovery:** flotation beneficiation; ore-sorter at **90% REO recovery**;
  products to 99.5%+ PrNd oxide. Whole-rock, flotation — a different quantity
  from coal-ash leaching.

### Texas Mineral Resources — Round Top, Texas  (CIK 1445942; accession 0001580695-19-000478, EX-99.1, 2019)
- **Host:** **rhyolite** hard-rock (not coal). Process: dilute **sulfuric acid
  heap leach**. The fetched exhibit is a PEA summary; the recovery % is in the
  full technical report, not this exhibit — **not asserting a number** we did not
  source.

## Calibration verdict per factor
Current factors (parked `util/recovery.py`): LIGNITE 0.85 (documented), SUBBIT
0.55, BITUMINOUS 0.25, ANTHRACITE 0.15 (interpolated).

| factor | S-K 1300 evidence | verdict |
|---|---|---|
| **Lignite 0.85** (documented, Laudal weak-acid) | No coal TRS is lignite (Ramaco is subbituminous). | **Neither confirmed nor contradicted directly.** Unchanged. Indirectly consistent: low-rank coal-hosted REE is highly recoverable with a designed leach. |
| **Subbituminous 0.55** (interpolated guess) | **Ramaco Brook Mine (subbituminous): low-90s% process recovery** (bench + PEA-projected, caustic leach). | **A real anchor now exists (n=1).** It suggests 0.55 **understates achievable *process* recovery** for a designed flowsheet — but see the caveat below; **do not overwrite 0.55 with ~0.90.** Flagged for refinement. |
| **Bituminous 0.25** (interpolated) | No coal-hosted bituminous TRS found. | **No anchor.** Unchanged; still a guess. |
| **Anthracite 0.15** (interpolated) | No anchor. | **No anchor.** Unchanged; still a guess. |

## What the recovery figures actually mean (do not mix quantities)
TRS recoveries are **engineered process recoveries** for a **designed flowsheet**
on a **specific feed**, at **bench or PEA-projected** scale. Ramaco's low-90s is a
**caustic (alkaline) leach** result. That is **not the same quantity** as
**weak-acid extractability** from the geochemical literature (which is what the
lignite 0.85 = Laudal weak-acid anchor represents). Different reagent, different
scale, different question. **They must not be merged into one number without
saying so.** For that reason the numeric factors are **left unchanged**: n=1 for
coal, and the one anchor measures a different quantity than the factors it would
"correct."

## Decision
- Factors **unchanged** (n=1 coal; process-recovery vs extractability mismatch).
- This document records the SEC-sourced anchor with accession numbers.
- **Subbituminous is flagged:** if the model is ever reframed as *process* recovery
  (designed caustic-leach flowsheet) rather than *weak-acid extractability*, the
  Ramaco Brook Mine anchor (low-90s%, accession 0001213900-25-088773) supports a
  substantially higher subbituminous factor — but that is a different metric and
  would need to be relabelled as such.
- When the parked `util/recovery.py` is restored, add a comment on the
  SUBBITUMINOUS line citing this file + accession 0001213900-25-088773.

---

## Full-table read of the Ramaco Brook Mine TRS (accession 0001213900-25-088773, EX-96.1)

**Format caveat (what's machine-readable vs not):** the EX-96.1 HTML has **no
`<TABLE>` markup** — narrative is flowed `<P>` text and **every table/figure is a
page IMAGE** (110 `ex96-1_NNN.jpg`). Numbers below were read directly from those
page images; nothing is inferred.

### 1. Section 10 recoveries — SUMMARIZED, not per-composite (asks 1 & 2 not disclosed)
Section 10 (p58, img 065) prints only aggregate figures:
- Metallurgical testing by **Hazen**, directed by **Fluor**; **laboratory bench**
  leach-extraction + flotation, Metso HSC circuit simulation; since May 2023.
- **"Multi-stage leaching test results have yielded recoveries of REEs into the low 90s"** (%).
- **"overall critical mineral recovery of the REEs and including scandium, gallium
  and germanium averages 84 percent."**
- **No composite count, no per-composite head-grade↔recovery pairs, and no
  per-element recovery breakdown are printed.** So there is **no paired
  feed→recovery dataset** and **no Nd/Pr/Dy/Tb-vs-La/Ce recovery split** in the TRS —
  the series-dependence question cannot be answered from this filing. (The
  Hazen composite-level testwork is not reproduced in the TRS.)
- ROM thermal coal is sold as-is; met testing applies only to the CMOs.

### 3. Assay / drill data (ask 3) — large, but in Appendix A images
- ICP-MS analytical program cited at **~6,000 samples** (5,964 Th / 5,986 U samples);
  2023 **100-hole** program + 5 infill holes. **Appendix A "Drill Hole Database"**
  is filed (page images ~110+). Per-element assays + coordinates exist there but are
  **image pages**, not extracted here. Reporting basis is **ash-basis** (Table 7.5-1 note).

### 4. Material type (ask 4) — distribution IS tabled; recovery is NOT
**Table 7.5-1 "CMO Distribution by Lithology Group"** (p47, img 054; note: "% TREO+BREO+ScO,
ash-basis"). Total-percentage row (share of CMO by host lithology):
| Carbonaceous | Clay/Silt | Claystone | Coal | Coal-mixed | Shale | Sandstone | Scoria | Unconsol. | Not-logged | Other |
|---|---|---|---|---|---|---|---|---|---|---|
| 20.42 | 19.59 | 17.92 | **5.78** | 0.35 | 0.99 | 13.10 | 4.19 | 1.21 | 6.06 | 10.43 |

- **This directly supports our boundary-rock finding: only ~5.8% of the CMO sits in
  coal; the bulk is in carbonaceous material, clay/silt, and claystone (partings /
  boundary rock), plus sandstone (~13%).** §7.5.2 confirms seams (Dietz, Monarch,
  Carney, ~15 ft) are "relatively clean with some partings."
- **But recovery is NOT reported by material type.** §10.2 states test samples
  "include raw coal and other mineralized zones outside of the coal intervals" and
  that **"processing methods are not likely to vary significantly with ore type"** —
  i.e., the TRS *assumes a single ~uniform recovery across lithologies* and does not
  break it out coal vs claystone vs parting.

### Basis flag
Deposit grade is quoted **498 ppm ash-basis** and Table 7.5-1 is ash-basis, but
Fluor's process economics are "**preliminarily designed on a 500 ppm whole-rock
basis average ore grade**" (p60, img 067). ~Equal numerically but **different bases**;
the TRS does not explicitly reconcile them.

### Bearing on our recovery model
- The **84% overall CMO** / low-90s REE figure is a **bench + PEA-projected process
  recovery** for a designed caustic/leach+SX flowsheet — again, **not** weak-acid
  extractability, and **not** per-element.
- The TRS **neither supports nor refutes our uniform-across-series multiplier**: it
  doesn't disclose per-element recovery (it also assumes uniformity).
- A deeper nuance for the rank-conditioned factor: since ~94% of the CMO is in
  **non-coal lithologies** (claystone/carbonaceous/clay-silt/sandstone), a factor
  keyed to *coal rank* may be the wrong conditioning variable for this deposit type —
  the recoverable REE largely isn't in the coal maceral. Flagged, not acted on (n=1).
