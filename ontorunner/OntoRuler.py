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
    get_config,
)
import pandas as pd
import os
import spacy
from collections import defaultdict
from scispacy.linking import EntityLinker
from spacy.tokens import Doc, Span, Token
from spacy.matcher import PhraseMatcher, Matcher


class OntoRuler(object):
    def __init__(self):
        self.label = "ontology"
        self.phrase_matcher_attr = "LOWER"
        self.multiprocessing = False  # False -> Use single processor; True -> Use multiple processors
        self.processing_threshold = 100_000
        self.terms = {}
        self.list_of_pattern_dicts = []
        self.list_of_obj_docs = []
        self.nlp = spacy.load("en_ner_craft_md")

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
        #     self.phrase_matcher.add(self.label, None, *self.list_of_obj_docs)
        #     with open(TERMS_PICKLED, "rb") as tp:
        #         self.terms = pickle.load(tp)
        # else:

        df = self.get_ont_terms_df()

        if len(df) > self.processing_threshold:
            number_of_processes = 3  # OR multiprocessing.cpu_count() - 1
            self.multiprocessing = True

        # iterate over terms in ontology
        if self.multiprocessing:
            # * Multiprocessing
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
            # * Single process
            for (
                origin,
                object_id,
                object_label,
                description,
                object_category,
            ) in df.to_records(index=False):
                terms, patterns, object_doc = self.get_terms_patterns(
                    (
                        origin,
                        object_id,
                        object_label,
                        description,
                        object_category,
                    )
                )
                self.terms.update(terms)
                self.list_of_pattern_dicts.append(patterns)
                self.list_of_obj_docs.append(object_doc)

        ruler = self.nlp.add_pipe("entity_ruler", after="ner")
        ruler.add_patterns(self.list_of_pattern_dicts)

        self.phrase_matcher.add(self.label, None, *self.list_of_obj_docs)
        # Dump serialized files
        self.nlp.to_disk(CUSTOM_PIPE_DIR)
        with open(TERMS_PICKLED, "wb") as tp:
            pickle.dump(self.terms, tp)
        print("Serialized files dumped!")

        # variables for tokens, spans and docs extensions
        self.token_term_extension = "is_an_ontology_term"
        self.token_id_extension = "object_id"
        self.has_id_extension = "has_curies"

        # set extensions to tokens, spans and docs
        Token.set_extension(
            self.token_term_extension, default=False, force=True
        )
        Token.set_extension(self.token_id_extension, default=False, force=True)
        Token.set_extension("object_category", default=False, force=True)
        Token.set_extension("synonym_of", default=False, force=True)
        Token.set_extension("origin", default=False, force=True)
        Token.set_extension("sentence", default=False, force=True)
        Token.set_extension("start", default=False, force=True)
        Token.set_extension("end", default=False, force=True)

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
        return any([t._.get(self.token_term_extension) for t in tokens])

    def get_ont_terms_df(self):
        cols = [
            "CUI",
            "origin",
            "CURIE",
            "object_label",
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
        origin, object_id, object_label, description, object_category = args[0]
        terms_dict = {}
        pattern_dict = {}

        if "[SYNONYM_OF:" in description:
            synonym = description.split("[SYNONYM_OF:")[-1].rstrip("]")
        else:
            synonym = None

        if object_label is not None and object_label == object_label:
            terms_dict[object_label.lower()] = {
                "object_id": object_id,
                "object_category": object_category,
                "synonym_of": synonym,
                "origin": origin,
            }
            pattern_dict["id"] = object_id
            pattern_dict["label"] = origin.split(".")[0]
            pattern_dict["pattern"] = object_label

        return terms_dict, pattern_dict, self.nlp(object_label)
