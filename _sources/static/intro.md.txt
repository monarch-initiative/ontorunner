# ontoRunNER

This is a wrapper project around the following named entity recognition (NER) tools:
 - [OGER](https://github.com/OntoGene/OGER).
 - [spaCy](https://spacy.io)
   - using [sciSpaCy](https://scispacy.apps.allenai.org) pipeline 
   namely the CRAFT corpus (`en_ner_craft_md`) used by default. Others can be used as listed [here](https://github.com/allenai/scispacy#available-models)



## Setup
To setup `ontoRunNER`,
### For developers

After cloning the repository:
```
poetry install
```
### For users

Activate your virtual environment (`poetry` or `conda` or `venv` etc.)
```
pip install ontorunner

pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_ner_craft_md-0.5.0.tar.gz

python -m spacy download en_core_web_sm
```
> Note: If you're using poetry outside of `poetry shell`, precede all CLI commands with a `poetry run`.

## Ontology to [KGX](https://github.com/biolink/kgx) TSV

Generate `nodes.tsv` and `edges.tsv` files from your OBO JSON ontology file,

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

Generate termlist from the `output_nodes.tsv` generated in the previous step.
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

## Running OGER.

> **Note:** Make sure the output directory [`data/output`](https://github.com/monarch-initiative/ontorunner/tree/master/data/output) is empty before every run.

You can run OGER against a text document as follows,

### CLI
```
ontoger run -c abstract.txt -t termlist.tsv -o out.json -f bioc_json
```

> **Note:** This command is just to demonstrate how to OGER.
> For more use cases, [here](https://github.com/OntoGene/OGER/wiki/run)
> is the reference to the OGER documentation.

### Running OGER using a 'settings.ini' file

You can run `OGER` using a 'settings' file as follows,

### CLI
```
ontoger run -s settings.ini
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
ontospacy run
```

### Python
```
from ontorunner import spacy_module
spacy_module.run_spacy()
```
There will be two output tsv files generated:
 - `ontology_ontoRunNER.tsv`: This file is the output with the ontology termlists (generated above) as the dictionary for entity recognition.
 - `umls_ontoRunNER.tsv`: This file is the output derived by using `sciSpaCY`'s `EntityLinker`. By default the linker is `umls` but you can provide others as listed [here](https://github.com/allenai/scispacy#entitylinker).

 ## Visualization using `spaCy.displaCy`.

SpaCy visualizers are also available through ontoRunNER! There are two types of visualizers offered by displaCy:
 - Displays dependencies
 - Highlights entities

Both are rendered using one command - `run-viz`.
 ### CLI
```
ontospacy viz -t "text" 
```

### Python
```
from ontorunner import spacy_module
spacy_module.run_viz("text")
```
 ### Dependency display using displaCy.

 ![Sentence Dependency](../../data/images/example_dependency.svg)

 ### Entity display using displaCy. 

<html>
<div class="entities" style="line-height: 2.5; direction: ltr">
A
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    bacterial
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">TAXON</span>
</mark>
 isolate, designated 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    strain
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">pato-subset</span>
</mark>
 SZ,was obtained from noncontaminated 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    creek
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">envo</span>
</mark>
 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    sediment
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">envo</span>
</mark>
 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    microcosms
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">TAXON</span>
</mark>
 based on its ability to derive 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    energy
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">envo</span>
</mark>
 from 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    acetate
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">CHEBI</span>
</mark>
 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    oxidation
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">mop</span>
</mark>
 coupled to 
<mark class="entity" style="background: #ddd; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    tetrachloroethene
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">mesh_subset</span>
</mark>
.</div>
</html>