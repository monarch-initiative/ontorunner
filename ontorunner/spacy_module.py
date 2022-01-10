import os
from ontorunner import PARENT_DIR, SETTINGS_FILE, get_config
from ontorunner.OntoRuler import OntoRuler
from glob import glob
import pandas as pd
from spacy.tokens import Span
from multiprocessing import freeze_support
from ontorunner.post import util


def get_token_info(doc):
    key_list = [
        "matched_term",
        "POS",
        "tag",
        "object_id",
        "object_category",
        "object_label",
        "object_match_field",
        "origin",
        "sentence",
        "start",
        "end",
    ]
    onto_dict = {}
    for k in key_list:
        onto_dict[k] = []

    for token in doc:
        if token._.is_an_ontology_term:
            onto_dict["matched_term"].append(token.text)
            onto_dict["POS"].append(token.pos_)
            onto_dict["tag"].append(token.tag_)
            onto_dict["object_id"].append(token._.object_id)
            onto_dict["object_category"].append(token._.object_category)
            onto_dict["object_label"].append(token._.object_label)
            onto_dict["object_match_field"].append(token._.object_match_field)
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


def onto_tokenize(doc):
    # matches = onto_ruler_obj.match(doc)
    matches = onto_ruler_obj.phrase_matcher(doc)

    spans = [
        Span(doc, start, end, label=onto_ruler_obj.label)
        for matchId, start, end in matches
    ]
    doc.spans[onto_ruler_obj.label] = spans

    for i, span in enumerate(spans):
        span._.set("has_curies", True)

        for token in span:
            if span.text.lower() in onto_ruler_obj.terms.keys():
                token._.set(onto_ruler_obj.token_term_extension, True)
                token._.set(
                    "object_id",
                    onto_ruler_obj.terms[span.text.lower()]["object_id"],
                )
                token._.set(
                    "object_category",
                    onto_ruler_obj.terms[span.text.lower()]["object_category"],
                )
                token._.set(
                    "object_label",
                    onto_ruler_obj.terms[span.text.lower()]["object_label"],
                )
                token._.set(
                    "object_match_field",
                    onto_ruler_obj.terms[span.text.lower()][
                        "object_match_field"
                    ],
                )
                token._.set(
                    "origin", onto_ruler_obj.terms[span.text.lower()]["origin"]
                )
                token._.set("sentence", span.sent)
                token._.set("start", span.start_char)
                token._.set("end", span.end_char)
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
        onto_ruler_obj.nlp.pipe(input_df["text"].values, batch_size=1000)
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
        PARENT_DIR, get_config("termlist_stopwords")[0]
    )
    stopwords_file = open(stopwords_file_path, "r")
    stopwords = stopwords_file.read().splitlines()

    onto_df = onto_df.loc[~onto_df["POS"].isin(ignore_pos)]
    onto_df = onto_df.loc[~onto_df["matched_term"].isin(stopwords)]

    onto_df = util.consolidate_rows(onto_df)
    onto_df = util.get_object_doc_ratio(onto_df)

    export_tsv(kb_df, "umls_ontoRunNER")
    export_tsv(onto_df, "ontology_ontoRunNER")
    # export_tsv(nlp_df, "nlp_object_output")


if __name__ == "__main__":
    freeze_support()
    onto_ruler_obj = OntoRuler()
    main()

