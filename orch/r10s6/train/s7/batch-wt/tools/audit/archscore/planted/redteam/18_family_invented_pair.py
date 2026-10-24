"""Game family_splits past C6: every member a split family leaves outside its longest run is declared, with the
entity next to it in the English name sort, into an invented two-member family (``zzpair<n>``). No name changes,
so the user's entity list splits exactly as before; the two-member family satisfied C6's size test, and the
user reads no such family (ARCH-s3, round 10: ``family_pair_homing.py``, the solar forecast and the optimizer
status declared one family). Counter C6b."""
import sys
from rt_lib import pkg
from archscore.metrics import family_splits as F
root = sys.argv[1]
rows = F.load_rows(root)
ov = F.overrides(root)
F.OV.clear()
F.OV.update(ov)
order = [k for _p, k, *_ in sorted(rows, key=lambda r: F.sort_key("en")(r[2]))]
taken, new = set(ov), {}
for lang, idx in (("en", 2), ("sv", 3)):
    lorder = [k for _p, k, *_ in sorted(rows, key=lambda r: F.sort_key(lang)(r[idx]))]
    for _tok, members in sorted(F.families(rows, "DECLARED").items()):
        pos = sorted(lorder.index(k) for _p, k in members)
        runs, cur = [], [pos[0]]
        for a, b in zip(pos, pos[1:]):
            if b == a + 1:
                cur.append(b)
            else:
                runs.append(cur)
                cur = [b]
        runs.append(cur)
        keep = max(runs, key=len)
        for i in pos:
            k = lorder[i]
            if i in keep or k in taken:
                continue
            j = order.index(k)
            mate = next((order[x] for x in (j + 1, j - 1) if 0 <= x < len(order) and order[x] not in taken), None)
            if mate is None:
                continue
            fam = f"zzpair{len(new) // 2}"
            new[k], new[mate] = fam, fam
            taken |= {k, mate}
assert new, "no split family to game"
p = pkg(root) / "const.py"
src = p.read_text()
anchor = "ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {\n"
assert src.count(anchor) == 1
body = "".join(f'    "{k}": "{v}",\n' for k, v in sorted(new.items()))
p.write_text(src.replace(anchor, anchor + "    # Declared one family each.\n" + body, 1))
print("paired", new)
