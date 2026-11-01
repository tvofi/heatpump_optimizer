"""Round-2 reviewer's own stamp-class probe: every combination of which side bumps the claims-for stamp x which side changes claims."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ed", sys.argv[1] + "/tests/env_drift.py")
ed = importlib.util.module_from_spec(spec); sys.modules["ed"] = ed; spec.loader.exec_module(ed)
def f(v="7.0.4", claims=("alpha # a", "beta # b"), note=""):
    return "# h\n#\n# claims-for: %s\n%s#\n# note base\n\n" % (v, note) + "".join(c + "\n" for c in claims) + "# may-drift: wood_coil -- m\n"
base = f()
def run(name, o, t):
    m = ed.merge_claim_file(base, o, t)
    if m is None:
        print(f"RESULT {name}: refused  [{ed.merge_claim_refusal(base,o,t).splitlines()[0]}]")
    else:
        stamps = [l for l in m.splitlines() if l.startswith("# claims-for")]
        print(f"RESULT {name}: resolved stamps={stamps} claims={sorted(ed.parse_claim_map(m))}")
add_o = ("alpha # a", "beta # b", "gamma # o"); add_t = ("alpha # a", "beta # b", "delta # t")
run("S1 both bump same, both add disjoint", f("7.0.5", add_o), f("7.0.5", add_t))
run("S2 ours bumps only, theirs adds", f("7.0.5"), f(claims=add_t))
run("S3 theirs bumps only, ours adds (round-1 B2)", f(claims=add_o), f("7.0.5"))
run("S4 ours bumps+adds, theirs adds", f("7.0.5", add_o), f(claims=add_t))
run("S5 both bump same, only ours adds", f("7.0.5", add_o), f("7.0.5"))
run("S6 both bump differently, no claim change", f("7.0.5"), f("7.0.6"))
run("S7 ours bumps, theirs adds note beside stamp", f("7.0.5"), f(note="# theirs note\n"))
run("S8 theirs bumps, ours adds note beside stamp", f(note="# ours note\n"), f("7.0.5"))
run("S9 ours bumps + note, theirs adds note beside stamp + adds claim", f("7.0.5", note="# ours note\n"), f(claims=add_t, note="# theirs note\n"))
run("S10 ours bump+empty list (release reset), theirs adds", f("7.0.5", ()), f(claims=add_t))
