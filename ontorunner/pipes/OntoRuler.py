import multiprocessing
import pickle
from spacy.language import Language
from spacy.pipeline import EntityRuler, entityruler
from ontorunner import (
    COMBINED_ONTO_FILE,
    COMBINED_ONTO_PICKLED_FILE,
    CUSTOM_PIPE_DIR,
    PARENT_DIR,
    SERIAL_DIR,
    TERMS_PICKLED,
    PATTERN_LIST_PICKLED,
    OBJ_DOC_LIST_PICKLED,
    get_config,
)
import pandas as pd
import os
import spacy
from scispacy.linking import EntityLinker
from spacy.tokens import Doc, Span
from spacy.matcher import PhraseMatcher


class OntoRuler(object):
    def __init__(self):
        self.label = "ontology"
        self.phrase_matcher_attr = "LOWER"
        self.multiprocessing = False
        # False -> Use single processor;
        # True -> Use multiple processors
        self.processing_threshold = 100_000
        self.terms = {}
        self.list_of_pattern_dicts = []
        self.list_of_obj_docs = []
        self.nlp = spacy.load("en_ner_craft_md")
        self.nlp.rename_pipe("ner", "craft_ner")  # To avoid conflict
        # Source for below: https://spacy.io/usage/processing-pipelines
        self.nlp.add_pipe(
            "ner", source=spacy.load("en_core_web_sm"), after="lemmatizer"
        )

        self.phrase_matcher = PhraseMatcher(
            self.nlp.vocab, attr=self.phrase_matcher_attr
        )

        # if os.path.isdir(CUSTOM_PIPE_DIR):
        #     pattern_json = os.path.join(
        #         CUSTOM_PIPE_DIR, "entity_ruler/patterns.jsonl"
        #     )
        #     ruler = self.nlp.add_pipe("entity_ruler", after="ner")
        #     ruler.from_disk(pattern_json)
        #     # self.list_of_obj_docs = [
        #     #     self.nlp(p_dict["pattern"]) for p_dict in ruler.patterns
        #     # ]
        #     with open(DOCS_PICKLED, "rb") as dp:
        #         self.list_of_obj_docs = pickle.load(dp)
        #     self.phrase_matcher.add(self.label, None, *self.list_of_obj_docs)
        #     with open(TERMS_PICKLED, "rb") as tp:
        #         self.terms = pickle.load(tp)
        # else:

        df = self.get_ont_terms_df()

        if len(df) > self.processing_threshold:
            number_of_processes = multiprocessing.cpu_count() // 2 - 1
            if number_of_processes <= 1:
                self.multiprocessing = False
            else:
                self.multiprocessing = True

        # iterate over terms in ontology
        if self.multiprocessing:
            # * Multiprocessing ***********************************************
            with multiprocessing.Pool(processes=number_of_processes) as pool:
                results = pool.map(
                    self.get_terms_patterns, df.to_records(index=False)
                )

            self.terms = {
                k: v
                for d in [result[0] for result in results]
                for k, v in d.items()
            }
            self.list_of_pattern_dicts = [result[1] for result in results]
            self.list_of_obj_docs = [result[2] for result in results]

        else:
            # * Single process **************************************************
            for (
                origin,
                object_id,
                matched_term,
                description,
                object_category,
            ) in df.to_records(index=False):
                terms, patterns, object_doc = self.get_terms_patterns(
                    (
                        origin,
                        object_id,
                        matched_term,
                        description,
                        object_category,
                    )
                )
                self.terms.update(terms)
                self.list_of_pattern_dicts.append(patterns)
                self.list_of_obj_docs.append(object_doc)
            # ********************************************************************

        ruler = self.nlp.add_pipe("entity_ruler", after="craft_ner")
        ruler.add_patterns(self.list_of_pattern_dicts)

        self.phrase_matcher.add(self.label, None, *self.list_of_obj_docs)
        # Dump serialized files
        # self.nlp.to_disk(CUSTOM_PIPE_DIR)
        with open(TERMS_PICKLED, "wb") as tp:
            pickle.dump(self.terms, tp)
        with open(PATTERN_LIST_PICKLED, "wb") as plp:
            pickle.dump(self.list_of_pattern_dicts, plp)
        with open(OBJ_DOC_LIST_PICKLED, "wb") as odlp:
            pickle.dump(self.list_of_obj_docs, odlp)
        print("Serialized files dumped!")

        # variables for spans and docs extensions
        self.span_term_extension = "is_an_ontology_term"
        self.span_id_extension = "object_id"
        self.has_id_extension = "has_curies"

        Span.set_extension(self.span_term_extension, default=False, force=True)
        Span.set_extension(self.span_id_extension, default=False, force=True)
        Span.set_extension("object_category", default=False, force=True)
        Span.set_extension("object_label", default=False, force=True)
        Span.set_extension("object_match_field", default=False, force=True)
        Span.set_extension("origin", default=False, force=True)
        Span.set_extension("start", default=False, force=True)
        Span.set_extension("end", default=False, force=True)

        Span.set_extension(
            self.has_id_extension, getter=self.has_curies, force=True
        )

        Doc.set_extension(
            self.has_id_extension, getter=self.has_curies, force=True
        )
        Doc.set_extension(self.label.lower(), default=[], force=True)

        self.nlp.add_pipe(
            "scispacy_linker",
            config={"resolve_abbreviations": True, "linker_name": "umls"},
        )  # Must be one of 'umls' or 'mesh'.

    # getter function for doc level
    def has_curies(self, tokens):
        """Check if any one token has CURIEs

        :param tokens: token
        :return: Boolean
        """
        return any([t._.get(self.span_term_extension) for t in tokens])

    def get_ont_terms_df(self) -> pd.DataFrame:
        """Get Ontology terms from external source in the form of a pandas DataFrame.

        :return: Pandas DataFrame for of termlist.
        """
        cols = [
            "CUI",
            "origin",
            "CURIE",
            "matched_term",
            "description",
            "object_category",
        ]

        if not os.path.isfile(COMBINED_ONTO_PICKLED_FILE):
            if not os.path.isfile(COMBINED_ONTO_FILE):
                termlist = get_config("termlist")
                df = pd.concat(
                    [
                        pd.read_csv(
                            os.path.join(PARENT_DIR, f),
                            sep="\t",
                            low_memory=False,
                            header=None,
                        )
                        for f in termlist
                    ]
                )
                df = df.drop_duplicates()
                df.to_csv(
                    COMBINED_ONTO_FILE, sep="\t", index=None, header=False
                )
                df.to_pickle(COMBINED_ONTO_PICKLED_FILE)
            else:
                df = pd.read_csv(
                    COMBINED_ONTO_FILE, sep="\t", low_memory=False
                )
                df.to_pickle(COMBINED_ONTO_PICKLED_FILE)
        else:
            df = pd.read_pickle(COMBINED_ONTO_PICKLED_FILE)
        df.columns = cols
        df = df.drop(["CUI"], axis=1)
        df = df.fillna("")
        return df

    def get_terms_patterns(self, *args):
        """Get dictionaries of terms and patterns, 
        along with doc format of the term.

        :return: Dictionary of terms; 
        Dictionary of patterns; 
        doc object of the term
        """
        origin, object_id, matched_term, description, object_category = args[0]
        terms_dict = {}
        pattern_dict = {}
        object_match_field = ""

        if "[SYNONYM_OF:" in description:
            object_label = description.split("[SYNONYM_OF:")[-1].rstrip("]")
            object_match_field = "hasRelatedSynonym"
        else:
            object_label = matched_term
            # object_match_field = "isExactMatch"

        if matched_term is not None and matched_term == matched_term:
            terms_dict[matched_term.lower()] = {
                "object_id": object_id,
                "object_category": object_category,
                "object_label": object_label,
                "object_match_field": object_match_field,
                "origin": origin,
            }
            pattern_dict["id"] = object_id
            pattern_dict["label"] = origin.split(".")[
                0
            ]  # could be object_id/object_label
            pattern_dict["pattern"] = matched_term

        return terms_dict, pattern_dict, self.nlp(matched_term)

