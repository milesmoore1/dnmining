"""Run Miles's pipeline end to end, UNMODIFIED — replicates geodatabase_explorer.ipynb
cell for cell, calling only his util modules with his config. Adds no analysis: it
captures his numbers and serialises his classifier's output for the visualization.
"""
import json
import os
import sys
from pathlib import Path

os.environ["MPLBACKEND"] = "Agg"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # so cfg.GDB_PATH (relative) resolves

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, confusion_matrix, accuracy_score, classification_report
from xgboost import XGBClassifier

from util import config as cfg
from util.data_preparation import (
    load_layer, select_columns, fill_missing_ree, add_priority_labels, merge_samples,
)
from util.qualifiers import resolve_qualifiers
from util.modeling import prepare_train_test, evaluate_classifier
from util.plotting import plot_classifier_diagnostics

steps = {}

# ---- cell 6: load + select element layer ----
element_data_raw = load_layer(cfg.GDB_PATH, cfg.ELEMENT_LAYER)
element_data = select_columns(element_data_raw, cfg.ELEMENT_COLS_NEEDED)
steps["element_rows_loaded"] = len(element_data)

# ---- cell 8: DL/2 substitution -> chondrite fill -> median-split label ----
element_data = resolve_qualifiers(element_data, cfg.REY_ELEMENTS + cfg.FEATURE_ELEMENTS)
element_data = fill_missing_ree(element_data, cfg.TARGETS)
element_data = add_priority_labels(element_data, cfg.LABEL_ELEMENTS, cfg.PRICE_PER_KG, cfg.CLASS_NAMES)
steps["after_label_rows"] = len(element_data)
steps["labeled_rows"] = int(element_data["priority_tier"].notna().sum())
steps["class_balance"] = element_data["priority_tier"].value_counts(dropna=False).to_dict()

# ---- cell 10: load quality layer + merge ----
coal_quality_raw = load_layer(cfg.GDB_PATH, cfg.QUALITY_LAYER)
coal_quality = select_columns(coal_quality_raw, cfg.COAL_QUALITY_COLS_NEEDED)
final_data = merge_samples(element_data, coal_quality)
steps["merged_shape"] = list(final_data.shape)

# ---- cell 12: random stratified split + XGBoost ----
X_train, X_test, y_train, y_test = prepare_train_test(
    final_data, cfg.FEATURE_COLS, cfg.CATEGORICAL_COLS, cfg.TEST_SIZE, cfg.RANDOM_STATE,
)
steps["train_rows"], steps["test_rows"] = len(X_train), len(X_test)
model = XGBClassifier(**cfg.MODEL_PARAMS)
model.fit(X_train, y_train)

print("\n===== HIS evaluate_classifier (test set) =====")
preds = evaluate_classifier(model, X_test, y_test, cfg.CLASS_NAMES)

proba_test = model.predict_proba(X_test)[:, 1]
metrics = {
    "accuracy": float(accuracy_score(y_test, preds)),
    "auc": float(roc_auc_score(y_test, proba_test)),
    "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
    "report": classification_report(y_test, preds, target_names=cfg.CLASS_NAMES, output_dict=True),
}

# feature importances (his XGBoost, gain-based default)
imp = pd.Series(model.feature_importances_, index=X_train.columns).sort_values(ascending=False)
metrics["top_features"] = [{"feature": k, "importance": float(v)} for k, v in imp.head(15).items()]

# ---- cell 14: his diagnostic figures -> save PNGs ----
try:
    figs = plot_classifier_diagnostics(model, X_test, y_test, X_train.columns, cfg.CLASS_NAMES)
    names = ["miles_diag_panel", "miles_diag_proba", "miles_diag_importance"]
    for fig, nm in zip(figs, names):
        fig.savefig(HERE / f"{nm}.png", dpi=110, bbox_inches="tight", facecolor="#fcfcfb")
    print("saved diagnostic figures:", names)
