from runner.post.util import filter_synonyms, consolidate_rows
import pandas as pd
# from nltk.corpus.reader.wordnet import NOUN, VERB
from nltk.stem.wordnet import WordNetLemmatizer
# from textdistance.algorithms.edit_based import Levenshtein

import csv
import os
from glob import glob

import nltk
import textdistance
# from pandas.core.arrays.categorical import contains

if not nltk.find("corpora/wordnet"):
    nltk.download("wordnet")

pd.options.mode.chained_assignment = None  # default='warn'


def find_extensions(dr, ext):
    return glob(os.path.join(dr, "*.{}".format(ext)))


def sentencify(input_df, output_df, output_fn):
    """
        Add relevant sentences to the tokenized term in every row of a
        pandas DataFrame
        :param df: (DataFrame) pandas DataFrame.
        :return: None
    """
    for j, row in input_df.iterrows():
        idx = row.id
        text = row.text
        # Check for text = NaN
        if text == text:
            text = (
                text.replace("\t", " ")
                .replace("\u2028", " ")
                .replace("\n", "")
                .replace("\r", "",)
            )
            text_tok = nltk.sent_tokenize(text)
            sub_df = output_df[output_df["document_id"] == idx]
            # In certain instances, in spite of the 'matched' and 'preferred'
            # terms being the same, the term is registered as a synonym by KGX
            # and hence the biohub_converter codes this with a '_SYNONYM' tag.
            # In order to counter this, we need to filter these extra rows out.
            if not sub_df.empty and any(sub_df["entity_id"]
                                        .str.endswith("_SYNONYM")):
                sub_df = filter_synonyms(sub_df)

            if len(text_tok) == 1:
                sub_df["sentence"] = text
            else:
                relevant_tok = []
                start_reached = False
                end_reached = False
                for i, row2 in sub_df.iterrows():
                    term_of_interest = str(row2["matched_term"])
                    start_pos = int(row2["start_position"])
                    if start_pos == 0:
                        start_reached = True
                    end_pos = int(row2["end_position"])
                    if end_pos == len(text):
                        end_reached = True
                    if term_of_interest == "nan":
                        # get just the portion where
                        # 'matched_term' == 'preferred_form'
                        # because in case of _SYNONYM,
                        # there will be extra metadata which
                        # will not be present in the tokenized sentence.
                        term_of_interest = str(row2["preferred_form"]).lower()

                    relevant_tok = [x for x in text_tok
                                    if term_of_interest in x]
                    single_tok = relevant_tok
                    count = 0

                    while len(single_tok) != 1:
                        count += 1
                        # This keeps track of the # of times the start_pos
                        # and/or end_pos are shifted
                        # Detect the beginning and ending of sentences
                        # ---------------------
                        for tok in single_tok:
                            if tok.startswith(text[start_pos:end_pos]):
                                start_reached = True

                        if not start_reached:
                            start_pos -= 1

                        for tok in single_tok:
                            if tok.endswith(text[start_pos:end_pos]):
                                end_reached = True

                        if not end_reached:
                            end_pos += 1
                        # -------------------------------------------------------------------
                        term_of_interest = text[start_pos:end_pos]

                        single_tok = [
                            x for x in relevant_tok
                            if term_of_interest.strip() in x
                        ]

                        if count > 30 and 1 < len(single_tok):
                            single_tok = [single_tok[0]]
                            count = 0
                            break
                        # Reason for the break:
                        # In some instance the sentences are repeated.
                        # In such cases the expanding window with start_pos and
                        # end_pos goes expanding after 30 character match
                        # (arbitrarily) we take the first element out of the
                        # common terms and take that as the SENTENCE
                        # and then 'break'-ing out of the 'while' loop.
                        # Else, it'll continue looking for the unique
                        # sentence forever. It's a hack but for now it'll
                        # do until severe consequences detected.

                    sub_df.loc[i, "sentence"] = single_tok[0]

            if not sub_df.empty:
                sub_df["entity_sentence_%"] = sub_df.apply(
                    lambda x: 1
                    - textdistance.jaccard.distance(
                        x.matched_term.lower(), x.sentence.lower()
                    ),
                    axis=1,
                )

                sub_df.to_csv(output_fn, mode="a", sep="\t",
                              header=None, index=None)


