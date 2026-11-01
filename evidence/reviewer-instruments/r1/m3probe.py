"""M3 probe: main (theirs) deletes scenario alpha, this branch left it alone (plus an unrelated note so the files differ)."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ed", sys.argv[1] + "/tests/env_drift.py")
ed = importlib.util.module_from_spec(spec); sys.modules["ed"] = ed; spec.loader.exec_module(ed)
H = "# h\n#\n# claims-for: 7.0.4\n#\n# note base\n{n}\n"
base = H.format(n="") + "alpha # a\nbeta # b\n"
ours = H.format(n="# ours note\n") + "alpha # a\nbeta # b\ngamma # ours\n"
theirs = H.format(n="") + "beta # b\n"
m = ed.merge_claim_file(base, ours, theirs)
print("RESULT theirs-deleted alpha:", None if m is None else sorted(ed.parse_claim_map(m)))
