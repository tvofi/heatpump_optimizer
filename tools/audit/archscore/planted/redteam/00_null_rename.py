"""Null control: rename away.py's private helper _setback_fields -> _setback_field_values everywhere."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
n = 0
for p in sorted(pkg(root).glob("*.py")):
    s = p.read_text()
    t = re.sub(r"\b_setback_fields\b", "_setback_field_values", s)
    if t != s:
        n += 1
        p.write_text(t)
print("files", n)
