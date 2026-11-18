"""Game card_clone_copies by splitting windows with no-op statements: after every second card line that is a
``const``/``let`` statement, a distinct ``void <n>;`` is inserted, so a 20-token window of a copied function
no longer recurs. Nothing is deduplicated and the card behaves the same (#2373 round-1 review, P3). Counter
C22 (no-op statements dropped before windowing)."""
import sys
from rt_lib import pkg
root = sys.argv[1]
n = 0
for js in sorted((pkg(root) / "www").glob("*.js")):
    out = []
    for ln in js.read_text().split("\n"):
        out.append(ln)
        if ln.rstrip().endswith(";") and ln.lstrip().startswith(("const ", "let ")):
            n += 1
            if n % 2 == 0:
                out.append(ln[:len(ln) - len(ln.lstrip())] + f"void {n};")
    js.write_text("\n".join(out))
assert n > 2, n
print("inserted", n // 2)
