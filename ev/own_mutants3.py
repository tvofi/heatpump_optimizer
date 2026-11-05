"""Round-3 reviewer mutants (reviewer's own instrument) on the logic round 3 added; same driver as ev/finder_own_mutants2.py."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import beat_jobs_selftest as T
src = Path("tools/audit/seat/beat_jobs.py").read_text()
M = {
 "fold: gone.txt never written (re-sited)": ('    atomic(ctx.digest / "gone.txt", "".join(ln + "\\n" for ln in gone))\n', ''),
 "fold: gone.txt kept stale": ('    atomic(ctx.digest / "gone.txt", "".join(ln + "\\n" for ln in gone))\n', '    if gone:\n        atomic(ctx.digest / "gone.txt", "".join(ln + "\\n" for ln in gone))\n'),
 "fold: stamp on gone too": ("    if new:\n        atomic(ctx.digest / \"new.stamp\"", "    if new or gone:\n        atomic(ctx.digest / \"new.stamp\""),
 "roster: unterminated tail runs": ('read(ctx.state / "roster-drain.queue").split("\\n")[:-1]', 'read(ctx.state / "roster-drain.queue").split("\\n")'),
 "roster: shrink not sticky": ('if len(whole) < seen or ctx.memory("roster-shrank.json", False):', 'if len(whole) < seen:'),
 "roster: shrink undetected": ('if len(whole) < seen or ctx.memory("roster-shrank.json", False):', 'if ctx.memory("roster-shrank.json", False):'),
 "roster: drained count not remembered": ('    ctx.remember("roster-queue-lines.json", len(whole), 0)\n', ''),
 "roster: no-op-attempted not retried": ('        if not any("no op attempted" in ln for ln in said):', '        if True:'),
 "events: STUCK whole-file dedupe dropped": ("        elif line in kept:\n            return", "        elif False:\n            return"),
 "events: HEAD-MOVED never deduped": ("            if same and same[-1] == line:", "            if False:"),
 "tick: pass kept on UNREADABLE": ('ctx.remember("tick.json", {"pass": "", "transient": seen_before["transient"]}, {"pass": "", "transient": []})', 'pass'),
}
d = tempfile.mkdtemp(); surv = 0
for i, (name, (old, new)) in enumerate(M.items()):
    n = src.count(old)
    if n != 1:
        print(f"SITE {n}x  {name}"); continue
    p = Path(d) / f"m{i}.py"; p.write_text(src.replace(old, new))
    try:
        res = T.cases(T.load(p, f"own3_{i}")); failed = [k for k, v in res.items() if not v]
    except Exception as e:
        failed = [f"CRASH {type(e).__name__}: {e}"]
    if failed: print(f"KILLED   {name}  <- {failed[0][:90]}")
    else: surv += 1; print(f"SURVIVED {name}")
# null control: the unmutated source through the same driver
p = Path(d) / "null.py"; p.write_text(src); res = T.cases(T.load(p, "own3_null"))
print(f"NULL unmutated: {sum(1 for v in res.values() if not v)} failed of {len(res)}")
print(f"own_mutants3: {len(M)} planted, {surv} survived")
