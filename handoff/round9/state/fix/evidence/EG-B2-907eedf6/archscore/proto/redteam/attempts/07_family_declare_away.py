"""Game family_splits: for every split family, the members outside its longest run are
re-declared into singleton families (ENTITY_FAMILY_OVERRIDES key -> its own key). No entity
name, no translation, no sort order changes: the user's entity list is split exactly as before,
only the declaration now says those members are not family."""
import sys
from rt_lib import pkg, A3
sys.path.insert(0, str(A3))
import family_splits as F  # noqa: E402
root = sys.argv[1]
rows = F.load_rows(root)
F.OV.clear()
F.OV.update(F.overrides(root))
new = {}
for lang, idx in (("en", 2), ("sv", 3)):
    order = [(p, k) for p, k, *_ in sorted(rows, key=lambda r: F.sort_key(lang)(r[idx]))]
    for tok, members in sorted(F.families(rows, "DECLARED").items()):
        pos = sorted(order.index(m) for m in members)
        runs, cur = [], [pos[0]]
        for a, b in zip(pos, pos[1:]):
            if b == a + 1:
                cur.append(b)
            else:
                runs.append(cur)
                cur = [b]
        runs.append(cur)
        if len(runs) < 2:
            continue
        keep = max(runs, key=len)
        for i in pos:
            if i not in keep:
                new[order[i][1]] = order[i][1]
p = pkg(root) / "const.py"
src = p.read_text()
anchor = "ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {\n"
body = "".join(f'    "{k}": "{v}",\n' for k, v in sorted(new.items()))
p.write_text(src.replace(anchor, anchor + "    # Homed in their own family.\n" + body, 1))
print("re-declared", new)
