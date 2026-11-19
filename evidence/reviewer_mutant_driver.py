#!/usr/bin/env python3
"""Reviewer's mutant driver: apply one textual mutant, run the ADR-001 block, restore."""
import subprocess, sys, pathlib
WT = pathlib.Path("/Users/timmalmstrom/hpo-seats/r11/rev-3728/wt")
P = "custom_components/heatpump_optimizer/"
MUTANTS = [
 ("R1", P+"plan_step.py", "    return i if now < starts[i] + span else None", "    return i"),
 ("R2", P+"plan_step.py", "return covering_index(stamps, now, PLAN_STEP, PLAN_STEP)", "return covering_index(stamps, now, PLAN_STEP)"),
 ("R3", P+"pump_arbiter.py", "    i = plan_step_index(result, now)\n    points", "    import bisect as _b\n    i = _b.bisect_right(list(getattr(result, 'timestamps', None) or []), now) - 1\n    i = i if i >= 0 else None\n    points"),
 ("R4", P+"early_cutoff.py", "    i = plan_step_index(plan, now)", "    import bisect as _b\n    i = _b.bisect_right(list(getattr(plan, 'timestamps', None) or []), now) - 1\n    i = i if i >= 0 else None"),
 ("R5", P+"entity.py", "    if isinstance(value, float) and not math.isfinite(value):\n        return None\n", ""),
 ("R6", P+"drift.py", "    if value.tzinfo is None:\n        return value.replace(tzinfo=timezone.utc)\n    return value.astimezone", "    return value.astimezone"),
 ("R7", P+"drift.py", "        del self.evidence[:-EVIDENCE_KEEP]\n", ""),
 ("R8", P+"const.py", "WATER_CP_KJ_PER_KG_K: Final = WATER_SPECIFIC_HEAT * 3600.0 / WATER_KG_PER_L", "WATER_CP_KJ_PER_KG_K: Final = 4.186"),
 ("R9", P+"sensor.py", "volume * band * WATER_SPECIFIC_HEAT * 30.0", "volume * band * (4.187 / 3600.0) * 30.0"),
 ("R10", P+"manual_plan.py", "    return utc_instant(when).timestamp()", "    return when.timestamp()"),
 ("R11", P+"pump_arbiter.py", "    if (i is None or duty != \"both\"", "    if (duty != \"both\""),
 ("R12", P+"coordinator.py", "        return utc_instant(ts)", "        return ts.astimezone(__import__('datetime').timezone.utc)"),
 ("R13", P+"open_meteo.py", "        times.append(utc_instant(parsed))", "        times.append(parsed.astimezone(__import__('datetime').timezone.utc))"),
]
only = set(sys.argv[1:])
for name, rel, old, new in MUTANTS:
    if only and name not in only: continue
    f = WT/rel; src = f.read_text()
    n = src.count(old)
    if n != 1:
        print(f"{name} SKIP: anchor count {n}", flush=True); continue
    f.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", 'exec(open("../prelude.py").read())',
                            "# -- round-11 ADR-001 (R11-SEAM-kernel-step)", "# -- N-silent-zero (#2233)"],
                           cwd=WT, env={"PYTHONPATH": "tests/hastub", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
                           capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
        err = "Traceback" in out
        print(f"{name} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} traceback={err} fails={[x[:90] for x in fails]}", flush=True)
    finally:
        f.write_text(src)
