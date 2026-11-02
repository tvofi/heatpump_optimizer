"""Round-1 reviewer harness ev/mut.py (verdict/3090), anchors re-pointed at the round-2 drain key, plus round-2 mutants on the --front marking."""
import subprocess, pathlib
F = "tools/audit/seat/merge_train.py"
CMD = "python3 -I tools/audit/seat/merge_train.py --self-test"
KEY = 'key=lambda e: (not (e.get("priority") or e.get("front")), not crit(e)))'
M = [
 ("R1 priority key dropped from item", '**({"priority": True} if a.priority else {})}', '}'),
 ("R2 front not passed to train_add", '"--state-dir", a.state_dir, *rest], front=a.front)', '"--state-dir", a.state_dir, *rest], front=False)'),
 ("R3 --remove arm made front", 'return spool_edit(t, a.pr, "remove")', 'return spool_edit(t, a.pr, "front")'),
 ("R4 spool entry drops priority key", '"verdict_comment", "issues", "priority")', '"verdict_comment", "issues")'),
 ("B1 drain key 0", KEY, 'key=lambda e: 0)'),
 ("R5 critical before priority/front", KEY, 'key=lambda e: (not crit(e), not (e.get("priority") or e.get("front"))))'),
 ("R6 --priority flag ignored", 'if a.priority else {})}', 'if False else {})}'),
 ("F1 drain ignores front (round-1 key)", KEY, 'key=lambda e: (not e.get("priority"), not crit(e)))'),
 ("F2 spool_edit front marking dropped", '    if op == "front":  # the line keeps first place', '    if False:  # the line keeps first place'),
 ("F3 train_add new-entry front marking dropped", '        if front:\n            entry["front"] = True\n', ''),
]
for name, a, b in M:
    p = pathlib.Path(F); src = p.read_text(); n = src.count(a)
    if n != 1: print(f"== {name}: NOT PLANTED (anchor count {n})", flush=True); continue
    p.write_text(src.replace(a, b))
    try:
        r = subprocess.run(CMD.split(), capture_output=True, text=True, timeout=230)
        last = [l for l in r.stdout.splitlines() if "self-test:" in l][-1:] or [""]
        print(f"== {name}: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} | {last[0]}", flush=True)
    finally:
        p.write_text(src)
