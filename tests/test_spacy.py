import os
import unittest

import pandas as pd

from . import cleanup, run_spacy

cwd = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(cwd, "data")


class TestSpacy(unittest.TestCase):
    def setUp(self) -> None:
        self.output_dir = os.path.join(data_dir, "output")
        self.serialized = os.path.join(data_dir, "serialized")
        self.linker = "umls"
        self.onto_output = os.path.join(self.output_dir, "ontology_ontoRunNER.tsv")
        self.sciSpacy_output = os.path.join(
            self.output_dir, "sciSpacy_" + self.linker + "_ontoRunNER.tsv"
        )

    def test_run_spacy(self):
        settings_fp = os.path.join(cwd, "settings.ini")
        run_spacy(
            data_dir=data_dir,
            settings_file=settings_fp,
            linker=self.linker,
            to_pickle=False,
        )
        onto_out_df = pd.read_csv(self.onto_output, sep="\t", low_memory=False)
        sciSpacy_out_df = pd.read_csv(self.sciSpacy_output, sep="\t", low_memory=False)

        self.assertEqual(20, len(onto_out_df))
        self.assertEqual(61, len(sciSpacy_out_df))

        # Clean-up files for next test run
        cleanup(self.output_dir)
        cleanup(self.serialized)
