import os
import sys
from typing import List, Union

import pandas as pd

from tsv_utils import restore_integer_columns

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def upsert_df(df: pd.DataFrame, old_df: pd.DataFrame, key: Union[str, List[str]], label: str = "rows") -> pd.DataFrame:
    """
    This is an upsert, not a sync: rows are only ever added or overwritten,
    never removed. A row deleted upstream (e.g. in OpenMarkov) stays in
    old_df forever — that's a deliberate, conservative choice (nothing gets
    silently deleted), but it means the printed summary below is the only
    signal that a row you expected to disappear is still there.

    Args:
        df (pd.DataFrame): new data, e.g. freshly extracted from a pgmx file
        old_df (pd.DataFrame): existing data to be updated, e.g. source/nodes.tsv
        key (str | List[str]): column(s) to match rows on
        label (str): human-readable name for this dataset, used in log messages

    Returns:
        pd.DataFrame: old_df with rows from df overlaid on top (matched by key)
    """
    df = df.set_index(key)
    old_df = old_df.set_index(key)

    added_keys = [k for k in df.index if k not in old_df.index]
    stale_keys = [k for k in old_df.index if k not in df.index]
    matched = len(df.index) - len(added_keys)
    print(
        f"{label}: {matched} matched, {len(added_keys)} added, "
        f"{len(stale_keys)} present only in the old file (kept, not deleted)",
        file=sys.stderr,
    )

    combined = df.combine_first(old_df)

    # combine_first() returns rows sorted by the union of both indexes and
    # puts new-df columns before old-only columns, so a normal diff (or a
    # PGMX regenerated afterwards) reports the whole file as changed even
    # when nothing meaningful moved. Restore the original file's row and
    # column order instead.
    row_order = list(old_df.index) + added_keys
    combined = combined.reindex(row_order)
    column_order = list(old_df.columns) + [c for c in combined.columns if c not in old_df.columns]
    combined = combined[column_order]

    # A row that only exists in df (e.g. a node newly drawn in OpenMarkov,
    # which has no concept of "label"/"model"/"description") will be NaN in
    # every column that only old_df carries. Such a row is later dropped
    # silently by filter_by_model() and/or lands in Neo4j with model=NULL,
    # so flag it here instead.
    meta_only_columns = [c for c in old_df.columns if c not in df.columns]
    if meta_only_columns:
        for k in added_keys:
            missing = [c for c in meta_only_columns if pd.isna(combined.loc[k, c])]
            if missing:
                print(
                    f"Warning: new {label} row {k!r} has no {missing} — fill these in "
                    "manually, or it may be silently excluded from generated models/Neo4j.",
                    file=sys.stderr,
                )

    return restore_integer_columns(combined)


if __name__ == "__main__":
    # maps each source file to the key column(s) used to match old and new rows
    files = {"potentials": "variables", "nodes": "name", "links": ["source", "target"]}
    for f, key in files.items():
        old_df_file = os.path.join(BASE_DIR, "source", f"{f}.tsv")
        new_df_file = os.path.join(BASE_DIR, "pgmx_output", f"pgmx_output_{f}.tsv")

        old_df = pd.read_csv(old_df_file, sep="\t")
        new_df = pd.read_csv(new_df_file, sep="\t")

        combined = upsert_df(new_df, old_df, key, label=f)
        combined.to_csv(old_df_file, sep="\t", na_rep='NULL')
