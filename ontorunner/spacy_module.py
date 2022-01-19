from asyncio.base_tasks import _task_get_stack
import os
import pdb
from turtle import pos
from ontorunner import PARENT_DIR, SETTINGS_FILE, get_config
from ontorunner.pipes.OntoRuler import OntoRuler
from glob import glob
import pandas as pd
from spacy.tokens import Span
from multiprocessing import freeze_support
from ontorunner.post import util
import click


def get_token_info(doc):
    key_list = [
        "matched_term",
        "POS",
        "tag",
        "label",
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
            if (
                span._.is_an_ontology_term
                and span.text not in unwanted_span_list
            ):
                valid_span = any(
                    [token.pos_ not in ignore_pos for token in span]
                )

                if valid_span:
                    pos_list = ", ".join([token.pos_ for token in span])
                    tag_list = ", ".join([token.tag_ for token in span])
                    onto_dict["matched_term"].append(span.text)
                    onto_dict["POS"].append(pos_list)
                    onto_dict["tag"].append(tag_list)
                    onto_dict["label"].append(span.label_)
                    onto_dict["object_id"].append(span._.object_id)
                    onto_dict["object_category"].append(span._.object_category)
                    onto_dict["object_label"].append(span._.object_label)
                    onto_dict["object_match_field"].append(
                        span._.object_match_field
                    )
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
    new_df = pd.DataFrame()
    for _, doc_obj_row in df.iterrows():
        tmp_df = doc_obj_row[1]
        tmp_df.insert(0, "id", doc_obj_row.id)
        new_df = pd.concat([new_df, tmp_df], ignore_index=True)

    new_df = new_df.rename(columns={"id": "document_id"})
    return new_df


def onto_tokenize(doc):
    # matches = onto_ruler_obj.match(doc)
    matches = onto_ruler_obj.phrase_matcher(doc)

    spans = [
        Span(doc, start, end, label=onto_ruler_obj.label)
        for matchId, start, end in matches
    ]
    # doc.spans[onto_ruler_obj.label] = spans

    for i, span in enumerate(spans):
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
            span._.set(
                "origin", onto_ruler_obj.terms[span.text.lower()]["origin"]
            )

    return doc


def get_knowledgeBase_enitities(doc):
    linker = onto_ruler_obj.nlp.get_pipe("scispacy_linker")
    ent_dict = {}
    key_list = ["cui", "matched_term", "aliases", "definition", "tui"]
    for k in key_list:
        ent_dict[k] = []
    df = pd.DataFrame()

    for entity in doc.ents:
        for kb_ent in entity._.kb_ents:
            ent_object = linker.kb.cui_to_entity[kb_ent[0]]
            ent_dict["cui"].append(ent_object.concept_id)
            ent_dict["matched_term"].append(ent_object.canonical_name)
            ent_dict["aliases"].append(ent_object.aliases)
            ent_dict["definition"].append(ent_object.definition)
            ent_dict["tui"].append(ent_object.types)

    return pd.DataFrame.from_dict(ent_dict)


def export_tsv(df: pd.DataFrame, fn: str) -> None:
    fn_path = os.path.join(PARENT_DIR, "data/output/" + fn + ".tsv")
    df.to_csv(fn_path, sep="\t", index=None)


def main():
    batch_size = 10000
    input_dir_path = (
        os.path.join(PARENT_DIR, get_config("input-directory")[0]) + "/*.tsv"
    )
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
        lambda row: onto_tokenize(row)
    )

    input_df["spacy_tokens"] = input_df["spacy_doc_tok"].apply(
        lambda row: get_token_info(row)
    )

    input_df["spacy_kb_ent"] = input_df["spacy_doc_tok"].apply(
        lambda row: get_knowledgeBase_enitities(row)
    )

    kb_df = explode_df(input_df[["id", "spacy_kb_ent"]])
    onto_df = explode_df(input_df[["id", "spacy_tokens"]])
    # nlp_df = doc_to_df(dframcy, input_df[["id", "spacy_doc"]])

    stopwords_file_path = os.path.join(
        PARENT_DIR, get_config("termlist_stopwords")[0]
    )
    stopwords_file = open(stopwords_file_path, "r")
    stopwords = stopwords_file.read().splitlines()

    # onto_df = onto_df.loc[~onto_df["POS"].isin(ignore_pos)]
    onto_df = onto_df.loc[~onto_df["matched_term"].isin(stopwords)]

    onto_df = util.consolidate_rows(onto_df)
    # onto_df = util.get_object_doc_ratio(onto_df)
    onto_df = util.get_column_doc_ratio(onto_df, "object_label")
    onto_df = util.get_column_doc_ratio(onto_df, "matched_term")
    onto_df = util.get_ancestors(onto_df)

    onto_df = onto_df.astype(str).drop_duplicates()
    kb_df = kb_df.astype(str).drop_duplicates()

    export_tsv(kb_df, "umls_ontoRunNER")
    export_tsv(onto_df, "ontology_ontoRunNER")
    # export_tsv(nlp_df, "nlp_object_output")


@click.group()
def cli():
    pass


@cli.group
@cli.command("run-spacy")
def run_spacy_click():
    main()


if __name__ == "__main__":
    freeze_support()
    onto_ruler_obj = OntoRuler()
    cli()

