import pandas as pd
import sys
import os
from typing import List, Union


def _restore_integer_columns(df: pd.DataFrame) -> pd.DataFrame:
    """combine_first() upcasts whole int columns to float64 as soon as they
    contain any NaN (e.g. missing x/y coordinates), turning values like 701
    into 701.0 in the saved TSV. Cast such columns to the nullable Int64
    dtype so they round-trip cleanly instead of drifting on every upsert.
    """
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            non_null = df[col].dropna()
            if not non_null.empty and (non_null % 1 == 0).all():
                df[col] = df[col].astype("Int64")
    return df


def upsert_df(df: pd.DataFrame, old_df: pd.DataFrame, key: Union[str, List[str]]) -> pd.DataFrame:
    """
    Args:
        df (pd.DataFrame): new data, e.g. freshly extracted from a pgmx file
        old_df (pd.DataFrame): existing data to be updated, e.g. source/nodes.tsv
        key (str | List[str]): column(s) to match rows on

    Returns:
        pd.DataFrame: old_df with rows from df overlaid on top (matched by key)
    """
    df = df.set_index(key)
    old_df = old_df.set_index(key)
    combined = df.combine_first(old_df)
    return _restore_integer_columns(combined)


if __name__ == "__main__":
    # maps each source file to the key column(s) used to match old and new rows
    files = {"potentials": "variables", "nodes": "name", "links": ["source", "target"]}
    for f, key in files.items():
        old_df_file = os.path.join("./source", f"{f}.tsv")
        new_df_file = os.path.join("./pgmx_output", f"pgmx_output_{f}.tsv")

        old_df = pd.read_csv(old_df_file, sep="\t")
        new_df = pd.read_csv(new_df_file, sep="\t")

        combined = upsert_df(new_df, old_df, key)
        combined.to_csv(old_df_file, sep="\t", na_rep='NULL')
