"""Game literal_clone_copies by respelling positional arguments as keywords: in config_flow the copies of
``_number(1, 24, 1, slider=True)`` after the first pass a growing tail of their arguments by keyword
(``step=1``, then ``maximum=24``, then ``minimum=1``), so no two copies share a spelling. The call binds the same
parameters; a census that sorted keywords but never bound positionals read each copy as distinct (#2373
round-1 review, P2). Counter C20."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "config_flow.py"
s = p.read_text()
spelled = "_number(1, 24, 1, slider=True)"
variants = ["_number(1, 24, step=1, slider=True)", "_number(1, maximum=24, step=1, slider=True)",
            "_number(minimum=1, maximum=24, step=1, slider=True)"]
parts = s.split(spelled)
assert 4 <= len(parts) <= len(variants) + 2, len(parts)
out = parts[0] + spelled + parts[1]
for i, rest in enumerate(parts[2:]):
    out += variants[i] + rest
p.write_text(out)
print("respelled", len(parts) - 2)
