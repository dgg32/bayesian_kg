import pandas as pd
# Import BeautifulSoup
from bs4 import BeautifulSoup as bs
import os
import sys

output_folder = "pgmx_output"


def save_tsv(records: list, filename: str) -> pd.DataFrame:
    df = pd.DataFrame.from_records(records)
    df.to_csv(os.path.join(output_folder, filename), sep="\t", index=False, na_rep='NULL')
    return df


if __name__ == "__main__":
    pgmx_file = sys.argv[1] if len(sys.argv) > 1 else "manmade.pgmx"

    with open(pgmx_file, "r") as file:
        content = file.read()
    bs_content = bs(content, "xml")

    os.makedirs(output_folder, exist_ok=True)

    nodes = []
    for node in bs_content.find("Variables").find_all("Variable"):
        states = "; ".join([n.get("name") for n in node.find("States").find_all("State")])
        coordinates = node.find("Coordinates")
        x = int(coordinates.get("x")) if coordinates else None
        y = int(coordinates.get("y")) if coordinates else None

        nodes.append({"name": node.get("name"), "type": node.get("type"), "role": node.get("role"), "states": states, "x": x, "y": y})
    save_tsv(nodes, "pgmx_output_nodes.tsv")

    links = []
    for l in bs_content.find("Links").find_all("Link"):
        source, target = [x.get("name") for x in l.find_all("Variable")]
        links.append({"source": source, "target": target})
    save_tsv(links, "pgmx_output_links.tsv")

    potentials = []
    for potential in bs_content.find("Potentials").find_all("Potential"):
        variables = "; ".join([n.get("name") for n in potential.find("Variables").find_all("Variable")])
        values = potential.find("Values").text
        potentials.append({"type": potential.get("type"), "role": potential.get("role"), "variables": variables, "values": values})
    save_tsv(potentials, "pgmx_output_potentials.tsv")
