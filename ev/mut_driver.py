import subprocess, sys, shutil
F="tools/audit/check_scopes.py"; orig=open(sys.argv[1]).read()
M={
 "NULL": ("",""),
 "M11 drop out": ("evaluation_gaps(rnd, tree, show, merged, anc, changed, out)", "evaluation_gaps(rnd, tree, show, merged, anc, changed)"),
 "M12 rc always 0": ("1 if unmarked else 0, lines", "0, lines"),
 "M13 no isinstance": ('and not isinstance(c.get("gates_finders"), bool))', 'and "gates_finders" not in c)'),
 "M14 drop decision filter": ('if c.get("decision") == "accepted" and not', 'if not'),
 "M15 unmarked empty": ("unmarked = sorted(cid", "unmarked = [] or sorted(cid"),
 "M16 lines empty": ("lines = [f\"UNMARKED", "lines = [] and [f\"UNMARKED"),
 "M17 main exit 0": ("        sys.exit(rc)\n", "        sys.exit(0)\n"),
 "M18 main no stderr lines": ("            print(line, file=sys.stderr)", "            pass"),
 "M19 unsorted out": ('"open_cards": sorted(out)', '"open_cards": out[:0]+out'),
}
for k,(a,b) in M.items():
    if a and orig.count(a)!=1: print(k,"ANCHOR", orig.count(a)); continue
    open(F,"w").write(orig.replace(a,b,1) if a else orig)
    r=subprocess.run(["python3",F,"--repo",".","--ref","HEAD","--self-test"],capture_output=True,text=True)
    t=[l for l in (r.stdout+r.stderr).splitlines() if "evaluation arms" in l]
    print(f"{k}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} | {t[0].strip() if t else (r.stdout+r.stderr)[-200:]}")
open(F,"w").write(orig)
