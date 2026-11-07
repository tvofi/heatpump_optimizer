import subprocess, sys, pathlib
root = pathlib.Path(sys.argv[1]); f = root/"tools/audit/seat/plan_public.py"
orig = f.read_text(); code, mark, rest = orig.partition("#: (old, new, the check"); table, sep, tail = rest.partition("\n\ndef self_test(")
M = [
 ("int_dropped", "    rounds = [int(m[1]) for r", "    rounds = [m[1] for r"),
 ("max_to_min", "    return max(rounds) if rounds", "    return min(rounds) if rounds"),
 ("regex_no_end", r'-plan$")', r'-plan")'),
 ("html_check_off", "    if not _HTML.match(text):\n", "    if False:\n"),
 ("html_case_sensitive", '<!doctype html", re.I)', '<!doctype html")'),
 ("leak_off", "    why = refusal(text, ident)\n", "    why = None\n"),
 ("attribution_off", " + ref_privacy.attribution(text)\n", "\n"),
 ("host_ident_dropped", "ident or ref_privacy.Identity.of_host()", "ident"),
 ("rc_ignored_refs", "if rc == 0 else None", "if True else None"),
 ("show_rc_ignored", "    if rc != 0 or not text:", "    if not text:"),
 ("empty_text_published", "    if rc != 0 or not text:", "    if rc != 0:"),
 ("refused_rc0", '        return 1, f"plan_public: REFUSED', '        return 0, f"plan_public: REFUSED'),
 ("absent_rc1", '        return 2, f"plan_public: NOTHING TO PUBLISH: no {state_docs', '        return 1, f"plan_public: NOTHING TO PUBLISH: no {state_docs'),
 ("noref_rc0", '        return 2, "plan_public: NOTHING TO PUBLISH: no origin', '        return 0, "plan_public: NOTHING TO PUBLISH: no origin'),
 ("write_empty", "    dest.write_text(text)", "    dest.write_text('')"),
 ("dest_name", '    dest = out / PLAN_DIR / "index.html"', '    dest = out / PLAN_DIR / "plan.html"'),
 ("main_rc0", "    return rc\n", "    return 0\n"),
 ("main_print_stdout", "file=sys.stderr if rc else sys.stdout", "file=sys.stdout"),
 ("main_url_rc1", "        print(PLAN_URL)\n        return 0", "        print(PLAN_URL)\n        return 1"),
 ("main_repo_cwd_ignored", "    rc, msg = stage(a.repo, a.out)", "    rc, msg = stage(Path('/nonexistent'), a.out)"),
]
CMD=[sys.executable,"-I","-c","import sys; sys.path.insert(0,'tools/audit/seat'); import plan_public as p; sys.exit(p.self_test(False))"]
null = subprocess.run(CMD,capture_output=True,text=True,cwd=root)
print(f"NULL(cases-only) rc={null.returncode} {null.stdout.strip().splitlines()[-1]}", flush=True)
try:
  for name,a,b in M:
    n = code.count(a)+tail.count(a)
    if n!=1: print(f"{name} NOAPPLY count={n}"); continue
    f.write_text(code.replace(a,b)+mark+table+sep+tail.replace(a,b))
    r = subprocess.run(CMD,capture_output=True,text=True,cwd=root,timeout=300)
    fails=[l for l in (r.stdout+r.stderr).splitlines() if l.startswith(("FAIL","Traceback"))]
    print(f"{name} {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {fails[0][:150] if fails else ''}", flush=True)
finally:
  f.write_text(orig)
