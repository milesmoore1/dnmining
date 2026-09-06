# NETL extractability data inventory (on-disk + EDX) — corrects "no public dataset" claim

Inventory only, no modeling. **The earlier statement that no public dataset supports
extractability was wrong**: NETL hosts float-sink (washability) and leach datasets with
per-element assays, both on disk (dnmining/data/raw/netl) and downloadable from EDX.

## Step 1 — already on disk (dnmining/data/raw/netl/, loaded by src/netl_load.py, concentrations only)
Six `.xlsm` "REE researcher databases." The loader reads only the **Field** sheets and
**skips the Separation-Processing sheets** — which is where the extractability data is.

| file | sheet | rows | what's measured | per-sample |
|---|---|---|---|---|
| **de0027006** (UND, **low-rank** / Fort Union: Hagel, Harmon, Beulah) | Phase2 Separation-Processing **DMB** | **244** | **float-sink/density 40**, **leach 118** (mineral acid, pH, 1–4 h, staged), pyrolysis/thermal 45, oxalate precipitation 14; **Total % Recovery on 30 rows**; per-element product assays | yes; links to **44** distinct field samples |
| de0027006 | Phase2 Sep-Processing **DAB** | 117 | same method mix (float-sink 40, leach 50, thermal 13); % recovery not tabulated | yes; ~34 field links |
| **de0027035** (U. Kentucky, Appalachian) | Separation-Processing Samples | **1,550** | concentrations by **Sample Type + Size Fraction**; **no method / %-extracted / recovery columns** (different template) | per-sample concentrations, **not** paired % extractability |
| fe0030146 (Inventure) | Separation-Processing DMB | 30 | sparse; method/recovery not populated | unclear |
| foa-2003 / 2364 / 2404 | Separation-Processing / circuits | **0** | empty templates | — |

So on disk the **direct measurements are in de0027006**: ~40 float-sink/density rows and
~118 acid-leach rows (30 with a tabulated % recovery), **low-rank coal only**, from a
handful of North Dakota source coals, linked to ~44 field samples.

## Step 2 — on EDX (public CKAN API, **no account required**), downloadable XLSX
| dataset | XLSX files | content |
|---|---|---|
| **U. Kentucky sample analysis** | **8** | "Riffle Table + Mag Sep … **Washability Data**", "**Texas Lignite Washability Data**", "LTI II Riffle Table", "LTI II Magnetic", "Oil Agglomeration", "Multi-Gravity Separation", "**Washability REE Concentrations 19 Facilities**", "**Washability Correlated with REE Concentrations**" |
| **U. Utah sample analysis** | 1 | "REE Recovery from Western Coals Final Report All Tables" |
| **U. Alaska Fairbanks** | 1 | "University of Alaska **Washability Data**" |
| Middle Kittanning coal waste/underclay | 0 direct | EDX record is only an HTML pointer to a netl.doe.gov page (no XLSX in the CKAN record) |
| netl-ree-technical-reports | 7 PDF | reports, not spreadsheets |

