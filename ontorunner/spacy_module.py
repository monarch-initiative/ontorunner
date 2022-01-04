import os
import glob
from typing import Collection
import spacy
from spacy.language import Language
from spacy.tokens import Span
from ontorunner import PARENT_DIR
from ontorunner import OntoExtractor
from scispacy.linking import EntityLinker
from dframcy import DframCy
import pandas as pd
from multiprocessing import freeze_support
from ontorunner.post import util


@Language.component("onto_extractor")
def onto_extractor(doc):

    matches = onto.matcher(doc)

    spans = [
        Span(doc, start, end, label="ONTOLOGY")
        for matchId, start, end in matches
    ]

    doc.spans["ONTOLOGY"] = spans

    for i, span in enumerate(spans):
        span._.set("has_curies", True)

        for token in span:
            if span.text.lower() in onto.terms.keys():
                token._.set("is_an_onto_term", True)
                token._.set(
                    "object_id", onto.terms[span.text.lower()]["object_id"]
                )
                token._.set(
                    "object_category",
                    onto.terms[span.text.lower()]["object_category"],
                )
                token._.set(
                    "synonym_of", onto.terms[span.text.lower()]["synonym_of"]
                )
                token._.set("origin", onto.terms[span.text.lower()]["origin"])
                token._.set("sentence", span.sent)
                token._.set("start", span.start_char)
                token._.set("end", span.end_char)

    # * This code below causes the following error:
    # * ValueError: [E1010] Unable to set entity information
    # * for token 41 which is included in more than one span
    # * in entities, blocked, missing or outside.
    # Add ENVO labelled spans along with built-in ones
    # doc.ents += tuple(filter_spans(doc.spans["ENVO"]))

    return doc


def get_knowledgeBase_enitities(doc):
    linker = nlp.get_pipe("scispacy_linker")
    ent_dict = {}
    key_list = ["cui", "object_label", "aliases", "definition", "tui"]
    for k in key_list:
        ent_dict[k] = []
    df = pd.DataFrame()

    for entity in doc.ents:
        for kb_ent in entity._.kb_ents:
            ent_object = linker.kb.cui_to_entity[kb_ent[0]]
            ent_dict["cui"].append(ent_object.concept_id)
            ent_dict["object_label"].append(ent_object.canonical_name)
            ent_dict["aliases"].append(ent_object.aliases)
            ent_dict["definition"].append(ent_object.definition)
            ent_dict["tui"].append(ent_object.types)

    return pd.DataFrame.from_dict(ent_dict)


def get_token_info(doc):
    key_list = [
        "object_label",
        "POS",
        "tag",
        "object_id",
        "object_category",
        "synonym_of",
        "origin",
        "sentence",
        "start",
        "end",
    ]
    onto_dict = {}
    for k in key_list:
        onto_dict[k] = []
    df = pd.DataFrame()
    for token in doc:
        if token._.is_an_onto_term:
            onto_dict["object_label"].append(token.text)
            onto_dict["POS"].append(token.pos_)
            onto_dict["tag"].append(token.tag_)
            onto_dict["object_id"].append(token._.object_id)
            onto_dict["object_category"].append(token._.object_category)
            onto_dict["synonym_of"].append(token._.synonym_of)
            onto_dict["origin"].append(token._.origin)
            onto_dict["sentence"].append(token._.sentence)
            onto_dict["start"].append(token._.start)
            onto_dict["end"].append(token._.end)

    return pd.DataFrame.from_dict(onto_dict)


def explode_df(df: pd.DataFrame):
    new_df = pd.DataFrame()
    for _, doc_obj_row in df.iterrows():
        tmp_df = doc_obj_row[1]
        tmp_df.insert(0, "id", doc_obj_row.id)
        new_df = pd.concat([new_df, tmp_df], ignore_index=True)

    new_df = new_df.rename(columns={"id": "document_id"})
    return new_df


# def doc_to_df(dframcy: DframCy, df: pd.DataFrame) -> pd.DataFrame:
#     df_of_df = pd.DataFrame()
#     df_of_df["id"] = df["id"]
#     df_of_df["spacy_doc"] = (
#         df["spacy_doc"].apply(lambda row: dframcy.to_dataframe(row)).to_frame()
#     )

