from genericpath import isdir
import os
import shutil
from ontorunner import SERIAL_DIR
from ontorunner.converters import biohub_converter as bc
from kgx.cli.cli_utils import transform
import click


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
            output_format="tsv",
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


@cli.command("delete-cache")
def delete_cache():
    for f in os.listdir(SERIAL_DIR):
        path = os.path.join(SERIAL_DIR, f)
        if isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    print("Serialzed data folder purged!")


if __name__ == "__main__":
    cli()
