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
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    extras_require=EXTRAS,
    include_package_data=True,
    # add package dependencies
    install_requires=[
        "kgx",
        "click",
        "pandas",
        "sphinx",
        "sphinx_rtd_theme",
        "recommonmark",
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
        "jsonstreams",  # NEeded by KGX
        "jsonlines",  # Needed by KGX
        "neo4jrestclient",  # Needed by KGX
        "ijson",  # Needed by KGX
        "linkml-runtime",  # Needed by BMT
        "rdflib",  # Needed by linkml-runtime
        "wrapt",  # Needed by linkml-runtime
        "pyjsg",  # Needed by ShExJSG-0.7.1-py3.9.egg/ShExJSG/ShExJ.py
        "frozendict",  # Needed by pyld
        "cachetools",  # Needed by pyld
    ],
)
