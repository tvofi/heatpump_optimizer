import subprocess, sys, pathlib
T = pathlib.Path("/tmp/rv/mut/custom_components/heatpump_optimizer")
A, D, C = "accuracy.py", "draw_range.py", "coordinator.py"
M = [
 ("floor:min->low", D, "return max(float(on_threshold_kw(params)), min(floor, low_kw))", "return max(float(on_threshold_kw(params)), low_kw)"),
 ("floor:max dropped", D, "return max(float(on_threshold_kw(params)), min(floor, low_kw))", "return min(floor, low_kw)"),
 ("floor:config-key guard dropped", D, "if draw is None or cfg_min <= 0.0 or draw.config != (cfg_min, cfg_max):", "if draw is None or cfg_min <= 0.0:"),
 ("floor:cfg_min guard dropped", D, "if draw is None or cfg_min <= 0.0 or draw.config != (cfg_min, cfg_max):", "if draw is None or draw.config != (cfg_min, cfg_max):"),
 ("floor:MIN_SAMPLES->any", D, "    if len(drawn) < MIN_SAMPLES:\n        return floor\n    low_kw", "    if not drawn:\n        return floor\n    low_kw"),
 ("run_asked:min half dropped", D, "if a >= floor and a > 0.0]", "if a > 0.0]"),
 ("run_asked:>0 half dropped", D, "if a >= floor and a > 0.0]", "if a >= floor]"),
 ("evidence:no window pending", D, "    if draw is None:\n        return ASK_UNOBTAINABLE", "    if draw is None:\n        return ASK_PENDING"),
 ("evidence:full window stays pending", D, "return ASK_UNOBTAINABLE if len(draw.samples) >= WINDOW else ASK_PENDING", "return ASK_PENDING"),
 ("evidence:flat asks pending", D, "    if high < FOLLOW_ASK_SPAN * low:\n        return ASK_UNOBTAINABLE", "    if high < FOLLOW_ASK_SPAN * low:\n        return ASK_PENDING"),
 ("judge_ratio:pending not held", A, "            self.held.append(row)\n            return COP_REFUSED_NO_EVIDENCE", "            return COP_REFUSED_NO_EVIDENCE"),
 ("judge_ratio:pending arm deleted", A, "        if state == ASK_PENDING:\n            self.held.append(row)\n            return COP_REFUSED_NO_EVIDENCE\n", ""),
 ("judge_ratio:follows falls to base rule", A, "<= COP_ASK_TOLERANCE or state == ASK_FOLLOWS:", "<= COP_ASK_TOLERANCE:"),
 ("judge_ratio:off-ask refusal dropped", A, "        if state == ASK_IGNORED:\n            # #2262", "        if False:\n            # #2262"),
 ("release:ignored by base rule", A, "        if state == ASK_IGNORED:\n            return []\n", ""),
 ("release:follows drops", A, "        if state == ASK_FOLLOWS:\n            return rows\n", "        if state == ASK_FOLLOWS:\n            return []\n"),
 ("release:follows by base rule", A, "        if state == ASK_FOLLOWS:\n            return rows\n", ""),
 ("release:no week exit", A, "0.0 <= utc_elapsed_seconds(now, row.at) <= COP_HOLD_HORIZON_S", "0.0 <= utc_elapsed_seconds(now, row.at)"),
 ("release:future stamp waits", A, "0.0 <= utc_elapsed_seconds(now, row.at) <= COP_HOLD_HORIZON_S", "utc_elapsed_seconds(now, row.at) <= COP_HOLD_HORIZON_S"),
 ("release:no push-out", A, "if i >= over and 0.0 <=", "if 0.0 <="),
 ("release:pending waiting rows dropped", A, "                    self.held.append(row)\n                else:", "                    pass\n                else:"),
 ("release:hold not cleared", A, "        self.held.clear()\n", ""),
 ("release:base rule always folds", A, "        return [r for r in rows if self._base_folds(r, params)]", "        return rows"),
 ("judge_floor:no window", A, "if min(asked_kw, drawn_kw) < power_floor_kw(draw, params):", "if min(asked_kw, drawn_kw) < power_floor_kw(None, params):"),
 ("diag:configured floor", A, '"power_floor_kw": round(power_floor_kw(draw, params), 3),', '"power_floor_kw": round(power_floor_kw(None, params), 3),'),
 ("diag:held count 0", A, '"held_intervals": len(record.held),', '"held_intervals": 0,'),
 ("walk_ratio:returns walked", A, "        return before\n", "        return self.ratio_ewma\n"),
 ("coord:no release", C, "        for row in self._measured_cop.release(draw, params, dt_util.now()):\n            self._fold_cop_evidence(row.asked_kw, row.drawn_kw, None, row.reference, row.cop_scale)\n", "        self._measured_cop.release(draw, params, dt_util.now())\n"),
 ("coord:replay at live scale", C, "heat_kw, self._cop_scale if read_scale is None else read_scale", "heat_kw, self._cop_scale"),
 ("coord:replay feeds tail", C, "        if read_scale is not None:\n            return None  # a held", "        if False:\n            return None  # a held"),
 ("coord:row stamped live scale 1.0", C, "self._cop_reference_curve(), self._cop_scale, dt_util.now())", "self._cop_reference_curve(), 1.0, dt_util.now())"),
 ("coord:fold floor no window", C, "MeasuredCop.judge_floor(commanded, self._measured_power, params, draw)):", "MeasuredCop.judge_floor(commanded, self._measured_power, params)):"),
 ("coord:flow-lift floor no window", C, "if commanded < draw_range.power_floor_kw(coord._accuracy.draw, params):", "if commanded < draw_range.power_floor_kw(None, params):"),
 ("coord:span-close floor no window", C, "MeasuredCop.judge_floor(close.asked_kw, close.elec_kw, ctx._thermal_params, coord._accuracy.draw)", "MeasuredCop.judge_floor(close.asked_kw, close.elec_kw, ctx._thermal_params)"),
 ("coord:save cadence %10", C, "if self._cop_samples // 10 != cop_samples_before // 10:", "if self._cop_samples != cop_samples_before and self._cop_samples % 10 == 0:"),
 ("coord:replay reference = live curve", C, "None, row.reference, row.cop_scale)", "None, self._cop_reference_curve(), row.cop_scale)"),
 ("coord:learn passes no window", C, "        self._learn_measured_cop(self._accuracy.draw)\n", "        self._learn_measured_cop()\n"),
]
only = sys.argv[1:] 
for name, f, old, new in M:
    if only and not any(o in name for o in only): continue
    p = T / f; src = p.read_text()
    if src.count(old) != 1:
        print(f"MUTANT {name}: NOT-APPLIED count={src.count(old)}"); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run(["/tmp/rv/blocks.sh", "/tmp/rv/mut", "2"], capture_output=True, text=True)
    finally:
        p.write_text(src)
    first = (r.stdout.strip().splitlines() or ["<no output>"])[0][:200]
    print(f"MUTANT {name}: {'KILLED' if r.returncode else 'SURVIVED'} | {first}", flush=True)
r = subprocess.run(["/tmp/rv/blocks.sh", "/tmp/rv/mut", "2"], capture_output=True, text=True)
print("NULL unmutated rc", r.returncode, r.stdout.strip().replace("\n"," | "))
subprocess.run(["git","-C","/tmp/rv/mut","status","--short"])
