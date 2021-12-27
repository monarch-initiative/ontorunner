"""Constants."""

import os

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
# PATTERN_FILE = os.path.join(SERIAL_DIR, "onto_patterns.tsv")
