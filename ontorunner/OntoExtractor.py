# Sourced from : https://linuskohl.medium.com/extracting-and-linking-ontology-terms-from-text-7806ae8d8189
from multiprocessing.spawn import freeze_support
import re
from spacy.tokens import Doc, Span, Token
from spacy.matcher import PhraseMatcher
import pandas as pd
from ontorunner import (
    PARENT_DIR,
    SETTINGS_FILE,
    SETTINGS_FILE,
    COMBINED_ONTO_PICKLED_FILE,
    COMBINED_ONTO_FILE,
)
import os
import configparser
import multiprocessing


class OntoExtractor(object):
    name = "Ontology Extractor"

    def __init__(self, nlp):
        self.label = "onto"
        self.terms = {}
        self.patterns = []
        self.multiprocessing = False  # False -> Use single processor; True -> Use multiple processors
        self.processing_threshold = 100_000
        self.nlp = nlp

        df = self.get_ont_terms_df()

        if len(df) > self.processing_threshold:
            number_of_processes = 3  # OR multiprocessing.cpu_count() - 1
            self.multiprocessing = True

        # iterate over terms in ontology
        if self.multiprocessing:
            # * Multiprocessing attempt
            with multiprocessing.Pool(processes=number_of_processes) as pool:
                results = pool.map(
                    self.get_terms_patterns, df.to_records(index=False)
                )

            self.terms = {
                k: v
                for d in [result[0] for result in results]
                for k, v in d.items()
            }
            self.patterns = [result[1] for result in results]

        else:
            # * Single process
            for (
                origin,
                object_id,
                object_label,
                description,
                object_category,
            ) in df.to_records(index=False):
                terms, patterns = self.get_terms_patterns(
                    (
                        origin,
                        object_id,
                        object_label,
                        description,
                        object_category,
                    )
                )
                self.terms.update(terms)
                self.patterns.append(patterns)

        # initialize matcher and add patterns
        self.matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        self.matcher.add(
            self.label, None, *self.patterns, on_match=self.resolve_substrings
        )

        # variables for tokens, spans and docs extensions
        self.token_term_extension = "is_an_" + self.label.lower() + "_term"
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

    # * Multiprocessing relevant ****************************************
    def get_terms_patterns(self, *args):
        origin, object_id, object_label, description, object_category = args[0]
        terms = {}

        if "[SYNONYM_OF:" in description:
            synonym = description.split("[SYNONYM_OF:")[-1].rstrip("]")
        else:
            synonym = None

        if object_label is not None and object_label == object_label:
            terms[object_label.lower()] = {
                "object_id": object_id,
                "object_category": object_category,
                "synonym_of": synonym,
                "origin": origin,
            }

        return terms, self.nlp(object_label)

    # ********************************************************************

    # getter function for doc level
    def has_curies(self, tokens):
        return any([t._.get(self.token_term_extension) for t in tokens])

    def get_config(self, param):
        read_config = configparser.ConfigParser()
        read_config.read(SETTINGS_FILE)
        main_section = dict(read_config.items("Main"))
        if param == "termlist":
            return [
                v
                for k, v in main_section.items()
                if param in k and re.search(r"\d", k)
            ]
        else:
            return [v for k, v in main_section.items() if param in k]

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
                termlist = self.get_config("termlist")
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
            # df = pd.read_csv(COMBINED_ONTO_FILE, sep="\t", low_memory=False)
            df = pd.read_pickle(COMBINED_ONTO_PICKLED_FILE)
        df.columns = cols
        df = df.drop(["CUI"], axis=1)
        df = df.fillna("")
        return df

    def resolve_substrings(matcher, doc, i, matches):
        # Get the current match and create
        # tuple of entity label, start and end.
        # Append entity to the doc's entity.
        # (Don't overwrite doc.ents!)

        match_id, start, end = matches[i]
        entity = Span(doc, start, end, label="DUPLICATE")
        doc.ents += (entity,)
