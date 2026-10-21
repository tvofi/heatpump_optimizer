# reviewer's replay: Tick.main at <tick.py> with commits/main answered by <tip>
import importlib.util, sys
spec = importlib.util.spec_from_file_location("tick", sys.argv[1]); m = importlib.util.module_from_spec(spec)
sys.modules["tick"] = m; spec.loader.exec_module(m)
t = m.Tick("tvofi/heatpump_optimizer", sys.argv[3]); real = t.gh
calls = []
def gh(argv):
    calls.append(argv)
    return (0, sys.argv[2]) if any(str(a).endswith("/commits/main") for a in argv) else real(argv)
t.gh = gh
t.mandate = t.pins = t.policy_drift = lambda S: None
t.main()
for l in t.sections["MAIN"]: print("RESULT", ("FLAG " if l["flag"] else "     ") + l["text"][:220])
print("RESULT briefs:", [f["text"][:80] for f in t.findings if "main-red" in f["text"]])
print("RESULT annotation reads:", sum(1 for c in calls if any("annotations" in str(a) for a in c)))
