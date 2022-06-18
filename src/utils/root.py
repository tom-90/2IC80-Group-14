import os

def is_root():
    return os.geteuid() == 0