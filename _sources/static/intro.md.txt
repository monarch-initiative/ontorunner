# ontoRunNER

This repository contains a few accessory scripts for
parsing a KGX generated nodes TSV into a term list
that is compatible with [OGER](https://github.com/OntoGene/OGER).

The long term goal is to build term list inputs for
NER tools in addition to OGER.

## Setup
To setup ontoRunNER,
```
python setup.py install
```

## Ontology to KGX TSV

To generate a TSV from your OBO JSON ontology,

### CLI
```
python -m ontorunner.pre.util json2tsv -i ontology.json -o output
```
### Python
```
from ontorunner.pre.util import json2tsv
json2tsv('ontology.json', 'output.tsv')
```

## Preparing term-list

### CLI
The conversion can be done as follows,
```
python -m ontorunner.pre.util prepare-termlist -i output_nodes.tsv -o termlist.tsv
```

### Python
```
from ontorunner.pre.util import prepare_termlist
prepare_termlist('output_nodes.tsv', 'termlist.tsv')
```

## Running OGER on a document

You can run OGER against a text document as follows,

### CLI
```
python -m ontorunner.oger_module run-oger -c abstract.txt -t termlist.tsv -o out.json -f bioc_json
```

> **Note:** This command is just to demonstrate how to OGER.
> For more complex use cases, it is advised to run OGER
> as recommended [here](https://github.com/OntoGene/OGER/wiki/run).

## Running OGER using a 'settings.ini' file

You can run OGER using a 'settings' file as follows,

### CLI
```
python -m ontorunner.oger_module run-oger -s settings.ini
```

### Python
```
from ontorunner import oger_module
oger_module.run_oger(settings=settingsFile)
```
> The [settings.ini](https://github.com/monarch-initiative/ontorunner/blob/master/ontorunner/settings.ini) file provides all relevant arguments to OGER. More information on the parameter list could be found at the [OGER GitHub](https://github.com/OntoGene/OGER/wiki/run#parameter-index)
