# Basin × material × method recovery table (documented) + basin-ranking impact

Not a per-sample model — a **conditioned recovery table at the level a flowsheet is
designed for**, harvested from published measurements. Source rows in
`data/recovery_literature.csv`.

## Anchor verified (with a citation correction)
The "basin-conditioned recovery" anchor is **Taggart, Hower & Hsu-Kim (2018),
*Int. J. Coal Geol.* 196, OSTI 1526009** — NOT `10.1021/acs.est.2c09273` (that
"Green Approach" is a separate 2023 ES&T paper). The cited numbers are Taggart 2018
and were verified from the OSTI full text:
- **7 coal fly-ash samples**, 3 basins (Appalachian, Illinois, Powder River), ash
  types stoker/ESP/silo/pond.
- **Powder River fly ash ≈ 100%** total-REE recovery with **acid leaching alone**
  (regardless of roasting agent/ratio) — "more soluble."
- **Appalachian & Illinois fly ash: >70%** with **1:1 NaOH-ash roast (450 °C, 30 min)
  + 1–2 mol/L HNO₃.**
- **NaOH roast recovered >90%** total REE (≈ USGS Na₂O₂ sinter); other additives
  (CaO, Na₂CO₃, CaSO₄, (NH₄)₂SO₄) <50%.
- **Strong positive correlation between REE extraction and leachate H⁺ molarity.**
All figures are **total REE, bench scale, FLY ASH.**

## CRITICAL material distinction (tagged in every CSV row — do not merge)
| material | what it is | documented anchor |
|---|---|---|
| **fly ash** | REE locked in a **combustion-created glassy aluminosilicate/mullite matrix** (recalcitrant) | Taggart 2018 (PRB ~100% acid; App/IL >70% roast+acid) |
| **raw coal** | organically-bound (low-rank) + mineral REE, unburned | Laudal Fort Union lignite weak-acid **80–95%**; Ramaco PRB subbit caustic **process** ~84% (bench+PEA) |
| **refuse / underclay** | mineral-hosted, unburned | none extracted (Middle Kittanning pending) |
| **AMD solids** | Fe/Al oxyhydroxide sludge, easily leached | qualitative only (OSTI 3010013/3020894); no % fabricated |

## Coverage matrix (documented ✓ / empty)
| basin | fly ash | raw coal | refuse/underclay | AMD |
|---|---|---|---|---|
| Powder River (subbit) | ✓ ~100% acid | ✓ ~84% caustic (Ramaco) | — | — |
| Appalachian (bit) | ✓ >70% roast+acid | — | — | qual. (WV/PA AMD) |
| Illinois/Eastern (bit) | ✓ >70% roast+acid | — | — | — |
| Fort Union (lignite) | — | ✓ 80–95% weak-acid (Laudal); DE-FE0027006 leach n~30 | — | — |
| all other basins | — | — | — | — |
**Sparse:** fly-ash row = 3 basins; raw-coal row = 2 ranks (lignite, subbit); everything
else interpolated. Documented n is small (7 ash samples + Laudal + 1 Ramaco deposit +
~30 DE-FE0027006 leach). This is a validation/anchor set, not a training set.

## Basin-ranking impact — rank-only (interpolated) vs documented FLY-ASH recovery
Recoverable magnet value = median ash-basis contained value × recovery factor, per basin
(full-suite samples). Rank-only factors {lignite .85, subbit .55, bit .25, anthr .15}
vs documented fly-ash {PRB 1.00; App×3 & Illinois/Eastern 0.70; others = interpolated}.

| basin | rank | n | contained $/t | rank-only pos → documented pos | move |
|---|---|---|---|---|---|
| **Central Appalachian** | bit | 1661 | 68.2 | **9 → 1** | **+8** |
| Southern Appalachian | bit | 999 | 63.5 | 10 → 4 | +6 |
| Eastern (Illinois) | bit | 373 | 55.1 | 11 → 5 | +6 |
| Northern Appalachian | bit | 1687 | 52.9 | 12 → 7 | +5 |
| Powder River | subbit | 163 | 44.9 | 6 → 3 | +3 |
| Fort Union | lignite | 64 | 44.3 | 2 → 6 | −4 |
| Texas / Wind River / Alaska / Green River (interpolated) | low-rank | — | — | drop 4–5 places | − |

**The rank-only factor severely mis-ranks basins for the ash pathway.** It buries the
bituminous Appalachian basins at the bottom (factor 0.25) *despite their highest
contained value*; under documented fly-ash recovery Central Appalachian moves **9 → 1**.
The premise that bituminous REE is nearly unrecoverable (0.25) is contradicted by the
documented >70% fly-ash recovery with roasting.

## Honest limits
- **This ranking is the FLY-ASH pathway** (burn coal → leach ash). Our COALQUAL contained
  value is **raw coal**; applying fly-ash recoveries assumes the coal→ash→leach route.
  For a **raw-coal** leach route the only documented anchors are lignite weak-acid (Laudal)
  and PRB subbit caustic *process* (Ramaco); **bituminous raw-coal leach is undocumented**,
  so 0.70 must NOT be reused for raw-coal bituminous.
- Documented cells cover **5 basins for fly ash + 2 ranks for raw coal**; all other cells
  remain interpolated and are flagged as such.
- OSTI harvest: the Taggart anchor was extracted from full text; other program reports
  (Gulf Coast CORE-CM 3009720/3017488, AMDREE 3010013, electrochemical 3376162, etc.)
  were **identified but their leach tables not OCR'd this pass** — no rows fabricated for
  unread reports; the CSV holds verified rows only and is extendable.
