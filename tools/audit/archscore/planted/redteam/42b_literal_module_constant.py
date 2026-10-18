"""Game literal_clone_copies by hoisting a bound into module constants: in config_flow every copy of
``_number(1, 24, 1, slider=True)`` after the first reads its upper bound from its own module constant
(``_LAST_HOUR_<i> = 24``). The same selector is declared as often as before; a census that inlined only
function locals read each copy as a different declaration (#2373 round-1 review, P1). Counter C21."""
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
    out += f"_number(1, _LAST_HOUR_{i}, 1, slider=True)" + rest
anchor = "\ndef _number("
assert out.count(anchor) == 1
out = out.replace(anchor, "\n" + "".join(f"_LAST_HOUR_{i} = 24\n" for i in range(len(parts) - 2)) + "\n" + anchor, 1)
p.write_text(out)
print("hoisted", len(parts) - 2)
