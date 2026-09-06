"""DISPLAY-ONLY sidecar for the geoscience panels. NOT an analytical change.

Reads the SAME geodatabase Miles's pipeline already reads (REE0009), pulling the
REE columns and _Q qualifier flags his export happens to drop. His model,
features, target, split, metrics and miles_data.json are untouched; this only
writes web/geochem.json, keyed on Sample_ID, for display.

  FACE  = value as stored in the source geodatabase (COALQUAL). For an L-flagged
          element that stored value IS the detection limit, not a measurement.
          Read directly — no reconstruction by doubling DL/2.
  DL/2  = Miles's substitution, computed via his own util/qualifiers.py so the
          comparison is faithful to his pipeline.

Chondrite normalization: McDonough & Sun (1995) CI. Derived geochemical indices
are computed here (display arithmetic) for both FACE and DL/2.
"""
import json
import math
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from util.qualifiers import resolve_qualifiers  # import only; not modified

GDB = ROOT / "ree-and-coal-open-geodatabase.gdb"
LANTH = ["La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu"]
REY = LANTH + ["Y"]
ELEMS = REY + ["Sc"]

# McDonough & Sun (1995) CI chondrite, ppm
CHOND = {"La": 0.237, "Ce": 0.613, "Pr": 0.0928, "Nd": 0.457, "Sm": 0.148,
         "Eu": 0.0563, "Gd": 0.199, "Tb": 0.0361, "Dy": 0.246, "Ho": 0.0546,
         "Er": 0.160, "Tm": 0.0247, "Yb": 0.161, "Lu": 0.0246, "Y": 1.57}
CRIT = ["Nd", "Eu", "Tb", "Dy", "Er", "Y"]        # Seredin & Dai critical
EXC = ["Ce", "Ho", "Tm", "Yb", "Lu"]              # Seredin & Dai excessive
LREE = ["La", "Ce", "Pr", "Nd", "Sm", "Eu"]
HREE = ["Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y"]


def norm(vals):
    return {e: (vals[e] / CHOND[e] if vals.get(e) not in (None, 0) and vals.get(e) is not None else None)
            for e in REY}


def _r(x, n=4):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return round(float(x), n)


def indices(vals, censored):
    """Derived REE indices from a dict of element ppm. `censored` = set of L elements
    used to flag indices computed partly from detection limits."""
    n = norm(vals)
    def g(e):  # normalized, or None
        return n.get(e)
    out = {}
    def flag(elts):
        return any(e in censored for e in elts)
    # Eu/Eu*
    if g("Eu") and g("Sm") and g("Gd"):
        out["EuEu"] = {"v": _r(g("Eu") / math.sqrt(g("Sm") * g("Gd"))), "cens": flag(["Eu", "Sm", "Gd"])}
    if g("Ce") and g("La") and g("Pr"):
        out["CeCe"] = {"v": _r(g("Ce") / math.sqrt(g("La") * g("Pr"))), "cens": flag(["Ce", "La", "Pr"])}
    if g("La") and g("Yb"):
        out["LaYb"] = {"v": _r(g("La") / g("Yb")), "cens": flag(["La", "Yb"])}
    if g("La") and g("Sm"):
        out["LaSm"] = {"v": _r(g("La") / g("Sm")), "cens": flag(["La", "Sm"])}
    if g("Gd") and g("Yb"):
        out["GdYb"] = {"v": _r(g("Gd") / g("Yb")), "cens": flag(["Gd", "Yb"])}
    lree = [vals[e] for e in LREE if vals.get(e) is not None]
    hree = [vals[e] for e in HREE if vals.get(e) is not None]
    if lree and hree and sum(hree) > 0:
        out["LREE_HREE"] = {"v": _r(sum(lree) / sum(hree)), "cens": flag(LREE + HREE)}
    tree = [vals[e] for e in REY if vals.get(e) is not None]
    out["TREE"] = {"v": _r(sum(tree)) if tree else None, "cens": flag(REY)}
    # Seredin & Dai enrichment type (needs La_N, Sm_N, Gd_N, Lu_N)
    if g("La") and g("Lu"):
        laLu = g("La") / g("Lu")
        typ = None
        if laLu > 4:
            typ = "L (light)"
        elif laLu < 1:
            typ = "H (heavy)"
        elif g("La") and g("Sm") and g("Gd") and g("Lu") and (g("La") / g("Sm") < 1) and (g("Gd") / g("Lu") > 1):
            typ = "M (medium)"
        else:
            typ = "L/M transitional"
        out["seredin"] = {"v": typ, "cens": flag(["La", "Sm", "Gd", "Lu"])}
    # Outlook coefficient (Seredin & Dai 2012): crit share / exc share
    crit = [vals[e] for e in CRIT if vals.get(e) is not None]
    exc = [vals[e] for e in EXC if vals.get(e) is not None]
    if crit and exc and sum(exc) > 0 and tree and sum(tree) > 0:
        c_share = sum(crit) / sum(tree)
        e_share = sum(exc) / sum(tree)
        coutl = c_share / e_share if e_share > 0 else None
        out["coutl"] = {"v": _r(coutl), "cens": flag(CRIT + EXC),
                        "call": ("promising" if (coutl is not None and coutl > 0.7) else "unpromising")}
    return out


