# Sourced from : https://linuskohl.medium.com/extracting-and-linking-ontology-terms-from-text-7806ae8d8189
import re
from spacy.tokens import Doc, Span, Token
from spacy.matcher import PhraseMatcher
import pandas as pd
from . import PARENT_DIR
import os
import configparser

# ENVO = "../data/terms/envo_syn_termlist.tsv"
TERMS_DIR = os.path.join(PARENT_DIR, "data/terms")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.ini")
COMBINED_ONTO_FILE = os.path.join(TERMS_DIR, "onto_termlist.tsv")


class OntoExtractor(object):
    name = "Ontology Extractor"

    def __init__(self, nlp):
        self.label = "onto"
        self.terms = {}
        self.patterns = []

        df = self.get_ont_terms_df()

        # iterate over terms in ontology
        for source, curie, name, description, category in df.to_records(
            index=False
        ):
            if "[SYNONYM_OF:" in description:
                synonym = description.split("[SYNONYM_OF:")[-1].rstrip("]")
            else:
                synonym = None

            if name is not None:
                self.terms[name.lower()] = {
                    "id": curie,
                    "category": category,
                    "synonym_of": synonym,
                    "source": source,
                }
                self.patterns.append(nlp(name))

        # initialize matcher and add patterns
        self.matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        self.matcher.add(
            self.label, None, *self.patterns, on_match=self.resolve_substrings
        )

        # variables for tokens, spans and docs extensions
        self.token_term_extension = "is_an_" + self.label.lower() + "_term"
        self.token_id_extension = "curie"
        self.has_id_extension = "has_curies"

        # set extensions to tokens, spans and docs
        Token.set_extension(
            self.token_term_extension, default=False, force=True
        )
        Token.set_extension(self.token_id_extension, default=False, force=True)
        Token.set_extension("category", default=False, force=True)
        Token.set_extension("synonym_of", default=False, force=True)
        Token.set_extension("source", default=False, force=True)
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

    # getter function for doc level
    def has_curies(self, tokens):
        return any([t._.get(self.token_term_extension) for t in tokens])

    def get_termlist(self):
        read_config = configparser.ConfigParser()
        read_config.read(SETTINGS_FILE)
        main_section = dict(read_config.items("Main"))
        return [
            v
            for k, v in main_section.items()
            if "termlist" in k and re.search(r"\d", k)
        ]

    def get_ont_terms_df(self):
        cols = [
            "CUI",
            "source",
            "CURIE",
            "name",
            "description",
            "category",
        ]

        if not os.path.isfile(COMBINED_ONTO_FILE):
            termlist = self.get_termlist()
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
            df.to_csv(COMBINED_ONTO_FILE, sep="\t", index=None, header=False)
        else:
            df = pd.read_csv(COMBINED_ONTO_FILE, sep="\t", low_memory=False)
        df.columns = cols
        df = df.drop(["CUI"], axis=1)
        return df

    def resolve_substrings(matcher, doc, i, matches):
        # Get the current match and create
        # tuple of entity label, start and end.
        # Append entity to the doc's entity.
        # (Don't overwrite doc.ents!)

        match_id, start, end = matches[i]
        entity = Span(doc, start, end, label="DUPLICATE")
        doc.ents += (entity,)

