import click
from biohub_converter import parse
from oger.ctrl.router import Router, PipelineServer
from oger.doc import EXPORTERS
from oger.ctrl.run import run
import configparser

@click.group()
def cli():
    pass

@cli.command('prepare-termlist')
@click.option('--input', '-i', type=click.Path(exists=True), required=True)
@click.option('--output', '-o', type=str, required=True)
def prepare_termlist(input, output):
    """
    Generates a Bio Term Hub formatted term list for use with OGER.
    """
    parse(input, output)


@cli.command('run-oger')
@click.argument('content', type=click.Path(exists=True), required=True)
@click.option('--termlist', '-t', type=click.Path(exists=True), required=True)
@click.option('--output', '-o', type=str, required=True)
@click.option('--output-format', '-f', type=click.Choice(EXPORTERS), default='bioc_json')
def run_oger(content, termlist, output, output_format):
    conf = Router(termlist_path=termlist)
    pl = PipelineServer(conf)
    doc = pl.load_one(content, 'txt')
    pl.process(doc)
    n = len([x for x in doc.iter_entities()])
    print(f"Number of recognized entities: {n}")
    with open(output, 'w', encoding='utf8') as f:
        pl.write(doc, output_format, f)

@cli.command('run-oger-with-settings')
@click.option('--n_workers', '-w', default = 1)
def run_oger_with_settings(n_workers):
    config = configparser.ConfigParser()
    config.read('settings.ini')
    sections = config._sections
    settings = sections['Main']
    settings['n_workers'] = n_workers
    run(**settings)
    

if __name__ == '__main__':
    cli()
