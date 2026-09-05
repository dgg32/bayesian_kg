import pandas as pd
from jinja2 import Environment, FileSystemLoader
import sys

from model_filter import filter_by_model

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
template = env.get_template('unicriterion_pgmx.txt')


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

        states = [x.strip() for x in row["states"].split(";")]

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
            "name": row["name"],
            "type": row["type"],
            "role": row["role"],
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
        potentials_to_jinja.append({
            "type": row["type"].strip(),
            "role": row["role"].strip(),
            "variables": variables,
            "value": row["values"],
        })

    output = template.render(nodes=nodes_to_jinja, links=links_to_jinja, potentials=potentials_to_jinja)
    return output


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: python {sys.argv[0]} <model_name>")
    model = sys.argv[1]

    nodes = pd.read_csv("./source/nodes.tsv", sep="\t")
    links = pd.read_csv("./source/links.tsv", sep="\t")
    potentials = pd.read_csv("./source/potentials.tsv", sep="\t")

    model_nodes = filter_by_model(nodes, model)
    model_links = filter_by_model(links, model)
    model_potentials = filter_by_model(potentials, model)

    if model_nodes.empty:
        print(f"Warning: no nodes found for model '{model}'. Check the spelling in source/nodes.tsv.", file=sys.stderr)

    pgmx = get_pgmx(model_nodes, model_links, model_potentials)
    print(pgmx)
