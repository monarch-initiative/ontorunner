"""Run Spacy."""
import os
from glob import glob
from multiprocessing import freeze_support
from pathlib import Path

import click
import pandas as pd
from spacy.tokens import Doc, Span

from ontorunner import (DATA_DIR, INPUT_DIR_NAME, OUTPUT_DIR_NAME,
                        SETTINGS_FILE_PATH, _get_config)
from ontorunner.pipes.OntoRuler import OntoRuler
from ontorunner.post import NODE_AND_EDGE_NAME, util

SCI_SPACY_LINKERS = ["umls", "mesh"]


def get_token_info(doc: Doc) -> pd.DataFrame:
    """Get metadata associated with spans within a document.

    :param doc: Doc object.
    :return: Pandas DataFrame.
    """ """"""
    key_list = [
        "matched_term",
        "POS",
        "tag",
        "scispacy_object_category",
        "object_id",
        "object_category",
        "object_label",
        "object_match_field",
        "origin",
        "sentence",
        "start",
        "end",
    ]

    # # Filter df to remove certain POS'
    # """
    # List of POS codes
    # POS | DESCRIPTION | EXAMPLES
    # ADJ | adjective | *big, old, green, incomprehensible, first*
    # ADP | adposition | *in, to, during*
    # ADV | adverb | *very, tomorrow, down, where, there*
    # AUX | auxiliary | *is, has (done), will (do), should (do)*
    # CONJ | conjunction | *and, or, but*
    # CCONJ | coordinating conjunction | *and, or, but*
    # DET | determiner | *a, an, the*
    # INTJ | interjection | *psst, ouch, bravo, hello*
    # NOUN | noun | *girl, cat, tree, air, beauty*
    # NUM | numeral | *1, 2017, one, seventy-seven, IV, MMXIV*
    # PART | particle | *’s, not,*
    # PRON | pronoun | *I, you, he, she, myself, themselves, somebody*
    # PROPN | proper noun | *Mary, John, London, NATO, HBO*
    # PUNCT | punctuation | *., (, ), ?*
    # SCONJ | subordinating conjunction | *if, while, that*
    # SYM | symbol | *$, %, §, ©, +, −, ×, ÷, =, :), 😝*
    # VERB | verb | *run, runs, running, eat, ate, eating*
    # X | other | *sfpksdpsxmsa*
    # SPACE | space

    # """
    ignore_pos = [
        "ADP",
        "CCONJ",
        "CONJ",
        "DET",
        "INTJ",
        "SCONJ",
        "PART",
        "PUNCT",
        "PRON",
        "AUX",
        "NUM",
        "ADV",
        "VERB",
    ]
    onto_dict = {}
    for k in key_list:
        onto_dict[k] = []

    unwanted_labels = [
        "ORG",
        "GPE",
        "LOC",
    ]
    unwanted_span_list = []
    valid_span = True
    df = pd.DataFrame()

    for span in doc.ents:
        # Filter out spans with labels that are irrelevant
        if span.label_ in unwanted_labels:
            unwanted_span_list.append(span.text)
        else:
            if span._.is_an_ontology_term and span.text not in unwanted_span_list:
                valid_span = any([token.pos_ not in ignore_pos for token in span])

                if valid_span:
                    pos_list = ", ".join([token.pos_ for token in span])
                    tag_list = ", ".join([token.tag_ for token in span])
                    onto_dict["matched_term"].append(span.text)
                    onto_dict["POS"].append(pos_list)
                    onto_dict["tag"].append(tag_list)
                    onto_dict["scispacy_object_category"].append(span.label_)
                    onto_dict["object_id"].append(span._.object_id)
                    onto_dict["object_category"].append(span._.object_category)
                    onto_dict["object_label"].append(span._.object_label)
                    onto_dict["object_match_field"].append(span._.object_match_field)
                    onto_dict["origin"].append(span._.origin)
                    onto_dict["sentence"].append(span.sent)
                    onto_dict["start"].append(span.start_char)
                    onto_dict["end"].append(span.end_char)
                df = pd.DataFrame.from_dict(onto_dict)
                # Filter out terms that may have been
                # missed by the 'valid_span' flag determination.
                df = df[~df["matched_term"].isin(unwanted_span_list)]

    return df


