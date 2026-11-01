"""Reviewer's own adversarial planted merges against env_drift's claimnotes driver (fix-review of #3066)."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ed", sys.argv[1] + "/tests/env_drift.py")
ed = importlib.util.module_from_spec(spec); sys.modules["ed"] = ed; spec.loader.exec_module(ed)
H = "# Scenarios header.\n#\n# claims-for: {v}\n#\n# note base\n"
def f(claims, v="7.0.4", extra="", md="# may-drift: wood_coil -- machine-sensitive\n# may-drift: flat_prices -- polish\n"):
    return H.format(v=v) + extra + "\n" + "".join(c + "\n" for c in claims) + md
base = f(["alpha # base reason", "beta # base reason"])
def run(name, b, o, t, expect):
    m = ed.merge_claim_file(b, o, t)
    got = "refused" if m is None else "resolved"
    claims = None if m is None else ed.parse_claim_map(m)
    md = None if m is None else sorted(l for l in m.splitlines() if "may-drift:" in l and l.startswith("# may-drift"))
    ok = got == expect[0] and (expect[1] is None or expect[1](m))
    msg = ed.merge_claim_refusal(b, o, t).splitlines()[0:3] if m is None else ""
    print(f"RESULT {name}: {got} {'OK' if ok else 'FAIL'} claims={claims} md={md} {msg}")
# A both sides rewrote one scenario
run("A-both-rewrite-one", base, f(["alpha # ours new", "beta # base reason"]), f(["alpha # theirs new", "beta # base reason"]), ("refused", None))
# B differing stamps, both change claims
run("B-stamps-differ", base, f(["alpha # base reason", "beta # base reason", "gamma # ours"]), f([], v="7.0.5"), ("refused", None))
run("B2-stamp-bump-only-main-ours-adds", base, f(["alpha # base reason", "beta # base reason", "gamma # ours"]), f(["alpha # base reason", "beta # base reason"], v="7.0.5"), ("resolved", None))
# C delete vs edit
run("C-ours-delete-theirs-edit", base, f(["beta # base reason"]), f(["alpha # theirs edit", "beta # base reason"]), ("refused", None))
run("C2-theirs-delete-ours-edit", base, f(["alpha # ours edit", "beta # base reason"]), f(["beta # base reason"]), ("refused", None))
# C3 delete vs silence -> deleted
run("C3-delete-vs-silence", base, f(["beta # base reason"]), base.replace("# note base\n", "# note base\n# note theirs\n"), ("resolved", lambda m: "alpha" not in ed.parse_claim_map(m)))
# D deleted may-drift vs changed neighbour claim
md_wo_flat = "# may-drift: wood_coil -- machine-sensitive\n"
run("D-ours-del-maydrift-theirs-edit-beta", base, f(["alpha # base reason", "beta # base reason", "flat_prices # ours claims it"], md=md_wo_flat), f(["alpha # base reason", "beta # theirs edit"]),
    ("resolved", lambda m: "# may-drift: flat_prices -- polish" not in m and ed.parse_claim_map(m).get("flat_prices") and ed.parse_claim_map(m)["beta"] == ed.parse_claim_map(f(["beta # theirs edit"]))["beta"]))
# D2 deleted may-drift vs theirs editing the adjacent may-drift line
run("D2-ours-del-flat-theirs-edit-wood", base, f(["alpha # base reason", "beta # base reason"], md=md_wo_flat), f(["alpha # base reason", "beta # base reason"], md="# may-drift: wood_coil -- machine-sensitive (reworded)\n# may-drift: flat_prices -- polish\n"),
    ("resolved", lambda m: "flat_prices -- polish" not in m and "(reworded)" in m and "wood_coil -- machine-sensitive\n" not in m))
# D3 widening attempt: theirs deletes a may-drift line, ours rewrites the same line (suspend vs reword)
run("D3-widen-theirs-del-ours-reword", base, f(["alpha # base reason", "beta # base reason"], md="# may-drift: wood_coil -- machine-sensitive\n# may-drift: flat_prices -- polish v2\n"), f(["alpha # base reason", "beta # base reason"], md=md_wo_flat),
    ("refused", None))
# D4 widening: both delete flat_prices may-drift, ours re-adds a may-drift for a NEW fixture (allowed: ours' own line), check flat stays gone
run("D4-both-delete", base, f(["alpha # base reason", "beta # base reason"], md=md_wo_flat), f(["alpha # base reason", "beta # base reason"], md=md_wo_flat), ("resolved", lambda m: "flat_prices" not in m))
# E both add identical / differing
run("E-both-add-identical", base, f(["alpha # base reason", "beta # base reason", "gamma # same"]), f(["alpha # base reason", "beta # base reason", "gamma # same"]), ("resolved", lambda m: m.count("gamma # same") == 1))
run("E-both-add-identical-plus-disjoint", base, f(["alpha # base reason", "beta # base reason", "gamma # same", "delta # ours"]), f(["alpha # base reason", "beta # base reason", "gamma # same", "eps # theirs"]), ("resolved", lambda m: m.count("gamma # same") == 1 and set(ed.parse_claim_map(m)) == {"alpha","beta","gamma","delta","eps"}))
run("E-both-add-differing", base, f(["alpha # base reason", "beta # base reason", "gamma # ours"]), f(["alpha # base reason", "beta # base reason", "gamma # theirs"]), ("refused", None))
# H multi-line scenario: ours removes one line, theirs adds one
b2 = f(["alpha # r1", "alpha # r2"])
run("H-multiline-split", b2, f(["alpha # r1"]), f(["alpha # r1", "alpha # r2", "alpha # r3"]), ("refused", None))
# I disjoint null
run("I-disjoint", base, f(["alpha # ours", "beta # base reason"]), f(["alpha # base reason", "beta # theirs"]), ("resolved", lambda m: ed.parse_claim_map(m) == ed.parse_claim_map(f(["alpha # ours", "beta # theirs"]))))
# J shape lines, both add different
run("J-shape-both-add", base, f(["alpha # base reason", "beta # base reason", "shape: space_reasons[*] * -> 'idle'  # ours"]), f(["alpha # base reason", "beta # base reason", "shape: dhw_reasons[*] * -> 'idle'  # theirs"]), ("resolved", None))
run("J2-shape-same-key-diff-reason", base, f(["alpha # base reason", "beta # base reason", "shape: space_reasons[*] * -> 'idle'  # ours"]), f(["alpha # base reason", "beta # base reason", "shape: space_reasons[*] * -> 'idle'  # theirs"]), ("refused", None))
