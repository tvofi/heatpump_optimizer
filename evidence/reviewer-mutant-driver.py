import sys,subprocess,pathlib
p=pathlib.Path("tools/audit/seat/beat_jobs.py"); orig=p.read_text()
M={
"null":(None,None),
"moved_early_return":('            lines.append(f"plan-beat: PLAN MOVED {Path(mirror) / \'PLAN.html\'} re-rendered; republish owed")','            return write_job(ctx, "plan-beat", [f"plan-beat: PLAN MOVED {Path(mirror) / \'PLAN.html\'} re-rendered; republish owed"])'),
"moved_on_rc1":("    if rc == 0:\n        page = read(","    if rc in (0, 1):\n        page = read("),
"dispatch_only_rc0":('    if rc in (0, 1) and re.search(r"^pushed "','    if rc == 0 and re.search(r"^pushed "'),
"dispatch_rc012":('    if rc in (0, 1) and re.search(r"^pushed "','    if rc in (0, 1, 2) and re.search(r"^pushed "'),
"pushed_regex_unanchored":('re.search(r"^pushed ", out, re.M)','re.search(r"pushed", out)'),
"pages_err_dropped":("        if drc != 0:\n            lines.append(f\"plan-beat: PAGES","        if False:\n            lines.append(f\"plan-beat: PAGES"),
"dispatch_ref_dropped":('"--ref", "main"]','"--ref", "HEAD"]'),
"remember_dropped":('        ctx.remember("plan-page.json", sha, "")\n','        pass\n'),
"moved_always":("        if moved:\n            lines.append","        if True:\n            lines.append"),
"word_swapped":('word = "PLAN UNAVAILABLE" if rc == 1 else "REFUSED"','word = "REFUSED" if rc == 1 else "PLAN UNAVAILABLE"'),
}
sel=sys.argv[1:] or list(M)
try:
  for k in sel:
    a,b=M[k]
    if a is not None:
      assert orig.count(a)==1,(k,orig.count(a)); p.write_text(orig.replace(a,b))
    r=subprocess.run([sys.executable,"-I","tools/audit/seat/beat_jobs.py","--self-test","--no-mutants"],capture_output=True,text=True)
    fails=[l for l in r.stdout.splitlines() if l.lstrip().startswith("FAIL")]
    print(f"{k}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}"+("" if not fails else " | "+fails[0].strip()))
    p.write_text(orig)
finally: p.write_text(orig)
