"""The control for P9/P10: the same two gaps expressed on the MERGE BASE's own pump_arbiter._bounded,
to tell an introduced coverage gap from one this pull request inherited. Reviewer's instrument.
    python3 reviewer2_mutants_mergebase.py WORKTREE_AT_MERGE_BASE [script ...]"""
import subprocess, sys, os
W = sys.argv[1]; SCRIPTS = sys.argv[2:] or ["tests/block_duty.py"]
CC = os.path.join(W, "custom_components/heatpump_optimizer")
M = [
 ("Q9 (= P9) merge base: _bounded drops the caller's floor", "pump_arbiter.py",
  "    value = max(value, floor, low if low is not None else floor)\n",
  "    value = max(value, -1e9, low if low is not None else -1e9)\n"),
 ("Q10 (= P10) merge base: _bounded drops the caller's rounding", "pump_arbiter.py",
  "        inp.hass, entity, value, rounding=rounding,\n",
  '        inp.hass, entity, value, rounding="nearest",\n'),
 ("NULL", "pump_arbiter.py", "    low, high = setpoint_range_c(inp.hass, entity)\n", "    low, high = setpoint_range_c(inp.hass, entity)  # null\n"),
]
for name, f, old, new in M:
    p = os.path.join(CC, f); src = open(p).read()
    if src.count(old) != 1: print(f"{name}: ANCHOR x{src.count(old)}", flush=True); continue
    open(p, "w").write(src.replace(old, new))
    try:
        out = []
        for s in SCRIPTS:
            r = subprocess.run([sys.executable, s], cwd=W, capture_output=True, text=True, env={**os.environ, "PYTHONPATH": "tests/hastub"}, timeout=1800)
            fails = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip().startswith("FAIL")]
            out.append((s, r.returncode, fails))
        print(f"{name}: {'KILLED' if any(rc for _s, rc, _f in out) else 'SURVIVED'} " + " ".join(f"{s} rc={rc} {len(fl)} failing" for s, rc, fl in out), flush=True)
        for _s, _rc, fl in out:
            for l in fl[:2]: print("    " + l[:170], flush=True)
    finally:
        open(p, "w").write(src)
