import subprocess, sys, pathlib, json
W = pathlib.Path(sys.argv[1]); S = pathlib.Path("/Users/timmalmstrom/hpo-seats/r10s6/rev-3869-scratch")
CC = "custom_components/heatpump_optimizer/"
M = [
 ("M01 R1 short never", "duty_legs.py", "short = two & (dhw_run < dhw_min)", "short = two & False"),
 ("M02 keep -> 0", "duty_switch.py", "keep = rule.dhw_min if current == \"dhw\" else rule.heat_min if previous == pump_mode.MODE_DHW else 0.0", "keep = 0.0"),
 ("M03 keep heat regardless of previous", "duty_switch.py", "rule.heat_min if previous == pump_mode.MODE_DHW else 0.0", "rule.heat_min"),
 ("M04 need branch off", "duty_switch.py", "or (need > 0 and _kept_minutes(legs, start, now, wanted) < need)", "or False"),
 ("M05 kept_minutes past end -> 0", "duty_switch.py", "        at += minutes\n    return math.inf", "        at += minutes\n    return 0.0"),
 ("M06 idle does not continue", "duty_switch.py", "leg not in (duty, \"idle\")", "leg != duty"),
 ("M07 solve_before not stored", "duty_switch.py", "        rec.solve_before = before\n", "        pass\n"),
 ("M08 leg_minimum no clamp", "duty_legs.py", "min(max(value, 0.0), LEG_MIN_MAX_MINUTES)", "value"),
 ("M09 sandwich left any", "duty_legs.py", "(left[..., s_slot] == DHW) & ", ""),
 ("M10 sandwich right any", "duty_legs.py", " & (right[..., s_slot] == DHW)", ""),
 ("M11 no whole on short", "duty_legs.py", "whole = (short & (step_minutes - longer < SPLIT_MIN_MINUTES)) | sandwich", "whole = sandwich"),
 ("M12 before ignored in ffill", "duty_legs.py", "np.maximum(known, 0), axis=-1), before)", "np.maximum(known, 0), axis=-1), IDLE)"),
 ("M13 re-send restarts leg", "duty_switch.py", "if rec.leg is None or rec.leg[0] != new:", "if True:"),
 ("M14 share only both", "pump_arbiter.py", "if (i is None or inp.mode", "if (i is None or duty != \"both\" or inp.mode"),
 ("M15 share block exemption off", "pump_arbiter.py", " or held.block_active(c, now)", ""),
 ("M16 availability moved zero", "duty_legs.py", "    charged = two & (first == DHW)\n", "    moved = moved * 0\n    charged = two & (first == DHW)\n"),
 ("M17 kept current==wanted guard off", "duty_switch.py", "current is None or current == wanted", "current is None"),
 ("M18 age stamp-ahead", "duty_switch.py", "if 0.0 <= age_min < keep", "if age_min < keep"),
 ("M19 fixed point range(1)", "duty_legs.py", "for _ in range(2 * first.shape[-1] + 1):", "for _ in range(1):"),
 ("M20 run inf deleted", "duty_legs.py", "    run = np.where((s_idx == 0) & (codes == before), math.inf, run)\n", ""),
 ("M21 rule ignores cfg dhw_min", "duty_switch.py", "dhw_min=duty_legs.leg_minimum(cfg.mode_leg_dhw_min_minutes)", "dhw_min=0.0"),
 ("M22 rule ignores cfg heat_min", "duty_switch.py", "heat_min=duty_legs.leg_minimum(cfg.mode_leg_heat_min_minutes)", "heat_min=0.0"),
 ("M23 order latch ignored", "duty_switch.py", "        legs = (*legs[:i], rec.order[1], *legs[i + 1:])\n", "        pass\n"),
 ("M24 lengthen dropped", "duty_legs.py", "stretched = np.where(lengthen, longer if lead_dhw else step_minutes - longer, first_min)", "stretched = first_min"),
]
mode = sys.argv[2]
blocks = {
 "ds": ("from heatpump_optimizer import duty_switch as _ds_mod", "# --- R10-CEILING-PROBE (#2498", S/"prelude_ds.py"),
 "ml": ("# --- R11-OWNER-MODE-LEGS (#3859)", "# --- R10-CEILING-PROBE (#2498", S/"prelude_ml.py"),
 "dsp": ("import heatpump_optimizer.optimizer as _dsp_om", "# --- #3616: an implausible slab", S/"prelude_dsp.py"),
}
st, en, pre = blocks[mode]
sel = sys.argv[3].split(",") if len(sys.argv) > 3 else None
for name, f, old, new in M:
    if sel and name.split()[0] not in sel: continue
    p = W/CC/f; src = p.read_text()
    if src.count(old) != 1:
        print(f"{name}: NOT-APPLIED (count {src.count(old)})", flush=True); continue
    p.write_text(src.replace(old, new))
    try:
        r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f"exec(open('{pre}').read())", st, en],
                           cwd=W, capture_output=True, text=True, timeout=900)
        out = r.stdout + r.stderr
        fails = [l.strip()[:110] for l in out.splitlines() if l.lstrip().startswith("FAIL")]
        tail = out.strip().splitlines()[-1][:120] if out.strip() else ""
        verdict = "KILLED" if r.returncode != 0 else "SURVIVED"
        print(f"{name}: {verdict} rc={r.returncode} fails={len(fails)} | {tail}", flush=True)
        for l in fails[:4]: print("    ", l, flush=True)
    finally:
        p.write_text(src)
