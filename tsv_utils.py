import pandas as pd


def restore_integer_columns(df: pd.DataFrame) -> pd.DataFrame:
    """pandas upcasts a whole-number int column to float64 as soon as it
    contains any NaN (e.g. a coordinate that's blank for non-Bayesian rows
    like Anatomy nodes), turning values like 701 into 701.0 wherever that
    dataframe is next written out. Cast such columns to the nullable Int64
    dtype so they round-trip and export cleanly instead of drifting.
    """
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            non_null = df[col].dropna()
            if not non_null.empty and (non_null % 1 == 0).all():
                df[col] = df[col].astype("Int64")
    return df
