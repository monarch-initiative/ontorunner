from sys import path
import pandas as pd
import os
from glob import glob

from pandas.core.arrays.categorical import contains
def find_extensions(dr, ext):
    return glob(os.path.join(dr, "*.{}".format(ext)))

def parse(input_directory, output_directory) -> None:
    '''
    This parses the OGER output and adds sentences of relevant tokenized terms for context to the reviewer.
    :param input_directory: (str) Input directory path.
    :param output_directory: (str) Output directory path.
    :return: None.
    '''
    # Get a list of potential input files for particular formats
    input_list_tsv = find_extensions(input_directory, 'tsv')
    input_list_txt = find_extensions(input_directory, 'txt')
    output_files = find_extensions(output_directory, 'tsv')
    output_file = [x for x in output_files if '_node' not in x if '_edge' not in x if 'runNER' not in x][0]
    output_df = pd.read_csv(output_file, sep='\t', low_memory=False)
    output_df['SENTENCE'] = ''

    final_output_file = os.path.join(output_directory, 'runNER_Output.tsv')
    
    pd.DataFrame(output_df.columns).to_csv(final_output_file, sep='\t', index=None)
    
    if len(input_list_tsv) > 0:
        input_df = pd.read_csv(input_list_tsv[0], sep='\t', low_memory=False, index_col=None)

    if len(input_list_txt) > 0:
        # Read each text file such that Id = filename and text = full text
        pass

    for row in input_df.iterrows():
        idx = row[1].Id
        text = row[1].Text

        df = output_df[output_df['DOCUMENT ID'] == idx]
        import pdb; pdb.set_trace()
        # loop through OR compare to unique
        if df['END POSITION'] - df['START POSITION'] == len(text):
            df['SENTENCE'] = text
        else:
            # Look into the text to find a sentence where the term exists
            pass

        df.to_csv(final_output_file, mode='a', sep='\t', header=None, index=None )
        import pdb; pdb.set_trace()


