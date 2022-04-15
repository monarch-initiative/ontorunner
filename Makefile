# Create required dirs


# Prepare termlist
terms/%_termlist.tsv: data/output/%_nodes.tsv
	python -m ontorunner.oger_module prepare-termlist -i $< -o $@

# Run OGER
data/output/ontoRunNER_Output.tsv: data/input/%.tsv
	python -m ontorunner.oger_module run-oger -s ontorunner/settings.ini

# Create Sphinx Docs
.PHONY: sphinx
sphinx:
	cd sphinx &&\
	find ./ -name "*.rst" -not -name "index.rst" -exec rm {} \; &&\
	sphinx-apidoc --ext-autodoc -o . .. &&\
	make clean html

.PHONY: deploy-docs
deploy-docs:
	cp -r sphinx/_build/html/* docs/