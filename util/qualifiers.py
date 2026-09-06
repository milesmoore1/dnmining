"""Apply the notebook's existing measurement-qualifier substitutions."""

def resolve_qualifiers(df, columns, substitute="half"):
    factor = {"half": 0.5, "zero": 0.0, "full": 1.0}[substitute]
    df = df.copy()
    for col in columns:
        q_col = f"{col}_Q"
        if q_col not in df.columns:
            continue
        codes = df[q_col].fillna("")
        is_l = codes.str.contains(r'(?:^|,)L(?:,|$)', regex=True)
        is_n = codes.str.contains(r'(?:^|,)N(?:,|$)', regex=True)
        df.loc[is_l, col] = df.loc[is_l, col] * factor
        df.loc[is_n, col] = 0
    return df

