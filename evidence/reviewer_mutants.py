"""Reviewer's own mutants for PR #3872, driven by the fixer's harness runner (same block + block_duty)."""
import importlib.util, os, subprocess, sys, tempfile
spec = importlib.util.spec_from_file_location("h", "dev/audit/harnesses/r11_owner_fault_hold_mutants.py")
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
P = h.P
M = [
 ("falling edge keeps holding before clear", "fault_hold.py", "        latch.holding = False\n        _clear(hass)\n", "        _clear(hass)\n"),
 ("latch entity/hass not recorded", "fault_hold.py", "    latch.entity, latch.hass = reading.entity_id, hass\n", ""),
 ("since ignores last_changed", "fault_hold.py", "latch.since = min(dt_util.as_utc(changed), now) if changed is not None else now", "latch.since = now"),
 ("consult ignores Off", "fault_hold.py", "off=inp.mode == MODE_OFF, released=inp.entry_released", "off=False, released=inp.entry_released"),
 ("consult ignores released", "fault_hold.py", "off=inp.mode == MODE_OFF, released=inp.entry_released", "off=inp.mode == MODE_OFF"),
 ("gate never consults (held only)", "fault_hold.py", "    if value is not False or not consult(entry, inp):", "    if value is not False or not held(entry):"),
 ("release does not pop", "fault_hold.py", "    latch = _STATES.pop(entry, None)", "    latch = _STATES.get(entry)"),
 ("diagnostics since dropped", "fault_hold.py", '"since": latch.since.isoformat() if latch.since else None', '"since": None'),
 ("publish ignores mode_off", "heat_curve.py", "fault_hold.holding(entry, hass, config, off=mode_off, released=released)", "fault_hold.holding(entry, hass, config, off=False, released=released)"),
 ("publish ignores released", "heat_curve.py", "fault_hold.holding(entry, hass, config, off=mode_off, released=released)", "fault_hold.holding(entry, hass, config, off=mode_off)"),
 ("consult after duty-off return", "pump_arbiter.py", "    faulted = fault_hold.consult(coord.entry, inp, now)  # every install, duty off too\n    mode = duty_mode(inp.config)\n    if mode == DUTY_OFF:\n        release_listeners(coord)\n        return\n", "    mode = duty_mode(inp.config)\n    if mode == DUTY_OFF:\n        release_listeners(coord)\n        return\n    faulted = fault_hold.consult(coord.entry, inp, now)\n"),
 ("fault_stands not dropping space_before only when faulted", "pump_arbiter.py", "    if faulted:\n        held.space_before = None\n        held.retry.clear()\n", "    held.space_before = None\n    if faulted:\n        held.retry.clear()\n"),
 ("cutoff last_held mark", "early_cutoff.py", '        held.last_held = "fault"\n', ''),
 ("ledger faulted reset per pass", "duty_ledger.py", '"dhw_mode": False, "faulted": False}', '"dhw_mode": False, "faulted": faulted}'),
]
def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    with tempfile.TemporaryDirectory() as copy:
        a = subprocess.run(["git", "archive", ref, "custom_components", "tests", "tools"], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", copy], input=a, check=True)
        prelude = os.path.join(copy, "fh_prelude.py")
        subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--emit-prelude", prelude, h.START, h.END], cwd=copy, capture_output=True, check=True, env={**os.environ, "PYTHONPATH": "tests/hastub"})
        base = h.run(copy, prelude); print(f"BASELINE {len(base)} failing", flush=True)
        surv = 0
        for name, f, old, new in M:
            path = os.path.join(copy, P + f); src = open(path).read()
            if src.count(old) != 1:
                print(f"STALE {name}", flush=True); continue
            open(path, "w").write(src.replace(old, new))
            try: fails = h.run(copy, prelude)
            finally: open(path, "w").write(src)
            surv += not fails
            print(f"{'KILLED' if fails else 'SURVIVED'} {name} ({f}): {len(fails)} failing", flush=True)
            for x in fails[:3]: print("    - " + x[:150], flush=True)
        print(f"RESULT mutants={len(M)}\nRESULT survived={surv}")
main()