except Exception as e:
    print("diagnostic plotting skipped:", e)

# ---- serialise HIS output for the map: predicted P(high) for every labeled sample ----
proba_all = pd.Series(index=list(X_train.index) + list(X_test.index), dtype=float)
proba_all.loc[X_train.index] = model.predict_proba(X_train)[:, 1]
proba_all.loc[X_test.index] = model.predict_proba(X_test)[:, 1]
split = pd.Series("train", index=proba_all.index)
split.loc[X_test.index] = "test"

REY = cfg.REY_ELEMENTS  # DL/2-substituted values live in final_data now
samples = []
for idx in proba_all.index:
    r = final_data.loc[idx]
    lat, lon = pd.to_numeric(r.get("Latitude"), errors="coerce"), pd.to_numeric(r.get("Longitude"), errors="coerce")
    if not (np.isfinite(lat) and np.isfinite(lon)):
        continue
    def num(c):
        v = pd.to_numeric(r.get(c), errors="coerce")
        return None if pd.isna(v) else round(float(v), 4)
    def sval(c):  # string field -> None if missing (avoid NaN in JSON)
        v = r.get(c)
        try:
            return None if pd.isna(v) else str(v)
        except (TypeError, ValueError):
            return v
    p = float(proba_all.loc[idx])
    samples.append({
        "id": sval("Sample_ID"), "lat": round(float(lat), 5), "lon": round(float(lon), 5),
        "county": sval("County"), "state": sval("State"), "basin": sval("Region"),
        "bed": sval("Bed"), "rank": sval("Estimated_Rank"),
        "ash": num("GSAsh_Dry"), "thick": num("Thickness__in_"),
        "value": num("critical_ree_value_per_ton"),   # HIS whole-coal value, his prices
        "p_high": round(p, 4), "pred": cfg.CLASS_NAMES[1 if p >= 0.5 else 0],
        "tier": (None if pd.isna(r.get("priority_tier")) else str(r.get("priority_tier"))),
        "split": split.loc[idx],
        "dl2": {e: num(e) for e in REY if e in final_data.columns},
        "feat": {c: (num(c) if c not in cfg.CATEGORICAL_COLS
                     else (None if pd.isna(r.get(c)) else str(r.get(c))))
                 for c in cfg.FEATURE_COLS if c in final_data.columns},
    })

meta = {
    "pipeline": "Miles / geodatabase_explorer.ipynb, unmodified",
    "treatment": "DL/2 substitution (util/qualifiers.py substitute='half')",
    "basis": "whole-coal; hardcoded prices in util/config.py",
    "prices_used": cfg.PRICE_PER_KG,
    "steps": steps, "metrics": metrics,
    "class_names": cfg.CLASS_NAMES,
    "his_caveat": ("Random stratified split. Per his notebook: \"This score measures the "
                   "existing random holdout, not performance in unseen regions.\""),
}
import math

def clean(o):
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else o
    if isinstance(o, dict):
        out = {}
        for k, v in o.items():
            if not isinstance(k, str):
                k = "NaN" if (isinstance(k, float) and math.isnan(k)) else str(k)
            out[k] = clean(v)
        return out
    if isinstance(o, (list, tuple)):
        return [clean(x) for x in o]
    if isinstance(o, np.floating):
        f = float(o)
        return None if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(o, np.integer):
        return int(o)
    return o

payload = clean({"meta": meta, "samples": samples})
(HERE / "miles_data.json").write_text(json.dumps(payload, separators=(",", ":"), allow_nan=False))

print("\n===== SUMMARY OF HIS NUMBERS =====")
print(json.dumps({"steps": steps,
                  "accuracy": metrics["accuracy"], "auc": metrics["auc"],
                  "confusion_matrix": metrics["confusion_matrix"],
                  "top5_features": metrics["top_features"][:5]}, indent=2))
print(f"\nserialized {len(samples):,} georeferenced labeled samples -> web/miles_data.json")
