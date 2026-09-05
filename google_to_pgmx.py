import os
import sys
from urllib.parse import quote

import pandas as pd
import yaml

import tsv_to_pgmx
from model_filter import filter_by_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _read_sheet(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    # Sheet names can contain spaces ("has symptom"), which must be
    # URL-encoded or the gviz request comes back malformed/404.
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={quote(sheet_name)}"
    try:
        return pd.read_csv(url)
    except Exception as exc:
        sys.exit(
            f"Failed to fetch the '{sheet_name}' sheet from Google Sheets ({exc}). "
            "Check google_sheet_id/google_sheet_node/google_sheet_link/google_sheet_potentials "
            "in config.yaml, that the sheet is shared as 'Anyone with the link', and your network connection."
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: python {sys.argv[0]} <model_name>")
    model = sys.argv[1]

    with open(os.path.join(BASE_DIR, "config.yaml"), "r") as stream:
        try:
            PARAM = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            sys.exit(f"Failed to parse config.yaml: {exc}")

    nodes = _read_sheet(PARAM["google_sheet_id"], PARAM["google_sheet_node"])
    links = _read_sheet(PARAM["google_sheet_id"], PARAM["google_sheet_link"])
    potentials = _read_sheet(PARAM["google_sheet_id"], PARAM["google_sheet_potentials"])

    model_nodes = filter_by_model(nodes, model)
    model_links = filter_by_model(links, model)
    model_potentials = filter_by_model(potentials, model)

    if model_nodes.empty:
        print(f"Warning: no nodes found for model '{model}'. Check the spelling in the Google Sheet.", file=sys.stderr)

    pgmx = tsv_to_pgmx.get_pgmx(model_nodes, model_links, model_potentials)
    print(pgmx)
