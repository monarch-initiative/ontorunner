# ontoRunNER

This repository is a wrapper project around the following named entity recognition (NER tools:
 - [OGER](https://github.com/OntoGene/OGER).
 - [spaCy](https://spacy.io)
   - using [sciSpaCy](https://scispacy.apps.allenai.org) pipeline 
   namely the CRAFT corpus (`en_ner_craft_md`) used by default. Others can be used as listed [here](https://github.com/allenai/scispacy#available-models)



## Setup
To setup `ontoRunNER`,
```
python setup.py install
```

## Ontology to [KGX](https://github.com/biolink/kgx) TSV

Generate `nodes.tsv` and `edges.tsv` files from your OBO JSON ontology file,

### CLI
```
poetry run python -m ontorunner.pre.util json2tsv -i ontology.json -o output
```
### Python
```
from ontorunner.pre.util import json2tsv
json2tsv('ontology.json', 'output.tsv')
```

## Preparing term-list

Generate termlist from the `output_nodes.tsv` generated in the previous step.
### CLI
The conversion can be done as follows,
```
poetry run python -m ontorunner.pre.util prepare-termlist -i output_nodes.tsv -o termlist.tsv
```

### Python
```
from ontorunner.pre.util import prepare_termlist
prepare_termlist('output_nodes.tsv', 'termlist.tsv')
```

## Running OGER.

> **Note:** Make sure the output directory [`data/output`](https://github.com/monarch-initiative/ontorunner/tree/master/data/output) is empty before every run.

You can run OGER against a text document as follows,

### CLI
```
poetry run python -m ontorunner.oger_module run-oger -c abstract.txt -t termlist.tsv -o out.json -f bioc_json
```

> **Note:** This command is just to demonstrate how to OGER.
> For more use cases, [here](https://github.com/OntoGene/OGER/wiki/run)
> is the reference to the OGER documentation.

### Running OGER using a 'settings.ini' file

You can run `OGER` using a 'settings' file as follows,

### CLI
```
poetry run python -m ontorunner.oger_module run-oger -s settings.ini
```

### Python
```
from ontorunner import oger_module
oger_module.run_oger(settings=settingsFile)
```
> The [settings.ini](https://github.com/monarch-initiative/ontorunner/blob/master/ontorunner/settings.ini) file provides all relevant arguments to OGER. More information on the parameter list could be found at the [OGER GitHub](https://github.com/OntoGene/OGER/wiki/run#parameter-index)

There will be two output tsv files generated:
 - An output whose filename is exactly similar to the input filename (say `docs.tsv`)
     - This is the pure output from `OGER`
 - Another file named `docs_ontoRunNER.tsv` which contains more results because it is the outcome of some postprocessing.

## Running spaCy.
For now, `spaCy` (within `ontoRunNER`) can only process documents prepared as a tsv 
(or multiple tsv) file(s) with two columns:
 - id
 - text

By default, these files are expected to be in the [`data/input`](https://github.com/monarch-initiative/ontorunner/tree/master/data/input) directory. If not, then the user can provide the path of the data directory using the `-d` or `--data-dir` parameter.

The `settings.ini` file used in `OGER` above is also used by `spaCy` for some of its parameters.
 ### CLI
```
poetry run python -m ontorunner.spacy_module run-spacy 
```

### Python
```
from ontorunner import spacy_module
spacy_module.run_spacy()
```
There will be two output tsv files generated:
 - `ontology_ontoRunNER.tsv`: This file is the output with the ontology termlists (generated above) as the dictionary for entity recognition.
 - `umls_ontoRunNER.tsv`: This file is the output derived by using `sciSpaCY`'s `EntityLinker`. By default the linker is `umls` but you can provide others as listed [here](https://github.com/allenai/scispacy#entitylinker).