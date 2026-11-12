import shutil, subprocess, sys, tempfile
from pathlib import Path
src=Path("/root/wt/tools/audit/seat")
M={
 "report_record_dropped":("out.append(line_ck(runs, rd(record) if record else None))","out.append(line_ck(runs, None))"),
 "yield_path_wrong":('d.parent / "study" / "work" / "yield.py"','d / "study" / "work" / "yield.py"'),
 "gate_name_any":('if j["name"] == "gate":','if True:'),
 "count_rc_ignored":("    if rc not in (0, 1):\n        return None\n",""),
 "dedup_dropped":("        if k in seen:\n            continue\n",""),
 "first_by_input_not_t":("last = sorted(by.values(), key=lambda vs: vs[0][\"t\"])[-WINDOW_PRS:]","last = list(by.values())[-WINDOW_PRS:]"),
 "ratchet_rc_ignored":('m = json.loads(out) if rc == 0 else None','m = json.loads(out)'),
 "named_regex_no_merged":('r"(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)"','r"(BATCH|SKIP|PARK|ADMIT|ALREADY)"'),
 "escape_open_done_counted":('.get("stage") != "done"','.get("stage") != "donex"'),
}
for name,(a,b) in M.items():
    t=Path(tempfile.mkdtemp()); shutil.copy(src/"scorecard.py",t); shutil.copy(src/"scorecard_selftest.py",t)
    s=(t/"scorecard.py").read_text(); n=s.count(a)
    if n!=1: print(f"{name}: ANCHOR count {n}"); continue
    (t/"scorecard.py").write_text(s.replace(a,b))
    p=subprocess.run(["python3","-I",str(t/"scorecard.py"),"--self-test","--no-mutants"],capture_output=True,text=True)
    fails=[l for l in (p.stdout+p.stderr).splitlines() if l.startswith(("FAIL","not ok","Traceback")) or "FAIL" in l[:6]]
    print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} {fails[:3]}")
