import subprocess, sys, pathlib, os
WT = pathlib.Path(os.environ.get("MUTWT", os.environ["HOME"] + "/wt"))
P = "custom_components/heatpump_optimizer/"
BLOCK = ["python3", "tools/audit/seat/features_block.py", "# R11-SEAM-cycle-reporting: how a failure is reported"]
env = dict(os.environ, PYTHONPATH="tests/hastub:tests")
M = {
 "NULL": (None, None, None, BLOCK),
 "M1": (P+"store.py", 'log_held(owner, key, True, "Could not persist %s: %s", what, err, exc_info=err)', '_LOGGER.debug("Could not persist %s: %s", what, err)', BLOCK),
 "M2": (P+"coordinator.py", 'log_held(coord.entry, _UPDATE_FAILED, True, "Error updating Heat Pump Optimizer: %s", err, exc_info=err)', '_LOGGER.error("Error updating Heat Pump Optimizer: %s", err, exc_info=True)', BLOCK),
 "M2b": (P+"coordinator.py", 'log_held(coord.entry, _UPDATE_FAILED, True,', 'log_held(coord, _UPDATE_FAILED, True,', BLOCK),
 "M3": (P+"optimizer.py", '        _LOGGER.debug("L-BFGS-B restart failed; the start\'s own point kept", exc_info=True)\n', '', BLOCK),
 "M4": (P+"services.py", 'if not away_mode.clears_return_time(raw) and away_mode.parse_return_time(raw) is None:', 'if False:', BLOCK),
 "M5": (P+"coordinator.py", 'coord._ctx = replace(self, _opt_config=replace(self._opt_config, **fields))', '[setattr(self._opt_config, k, v) for k, v in fields.items()]', BLOCK),
 "M6": (P+"coordinator.py", '            defrosting=self._pump_signals.defrosting,\n            opt_config=ctx._opt_config,\n', '            defrosting=self._pump_signals.defrosting,\n', BLOCK),
 "M8": (P+"quality_scale.yaml", "  strict-typing:\n    status: todo\n", "  strict-typing:\n    status: done\n", ["python3", "tests/entities.py"]),
 "M7": (P+"coordinator.py", '    config_entry: HeatPumpOptimizerConfigEntry  # the typed entry (D10-s3-02)\n', '', ["python3", "tests/doc_claims.py"]),
}
for name in sys.argv[1:]:
    f, old, new, cmd = M[name]
    if f:
        p = WT / f; src = p.read_text()
        assert src.count(old) == 1, (name, src.count(old))
        p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(cmd, cwd=WT, env=env, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l for l in out.splitlines() if l.lstrip().startswith("FAIL") or "PASSED" in l or "FAILED" in l or "Traceback" in l]
        print(f"RESULT {name} rc={r.returncode}")
        for l in fails[:12]: print("   ", l[:220])
    finally:
        if f: subprocess.run(["git", "checkout", "--", f], cwd=WT)
