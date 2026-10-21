"""Reviewer probe (built by the fix reviewer, not the finder): does the P2
matcher registered as defrost_standoff catch a predicate that copies the flag
to a local before deciding?

The matcher and its helpers are extracted verbatim from the committed
tests/entities.py at the measured head, so this drives the real rule rather
than a re-implementation of it.
"""
import ast, sys

ENT = sys.argv[1]
src = open(ENT, encoding="utf-8").read()
tree = ast.parse(src)
want = {"_p2_decides", "_p2_match_defrost_decides", "_p2_index"}
ns = {"ast": ast}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in want:
        exec(compile(ast.Module(body=[node], type_ignores=[]), ENT, "exec"), ns)

parents_of = ns["_p2_index"]
decide = ns["_p2_match_defrost_decides"]

CASES = {
    "direct-if": "def _p2_plant(signals):\n    if signals.defrosting:\n        return 1\n    return 0\n",
    "bool-call": "def _p2_plant(signals):\n    return bool(signals.defrosting)\n",
    "not-and": "def _p2_plant(signals):\n    x = 1 if not signals.defrosting else 2\n    return x\n",
    "copy-to-local": "def _p2_plant(signals):\n    d = signals.defrosting\n    if d:\n        return 1\n    return 0\n",
    "walrus": "def _p2_plant(signals):\n    if (d := signals.defrosting):\n        return 1\n    return 0\n",
}

total = 0
for name, text in CASES.items():
    t = ast.parse(text)
    parents, _ = parents_of(t)
    hits = [n.lineno for n in ast.walk(t) if decide(n, parents)]
    total += len(hits)
    print(f"RESULT case={name} hits={len(hits)} count")
print(f"RESULT cases={len(CASES)} total_hits={total} count")