#     return explode_df(df_of_df)


def export_tsv(df: pd.DataFrame, fn: str) -> None:
    fn_path = os.path.join(PARENT_DIR, "data/output/" + fn + ".tsv")
    df.to_csv(fn_path, sep="\t", index=None)


def main():

    nlp.add_pipe("onto_extractor", after="ner")

    nlp.add_pipe(
        "scispacy_linker",
        config={"resolve_abbreviations": True, "linker_name": "umls"},
    )  # Must be one of 'umls' or 'mesh'.

    # dframcy = DframCy(nlp)

    input_dir_path = (
        os.path.join(PARENT_DIR, onto.get_config("input-directory")[0])
        + "/*.tsv"
    )
    input_file_list = glob.glob(input_dir_path)
    list_of_input_dfs = []
    for fn in input_file_list:
        in_df = pd.read_csv(fn, sep="\t", low_memory=False)
        list_of_input_dfs.append(in_df)
    input_df = pd.concat(list_of_input_dfs, axis=0, ignore_index=True)

    input_df["spacy_doc"] = list(
        nlp.pipe(input_df["text"].values, batch_size=1000)
    )

    input_df["spacy_kb_ent"] = input_df["spacy_doc"].apply(
        lambda row: get_knowledgeBase_enitities(row)
    )
    input_df["spacy_tokens"] = input_df["spacy_doc"].apply(
        lambda row: get_token_info(row)
    )

    kb_df = explode_df(input_df[["id", "spacy_kb_ent"]])
    onto_df = explode_df(input_df[["id", "spacy_tokens"]])
    # nlp_df = doc_to_df(dframcy, input_df[["id", "spacy_doc"]])

    # Filter df to remove certain POS'
    """
    List of POS codes
    POS | DESCRIPTION | EXAMPLES
    ADJ | adjective | *big, old, green, incomprehensible, first*
    ADP | adposition | *in, to, during*
    ADV | adverb | *very, tomorrow, down, where, there*
    AUX | auxiliary | *is, has (done), will (do), should (do)*
    CONJ | conjunction | *and, or, but*
    CCONJ | coordinating conjunction | *and, or, but*
    DET | determiner | *a, an, the*
    INTJ | interjection | *psst, ouch, bravo, hello*
    NOUN | noun | *girl, cat, tree, air, beauty*
    NUM | numeral | *1, 2017, one, seventy-seven, IV, MMXIV*
    PART | particle | *’s, not,*
    PRON | pronoun | *I, you, he, she, myself, themselves, somebody*
    PROPN | proper noun | *Mary, John, London, NATO, HBO*
    PUNCT | punctuation | *., (, ), ?*
    SCONJ | subordinating conjunction | *if, while, that*
    SYM | symbol | *$, %, §, ©, +, −, ×, ÷, =, :), 😝*
    VERB | verb | *run, runs, running, eat, ate, eating*
    X | other | *sfpksdpsxmsa*
    SPACE | space

    """
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
    ]
    stopwords_file_path = os.path.join(
        PARENT_DIR, onto.get_config("termlist_stopwords")[0]
    )
    stopwords_file = open(stopwords_file_path, "r")
    stopwords = stopwords_file.read().splitlines()

    onto_df = onto_df.loc[~onto_df["POS"].isin(ignore_pos)]
    onto_df = onto_df.loc[~onto_df["object_label"].isin(stopwords)]

    onto_df = util.consolidate_rows(onto_df)
    onto_df = util.get_object_doc_ratio(onto_df)

    export_tsv(kb_df, "umls_ontoRunNER")
    export_tsv(onto_df, "ontology_ontoRunNER")
    # export_tsv(nlp_df, "nlp_object_output")


if __name__ == "__main__":
    # python -m spacy download en_core_web_sm
    # nlp = spacy.load("en_core_web_sm")
    nlp = spacy.load("en_ner_craft_md")
    freeze_support()
    onto = OntoExtractor.OntoExtractor(nlp)
    main()
