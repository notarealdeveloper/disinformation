#!/usr/bin/env python

import numpy as np
import pandas as pd

__all__ = [
    "encode_presence_value_jaynes",
    "encode_presence_value_shannon",
]


def to_dataframe(x):
    if isinstance(x, pd.Series):
        name = x.name if x.name is not None else "x"
        return x.to_frame(name=name)
    if isinstance(x, pd.DataFrame):
        return x.copy()
    raise TypeError("expected pandas Series or DataFrame")


def empirical_cdf_signed(s):
    s = pd.to_numeric(s, errors="coerce")
    obs = s.dropna()

    out = pd.Series(np.nan, index=s.index, dtype=float)

    n = len(obs)
    if n == 0:
        return out

    if n == 1:
        out.loc[obs.index] = 0.0
        return out

    ranks = obs.rank(method="average")
    u = (ranks - 1.0) / (n - 1.0)

    out.loc[obs.index] = 2.0 * u - 1.0
    return out


def encode_presence_value_jaynes(df):
    """
    Fully bounded encoding in [-1, 1].

    Value:
        x -> 2 * CDF(x) - 1

    Presence:
        present -> +(1 - p)
        absent  -> -p

    where p = fraction of rows where value is present.
    """

    df = to_dataframe(df)
    out = pd.DataFrame(index=df.index)

    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        m = s.notna()

        p = m.mean()

        # presence encoding
        presence = pd.Series(-p, index=df.index, dtype=float)
        presence.loc[m] = 1.0 - p

        # value encoding via empirical CDF
        value = empirical_cdf_signed(s)

        # missing values --> 0 (neutral center)
        value = value.fillna(0.0)

        out[f"{c}_presence"] = presence
        out[f"{c}_value"] = value

    return out


def encode_presence_value_shannon(
    df,
    lambda_mask=1.0,
    eps=1e-6,
):
    """
    Unbounded / z-score-like encoding.

    Value:
        standard z-score on observed entries
        missing -> 0

    Presence:
        present -> +lambda * sqrt(-log2(p))
        absent  -> -lambda * sqrt(-log2(1 - p))

    Rare events have larger magnitude.
    """

    df = to_dataframe(df)
    out = pd.DataFrame(index=df.index)

    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        m = s.notna()

        # ----- value (true z-score) -----
        obs = s[m]

        if len(obs) == 0:
            z = pd.Series(0.0, index=df.index)
        else:
            mu = obs.mean()
            sigma = obs.std()

            if sigma == 0 or np.isnan(sigma):
                z_obs = obs - mu
            else:
                z_obs = (obs - mu) / sigma

            z = pd.Series(0.0, index=df.index)
            z.loc[m] = z_obs

        # ----- presence (surprisal, signed) -----
        p = m.mean()
        p = min(max(p, eps), 1 - eps)

        w_present = lambda_mask * np.sqrt(-np.log2(p))
        w_absent  = lambda_mask * np.sqrt(-np.log2(1 - p))

        presence = pd.Series(-w_absent, index=df.index, dtype=float)
        presence.loc[m] = w_present

        out[f"{c}_presence"] = presence
        out[f"{c}_value"] = z

    return out
