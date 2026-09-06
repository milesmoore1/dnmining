"""DISPLAY-ONLY sidecar: MSHA coal mines + basin/coal-field boundaries.
No change to his pipeline, model, or miles_data.json. Writes:
  web/mines.json       MSHA coal mines (filtered), for the mine layer + nearest-mine
  web/basins.geojson   named analysis-basin extents (convex hull of each Region's
                       samples) + centroid + count  [analysis basins live on the
                       sample Region field; the geodatabase polygon layers carry
                       no name attribute, so hulls are the named, analysis-aligned
                       boundary]
  web/coalfields2.geojson  geodatabase coal-field polygons (REE0159), simplified,
                       unnamed — faint geographic context only
"""
import json
import math
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPoint, mapping

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MSHA = Path("/tmp/msha_mines/Mines.txt")
GDB = ROOT / "ree-and-coal-open-geodatabase.gdb"

STATUS_FILLED = {"Active", "New Mine", "NonProducing", "Temporarily Idled"}
TYPE = {"Surface": "S", "Underground": "U", "Facility": "F"}
COMM = {"Coal (Bituminous)": "B", "Coal (Anthracite)": "A", "Coal (Lignite)": "L"}


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def mines():
    df = pd.read_csv(MSHA, sep="|", dtype=str, encoding="latin-1", low_memory=False)
    coal = df[df["COAL_METAL_IND"] == "C"].copy()
    lat = pd.to_numeric(coal["LATITUDE"], errors="coerce")
    lon = pd.to_numeric(coal["LONGITUDE"], errors="coerce")
    ok = lat.between(18, 72) & lon.between(-180, -60) & (lat != 0) & (lon != 0)
    coal = coal[ok]
    def sv(x):
        return None if (x is None or (isinstance(x, float) and math.isnan(x)) or pd.isna(x)) else str(x)
    out = []
    for _, r in coal.iterrows():
        emp = num(r.get("NO_EMPLOYEES"))
        st = sv(r.get("CURRENT_MINE_STATUS"))
        out.append({
            "id": sv(r["MINE_ID"]), "n": sv(r.get("CURRENT_MINE_NAME")),
            "o": sv(r.get("CURRENT_OPERATOR_NAME")), "c": sv(r.get("CURRENT_CONTROLLER_NAME")),
            "lat": round(float(r["LATITUDE"]), 5), "lon": round(float(r["LONGITUDE"]), 5),
            "st": st,
            "ty": TYPE.get(sv(r.get("CURRENT_MINE_TYPE")), "F"),
            "cm": COMM.get(sv(r.get("PRIMARY_SIC")), "?"),
            "e": int(emp) if emp is not None else None,
            "tw": sv(r.get("NEAREST_TOWN")), "cty": sv(r.get("FIPS_CNTY_NM")), "stt": sv(r.get("STATE")),
            "f": st in STATUS_FILLED,
        })
    meta = {"source": "MSHA Mines dataset (arlweb.msha.gov OpenGovernmentData), COAL only, valid US coords",
            "n": len(out),
            "status_counts": coal["CURRENT_MINE_STATUS"].value_counts().to_dict(),
            "type_counts": coal["CURRENT_MINE_TYPE"].value_counts().to_dict()}
    (HERE / "mines.json").write_text(json.dumps({"meta": meta, "mines": out}, separators=(",", ":"), allow_nan=False))
    print(f"mines.json: {len(out):,} coal mines ({(HERE/'mines.json').stat().st_size/1e6:.1f} MB)")
    return out


def basins():
    d = json.loads((HERE / "miles_data.json").read_text())["samples"]
    by = {}
    for s in d:
        b = s.get("basin")
        if b and s.get("lat") is not None and s.get("lon") is not None:
            by.setdefault(b, []).append((s["lon"], s["lat"]))
    feats = []
    for b, pts in by.items():
        if len(pts) < 3:
            continue
        hull = MultiPoint(pts).convex_hull
        if hull.geom_type != "Polygon":
            continue
        c = hull.centroid
        feats.append({"type": "Feature",
                      "properties": {"basin": b, "n": len(pts),
                                     "cx": round(c.x, 4), "cy": round(c.y, 4)},
                      "geometry": mapping(hull)})
    (HERE / "basins.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}))
    print(f"basins.geojson: {len(feats)} named analysis-basin hulls")


def coalfields():
    g = gpd.read_file(GDB, layer="REE0159_Coal_Fields").to_crs(4326)
    g["geometry"] = g["geometry"].simplify(0.02, preserve_topology=True)
    g = g[~g.geometry.is_empty & g.geometry.notna()]
    g[["geometry"]].to_file(HERE / "coalfields2.geojson", driver="GeoJSON")
    print(f"coalfields2.geojson: {len(g)} coal-field polygons (context, unnamed) "
          f"({(HERE/'coalfields2.geojson').stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    mines(); basins(); coalfields()
