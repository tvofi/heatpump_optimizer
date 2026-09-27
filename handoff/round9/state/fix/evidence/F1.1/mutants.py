"""F1.1 mutation proof: each mutant applied to a temp copy of the head tree,
the pin that owns it run there, FAIL lines captured; then the unmutated copy."""
import shutil, subprocess, sys, tempfile, os
from pathlib import Path

HEAD = Path(sys.argv[1])
PY = sys.argv[2]
C = "custom_components/heatpump_optimizer/"
DST = ["env", "HASTUB_TZ=Europe/Stockholm", "PYTHONPATH=tests/hastub:tests:custom_components", PY, "tests/dst_checks.py"]
OM = ["env", "PYTHONPATH=tests/hastub", PY, "tests/open_meteo.py"]
F11 = ["env", "PYTHONPATH=tests/hastub", PY, "/tmp/claude-0/r9f11/f11_block.py"]

M = [
    ("P-grid", C + "coordinator.py", "_utc_age_seconds(now, midnight) / 60 / FORECAST_STEP_MINUTES", "(now - midnight).total_seconds() / 60 / FORECAST_STEP_MINUTES", DST),
    ("P-record-accuracy", C + "coordinator.py", '_utc_age_seconds(now, pending["when"]) / 3600.0', '(now - pending["when"]).total_seconds() / 3600.0', DST),
    ("P-dhw-lead", C + "coordinator.py", "self._dhw_accuracy.note_lead_prediction(\n                    utc_shift(solve_time, timedelta(hours=lead)),", "self._dhw_accuracy.note_lead_prediction(\n                    solve_time + timedelta(hours=lead),", DST),
    ("P-room-lead", C + "coordinator.py", "self._accuracy.note_lead_prediction(\n                    utc_shift(solve_time, timedelta(hours=lead)),", "self._accuracy.note_lead_prediction(\n                    solve_time + timedelta(hours=lead),", DST),
    ("P-next-opt", C + "coordinator.py", "self._next_optimization = utc_shift(dt_util.now(), timedelta(", "self._next_optimization = dt_util.now() + (timedelta(", DST),
    ("P-score", C + "accuracy.py", "age_h = utc_elapsed_seconds(now, target_time) / 3600.0", "age_h = (now - target_time).total_seconds() / 3600.0", DST),
    ("P-ext-rate", C + "external_heat.py", "dt_h = utc_elapsed_seconds(now, previous[0]) / 3600.0", "dt_h = (now - previous[0]).total_seconds() / 3600.0", DST),
    ("P-dhw-dyn", C + "dhw_learning.py", "dt_h = utc_elapsed_seconds(now, previous_time) / 3600.0", "dt_h = (now - previous_time).total_seconds() / 3600.0", DST),
    ("R-replay-step", "tests/replay.py", "    t = dt_util.as_utc(start)\n", "    t = start\n", DST),
    ("I1-outage-guard", C + "coordinator.py", "        if last.tzinfo is None and now.tzinfo is not None:", "        if False:", DST),
    ("I1-immersion-guard", C + "coordinator.py", "            if when.tzinfo is None and now.tzinfo is not None:", "            if False:", DST),
    ("I1-M02-open-meteo", C + "open_meteo.py", "        if parsed.tzinfo is None:", "        if False:", OM),
    ("N-target", C + "coordinator.py", "        return float({**self.entry.data, **self.entry.options}.get(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP))", '        return float(getattr(self, "_ctx", self)._opt_config.target_temp)', F11),
    ("R-as_utc-naive", C + "accuracy.py", "    if value.tzinfo is None:\n        return value.replace", "    if False:\n        return value.replace", DST),
    ("R-as_utc-aware", C + "accuracy.py", "    return value.astimezone(timezone.utc)\n", "    return value.replace(tzinfo=timezone.utc)\n", DST),
    ("R-utc_shift-wall", C + "accuracy.py", "    return (when.astimezone(timezone.utc) + delta).astimezone(when.tzinfo)", "    return when + delta", DST),
    ("R-outage-recovery", C + "coordinator.py", "self._outage_recovery_until = utc_shift(now, timedelta(", "self._outage_recovery_until = now + (timedelta(", DST),
    ("R-outage-dhw", C + "coordinator.py", "self._outage_dhw_until = utc_shift(now, timedelta(", "self._outage_dhw_until = now + (timedelta(", DST),
    ("R-replay-forecast-walk", "tests/replay.py", "t = dt_util.as_utc(now) + timedelta(hours=h)", "t = now + timedelta(hours=h)", DST),
    ("R-replay-price-walk", "tests/replay.py", "            t = dt_util.as_utc(day0)\n", "            t = day0\n", DST),
    ("R-replay-price-label", "tests/replay.py", '"starts_at": dt_util.as_local(t).isoformat()', '"starts_at": t.isoformat()', DST),
    ("CONTROL-unmutated", None, None, None, None),
]
only = sys.argv[3:]
for name, rel, old, new, cmd in M:
    if only and name not in only:
        continue
    with tempfile.TemporaryDirectory() as d:
        tree = Path(d) / "t"
        shutil.copytree(HEAD, tree, ignore=shutil.ignore_patterns(".git", "__pycache__"), symlinks=True)
        runs = [DST, OM, F11] if rel is None else [cmd]
        if rel is not None:
            f = tree / rel
            s = f.read_text()
            assert s.count(old) == 1, (name, s.count(old))
            f.write_text(s.replace(old, new))
        for c in runs:
            p = subprocess.run(c, cwd=tree, capture_output=True, text=True)
            fails = [l.strip() for l in p.stdout.splitlines() if "FAIL" in l]
            tail = [l.strip() for l in p.stdout.splitlines() if "PASSED" in l or "FAILED" in l]
            print(f"{name} [{c[-1].split('/')[-1]}] rc={p.returncode} {tail[-1:] }")
            for l in fails:
                print("   ", l[:400])
            if p.returncode and not fails:
                print("   stderr:", p.stderr.strip().splitlines()[-1:] )
