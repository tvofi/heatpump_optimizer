import subprocess, sys, pathlib, re
M = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
C='custom_components/heatpump_optimizer/'
muts = {
 'N00_null_comment': (C+'accuracy.py', 'from .thermal_model import is_sunlit_interval\n', 'from .thermal_model import is_sunlit_interval  # null\n'),
 'R01_house_gate_off': (C+'coordinator.py', '        # #2223: dark only; a sunlit residual carries the aperture\'s error here.\n        if is_sunlit_interval(previous_state.solar_radiation):\n            return\n', '        if False:\n            return\n'),
 'R02_lower_gate_off': (C+'coordinator.py', '        # #2223: the same dark gate; the lower replay carries the same sun term.\n        if is_sunlit_interval(previous_state.solar_radiation):\n            return\n', '        if False:\n            return\n'),
 'R03_refit_gate_off': (C+'accuracy.py', '    if is_sunlit_interval(s.solar_radiation):\n        return None\n', '    if False:\n        return None\n'),
 'R04_settled_clause_del': (C+'coordinator.py', '            or settled < INTERNAL_GAINS_MIN_UA_CONFIDENCE\n', ''),
 'R05_gauge_ge': (C+'thermal_model.py', 'return float(solar_radiation or 0.0) > HEAT_LOSS_MAX_SOLAR_W_M2', 'return float(solar_radiation or 0.0) >= HEAT_LOSS_MAX_SOLAR_W_M2'),
 'R06_gauge_1000': (C+'const.py', 'HEAT_LOSS_MAX_SOLAR_W_M2: Final = 50.0', 'HEAT_LOSS_MAX_SOLAR_W_M2: Final = 1000.0'),
 'R07_sample_solar_dropped': (C+'coordinator.py', '                    solar_radiation=pending.get("solar"),  # #2223, refit\'s gate\n', ''),
 'R08_pending_solar_none': (C+'coordinator.py', '"solar": ctx._current_state.solar_radiation,', '"solar": None,'),
 'R09_from_dict_drop': (C+'accuracy.py', '            solar_radiation=num("solar_radiation"),\n', ''),
 'R10_to_dict_drop': (C+'accuracy.py', '            "solar_radiation": self.solar_radiation,\n', ''),
 'R11_gate_before_aperture': (C+'coordinator.py', '        self._fold_solar_aperture(previous_state, residual, dt_h)\n        # #2223: dark only; a sunlit residual carries the aperture\'s error here.\n        if is_sunlit_interval(previous_state.solar_radiation):\n            return\n', '        if is_sunlit_interval(previous_state.solar_radiation):\n            return\n        self._fold_solar_aperture(previous_state, residual, dt_h)\n'),
 'R12_gate_before_cusum': (C+'coordinator.py', '        vent_changed = self._vent_cusum.update(now,', '        if is_sunlit_interval(previous_state.solar_radiation):\n            return\n        vent_changed = self._vent_cusum.update(now,'),
 'R14_pending_solar_line_deleted': (C+'coordinator.py', '            "solar": ctx._current_state.solar_radiation,  # #2223, the sample\'s\n', ''),
 'R13_gains_threshold_0': (C+'const.py', 'INTERNAL_GAINS_MIN_UA_CONFIDENCE: Final = 0.9', 'INTERNAL_GAINS_MIN_UA_CONFIDENCE: Final = 0.0'),
}
only = sys.argv[3:] or list(muts)
for name in only:
    if name != 'M00_unmutated':
        f, a, b = muts[name]; p = M/f; s = p.read_text()
        assert s.count(a) == 1, (name, s.count(a)); p.write_text(s.replace(a, b))
    r = subprocess.run(['python3','tests/features.py'], cwd=M, env={**__import__('os').environ,'PYTHONPATH':'tests/hastub'}, capture_output=True, text=True)
    out = r.stdout + r.stderr
    (OUT/f'{name}.log').write_text(out)
    fails = [l for l in out.splitlines() if l.startswith('  FAIL ') or l.startswith('Traceback') or re.match(r'^[A-Za-z]+Error:', l)][:15]
    tail = [l for l in out.splitlines() if 'FEATURE CHECKS' in l][-1:]
    print(f'RESULT {name} rc={r.returncode} ' + ' | '.join(tail), flush=True)
    for l in fails: print('   ', l[:220], flush=True)
    subprocess.run(['git','checkout','-q','--','.'], cwd=M)
