"""Game literal_clone_copies by re-spelling copies: in config_flow each copy of a duplicated hour selector
(``_number(0, 23, 1, slider=True)``, ``_number(1, 24, 1, slider=True)``) after the first is written with a
different mix of float and integer bounds, so no two copies share a spelling. The same selector is declared as
often as before; an exact-text census read each re-spelled copy as a different declaration. Counter C20."""
import sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "config_flow.py"
src = p.read_text()
n = 0
for lo, hi in ((0, 23), (1, 24)):
    spelled = f"_number({lo}, {hi}, 1, slider=True)"
    variants = [f"_number({lo}.0, {hi}, 1, slider=True)", f"_number({lo}, {hi}.0, 1, slider=True)",
                f"_number({lo}, {hi}, 1.0, slider=True)", f"_number({lo}.0, {hi}.0, 1, slider=True)",
                f"_number({lo}.0, {hi}, 1.0, slider=True)", f"_number({lo}, {hi}.0, 1.0, slider=True)"]
    parts = src.split(spelled)
    assert 2 < len(parts) <= len(variants) + 2, (spelled, len(parts))
    out = parts[0] + spelled + parts[1]
    for i, rest in enumerate(parts[2:]):
        out += variants[i] + rest
        n += 1
    src = out
p.write_text(src)
print("re-spelled", n)
