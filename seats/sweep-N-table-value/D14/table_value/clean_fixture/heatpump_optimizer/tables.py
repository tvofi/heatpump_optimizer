"""Null-control fixture: nothing here is a numeric data table of >= 3 leaves."""
NAMES = {"a": "alpha", "b": "beta", "c": "gamma"}   # strings only
PAIR = (0.5, 5.0)                                    # two leaves
FLAGS = (True, False, True)                          # bools are not numeric leaves
LABELS = ["x", "y", "z"]


class Holder:
    INNER = {"k": 1.0, "m": 2.0, "n": 3.0}           # class scope, not module scope
