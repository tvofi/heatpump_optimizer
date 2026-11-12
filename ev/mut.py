"""Reviewer's mutant driver: apply one replacement at a time in the worktree, run the group's command, restore."""
import subprocess, sys, pathlib
W = "/tmp/tmp.I0JMrj4V2w"; WT = pathlib.Path(W) / "wt"
P = "custom_components/heatpump_optimizer/"
M = [
 ("supply_hold.py", "held.supply_held, held.held_until = True, now + _freeze_span(inp.config)", "held.supply_held = True", "held_until never set"),
 ("supply_hold.py", "held.supply_held, held.held_until = True, now + _freeze_span(inp.config)", "held.supply_held, held.held_until = True, now", "span zero"),
 ("supply_hold.py", "return 2 * timedelta(", "return 3 * timedelta(", "span three intervals"),
 ("supply_hold.py", "return 2 * timedelta(", "return 1 * timedelta(", "span one interval"),
 ("supply_hold.py", "dt_util.as_utc(now or dt_util.now()) < until", "dt_util.as_utc(now or dt_util.now()) <= until", "< -> <="),
 ("supply_hold.py", "dt_util.as_utc(now or dt_util.now()) < until", "dt_util.as_utc(now or dt_util.now()) > until", "< -> >"),
 ("supply_hold.py", "return FREEZE_HELD if held_now else None", "return None", "never frozen"),
 ("supply_hold.py", "return FREEZE_HELD if held_now else None", "return FREEZE_HELD if until is not None else None", "frozen forever once held"),
 ("supply_hold.py", "    held.supply_held = False\n    if value is None:", "    if value is None:", "held flag never reset"),
 ("supply_hold.py", "    if wait:\n        held.supply_held", "    if True:\n        held.supply_held", "freeze stamped on every non-None write"),
 ("coordinator.py", "return supply_hold.freeze_reason(pump_arbiter.state_for(coord)) or learner_unmetered(", "return learner_unmetered(", "coordinator drops the held freeze"),
 ("coordinator.py", "    if early_cutoff.state_for(coord).interval_cut:\n        return early_cutoff.FREEZE_CUT\n    return supply_hold", "    return supply_hold", "cut freeze dropped (merged _tail_freeze)"),
 ("supply_hold.py", "wait = (age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value else age < MIN_RUN", "wait = (age < MIN_PAUSE or _ends_soon(inp, boosts, now)) if value else age <= MIN_RUN", "MIN_RUN < -> <="),
 ("supply_hold.py", "    if age is None or _passes(inp, boosts, now):\n        return value\n", "", "gate removed"),
 ("pump_arbiter.py", "if on is None and held.supply_held and not inp.entry_released:", "if on is None and held.supply_held:", "released entry retries"),
]
sel = [int(a) for a in sys.argv[1:]] or range(len(M))
for i in sel:
    f, a, b, why = M[i]
    path = WT / P / f; src = path.read_text()
    n = src.count(a)
    if n != 1:
        print(f"NOAPPLY {i} {f}: {why} (matches {n})"); continue
    path.write_text(src.replace(a, b))
    try:
        r = subprocess.run(["bash", f"{W}/ev/mutant_cmd.sh"], capture_output=True, text=True)
        out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
        fails = subprocess.run(["grep", "-h", "-m1", "FAIL\\|Error", f"{W}/blkA.out", f"{W}/blkB.out"], capture_output=True, text=True).stdout.strip().splitlines()
        print(f"{'KILLED  ' if r.returncode else 'SURVIVED'} {i:2d} {f}: {why} | {out} | {(fails[0][:140] if fails else '')}")
    finally:
        path.write_text(src)
print("worktree clean:", subprocess.run(["git", "-C", str(WT), "status", "--porcelain"], capture_output=True, text=True).stdout.strip() == "")
