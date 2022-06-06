"""OntoRuler class for running Spacy."""
import multiprocessing
import os
import pickle
from pathlib import Path

import pandas as pd
import spacy
from scispacy.linking import EntityLinker  # noqa F401
from spacy.language import Language  # noqa F401
from spacy.matcher import PhraseMatcher
from spacy.pipeline import entityruler  # noqa F401
from spacy.tokens import Doc, Span

from ontorunner import (DATA_DIR, ONTO_TERMS_FILENAME,
                        PATTERN_LIST_PICKLED_FILENAME,
                        PHRASE_MATCHER_PICKLED_FILENAME, SERIAL_DIR_NAME,
                        SETTINGS_FILE_PATH, TERMS_DIR_NAME,
                        TERMS_PICKLED_FILENAME, _get_config)


class OntoRuler(object):
    """OntoRuler class."""

    def __init__(
        self,
        data_dir: Path = DATA_DIR,
        settings_filepath: Path = SETTINGS_FILE_PATH,
        linker: str = "umls",  # Must be one of 'umls' or 'mesh'.
        to_pickle: bool = True,
    ):
        # self.parent_dir = parent_dir
        self.data_dir = data_dir
        self.serial_dir = os.path.join(self.data_dir, SERIAL_DIR_NAME)
        self.terms_dir = os.path.join(self.data_dir, TERMS_DIR_NAME)

        self.phrase_matcher_pickled = os.path.join(
            self.serial_dir, PHRASE_MATCHER_PICKLED_FILENAME
        )
        self.terms_pickled = os.path.join(self.serial_dir, TERMS_PICKLED_FILENAME)
        self.pattern_list_pickled = os.path.join(
            self.serial_dir, PATTERN_LIST_PICKLED_FILENAME
        )
        self.phrase_matcher_pickled = os.path.join(
            self.serial_dir, PHRASE_MATCHER_PICKLED_FILENAME
        )
        self.settings_file = settings_filepath
        self.combined_onto_file = os.path.join(self.terms_dir, ONTO_TERMS_FILENAME)
        self.combined_onto_pickle = os.path.join(
            self.serial_dir, (ONTO_TERMS_FILENAME + ".pickle")
        )
        self.label = "ontology"
        self.phrase_matcher_attr = "LOWER"
        self.multiprocessing = False
        # False -> Use single processor;
        # True -> Use multiple processors
        self.processing_threshold = 100_000
        self.terms = {}
        self.list_of_pattern_dicts = []
        self.list_of_doc_obj = []
        self.nlp = spacy.load("en_ner_craft_md")
        self.nlp.rename_pipe("ner", "craft_ner")  # To avoid conflict
        # Source for below: https://spacy.io/usage/processing-pipelines
        self.nlp.add_pipe(
            "ner", source=spacy.load("en_core_web_sm"), before="craft_ner"
        )

        if os.path.isfile(self.phrase_matcher_pickled):
            print("Found serialized files!")
            with open(os.path.join(self.terms_pickled), "rb") as tf:
                self.terms = pickle.load(tf)
            with open(self.pattern_list_pickled, "rb") as plp:
                self.list_of_pattern_dicts = pickle.load(plp)
            with open(self.phrase_matcher_pickled, "rb") as pmp:
                self.phrase_matcher = pickle.load(pmp)
            print("Serialized files imported!")

        else:
            self.extract_termlist_info(to_pickle=to_pickle)

        ruler = self.nlp.add_pipe("entity_ruler", after="craft_ner")
        ruler.add_patterns(self.list_of_pattern_dicts)
        print("Patterns added!")

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

        Span.set_extension(self.has_id_extension, getter=self.has_curies, force=True)

        Doc.set_extension(self.has_id_extension, getter=self.has_curies, force=True)
        Doc.set_extension(self.label.lower(), default=[], force=True)
        print("Extensions set!")

        self.nlp.add_pipe(
            "scispacy_linker",
            config={"resolve_abbreviations": True, "linker_name": linker},
        )
        print("SciSpacy loaded!")

    # getter function for doc level
    def has_curies(self, tokens):
        """Check if any one token has CURIEs

        :param tokens: token
        :return: Boolean
        """
        return any([t._.get(self.span_term_extension) for t in tokens])

    def get_ont_terms_df(self, to_pickle) -> pd.DataFrame:
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

        if not os.path.isfile(self.combined_onto_pickle):
            if not os.path.isfile(self.combined_onto_file):
                termlist = _get_config("termlist", self.settings_file)
                df = pd.concat(
                    [
                        pd.read_csv(
                            os.path.join(self.terms_dir, f),
                            sep="\t",
                            low_memory=False,
                            header=None,
                        )
                        for f in termlist
                    ]
                )
                df = df.drop_duplicates()
                df.to_csv(self.combined_onto_file, sep="\t", index=None, header=False)
                df.to_pickle(self.combined_onto_pickle)
            else:
                df = pd.read_csv(self.combined_onto_file, sep="\t", low_memory=False)
                if to_pickle:
                    df.to_pickle(self.combined_onto_pickle)
        else:
            df = pd.read_pickle(self.combined_onto_pickle)
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

    def extract_termlist_info(self, to_pickle: bool):
        df = self.get_ont_terms_df(to_pickle=to_pickle)

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
                results = pool.map(self.get_terms_patterns, df.to_records(index=False))

            self.terms = {
                k: v for d in [result[0] for result in results] for k, v in d.items()
            }
            self.list_of_pattern_dicts = [result[1] for result in results]
            self.list_of_doc_obj = [result[2] for result in results]

        else:
            # * Single process **********************************************
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
                self.list_of_doc_obj.append(object_doc)
            # ***************************************************************

        self.phrase_matcher = PhraseMatcher(
            self.nlp.vocab, attr=self.phrase_matcher_attr
        )
        self.phrase_matcher.add(self.label, None, *self.list_of_doc_obj)

        if to_pickle:
            # Dump serialized files
            # self.nlp.to_disk(CUSTOM_PIPE_DIR)
            with open(self.terms_pickled, "wb") as tp:
                pickle.dump(self.terms, tp)
            with open(self.pattern_list_pickled, "wb") as plp:
                pickle.dump(self.list_of_pattern_dicts, plp)
            # with open(OBJ_DOC_LIST_PICKLED, "wb") as odlp:
            #     pickle.dump(self.list_of_doc_obj, odlp)
            with open(self.phrase_matcher_pickled, "wb") as pmp:
                pickle.dump(self.phrase_matcher, pmp)

            print("Serialized files dumped!")
