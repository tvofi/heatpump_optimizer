"""Reviewer's own instrument (not the fixer's, not the finder's): independently
checks every CMP_BOUND mutant in the inventory."""
import ast, sys, re
sys.path.insert(0, "tests")
import mutation_table as mt
sites = [s for s in mt.inventory() if s["kind"] == "CMP_BOUND"]
OPS = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">="}
bad = 0; susp = []
# independent expectation: count per (file,line) of ordering ops in one-line Compares
exp = {}
for p in sorted(mt.PRODUCTION.rglob("*.py")):
    src = p.read_text(); lines = src.splitlines()
    rel = str(p.relative_to(mt.ROOT))
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Compare) and n.end_lineno == n.lineno:
            k = sum(type(o) in OPS for o in n.ops)
            if k and lines[n.lineno-1].strip() and not lines[n.lineno-1].strip().startswith("#"):
                exp[(rel, n.lineno)] = exp.get((rel, n.lineno), 0) + k
got = {}
for s in sites:
    got[(s["file"], s["line"])] = got.get((s["file"], s["line"]), 0) + 1
    o, nw = s["old"].strip(), s["new"].strip()
    # mutant must parse
    try:
        to = ast.parse(o if not o.endswith(":") else o + " pass")
    except SyntaxError:
        to = None
    try:
        tn = ast.parse(nw if not nw.endswith(":") else nw + " pass")
    except SyntaxError:
        tn = None
    if (to is None) != (tn is None):
        bad += 1; print("PARSE-DIFF", s["file"], s["line"], nw); continue
    # exactly one ordering op differs, by one step
    if to is not None:
        ao = [type(x) for x in ast.walk(to) if isinstance(x, ast.cmpop)]
        an = [type(x) for x in ast.walk(tn) if isinstance(x, ast.cmpop)]
        diffs = [(a, b) for a, b in zip(ao, an) if a != b]
        okpairs = {(ast.Lt, ast.LtE), (ast.LtE, ast.Lt), (ast.Gt, ast.GtE), (ast.GtE, ast.Gt)}
        if len(ao) != len(an) or len(diffs) != 1 or diffs[0] not in okpairs:
            bad += 1; print("NOT-ONE-STEP", s["file"], s["line"], o, "=>", nw)
        # identical text apart from the operator
        if ast.dump(to).count("Compare") != ast.dump(tn).count("Compare"):
            bad += 1
    # equivalence heuristics: int-valued side vs non-integer constant; +-inf
    if re.search(r"(len\(|count|_idx|\bn\b|int\().*[<>]=?\s*-?\d+\.\d*[1-9]", o) or "inf" in o:
        susp.append(f'{s["file"]}:{s["line"]}: {o}')
miss = {k: v for k, v in exp.items() if got.get(k, 0) != v}
print(f"RESULT rv sites={len(sites)} expected={sum(exp.values())} line_mismatch={len(miss)} bad={bad}")
for k, v in list(miss.items())[:20]: print("MISMATCH", k, "expected", v, "got", got.get(k, 0))
print(f"RESULT rv equivalence_suspects={len(susp)}")
for x in susp: print("  SUSPECT", x)
