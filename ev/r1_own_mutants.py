import sys, tempfile
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import beat_jobs_selftest as T
src = Path("tools/audit/seat/beat_jobs.py").read_text()
M = {
 "tick: provenance check -> any text": ("    if not PROVENANCE.match(first):\n", "    if not text:\n"),
 "tick: transient memory not saved": ('    ctx.remember("tick.json", {"pass": first, "transient": transient})', '    ctx.remember("tick.json", {"pass": first, "transient": []})'),
 "owed: --tick arg points at state": ('"--tick", str(ctx.board)', '"--tick", str(ctx.state)'),
 "owed: rc0 falls through": ('    if rc == 0:\n        return write_job(ctx, "owed-check", [])', '    if False:\n        return write_job(ctx, "owed-check", [])'),
 "roster: no-op-attempted marked done": ('        if not any("no op attempted" in ln for ln in said):', '        if True:'),
 "roster: stale bound doubled": ("if ctx.now - first > HOLD_STALE_S:", "if ctx.now - first > 2 * HOLD_STALE_S:"),
 "plan: rc2 called UNAVAILABLE": ('word = "PLAN UNAVAILABLE" if rc == 1 else "REFUSED"', 'word = "PLAN UNAVAILABLE"'),
 "plan: replan args dropped": ('"--out", plan, "--slots", slots, "--seats", seats)', '"--out", plan)'),
 "pulse: unreadable rc ignored": ("    if rc not in (0, 1, 2) or not out:", "    if not out:"),
 "pulse: seat_alives dropped": ('        args += ["--seat-alive", e]', '        pass'),
 "cancel: rc!=0 ignored": ("    if rc != 0:\n        bad.append(f\"cancel-sweep", "    if False:\n        bad.append(f\"cancel-sweep"),
 "disk: floor compare >": ("    if ctx.free_gib() >= floor:", "    if ctx.free_gib() > floor - 100:"),
 "opener: rc!=0 ignored": ("    if rc != 0:\n        lines.append(f\"opener", "    if False:\n        lines.append(f\"opener"),
 "opener: --board dropped": ('"tools/audit/seat/open_driver.py", "--board", str(ctx.board))', '"tools/audit/seat/open_driver.py")'),
 "head: heads.tsv never rewritten": ("    if read(path) != text:\n        atomic(path, text)", "    if False:\n        atomic(path, text)"),
 "head: rc check dropped": ('    if rc != 0:\n        return write_job(ctx, "head-watch"', '    if False:\n        return write_job(ctx, "head-watch"'),
 "fold: gone.txt never written": ("    if gone:\n", "    if False:\n"),
 "event: dedupe removed": ("        if any(ln.split(\" \", 1)[-1] == line for ln in read(path).splitlines()):\n            return\n", ""),
 "norm: stamps not normalised": ('STAMP.sub("<t>", line.rstrip())', 'line.rstrip()'),
}
d = tempfile.mkdtemp()
for i, (name, (old, new)) in enumerate(M.items()):
    if src.count(old) != 1:
        print(f"SITE {src.count(old)}x  {name}"); continue
    p = Path(d) / f"o{i}.py"; p.write_text(src.replace(old, new))
    try:
        res = T.cases(T.load(p, f"own{i}"))
        failed = [k for k, v in res.items() if not v]
    except Exception as e:
        failed = [f"CRASH {e.__class__.__name__}: {e}"]
    print(f"{'KILLED  ' if failed else 'SURVIVED'} {name}" + (f"  <- {failed[0][:80]}" if failed else ""))
