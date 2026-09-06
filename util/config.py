"""Dataset columns, label assumptions, and model configuration."""

from pathlib import Path

ELEMENT_ID_COLS = ["Sample_ID", "PointId"]

ELEMENT_LOCATION_COLS = [
    "State", "County", "Latitude", "Longitude",
    "Province", "Region", "Field", "District",
    "Formation", "Bed", "Member", "System", "Thickness__in_", "geometry",
]

ELEMENT_RANK_COLS = ["Estimated_Rank", "Apparent_Rank"]

ELEMENT_PROVENANCE_COLS = [
    "Analytical_Lab", "Values_Represent", "dateupdated",
    "source_organization", "dataset_name", "source_ID",
]

# ---------------------------------------------------------------------------
# Rare earth elements: CORE (the label) vs SUPPORT (interpolation neighbors)
# See notes below for why each element landed where it did.
# ---------------------------------------------------------------------------
CORE_REY_ELEMENTS = ["Nd", "Pr", "Tb", "Dy", "Y"]
SUPPORT_REY_ELEMENTS = ["La", "Ce", "Sm", "Gd", "Ho"]

REY_ELEMENTS = CORE_REY_ELEMENTS + SUPPORT_REY_ELEMENTS
ELEMENT_REY_COLS = [c for e in REY_ELEMENTS for c in (e, f"{e}_Q")]

FEATURE_ELEMENTS = ["GSAsh_Dry", "Si", "Al", "Ca", "Mg", "Na", "K",
                     "Fe", "Ti", "TS", "As", "Mo", "Zn", "P",
                     "Zr", "Sc", "Th", "U", "Nb", "Ga", "Li", "Ba", "Sr", "V"]
ELEMENT_FEATURE_COLS = [c for e in FEATURE_ELEMENTS for c in (e, f"{e}_Q")]

ELEMENT_COLS_NEEDED = (
    ELEMENT_ID_COLS + ELEMENT_LOCATION_COLS + ELEMENT_RANK_COLS
    + ELEMENT_PROVENANCE_COLS + ELEMENT_REY_COLS + ELEMENT_FEATURE_COLS
)


COAL_QUALITY_ID_COLS = ["Sample_ID", "State"]  # State kept only for the sanity check

COAL_QUALITY_VALIDATION_COLS = ["Proximate_Validation", "Ultimate_Validation"]

COAL_QUALITY_FEATURE_BASE = [
    "Moisture", "Volatile_Matter", "Fixed_Carbon", "Standard_Ash",
    "Carbon", "Sulfur", "Btu",
    "Sulfate_Sulfur", "Pyritic_Sulfur", "Organic_Sulfur",
    "Btu_Moist_MMF", "VM_Dry_MMF", "Fixed_C_Dry_MMF",
    "Organic_C", "Carbonate_C", "Total_Carbon",
    "Ash_Deformation", "Ash_Softening", "Ash_Fluid", "Hydrogen", "Nitrogen", "Oxygen",
]

COAL_QUALITY_FEATURE_COLS = [c for e in COAL_QUALITY_FEATURE_BASE for c in (e, f"{e}_Q")]

COAL_QUALITY_COLS_NEEDED = (
    COAL_QUALITY_ID_COLS + COAL_QUALITY_VALIDATION_COLS + COAL_QUALITY_FEATURE_COLS
)


FEATURE_COLS = [
    "GSAsh_Dry", "Si", "Al", "Ca", "Mg", "Na", "K", "Fe", "Ti", "TS", "As", "Mo", "Zn", "P",
    "Moisture", "Volatile_Matter", "Fixed_Carbon", "Standard_Ash", "Carbon", "Sulfur", "Btu",
    "Sulfate_Sulfur", "Pyritic_Sulfur", "Organic_Sulfur", "Btu_Moist_MMF", "VM_Dry_MMF",
    "Fixed_C_Dry_MMF", "Organic_C", "Carbonate_C", "Total_Carbon",
    "Zr", "Sc", "Th", "U", "Nb",
    "Formation", "Region", "Estimated_Rank", "System",
    "Thickness__in_", "Latitude", "Longitude",
    "Ga", "Li", "Ba", "Sr", "V",
    "Ash_Deformation", "Ash_Softening", "Ash_Fluid",
    "Hydrogen", "Nitrogen", "Oxygen",
]

CATEGORICAL_COLS = ["Formation", "Region", "Estimated_Rank", "System"]
LABEL_ELEMENTS = ["Nd", "Pr", "Tb", "Dy"]          # required present to get a tier
PRICE_PER_KG = {
    "Nd": 109.55,
    "Pr": 109.55,
    "Tb": 969.69,
    "Dy": 208.68,
    "Y": 34.82,   # Shanghai Metals Exchange
}


# Chondrite reference values, ppm (McDonough & Sun, 1995) — removes the
# natural odd/even zigzag so the smooth REE trend can be interpolated.
# Ce is included as an interpolation INPUT only, never a target (redox
# anomaly). Y has no atomic-number slot in this series, so it's handled
# separately and never interpolated.
CHONDRITE = {"La": 0.237, "Ce": 0.612, "Pr": 0.095, "Nd": 0.467,
             "Sm": 0.153, "Gd": 0.2055, "Tb": 0.0374, "Dy": 0.254, "Ho": 0.0566}
ATOMIC_NUM = {"La": 57, "Ce": 58, "Pr": 59, "Nd": 60,
              "Sm": 62, "Gd": 64, "Tb": 65, "Dy": 66, "Ho": 67}

TARGETS = ["Pr", "Nd", "Tb", "Dy"]   # core elements eligible to be filled
SERIES_COLS = list(CHONDRITE)        # La..Ho, in atomic-number order


GDB_PATH = Path("ree-and-coal-open-geodatabase.gdb")
ELEMENT_LAYER = "REE0009_Trace_Elements_Data"
QUALITY_LAYER = "REE0008_Proximate_Ultimate_Data"
CLASS_NAMES = ["low", "high"]
RANDOM_STATE = 42
TEST_SIZE = 0.2
MODEL_PARAMS = {
    "objective": "binary:logistic",
    "n_estimators": 500,
    "max_depth": 4,
    "learning_rate": 0.05,
    "eval_metric": "logloss",
    "random_state": RANDOM_STATE,
}
