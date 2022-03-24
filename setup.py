from setuptools import setup, find_packages
import post_install

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
        "textdistance>=4.2",
        "textdistance[extras]",  # With extra libraries for maximum speed
        "pytest>=7",
        "OGER@git+git://github.com/OntoGene/OGER@master#egg=OGER",
        "six>=1.16",  # Needed by python_dateutil-2.8.2-py3.9.egg/dateutil/tz/tz.py
        "requests>=2.26",  # Needed by KGX
        "pyyaml>=5.4",  # Needed by KGX
        "validators>=0.18",  # Needed by KGX
        "bmt>=0.7",  # Needed by KGX
        "ordered_set",  # # Needed by KGX
        "jsonstreams>=0.6",  # Needed by KGX
        "jsonlines>=3",  # Needed by KGX
        "neo4jrestclient>=2.1",  # Needed by KGX
        "ijson>=3.1",  # Needed by KGX
        "linkml-runtime>=1.1",  # Needed by BMT
        "rdflib>=6",  # Needed by linkml-runtime
        "wrapt>=1.13",  # Needed by linkml-runtime
        "pyjsg>=0.11",  # Needed by ShExJSG-0.7.1-py3.9.egg/ShExJSG/ShExJ.py
        "frozendict>=2.1",  # Needed by pyld
        "cachetools>=4.2",  # Needed by pyld
        "spacy>=3.2.0,<3.3.0",  # dictated by scispacy
        "scispacy==0.5.0",
        "scipy==1.7.3",  # required by scispacy
        "conllu>=4.4",  # required by scispacy
        "nmslib>=1.7.3.6",  # required by scispacy
        "pysbd>=0.3",  # required by scispacy
        "dframcy>=0.1",
        "ontobio>=2.7"  # TODO: remove dependency and use alternate method.
        # "en_core_sci_scibert"
        # "en_ner_jnlpba_md",  # Joint wkshp for NLP in Biomedicine & application
        # "en_ner_bc5cdr_md",  # Biocreative V Chemical induce Disease NER
    ],
    dependency_links=[
        # From https://allenai.github.io/scispacy/
        # 1. NER CRAFT corpus
        # 2. SciBERT
        "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_ner_craft_md-0.5.0.tar.gz",
        "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_core_sci_scibert-0.5.0.tar.gz",
    ],
)

post_install.run()
