"""Setup parameters."""
import subprocess
from ontorunner import __version__
from setuptools import find_packages, setup
from setuptools.command.install import install

NAME = "ontoRunNER"
URL = "https://github.com/monarch-initiative/ontorunner"
AUTHOR = "Harshad Hegde"
EMAIL = "hhegde@lbl.gov"
REQUIRES_PYTHON = ">=3.8.0"
VERSION = __version__
LICENSE = "MIT"

# with open("requirements.txt", "r") as FH:
#     REQUIREMENTS = FH.readlines()


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        url = "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_ner_craft_md-0.5.0.tar.gz"
        commands = [
            ["pip", "install", url],
            ["python", "-m", "spacy", "download", "en_core_web_sm"],
        ]

        """Run these commands after dependency installation."""
        for command in commands:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            stdout, stderr = process.communicate()
            print(stderr)
            print(stdout)


EXTRAS = {
    "docs": ["sphinx>=2.3", "sphinx_rtd_theme>=0.4", "recommonmark>=0.7"]
}

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
        "textdistance>=4.2",
        "textdistance[extras]",  # With extra libraries for maximum speed
        "pytest>=7",
        "oger",
        "six>=1.16",  # Needed by python_dateutil-2.8.2-py3.9
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
        "dframcy>=0.1"
        # "en_core_sci_scibert"
        # "en_ner_jnlpba_md",  # Joint wkshp for NLP in Biomedicine & app
        # "en_ner_bc5cdr_md",  # Biocreative V Chemical induce Disease NER
    ],
    # dependency_links=[
    # From https://allenai.github.io/scispacy/
    # 1. NER CRAFT corpus
    # "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_ner_craft_md-0.5.0.tar.gz",
    # 2. SciBERT
    # "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.0/en_core_sci_scibert-0.5.0.tar.gz",
    # ],
    cmdclass={
        "install": PostInstallCommand,
    },
)
