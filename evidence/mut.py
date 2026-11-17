import subprocess, sys, os, shutil, tempfile
R = os.path.expanduser("~/wt"); S = os.path.expanduser("~/scratch")
rp = "custom_components/heatpump_optimizer/rooms.py"; cp = "custom_components/heatpump_optimizer/coordinator.py"
M = [
 ("M1 hvac-mode filter off", rp, "and r.hvac_mode in TARGET_COUNTS_IN", "and True"),
 ("M2 deadband 0", rp, "ROOM_LIFT_DEADBAND_C = 0.2", "ROOM_LIFT_DEADBAND_C = 0.0"),
 ("M3 per-step holiday band", rp, "0.0 if holiday else target_c - floor_c", "target_c - floor_c"),
 ("M4 start holiday gate", rp, '"holiday" if holiday', '"holiday" if False'),
 ("M5 no house shortfall", rp, "worst[0] - (target_c - house_c)", "worst[0]"),
 ("M6 ramp ignores base margin", rp, "max(held.anchor_c - float(margins[0]), 0.0)", "max(held.anchor_c, 0.0)"),
 ("M7 band ignores base", rp, "    ]) - margins\n", "    ])\n"),
 ("M8 window gate", cp, "open_window=self._vent_cusum.tripped", "open_window=False"),
 ("M9 pin gate", cp, "manual_pin=space_pins is not None", "manual_pin=False"),
 ("M10 two-zone gate", cp, "two_zone=params.two_zone_enabled", "two_zone=False"),
 ("M11 whatif lift", cp, "rooms.lifted(rooms.lift_of(self), self._confidence", "rooms.lifted(None, self._confidence"),
 ("M12 cap 2.0", rp, "ROOM_LIFT_CAP_C = 1.0", "ROOM_LIFT_CAP_C = 2.0"),
 ("M13 ramp 0.5", rp, "ROOM_LIFT_RAMP_C_PER_H = 0.25", "ROOM_LIFT_RAMP_C_PER_H = 0.5"),
 ("M14 quorum", rp, 'else "quorum" if summarize(readings) is None', 'else "quorum" if False'),
 ("M15 identity return", rp, "return margins + lift if lift.any() else base", "return margins + lift"),
 ("M16 away gate", cp, "away=self._away_state.active", "away=False"),
 ("M17 band at start only", rp, "(_comfort_at(config, t) for t in steps)", "(_comfort_at(config, start_time) for t in steps)"),
 ("M18 anchor 0", rp, "HeldLift(lift_c, worst[1], None, house_c - floor_c)", "HeldLift(lift_c, worst[1], None, 0.0)"),
 ("M19 economy gate", cp, "economy=self._mode == MODE_ECONOMY", "economy=False"),
 ("M20 house_unknown", rp, 'None if math.isfinite(house_c) else "house_unknown"', 'None'),
]
only = sys.argv[1:]
for name, path, old, new in M:
    if only and name.split()[0] not in only: continue
    d = tempfile.mkdtemp(dir=S)
    subprocess.run(f"git -C {R} archive HEAD | tar -x -C {d}", shell=True, check=True)
    f = os.path.join(d, path); src = open(f).read()
    n = src.count(old)
    if n != 1: print(f"{name}: SKIP count={n}", flush=True); shutil.rmtree(d); continue
    open(f, "w").write(src.replace(old, new))
    p = subprocess.run([f"{S}/block.sh", d], capture_output=True, text=True)
    out = p.stdout + p.stderr
    fails = [l.strip()[:140] for l in out.splitlines() if l.lstrip().startswith("FAIL") or "Error" in l][:3]
    print(f"{name}: rc={p.returncode} {'KILLED' if p.returncode else 'SURVIVED'} {fails}", flush=True)
    shutil.rmtree(d)
