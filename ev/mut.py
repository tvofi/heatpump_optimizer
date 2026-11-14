"""Reviewer's mutants over the delta d3c536ef..c8ad0cc3 of tools/audit/check_scopes.py (and R12 on scopes.json).
Each is a unique-string change; --self-test must exit non-zero. Run from the worktree root."""
import hashlib, subprocess, sys, time
F = "tools/audit/check_scopes.py"; S = "dev/audit/config/scopes.json"
M = [
 ("D1 isfinite dropped", F, " and not isinstance(v, bool) and math.isfinite(v)", " and not isinstance(v, bool)"),
 ("D2 empty dict is a read", F, "(isinstance(v, dict) and bool(v) and all(isnum(x) for x in v.values()))", "(isinstance(v, dict) and all(isnum(x) for x in v.values()))"),
 ("D3 dict of non-numbers is a read", F, "(isinstance(v, dict) and bool(v) and all(isnum(x) for x in v.values()))", "(isinstance(v, dict) and bool(v))"),
 ("D4 is_no_read back to prefix", F, 'return "noread" in norm(text)', 'return str(text).strip().startswith("NO-READ")'),
 ("D5 is_no_read case-sensitive", F, 'return "noread" in norm(text)', 'return "NOREAD" in norm(text).upper().replace("NOREAD","NOREAD") and "NO" in str(text)'),
 ("D6 enumerator any tracked file", F, "return tok in tree and tok.endswith(SCRIPT_SUFFIXES)", "return tok in tree"),
 ("D7 enumerator any script name", F, "return tok in tree and tok.endswith(SCRIPT_SUFFIXES)", "return tok.endswith(SCRIPT_SUFFIXES)"),
 ("D8 every group can build", F, "return {k for k, g in groups.items() if roster_lib.carry_receivable(g)}", "return set(groups)"),
 ("D9 term builder not checked against roster", F, """elif full(row.get("builder")) and row["builder"] not in groups:""", """elif full(row.get("builder")) and False:"""),
 ("D10 axis builder not checked against roster", F, """if full(b) and b not in groups and not (b.startswith("card:") and b[5:] in cards):""", """if full(b) and False:"""),
 ("D11 axis builder any card: prefix passes", F, """not (b.startswith("card:") and b[5:] in cards)""", """not b.startswith("card:")"""),
 ("D12 accepted-unset refusal dropped", F, """gaps += [f"{path} card {cid} is accepted for {u}, which {OBJECTIVE} still leaves unset" for u in unset]""", "pass"),
 ("D13 accepted-unset: threshold only", F, """("criterion", spec.get("owner_criteria", {}))) if card.get(k) in vals and vals[card[k]] is None]""", """("criterion", {})) if card.get(k) in vals and vals[card[k]] is None]"""),
 ("D14 accepted-unset: set value refused too", F, "if card.get(k) in vals and vals[card[k]] is None]", "if card.get(k) in vals]"),
 ("D15 axis no_read reason unchecked", F, """for k in ("no_read", "builder") if not full(ax.get(k))]""", """for k in ("builder",) if not full(ax.get(k))]"""),
 ("D16 name axis keeps required", F, "return used - (req - opt)", "return used"),
 ("D17 name axis drops optional-too", F, "return used - (req - opt)", "return used - req"),
 ("D18 name pattern search not fullmatch", F, "isinstance(n, ast.Name) and re.fullmatch(pattern, n.id)}", "isinstance(n, ast.Name) and re.match(pattern, n.id)}"),
 ("D19 required=True rows ignored", F, 'rows = {c.func.id for c in calls if marked(c) and isinstance(c.func, ast.Name)}', 'rows = set()'),
 ("D20 Required attr ignored", F, 'for c in calls if attr(c, "Required") or marked(c)))', 'for c in calls if marked(c)))'),
 ("D21 Optional attr ignored", F, 'if attr(c, "Optional") or (not marked(c)', 'if (not marked(c)'),
 ("D22 records: prev round is rnd", F, 'return f"{YARDSTICK}round{rnd - 1}/OBJECTIVE.json"', 'return f"{YARDSTICK}round{rnd}/OBJECTIVE.json"'),
 ("D23 no roster: any group", F, "if newest in tree else {}", "if newest in tree else {'G1': {}}"),
 ("R12 yardstick out of the exclusion", S, '"dev/audit/{rounds,yardstick}/**"', '"dev/audit/rounds/**"'),
 ("D24 untracked source refusal", F, "is not tracked at the ref", "is not tracked at the ref "),
]
def run():
    return subprocess.run([sys.executable, F, "--repo", ".", "--self-test"], capture_output=True, text=True).returncode
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
print("unmutated rc", run())
surv = 0
for name, p, old, new in M:
    src = open(p).read(); h = sha(p)
    if src.count(old) != 1:
        print(f"SKIP {name}: anchor count {src.count(old)}"); continue
    open(p, "w").write(src.replace(old, new))
    try: rc = run()
    finally: open(p, "w").write(src)
    assert sha(p) == h
    surv += rc == 0
    print(f"{'SURVIVED' if rc == 0 else 'killed'} rc={rc} {name}")
print("unmutated rc", run(), "survivors", surv, "of", len(M))
