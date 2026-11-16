import json, subprocess, sys
S = sys.argv[1]; T = S + "/mut"
A = "custom_components/heatpump_optimizer/accuracy.py"; C = "custom_components/heatpump_optimizer/coordinator.py"; D = "custom_components/heatpump_optimizer/draw_range.py"
M = [
 ("admission state guard: == UNOBTAINABLE -> != IGNORED", A, "return state == ASK_UNOBTAINABLE and draw is not None and not measured_heat", "return state != ASK_IGNORED and draw is not None and not measured_heat"),
 ("admission measured-heat guard dropped", A, "return state == ASK_UNOBTAINABLE and draw is not None and not measured_heat", "return state == ASK_UNOBTAINABLE and draw is not None"),
 ("restore statement deleted", C, "        if self._measured_cop.take_restore():\n            self._apply_cop_scale(ctx._config.cop_scale)\n", ""),
 ("restore target: current scale", C, "self._apply_cop_scale(ctx._config.cop_scale)\n        if refusal", "self._apply_cop_scale(self._cop_scale)\n        if refusal"),
 ("judge_ratio latch: ignored folds", A, "return COP_REFUSED_OFF_ASK if verdict == ASK_IGNORED else None", "return None"),
 ("release: reset dropped", A, "            self.probe.clear()\n            self.scale_response, self.reseeded = ASK_PENDING, False\n", ""),
 ("from_dict: verdict not read", A, "            record.scale_response, record.restore_due = response, response == ASK_IGNORED\n", "            pass\n"),
 ("clamp re-seed dropped", A, "        if not self.probe and not self.reseeded and not COP_SCALE_MIN < row.cop_scale < COP_SCALE_MAX:", "        if False:"),
 ("draw_response slope: >= -> <", D, "return ASK_FOLLOWS if slope >= FOLLOW_SLOPE_MIN else", "return ASK_FOLLOWS if slope < FOLLOW_SLOPE_MIN else"),
 ("judge_floor no-draw guard dropped", A, "if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw", "if min(asked_kw, drawn_kw or 0.0) < power_floor_kw"),
]
for name, path, old, new in M:
    p = f"{T}/{path}"; src = open(p).read()
    if src.count(old) != 1:
        print(f"MUTANT {name}: NOT-APPLIED (matches={src.count(old)})", flush=True); continue
    open(p, "w").write(src.replace(old, new))
    r = subprocess.run(["bash", f"{S}/drive.sh", T], capture_output=True, text=True)
    subprocess.run(["git", "-C", T, "checkout", "-q", "--", path])
    out = r.stdout + r.stderr
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")]
    tail = [l for l in out.splitlines() if "FEATURES BLOCK" in l or "Error" in l][-1:]
    print(f"MUTANT {name}: rc={r.returncode} {'KILLED' if r.returncode else 'SURVIVED'} {tail} first_fail={fails[:1]}", flush=True)
print("MUTANTS DONE", flush=True)
