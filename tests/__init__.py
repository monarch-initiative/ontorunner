import os
from posix import listdir


def cleanup(dir):
    for f in listdir(dir):
        if f != "README.txt":
            os.remove(os.path.join(dir, f))
