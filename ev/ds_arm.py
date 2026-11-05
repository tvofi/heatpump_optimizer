import sys
sys.path.insert(0, sys.argv[1] + "/tools/policy")
import budget_raise_gate as g
sec = open(sys.argv[2]).read()
measured = "Architecture score: dS +0.0000 NULL"
planted = sec.replace("dS +0.0000 NULL", "dS +0.0012 IMPROVES")
assert planted != sec
score = lambda: measured
for name, body in (("planted round-1 (+0.0012 IMPROVES)", planted), ("measured (+0.0000 NULL)", sec)):
    print("justified:", name, "->", g.justified(body, score))
    print("check_body raise:", name, "->", g.check_body(body, ["tests/ci_budgets.json: critical_path_minutes_band: new at 1.3"], score))
    print("check_body no-raise (null):", name, "->", g.check_body(body, [], score))
print("shape-only justification(planted):", g.justification(planted))
