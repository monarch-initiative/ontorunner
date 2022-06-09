"""Constants."""

import configparser
import re
from os import pardir
from os.path import abspath, dirname, join
from pathlib import Path

__version__ = "0.1.0"
# import pathlib

# HERE = pathlib.Path(__file__).parent.resolve()

DATA_DIR_NAME = "data"
TERMS_DIR_NAME = "terms"
SERIAL_DIR_NAME = "serialized"
INPUT_DIR_NAME = "input"
OUTPUT_DIR_NAME = "output"

PARENT_DIR = abspath(join(dirname(__file__), pardir))
DATA_DIR = join(PARENT_DIR, DATA_DIR_NAME)
ONTO_TERMS_FILENAME = "onto_termlist.tsv"
TERMS_PICKLED_FILENAME = "terms.pickle"
PATTERN_LIST_PICKLED_FILENAME = "patterns.pickle"
PHRASE_MATCHER_PICKLED_FILENAME = "phrase_matcher.pickle"
SETTINGS_FILENAME = "settings.ini"
STOPWORDS_FILENAME = "stopWords.txt"

SETTINGS_FILE_PATH = join(dirname(__file__), SETTINGS_FILENAME)


def _get_config(param: str, settings_file: Path = SETTINGS_FILE_PATH):
    read_config = configparser.ConfigParser()
    read_config.read(settings_file)
    main_section = dict(read_config.items("Main"))
    if param == "termlist":
        return [
            v.split("/")[-1]
            for k, v in main_section.items()
            if param in k and re.search(r"\d", k)
        ]
    else:
        return [v.replace("data/", "") for k, v in main_section.items() if param in k]
