import pandas as pd
import tsv_to_neo4j
import yaml

output_folder = "./neo4j"


with open("config.yaml", "r") as stream:
    try:
        PARAM = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

if __name__ == "__main__":
    sheet_id = PARAM["google_sheet_id"]
    nodes_sheet = PARAM["google_sheet_node"]
    links_sheet = PARAM["google_sheet_link"]
    potentials_name = PARAM["google_sheet_potentials"]

    nodes_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={nodes_sheet}"
    nodes = pd.read_csv(nodes_url)

    links_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={links_sheet}"
    links = pd.read_csv(links_url)

    tsv_to_neo4j.to_neo4j(nodes, links)