import pandas as pd
import yaml
import sys
import tsv_to_pgmx
from model_filter import filter_by_model

if len(sys.argv) != 2:
    sys.exit(f"Usage: python {sys.argv[0]} <model_name>")
model = sys.argv[1]

with open("config.yaml", "r") as stream:
    try:
        PARAM = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        sys.exit(f"Failed to parse config.yaml: {exc}")

sheet_id = PARAM["google_sheet_id"]
nodes_sheet = PARAM["google_sheet_node"]
links_sheet = PARAM["google_sheet_link"]
potentials_name = PARAM["google_sheet_potentials"]

nodes_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nodes_sheet}"
nodes = pd.read_csv(nodes_url)

links_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={links_sheet}"
links = pd.read_csv(links_url)

potentials_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={potentials_name}"
potentials = pd.read_csv(potentials_url)

model_nodes = filter_by_model(nodes, model)
model_links = filter_by_model(links, model)
model_potentials = filter_by_model(potentials, model)

if model_nodes.empty:
    print(f"Warning: no nodes found for model '{model}'. Check the spelling in the Google Sheet.", file=sys.stderr)

pgmx = tsv_to_pgmx.get_pgmx(model_nodes, model_links, model_potentials)
print(pgmx)
