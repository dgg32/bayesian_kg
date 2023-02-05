import pandas as pd
import sys
import os

def upsert_df (df: pd.DataFrame, old_df: pd.DataFrame, key: str):
    """
    Args:
        df (pd.DataFrame): pandas dataframe with columns: name, type, role, states
        old_df (pd.DataFrame): pandas dataframe with columns: source, target
        key (str): key to use for upsert

    Returns:
        pd.DataFrame: combined dataframe
    """
    df = df.set_index(key)
    old_df = old_df.set_index(key)
    combined = df.combine_first(old_df)
    return combined

if __name__ == "__main__":
    # list of strings
    files = {"potentials": "variables", "nodes": "name", "links": ["source", "target"]}
    for f in files:
        old_df_file = os.path.join("./source", f"{f}.tsv")
        new_df_file = os.path.join("./pgmx_output", f"pgmx_output_{f}.tsv")

        old_df = pd.read_csv(old_df_file, sep="\t")
        new_df = pd.read_csv(new_df_file, sep="\t")

        combined = upsert_df(new_df, old_df, files[f])
        combined.to_csv(old_df_file, sep="\t", na_rep='NULL')

    