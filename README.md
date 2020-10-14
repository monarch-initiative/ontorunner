# runNER

This repository contains a few accessory scripts for
parsing a KGX generated nodes TSV into a term list
that is compatible with [OGER](https://github.com/OntoGene/OGER).

The long term goal is to build term list inputs for
NER tools in addition to OGER.

## Ontology to KGX TSV

To generate a TSV from your OBO JSON ontology,
```
kgx transform ontology.json --input-format obojson --output output --output-format tsv 
```

## Preparing term-list

The conversion can be done as follows,
```
python runner.py prepare-termlist -i output_nodes.tsv -o termlist.tsv
```

## Running OGER on a document

You can run OGER against a text document as follows,
```
python runner.py run-oger abstract.txt -t termlist.tsv -o out.json -f bioc_json
```

> **Note:** This command is just to demonstrate how to OGER.
> For more complex use cases, it is advised to run OGER
> as recommended [here](https://github.com/OntoGene/OGER/wiki/run).

