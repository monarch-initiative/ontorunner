"""Constants."""

import os
import configparser
import re

# import pathlib

# HERE = pathlib.Path(__file__).parent.resolve()
PARENT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir)
)
DATA_DIR = os.path.join(PARENT_DIR, "data")
TERMS_DIR = os.path.join(DATA_DIR, "terms")
SERIAL_DIR = os.path.join(DATA_DIR, "serialized")
ONTO_TERMS_FILENAME = "onto_termlist.tsv"
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.ini")
COMBINED_ONTO_FILE = os.path.join(TERMS_DIR, ONTO_TERMS_FILENAME)
COMBINED_ONTO_PICKLED_FILE = os.path.join(
    SERIAL_DIR, ONTO_TERMS_FILENAME + ".pickle"
)
CUSTOM_PIPE_DIR = os.path.join(SERIAL_DIR, "OntoExtractor")
TERMS_PICKLED = os.path.join(SERIAL_DIR, "terms.pickle")
DOCS_PICKLED = os.path.join(SERIAL_DIR, "docs.pickle")
PATTERN_LIST_PICKLED = os.path.join(SERIAL_DIR, "patterns.pickle")
OBJ_DOC_LIST_PICKLED = os.path.join(SERIAL_DIR, "object_docs.pickle")


def get_config(param):
    read_config = configparser.ConfigParser()
    read_config.read(SETTINGS_FILE)
    main_section = dict(read_config.items("Main"))
    if param == "termlist":
        return [
            v
            for k, v in main_section.items()
            if param in k and re.search(r"\d", k)
        ]
    else:
        return [v for k, v in main_section.items() if param in k]
