import subprocess, sys, shutil, pathlib
M = [
 ("R1 resolved: priority key dropped from item", "tools/audit/seat/merge_train.py",
  '**({"priority": True} if a.priority else {})}', '}', "python3 -I tools/audit/seat/merge_train.py --self-test"),
 ("R2 resolved: front not passed to train_add", "tools/audit/seat/merge_train.py",
  '"--state-dir", a.state_dir, *rest], front=a.front)', '"--state-dir", a.state_dir, *rest], front=False)', "python3 -I tools/audit/seat/merge_train.py --self-test"),
 ("R3 resolved: --remove arm made front", "tools/audit/seat/merge_train.py",
  'return spool_edit(t, a.pr, "remove")', 'return spool_edit(t, a.pr, "front")', "python3 -I tools/audit/seat/merge_train.py --self-test"),
 ("R4 spool entry drops priority key", "tools/audit/seat/merge_train.py",
  '"verdict_comment", "issues", "priority")', '"verdict_comment", "issues")', "python3 -I tools/audit/seat/merge_train.py --self-test"),
 ("B1 body: drain key 0", "tools/audit/seat/merge_train.py",
  'key=lambda e: (not e.get("priority"), not crit(e)))', 'key=lambda e: 0)', "python3 -I tools/audit/seat/merge_train.py --self-test"),
 ("R5 drain: critical before priority", "tools/audit/seat/merge_train.py",
  'key=lambda e: (not e.get("priority"), not crit(e)))', 'key=lambda e: (not crit(e), not e.get("priority")))', "python3 -I tools/audit/seat/merge_train.py --self-test"),
 ("R6 --priority argparse flag ignored", "tools/audit/seat/merge_train.py",
  'if a.priority else {})}', 'if False else {})}', "python3 -I tools/audit/seat/merge_train.py --self-test"),
]
for name, f, a, b, cmd in M:
    p = pathlib.Path(f); src = p.read_text(); n = src.count(a)
    if n != 1: print(f"== {name}: NOT PLANTED (anchor count {n})"); continue
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=200)
        last = (r.stdout.strip().splitlines() or [""])[-1]
        print(f"== {name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} | {last}")
    finally:
        p.write_text(src)
