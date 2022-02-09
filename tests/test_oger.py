import os
from posix import listdir
import unittest
import pandas as pd
from ontorunner.oger_module import run_oger
from ontorunner.pre.util import json2tsv, prepare_termlist

cwd = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(cwd, "data")


def cleanup(dir):
    for f in listdir(dir):
        if f != "README.txt":
            os.remove(os.path.join(dir, f))


class TestOger(unittest.TestCase):
    def setUp(self) -> None:
        self.input = f"{data_dir}/input/"
        self.tsv = os.path.join(self.input, "test.tsv")
        self.txt = os.path.join(self.input, "test.txt")
        self.json = os.path.join(self.input, "envo.json")
        self.output = f"{data_dir}/output/"
        self.output_file = os.path.join(self.output, "test_ontoRunNER.tsv")
        self.terms = f"{data_dir}/terms/"
        self.termlist = os.path.join(self.terms, "envo_termlist.tsv")
        self.settings = f"{cwd}/settings.ini"
        print("setup runs here")

    def test_json2tsv(self) -> None:
        ofilename = os.path.join(self.output, "envo")
        json2tsv(self.json, ofilename)
        ofiles = [ofilename + "_nodes.tsv", ofilename + "_edges.tsv"]
        ofile_rows = [6405, 9645]
        for i, file in enumerate(ofiles):
            self.assertTrue(os.path.isfile(file))
            self.assertEqual(len(pd.read_csv(file, sep="\t")), ofile_rows[i])

    def test_prepare_termlist(self) -> None:
        ifile = os.path.join(self.output, "envo_nodes.tsv")
        prepare_termlist(ifile, self.termlist)
        self.assertEqual(len(pd.read_csv(self.termlist, sep="\t")), 11726)

    def test_run_oger(self) -> None:
        run_oger(settings=self.settings)
        self.assertTrue(os.path.isfile(self.output_file))
        self.assertEqual(len(pd.read_csv(self.output_file, sep="\t")), 148)

        # Clean-up files for next test run
        cleanup(self.output)
        cleanup(self.terms)
