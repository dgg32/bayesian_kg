import pandas as pd
from jinja2 import Environment, FileSystemLoader
import sys

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
    for i, row in nodes_df.iterrows():
 
        states = [x.strip() for x in row.states.split(";")]
        x = 1+ i * 100
        y = 1+ i * 100

        if "x" in row and row["x"]:
            x = int(row["x"])
        if "y" in row and row["y"]:
            y = int(row["y"])


        nodes_to_jinja.append({"name": row["name"], "type": row.type, "role": row.role, "states": states, "x": x, "y": y})


    links_to_jinja = []
    for i, row in links_df.iterrows():
        
        links_to_jinja.append({"source": row["source"], "target": row.target})



    potentials_to_jinja = []
    for i, row in potentials_df.iterrows():
        variables = [x.strip() for x in row.variables.split(";")]
        potentials_to_jinja.append({"type": row["type"], "role": row.role, "variables": variables, "value": row["values"]})

    #print (potentials_to_jinja)

    output = template.render(nodes=nodes_to_jinja, links = links_to_jinja, potentials = potentials_to_jinja)
    return (output)

if __name__ == "__main__":
    model = sys.argv[1]

    nodes = pd.read_csv("./source/nodes.tsv", sep="\t")
    links = pd.read_csv("./source/links.tsv", sep="\t")
    potentials = pd.read_csv("./source/potentials.tsv", sep="\t")

    

    model_nodes = nodes[nodes['model'].notna()]
    mask = model_nodes['model'].str.split(";").apply(lambda x: model in [e.strip() for e in x])
    model_nodes = model_nodes[mask]

    
    
    model_links = links[links['model'].notna()]
    mask = model_links['model'].str.split(";").apply(lambda x: model in [e.strip() for e in x])
    model_links = model_links[mask]

    model_potentials = potentials[potentials['model'].notna()]
    mask = model_potentials['model'].str.split(";").apply(lambda x: model in [e.strip() for e in x])
    model_potentials = model_potentials[mask]

    #print (model_potentials.head())

    pgmx = get_pgmx(model_nodes, model_links, model_potentials)
    print (pgmx)