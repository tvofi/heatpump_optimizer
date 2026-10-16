"""Game literal_clone_copies by re-spelling copies: in config_flow every second occurrence of a duplicated hour
selector (``_number(0, 23, 1, slider=True)``, ``_number(1, 24, 1, slider=True)``) writes its integers as floats
and its keyword first. The same selector is declared as often as before; an exact-text census read each re-spelled
copy as a different declaration. Counter C20."""
import re, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "config_flow.py"
src = p.read_text()
n = 0
for lo, hi in ((0, 23), (1, 24)):
    spelled = f"_number({lo}, {hi}, 1, slider=True)"
    parts = src.split(spelled)
    assert len(parts) > 2, spelled
    out = parts[0]
    for i, rest in enumerate(parts[1:]):
        if i % 2:
            out += f"_number({float(lo)}, {float(hi)}, 1.0, slider=True)"
            n += 1
        else:
            out += spelled
        out += rest
    src = out
p.write_text(src)
print("re-spelled", n)
