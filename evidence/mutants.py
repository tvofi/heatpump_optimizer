"""Reviewer's own mutants for #2379. Each: (id, file, old, new, tests). Applies, runs, restores (git checkout)."""
import subprocess, sys, time, os
WT = "/Users/timmalmstrom/hpo-seats/r10s3/review-2379/wt"
EV = "/Users/timmalmstrom/hpo-seats/r10s3/review-2379/h/ev"
E = "custom_components/heatpump_optimizer/entity.py"
S = "custom_components/heatpump_optimizer/sensor.py"
C = "custom_components/heatpump_optimizer/climate.py"
MUT = [
 ("R1_np_unwrap", E, "    if isinstance(value, np.generic):\n        value = value.item()\n    if isinstance(value, bool)", "    if isinstance(value, bool)", ["finite_boundary"]),
 ("R2_types_ignored", S, "return payload_number(node.get(self._payload_path[-1]), self._payload_types)", "return payload_number(node.get(self._payload_path[-1]))", ["finite_boundary"]),
 ("R3_no_rounding", S, "        if value is None or self._payload_digits is None:\n            return value\n        return round(value, self._payload_digits)", "        return value", ["finite_boundary", "features"]),
 ("R4_dhw_text_zero", E, "    dhw = 0.0 if raw_dhw is None else payload_number(raw_dhw)", "    dhw = payload_number(raw_dhw) or 0.0", ["finite_boundary"]),
 ("R5_outdoor_order", E, "    if (data.get(\"reading_ok\") or {}).get(\"outdoor_temperature\"):", "    if False and (data.get(\"reading_ok\") or {}).get(\"outdoor_temperature\"):", ["finite_boundary", "features"]),
 ("R6_zone_swap", E, "            (\"upper_setpoint\", \"upper_floor_setpoint\"),\n            (\"lower_setpoint\", \"lower_floor_setpoint\"),", "            (\"upper_setpoint\", \"lower_floor_setpoint\"),\n            (\"lower_setpoint\", \"upper_floor_setpoint\"),", ["features", "finite_boundary"]),
 ("R7_climate_indoor_raw", C, "            indoor = payload_number(self.coordinator.data.get(\"indoor_temperature\"))\n            if indoor is not None:", "            indoor = self.coordinator.data.get(\"indoor_temperature\")\n            if indoor is not None:", ["finite_boundary"]),
 ("R8_hvac_skip_all", E, "            if owner.__module__.partition(\".\")[0] == \"homeassistant\":", "            if owner.__module__.partition(\".\")[0] != \"heatpump_optimizer\":", ["finite_boundary"]),
]
only = sys.argv[2:]
OVERRIDE = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "-" else None
env = dict(os.environ, PYTHONPATH="tests/hastub")
for mid, f, old, new, tests in MUT:
    if only and mid not in only: continue
    p = os.path.join(WT, f); src = open(p).read()
    n = src.count(old)
    if n != 1:
        print(f"{mid} NOT APPLIED (matches={n})", flush=True); continue
    open(p, "w").write(src.replace(old, new))
    try:
        for t in (OVERRIDE or tests):
            t0 = time.time()
            r = subprocess.run(["python3", f"tests/{t}.py"], cwd=WT, env=env, capture_output=True, text=True, timeout=2400)
            log = r.stdout + r.stderr
            open(f"{EV}/mut_{mid}_{t}_2.log", "w").write(log)
            fails = [l.strip()[:220] for l in log.splitlines() if l.strip().startswith("FAIL")]
            print(f"{mid} {t} rc={r.returncode} {int(time.time()-t0)}s {'KILLED' if r.returncode else 'SURVIVED'} fails={len(fails)}", flush=True)
            for l in fails[:4]: print("    ", l, flush=True)
    finally:
        subprocess.run(["git", "checkout", "--", f], cwd=WT, check=True)
print("restored; status:", subprocess.run(["git","status","--short"],cwd=WT,capture_output=True,text=True).stdout or "clean")
