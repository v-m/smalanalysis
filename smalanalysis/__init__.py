import os

def get_baksmali_bin():
    _ROOT = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(_ROOT, 'jar', 'baksmali-2.2.1.jar')