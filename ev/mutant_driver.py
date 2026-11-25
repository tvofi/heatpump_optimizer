import subprocess, sys, pathlib
W = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else "/root/wt"); S = pathlib.Path("/root/scr")
CC = "custom_components/heatpump_optimizer/"
# Mutants on the lines the main-merge resolution (c0a750fa6e) and its repair (ec6be8dbdf) wrote.
M = [
 ("R1 leg_rule off-time reads unmasked stop (branch side)", "duty_legs.py",
  "(off_seconds[into] / 60.0 if stops[into] else None)", "(off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)"),
 ("R2 leg_rule ignores unlatched mask", "duty_legs.py",
  "stops = [p > 0 and not free for p, free in zip(stop_probability, unlatched)]", "stops = [p > 0 for p in stop_probability]"),
 ("R3 planner _leg_rule mask -> latched", "optimizer.py",
  "opt.config.duty_switch_unlatched, opt.config.mode_leg_heat_min_minutes,", "(False, False), opt.config.mode_leg_heat_min_minutes,"),
 ("R4 _fields drops learner fields (mask/pairs)", "duty_switch.py",
  "return {**fields, \"mode_leg_heat_min_minutes\"", "return {\"mode_leg_heat_min_minutes\""),
 ("R5 leg_rule heat_min dropped", "duty_legs.py",
  "leg_minimum(heat_min), leg_minimum(dhw_min), before)", "0.0, leg_minimum(dhw_min), before)"),
 ("R6 leg_rule before dropped", "duty_legs.py",
  "leg_minimum(heat_min), leg_minimum(dhw_min), before)", "leg_minimum(heat_min), leg_minimum(dhw_min), IDLE)"),
 ("R7 split ignores unlatched (arbiter side)", "duty_switch.py",
  "return duty_legs.leg_rule(*self.planner_pairs(), self.unlatched())", "return duty_legs.leg_rule(*self.planner_pairs())"),
 ("R8 planner _leg_rule stops unpriced", "optimizer.py",
  "_priced_stops(opt) or (0.0, 0.0), duty_legs.priced_pair(opt.config.duty_switch_off_seconds),\n        opt.config.duty_switch_unlatched, opt.config.mode_leg_heat_min",
  "(0.0, 0.0), duty_legs.priced_pair(opt.config.duty_switch_off_seconds),\n        opt.config.duty_switch_unlatched, opt.config.mode_leg_heat_min"),
]
blocks = {
 "ml": ("# --- R11-OWNER-MODE-LEGS (#3859)", "# --- R10-CEILING-PROBE (#2498", S/"prelude_ml.py"),
 "dsp": ("import heatpump_optimizer.optimizer as _dsp_om", "# --- #3616: an implausible slab", S/"prelude_dsp.py"),
}
mode = sys.argv[1]
st, en, pre = blocks[mode]
sel = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] != "ALL" else None
def run():
    r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f"exec(open('{pre}').read())", st, en],
                       cwd=W, capture_output=True, text=True, timeout=1500)
    return r
if sel == ["BASE"]:
    r = run(); out = (r.stdout + r.stderr).strip().splitlines()
    print(f"BASE {mode}: rc={r.returncode} | {out[-1][:140] if out else ''}", flush=True); sys.exit(0)
for name, f, old, new in M:
    if sel and name.split()[0] not in sel: continue
    p = W/CC/f; src = p.read_text()
    if src.count(old) != 1:
        print(f"{name}: NOT-APPLIED (count {src.count(old)})", flush=True); continue
    p.write_text(src.replace(old, new))
    try:
        r = run(); out = r.stdout + r.stderr
        fails = [l.strip()[:150] for l in out.splitlines() if l.lstrip().startswith("FAIL")]
        tail = out.strip().splitlines()[-1][:140] if out.strip() else ""
        print(f"{name} [{mode}]: {'KILLED' if r.returncode else 'SURVIVED'} rc={r.returncode} fails={len(fails)} | {tail}", flush=True)
        for l in fails[:4]: print("    ", l, flush=True)
    finally:
        p.write_text(src)
