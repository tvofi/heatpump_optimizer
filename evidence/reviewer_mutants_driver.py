import subprocess, sys, os
os.chdir(os.path.expanduser("~/wt"))
D="custom_components/heatpump_optimizer/draw_range.py"; C="custom_components/heatpump_optimizer/coordinator.py"; SN="custom_components/heatpump_optimizer/sensor.py"
M=[
("M01_observe_no_update",D,"        update_floor(self)\n",""),
("M02_clear_threshold",D,"moved = low if low > (1.0 + AGREE_TOLERANCE) * cfg_min else None","moved = low if low > cfg_min else None"),
("M03_move_no_reset",D,"draw.floor_kw, draw.floor_since = moved, 0","draw.floor_kw = moved"),
("M04_reconfig_keeps_floor",D,"self.floor_kw = self.floor_kw if self.config == configured else None","self.floor_kw = self.floor_kw"),
("M05_bandfields_top_only",C,'band.source == "configured" and band.min_source == "configured"','band.source == "configured"'),
("M06_applies_always",C,"applies_floor=levels_clamped(config)","applies_floor=True"),
("M07_no_top_clamp",D,"min(floor or cfg_min, top)","(floor or cfg_min)"),
("M08_stored_ge",D,"np.isfinite(floor) and floor > cfg_min","np.isfinite(floor) and floor >= cfg_min"),
("M09_evidence_no_start",D,"self._aligned()))[start:]","self._aligned()))[0:]"),
("M10_last_window",D,"last=draw.floor_since,","last=WINDOW,"),
("M11_since_unclamped",D,"self.floor_since = min(self.floor_since + 1, WINDOW)","self.floor_since = self.floor_since + 1"),
("M12_sensor_no_min",SN,'            **_pump_min_power(data.get("pump_max_power")),\n',""),
("M13_stored_nonfinite",D,"keep = floor is not None and np.isfinite(floor) and","keep = floor is not None and"),
("M14_fromdict_no_floor",D,"        out.floor_kw, out.floor_since = _stored_floor(data, lo, len(out.samples))\n",""),
("M15_asdict_no_since",D,'            "floor_since": self.floor_since,\n',""),
("M16_lower_hold_band",D,"if low is None or (1.0 - AGREE_TOLERANCE) * f <= low <= (1.0 + AGREE_TOLERANCE) * f:","if low is None or low <= (1.0 + AGREE_TOLERANCE) * f:"),
("M17_reason_cycled_books",D,'"metered" if reason == "measured" else "configured"','"metered" if reason in ("measured", "cycled") else "configured"'),
("M18_echo_ignored",D,"    if echo:\n        reason = \"plan_writes_power\"\n    elif floor is None:","    if False:\n        reason = \"plan_writes_power\"\n    elif floor is None:"),
]
blk="# -- R11-OUTSIDE-HONEST-METERED-FLOOR: the learned floor moves the plan"
pre=sys.argv[1]
only=sys.argv[2:] 
for name,f,old,new in M:
    if only and name not in only: continue
    src=open(f).read()
    if src.count(old)!=1: print(f"{name} BADPATTERN count={src.count(old)}"); continue
    open(f,"w").write(src.replace(old,new))
    try:
        r=subprocess.run([sys.executable,"tools/audit/seat/features_block.py","--prelude",f"exec(open('{pre}').read())",blk],capture_output=True,text=True,env={**os.environ,"PYTHONPATH":"tests/hastub"},timeout=600)
        fails=[l.strip()[:110] for l in r.stdout.splitlines() if l.strip().startswith(("FAIL","X ","!!"))]
        tail=r.stdout.strip().splitlines()[-1:] if r.stdout.strip() else r.stderr.strip().splitlines()[-1:]
        print(f"{name} {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} {tail}")
    finally:
        open(f,"w").write(src)
subprocess.run(["git","status","--short","custom_components"])
