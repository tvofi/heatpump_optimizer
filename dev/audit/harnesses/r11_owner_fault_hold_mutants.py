#!/usr/bin/env python3
"""R11-OWNER-FAULT-HOLD (#3856): the mutation proof, one production predicate at a time.

Each mutant deletes or weakens one line of the fault hold (``fault_hold.py``,
its consults in ``pump_arbiter.py``, ``duty_ledger.py``, ``heat_curve.py``,
``early_cutoff.py`` and ``coordinator.py``) in a ``git archive`` copy of the
tree at REF, then runs the fault-hold block of ``tests/features.py`` (through
``tools/audit/seat/features_block.py``, its prelude emitted in the copy) and
``tests/block_duty.py``. Printed per mutant: KILLED with the failing check
names, or SURVIVED. The baseline line is the unmutated copy: 0 failing, or
the run measures nothing. A mutant whose text no longer matches exactly once
exits 2 rather than run a vacuous mutant.

Command (repository root):
    python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py [REF]   # REF: HEAD
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

P = "custom_components/heatpump_optimizer/"
START = 'R.section("R11-OWNER-FAULT-HOLD'
END = 'R.section("duty-switch restart learning, part A'
M = [
 ("hold-after comparison", "fault_hold.py", "latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER", "latch.since is not None and now - latch.since > FAULT_HOLD_AFTER"),
 ("hold-after dropped", "fault_hold.py", "latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER", "latch.since is not None"),
 ("unbounded read", "fault_hold.py", "read_bool(CONF_HEAT_PUMP_FAULT_ENTITY, max_age_minutes=UNBOUNDED)", "read_bool(CONF_HEAT_PUMP_FAULT_ENTITY)"),
 ("legible-off reset", "fault_hold.py", "    if reading.flag is False and reading.ok:\n        latch.since = None\n", "    if reading.flag is False and reading.ok:\n        pass\n"),
 ("unusable resets", "fault_hold.py", "    if reading.flag is False and reading.ok:", "    if not (reading.flag and reading.ok):"),
 ("unusable starts", "fault_hold.py", "    elif reading.flag and reading.ok and latch.since is None:", "    elif latch.since is None:"),
 ("since bounded to now", "fault_hold.py", "min(dt_util.as_utc(changed), now)", "dt_util.as_utc(changed)"),
 ("released guard", "fault_hold.py", "    if released:\n        return False\n", ""),
 ("opt-out", "fault_hold.py", "if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:", "if off or not cfg.heat_pump_fault_entity:"),
 ("off clears", "fault_hold.py", "if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:", "if not cfg.fault_hold or not cfg.heat_pump_fault_entity:"),
 ("rising-edge repair", "fault_hold.py", "        issues.set_issue(hass, ISSUE, True,", "        (lambda *a, **k: None)(hass, ISSUE, True,"),
 ("falling-edge clear", "fault_hold.py", "        latch.holding = False\n        _clear(hass)\n", "        latch.holding = False\n"),
 ("same-hass filter", "fault_hold.py", "other.holding and other.hass is hass", "other.holding"),
 ("gate False-only", "fault_hold.py", "    if value is not False or not consult(entry, inp):", "    if value is None or not consult(entry, inp):"),
 ("gate held mark", "fault_hold.py", "    held_state.supply_held = True\n", ""),
 ("release clears", "fault_hold.py", "    if was:\n        _clear(hass)\n", ""),
 ("apply consult", "pump_arbiter.py", "faulted = fault_hold.consult(coord.entry, inp, now)", "faulted = False"),
 ("_arbitrate return", "pump_arbiter.py", " or _fault_stands(inp.hass, held, faulted):", ":"),
 ("retry drop", "pump_arbiter.py", "        held.retry.clear()\n", ""),
 ("ignored-issue clear", "pump_arbiter.py", "        issues.clear_issue(hass, ISSUE_IGNORED)\n    return faulted", "    return faulted"),
 ("space_before drop", "pump_arbiter.py", "    if faulted:\n        held.space_before = None\n", "    if faulted:\n"),
 ("_lead_mode skip", "pump_arbiter.py", " or fault_hold.held(coord.entry):\n            return\n        duty = _step_duty", ":\n            return\n        duty = _step_duty"),
 ("release row skip", "pump_arbiter.py", " and inp.mode != MODE_OFF and not faulted:", " and inp.mode != MODE_OFF:"),
 ("ledger faulted mark", "pump_arbiter.py", "start_below=_dhw_start_below_c(inp), faulted=faulted)", "start_below=_dhw_start_below_c(inp))"),
 ("verdict fault-first", "duty_ledger.py", '    if row.get("faulted"):', '    if False:'),
 ("observe keeps faulted", "duty_ledger.py", 'row["faulted"] = row["faulted"] or faulted', 'row["faulted"] = faulted'),
 ("diagnostics row", "diagnostics.py", '    ("fault_hold", lambda c: fault_hold.diagnostics_view(c.entry)),\n', ''),
 ("publish return", "heat_curve.py", "    if fault_hold.holding(entry, hass, config, off=mode_off, released=released):\n        return\n", ""),
 ("cut-off consult", "early_cutoff.py", "    if fault_hold.consult(wiring.entry, inp, now):", "    if False:"),
 ("frequency guard", "coordinator.py", " or self._mode == MODE_OFF or fault_hold.held(self.entry):", " or self._mode == MODE_OFF:"),
 ("switch gate wired", "coordinator.py", "value = fault_hold.gate(self.entry, held, self.arbiter_inputs(), supply_hold.hold_supply(", "value = (lambda *a: a[3])(self.entry, held, self.arbiter_inputs(), supply_hold.hold_supply("),
 ("cut-off entry wired", "coordinator.py", "self.entry.async_on_unload, entry=self.entry)", "self.entry.async_on_unload)"),
]


def run(copy: str, prelude: str) -> list[str]:
    env = {**os.environ, "PYTHONPATH": "tests/hastub"}
    out: list[str] = []
    for cmd in ([sys.executable, "tools/audit/seat/features_block.py", "--prelude",
                 f"exec(open({prelude!r}).read())", START, END],
                [sys.executable, "tests/block_duty.py"]):
        r = subprocess.run(cmd, cwd=copy, capture_output=True, text=True, env=env, timeout=1500)
        txt = r.stdout + r.stderr
        fails = [line.strip()[5:] for line in txt.splitlines() if line.strip().startswith("FAIL ")]
        if not fails and r.returncode != 0:
            fails = ["CRASH " + (txt.strip().splitlines() or ["no output"])[-1]]
        out += fails
    return out


def main(argv: list[str]) -> int:
    ref = argv[0] if argv else "HEAD"
    with tempfile.TemporaryDirectory() as copy:
        archive = subprocess.run(["git", "archive", ref, "custom_components", "tests", "tools"],
                                 capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", copy], input=archive, check=True)
        prelude = os.path.join(copy, "fh_prelude.py")
        subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--emit-prelude", prelude, START, END],
                       cwd=copy, capture_output=True, check=True, env={**os.environ, "PYTHONPATH": "tests/hastub"})
        base = run(copy, prelude)
        print(f"BASELINE {len(base)} failing")
        for b in base:
            print(f"    - {b[:150]}")
        survived = 0
        for name, f, old, new in M:
            path = os.path.join(copy, P + f)
            src = open(path, encoding="utf-8").read()
            if src.count(old) != 1:
                print(f"STALE {name} ({f}): the mutant's text is not on this tree once")
                return 2
            open(path, "w", encoding="utf-8").write(src.replace(old, new))
            try:
                fails = run(copy, prelude)
            finally:
                open(path, "w", encoding="utf-8").write(src)
            survived += not fails
            print(f"{'KILLED' if fails else 'SURVIVED'} {name} ({f}): {len(fails)} failing")
            for x in fails[:4]:
                print(f"    - {x[:150]}")
        print(f"RESULT mutants={len(M)}")
        print(f"RESULT survived={survived}")
    return 0 if survived == 0 and not base else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
