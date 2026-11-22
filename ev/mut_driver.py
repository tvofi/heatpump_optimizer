import subprocess, sys, pathlib
S = sys.argv[1]
import os
START = os.environ.get("MSTART", "# Cooling is the user's season (``pump_arbiter.cooling_mode``)")
END = os.environ.get("MEND", "from heatpump_optimizer import duty_switch as _ds_mod")
P = "custom_components/heatpump_optimizer/"
MUTANTS = [
 ("supply_write cooling term dropped", "supply_hold.py", "if note_cooling(held, inp, signals, on) is None and", "if (note_cooling(held, inp, signals, on) is None or True) and"),
 ("cooling_mode always None", "pump_arbiter.py", "    return mode if mode.cooling else None", "    return None"),
 ("cooling_mode live arm dropped", "pump_arbiter.py", "    mode = live if live.cooling else getattr(signals, \"mode\", live)", "    mode = getattr(signals, \"mode\", live)"),
 ("cooling_mode signals arm dropped", "pump_arbiter.py", "    mode = live if live.cooling else getattr(signals, \"mode\", live)", "    mode = live"),
 ("note_cooling never clears", "supply_hold.py", "        issues.clear_issue(inp.hass, ISSUE_COOLING)", "        pass"),
 ("note_cooling once-guard dropped", "supply_hold.py", "asks_heat and not held.cooling_asked:", "asks_heat:"),
 ("note_cooling asks_heat ignored", "supply_hold.py", "elif mode is not None and asks_heat and", "elif mode is not None and"),
 ("coordinator per-cycle note_cooling dropped", "coordinator.py", "        supply_hold.note_cooling(pump_arbiter.state_for(self), self.arbiter_inputs(), self._pump_signals)  # clears once cooling is left", "        pass"),
 ("early_cutoff cooling exemption dropped", "early_cutoff.py", "    if cooling_mode(inp):  # the switch", "    if False:  # the switch"),
 ("desired cooling guard dropped", "pump_arbiter.py", "    if cooling_mode(inp):  # hands off, the silent switch included", "    if False:"),
 ("_mode_for cooling term dropped", "pump_arbiter.py", "    if duty == \"idle\" or cooling_mode(inp):", "    if duty == \"idle\":"),
 ("blocked-both OFF skip dropped", "supply_hold.py", "(on or not (signals.space_blocked and signals.dhw_blocked))", "(on or True)"),
]
def run():
    r = subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--prelude", f"exec(open('{os.environ.get("MPRE", S + "/prelude.py")}').read())", START, END], capture_output=True, text=True, timeout=200)
    out = r.stdout + r.stderr
    last = [l for l in out.splitlines() if "FEATURES BLOCK" in l]
    first = next((l.strip() for l in out.splitlines() if l.strip().startswith("FAIL")), "")
    return r.returncode, (last[-1] if last else out[-300:]), first
only = sys.argv[2:] 
for name, f, old, new in MUTANTS:
    if only and name not in only: continue
    p = pathlib.Path(P + f); src = p.read_text()
    n = src.count(old)
    if n != 1:
        print(f"MUTANT {name}: anchor count {n} -- not applied"); continue
    p.write_text(src.replace(old, new))
    try:
        rc, summary, first = run()
    finally:
        p.write_text(src)
    print(f"MUTANT {name}: rc={rc} {summary} | first: {first}", flush=True)
d = subprocess.run(["git", "diff", "--quiet", "--", "custom_components"]).returncode
print("restored: production files equal HEAD" if d == 0 else "RESTORE FAILED")
