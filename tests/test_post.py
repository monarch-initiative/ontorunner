import os
import unittest

import numpy as np
import pandas as pd

from ontorunner.post.util import get_ancestors

cwd = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(cwd, "data")


class TestPost(unittest.TestCase):
    def setUp(self) -> None:
        self.input_dir = os.path.join(data_dir, "input")
        self.ancestor_input_dir = os.path.join(self.input_dir, "ancestor_test_input")
        self.node_and_edge_dir = os.path.join(data_dir, "nodes_and_edges")
        self.input_file = os.path.join(self.ancestor_input_dir, "ancestor_test.tsv")
        self.df = pd.read_csv(self.input_file, sep="\t", low_memory=False)
        self.valid_dir = os.path.join(data_dir, "validation")
        self.valid_ancestor_output = os.path.join(
            self.valid_dir, "ancestor_test_valid.tsv"
        )

    def test_get_ancestors(self) -> None:
        """Testing the get_ancestors method."""
        df_with_ancestors = get_ancestors(self.df, self.node_and_edge_dir)
        valid_ouput_df = pd.read_csv(
            self.valid_ancestor_output, sep="\t", low_memory=False
        ).replace(np.nan, "")
        pd.testing.assert_frame_equal(df_with_ancestors, valid_ouput_df)
