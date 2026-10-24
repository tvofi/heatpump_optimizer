"""Game card_clone_copies by renaming: in every top-level card ``function`` that shares a window with another,
each parameter and ``const``/``let`` name gains that function's own suffix, so no two copies spell their names
alike. Nothing is deduplicated; a census on raw tokens read the copies as distinct code. Counter C22."""
import re, sys
from rt_lib import pkg
from archscore.metrics import card as K
root = sys.argv[1]
p = pkg(root) / "www" / "heatpump-optimizer-card.js"
src = p.read_text()
members = {m.split("@")[0] for g in K.clone_copies(K.tokenize(src)) for m in g}
done = 0
for k, name in enumerate(sorted(members)):
    m = re.search(rf"^function {re.escape(name)}\(([^)]*)\) \{{\n", src, re.M)
    if m is None:
        continue
    start, depth, i = m.start(), 0, m.end() - 2
    while i < len(src):  # the body's extent by braces (the card's top-level functions keep braces balanced)
        depth += src[i] == "{"
        depth -= src[i] == "}"
        i += 1
        if depth == 0:
            break
    body = src[start:i]
    params = [x.strip().split("=")[0].strip() for x in m.group(1).split(",") if x.strip()]
    locals_ = set(params) | set(re.findall(rf"\b(?:const|let|var)\s+({K._IDENT.pattern})", body))
    for name2 in sorted(locals_):
        if K._IDENT.fullmatch(name2):
            body = re.sub(rf"(?<![\w$.]){re.escape(name2)}(?![\w$])", f"{name2}_f{k}", body)
    src = src[:start] + body + src[i:]
    done += 1
assert done, "no clone-class member is a top-level function"
p.write_text(src)
print("renamed locals in", done)
