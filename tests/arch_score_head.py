#!/usr/bin/env python3
"""The architecture score still measures today's tree (R9-EG-A1).

tests/arch_score.py measures a pinned tree and stored history, so it cannot notice the instrument
going blind on the tree it is run against: a coordinator renamed, a role the engine no longer finds, a
module the metrics cannot parse. This is that check, and it is the only part that reads the working tree
-- so it is its own script, and a change to the integration selects it and not the calibration.

  * every score metric and every tripwire is a number on this tree;
  * a tree compared with itself reads NULL, and the report names no metric;
  * the coordinator class the metrics key on is the one ``tests/structure.py`` keys on;
  * nothing the scheduled cycle or the what-if reaches writes the coordinator's three hubs,
    except the producers CYCLE_HUB_WRITERS names (#1736), the pre-solve steps included.

    PYTHONPATH=tests/hastub python3 tests/arch_score_head.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "audit"))

from harness import Results  # noqa: E402

from archscore import counters, score, vector  # noqa: E402
from archscore.metrics import common, footprint, hub_solve_writes  # noqa: E402

R = Results("architecture score on today's tree (R9-EG-A1)")

#: #1736: a solve plans from one record built on the loop, so every hub write
#: the scheduled cycle reaches (hub_solve_writes' roots: the cycle and the
#: what-if, R9-EG-A4) is a producer moving live state at the event that changed
#: it: a reading, a learner's adoption, the cycle's carried corrections. Keyed
#: writer -> (the hub fields it writes, why). A writer or a field outside this
#: table is a solve-scoped value written into shared state: #1736's class,
#: wherever in the cycle it sits -- #1887's round-1 review moved one into the
#: pre-solve step, which the solve-only roots did not reach.
_C = "coordinator:HeatPumpOptimizerCoordinator."
CYCLE_HUB_WRITERS = {
    _C + "_update_current_state": (
        {"_current_state." + f for f in (
            "buffer_tank_temperature", "dhw_hours_since_legionella", "dhw_temperature",
            "floor_return_temperature", "lower_floor_temperature", "outdoor_temperature",
            "room_temperature", "slab_temperature", "solar_radiation",
            "upper_floor_temperature", "wood_tank_temperature")}
        | {"_thermal_params.ambient_humidity", "_thermal_params.mixing_valve_target"},
        "this cycle's sensor readings into the live state"),
    "thermal_model:ThermalModel.update_slab_from_return_temp": (
        {"_current_state.floor_return_temperature", "_current_state.slab_temperature"},
        "the slab estimate advanced from this cycle's return reading"),
    "thermal_model:ThermalModel.update_ecl110_displace_state": (
        {"_current_state.ecl110_displace_command", "_current_state.ecl110_effective_displace"},
        "the ECL110 displacement state from this cycle's command"),
    _C + "_refresh_model_corrections": (
        {"_thermal_params." + f for f in (
            "dhw_inlet_current", "flow_curve_bias", "flow_curve_indoor_target",
            "internal_gains_profile", "solar_aperture_scale")},
        "the cycle's corrections carried on the live model after the learners (#1736)"),
    _C + "_apply_comfort_weight": (
        {"_opt_config.comfort_weight"},
        "the quiet-period learner in the solve's tail moved the learned weight"),
    _C + "_apply_house_heat_loss_scale": (
        {"_thermal_params.house_heat_loss_scale"},
        "a finished system identification adopts its fitted scale"),
    _C + "_apply_cop_scale": ({"_thermal_params.cop_scale"}, "the COP learner adopts its scale"),
    _C + "_apply_lower_floor_loss_ratio": (
        {"_thermal_params.lower_floor_loss_ratio"}, "the zone learner adopts its ratio"),
    _C + "_apply_buffer_cooling_rate": (
        {"_thermal_params.buffer_cooling_rate"}, "the buffer learner adopts its rate"),
    _C + "_apply_learner_payloads": (
        {"_thermal_params.defrost_derate"}, "a restored learner payload is adopted"),
    "dhw_learning:DhwProfileLearner.apply_cooling_rate": (
        {"_thermal_params.dhw_cooling_rate"}, "the DHW learner adopts its cooling rate"),
    "dhw_learning:DhwProfileLearner.apply_payload": (
        {"_thermal_params.dhw_hourly_draw_pattern"}, "a restored DHW profile is adopted"),
    "dhw_learning:DhwProfileLearner.async_learn_usage": (
        {"_thermal_params.dhw_hourly_draw_pattern"}, "the DHW learner adopts a learned draw profile"),
}
LISTED = {(w, f) for w, (fields, _why) in CYCLE_HUB_WRITERS.items() for f in fields}
#: The planted writes the controls add: one as async_run_optimization's first
#: statement, one as the pre-solve step's last (#1887's round-1 probe).
_PLANT_AT = '        ctx = getattr(self, "_ctx", self)\n        _LOGGER.info("Running heat pump optimization'
_PLANT = '        ctx._opt_config.peak_count = 3\n'
_PRESOLVE_AT = '        params.flow_curve_indoor_target = fresh["flow_curve_indoor_target"]\n'
_PRESOLVE = '        getattr(self, "_ctx", self)._opt_config.peak_count = 3\n'

#: #1776: the fragment-chain guard. ``params_over_10`` is a count, so a split
#: that decomposes nothing RAISES it (the pre-study's perturbation B3c), and a
#: keyword bag does not lower it (counter C11). The functions this group left
#: over the line are rows here, each with why; the ones the round converted
#: take the horizon, the weather series or a frozen record of their related
#: arrays instead of positional lists. A site the instrument returns that is
#: not a row is red, and a row the instrument no longer returns is red too --
#: the table shrinks only by a deliberate edit that says the function went
#: under. Keyed ``module.qualname``, never a line number.
PARAMS_OVER_10_LEFT = {
    "away.resolve":
        "the operating-mode resolver's five option groups, each keyword-only "
        "with its own default; a record would re-wrap the mode dict its "
        "callers already hold",
    "comfort_band._pair_violations":
        "two (key, default) quartets read out of the candidate and current "
        "option dicts; those dicts are the records, and a schedule record "
        "would name each key twice",
    "optimizer.HeatPumpOptimizer._build_result":
        "keyword-only already, and every optional is one published result "
        "field; the OptimizationResult it assembles IS the record",
    "tariff._peak_charge":
        "the capacity-charge scaffolding's shared core; the tariff-record "
        "family (peak_cost, peak_cost_smooth, peak_cost_batch, this) is the "
        "next family owed, outside this group's line cap",
    "tariff.peak_cost":
        "the published capacity charge; the tariff-record family is the next "
        "family owed, outside this group's line cap",
    "tariff.peak_cost_batch":
        "the batch twin; same family, same disposition",
    "tariff.peak_cost_smooth":
        "the solver's smooth surrogate; same family, same disposition",
    "thermal_model.ThermalModel._simulate_step_single":
        "the per-step hot path takes scalars; a frozen per-step record "
        "allocated one object per simulated step, and the sysid rollout was "
        "already priced out of its harness budget once by per-sub-step work",
    "thermal_model.ThermalModel._simulate_step_two_zone":
        "the two-zone step twin; same per-step path, same disposition",
    "thermal_model.ThermalModel.simulate_step":
        "the public per-step entry, 12 production and 27 test call sites; "
        "its step conditions travel as scalars into the two models above",
    "topology.rank_sensor_gaps":
        "a keyword-only scenario probe for the diagnostics estimate, every "
        "parameter an independent knob with a published default; a record "
        "would move those defaults into a second home",
    "wood_fuel.build_wood_fuel_view":
        "the wood-furnace card view; the series it reads are derived views, "
        "not the planner's positional arrays",
}

#: The seven planted parameters the control appends to hold_demand_kw's
#: signature (four plus seven crosses the line).
_PARAM_PLANT = "".join(
    f"    extra_unplanned_{i}: float | None = None,\n" for i in range(7))
_PARAM_PLANT_AT = "    solar_mean: float = 0.0,\n) -> float:"


def param_sites(root: Path) -> list[str]:
    """``module.qualname`` for every function the fragment-chain guard counts."""
    pkg = common.load(str(root))
    trees = {m.name: m.tree for m in pkg.mods.values() if "." not in m.name}
    return footprint.params_over_10_sites(trees)


def planted_param_site() -> tuple[bool, list[str]]:
    """The positive control: today's package with one parameter planted on
    ``hold_demand_kw``. ``(planted, sites)``."""
    with tempfile.TemporaryDirectory(prefix="archscore-params-") as tmp:
        root = Path(tmp)
        shutil.copytree(ROOT / counters.PKG, root / counters.PKG,
                        ignore=shutil.ignore_patterns("__pycache__"))
        opt = root / counters.PKG / "optimizer.py"
        text = opt.read_text()
        if _PARAM_PLANT_AT not in text:
            return False, []
        opt.write_text(text.replace(_PARAM_PLANT_AT,
                                    _PARAM_PLANT + _PARAM_PLANT_AT, 1))
        return True, param_sites(root)


def hub_writers(root: Path) -> set[tuple[str, str]]:
    """(writer, hub.field) for every hub write the solve roots reach in ``root``."""
    with tempfile.TemporaryDirectory(prefix="archscore-hubs-") as tmp:
        flat = Path(tmp)
        counters.flatten(root, flat, inline=True)
        pkg = common.load(str(flat))
        eng = common.engine(pkg)
        out: set[tuple[str, str]] = set()
        for r in hub_solve_writes.ROOTS:
            q = f"{common.COORD_MODULE}:{common.COORD_CLASS}.{r}"
            if q in pkg.funcs:
                out |= {(x[4], f"{x[2]}.{x[3]}") for x in hub_solve_writes._sites(eng, q)}
        return out


def planted_writers(at: str, cut_after: str, plant: str) -> tuple[bool, set[tuple[str, str]]]:
    """A positive control: today's package with ``plant`` inserted after
    ``cut_after``, the head of the one occurrence of ``at``. ``(planted, writers)``."""
    with tempfile.TemporaryDirectory(prefix="archscore-plant-") as tmp:
        root = Path(tmp)
        shutil.copytree(ROOT / counters.PKG, root / counters.PKG,
                        ignore=shutil.ignore_patterns("__pycache__"))
        coord = root / counters.PKG / "coordinator.py"
        text = coord.read_text()
        if text.count(at) != 1:
            return False, set()
        cut = text.find(at) + len(cut_after)
        coord.write_text(text[:cut] + plant + text[cut:])
        return True, hub_writers(root)


def main() -> int:
    here = vector.measure(ROOT)
    missing = [m for m in (*vector.SCORE_METRICS, *vector.GATE_ONLY) if not isinstance(here.get(m), int)]
    R.check("every score metric and tripwire measures on today's tree", not missing,
            f"no value for {missing}; errors {[v for k, v in here.items() if k.endswith('_error')]}")
    R.check("a tree against itself reads NULL", score.delta(here, here)["verdict"] == "NULL")
    R.check("a tree against itself reports no metric moved",
            score.report(here, here).count("\n") == 0, score.report(here, here))
    structure = vector.load_structure(ROOT)
    R.check("the metrics and tests/structure.py key on the same coordinator class",
            common.COORD_CLASS == structure.COORDINATOR_CLASS_NAME,
            f"{common.COORD_CLASS} vs {structure.COORDINATOR_CLASS_NAME}")
    trees = structure.module_trees()
    shared, adjacent = structure.duplicate_clones(trees), counters.gapped_clones(structure, trees, gap=0)
    R.check("the score's clone census with no gap is the ratchet's census (C3 only widens it)",
            adjacent == shared, f"{len(adjacent)} classes vs {len(shared)}")
    wide = counters.gapped_clones(structure, trees)
    R.check("...and with any gap it keeps every class the ratchet finds",
            all(any(set(g) <= set(w) for w in wide) for g in shared))
    writers = hub_writers(ROOT)
    R.check("nothing the scheduled cycle reaches writes a hub but its listed producers (#1736)",
            writers <= LISTED,
            f"unlisted: {sorted(writers - LISTED)}: put the value in the solve's record, or "
            "list the producer with the event that moves it")
    for name, (at, cut_after, plant, writer) in {
        "at the top of the solve": (_PLANT_AT, '        ctx = getattr(self, "_ctx", self)\n', _PLANT,
                                    _C + "async_run_optimization"),
        "in the pre-solve step": (_PRESOLVE_AT, _PRESOLVE_AT, _PRESOLVE, _C + "_refresh_model_corrections"),
    }.items():
        planted, seen = planted_writers(at, cut_after, plant)
        R.check(f"the hub check refuses a write planted {name}, and lists only it",
                planted and seen - LISTED == {(writer, "_opt_config.peak_count")},
                f"planted={planted}; unlisted {sorted(seen - LISTED)}")
    R.check("every listed producer is still reached, so the table holds no stale row",
            LISTED <= writers, f"stale: {sorted(LISTED - writers)}")
    sites = param_sites(ROOT)
    R.check("the head census does not out-count the score's own guard (C4 can only add copies)",
            len(sites) <= here["params_over_10"],
            f"census {len(sites)} vs guard {here['params_over_10']}")
    R.check("every function over ten parameters is a dispositioned row (#1776)",
            set(sites) <= set(PARAMS_OVER_10_LEFT),
            f"unlisted: {sorted(set(sites) - set(PARAMS_OVER_10_LEFT))}: take the horizon, "
            "the weather series or a frozen record of the related arrays, or row the "
            "function here with why it stays over the line")
    R.check("every dispositioned row is still over the line, so the table holds no stale row",
            set(PARAMS_OVER_10_LEFT) <= set(sites),
            f"stale: {sorted(set(PARAMS_OVER_10_LEFT) - set(sites))}: drop the row -- the "
            "function went under the line")
    R.check("the guard's round target holds: no more than 14 over the line",
            len(sites) <= 14, f"{len(sites)} sites")
    planted, psites = planted_param_site()
    R.check("the guard refuses a parameter planted on a four-parameter function, and lists only it",
            planted and psites and sorted(set(psites) - set(sites)) == ["optimizer.hold_demand_kw"],
            f"planted={planted}; new {sorted(set(psites) - set(sites))}")
    return R.close("ARCHITECTURE SCORE HEAD CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
