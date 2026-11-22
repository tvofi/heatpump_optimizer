import subprocess, sys, pathlib, os
WT = pathlib.Path(os.environ["HOME"]) / "wt-mut"
P = "custom_components/heatpump_optimizer/"
FEAT = ["python3", "tests/features.py"]
BLOCK = ["python3", "tools/audit/seat/features_block.py", "# R11-SEAM-cycle-reporting: how a failure is reported"]
M = {
 "M1": (P+"store.py", 'log_held(owner, key, True, "Could not persist %s: %s", what, err, exc_info=err)', '_LOGGER.debug("Could not persist %s: %s", what, err)', BLOCK),
 "M2": (P+"coordinator.py", 'log_held(coord.entry, _UPDATE_FAILED, True, "Error updating Heat Pump Optimizer: %s", err, exc_info=err)', '_LOGGER.error("Error updating Heat Pump Optimizer: %s", err, exc_info=True)', BLOCK),
 "M2b": (P+"coordinator.py", 'log_held(coord.entry, _UPDATE_FAILED, True,', 'log_held(coord, _UPDATE_FAILED, True,', BLOCK),
 "M3": (P+"optimizer.py", '_LOGGER.debug("L-BFGS-B restart failed; the start\'s own point kept", exc_info=True)', 'pass', BLOCK),
 "M4": (P+"services.py", 'if not away_mode.clears_return_time(raw) and away_mode.parse_return_time(raw) is None:', 'if False:', BLOCK),
 "M5": (P+"coordinator.py", 'coord._ctx = replace(self, _opt_config=replace(self._opt_config, **fields))', '[object.__setattr__(self._opt_config, k, v) for k, v in fields.items()]', BLOCK),
 "M6": (P+"coordinator.py", '            opt_config=ctx._opt_config,\n            draw=self._accuracy.draw,', '            draw=self._accuracy.draw,', BLOCK),
 "M7": (P+"coordinator.py", '    config_entry: HeatPumpOptimizerConfigEntry  # the typed entry (D10-s3-02)\n', '', ["python3", "tests/doc_claims.py"]),
 "M9": (P+"duty_switch.py", '        rec.dirty = False  # a failed save stays dirty', '        pass\n    rec.dirty = False  # a failed save stays dirty', FEAT),
 "M10": (P+"room_record.py", '        rec.unsaved = 0  # a failed save stays unsaved', '        pass\n    rec.unsaved = 0  # a failed save stays unsaved', ["sh","-c","python3 tests/finite_boundary.py && python3 tests/deployment_shape.py"]),
 "M11": (P+"away.py", None, None, BLOCK),
}
names = sys.argv[1:] or [k for k in M]
env = dict(os.environ, PYTHONPATH="tests/hastub:tests")
for n in names:
    f, old, new, cmd = M[n]
    p = WT / f; src = p.read_text()
    if old is None: continue
    c = src.count(old)
    if c != 1:
        print(f"{n} SKIP count={c}"); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(cmd, cwd=WT, env=env, capture_output=True, text=True, timeout=1500)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if "FAIL" in l][:6]
        print(f"{n} rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'}")
        for l in fails: print("   ", l[:300])
        print("   last:", (out.strip().splitlines() or [''])[-1][:200])
    finally:
        p.write_text(src)
    sys.stdout.flush()
subprocess.run(["git", "status", "--short"], cwd=WT)
print("MUT-DONE")
