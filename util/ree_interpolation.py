"""Interpolate missing REE measurements using configured references."""

import pandas as pd

from .config import ATOMIC_NUM, CHONDRITE, SERIES_COLS, TARGETS

def interpolate_row(row):
    norm = pd.Series({e: row[e] / CHONDRITE[e] for e in SERIES_COLS})
    norm.index = [ATOMIC_NUM[e] for e in SERIES_COLS]
    filled = norm.sort_index().interpolate(method="index", limit_area="inside")
    filled.index = SERIES_COLS
    return filled[TARGETS] * pd.Series(CHONDRITE)[TARGETS]

