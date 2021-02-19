import click
from biohub_converter import parse
from oger.ctrl.router import Router, PipelineServer
from oger.doc import EXPORTERS
from oger.ctrl.run import run
import configparser
from kgx.cli.cli_utils import transform
import os

@click.group()
def cli():
    pass

@cli.command('json2tsv')
@click.option('--input', '-i', type=click.Path(exists=True))#, required=True)
@click.option('--output', '-o', type=str)#, required=True)
def json2tsv(input, output):
    """
    Converts an JSON file into 'nodes' and 'edges' TSV.
    """
    if input:
        if output == None:
            output = 'data/output'

        transform(inputs=[input], input_format='obojson', output=output, output_format='tsv')
    else:
        input_folder = 'data/input/'
        output_folder = 'data/output/'

        for subdir, dirs, files in os.walk(input_folder):
            for file in files:
                fn, ext = os.path.splitext(file)

                if ext == '.json':
                    transform(inputs=[subdir+file], input_format='obojson', output=output_folder+fn, output_format='tsv')
                

@cli.command('prepare-termlist')
@click.option('--input', '-i', type=click.Path(exists=True), required=True)
@click.option('--output', '-o', type=str, required=True)
def prepare_termlist(input, output):
    """
    Generates a Bio Term Hub formatted term list for use with OGER.
    """
    parse(input, output)


@cli.command('run-oger')
@click.option('--content', '-c', type=click.Path(exists=True))
@click.option('--termlist', '-t', type=click.Path(exists=True))
@click.option('--output', '-o', type=str)
@click.option('--output-format', '-f', type=click.Choice(EXPORTERS), default='bioc_json')
@click.option('--settings', '-s', type=click.Path(exists=True))
@click.option('--workers', '-w', default = 1)
def run_oger(content, termlist, output, output_format, settings, workers):
    if settings:
        config = configparser.ConfigParser()
        config.read('settings.ini')
        sections = config._sections
        settings = sections['Main']
        settings['n_workers'] = workers
        run(**settings)
    else:
        conf = Router(termlist_path=termlist)
        pl = PipelineServer(conf)
        doc = pl.load_one(content, 'txt')
        pl.process(doc)
        n = len([x for x in doc.iter_entities()])
        print(f"Number of recognized entities: {n}")
        with open(output, 'w', encoding='utf8') as f:
            pl.write(doc, output_format, f)
    

if __name__ == '__main__':
    cli()
