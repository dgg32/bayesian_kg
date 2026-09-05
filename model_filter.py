import pandas as pd


def filter_by_model(df: pd.DataFrame, model: str, column: str = "model") -> pd.DataFrame:
    """Keep only the rows of df that belong to the given model.

    The model column holds a ";"-separated list of model names per row
    (a single node/link/potential can belong to several models), so
    membership has to be checked against the split list rather than
    with a plain equality/substring match.

    Args:
        df (pd.DataFrame): dataframe with a column of ";"-separated model names
        model (str): model name to keep
        column (str): name of the column holding the ";"-separated model names

    Returns:
        pd.DataFrame: rows of df whose model column includes `model`
    """
    if column not in df.columns:
        raise KeyError(f"Expected a '{column}' column but found: {list(df.columns)}")

    with_model = df[df[column].notna()]
    # .astype(str) makes this robust to a model column that pandas inferred
    # as numeric (e.g. every model name in the sheet happens to look like a
    # number), where the .str accessor would otherwise raise.
    mask = with_model[column].astype(str).str.split(";").apply(lambda names: model in [n.strip() for n in names])
    return with_model[mask]
