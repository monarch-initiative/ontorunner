from setuptools import setup, find_packages

NAME = "ontoRunNER"
URL = "https://github.com/monarch-initiative/ontorunner"
AUTHOR = "Harshad Hegde"
EMAIL = "hhegde@lbl.gov"
REQUIRES_PYTHON = ">=3.7.0"
VERSION = "0.0.1"
LICENSE = "BSD"

# with open("requirements.txt", "r") as FH:
#     REQUIREMENTS = FH.readlines()

EXTRAS = {}

setup(
    name=NAME,
    author=AUTHOR,
    version=VERSION,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license=LICENSE,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    extras_require=EXTRAS,
    include_package_data=True,
    # add package dependencies
    install_requires=[
        "kgx>=1.5",
        "click>=7.1",
        "pytz",  # required by pandas
        "python-dateutil>=2.8",  # required by pandas
        "pandas>=1.3",
        "sphinx>=2.3",
        "sphinx_rtd_theme>=0.4",
        "recommonmark>=0.7",
        "textdistance",
        "textdistance[extras]",  # With extra libraries for maximum speed
        "pytest",
        "OGER@git+git://github.com/OntoGene/OGER@master#egg=OGER",
        "six",  # Needed by python_dateutil-2.8.2-py3.9.egg/dateutil/tz/tz.py
        "requests",  # Needed by KGX
        "pyyaml",  # Needed by KGX
        "validators",  # Needed by KGX
        "bmt",  # Needed by KGX
        "ordered_set",  # # Needed by KGX
        "jsonstreams",  # Needed by KGX
        "jsonlines",  # Needed by KGX
        "neo4jrestclient",  # Needed by KGX
        "ijson",  # Needed by KGX
        "linkml-runtime",  # Needed by BMT
        "rdflib",  # Needed by linkml-runtime
        "wrapt",  # Needed by linkml-runtime
        "pyjsg",  # Needed by ShExJSG-0.7.1-py3.9.egg/ShExJSG/ShExJ.py
        "frozendict",  # Needed by pyld
        "cachetools",  # Needed by pyld
        "spacy>=3.0.0,<3.1.0",  # dictated by scispacy
        "scispacy",
        "scipy",  # required by scispacy
        "conllu",  # required by scispacy
        "nmslib>=1.7.3.6",  # required by scispacy
        "pysbd",  # required by scispacy
        "dframcy",
        "ontobio"
        # "en_core_sci_scibert"
        # "en_ner_jnlpba_md",  # Joint wkshp for NLP in Biomedicine & application
        # "en_ner_bc5cdr_md",  # Biocreative V Chemical induce Disease NER
    ],
    dependency_links=[
        # From https://allenai.github.io/scispacy/
        # 1. NER CRAFT corpus
        # 2. SciBERT
        "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_ner_craft_md-0.4.0.tar.gz",
        "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_scibert-0.4.0.tar.gz",
    ],
)
