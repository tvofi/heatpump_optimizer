import shutil, subprocess, tempfile
from pathlib import Path
src=Path("/root/wt3502/tools/audit/seat")
M={
 "report_record_dropped":("out.append(line_ck(runs, rd(record) if record else None))","out.append(line_ck(runs, None))"),
 "gate_name_any":('if j["name"] == "gate":','if True:'),
 "count_rc_ignored":("    if rc not in (0, 1):\n        return None\n",""),
 "first_by_input_not_t":('for v in sorted(verdicts, key=lambda v: v["t"]):','for v in verdicts:'),
 "first_last_wins":('first.setdefault(v["pr"], v)','first[v["pr"]] = v'),
 "sort_reverse":('sorted(verdicts, key=lambda v: v["t"])','sorted(verdicts, key=lambda v: v["t"], reverse=True)'),
 "window_head_not_tail":('last = list(first.values())[-WINDOW_PRS:]','last = list(first.values())[:WINDOW_PRS]'),
 "span_swapped":("{last[0]['t'][:16]} .. {last[-1]['t'][:16]}","{last[-1]['t'][:16]} .. {last[0]['t'][:16]}"),
 "mf_first_any_blocked":('v["kind"] == "blocked" and family_of','v["kind"] != "merge" and family_of'),
 "ratchet_rc_ignored":('m = json.loads(out) if rc == 0 else None','m = json.loads(out)'),
 "named_regex_no_merged":('(BATCH|SKIP|PARK|MERGED|ADMIT|ALREADY)','(BATCH|SKIP|PARK|ADMIT|ALREADY)'),
 "escape_open_done_counted":('.get("stage") != "done"','.get("stage") != "donex"'),
}
for name,(a,b) in M.items():
    t=Path(tempfile.mkdtemp()); shutil.copy(src/"scorecard.py",t); shutil.copy(src/"scorecard_selftest.py",t)
    s=(t/"scorecard.py").read_text(); n=s.count(a)
    if n!=1: print(f"{name}: ANCHOR count {n}"); continue
    (t/"scorecard.py").write_text(s.replace(a,b))
    p=subprocess.run(["python3","-I",str(t/"scorecard.py"),"--self-test","--no-mutants"],capture_output=True,text=True)
    fails=[l for l in (p.stdout+p.stderr).splitlines() if l.startswith(("FAIL","not ok","Traceback"))]
    print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} {fails[:2]}")
