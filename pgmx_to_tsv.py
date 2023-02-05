import pandas as pd
# Import BeautifulSoup
from bs4 import BeautifulSoup as bs
import os

content = []

# Read the XML file
with open("manmade.pgmx", "r") as file:
    # Read each line in the file, readlines() returns a list of lines
    content = file.readlines()
# Combine the lines in the list into a string
content = "".join(content)
bs_content = bs(content, "xml")

nodes = []
for node in bs_content.find("Variables").find_all("Variable"):
    states = "; ".join([n.get("name") for n in node.find("States").find_all("State")])
    x = int(node.find("Coordinates").get("x"))
    y = int(node.find("Coordinates").get("y"))

    nodes.append({"name": node.get("name"), "type": node.get("type"), "role": node.get("role"), "states": states, "x": x, "y": y})
    #print (node)
df = pd.DataFrame.from_records(nodes)
df.to_csv(os.path.join("pgmx_output", "pgmx_output_nodes.tsv"), sep="\t", index=False, na_rep='NULL')


links = []
for l in bs_content.find("Links").find_all("Link"):
    
    source, target = [x.get("name") for x in l.find_all("Variable")]

    links.append({"source": source, "target": target})
    
df = pd.DataFrame.from_records(links)
df.to_csv(os.path.join("pgmx_output", "pgmx_output_links.tsv"), sep="\t", index=False, na_rep='NULL')


potentials = []
for potential in bs_content.find("Potentials").find_all("Potential"):
    variables = "; ".join([n.get("name") for n in potential.find("Variables").find_all("Variable")])
    values = potential.find("Values").text
    potentials.append({"type": potential.get("type"), "role": potential.get("role"), "variables": variables, "values": values})
    
df = pd.DataFrame.from_records(potentials)
df.to_csv(os.path.join("pgmx_output", "pgmx_output_potentials.tsv"), sep="\t", index=False, na_rep='NULL')
