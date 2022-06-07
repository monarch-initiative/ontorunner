DATA_DIR = data/
INPUT_DIR = $(DATA_DIR)/input
OUTPUT_DIR = $(DATA_DIR)/output/
NODES_AND_EDGES_DIR = $(DATA_DIR)/nodes_and_edges/

# JSON => TSV
$(NODES_AND_EDGES_DIR)/%_nodes.tsv: %.json
	python -m ontorunner.pre.util json2tsv -i $< -o $@

# Prepare termlist
terms/%_termlist.tsv: $(NODES_AND_EDGES_DIR)/%_nodes.tsv
	python -m ontorunner.pre.util prepare-termlist -i $< -o $@

# Run OGER
oger:
	python -m ontorunner.oger_module run-oger -s ontorunner/settings.ini -w 5 -a False

# Run Spacy
spacy:
	python -m ontorunner.spacy_module run-spacy -s ontorunner/settings.ini -a False

# # Create Sphinx Docs
# .PHONY: sphinx
# sphinx:
# 	cd sphinx &&\
# 	find ./ -name "*.rst" -not -name "index.rst" -exec rm {} \; &&\
# 	sphinx-apidoc --ext-autodoc -o . .. &&\
# 	make clean html

# .PHONY: deploy-docs
# deploy-docs:
# 	cp -r sphinx/_build/html/* docs/