def explode_df(df: pd.DataFrame) -> pd.DataFrame:
    """Explode multiple DataFrames in a single row into multiple rows.

    :param df: Dataframe to be exploded.
    :return: Exploded DataFrame where each row correspond to a row in the DataFrame.
    """
    new_df = pd.DataFrame()
    for _, doc_obj_row in df.iterrows():
        tmp_df = doc_obj_row[1]
        tmp_df.insert(0, "id", doc_obj_row.id)
        new_df = pd.concat([new_df, tmp_df], ignore_index=True)

    new_df = new_df.rename(columns={"id": "document_id"})
    return new_df


def onto_tokenize(doc: Doc, onto_ruler_obj: OntoRuler) -> Doc:
    """Set custom span information from the Doc object.

    :param doc: Doc object.
    :param onto_ruler_obj: OntoRuler object.
    :return: Doc object.
    """
    # matches = onto_ruler_obj.match(doc)
    matches = onto_ruler_obj.phrase_matcher(doc)
    spans = [
        Span(doc, start, end, label=onto_ruler_obj.label)
        for match_id, start, end in matches
    ]
    # doc.spans[onto_ruler_obj.label] = spans

    for _, span in enumerate(spans):
        span._.set("has_curies", True)

        if span.text.lower() in onto_ruler_obj.terms.keys():
            span._.set(onto_ruler_obj.span_term_extension, True)
            span._.set(
                "object_id",
                onto_ruler_obj.terms[span.text.lower()]["object_id"],
            )
            span._.set(
                "object_category",
                onto_ruler_obj.terms[span.text.lower()]["object_category"],
            )
            span._.set(
                "object_label",
                onto_ruler_obj.terms[span.text.lower()]["object_label"],
            )
            span._.set(
                "object_match_field",
                onto_ruler_obj.terms[span.text.lower()]["object_match_field"],
            )
            span._.set("origin", onto_ruler_obj.terms[span.text.lower()]["origin"])

    return doc


def get_knowledge_base_enitities(doc: Doc, onto_ruler_obj: OntoRuler) -> pd.DataFrame:
    """Get information from the SciSpacy pipeline.

    :param doc: Doc object.
    :param onto_ruler_obj: OntoRuler object.
    :return: Pandas DataFrame.
    """
    linker = onto_ruler_obj.nlp.get_pipe("scispacy_linker")
    ent_dict = {}
    key_list = ["cui", "matched_term", "aliases", "definition", "tui"]
    for k in key_list:
        ent_dict[k] = []

    for entity in doc.ents:
        for kb_ent in entity._.kb_ents:
            ent_object = linker.kb.cui_to_entity[kb_ent[0]]
            ent_dict["cui"].append(ent_object.concept_id)
            ent_dict["matched_term"].append(ent_object.canonical_name)
            ent_dict["aliases"].append(ent_object.aliases)
            ent_dict["definition"].append(ent_object.definition)
            ent_dict["tui"].append(ent_object.types)

    return pd.DataFrame.from_dict(ent_dict)


def export_tsv(df: pd.DataFrame, data_dir: str, fn: str) -> None:
    """Export pandas DataFrame object into a TSV file.

    :param df: Pandas DataFrame.
    :param data_dir: Destination directory for export.
    :param fn: Filename.
    """
    fn_path = os.path.join(data_dir, OUTPUT_DIR_NAME, fn + ".tsv")
    df.to_csv(fn_path, sep="\t", index=None)


@click.group()
def main():
    """
    Spacy module to run NER.

    e.g. poetry run python -m ontorunner.spacy_module run-spacy
    """
    pass


