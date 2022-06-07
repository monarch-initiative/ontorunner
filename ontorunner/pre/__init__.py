"""Constants."""

import os

PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATA_DIR = os.path.join(PARENT_DIR, "data")
SERIAL_DIR = os.path.join(DATA_DIR, "serialized")
