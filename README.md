

# Introduction

  

  

This repository contains code and data for my article "[How to build a Bayesian Knowledge Graph](https://dgg32.medium.com/how-to-build-a-bayesian-knowledge-graph-dee1cc821d35)".

1. The scripts are for data flow between Google Sheets, Neo4j and OpenMarkov.

  

2. The source data folder contains the TSV downloaded from the Google Sheets for debugging purpose. The pgmx_output folder contains TSV files that are extracted from a pgmx file.

  

  

# Prerequisite

Neo4j Desktop

OpenMarkov
  

# Run
First, config the config.yaml to match your Google Sheets setup.
  
1. Convert data from Google Sheets to a pgmx file
```console
python google_to_pgmx.py [model_name] > [model].pgmx
```

For example:
```console
python google_to_pgmx.py Asia > manmade_google.pgmx
```

 
2. Convert data from Google Sheets to Neo4j

```console
python tsv_to_neo4j.py
```
It generates a series of files in the ./neo4j folder.



## Authors

  

*  **Sixing Huang** - *Concept and Coding*

  

## License

  

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
