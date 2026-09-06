"""DISPLAY-ONLY sidecar: per-sample feed-composition separation index -> web/sepindex.json.
No change to the index math, his model, or any analytical module. Uses the restored
util/treatments.py (MARGINAL/JOINT) and data/prices.csv. Full-suite samples only;
samples without all 15 REY reported get NO record (null on lookup), never a guess.

Index (calibration A, PC88A-anchored, ionic-radius fit — see docs/separation_index_beta.md):
  D_norm = Σ_cut w_c / ln(β_c) ;  D_abs = V_ash · D_norm ;  w_c = 2·f_L·f_R (magnet-value split)
"""
import json, math, sys
from pathlib import Path
import geopandas as gpd, numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from util.treatments import apply_treatment, TREATMENTS  # restored module

def _prices(elements):  # read data/prices.csv directly (per-kg-element = oxide price × oxide_factor)
    p = pd.read_csv(ROOT/"data"/"prices.csv", comment="#")
    d = dict(zip(p["element"], p["price_usd_per_kg_oxide"]*p["oxide_factor"]))
    return {e: float(d[e]) for e in elements}

GDB = ROOT / "ree-and-coal-open-geodatabase.gdb"
LANTH = ["La","Ce","Pr","Nd","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu"]; REY = LANTH + ["Y"]
R = {"La":1.160,"Ce":1.143,"Pr":1.126,"Nd":1.109,"Sm":1.079,"Eu":1.066,"Gd":1.053,"Tb":1.040,
     "Dy":1.027,"Y":1.019,"Ho":1.015,"Er":1.004,"Tm":0.994,"Yb":0.985,"Lu":0.977}
ORD = ["La","Ce","Pr","Nd","Sm","Eu","Gd","Tb","Dy","Y","Ho","Er","Tm","Yb","Lu"]
bA = 10.35
BETA = [10**(bA*(R[ORD[i]] - R[ORD[i+1]])) for i in range(len(ORD)-1)]
PAIR = [f"{ORD[i]}/{ORD[i+1]}" for i in range(len(ORD)-1)]
MAG = ["Nd","Pr","Dy","Tb"]
PRICE = _prices(MAG)
POS = {m: ORD.index(m) for m in MAG}


def cut_contribs(conc, beta):
    V = {m: (conc[m] or 0)*PRICE[m] for m in MAG}; tot = sum(V.values())
    if tot <= 0: return None, None
    fV = {m: V[m]/tot for m in MAG}
    contrib = []
    for c in range(len(ORD)-1):
        fL = sum(fV[m] for m in MAG if POS[m] <= c); w = 2*fL*(1-fL)
        contrib.append(w/math.log(beta[c]) if w > 0 else 0.0)
    dnorm = sum(contrib)
    return dnorm, contrib


def main():
    el = gpd.read_file(GDB, layer="REE0009_Trace_Elements_Data")
    ash = pd.to_numeric(el["GSAsh_Dry"], errors="coerce")/100.0
    sid = el["Sample_ID"].astype(object)
    faces = {e: pd.to_numeric(el[e], errors="coerce") for e in REY}
    treat = {"FACE": faces}
    for t in ["DL2","MARGINAL","JOINT"]:
        f = apply_treatment(el, t); treat[t] = {e: pd.to_numeric(f[e], errors="coerce") for e in REY}
    isL = {m: el[f"{m}_Q"].fillna("").astype(str).str.contains(r'(?:^|,)L(?:,|$)', regex=True).to_numpy() for m in MAG}

    full = np.ones(len(el), bool)
    for e in REY: full &= faces[e].notna().to_numpy()

    recs, n = {}, 0
    for i in range(len(el)):
        s = sid.iloc[i]
        if s is None or (isinstance(s, float) and pd.isna(s)): continue
        s = str(s)
        if not full[i]:
            continue  # no full REE suite -> no record (null on lookup), never guessed
        Dn, Da = {}, {}
        cutshare = None; hard = None
        for t in TREATMENTS:
            conc = {e: (None if pd.isna(treat[t][e].iloc[i]) else float(treat[t][e].iloc[i])) for e in REY}
            dn, contrib = cut_contribs(conc, BETA)
            if dn is None: continue
            Dn[t] = round(dn, 5)
            af = ash.iloc[i]
            if af and af > 0:
                Vash = sum((conc[m]/af)*PRICE[m] for m in MAG)
                Da[t] = round(dn*Vash, 1)
            if t == "JOINT" and dn > 0:
                shares = [{"pair": PAIR[c], "share": round(contrib[c]/dn, 4)} for c in range(len(PAIR)) if contrib[c] > 0]
                shares.sort(key=lambda x: -x["share"])
                cutshare = shares; hard = shares[0] if shares else None
                Vj = sum((conc[m] or 0)*PRICE[m] for m in MAG)
                cmf = sum((conc[m] or 0)*PRICE[m] for m in MAG if isL[m][i])/Vj if Vj > 0 else None
                below = [m for m in MAG if isL[m][i]]
        if "JOINT" not in Dn: continue
        recs[s] = {"Dn": Dn, "Da": Da, "cuts": cutshare, "hardcut": hard,
                   "cmf": round(cmf, 3) if cmf is not None else None, "below": below,
                   "basin": (None if pd.isna(el["Region"].iloc[i]) else str(el["Region"].iloc[i]))}
        n += 1

    meta = {
        "label": ("Feed-composition separation index — physically-grounded ionic-radius "
                  "selectivity model, one stated extractant system (PC88A-anchored, calibration A). "
                  "Not a separation-difficulty measurement, not stage counts. 1 sourced beta pair, "
                  "13 fitted. Ranking is algebraically invariant to uniform beta scaling; per-cut "
                  "±20% holds Spearman 0.993."),
        "calibration": "A (PC88A Nd/Pr=1.5; ionic-radius fit)",
        "primary_treatment": "JOINT", "treatments": TREATMENTS,
        "magnet_elements": MAG, "prices_usd_per_kg": {m: round(PRICE[m], 2) for m in MAG},
        "beta": {PAIR[c]: round(BETA[c], 3) for c in range(len(PAIR))},
        "censoring_note": ("median 53% of magnet value is imputed; 58% of samples draw >50% of magnet "
                           "value from below-detection elements (Dy 87% censored). The index rests on "
                           "substituted values for most samples."),
        "ranking_status": "PROVISIONAL",
    }
    (HERE/"sepindex.json").write_text(json.dumps({"meta": meta, "records": recs}, separators=(",", ":"), allow_nan=False))

    his = json.loads((HERE/"miles_data.json").read_text())["samples"]
    his_ids = [str(x["id"]) for x in his if x.get("id") is not None]
    matched = sum(1 for i in his_ids if i in recs)
    print(f"full-suite records written: {len(recs):,}")
    print(f"his atlas samples: {len(his_ids):,}  with sep-index: {matched:,} "
          f"({100*matched/len(his_ids):.1f}%)  null (no full REE suite): {len(his_ids)-matched}")
    print(f"wrote sepindex.json ({(HERE/'sepindex.json').stat().st_size/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