def run_spacy(
    data_dir: Path = DATA_DIR,
    settings_file: Path = SETTINGS_FILE_PATH,
    linker: str = "umls",
    to_pickle: bool = True,
    need_ancestors: bool = True,
):
    """
    Run spacy with sciSpacy pipeline.

    :param data_dir: Path to the data directory.
    :param settings: Path to settings.ini file.
    :param linker: Type of sciSpacy linker desired ([umls]/mesh).
    """
    if linker not in SCI_SPACY_LINKERS:
        raise (
            ValueError(
                f"SciSpacy linker provided '{linker}' is invalid."
                f"Choose one of the following: {SCI_SPACY_LINKERS}"
            )
        )
    onto_ruler_obj = OntoRuler(
        data_dir=data_dir,
        settings_filepath=settings_file,
        linker=linker,
        to_pickle=to_pickle,
    )
    batch_size = 10000
    input_dir_path = os.path.join(data_dir, INPUT_DIR_NAME) + "/*.tsv"
    input_file_list = glob(input_dir_path)
    list_of_input_dfs = []
    for fn in input_file_list:
        in_df = pd.read_csv(fn, sep="\t", low_memory=False)
        list_of_input_dfs.append(in_df)

    input_df = pd.concat(list_of_input_dfs, axis=0, ignore_index=True)

    input_df["spacy_doc"] = list(
        onto_ruler_obj.nlp.pipe(input_df["text"].values, batch_size=batch_size)
    )

    input_df["spacy_doc_tok"] = input_df["spacy_doc"].apply(
        lambda row: onto_tokenize(row, onto_ruler_obj)
    )

    input_df["spacy_tokens"] = input_df["spacy_doc_tok"].apply(
        lambda row: get_token_info(row)
    )

    input_df["spacy_kb_ent"] = input_df["spacy_doc_tok"].apply(
        lambda row: get_knowledge_base_enitities(row, onto_ruler_obj)
    )

    kb_df = explode_df(input_df[["id", "spacy_kb_ent"]])
    onto_df = explode_df(input_df[["id", "spacy_tokens"]])
    # nlp_df = doc_to_df(dframcy, input_df[["id", "spacy_doc"]])

    stopwords_file_path = os.path.join(data_dir, _get_config("termlist_stopwords")[0])
    stopwords_file = open(stopwords_file_path, "r")
    stopwords = stopwords_file.read().splitlines()
    onto_df = onto_df.loc[~onto_df["matched_term"].isin(stopwords)]

    onto_df = util.consolidate_rows(onto_df)
    onto_df = util.get_column_doc_ratio(onto_df, "object_label")
    onto_df = util.get_column_doc_ratio(onto_df, "matched_term")
    if need_ancestors:
        nodes_and_edges_dir = os.path.join(data_dir, NODE_AND_EDGE_NAME)
        onto_df = util.get_ancestors(
            df=onto_df, nodes_and_edges_dir=nodes_and_edges_dir
        )

    onto_df = onto_df.astype(str).drop_duplicates()
    kb_df = kb_df.astype(str).drop_duplicates()

    export_tsv(kb_df, data_dir, "sciSpacy_" + linker + "_ontoRunNER")
    export_tsv(onto_df, data_dir, "ontology_ontoRunNER")


@main.command("run-spacy")
@click.option("-d", "--data-dir", help="Data directory path.", default=DATA_DIR)
@click.option(
    "-s",
    "--settings-file",
    help="settings.ini file path.",
    default=SETTINGS_FILE_PATH,
)
@click.option(
    "-l",
    "--linker",
    type=click.Choice(["umls", "mesh"]),
    help="Which sciSpacy linker to use.('umls'[Default] or 'mesh')",
    default="umls",
)
@click.option(
    "-p",
    "--pickle-files",
    help="Boolean to determine if intermediate files should be pickled or no",
    default=True,
)
@click.option("--need-ancestors", "-a", type=bool, default=False)
def run_spacy_click(
    data_dir: Path,
    settings_file: Path,
    linker: str,
    pickle_files: bool,
    need_ancestors: bool,
):
    """CLI for running the spacy module.

    :param data_dir: Data dorectory path.
    :param settings_file: Filepath for settings.ini file.
    :param linker: Type of sciSpacy linker desired ([umls]/mesh).
    :param pickle_files: Bool representing if files
        must be pickled or not.
    :param need_ancestors: Bool indicatind if output should.
        contain ancestors of matched term or not.
    """
    run_spacy(
        data_dir=data_dir,
        settings_file=settings_file,
        linker=linker,
        to_pickle=pickle_files,
        need_ancestors=need_ancestors,
    )

    # os.system('say "Done!"')


if __name__ == "__main__":
    freeze_support()
    main()
