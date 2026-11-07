import subprocess, sys, os, tempfile, shutil
head = sys.argv[1]; out = sys.argv[2]
M = {
 "m0-null": None,
 "m1-no-owned": ("    if owned := _owned_lane(group):\n        return owned\n", ""),
 "m2-no-kindfallback": ('    if k in INSTRUMENT_KINDS or group.get("class") == "instrument":\n        return "Instruments"\n', ""),
 "m3-no-class": ('if k in INSTRUMENT_KINDS or group.get("class") == "instrument":', 'if k in INSTRUMENT_KINDS:'),
 "m4-any": ("if not files or not all(", "if not files or not any("),
 "m5-nofiles-guard": ("if not files or not all(", "if not all("),
 "m6-userdocs-tooling": ('                 and not any(f.startswith(_TOOLING_PREFIXES) for f in files))', '                 )'),
 "m7-doc-kind": ('return "Docs" if group.get("kind") == "doc" or user_docs else "Instruments"', 'return "Docs" if user_docs else "Instruments"'),
 "m8-hotfiles": ('files = list(group.get("files") or []) + list(group.get("hot_files") or [])', 'files = list(group.get("files") or [])'),
 "m9-docs-prefix": ('_NON_PRODUCT_PREFIXES = ("tools/", "tests/", ".github/", ".claude/", "dev/", "docs/")', '_NON_PRODUCT_PREFIXES = ("tools/", "tests/", ".github/", ".claude/", "dev/")'),
 "m10-rootfiles": ('_NON_PRODUCT_FILES = ("CLAUDE.md", "AGENTS.md", "README.md", "RELEASE_NOTES.md")', '_NON_PRODUCT_FILES = ()'),
 "m11-rca-kind": ('INSTRUMENT_KINDS = ("instrument", "policy", "rca", "tooling")', 'INSTRUMENT_KINDS = ("instrument", "policy", "tooling")'),
 "m12-userdocs-any": ("user_docs = (any(", "user_docs = True or (any("),
 "m13-workclass-tuple": ('or k in INSTRUMENT_KINDS:\n        return "instrument"', 'or k in ("instrument", "policy"):\n        return "instrument"'),
}
log = open(out, "w")
for name, sub in M.items():
    d = tempfile.mkdtemp()
    subprocess.run(f"git -C /home/user/rev archive {head} | tar -x -C {d}", shell=True, check=True)
    p = os.path.join(d, "tools/plan/replan.py"); s = open(p).read()
    if sub:
        n = s.count(sub[0])
        if n != 1:
            log.write(f"MUTANT {name} MATCH-COUNT={n} (not applied)\n"); continue
        s = s.replace(sub[0], sub[1]); open(p, "w").write(s)
    r = subprocess.run([sys.executable, "-I", "tools/plan/replan.py", "--self-test"], cwd=d, capture_output=True, text=True)
    fails = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("FAIL") and "lane" in l]
    tail = [l for l in (r.stdout + r.stderr).splitlines() if "self-test:" in l]
    log.write(f"MUTANT {name} rc={r.returncode} {tail}\n" + "".join(f"  {l}\n" for l in fails))
    shutil.rmtree(d)
