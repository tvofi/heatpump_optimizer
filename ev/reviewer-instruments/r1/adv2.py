"""D2 with the suspension paired with its claim (the R8-P3 shape): does the merged file pass the gate's may-drift rules?"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ed", sys.argv[1] + "/tests/env_drift.py")
ed = importlib.util.module_from_spec(spec); sys.modules["ed"] = ed; spec.loader.exec_module(ed)
H = "# Scenarios header.\n#\n# claims-for: 7.0.4\n#\n# note base\n\n"
MD = "# may-drift: wood_coil -- machine-sensitive\n# may-drift: flat_prices -- polish\n"
base = H + "alpha # base reason\n" + MD
ours = H + "alpha # base reason\nflat_prices # ours claims it, suspending its may-drift\n" + "# may-drift: wood_coil -- machine-sensitive\n"
theirs = H + "alpha # base reason\n" + "# may-drift: wood_coil -- machine-sensitive (reworded)\n# may-drift: flat_prices -- polish\n"
m = ed.merge_claim_file(base, ours, theirs)
print("RESULT D2c merged:", "refused" if m is None else "resolved")
if m:
    print(m)
    md = ed.parse_may_drift(m) if hasattr(ed, "parse_may_drift") else None
    print("RESULT D2c may_drift_error:", ed.may_drift_error(md, ed.parse_claim_map(m)) if md is not None else "no parser")
import tempfile, os
d = tempfile.mkdtemp(); p = os.path.join(d, ed.CLAIM_FILE); os.makedirs(os.path.dirname(p)); open(p, "w").write(m)
md = ed._may_drift(d)
print("RESULT D2c may-drift map:", md)
print("RESULT D2c may_drift_error:", (ed.may_drift_error(md, ed.parse_claim_map(m)) or "None")[:300])
