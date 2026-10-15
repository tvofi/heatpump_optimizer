"""D3-s3 mutant catalogue (D3.M1). Hand-weighted selection, no RNG (seed: n/a, recorded here).
Weights: 3 = guard on money/comfort/hardware, 2 = guard on a published value, 1 = hygiene guard.
Each mutant: (id, weight, file, old, new). old must occur exactly once."""
P = "custom_components/heatpump_optimizer/"
MUTANTS = [
 ("M01",3,"power_guard.py","not self.suppressing and self._over_count >= HYSTERESIS_SAMPLES","not self.suppressing and self._over_count >= 1"),
 ("M02",3,"power_guard.py","    if mean_so_far_kw is None:\n        elapsed = 0.0\n","    if mean_so_far_kw is None:\n        pass\n"),
 ("M03",3,"power_guard.py","self.suppressing and self._clear_count >= HYSTERESIS_SAMPLES","self.suppressing and self._clear_count >= 1"),
 ("M04",2,"wear.py","if self._streak < START_HYSTERESIS_SAMPLES:","if self._streak < 1:"),
 ("M05",2,"wear.py","        if immersion_active:\n            self._streak = 0\n            return False\n","        if False:\n            self._streak = 0\n            return False\n"),
 ("M06",3,"wear.py","return float(replacement_cost) / max(1, int(rated_starts))","return float(replacement_cost)"),
 ("M07",3,"silent_mode.py","cap = max(float(fraction), CAPACITY_FLOOR_FRACTION) * float(p_max)","cap = float(fraction) * float(p_max)"),
 ("M08",3,"early_cutoff.py","if now - held.cut_at >= MIN_OFF:","if now - held.cut_at >= MIN_OFF * 0:"),
 ("M09",3,"early_cutoff.py","return max(base, *_planned_room(inp.plan, now)) + MARGIN_K","return base + MARGIN_K"),
 ("M10",3,"early_cutoff.py","if held.cycle_end is None or held.cycle_end - utc < MIN_OFF:","if held.cycle_end is None:"),
 ("M11",2,"curve_learning.py","if worst_margin_c < COMFORT_MARGIN_C:","if worst_margin_c < 0.0:"),
 ("M12",2,"curve_learning.py","if self.bias >= BIAS_MAX:","if False:"),
 ("M13",3,"setpoint_check.py","floor = max(floor, float(params.dhw_legionella_temp))","floor = floor"),
 ("M14",3,"pump_arbiter.py","value = min(value, high) if high is not None else value","value = value"),
 ("M15",1,"dhw_draws.py","self._open_kwh += max(0.0, float(energy_kwh))","self._open_kwh += float(energy_kwh)"),
 ("M16",2,"notifier.py","if low >= floor:","if low > floor:"),
 ("M17",2,"comfort_band.py","    if night > day:","    if night > day + 100:"),
 ("M18",2,"away.py",'        if value in ("not_home", "away"):','        if value in ("not_home",):'),
]
