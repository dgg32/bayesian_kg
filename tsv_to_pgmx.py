import os
import sys

import pandas as pd
from jinja2 import Environment, FileSystemLoader

from model_filter import filter_by_model

# Anchor all paths to this file's location so the scripts behave the same
# regardless of the caller's current working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_loader = FileSystemLoader(os.path.join(BASE_DIR, "templates"))
# autoescape=True is required even though this is XML, not HTML: without it
# a node/state name containing "&", "<", "\"", etc. (all legal in a Google
# Sheet) is written raw into an attribute value and produces a PGMX file
# that no XML parser (including OpenMarkov's) can read.
env = Environment(loader=file_loader, autoescape=True)
template = env.get_template('unicriterion_pgmx.txt')


def _require(value, node_name: str, field: str):
    """Raise a clear error instead of letting a NaN silently render as the
    literal text "nan" in the generated PGMX (invalid for OpenMarkov)."""
    if pd.isna(value):
        raise ValueError(f"Node '{node_name}' is missing its '{field}' value in nodes.tsv")
    return value


def get_pgmx(nodes_df: pd.DataFrame, links_df: pd.DataFrame, potentials_df: pd.DataFrame) -> str:
    """
    Args:
        nodes_df (pd.DataFrame): pandas dataframe with columns: name, type, role, states
        links_df (pd.DataFrame): pandas dataframe with columns: source, target
        potentials_df (pd.DataFrame): pandas dataframe with columns: type, role, variables, values

    Returns:
        str: pgmx file
    """

    nodes_to_jinja = []
    for position, (_, row) in enumerate(nodes_df.iterrows()):
        name = row["name"]
        states_raw = _require(row["states"], name, "states")
        states = [x.strip() for x in states_raw.split(";")]

        # Fall back to a simple diagonal layout when a node has no
        # explicit coordinates. Use the enumeration position rather than
        # the (possibly sparse, non-sequential) dataframe index so that
        # nodes still end up laid out close together.
        x = 1 + position * 100
        y = 1 + position * 100

        if "x" in row and pd.notna(row["x"]):
            x = int(row["x"])
        if "y" in row and pd.notna(row["y"]):
            y = int(row["y"])

        nodes_to_jinja.append({
            "name": name,
            "type": _require(row["type"], name, "type"),
            "role": _require(row["role"], name, "role"),
            "states": states,
            "x": x,
            "y": y,
        })

    links_to_jinja = []
    for _, row in links_df.iterrows():
        links_to_jinja.append({"source": row["source"], "target": row["target"]})

    potentials_to_jinja = []
    for _, row in potentials_df.iterrows():
        variables = [x.strip() for x in row["variables"].split(";")]
        values = row["values"]
        if isinstance(values, str) and "," in values:
            print(
                f"Warning: potential for {variables} has a comma in its values "
                "(expected space-separated numbers) — OpenMarkov may misread the table.",
                file=sys.stderr,
            )
        potentials_to_jinja.append({
            "type": row["type"].strip(),
            "role": row["role"].strip(),
            "variables": variables,
            "value": values,
        })

    output = template.render(nodes=nodes_to_jinja, links=links_to_jinja, potentials=potentials_to_jinja)
    return output


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: python {sys.argv[0]} <model_name>")
    model = sys.argv[1]

    nodes = pd.read_csv(os.path.join(BASE_DIR, "source", "nodes.tsv"), sep="\t")
    links = pd.read_csv(os.path.join(BASE_DIR, "source", "links.tsv"), sep="\t")
    potentials = pd.read_csv(os.path.join(BASE_DIR, "source", "potentials.tsv"), sep="\t")

    model_nodes = filter_by_model(nodes, model)
    model_links = filter_by_model(links, model)
    model_potentials = filter_by_model(potentials, model)

    if model_nodes.empty:
        print(f"Warning: no nodes found for model '{model}'. Check the spelling in source/nodes.tsv.", file=sys.stderr)

    pgmx = get_pgmx(model_nodes, model_links, model_potentials)
    print(pgmx)