def get_match_type(token1: str, token2: str) -> str:
    """
    Return type of token match

    :param token1: token from 'matched_term'
    :type token1: str
    :param token2: token from 'preferred_term'
    :type token2: str
    :return: Type of match [e.g.: 'exact_match' etc.]
    :rtype: str
    """

    match = ""
    lemma = WordNetLemmatizer()

    if token1.lower() == token2.lower():
        match = "exact_match"
    elif lemma.lemmatize(token1) == lemma.lemmatize(token2):
        # pos = NOUN by default
        match = "lemmatic_match"
    elif lemma.lemmatize(token1, pos="v") == lemma.lemmatize(token2, pos="v"):
        # testing pos = VERB
        match = "lemmatic_match"
    elif lemma.lemmatize(token1, pos="a") == lemma.lemmatize(token2, pos="a"):
        # testing pos = ADJECTIVE
        match = "lemmatic_match"
    elif lemma.lemmatize(token1, pos="r") == lemma.lemmatize(token2, pos="r"):
        # testing pos = ADVERB
        match = "lemmatic_match"

    return match


def parse(input_directory, output_directory) -> None:
    """
    This parses the OGER output and adds sentences of relevant tokenized terms
    for context to the reviewer.
    :param input_directory: (str) Input directory path.
    :param output_directory: (str) Output directory path.
    :return: None.
    """
    # Get a list of potential input files for particular formats
    input_list_tsv = find_extensions(input_directory, "tsv")
    input_list_txt = find_extensions(input_directory, "txt")
    output_files = find_extensions(output_directory, "tsv")
    output_file = [
        x
        for x in output_files
        if "_node" not in x
        if "_edge" not in x
        if "runNER" not in x
    ][0]
    output_df = pd.read_csv(output_file, sep="\t", low_memory=False)
    output_df.columns = output_df.columns.str.replace(" ", "_").str.lower()
    # Consolidate rows where the entitys is the same
    # and recognized from multiple origins
    output_df = consolidate_rows(output_df)

    output_df[["preferred_form", "match_field"]] = \
        output_df["preferred_form"].str.split("\\[SYNONYM_OF:", expand=True)

    output_df["match_field"] = \
        output_df["match_field"].str.replace("]", "", regex=True)

    # Add column which indicates how close of a match is the recognized entity.
    output_df.insert(
        6,
        "match_type",
        output_df.apply(
            lambda x:
                get_match_type(
                                x.matched_term.lower(),
                                x.preferred_form.lower()
                            ),
            axis=1,
        ),
    )

    # Levenshtein distances
    output_df.insert(
        7,
        "levenshtein_distance",
        output_df.apply(
            lambda x: textdistance.levenshtein.distance(
                x.matched_term.lower(), x.preferred_form.lower()
            ),
            axis=1,
        ),
    )

    # Jaccard Index

    output_df.insert(
        8,
        "jaccard_index",
        output_df.apply(
            lambda x: textdistance.jaccard.distance(
                x.matched_term.lower(), x.preferred_form.lower()
            ),
            axis=1,
        ),
    )

    # Monge-Elkan
    output_df.insert(
        9,
        "monge_elkan",
        output_df.apply(
            lambda x: textdistance.monge_elkan.distance(
                x.matched_term.lower(), x.preferred_form.lower()
            ),
            axis=1,
        ),
    )

    output_df["sentence"] = ""

    output_df["entity_sentence_%"] = ""

    output_df = output_df.reindex(
        columns=[
            "document_id",
            "type",
            "start_position",
            "end_position",
            "matched_term",
            "preferred_form",
            "match_field",
            "match_type",
            "levenshtein_distance",
            "jaccard_index",
            "monge_elkan",
            "entity_id",
            "sentence_id",
            "umls_cui",
            "origin",
            "sentence",
            "entity_sentence_%",
        ]
    )

    final_output_file = os.path.join(output_directory, "runNER_Output.tsv")

    pd.DataFrame(output_df.columns).T.to_csv(
        final_output_file, sep="\t", index=None, header=None
    )

    if len(input_list_tsv) > 0:
        for f in input_list_tsv:
            input_df = pd.read_csv(f, sep="\t",
                                   low_memory=False,
                                   index_col=None)
            sentencify(input_df, output_df, final_output_file)

    if len(input_list_txt) > 0:
        # Read each text file such that Id = filename and text = full text
        for f in input_list_txt:
            input_df = pd.DataFrame(columns=["id", "text"])
            sniffer = csv.Sniffer()
            sample_bytes = 128
            dialect = sniffer.sniff(open(f).readline(sample_bytes))
            if dialect.delimiter == "\t" or dialect.delimiter == ",":
                input_df = pd.read_csv(f, sep="\t", low_memory=False,
                                       index_col=None)
            else:
                id = f.split("/")[-1].split(".txt")[0]
                with open(f, "r") as fn:
                    text = fn.readlines()
                    text = "".join(text).replace("\n", " ")
                input_df = input_df.append({"id": id, "text": text},
                                           ignore_index=True)

            sentencify(input_df, output_df, final_output_file)
