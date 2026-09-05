import os
import sys

import pandas as pd
# Import BeautifulSoup
from bs4 import BeautifulSoup as bs

# Anchor the output folder to this file's location, independent of the
# caller's current working directory.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(BASE_DIR, "pgmx_output")


def _find_all(root, section_name: str, item_tag: str) -> list:
    """bs_content.find(section_name) is None for a PGMX section that is
    simply absent (e.g. a fresh OpenMarkov model with no links yet), so
    calling .find_all on it raises AttributeError. Treat "absent" the same
    as "empty" instead of crashing."""
    section = root.find(section_name)
    return section.find_all(item_tag) if section else []


def _to_int(value):
    if value is None:
        return None
    # OpenMarkov writes plain integers ("214"), but be tolerant of
    # decimal-formatted coordinates ("214.0") from other tools/versions.
    return int(float(value))


def parse_pgmx(bs_content) -> tuple:
    nodes = []
    for node in _find_all(bs_content, "Variables", "Variable"):
        states = "; ".join([n.get("name") for n in node.find("States").find_all("State")])
        coordinates = node.find("Coordinates")
        x = _to_int(coordinates.get("x")) if coordinates else None
        y = _to_int(coordinates.get("y")) if coordinates else None

        nodes.append({"name": node.get("name"), "type": node.get("type"), "role": node.get("role"), "states": states, "x": x, "y": y})

    links = []
    for l in _find_all(bs_content, "Links", "Link"):
        source, target = [x.get("name") for x in l.find_all("Variable")]
        links.append({"source": source, "target": target})

    potentials = []
    for potential in _find_all(bs_content, "Potentials", "Potential"):
        variables = "; ".join([n.get("name") for n in potential.find("Variables").find_all("Variable")])
        values = potential.find("Values").text
        potentials.append({
            "type": (potential.get("type") or "").strip(),
            "role": (potential.get("role") or "").strip(),
            "variables": variables,
            "values": values,
        })

    return nodes, links, potentials


if __name__ == "__main__":
    pgmx_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "manmade.pgmx")

    with open(pgmx_file, "r") as file:
        content = file.read()
    bs_content = bs(content, "xml")

    # Parse all three sections into memory before writing anything. A PGMX
    # that fails to parse (e.g. a malformed <Potentials> block) must not
    # leave pgmx_output/ with a fresh nodes.tsv sitting next to a stale
    # links/potentials.tsv from a previous, unrelated run.
    nodes, links, potentials = parse_pgmx(bs_content)

    os.makedirs(output_folder, exist_ok=True)
    # Pass the expected columns explicitly so a legitimately empty section
    # (e.g. a fresh model with no links yet) still produces a well-formed,
    # header-only TSV instead of a zero-column file that later blows up
    # upsert_tsv.py with pandas.errors.EmptyDataError.
    pd.DataFrame.from_records(nodes, columns=["name", "type", "role", "states", "x", "y"]) \
        .to_csv(os.path.join(output_folder, "pgmx_output_nodes.tsv"), sep="\t", index=False, na_rep='NULL')
    pd.DataFrame.from_records(links, columns=["source", "target"]) \
        .to_csv(os.path.join(output_folder, "pgmx_output_links.tsv"), sep="\t", index=False, na_rep='NULL')
    pd.DataFrame.from_records(potentials, columns=["type", "role", "variables", "values"]) \
        .to_csv(os.path.join(output_folder, "pgmx_output_potentials.tsv"), sep="\t", index=False, na_rep='NULL')
