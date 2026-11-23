#!/usr/bin/env python3
"""Run a round-11 D16-s2 finder script on its rig, ported to the step tail where the tree has one.

WHY IT EXISTS. `dev/audit/rounds/round11/D16/s2/rig.py` re-implements the cycle's write tail and the
one-minute tick by name: the cycle calls `_apply_action`, `_command_frequency` and `_async_drive_pumps`,
the solve's valve write follows the adoption, and the tick builds a `SupplyWiring` of three fields.
R11-SEAM-actuation-writes folds those into one tail (`_async_step_tail`, run under the arbiter's
`tail_lock` by the cycle and by the tick), moves the publish out of `_apply_action` into it, cuts the
action through `_cut_action` and gives the tick its wiring through `_supply_wiring`. On that tree the
rig as written skips the publish and the tick's step half, so its stale shares read the rig, not the
tree. This launcher loads the finder's rig and, only where the coordinator has `_async_step_tail`,
replaces its adoption, cycle tail and tick with production's own calls; at a tree without it (the base)
the rig runs unchanged, so one command measures both ends. The finder's scripts are not edited:
they `import rig`, which resolves to the module placed in `sys.modules` here.

    PYTHONPATH=tests/hastub:. python3 dev/audit/harnesses/r11_d16_s2_ported.py <script.py> [args...]

e.g. `... r11_d16_s2_ported.py dev/audit/rounds/round11/D16/s2/timing.py`. Prints `PORTED rig: step tail`
or `PORTED rig: unchanged (no step tail)` first, then the script's own output. `--no-switch` (before the
script) drops `heat_pump_switch_entity` from the rig's configuration: the install with no supply switch,
on which the step half must still run and the switch is never written.
"""
from __future__ import annotations

import os
import runpy
import sys

RIG_DIR = os.path.join("dev", "audit", "rounds", "round11", "D16", "s2")


def _port(rig):
    from homeassistant.util import dt as dt_util

    from heatpump_optimizer import coordinator as co_mod, pump_arbiter
    from heatpump_optimizer.optimizer import HeatPumpOptimizer
    from heatpump_optimizer.thermal_model import ThermalModel

    if not hasattr(co_mod.HeatPumpOptimizerCoordinator, "_async_step_tail"):
        return "unchanged (no step tail)"

    def adopt(self, result):
        c = self.coord
        c._optimization_result = result
        c._last_optimization = dt_util.now()
        c._cut_by = HeatPumpOptimizer(ThermalModel(c._ctx._thermal_params), c._ctx._opt_config)
        c._cut_action()

    async def _cycle_writes(self):
        c = self.coord
        c._overlay_boost()
        await c._apply_action()
        async with pump_arbiter.state_for(c).tail_lock:
            await c._async_step_tail()

    def cycle(self, result=None, write_delay_s=0):
        self.run(self.coord._update_current_state())
        if result is not None:
            self.adopt(result)
        if write_delay_s:
            self.at(self.now + rig.timedelta(seconds=write_delay_s))
        self.run(self._cycle_writes())

    def tick(self):
        c = self.coord
        self.run(pump_arbiter.apply(c, dt_util.now()))
        held = pump_arbiter.state_for(c)
        if held.supply is not None:  # armed by the cycle's note_supply, as production arms it
            self.run(pump_arbiter.supply_tick(held, c._supply_wiring(), dt_util.now()))

    rig.Sim.adopt, rig.Sim._cycle_writes, rig.Sim.cycle, rig.Sim.tick = adopt, _cycle_writes, cycle, tick
    return "step tail"


def _no_switch(rig):
    config = rig.config

    def without(**extra):
        cfg = config(**extra)
        cfg.pop("heat_pump_switch_entity", None)
        return cfg

    rig.config = without


def main():
    argv = sys.argv[1:]
    no_switch = argv[:1] == ["--no-switch"]
    script, args = argv[no_switch], argv[no_switch + 1:]
    sys.path.insert(0, os.path.abspath(RIG_DIR))
    import rig  # noqa: E402  the finder's rig, which imports the package itself

    if no_switch:
        _no_switch(rig)
    print(f"PORTED rig: {_port(rig)}{' (no switch)' if no_switch else ''}", flush=True)
    sys.argv = [script, *args]
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
