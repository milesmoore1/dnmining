"""Four below-detection treatments for the REY elements. See CHANGES.md CHANGE 1.

Below-detection ('L') rows in this geodatabase store their own detection limit
(DL) as the reported value; 'N' (not detected) -> 0; 'B' (blank) -> already NaN.

  FACE        value as reported (for L rows this IS the detection limit)
  DL2         DL * 0.5  (Miles's current behavior; N -> 0)
  MARGINAL    per-element left-censored lognormal fit by MLE. Detected values
              contribute their density; each censored value contributes the CDF
              at its own detection limit. Each censored sample is imputed with
              E[X | X < DL_i] under the fitted lognormal.
  JOINT       joint model: for each censored element, a log-linear regression on
              the well-measured elements (Y, Yb, Sc, La) plus ash (GSAsh_Dry) and
              Al (stoichiometric stand-in for Al2O3, which is absent from the
              layer), fit on detected rows. Each censored sample is imputed with
              its conditional truncated mean E[X | X < DL_i, predictors], so
              censored heavies borrow strength from the REE correlation structure.
              NOTE ON NAMING: this is a regression-based approximation of the
              dnmining "joint MVN" model (both borrow the REE correlation
              structure) and behaves like it (Fort Union Dy 1.96 vs their 1.85).
              It is NOT the dnmining "per-element conditional" (independent per-
              element censored regression, their Dy 0.79). Kept national on
              purpose — the map is national and basin-local refits would create
              discontinuities at basin boundaries.
"""

import numpy as np
import pandas as pd
from scipy import optimize
from scipy.stats import norm

REY = ["La", "Ce", "Pr", "Nd", "Sm", "Eu", "Gd", "Tb",
       "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Y", "Sc"]

# Well-measured predictors for the conditional model (Al2O3 absent -> use Al).
CONDITION_ON = ["Y", "Yb", "Sc", "La", "GSAsh_Dry", "Al"]

TREATMENTS = ["FACE", "DL2", "MARGINAL", "JOINT"]


def _flags(df, e):
    q = df[f"{e}_Q"].fillna("").astype(str)
    is_l = q.str.contains(r'(?:^|,)L(?:,|$)', regex=True)
    is_n = q.str.contains(r'(?:^|,)N(?:,|$)', regex=True)
    return is_l, is_n


def _to_num(s):
    return pd.to_numeric(s, errors="coerce")


def _trunc_lognormal_mean_below(mu, sigma, dl):
    """E[X | X < dl] for X ~ Lognormal(mu, sigma) (mu, sigma in log space)."""
    dl = np.asarray(dl, dtype=float)
    a = (np.log(dl) - mu) / sigma
    den = norm.cdf(a)
    num = np.exp(mu + sigma * sigma / 2.0) * norm.cdf(a - sigma)
    out = np.where(den > 1e-12, num / np.maximum(den, 1e-12), dl * 0.5)
    return out


def _fit_censored_lognormal(x_det, dl_cens):
    """MLE of (mu, sigma) in log space from detected values + censoring DLs."""
    logd = np.log(x_det[x_det > 0])
    dl_cens = np.asarray(dl_cens, dtype=float)
    dl_cens = dl_cens[dl_cens > 0]

    def nll(p):
        mu, log_s = p
        s = np.exp(log_s)
        ll = norm.logpdf(logd, mu, s).sum()
        if dl_cens.size:
            ll += norm.logcdf((np.log(dl_cens) - mu) / s).sum()
        return -ll

    mu0 = logd.mean()
    s0 = max(logd.std(ddof=0), 0.1)
    res = optimize.minimize(nll, [mu0, np.log(s0)], method="Nelder-Mead",
                            options={"xatol": 1e-4, "fatol": 1e-4, "maxiter": 2000})
    return res.x[0], float(np.exp(res.x[1]))


def _predictor_matrix(df):
    """Log-space, median-imputed predictor matrix from CONDITION_ON (face values)."""
    cols = []
    for c in CONDITION_ON:
        v = _to_num(df[c]).clip(lower=1e-6)
        lv = np.log(v)
        lv = lv.fillna(lv.median())
        cols.append(lv.rename(c))
    P = pd.concat(cols, axis=1)
    return P


def apply_treatment(df, treatment, elements=REY):
    """Return a copy of df with each REY element replaced by its imputed values
    under `treatment`. Detected values are untouched; N -> 0; B stays NaN."""
    if treatment not in TREATMENTS:
        raise ValueError(f"unknown treatment {treatment!r}; choose from {TREATMENTS}")
    out = df.copy()
    P = _predictor_matrix(df) if treatment == "JOINT" else None

    for e in elements:
        v = _to_num(df[e])
        is_l, is_n = _flags(df, e)
        detected = v.notna() & ~is_l & ~is_n
        col = v.copy()
        col[is_n] = 0.0  # not detected

        if treatment == "FACE":
            pass  # L rows keep the DL as reported
        elif treatment == "DL2":
            col[is_l] = v[is_l] * 0.5
        elif treatment == "MARGINAL":
            x_det = v[detected].to_numpy()
            dl = v[is_l].to_numpy()
            if x_det.size >= 20 and is_l.any():
                mu, sigma = _fit_censored_lognormal(x_det, dl)
                col.loc[is_l] = _trunc_lognormal_mean_below(mu, sigma, dl)
            else:
                col[is_l] = v[is_l] * 0.5  # fallback if too few detects
        elif treatment == "JOINT":
            x_det = v[detected]
            if detected.sum() >= 50 and is_l.any():
                Xd = np.column_stack([np.ones(detected.sum()), P.loc[detected].to_numpy()])
                yd = np.log(x_det.clip(lower=1e-6).to_numpy())
                beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
                resid = yd - Xd @ beta
                sigma = max(resid.std(ddof=Xd.shape[1]), 0.05)
                Xc = np.column_stack([np.ones(is_l.sum()), P.loc[is_l].to_numpy()])
                mu_i = Xc @ beta
                dl = v[is_l].to_numpy()
                col.loc[is_l] = _trunc_lognormal_mean_below(mu_i, sigma, dl)
            else:
                col[is_l] = v[is_l] * 0.5  # fallback

        out[e] = col
    return out


def total_rey(df, elements=REY):
    """Sum of the given elements per row (min_count=1 so all-missing -> NaN)."""
    return df[elements].apply(_to_num).sum(axis=1, min_count=1)
