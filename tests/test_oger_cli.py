import os
import unittest
import subprocess
import pandas as pd
from . import cleanup


cwd = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(cwd, "data")


class TestOgerCLI(unittest.TestCase):
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

    def test_cli_json2tsv(self) -> None:
        ofilename = os.path.join(self.output, "envo")
        ofiles = [ofilename + "_nodes.tsv", ofilename + "_edges.tsv"]
        cli_ofile_rows = [6405, 9643]
        process = subprocess.Popen(
            [
                "python",
                "-m",
                "ontorunner.pre.util",
                "json2tsv",
                "-i",
                self.json,
                "-o",
                ofilename,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        print(stderr)
        print(stdout)

        for i, file in enumerate(ofiles):
            self.assertTrue(os.path.isfile(file))
            self.assertEqual(
                len(pd.read_csv(file, sep="\t")), cli_ofile_rows[i]
            )

    def test_cli_prepare_termlist(self) -> None:
        ifile = os.path.join(self.output, "envo_nodes.tsv")

        process = subprocess.Popen(
            [
                "python",
                "-m",
                "ontorunner.pre.util",
                "prepare-termlist",
                "-i",
                ifile,
                "-o",
                self.termlist,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        print(stderr)
        print(stdout)

        self.assertEqual(len(pd.read_csv(self.termlist, sep="\t")), 11726)

    def test_cli_run_oger_with_settings(self) -> None:
        s = self.settings
        process = subprocess.Popen(
            ["python", "-m", "ontorunner.oger_module", "run-oger", "-s", s],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        print(stderr)
        print(stdout)

        self.assertTrue(os.path.isfile(self.output_file))
        self.assertEqual(len(pd.read_csv(self.output_file, sep="\t")), 148)
        # cleanup(self.output)

        # Clear output for next test

    def test_cli_run_oger_without_settings(self) -> None:
        process = subprocess.Popen(
            [
                "python",
                "-m",
                "ontorunner.oger_module",
                "run-oger",
                "-c",
                self.txt,
                "-t",
                self.termlist,
                "-o",
                self.output_file,
                "-f",
                "tsv",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        print(stderr)
        print(stdout)

        # self.assertTrue(os.path.isfile(self.output_file))
        self.assertEqual(len(pd.read_csv(self.output_file, sep="\t")), 148)

        # Clean-up files for next test run
        cleanup(self.output)
