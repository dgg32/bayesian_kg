import pandas as pd
import os


output_folder = "./neo4j"

def to_neo4j(nodes_df: pd.DataFrame, links_df: pd.DataFrame):
    """
    Args:
        nodes_df (pd.DataFrame): pandas dataframe with columns: name, type, role, states
        links_df (pd.DataFrame): pandas dataframe with columns: source, target

    Returns:
    """

    node_labels = pd.unique(nodes_df['label'])

    for l in node_labels:
        temp_df = nodes_df[nodes_df['label'] == l]
        temp_df.to_csv(os.path.join(output_folder, l.lower() + ".tsv"), sep="\t", index=False, na_rep='NULL')

    link_labels = pd.unique(links_df['label'])

    for l in link_labels:
        temp_df = links_df[links_df['label'] == l]
        temp_df.to_csv(os.path.join(output_folder, l.lower() + ".tsv"), sep="\t", index=False, na_rep='NULL')


if __name__ == "__main__":

    nodes = pd.read_csv("./source/nodes.tsv", sep="\t")
    links = pd.read_csv("./source/links.tsv", sep="\t")

    to_neo4j(nodes, links)