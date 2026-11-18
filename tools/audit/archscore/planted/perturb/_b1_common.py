import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from _lib import COORD, read, find_method


def as_float_source(new_name: str) -> str:
    src = read(COORD)
    fn = find_method(src, None, "_as_float")
    text = "".join(src.splitlines(keepends=True)[fn.lineno - 1:fn.end_lineno])
    return text.replace("def _as_float(", f"def {new_name}(", 1)
