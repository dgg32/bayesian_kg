import os

import pandas as pd

from tsv_utils import restore_integer_columns

# Anchor the output folder to this file's location, independent of the
# caller's current working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(BASE_DIR, "neo4j")


def to_neo4j(nodes_df: pd.DataFrame, links_df: pd.DataFrame):
    """
    Args:
        nodes_df (pd.DataFrame): pandas dataframe with columns: name, type, role, states, label
        links_df (pd.DataFrame): pandas dataframe with columns: source, target, label

    Returns:
    """
    for df, kind in ((nodes_df, "nodes"), (links_df, "links")):
        if "label" not in df.columns:
            raise KeyError(
                f"The {kind} sheet/TSV has no 'label' column — add one so each row "
                "can be routed to the right Neo4j import file."
            )

    # A column with any blank cell (e.g. x/y for non-Bayesian Anatomy rows)
    # gets read/inferred as float64, so a clean integer coordinate like 701
    # would otherwise be exported to Neo4j as "701.0".
    nodes_df = restore_integer_columns(nodes_df)
    links_df = restore_integer_columns(links_df)

    os.makedirs(output_folder, exist_ok=True)

    node_labels = nodes_df['label'].dropna().unique()

    for l in node_labels:
        temp_df = nodes_df[nodes_df['label'] == l]
        # Empty string (not the literal text "NULL") for blank cells: these
        # TSVs are LOAD CSV'd straight into Neo4j property values, and
        # "NULL" would land in the graph as a real, permanent four-character
        # string rather than an absent property.
        temp_df.to_csv(os.path.join(output_folder, l.lower() + ".tsv"), sep="\t", index=False, na_rep='')

    link_labels = links_df['label'].dropna().unique()

    for l in link_labels:
        temp_df = links_df[links_df['label'] == l]
        temp_df.to_csv(os.path.join(output_folder, l.lower() + ".tsv"), sep="\t", index=False, na_rep='')


if __name__ == "__main__":

    nodes = pd.read_csv(os.path.join(BASE_DIR, "source", "nodes.tsv"), sep="\t")
    links = pd.read_csv(os.path.join(BASE_DIR, "source", "links.tsv"), sep="\t")

    to_neo4j(nodes, links)
