# Prepare termlist
terms/%_termlist.tsv: data/output/%_nodes.tsv
	python -m runner.runner prepare-termlist -i $< -o $@

# Run OGER
data/output/runNER_Output.tsv: data/input/%.tsv
	python -m runner.runner run-oger -s runner/settings.ini

# Create Sphinx Docs
.PHONY: sphinx
sphinx:
	cd sphinx &&\
	find ./ -name "*.rst" -not -name "index.rst" -exec rm {} \;
	sphinx-apidoc --ext-autodoc -o . ..
	make clean html

.PHONY: deploy-docs
deploy-docs:
	cp -r sphinx/_build/html/* docs/