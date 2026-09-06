# ASTM C618 bridge — coal ash oxide chemistry → per-sample fly-ash class → recovery

Turns Taggart's 3 basin-level fly-ash recovery figures into a **per-sample**
recovery assignment across all 7,658 COALQUAL samples, on a **mechanistic**
(oxide-chemistry) basis rather than a basin lookup.

## Gate (verified BEFORE building — PASS, with a label correction)
Converted whole-coal element ppm → **oxide wt% in ash** (`ppm / ash_frac / 1e4 ×
oxide_factor`; median oxide sum in ash = 92% → conversion sound). Classified all
samples and checked Taggart's basins:

| basin | Class F | high-Ca (C/interm) | med CaO | med SAF | Taggart says |
|---|---|---|---|---|---|
| Central Appalachian | **96%** | 0% | 1.5 | 87 | recalcitrant (roast, >70%) |
| Northern Appalachian | **98%** | 0% | 1.3 | 89 | recalcitrant |
| Southern Appalachian | **95%** | 0% | 1.9 | 86 | recalcitrant |
| Eastern (Illinois) | **92%** | 0% | 1.8 | 85 | recalcitrant |
| Powder River | 12% | 31% | **15.4** | 51 | soluble (~100% acid alone) |
| Fort Union (lignite) | 3% | 13% | 15.3 | 42 | (soluble end) |

- **Appalachian + Illinois reproduce Class F at 92–98%** — Taggart's recalcitrant
  group. Strong, clean pass.
- **Powder River is NOT strict "Class C"** — its ash is so calcic/silica-poor
  (CaO 15%, SAF 51) that 57% falls *below* the Class-C SAF≥50 floor into "other."
  That overshoots toward MORE soluble, consistent with Taggart's PRB ~100% acid
  alone. The mechanism holds; the strict binary label is too narrow.
- **The clean discriminator is CaO / Class-F membership**, not the "C" label:
  `CaO<10 & SAF≥70 → Class F (recalcitrant)` vs `CaO≥10 → high-Ca (acid-soluble)`.
- **Continuous base/acid** separates at the group level (PRB 0.66, Fort Union 1.05
  vs Appalachian 0.20–0.40) but mis-orders within (Illinois 0.55 > Appalachian
  despite being recalcitrant F). **CaO% is the better continuous variable** for
  this split; corr(base/acid, CaO)=0.40.

## National distribution (n=7,508 classified)
| Class F | C-interm (CaO 10–20) | Class C (CaO≥20) | F-lowSAF (50–70) | other |
|---|---|---|---|---|
| **79.2%** | 11.8% | 4.6% | 4.2% | 0.2% |
**~79% of the US coal REE resource would produce recalcitrant Class F ash — the
roast-required route. Only ~16% is high-Ca acid-soluble.**

## Recovery assignment by class (Taggart-anchored, per sample)
| ash class | recovery | reagent route |
|---|---|---|
| high-Ca (CaO≥10) | **~1.00** | acid alone (Taggart PRB) |
| Class F (SAF≥70, CaO<10) | **~0.70** | **1:1 NaOH roast 450 °C + 1–2 M HNO₃** (much lower with acid alone) |
| low-Ca low-SAF intermediate | ~0.85 | — |

Independent sanity: median class factor by rank came out **lignite→1.00,
subbit→0.85, bit→0.70, anthracite→0.70** — the bridge recovers the rank *ordering*
from ash chemistry alone, but on a **compressed 0.70–1.00 range** vs rank-only's
0.15–0.85.

## Basin ranking — three schemes (median recoverable magnet value $/t ash, n≥20)
| basin | contained $/t | A rank-only pos | B Taggart-basin pos | C class-bridge pos |
|---|---|---|---|---|
| Central Appalachian | 68 | 8 | **1** | **1** |
| Southern Appalachian | 63 | 9 | 4 | **2** |
| Texas | 54 | 1 | 2 | 3 |
| Powder River | 45 | 4 | 3 | 4 |
| Fort Union | 44 | 2 | 7 | 5 |
| Eastern (Illinois) | 54 | 11 | 5 | 7 |
| Northern Appalachian | 53 | 13 | 6 | 8 |
| Pennsylvania Anthracite | 51 | 14 | 14 | 9 |
| Green River | 43 | 12 | 13 | 14 |

**Findings**
1. **Rank-only's 0.25 bituminous penalty is the anomaly.** Both Taggart's
   measurement (>70% with roast) and the independent class assignment (Class F is
   recoverable) contradict it. Central Appalachian moves **8 → 1**.
2. **B (basin lookup) and C (per-sample class) agree at the top** — both put Central
   Appalachian #1 and lift the Appalachian/Illinois basins. C additionally
   **rehabilitates anthracite** (PA 14 → 9): anthracite ash is Class F (0.70), not
   the 0.15 rank-only assigns.
3. **Under the mechanistic bridge, recovery is nearly flat (0.70–1.00), so basin
   ranking collapses onto CONTAINED VALUE.** The ordering is essentially the
   contained-value ordering. Recovery stops being the discriminator basins were
   ranked on.

## Caveats that travel with this bridge (non-negotiable)
- **COAL ASH ≠ FLY ASH.** COALQUAL ash is lab-ashed (~750 °C, ASTM). Fly ash forms
  at 1400 °C+ in a boiler, where the glass/mullite phases that lock REE actually
  form. Bulk oxide proportions are broadly inherited; **the mineralogy is created by
  combustion.** This predicts what CLASS of fly ash a coal would produce — not the
  fly ash itself.
- Recovery figures rest on **n=7, three basins, total REE (not per-element), bench
  scale.**
- **Boiler type matters:** higher-temperature boilers yield more glassy phase, so the
  same coal gives different ash by plant. Not captured.
- **Fly-ash pathway only.** Raw-coal bituminous recovery remains undocumented.
- **The class assignment is a MECHANISTIC PROXY, not a measurement.**
- Reagent route is part of the number: Class F 0.70 requires the alkaline-roast
  flowsheet (added cost); Class C 1.00 is simple acid. A cost model must not treat
  them as equal-cost.
