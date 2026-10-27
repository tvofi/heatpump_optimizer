"""R10-ARCH-SHAPES census (D8-s1-01): every site one tree's ``channel_active_kw`` P2 rule returns in another tree.

Applies ``tests/entities.py::_p2_match_channel_line`` as written at RULE_TREE
to the package under TARGET_TREE and prints one line per hit, as
``module::qualname :line source``, so the head's rule (which follows
``CHANNEL_ACTIVE_KW`` by name, a second module-level 0.05 kW constant, and the
literal) can be read against the base, where the renamed sites were invisible
to the literal-only rule.

    python3 dev/audit/harnesses/r10_channel_line_reach.py RULE_TREE TARGET_TREE

The registry's dispositions and owner are ``tests/entities.py``'s; this lists
the reach only. Null control: ``tests/entities.py`` plants each spelling
("and D8-s1-01's rule fails on each spelling of the channel line").
"""
import ast
import pathlib
import re
import sys

rule_tree, target = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
src = (rule_tree / "tests/entities.py").read_text()
ns = {"ast": ast, "re": re}
exec(src[src.index("def _p2_match_channel_line"):src.index("def _p2_match_literal_domain")], ns)
exec(src[src.index("def _p2_index"):src.index("_P2_FILE_CACHE = {}")], ns)
hits = 0
for p in sorted((target / "custom_components/heatpump_optimizer").glob("*.py")):
    if p.name == "const.py":
        continue
    tree = ast.parse(p.read_text())
    parents, qual = ns["_p2_index"](tree)
    for n in ast.walk(tree):
        if ns["_p2_match_channel_line"](n, parents):
            hits += 1
            print(f"{p.name}::{ns['_p2_owner_of'](n, parents, qual)} :{n.lineno} {ast.unparse(n)[:70]}")
print(f"RESULT hits={hits}")
