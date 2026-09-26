import shutil, subprocess, sys, pathlib
SRC = pathlib.Path('/tmp/claude-0/i5/head')  # clean archive of the head commit
OPT = 'custom_components/heatpump_optimizer/optimizer.py'
PV = 'custom_components/heatpump_optimizer/pv.py'
MUTANTS = {
 'M1-P7-wallclock': (OPT, [('now_s = current_time.timestamp()', 'now_s = current_time.replace(tzinfo=None).timestamp()'),
                           ('starts = [ts.timestamp() for ts in result.timestamps]', 'starts = [ts.replace(tzinfo=None).timestamp() for ts in result.timestamps]')]),
 'M2-D12-band-floor': (OPT, [('low, band = 0.0, p_max', 'low, band = p_min, 0.1')]),
 'M3-D12-no-clip': (OPT, [('return float(min(1.0, max(0.0, (power - low) / band)))', 'return float((power - low) / band)')]),
 'M4-D2s281-scalar-halved': (OPT, [('\n            ) + weight * (np.sum(undershoot_u) + np.sum(undershoot_l)) * _COMFORT_FLOOR_L1', '\n            ) + 0.5 * weight * (np.sum(undershoot_u) + np.sum(undershoot_l)) * _COMFORT_FLOOR_L1')]),
 'M5-D2s281-batch-halved': (OPT, [('                ) + weight * (np.sum(undershoot_u) + np.sum(undershoot_l)) * _COMFORT_FLOOR_L1', '                ) + 0.5 * weight * (np.sum(undershoot_u) + np.sum(undershoot_l)) * _COMFORT_FLOOR_L1')]),
 'M6-D2s302-floor': (PV, [('return np.asarray(import_prices, dtype=float) - float(export_price)', 'return np.clip(np.asarray(import_prices, dtype=float) - float(export_price), 0.0, None)')]),
}
for name, (f, reps) in MUTANTS.items():
    d = pathlib.Path('/tmp/claude-0/mut') / name
    if d.exists(): shutil.rmtree(d)
    shutil.copytree(SRC, d, ignore=shutil.ignore_patterns('tools'))
    p = d / f; s = p.read_text()
    for a, b in reps:
        assert s.count(a) == 1, (name, a); s = s.replace(a, b)
    p.write_text(s)
    r = subprocess.run(['/home/claude/venv314/bin/python', '/tmp/claude-0/-home-claude/41b9b4b6-b90f-578b-a333-875e91f8ef0b/scratchpad/r9-f2-solver/run_block.py'],
                       cwd=d, env={'PYTHONPATH': 'tests/hastub', 'PATH': '/usr/bin:/bin'}, capture_output=True, text=True)
    out = r.stdout + r.stderr
    print(f'=== {name} rc={r.returncode}')
    for line in out.splitlines():
        if 'FAIL' in line or 'PASSED' in line or 'Error' in line:
            print('   ', line[:220])
