import os
from posix import listdir

# If the import below is removed,
# pytest complains about duplicate kwargs.
from ontorunner.spacy_module import run_spacy  # noqa: F401


def cleanup(dir):
    for f in listdir(dir):
        if f != "README.txt":
            os.remove(os.path.join(dir, f))
