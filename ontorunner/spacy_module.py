import os
from pandas.core.frame import DataFrame
import spacy
from spacy.language import Language
from spacy.tokens import Span

# from spacy.util import filter_spans
from . import PARENT_DIR, OntoExtractor
from .ss_module import TEXT, input_df
import scispacy
from scispacy.linking import EntityLinker
from dframcy import DframCy
import pandas as pd
from multiprocessing import freeze_support

# python -m spacy download en_core_web_sm
# nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_ner_craft_md")
onto = OntoExtractor.OntoExtractor(nlp)

output_columns = [
    "document_id",
    "object_category",
    "start_position",
    "end_position",
    "matched_term",
    "preferred_form",
    "object_label",
    "doc_count",
    "object_label_doc_ratio",
    "match_type",
    "levenshtein_distance",
    "jaccard_index",
    "monge_elkan",
    "object_id",
    "sentence_id",
    "umls_cui",
    "origin",
    "sentence",
    "object_sentence_%",
]


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
            token._.set("is_an_onto_term", True)
            token._.set("curie", onto.terms[span.text.lower()]["id"])
            token._.set("category", onto.terms[span.text.lower()]["category"])
            token._.set(
                "synonym_of", onto.terms[span.text.lower()]["synonym_of"]
            )
            token._.set("source", onto.terms[span.text.lower()]["source"])
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
    ent_list = []

    for entity in doc.ents:
        for kb_ent in entity._.kb_ents:
            ent_dict = {}
            ent_object = linker.kb.cui_to_entity[kb_ent[0]]
            ent_dict["cui"] = ent_object.concept_id
            ent_dict["name"] = ent_object.canonical_name
            ent_dict["aliases"] = ent_object.aliases
            ent_dict["definition"] = ent_object.definition
            ent_dict["tui"] = ent_object.types
            ent_list.append(ent_dict)
    return ent_list


def get_token_info(doc):
    onto_dict = {}
    for token in doc:
        if token._.is_an_onto_term:
            onto_dict["name"] = token.text
            onto_dict["POS"] = token.pos_
            onto_dict["tag"] = token.tag_
            onto_dict["curie"] = token._.curie
            onto_dict["category"] = token._.category
            onto_dict["synonym_of"] = token._.synonym_of
            onto_dict["source"] = token._.source
            onto_dict["sentence"] = token._.sentence
            onto_dict["start"] = token._.start
            onto_dict["end"] = token._.end

    return onto_dict


def doc_to_df(dframcy: DframCy, df: pd.DataFrame) -> pd.DataFrame:
    # dframcy_df = pd.DataFrame()
    # for idx, row in df.iterrows():
    #     tmp_df = dframcy.to_dataframe(row.spacy_doc)
    #     tmp_df.insert(0, "id", row.id)
    #     dframcy_df = pd.concat([dframcy_df, tmp_df])
    # return dframcy_df
    df_of_df = pd.DataFrame()
    dframcy_df = pd.DataFrame()
    df_of_df["id"] = df["id"]
    df_of_df["spacy_doc"] = (
        df["spacy_doc"].apply(lambda row: dframcy.to_dataframe(row)).to_frame()
    )

    for _, doc_obj_row in df_of_df.iterrows():
        tmp_df = doc_obj_row.spacy_doc
        tmp_df.insert(0, "id", doc_obj_row.id)
        dframcy_df = pd.concat([dframcy_df, tmp_df], ignore_index=True)

    return dframcy_df


def export_tsv(df: pd.DataFrame, fn: str) -> None:
    path = os.path.join(PARENT_DIR, "data/output/" + fn + ".tsv")
    df.to_csv(fn, sep="\t", index=None)


def main():
    nlp.add_pipe("onto_extractor", after="ner")

    nlp.add_pipe(
        "scispacy_linker",
        config={"resolve_abbreviations": True, "linker_name": "umls"},
    )  # Must be one of 'umls' or 'mesh'.

    dframcy = DframCy(nlp)

    input_df["spacy_doc"] = list(
        nlp.pipe(input_df["text"].values, batch_size=100)
    )

    input_df["spacy_kb_ent"] = input_df["spacy_doc"].apply(
        lambda row: get_knowledgeBase_enitities(row)
    )
    input_df["spacy_tokens"] = input_df["spacy_doc"].apply(
        lambda row: get_token_info(row)
    )

    kb_df = input_df[["id", "spacy_kb_ent"]]
    onto_df = input_df[["id", "spacy_tokens"]]
    nlp_df = doc_to_df(dframcy, input_df[["id", "spacy_doc"]])

    export_tsv(kb_df, "kb_entities_output")
    export_tsv(onto_df, "onto_tokens_output")
    export_tsv(nlp_df, "nlp_object_output")


if __name__ == "__main__":
    main()
