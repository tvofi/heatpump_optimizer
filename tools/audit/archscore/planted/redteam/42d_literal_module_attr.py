"""Game literal_clone_copies by reading a bound through a module binding: in config_flow every copy of
``_number(1, 24, 1, slider=True)`` after the first reads its upper bound as ``_rt_c.LAST_HOUR_<i>``, with
``from . import const as _rt_c`` and each ``LAST_HOUR_<i> = 24`` appended to const.py. The same selector is
declared as often as before; a census that folded only ``from .m import X`` constants read each copy as a
different declaration (#2373 round-2 review, P5). Counter C21."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "config_flow.py"
s = p.read_text()
spelled = "_number(1, 24, 1, slider=True)"
parts = s.split(spelled)
assert len(parts) >= 4, len(parts)
out = parts[0] + spelled + parts[1]
for i, rest in enumerate(parts[2:]):
    out += f"_number(1, _rt_c.LAST_HOUR_{i}, 1, slider=True)" + rest
anchor = "\ndef _number("
assert out.count(anchor) == 1
out = out.replace(anchor, "\nfrom . import const as _rt_c\n\n" + anchor, 1)
p.write_text(out)
c = pkg(root) / "const.py"
c.write_text(c.read_text() + "".join(f"\nLAST_HOUR_{i} = 24" for i in range(len(parts) - 2)) + "\n")
print("read through the binding", len(parts) - 2)
