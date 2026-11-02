import sys, importlib.util
tree = sys.argv[1]
spec = importlib.util.spec_from_file_location("arch_score", tree + "/tests/arch_score.py")
m = importlib.util.module_from_spec(spec); sys.argv=[sys.argv[0]]; spec.loader.exec_module(m)
try:
    m.card_rule_spellings()
except Exception as e:
    print("RAISED", type(e).__name__, e)
print(f"RESULT checks={m.R.checks} failures={m.R.failures}")
