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
