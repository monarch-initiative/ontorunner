"""Post process the NER results."""
import os

from ontorunner import DATA_DIR

NODE_AND_EDGE_NAME = "nodes_and_edges"

NODE_AND_EDGE_DIR = os.path.join(DATA_DIR, NODE_AND_EDGE_NAME)
SUBCLASS_PREDICATE = "biolink:subclass_of"
SUBCLASS_RELATION = "rdfs:subClassOf"
