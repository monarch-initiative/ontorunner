import click
from runner.converters import biohub_converter as bc
from runner.post import add_sentence
from oger.ctrl.router import Router, PipelineServer
from oger.doc import EXPORTERS
from oger.ctrl.run import run
import configparser
from kgx.cli.cli_utils import transform
import os
import csv


def json2tsv(input, output) -> None:
    """
    Converts an JSON file into 'nodes' and 'edges' TSV.

    :param input: Input file (JSON file).
    :param ouput: Output file name desired.
    :return: None.
    """
    if input:
        if output is None:
            output = "data/output/output"

        transform(
            inputs=[input],
            input_format="obojson",
            output=output,
            output_format="tsv"
        )
    else:
        input_folder = "data/input/"
        output_folder = "data/output/"

        for subdir, dirs, files in os.walk(input_folder):
            for file in files:
                fn, ext = os.path.splitext(file)

                if ext == ".json":
                    transform(
                        inputs=[subdir + file],
                        input_format="obojson",
                        output=output_folder + fn,
                        output_format="tsv",
                    )


def prepare_termlist(input, output) -> None:
    """
    Generates a Bio Term Hub formatted term list for use with OGER.

    :param input: Input file 'ontology_nodes.tsv'.
    :param ouput: TSV file of list of terms 'ontology_termlist.tsv'.
    :return: None.
    """
    bc.parse(input, output)


def run_oger(
    content="data/input",
    termlist="data/terms/DICT.tsv",
    output="data/output/",
    output_format="tsv",
    settings="settings.ini",
    workers=1,
) -> None:
    """
    Run Oger

    :param content: Input file OR folder containing txt files.
    :param termlist: Path to the dictionary (TSV format).
    :param output: Path to save the output file.
    :param output_format: tsv (default).
    :param settings: If this is provided, all other arguments
    are provided in this file and are hence optional.
    Make changes to this file according to project needs
    s(default:'settings.ini').
    :param workers: Number of parallel threads (default = 5).
    :return: None.
    """
    if settings:
        config = configparser.ConfigParser()
        config.read(settings)
        sections = config._sections
        settings = sections["Main"]
        settings["n_workers"] = workers
        output = settings["output-directory"]
        input = settings["input-directory"]
        run(**settings)

    else:
        sniffer = csv.Sniffer()
        sample_bytes = 128
        dialect = sniffer.sniff(open(content).readline(sample_bytes))
        delim = ""
        if dialect.delimiter == "\t" or dialect.delimiter == ",":
            delim = "txt_tsv"
        else:
            delim = "txt"

        conf = Router(termlist_path=termlist, include_header=True)
        pl = PipelineServer(conf)
        doc = pl.load_one(content, delim)
        pl.process(doc)
        n = len([x for x in doc.iter_entities()])
        print(f"Number of recognized entities: {n}")
        with open(output, "w", encoding="utf8") as f:
            pl.write(doc, output_format, f)
        # Add sentence
        if os.path.isdir(content):
            input = content
        elif os.path.isfile(content):
            input = os.path.dirname(content)
            output = os.path.dirname(output)

    add_sentence.parse(input, output)


@click.group()
def cli():
    pass


@cli.command("json2tsv")
@click.option("--input", "-i", type=click.Path(exists=True))
@click.option("--output", "-o", type=str)
def json2tsv_click(input, output):
    json2tsv(input, output)


@cli.command("prepare-termlist")
@click.option("--input", "-i", type=click.Path(exists=True), required=True)
@click.option("--output", "-o", type=str, required=True)
def prepare_termlist_click(input, output):
    prepare_termlist(input, output)


@cli.command("run-oger")
@click.option("--content", "-c", type=click.Path(exists=True))
@click.option("--termlist", "-t", type=click.Path(exists=True))
@click.option("--output", "-o", type=str)
@click.option(
    "--output-format", "-f", type=click.Choice(EXPORTERS), default="bioc_json"
)
@click.option("--settings", "-s", type=click.Path(exists=True))
@click.option("--workers", "-w", default=1)
def run_oger_click(content, termlist, output,
                   output_format, settings, workers):
    run_oger(content, termlist, output, output_format, settings, workers)


if __name__ == "__main__":
    __spec__ = None
    cli()
