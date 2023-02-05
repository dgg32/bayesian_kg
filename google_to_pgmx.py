import pandas as pd
import yaml
import sys
import tsv_to_pgmx

model = sys.argv[1]


with open("config.yaml", "r") as stream:
    try:
        PARAM = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

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


model_nodes = nodes[nodes['model'].notna()]
mask = model_nodes['model'].str.split(";").apply(lambda x: model in [e.strip() for e in x])
model_nodes = model_nodes[mask]

model_links = links[links['model'].notna()]
mask = model_links['model'].str.split(";").apply(lambda x: model in [e.strip() for e in x])
model_links = model_links[mask]

model_potentials = potentials[potentials['model'].notna()]
mask = model_potentials['model'].str.split(";").apply(lambda x: model in [e.strip() for e in x])
model_potentials = model_potentials[mask]

pgmx = tsv_to_pgmx.get_pgmx(model_nodes, model_links, model_potentials)
print (pgmx)