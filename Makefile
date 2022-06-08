DATA_DIR = data/
INPUT_DIR = $(DATA_DIR)/input
OUTPUT_DIR = $(DATA_DIR)/output/
NODES_AND_EDGES_DIR = $(DATA_DIR)/nodes_and_edges/
RUN = poetry run

# JSON => TSV
$(NODES_AND_EDGES_DIR)/%_nodes.tsv: %.json
	$(RUN) python -m ontorunner.pre.util json2tsv -i $< -o $@

# Prepare termlist
terms/%_termlist.tsv: $(NODES_AND_EDGES_DIR)/%_nodes.tsv
	$(RUN) python -m ontorunner.pre.util prepare-termlist -i $< -o $@

# Run OGER
oger:
	$(RUN) python -m ontorunner.oger_module run-oger -s ontorunner/settings.ini -w 5 -a False

# Run Spacy
spacy:
	$(RUN) python -m ontorunner.spacy_module run-spacy -s ontorunner/settings.ini -a False

# Update Sphinx *.rst files
sphinx-clean:
	find docs/ -name "*.rst" -type f ! -name "index.rst" -delete

# Re-build sphinx docs
sphinx-gen:
	sphinx-apidoc -o docs/ . --ext-autodoc
	
test:
	$(RUN) python -m ontorunner.oger_module --help