"Washability" = float-sink density fractionation with **per-fraction REE assays** — the
direct organic-vs-mineral measurement the organic-affinity regression was substituting
for. UK covers **19 prep facilities** + Texas lignite; Utah = western coals; Alaska =
Alaska coal — multiple ranks/states. (Not yet downloaded/opened — that's the next pass.)

## Step 3 — honest count (what we can state now)
| source | material | n | measured | per-sample? |
|---|---|---|---|---|
| de0027006 DMB (on disk) | ND low-rank coal | 40 | float-sink density fractions + REE | yes |
| de0027006 DMB (on disk) | ND low-rank coal | 118 (30 w/ %rec) | acid leach + REE recovery | yes, ~44 field links |
| de0027035 (on disk) | Appalachian | 1,550 | concentration by size-fraction/type | yes (concentration only) |
| EDX UK washability | multi-state, 19 facilities, TX lignite | **TBD** | float-sink per-fraction REE | expected yes |
| EDX Utah / Alaska | western / AK coal | **TBD** | washability / recovery | expected yes |

## Step 4 — feasibility (paired bulk-chemistry + measured extractability/float-sink)
- **On disk:** paired records = **dozens**, single-rank (ND low-rank): ~40 float-sink,
  ~30 leach-with-%recovery, ~44 field-sample links. Small, and not rank-diverse.
- **EDX washability** is the direct float-sink measurement across 19 facilities + Texas
  lignite + Utah western + Alaska — plausibly **hundreds** of paired fraction/assay
  records across ranks, which would materially change the answer. **Exact paired n
  requires downloading and opening those XLSX (next pass).**
- Bottom line: direct extractability/mode-of-occurrence data **exists and is obtainable**;
  on-disk it is small and low-rank-only, EDX likely expands it. No modeling done here.

---

## EDX washability XLSX — DOWNLOADED and counted (float-sink partitions)

Downloaded 10 XLSX (public CKAN, **no account**): U. Kentucky ×8, U. Utah, U. Alaska.
No separate Penn State / WVU washability dataset surfaced in this program (only KY,
Utah, Alaska carry washability XLSX; Penn State appears only as PDF). Middle Kittanning
CKAN record is an HTML pointer to a netl.doe.gov page, not a spreadsheet.

Each washability file has real float-sink structure: **density cuts (Min/Max SG or
"Density Fraction"/"Density Class"), per-fraction full REE suite (Sc,Y,La–Lu) + Ash%,
mass%, and sample/stream IDs** so a sample is traceable across its fractions.

### THE COUNT THAT MATTERS — samples with a measured density partition, by rank
| rank | source | partitioned samples | notes |
|---|---|---|---|
| **Bituminous** (Appalachian/KY) | UK 19-Facilities (`Washability REE Concentrations`) | **61** sample×stream (≈19 raw-coal feeds + clean/reject streams) | SG cuts 1.3–2.2; 16-element REE ×~4 basis blocks + Ash; Sample/Lab IDs |
| Bituminous (KY) | UK "Washability Correlated" | 8 per-stream sheets (2 KY sites × 4 streams; **overlaps** the 19-facility set) | detailed size×density tables |
| **Subbituminous / western** | Utah `F&S – Bal/UnBal` | **~8–10** (WY Powder River, CO, UT, MO prefixes) | "Density Class" fractions, REE-in-ash; also Flotation + Magnetic Feed/Conc/Tails |
| **Lignite** | Utah F&S (ND Fort Union, "NDBM") | ~2 | within the 10 above |
| **Lignite** | Texas Lignite Washability | **1** ("Texas lignite", 22 density×size fractions, all type **"Parting"**) | boundary-rock emphasis |
| Alaska (subbit) | U. Alaska Washability | ~1–2 (non-standard layout, not fully parsed) | present, small |
| **Lignite (on disk)** | de0027006 Phase2 Sep-Proc | ~40 density rows across a handful of **ND Fort Union** source coals | "heavy mineral fraction" split (coarse, not full 1.3–2.0 curve) |

**Totals: ≈ 70–80 partitioned samples with per-fraction REE assays — but ~60 are
bituminous Kentucky; only single-digits-to-~10 each for subbituminous/western, lignite,
and Alaska.** This is **NOT "hundreds across ranks."**

### Separate quantity — LEACH (not float-sink), on disk
de0027006: ~118 acid-leach rows (mineral acid, pH, 1–4 h, staged), **30 with a tabulated
% recovery**, ND low-rank, linked to ~44 Fort Union field samples. This is *leach
extractability*, a different measurement from float-sink mode-of-occurrence.

### Feasibility (no modeling) — what the by-rank count implies
- The **direct float-sink measurement exists** (the organic-affinity regression, which
  failed at R²=0.069, was substituting for exactly this). So a *proper* mode-of-occurrence
  calc is possible **for bituminous Kentucky (n≈60)**.
- For the **low-rank classes** (lignite, subbituminous) — where organic association most
  drives extractability and where our recovery factors are guesses — the direct float-sink
  data is **single-digit** per rank. Enough to **validate/anchor**, **not** to fit a
  per-rank model.
- So the direct data does not resurrect a national per-rank organic-affinity model at n;
  it enables (a) a direct bituminous mode-of-occurrence characterization, and (b) low-rank
  anchor points (Texas lignite parting; ND Fort Union; de0027006 leach). Decision on
  whether to use any of it is deferred — counts only, per instruction.

### On-disk loader note
`src/netl_load.py` reads only the Field sheets and **skips the Separation-Processing
sheets** (its comment: lab process-stream sheets "lack location and are skipped"). The
float-sink (~40) and leach (~118, 30 w/ %recovery) data in de0027006 was therefore
present but unread the whole time.
