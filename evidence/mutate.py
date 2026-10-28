import sys, subprocess, pathlib, tempfile
W, wt = sys.argv[1], sys.argv[2]
src = pathlib.Path(wt, "tests/env_drift.py").read_text()
M = {
 "R1 drop path fullmatch": ("            and self.paths.fullmatch(leaf) is not None\n", ""),
 "R2 drop old-not-in-tos": ("and new in self.tos and old not in self.tos", "and new in self.tos"),
 "R3 drop new-in-tos": ("and new in self.tos and old not in self.tos", "and old not in self.tos"),
 "R4 drop froms test": ("            and (self.froms is None or old in self.froms)\n", ""),
 "R5 drop isinstance": ("isinstance(old, str) and isinstance(new, str)\n            and ", ""),
 "R6 drop matched|=hits": ("        matched |= hits\n", ""),
 "R7 drop shape_hits|=": ("        shape_hits |= matched\n", ""),
 "R8 drop claimed_hits.extend": ("    claimed_hits.extend(sorted(shape_hits))\n", ""),
 "R9 SHAPED arm excuses loose": ("        elif not loose:\n", "        elif True:\n"),
 "R10 drop prefix guard": ("if path.startswith(prefix) and shape.matches", "if shape.matches"),
 "R11 drop both-ways raise": ("    if froms is not None and froms & tos:\n", "    if False:\n"),
 "R12 literal any": ("_SHAPE_LITERAL = re.compile(r\"'[^'\\s|#\\\\]*'\")", "_SHAPE_LITERAL = re.compile(r\".*\")"),
 "R13 index wildcard any": (r'.replace(r"\[\*\]", r"\[\d+\]")', r'.replace(r"\[\*\]", r".*")'),
 "R14 key wildcard crosses dots": (r'.replace(r"\*", r"[^.\[\]]*"))', r'.replace(r"\*", r".*"))'),
 "R15 shape_claim_error wiring (1st)": ("        scope_problem = (may_drift_error(may_drift, claims)\n                         or shape_claim_error(claims))", "        scope_problem = (may_drift_error(may_drift, claims))"),
 "R16 shape branch in runner_conditional_error": ("    if name.startswith(SHAPE_CLAIM_MARKER):\n        return (\n            f\"SHAPE CLAIM MATCHED", "    if False:\n        return (\n            f\"SHAPE CLAIM MATCHED"),
 "R17 parse_shape_claim fullmatch->match": ("match = _SHAPE_LINE.fullmatch(line)", "match = _SHAPE_LINE.match(line)"),
}
for name, (old, new) in M.items():
    n = src.count(old)
    if n != 1:
        print(f"MUTANT {name}: anchor count {n} -- NOT APPLIED"); continue
    d = tempfile.mkdtemp(dir=W); p = pathlib.Path(d, "env_drift.py"); p.write_text(src.replace(old, new))
    r = subprocess.run([sys.executable, f"{W}/tools/sc_pins.py", str(p), f"{wt}/tests/entities.py"], cwd=wt, capture_output=True, text=True, env={"PYTHONPATH": "tests/hastub", "PATH": "/usr/bin:/bin"})
    out = (r.stdout + r.stderr).strip().splitlines()
    res = [l for l in out if l.startswith("RESULT")]
    print(f"MUTANT {name}: {res[0] if res else 'CRASH '+out[-1] if out else 'no output'} {'KILLED' if (not res or 'fails=0' not in res[0]) else 'SURVIVED'}")
