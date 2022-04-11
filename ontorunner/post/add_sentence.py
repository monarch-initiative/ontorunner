from ontorunner.post.util import (
    filter_synonyms,
    consolidate_rows,
    get_column_doc_ratio,
    # get_ancestors,
)
import pandas as pd
import csv
import os
from glob import glob
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import textdistance

# if not nltk.find("corpora/wordnet"):
nltk.download("wordnet")
nltk.download("punkt")
nltk.download("omw-1.4")
nltk.download("averaged_perceptron_tagger")  # for GH Actions.
nltk.download("maxent_ne_chunker")
nltk.download("words")


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
            # ** This block is for freq count of term in text
            # # Calcualte frquencies of words and phrases
            # word_tok = nltk.word_tokenize(text.lower())
            # # This gets freq count for each word
            # word_tok_freq = FreqDist(word_tok)
            # # This will capture phrases and corresponding frequencies
            # phrases = dict()
            # for size in 2, 3, 4, 5:
            #     phrases[size] = FreqDist(ngrams(word_tok, size))

            sub_df = output_df[output_df["document_id"] == idx]
            # In certain instances, in spite of the 'matched' and 'preferred'
            # terms being the same, the term is registered as a synonym by KGX
            # and hence the biohub_converter codes this with a '_SYNONYM' tag.
            # In order to counter this, we need to filter these extra rows out.
            if not sub_df.empty and any(
                sub_df["object_id"].str.endswith("_SYNONYM")
            ):
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

                    relevant_tok = [
                        x for x in text_tok if term_of_interest in x
                    ]

                    # ** This block is for freq count of term in text ****
                    # # Add frequency count for the `term_of_interest`
                    # ngram = term_of_interest.split()

                    # if len(ngram) == 1:
                    #     if ngram[0] in word_tok_freq.keys():
                    #         sub_df.loc[i, "matched_term_freq"]
                    #               = word_tok_freq[
                    #             term_of_interest.strip()
                    #         ]
                    #     else:
                    #         key_match = [
                    #             key
                    #             for key in word_tok_freq.keys()
                    #             if ngram[0] in key and "-" in key
                    #         ]

                    #         freq = 0

                    #         for key in key_match:
                    #             # * Check how similar the
                    #             # * tokens are to decide frequency
                    #             similarity = textdistance.jaccard.distance(
                    #                 key, ngram[0]
                    #             )
                    #             if similarity <= 0.40:
                    #                 freq += word_tok_freq[key]
                    #             import pdb

                    #             pdb.set_trace()

                    #         if freq > 0:
                    #             sub_df.loc[i, "matched_term_freq"] = freq

                    # elif len(ngram) > 1:
                    #     sub_df.loc[i, "matched_term_freq"] = phrases[
                    #         len(ngram)
                    #     ][tuple(ngram)]
                    # else:
                    #     logging.warning(
                    #         f"Term: {term_of_interest} => no frequency count"
                    #     )
                    # **********************************************************

                    # Sometimes the term we're looking for gets separated by
                    # sentence tokenizer from NLTK
                    # for e.g. CHEBI identifies "J. A"

                    #           PREFERRED FORM            |    object_id
                    # j?_a?[SYNONYM_OF:GlyTouCan G98058RD]|CHEBI:146303_SYNONYM

                    # but the tokenizer object is ['Downing, J.', 'A., Cole,].
                    # In such a case, let relevant_tok = "irrelevant token"
                    if relevant_tok == []:
                        relevant_tok = ["irrelevant token: can be ignored."]

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
                            x
                            for x in relevant_tok
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
                sub_df["object_sentence_%"] = sub_df.apply(
                    lambda x: 1
                    - textdistance.jaccard.distance(
                        x.matched_term.lower(), x.sentence.lower()
                    ),
                    axis=1,
                )

                sub_df.to_csv(
                    output_fn, mode="a", sep="\t", header=None, index=None
                )


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
    output_file_list = [
        x
        for x in output_files
        if "_node" not in x
        if "_edge" not in x
        if "ontoRunNER" not in x
    ]
    for output_file in output_file_list:
        output_df = pd.read_csv(output_file, sep="\t", low_memory=False)
        output_df.columns = output_df.columns.str.replace(" ", "_").str.lower()
        # Consolidate rows where the entitys is the same
        # and recognized from multiple origins
        output_df = output_df.rename(
            columns={"entity_id": "object_id", "type": "object_category"}
        )

        output_df = consolidate_rows(output_df)

        output_df[["preferred_form", "object_label"]] = output_df[
            "preferred_form"
        ].str.split("\\[SYNONYM_OF:", expand=True)

        output_df["object_label"] = output_df["object_label"].str.replace(
            "]", "", regex=True
        )
        output_df["object_label"] = output_df["object_label"].fillna(
            output_df["preferred_form"]
        )

        output_df["pos_and_ne_chunk"] = (
            output_df["matched_term"]
            .apply(word_tokenize)
            .apply(pos_tag)
            .apply(ne_chunk)
        )

        output_df = get_column_doc_ratio(output_df, "object_label")
        output_df = get_column_doc_ratio(output_df, "matched_term")

        # Add column which indicates how close
        # of a match is the recognized entity.
        output_df.insert(
            6,
            "match_type",
            output_df.apply(
                lambda x: get_match_type(
                    x.matched_term.lower(), x.preferred_form.lower()
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

        output_df["object_sentence_%"] = ""

        output_df = output_df.reindex(
            columns=[
                "document_id",
                "object_category",
                "start_position",
                "end_position",
                "matched_term",
                "preferred_form",
                "object_label",
                "object_label_doc_ratio",
                "matched_term_doc_ratio",
                "match_type",
                "levenshtein_distance",
                "jaccard_index",
                "monge_elkan",
                "object_id",
                "pos_and_ne_chunk",
                "sentence_id",
                "umls_cui",
                "origin",
                "sentence",
                "object_sentence_%",
            ]
        )
        # output_df = get_ancestors(output_df) Ontobio alternative to get Ancestors.
        # Takes too long

        final_output_file = output_file.replace(".tsv", "_ontoRunNER.tsv")

        pd.DataFrame(output_df.columns).T.to_csv(
            final_output_file, sep="\t", index=None, header=None
        )

        if len(input_list_tsv) > 0:
            for f in input_list_tsv:
                input_df = pd.read_csv(
                    f, sep="\t", low_memory=False, index_col=None
                )
                sentencify(input_df, output_df, final_output_file)

        if len(input_list_txt) > 0:
            # Read each text file such that Id = filename and text = full text
            for f in input_list_txt:
                input_df = pd.DataFrame(columns=["id", "text"])
                sniffer = csv.Sniffer()
                sample_bytes = 128
                dialect = sniffer.sniff(open(f).readline(sample_bytes))
                if dialect.delimiter == "\t" or dialect.delimiter == ",":
                    input_df = pd.read_csv(
                        f, sep="\t", low_memory=False, index_col=None
                    )
                else:
                    id = f.split("/")[-1].split(".txt")[0]
                    with open(f, "r") as fn:
                        text = fn.readlines()
                        text = "".join(text).replace("\n", " ")
                    input_df = input_df.append(
                        {"id": id, "text": text}, ignore_index=True
                    )

                sentencify(input_df, output_df, final_output_file)
