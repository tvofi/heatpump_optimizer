"""Round-2 reviewer mutants for beat_jobs.py: each planted in a temp copy; killed when any self-test case fails."""
import sys, tempfile
from pathlib import Path
sys.path.insert(0, "tools/audit/seat")
import beat_jobs_selftest as T
src = Path("tools/audit/seat/beat_jobs.py").read_text()
M = {
 "tick: NOT REVIEWABLE not transient": ('TRANSIENT = re.compile(r"^#\\d+: (?:NOT REVIEWABLE|RED unanswered)")', 'TRANSIENT = re.compile(r"^#\\d+: (?:RED unanswered)")'),
 "tick: MERGE-READY dropped from family": ("|APPROVAL-OWED:|MERGE-READY:|", "|APPROVAL-OWED:|"),
 "tick: DIRTY dropped from family": ("|mergeable state DIRTY|", "|"),
 "owed: --acks dropped": ('"--acks", got[0])', ')'),
 "owed: rc1 without keys silent": ('    why = next((ln for ln in (out + err).splitlines() if ln.startswith("UNREADABLE")), f"rc={rc}")\n    write_job', '    return\n    write_job'),
 "roster: occurrence count dropped": ("        count[text] += 1\n", "        count[text] = 1\n"),
 "roster: comments run": ('        if not text or text.startswith("#"):', '        if not text:'),
 "roster: malformed hold retried": ('                lines.append(f"roster: refused malformed hold line: {text}")\n                done.add(key)', '                lines.append(f"roster: refused malformed hold line: {text}")'),
 "roster: hold op not stripped": ("            op = parts[2]\n", ""),
 "plan: state_docs --mirror dropped": ('"--push", "--mirror", mirror, "--plan", plan)', '"--push", "--plan", plan)'),
 "plan: overlay key missing silent": ('def plan_beat(ctx: Ctx) -> None:\n    got = ctx.need("plan-beat", "plan_json", "plan_slots", "plan_seats", "state_mirror")', 'def plan_beat(ctx: Ctx) -> None:\n    got = ctx.need("plan-beat", "plan_json")'),
 "pulse: pulse.txt not written": ('    atomic(ctx.state / "beatd" / "pulse.txt", out)\n', ''),
 "pulse: launch ledger dropped": ('        args += ["--launch-ledger", str(o["launch_ledger"])]', '        pass'),
 "pulse: seat_queues dropped": ('    args += shlex.split(str(o.get("seat_queues") or ""))\n', ''),
 "cancel: truncated not a failure": ("unreadable|truncated", "unreadable"),
 "disk: gc never run": ('    rc, _, _ = ctx.run(["bash", str(ctx.repo / "tools/audit/worktree_gc.sh"), got[0]], ctx.repo, ctx.env)', '    rc = 0'),
 "opener: NEEDS-TITLE dropped": ('|NEEDS-TITLE |STARVED |STUCK ', '|STARVED |STUCK '),
 "opener: STARVED dropped": ('|NEEDS-TITLE |STARVED |STUCK ', '|NEEDS-TITLE |STUCK '),
 "head: HEAD-MOVED dedupe any-same": ("            if same and same[-1] == line:", "            if line in same:"),
 "head: closed PRs kept forever": ('    text = "".join(f"{n}\\t{heads[n]}\\n" for n in sorted(heads, key=int))', '    text = "".join(f"{n}\\t{v}\\n" for n, v in sorted({**old, **heads}.items(), key=lambda kv: int(kv[0])))'),
 "fold: counter->set": ("    was, now = collections.Counter(old.splitlines()), collections.Counter(text.splitlines())", "    was, now = collections.Counter(set(old.splitlines())), collections.Counter(set(text.splitlines()))"),
 "fold: gone.txt never written": ("    if gone:\n", "    if False:\n"),
 "write_job: no norm": ('    text = "".join(norm(ln) + "\\n" for ln in lines if ln.strip())\n    path = ctx.digest / "jobs" / row', '    text = "".join(ln + "\\n" for ln in lines if ln.strip())\n    path = ctx.digest / "jobs" / row'),
 "need: empty string accepted": ('if self.overlay.get(k) in (None, "")]', 'if self.overlay.get(k) is None]'),
}
d = tempfile.mkdtemp()
surv = 0
for i, (name, (old, new)) in enumerate(M.items()):
    n = src.count(old)
    if n != 1:
        print(f"SITE {n}x  {name}"); continue
    p = Path(d) / f"m{i}.py"; p.write_text(src.replace(old, new))
    try:
        res = T.cases(T.load(p, f"own2_{i}"))
        failed = [k for k, v in res.items() if not v]
    except Exception as e:
        failed = [f"CRASH {type(e).__name__}: {e}"]
    if failed:
        print(f"KILLED   {name}  <- {failed[0][:90]}")
    else:
        surv += 1; print(f"SURVIVED {name}")
print(f"own_mutants2: {len(M)} planted, {surv} survived")
