"""Reviewer's mutant driver (mine, not the fixer's). Each mutant is one unique-string
replacement in tools/audit/check_scopes.py, loaded as a module from a temp copy; the
arms of evaluation_self_test and population_self_test are read directly (function level).
Killed = at least one arm false or an exception. Usage: mut.py <worktree>"""
import importlib.util, json, subprocess, sys, tempfile, os, shutil
wt = sys.argv[1]
src_path = os.path.join(wt, "tools/audit/check_scopes.py")
SRC = open(src_path).read()
M = [
 ("N1 is_no_read back to substring", 'return bool(re.search(r"(?<![^\\W_])no[\\W_]*read(?![^\\W_])", str(text).casefold()))', 'return "noread" in norm(text)'),
 ("N2 is_no_read no leading boundary", 'r"(?<![^\\W_])no[\\W_]*read(?![^\\W_])"', 'r"no[\\W_]*read(?![^\\W_])"'),
 ("N3 is_no_read no trailing boundary", 'r"(?<![^\\W_])no[\\W_]*read(?![^\\W_])"', 'r"(?<![^\\W_])no[\\W_]*read"'),
 ("N4 is_no_read never true", 'return bool(re.search(r"(?<![^\\W_])no[\\W_]*read(?![^\\W_])", str(text).casefold()))', 'return False'),
 ("N5 is_no_read no casefold", 'str(text).casefold()))', 'str(text)))'),
 ("N6 is_no_read separator only hyphen", 'no[\\W_]*read', 'no-read'),
 ("D7 enumerates without tok in tree", 'return tok in tree and tok.endswith(SCRIPT_SUFFIXES)', 'return tok.endswith(SCRIPT_SUFFIXES)'),
 ("E2 enumerates without suffix rule", 'return tok in tree and tok.endswith(SCRIPT_SUFFIXES)', 'return tok in tree'),
 ("E3 enumerates default True", '            return tok in tree and tok.endswith(SCRIPT_SUFFIXES)\n    return False', '            return tok in tree and tok.endswith(SCRIPT_SUFFIXES)\n    return True'),
 ("D22 records objective of round N", 'return f"{YARDSTICK}round{rnd - 1}/OBJECTIVE.json"', 'return f"{YARDSTICK}round{rnd}/OBJECTIVE.json"'),
 ("R2 records evaluation of round N-1", 'f"{YARDSTICK}round{rnd}/EVALUATION.json"', 'f"{YARDSTICK}round{rnd - 1}/EVALUATION.json"'),
 ("G1 same seat accepted", 'or seat == rev or', 'or'),
 ("G2 orchestrator evaluator accepted", '"orchestrator" in seat or', ''),
 ("G3 orchestrator reviewer accepted", ' or "orchestrator" in rev:', ':'),
 ("G4 non-approve review accepted", 'or rv.get("verdict") != "approve":', 'or False:'),
 ("G5 review sha unmerged accepted", 'elif not (full(rv.get("sha")) and merged(rv["sha"])):', 'elif not full(rv.get("sha")):'),
 ("G6 graded-other-objects accepted", 'if graded != rows:', 'if False:'),
 ("G7 commit before review accepted", 'elif revsha and anc(c, revsha):', 'elif False:'),
 ("G8 commit changing nothing accepted", 'elif not want & changed(c):', 'elif False:'),
 ("G9 remove on NO-READ accepted", 'elif row["verdict"] == "remove" and is_no_read(row["evidence"]):', 'elif False:'),
 ("G10 unowned count unchecked", 'and n < u["value"]:', 'and False:'),
 ("G11 isnum admits nan/inf", 'and not isinstance(v, bool) and math.isfinite(v)', 'and not isinstance(v, bool)'),
 ("G12 isnum admits bool", 'isinstance(v, (int, float)) and not isinstance(v, bool) and', 'isinstance(v, (int, float)) and'),
 ("G13 unset threshold uncarded accepted", 'if th.get("value") is None and k not in carded("threshold"):', 'if False:'),
 ("G14 unset criterion uncarded accepted", 'if p is None and d not in carded("criterion"):', 'if False:'),
 ("G15 term builder outside roster accepted", 'elif full(row.get("builder")) and row["builder"] not in groups:', 'elif False:'),
 ("G16 row outside object globs accepted", 'for f in sorted(rows) if f not in objects]', 'for f in sorted(rows) if False]'),
 ("G17 reads field unchecked", 'if ev.get("round") != rnd or ev.get("reads") != prev:', 'if ev.get("round") != rnd:'),
 ("G18 round field unchecked", 'if ev.get("round") != rnd or ev.get("reads") != prev:', 'if ev.get("reads") != prev:'),
 ("G19 ruling unchecked", 'if not full(card.get("ruling")):', 'if False:'),
 ("G20 accepted unmerged accepted", 'if not (c and merged(c)):', 'if False:'),
 ("G21 accepted card for unset value accepted", 'gaps += [f"{path} card {cid} is accepted for {u}, which {OBJECTIVE} still leaves unset" for u in unset]', 'pass'),
 ("G22 builder card missing accepted", '        if b not in cards:\n            gaps.append(f"{prev} term {t} builder card:{b}', '        if False:\n            gaps.append(f"{prev} term {t} builder card:{b}'),
 ("G23 open_builders: every group", 'return {k for k, g in groups.items() if roster_lib.carry_receivable(g)}', 'return set(groups)'),
 ("G24 axis builder unchecked", 'if full(b) and b not in groups and not (b.startswith("card:") and b[5:] in cards):', 'if False:'),
 ("G25 change with no card accepted", 'elif row["verdict"] != "keep" and row.get("card") not in cards:', 'elif False:'),
 ("G26 criterion path untracked accepted", 'elif p is not None and p not in tree:', 'elif False:'),
 ("G27 NO-READ no reason accepted", 'elif "value" not in row and not str(row.get("no_read", "")).strip():', 'elif False:'),
 ("P1 pairs formula", '(sum(sizes) ** 2 - sum(n * n for n in sizes)) // 2', '(sum(sizes) ** 2) // 2'),
 ("P2 name axis keeps required-and-optional out", 'return used - (req - opt)', 'return used - req'),
 ("P3 binary counted as one axis", 'sizes += [2] * len(lv)', 'sizes.append(len(lv))'),
 ("P4 empty axis accepted", '            if not lv:\n                raise ValueError("no level found")', '            pass'),
]
tree = set(subprocess.check_output(["git", "-C", wt, "ls-tree", "-r", "--name-only", "HEAD"], text=True).split())
show = lambda f, at=None: subprocess.check_output(["git", "-C", wt, "show", f"{at or 'HEAD'}:{f}"], text=True)
def arms(text):
    d = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(d, "seat"))
        for n in os.listdir(os.path.join(wt, "tools/audit")):
            p = os.path.join(wt, "tools/audit", n)
            if os.path.isfile(p) and n != "check_scopes.py": shutil.copy(p, d)
        for n in os.listdir(os.path.join(wt, "tools/audit/seat")):
            p = os.path.join(wt, "tools/audit/seat", n)
            if os.path.isfile(p): shutil.copy(p, os.path.join(d, "seat"))
        open(os.path.join(d, "check_scopes.py"), "w").write(text)
        code = ("import importlib.util,json,subprocess,sys\n"
                f"wt={wt!r}\n"
                f"s=importlib.util.spec_from_file_location('cs',{os.path.join(d,'check_scopes.py')!r});m=importlib.util.module_from_spec(s);s.loader.exec_module(m)\n"
                "tree=set(subprocess.check_output(['git','-C',wt,'ls-tree','-r','--name-only','HEAD'],text=True).split())\n"
                "show=lambda f,at=None: subprocess.check_output(['git','-C',wt,'show',f\"{at or 'HEAD'}:{f}\"],text=True)\n"
                "r={**{'ev: '+k:bool(v) for k,v in m.evaluation_self_test(tree,show).items()},**{'pop: '+k:bool(v) for k,v in m.population_self_test().items()}}\n"
                "print(json.dumps(r))\n")
        p = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True)
        if p.returncode: return None, p.stderr.strip().splitlines()[-1][:160]
        return json.loads(p.stdout.splitlines()[-1]), ""
    finally:
        shutil.rmtree(d)
base, err = arms(SRC)
assert base and all(base.values()), (err, base and [k for k, v in base.items() if not v])
print(f"UNMUTATED: {sum(base.values())}/{len(base)} arms held")
killed = surv = skip = 0
for name, old, new in M:
    if SRC.count(old) != 1:
        print(f"SKIP     {name}: anchor found {SRC.count(old)} times"); skip += 1; continue
    r, err = arms(SRC.replace(old, new))
    if r is None:
        print(f"KILLED   {name}: exception {err}"); killed += 1
    else:
        bad = [k for k, v in r.items() if not v]
        if bad: print(f"KILLED   {name}: {len(bad)} arm(s), first: {bad[0][:110]}"); killed += 1
        else: print(f"SURVIVED {name}"); surv += 1
print(f"RESULT mutants: {len(M)} planned, {killed} killed, {surv} survived, {skip} skipped")
