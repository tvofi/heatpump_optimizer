import json, subprocess, sys, os
W="/tmp/tmp.fZlfDxzmcH"; WT=W+"/wt"; C="custom_components/heatpump_optimizer/"
M = [
 ("G", C+"coordinator.py", 'MeasuredCop.from_dict(stored.get("measured_cop") if _COP_BASELINE_KEY in stored else None)', 'MeasuredCop.from_dict(stored.get("measured_cop"))'),
 ("CUSUM-CALL_DEL", C+"coordinator.py", 'self._cop_health_cusum.load(stored.get(_COP_HEALTH_CUSUM_KEY))', 'pass'),
 ("DOM-stat", C+"store.py", '"cop_health_cusum_measured/stat": Domain("real", 0.0,', '"cop_health_cusum_measured/stat": Domain("real", 1.0,'),
 ("DOM-band", C+"store.py", '"cop_baseline_measured/*/1": Domain("int", 1)', '"cop_baseline_measured/*/1": Domain("int", 2)'),
 ("M1", C+"coordinator.py", '        if measured:\n            self._measured_cop.record', '        if True:\n            self._measured_cop.record'),
 ("M3", C+"thermal_model.py", 'return None if self.measured_heat and not self.heat_counter else False', 'return False'),
 ("M4", C+"thermal_model.py", '    return const.ESTIMATE_ID_MARK in str(entity_id or "").lower()', '    return False'),
 ("M5", C+"coordinator.py", 'raw_baseline = stored.get(_COP_BASELINE_KEY)', 'raw_baseline = stored.get(_COP_BASELINE_KEY) or stored.get("cop_baseline")'),
 ("M5b-cusum-old", C+"coordinator.py", 'self._cop_health_cusum.load(stored.get(_COP_HEALTH_CUSUM_KEY))', 'self._cop_health_cusum.load(stored.get(_COP_HEALTH_CUSUM_KEY) or stored.get("cop_health_cusum"))'),
 ("M6", C+"coordinator.py", '    if not measurable:\n        return None, "cop_unmeasurable", []\n', ''),
 ("M7", C+"thermal_model.py", '            and (self.heat_sees_dhw or not dhw)\n', ''),
 ("R-power_est", C+"thermal_model.py", '            and not (self.heat_estimated or self.power_estimated)', '            and not (self.heat_estimated)'),
 ("R-heat_est", C+"thermal_model.py", '            and not (self.heat_estimated or self.power_estimated)', '            and not (self.power_estimated)'),
 ("R-electric", C+"thermal_model.py", '            and self.cop_electric()\n', ''),
 ("R-counter-outranks", C+"thermal_model.py", 'heat_estimated=not cfg.get(const.CONF_HEAT_ENERGY_ENTITY) and _estimated(', 'heat_estimated=_estimated('),
 ("R-src-estimate", C+"thermal_model.py", '    if source == const.METER_SOURCE_ESTIMATE:\n        return True\n', ''),
 ("R-src-meter", C+"thermal_model.py", '    if source == const.METER_SOURCE_METER:\n        return False\n', ''),
 ("R-sees_dhw-cfg", C+"thermal_model.py", 'heat_sees_dhw=bool(cfg.get(const.CONF_HEAT_METER_SEES_DHW, const.DEFAULT_HEAT_METER_SEES_DHW)),', 'heat_sees_dhw=False,'),
 ("R-obs-estimated", C+"coordinator.py", 'estimated=install.heat_estimated or install.power_estimated,', 'estimated=False,'),
 ("R-obs-guard", C+"accuracy.py", '    if not measured_heat:\n        return COP_NOT_MEASURABLE\n', ''),
 ("R-score-arg", C+"coordinator.py", 'probe_install(_ctx_of(self)._config).cop_measured(False)),', 'True),'),
 ("R-noheat-refuse", C+"coordinator.py", '        if (measured := probe_install(_ctx_of(self)._config).cop_sample(heat_kw, bool(cop_curve_dhw))) is None:\n            return COP_REFUSED_NO_HEAT\n', '        measured = probe_install(_ctx_of(self)._config).cop_sample(heat_kw, bool(cop_curve_dhw))\n'),
 ("R-factory-void", C+"coordinator.py", '"vent_cusum", _COP_BASELINE_KEY, _COP_HEALTH_CUSUM_KEY,', '"vent_cusum", "cop_baseline", "cop_health_cusum",'),
]
pre = json.load(open(W+"/prelude.json"))
args=[]
for p in pre: args += ["--prelude", p]
only = sys.argv[1:]
for name, f, old, new in M:
    if only and name not in only: continue
    path = os.path.join(WT, f); s = open(path).read()
    n = s.count(old)
    if n != 1: print(f"RESULT mutant={name} APPLY-FAIL count={n}", flush=True); continue
    open(path,"w").write(s.replace(old,new))
    try:
        p = subprocess.run([sys.executable,"tools/audit/seat/features_block.py",*args,'R.section("R10-HOTFIX-COP-UNMEASURED','R.section("early cut-off'],cwd=WT,capture_output=True,text=True,timeout=600)
        fails=[l.strip() for l in p.stdout.splitlines() if l.strip().startswith("FAIL")]
        tail=[l for l in p.stdout.splitlines() if "FEATURES BLOCK" in l]
        err = p.stderr.strip().splitlines()[-1:] if p.returncode and not fails else []
        print(f"RESULT mutant={name} rc={p.returncode} {tail[-1] if tail else ''} {err}", flush=True)
        for l in fails[:6]: print("   ", l[:220], flush=True)
    finally:
        open(path,"w").write(s)