def main():
    el = gpd.read_file(GDB, layer="REE0009_Trace_Elements_Data")
    face = el.copy()
    dl2 = resolve_qualifiers(el, ELEMS, substitute="half")  # his pipeline's own treatment

    def flags(e):
        q = el[f"{e}_Q"].fillna("").astype(str)
        return (q.str.contains(r'(?:^|,)L(?:,|$)', regex=True).to_numpy(),
                q.str.contains(r'(?:^|,)N(?:,|$)', regex=True).to_numpy())
    L = {e: flags(e)[0] for e in ELEMS}
    N = {e: flags(e)[1] for e in ELEMS}

    # national censoring (L% of valued) per element for the legend
    cens_rate = {}
    for e in ELEMS:
        v = pd.to_numeric(el[e], errors="coerce")
        valn = int(v.notna().sum())
        cens_rate[e] = _r(100 * L[e].sum() / valn, 1) if valn else None

    sid = el["Sample_ID"].astype("object")
    ash = pd.to_numeric(el["GSAsh_Dry"], errors="coerce")
    al = pd.to_numeric(el["Al"], errors="coerce") if "Al" in el.columns else pd.Series([np.nan] * len(el))
    region = el["Region"].astype("object")
    fnum = {e: pd.to_numeric(face[e], errors="coerce") for e in ELEMS}
    dnum = {e: pd.to_numeric(dl2[e], errors="coerce") for e in ELEMS}

    records, dup = {}, 0
    for i in range(len(el)):
        s = sid.iloc[i]
        if s is None or (isinstance(s, float) and math.isnan(s)):
            continue
        s = str(s)
        if s in records:
            dup += 1
            continue
        censored = {e for e in ELEMS if L[e][i]}
        fv = {e: (None if pd.isna(fnum[e].iloc[i]) else float(fnum[e].iloc[i])) for e in ELEMS}
        dv = {e: (None if pd.isna(dnum[e].iloc[i]) else float(dnum[e].iloc[i])) for e in ELEMS}
        el_rec = {e: {"f": _r(fv[e]), "d": _r(dv[e]),
                      "L": bool(L[e][i]), "N": bool(N[e][i])} for e in ELEMS}
        records[s] = {
            "ash": _r(ash.iloc[i], 3),
            "al2o3": _r(float(al.iloc[i]) * 1.8895, 3) if not pd.isna(al.iloc[i]) else None,
            "basin": (None if region.iloc[i] is None or (isinstance(region.iloc[i], float) and pd.isna(region.iloc[i])) else str(region.iloc[i])),
            "el": el_rec,
            "idx_face": indices(fv, censored),
            "idx_dl2": indices(dv, censored),
        }

    meta = {
        "normalization": "McDonough & Sun (1995) CI chondrite",
        "chondrite": {e: CHOND[e] for e in REY},
        "basis": "whole-coal (ppm), as reported in the source geodatabase",
        "order": REY, "lanthanides": LANTH,
        "censoring_pct": cens_rate,
        "dropped_from_his_export": ["Eu", "Er", "Tm", "Yb", "Lu"],
        "note": ("Eu, Er, Tm, Yb, Lu are present in the source geodatabase but not in "
                 "Miles's model feature/target set, so they appear in these geochemistry "
                 "panels and not in his predictions. This is his export scope, stated neutrally."),
        "seredin_critical": CRIT, "seredin_excessive": EXC,
        "references": {"chondrite": "McDonough & Sun 1995",
                       "ucc": "Rudnick & Gao 2003 (Upper Continental Crust)",
                       "world_coal": "Ketris & Yudovich 2009 (world hard coal)",
                       "indices": "Seredin & Dai 2012"},
    }
    payload = {"meta": meta, "records": records}
    (HERE / "geochem.json").write_text(json.dumps(payload, separators=(",", ":"), allow_nan=False))

    # join-rate report against his atlas samples
    his = json.loads((HERE / "miles_data.json").read_text())["samples"]
    his_ids = [str(s["id"]) for s in his if s.get("id") is not None]
    matched = sum(1 for i in his_ids if i in records)
    print(f"geodatabase rows: {len(el):,}  unique Sample_IDs written: {len(records):,}  duplicate IDs skipped: {dup}")
    print(f"his atlas samples: {len(his_ids):,}  joined to geochem: {matched:,} "
          f"({100*matched/len(his_ids):.1f}%)  unmatched: {len(his_ids)-matched}")
    print(f"wrote geochem.json ({(HERE/'geochem.json').stat().st_size/1e6:.1f} MB)")
    print("censoring % (L of valued):", {e: cens_rate[e] for e in REY})


if __name__ == "__main__":
    main()
