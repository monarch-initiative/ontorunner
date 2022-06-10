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
python -m ontorunner.oger_module run-oger -c abstract.txt -t termlist.tsv -o out.json -f bioc_json
```

> **Note:** This command is just to demonstrate how to OGER.
> For more use cases, [here](https://github.com/OntoGene/OGER/wiki/run)
> is the reference to the OGER documentation.

### Running OGER using a 'settings.ini' file

You can run `OGER` using a 'settings' file as follows,

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
python -m ontorunner.spacy_module run-spacy 
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
python -m ontorunner.spacy_module run-viz -t "text" 
```

### Python
```
from ontorunner import spacy_module
spacy_module.run_viz("text")
```
 ### Dependency display using displaCy.

 ![Sentence Dependency](../../data/images/example_dependency.svg)
 
 <!DOCTYPE html><html lang="en"><head><title>displaCy</title></head><body style="font-size: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; padding: 4rem 2rem; direction: ltr"><figure style="margin-bottom: 6rem"><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="en" id="67bc62a10e664754bbd5a1dd503b153c-0" class="displacy" width="2000" height="399.5" direction="ltr" style="max-width: none; height: 399.5px; color: #000000; background: #ffffff; font-family: Arial; direction: ltr"><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="50">A bacterial isolate,</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="50">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="125">designated</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="125">VERB</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="200"></tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="200">SPACE</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="275">strain</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="275">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="350">SZ,</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="350">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="425">was</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="425">AUX</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="500">obtained</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="500">VERB</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="575">from</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="575">ADP</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="650">noncontaminated</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="650">ADJ</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="725">creek</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="725">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="800"></tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="800">SPACE</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="875">sediment</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="875">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="950">microcosms</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="950">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1025">based</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1025">VERB</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1100">on</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1100">ADP</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1175">its</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1175">PRON</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1250">ability</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1250">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1325">to</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1325">PART</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1400">derive</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1400">VERB</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1475">energy</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1475">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1550">from</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1550">ADP</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1625">acetate</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1625">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1700">oxidation</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1700">NOUN</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1775">coupled</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1775">VERB</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1850">to</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1850">PART</tspan></text><text class="displacy-token" fill="currentColor" text-anchor="middle" y="309.5"><tspan class="displacy-word" fill="currentColor" x="1925">tetrachloroethene.</tspan><tspan class="displacy-tag" dy="2em" fill="currentColor" x="1925">NOUN</tspan></text><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-0" stroke-width="2px" d="M70,264.5 C70,39.5 495.0,39.5 495.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-0" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">nsubjpass</textPath></text><path class="displacy-arrowhead" d="M70,266.5 L62,254.5 78,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-1" stroke-width="2px" d="M70,264.5 C70,227.0 95.0,227.0 95.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-1" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">acl</textPath></text><path class="displacy-arrowhead" d="M95.0,266.5 L103.0,254.5 87.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-2" stroke-width="2px" d="M220,264.5 C220,189.5 325.0,189.5 325.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-2" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">compound</textPath></text><path class="displacy-arrowhead" d="M220,266.5 L212,254.5 228,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-3" stroke-width="2px" d="M295,264.5 C295,227.0 320.0,227.0 320.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-3" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">compound</textPath></text><path class="displacy-arrowhead" d="M295,266.5 L287,254.5 303,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-4" stroke-width="2px" d="M145,264.5 C145,152.0 330.0,152.0 330.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-4" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">xcomp</textPath></text><path class="displacy-arrowhead" d="M330.0,266.5 L338.0,254.5 322.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-5" stroke-width="2px" d="M445,264.5 C445,227.0 470.0,227.0 470.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-5" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">auxpass</textPath></text><path class="displacy-arrowhead" d="M445,266.5 L437,254.5 453,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-6" stroke-width="2px" d="M595,264.5 C595,77.0 940.0,77.0 940.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-6" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">case</textPath></text><path class="displacy-arrowhead" d="M595,266.5 L587,254.5 603,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-7" stroke-width="2px" d="M670,264.5 C670,227.0 695.0,227.0 695.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-7" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">amod</textPath></text><path class="displacy-arrowhead" d="M670,266.5 L662,254.5 678,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-8" stroke-width="2px" d="M745,264.5 C745,152.0 930.0,152.0 930.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-8" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">compound</textPath></text><path class="displacy-arrowhead" d="M745,266.5 L737,254.5 753,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-9" stroke-width="2px" d="M820,264.5 C820,189.5 925.0,189.5 925.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-9" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">compound</textPath></text><path class="displacy-arrowhead" d="M820,266.5 L812,254.5 828,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-10" stroke-width="2px" d="M895,264.5 C895,227.0 920.0,227.0 920.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-10" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">compound</textPath></text><path class="displacy-arrowhead" d="M895,266.5 L887,254.5 903,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-11" stroke-width="2px" d="M520,264.5 C520,39.5 945.0,39.5 945.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-11" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">nmod</textPath></text><path class="displacy-arrowhead" d="M945.0,266.5 L953.0,254.5 937.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-12" stroke-width="2px" d="M520,264.5 C520,2.0 1025.0,2.0 1025.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-12" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">advcl</textPath></text><path class="displacy-arrowhead" d="M1025.0,266.5 L1033.0,254.5 1017.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-13" stroke-width="2px" d="M1120,264.5 C1120,189.5 1225.0,189.5 1225.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-13" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">case</textPath></text><path class="displacy-arrowhead" d="M1120,266.5 L1112,254.5 1128,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-14" stroke-width="2px" d="M1195,264.5 C1195,227.0 1220.0,227.0 1220.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-14" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">nmod:poss</textPath></text><path class="displacy-arrowhead" d="M1195,266.5 L1187,254.5 1203,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-15" stroke-width="2px" d="M1045,264.5 C1045,152.0 1230.0,152.0 1230.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-15" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">nmod</textPath></text><path class="displacy-arrowhead" d="M1230.0,266.5 L1238.0,254.5 1222.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-16" stroke-width="2px" d="M1345,264.5 C1345,227.0 1370.0,227.0 1370.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-16" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">mark</textPath></text><path class="displacy-arrowhead" d="M1345,266.5 L1337,254.5 1353,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-17" stroke-width="2px" d="M1270,264.5 C1270,189.5 1375.0,189.5 1375.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-17" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">acl</textPath></text><path class="displacy-arrowhead" d="M1375.0,266.5 L1383.0,254.5 1367.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-18" stroke-width="2px" d="M1420,264.5 C1420,227.0 1445.0,227.0 1445.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-18" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">dobj</textPath></text><path class="displacy-arrowhead" d="M1445.0,266.5 L1453.0,254.5 1437.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-19" stroke-width="2px" d="M1570,264.5 C1570,189.5 1675.0,189.5 1675.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-19" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">case</textPath></text><path class="displacy-arrowhead" d="M1570,266.5 L1562,254.5 1578,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-20" stroke-width="2px" d="M1645,264.5 C1645,227.0 1670.0,227.0 1670.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-20" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">compound</textPath></text><path class="displacy-arrowhead" d="M1645,266.5 L1637,254.5 1653,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-21" stroke-width="2px" d="M1420,264.5 C1420,114.5 1685.0,114.5 1685.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-21" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">nmod</textPath></text><path class="displacy-arrowhead" d="M1685.0,266.5 L1693.0,254.5 1677.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-22" stroke-width="2px" d="M1720,264.5 C1720,227.0 1745.0,227.0 1745.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-22" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">acl</textPath></text><path class="displacy-arrowhead" d="M1745.0,266.5 L1753.0,254.5 1737.0,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-23" stroke-width="2px" d="M1870,264.5 C1870,227.0 1895.0,227.0 1895.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-23" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">case</textPath></text><path class="displacy-arrowhead" d="M1870,266.5 L1862,254.5 1878,254.5" fill="currentColor"/></g><g class="displacy-arrow"><path class="displacy-arc" id="arrow-67bc62a10e664754bbd5a1dd503b153c-0-24" stroke-width="2px" d="M1795,264.5 C1795,189.5 1900.0,189.5 1900.0,264.5" fill="none" stroke="currentColor"/><text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px"><textPath xlink:href="#arrow-67bc62a10e664754bbd5a1dd503b153c-0-24" class="displacy-label" startOffset="50%" side="left" fill="currentColor" text-anchor="middle">nmod</textPath></text><path class="displacy-arrowhead" d="M1900.0,266.5 L1908.0,254.5 1892.0,254.5" fill="currentColor"/></g></svg></figure></body></html>

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