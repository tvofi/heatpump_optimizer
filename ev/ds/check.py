import importlib.util, sys
tree, = sys.argv[1:2]
spec = importlib.util.spec_from_file_location("g", f"{tree}/tools/policy/budget_raise_gate.py"); g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
CI = "Architecture score: dS +0.0000 NULL"   # 3045 CI arch-score job 124591643014 (0ec244aa evidence/ci-arch-score-log.txt line 7)
for name in ("measured", "planted"):
    body = open(f"{sys.argv[2]}/{name}.md").read()
    print(f"RESULT body={name} justification={g.justification(body)[0]} justified={g.justified(body, lambda: CI)}")
    if hasattr(g, "check_body"):
        try: print(f"RESULT body={name} check_body(raises=[x])={g.check_body(body, ['tests/ci_budgets.json: critical_path_minutes_band: new at 1.3'], lambda: CI)}")
        except TypeError as e: print(f"RESULT body={name} check_body takes no score_fn at this tree ({e})")
