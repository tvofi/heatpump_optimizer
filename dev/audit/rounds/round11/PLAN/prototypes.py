#!/usr/bin/env python3
"""Round 11 plan (P3): the architecture-score reading of each planned move's prototype edit.

Metric (one line): score.py:report(vector(fork tree), vector(fork tree + arm)), every counter on
(ARCHSCORE_ABLATE is refused). KEY: the vector vector.py:measure returns for the edited copy.

Each arm is an exact-text edit of a temporary copy of the package at the fork; the tree under test is
never written. An arm proves what the score reads for the move's shape, nothing about behaviour: the
fixer's failing test, mutation proof and the finder's harness are still owed (fixer.md).

  hub     coordinator._apply_comfort_weight publishes a replaced context instead of writing the shared
          OptimizationConfig in place (D7-s2-03's perturbation as a text edit)            ADR-003
  sysid   sysid.arm_from_config hands the switch to arm() instead of storing it on the collaborator's
          config each cycle                                                                ADR-003
  circ    the circulation pumps' write and its record move to one owner object; the coordinator's
          dict and its in-place store go (D16-s3-02's owner)                               ADR-004
  reach   boost reads the mode it was already told; diagnostics reads it from the #1739 view ADR-005
  tasks   async_shutdown stops clearing the task set its done-callbacks already empty: the control for
          ADR-005's withdrawn part 3 (one counted statement goes, the set's other writers stay)  ADR-005
  clock   InputReader takes UTC from the standard library, not a function-scope Home Assistant import
                                                                                           ADR-002
  topk    tariff._smooth_topk_sum is one row of _smooth_topk_sum_batch                     ADR-006

  fabric  two of the fabric learners' folds (buffer cooling, internal gains) as functions of interval
          values in a module of the learners seam; the coordinator keeps the baseline advance, the freeze
          question, the apply, the log and the store write                                 ADR-007
  ceiling the thirteen fabric methods deleted outright: the bound on ADR-007's fall, not a design
  imports the fourteen import bindings D7-s1-03 lists, deleted (the kernel's dead-state part)  ADR-009
  kernel  D7 s1's eight clone arms (nine copies) and two layer arms, from that seat's own edit list
          (dev/audit/rounds/round11/D7/s1/m7_prototypes.py, GOOD + MORE), in one tree      ADR-001, ADR-002
  kstep klayer avail owners fdjac notice reader
          the same ten arms by the seam whose group carries each (SEAM_ARMS): the kernel's two clone
          owners, its two layer arms, entity.py's, money's two, sysid.py's, legionella.py's, inputs.py's

Run (from the repository root; about 30 s per arm):
    python3 dev/audit/rounds/round11/PLAN/prototypes.py                    the seven alone, then combined
    python3 dev/audit/rounds/round11/PLAN/prototypes.py --only hub,circ    those arms alone
    python3 dev/audit/rounds/round11/PLAN/prototypes.py --only hub,circ --combined
    python3 dev/audit/rounds/round11/PLAN/prototypes.py --case planned,floor  the named cases, each one tree

Read at the fork 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 on 2026-11-18 (darwin arm64):
    hub    dS +5.4429 IMPROVES  hub_solve_writes 1 -> 0
    sysid  dS +2.2590 IMPROVES  shared_inplace_writes 3 -> 2
    circ   dS +2.2625 IMPROVES  shared_inplace_writes 3 -> 2, coord_footprint 2496 -> 2490
    reach  dS +1.5850 IMPROVES  coordinator_private_reach 2 -> 0
    tasks  dS +2.2590 IMPROVES  shared_inplace_writes 3 -> 2   (a control since revision 2: not planned)
    clock  dS +0.3479 IMPROVES  layer_violations 13 -> 10
    topk   dS +0.6964 IMPROVES  duplication_copies 18 -> 17
    all seven combined  dS +18.9616 IMPROVES, admissible (shared_inplace_writes 3 -> 0)
    fabric dS +0.0163 IMPROVES  coord_footprint 2496 -> 2468
    ceiling coord_footprint 2496 -> 2359 (137 statements; the tree is broken, only the footprint is read)
    imports dS +0.0000 NULL
    kernel dS +9.2671 IMPROVES  duplication_copies 18 -> 9, layer_violations 13 -> 6
  the per-seam arms, each alone (revision 2):
    kstep  dS +1.4326 IMPROVES  duplication_copies 18 -> 16
    klayer dS +1.0000 IMPROVES  layer_violations 13 -> 6
    avail  dS +1.4326 IMPROVES  duplication_copies 18 -> 16
    owners dS +1.4326 IMPROVES  duplication_copies 18 -> 16
    fdjac  dS +0.6964 IMPROVES  duplication_copies 18 -> 17
    notice dS +0.6964 IMPROVES  duplication_copies 18 -> 17
    reader dS +0.6964 IMPROVES  duplication_copies 18 -> 17
    klayer+reader+clock combined  dS +2.9188  duplication_copies 18 -> 17, layer_violations 13 -> 2
  cases (--case), each one tree (revision 2; the task-set arm is no longer planned, ADR-005 part 3):
    planned          dS +24.3372  every planned move (duplication_copies 18 -> 8, shared_inplace_writes
                     3 -> 1, hub_solve_writes 1 -> 0, layer_violations 13 -> 2, coordinator_private_reach
                     2 -> 0, coord_footprint 2496 -> 2462); shape_copies 40 -> 35, no tripwire rising.
                     Revision 1 called this tree no-tasks; that name still runs it.
    floor            dS +22.9801  ADR-006 part 2 dropped (duplication_copies 18 -> 9)
    one-copy-short   dS +21.7525  the floor with one clone arm (notice) unrealised (18 -> 10): short of +22.7
    floor-no-fabric  dS +22.9638  the floor with ADR-007 unrealised (coord_footprint 2496 -> 2490 at the
                     fork, which main's nine statements and any fix's rise then put above 2496: inadmissible)
    no-circ          dS +21.1498  planned with the circ term not banked (shared_inplace_writes 3 -> 2,
                     coord_footprint 2496 -> 2468): short of +22.7 (decided 2026-11-18)
    floor-no-circ    dS +19.7927  the floor with the circ term not banked: short of +22.7
    with-tasks       dS +29.7802  the control: planned plus the withdrawn task-set arm (shared_inplace_writes
                     3 -> 0). Revision 1 called this tree full; that name still runs it. Not a planned reading.
Writes only under a tempfile root.
"""
from __future__ import annotations

import os
import py_compile
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
FORK = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
PKG = "custom_components/heatpump_optimizer"
sys.path.insert(0, str(REPO / "tools" / "audit"))

from archscore import score, vector  # noqa: E402


def sub(root: Path, rel: str, old: str, new: str) -> None:
    """Replace ``old`` by ``new`` in ``rel``; the anchor must occur exactly once."""
    path = root / PKG / rel
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"{rel}: anchor occurs {text.count(old)} times, not once: {old[:60]!r}")
    path.write_text(text.replace(old, new))


def cut(root: Path, rel: str, start: str, end: str, new: str, keep_end: bool) -> None:
    """Replace the text from ``start`` to ``end`` (``end`` kept when ``keep_end``) by ``new``."""
    path = root / PKG / rel
    text = path.read_text()
    a = text.index(start)
    b = text.index(end, a)
    path.write_text(text[:a] + new + text[b if keep_end else b + len(end):])


def hub(r: Path) -> None:
    sub(r, "coordinator.py",
        '        getattr(self, "_ctx", self)._opt_config.comfort_weight = self._comfort_weight()\n',
        "        ctx = self._ctx\n"
        "        self._ctx = replace(\n"
        "            ctx, _opt_config=replace(ctx._opt_config, comfort_weight=self._comfort_weight())\n"
        "        )\n")


def sysid(r: Path) -> None:
    sub(r, "sysid.py", "    ident.config.enabled = config.system_identification_enabled\n", "")
    sub(r, "sysid.py", "    armed = ident.arm(now, plant=plant, learner_samples=learner_samples, probe=probe)\n",
        "    armed = ident.arm(now, plant=plant, learner_samples=learner_samples, probe=probe,\n"
        "                      enabled=config.system_identification_enabled)\n")
    sub(r, "sysid.py",
        '        learner_samples: int = 0, probe: DrawRange | None = None,\n    ) -> bool:\n'
        '        """Arm an experiment',
        '        learner_samples: int = 0, probe: DrawRange | None = None, enabled: bool | None = None,\n'
        '    ) -> bool:\n        """Arm an experiment')
    sub(r, "sysid.py", "        if not self.config.enabled:\n",
        "        if not (self.config.enabled if enabled is None else enabled):\n")


def circ(r: Path) -> None:
    (r / PKG / "circulation.py").write_text(
        '"""The circulation pumps\' one owner: the write and the record of the write."""\n'
        "from __future__ import annotations\n\nimport logging\nfrom typing import Any\n\n"
        "_LOGGER = logging.getLogger(__name__)\n\n\n"
        "class CirculationPumps:\n"
        "    def __init__(self) -> None:\n"
        "        self.commanded: dict[str, bool] = {}\n\n"
        "    async def async_set(self, hass: Any, entity_id: str, on: bool, reason: str, *, off: bool) -> None:\n"
        "        previous = self.commanded.get(entity_id)\n"
        "        if off or (previous is not None and previous is on):\n"
        "            return\n"
        '        service = "turn_on" if on else "turn_off"\n'
        "        try:\n"
        '            await hass.services.async_call("homeassistant", service, {"entity_id": entity_id})\n'
        '            _LOGGER.info("Pump %s -> %s: %s", entity_id, service, reason)\n'
        "        except Exception as err:  # noqa: BLE001\n"
        '            _LOGGER.warning("Could not command pump %s: %s", entity_id, err)\n'
        "            return\n"
        "        self.commanded[entity_id] = on\n")
    cut(r, "coordinator.py", "        previous = self._pump_commanded.get(entity_id)\n",
        "        self._pump_commanded[entity_id] = on\n",
        "        await self._circulation.async_set(\n"
        "            self.hass, entity_id, on, reason, off=self._mode in (MODE_OFF,)\n"
        "        )\n", keep_end=False)
    sub(r, "coordinator.py", "        self._pump_commanded: dict[str, bool] = {}\n",
        "        self._circulation = CirculationPumps()\n")
    sub(r, "coordinator.py", "from . import boost\n", "from . import boost\nfrom .circulation import CirculationPumps\n")
    if "_pump_commanded" in (r / PKG / "coordinator.py").read_text():
        raise SystemExit("circ: a reader of the old dict is left")


def reach(r: Path) -> None:
    sub(r, "boost.py", '    return getattr(coord, "mode", None) == MODE_BOOST\n',
        "    return held_for(coord).mode_since is not None\n")
    sub(r, "diagnostics.py", '        "mode": getattr(coord, "mode", None),\n',
        '        "mode": state.mode if state else None,\n')
    sub(r, "coordinator.py", "    solve_failures: int | None = None\n    cop_scale: float | None = None\n",
        "    solve_failures: int | None = None\n    mode: str | None = None\n    cop_scale: float | None = None\n")
    sub(r, "coordinator.py", '            solve_failures=getattr(coord, "_solve_failures", None),\n',
        '            solve_failures=getattr(coord, "_solve_failures", None),\n'
        '            mode=getattr(coord, "_mode", None),\n')


def tasks(r: Path) -> None:
    sub(r, "coordinator.py", "        self._background_tasks.clear()\n", "")


def clock(r: Path) -> None:
    sub(r, "inputs.py",
        "        from homeassistant.util import dt as dt_util\n\n        utc_now: datetime = dt_util.utcnow()\n"
        "        return utc_now\n",
        "        return datetime.now(timezone.utc)\n")
    sub(r, "inputs.py", "from datetime import datetime, timedelta\n", "from datetime import datetime, timedelta, timezone\n")


def topk(r: Path) -> None:
    cut(r, "tariff.py",
        "    x = np.asarray(values, dtype=float)\n    if x.size == 0 or k <= 0:\n        return 0.0\n",
        "def _smooth_topk_sum_batch(",
        "    x = np.asarray(values, dtype=float)\n"
        "    return float(_smooth_topk_sum_batch(x[None, :], k, tau)[0])\n\n\n", keep_end=True)


def fabric(r: Path) -> None:
    """Two of the fabric folds as functions of values: the gate arithmetic leaves the coordinator class,
    which keeps the baseline advance, the freeze question, the apply, the log and the store write."""
    (r / PKG / "fabric_learning.py").write_text(
        '"""The fabric learners\' folds: interval values in, the new parameter out."""\n'
        "from __future__ import annotations\n\nfrom datetime import datetime\n\nimport numpy as np\n\n"
        "from .const import (\n    DHW_COOLING_REFERENCE_DELTA,\n    INTERNAL_GAINS_ALPHA,\n"
        "    INTERNAL_GAINS_MAX_FACTOR,\n    INTERNAL_GAINS_RIDGE,\n)\n\n"
        "BUFFER_COOLING_ALPHA_DOWN = 0.25\nBUFFER_COOLING_ALPHA_UP = 0.02\n"
        "BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.15\nBUFFER_COOLING_MAX_SAMPLE_HOURS = 3.0\n"
        "BUFFER_COOLING_MIN_DELTA = 4.0\nBUFFER_AMBIENT_TEMP = 20.0\n\n\n"
        "def fold_buffer_cooling(\n    rate: float, previous_temp: float, buffer_temp: float, dt_h: float,\n"
        "    bounds: tuple[float, float],\n) -> tuple[float, float] | None:\n"
        "    if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS or dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS:\n        return None\n"
        "    if buffer_temp > previous_temp:\n        return None\n"
        "    start_delta = previous_temp - BUFFER_AMBIENT_TEMP\n    end_delta = buffer_temp - BUFFER_AMBIENT_TEMP\n"
        "    if start_delta < BUFFER_COOLING_MIN_DELTA or end_delta < BUFFER_COOLING_MIN_DELTA:\n        return None\n"
        "    observed = float(-np.log(end_delta / start_delta) / dt_h * DHW_COOLING_REFERENCE_DELTA)\n"
        "    if not np.isfinite(observed) or observed < bounds[0] or observed > bounds[1]:\n        return None\n"
        "    alpha = BUFFER_COOLING_ALPHA_DOWN if observed < rate else BUFFER_COOLING_ALPHA_UP\n"
        "    return observed, (1.0 - alpha) * rate + alpha * observed\n\n\n"
        "def fold_internal_gains(\n    profile: list[float] | None, g0: float, capacity: float,\n"
        "    previous_time: datetime | None, residual: float, dt_h: float,\n) -> list[float] | None:\n"
        "    if previous_time is None or dt_h <= 1e-6 or capacity <= 1e-6:\n        return profile\n"
        "    y = residual * capacity / dt_h\n"
        "    if not np.isfinite(y):\n        return profile if profile is not None else [g0] * 24\n"
        "    out = list(profile) if profile is not None else [g0] * 24\n"
        "    hour = int(previous_time.hour) % 24\n"
        "    g = out[hour] + INTERNAL_GAINS_ALPHA * y - INTERNAL_GAINS_RIDGE * (out[hour] - g0)\n"
        "    out[hour] = float(np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05)))\n"
        "    return out\n")
    cut(r, "coordinator.py", "        if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:\n",
        "        self._buffer_cooling_samples += 1\n",
        "        fold = fold_buffer_cooling(\n"
        "            self._buffer_cooling_rate, previous_temp, buffer_temp, dt_h, self._buffer_cooling_bounds()\n"
        "        )\n"
        "        if fold is None:\n            return\n"
        "        observed, rate = fold\n"
        "        self._apply_buffer_cooling_rate(rate)\n", keep_end=True)
    cut(r, "coordinator.py", "        if previous_time is None or dt_h <= 1e-6:\n            return\n        capacity = _zone_capacity(",
        "    def ", 
        "        self._internal_gains_profile = fold_internal_gains(\n"
        "            self._internal_gains_profile, float(ctx._thermal_params.internal_gains),\n"
        "            _zone_capacity(ctx._thermal_params), previous_time, residual, dt_h,\n"
        "        )\n\n", keep_end=True)
    for name in ("ALPHA_DOWN", "ALPHA_UP", "MIN_SAMPLE_HOURS", "MAX_SAMPLE_HOURS", "MIN_DELTA"):
        cut(r, "coordinator.py", f"BUFFER_COOLING_{name} = ", "\n", "", keep_end=False)
    cut(r, "coordinator.py", "BUFFER_AMBIENT_TEMP = ", "\n", "", keep_end=False)
    sub(r, "coordinator.py", "from . import boost\n",
        "from . import boost\nfrom .fabric_learning import fold_buffer_cooling, fold_internal_gains\n")


FABRIC_METHODS = (
    "_buffer_cooling_bounds", "_apply_buffer_cooling_rate", "_apply_house_heat_loss_scale",
    "_apply_lower_floor_loss_ratio", "_void_heat_loss_learners", "async_reset_heat_loss_learners",
    "_house_heat_loss_anchor", "_heat_loss_anchors", "_reanchor_house_heat_loss_scale",
    "_async_learn_buffer_cooling", "_close_fabric_interval", "_async_learn_house_heat_loss", "_fold_internal_gains",
)


def ceiling(r: Path) -> None:
    """The thirteen fabric methods deleted outright: the most ADR-007 could ever pay, not a design."""
    import ast
    path = r / PKG / "coordinator.py"
    lines = path.read_text().splitlines(keepends=True)
    spans = [(n.lineno - 1, n.end_lineno) for n in ast.walk(ast.parse("".join(lines)))
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in FABRIC_METHODS]
    if len(spans) != len(FABRIC_METHODS):
        raise SystemExit(f"ceiling: {len(spans)} of {len(FABRIC_METHODS)} methods found")
    for a, b in sorted(spans, reverse=True):
        del lines[a:b]
    path.write_text("".join(lines))


UNUSED = (
    ("config_flow.py", "    CONF_AWAY_RETURN_ENTITY,\n"), ("config_flow.py", "    PRICE_SOURCE_TIBBER,\n"),
    ("coordinator.py", "    SCORE_ALPHA,\n"), ("coordinator.py", "    TIBBER_API_URL,\n"),
    ("coordinator.py", "    WATER_SPECIFIC_HEAT,\n"), ("modbus_prefill.py", "    CONF_UPPER_FLOOR_THERMAL_MASS,\n"),
    ("optimizer.py", "    MIN_RUNNING_DRAW_KW,\n"), ("optimizer.py", "    channel_heating_steps,\n"),
    ("pump_arbiter.py", "    CONF_SPACE_SETPOINT_POWER_FEEDBACK,\n"),
    ("thermal_model.py", "    BUFFER_COOLING_RATE_MAX,\n"), ("thermal_model.py", "    BUFFER_COOLING_RATE_MIN,\n"),
    ("thermal_model.py", "    DEFAULT_BUFFER_COOLING_RATE,\n"),
)


def imports(r: Path) -> None:
    """D7-s1-03's fourteen bindings nothing loads, deleted (the kernel's dead-state part)."""
    for rel, line in UNUSED:
        sub(r, rel, line, "")
    sub(r, "coordinator.py", "from .dhw_learning import DHW_PROFILE_STORE_VERSION, DhwProfileLearner\n",
        "from .dhw_learning import DhwProfileLearner\n")
    sub(r, "pump_arbiter.py", "InputReader, SetpointGrid, quantise_setpoint_c, read_setpoint,",
        "InputReader, SetpointGrid, read_setpoint,")


def _m7(r: Path, names: tuple[str, ...]) -> None:
    """Arms of D7 s1's own edit list (dev/audit/rounds/round11/D7/s1/m7_prototypes.py), by name."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("m7_prototypes", REPO / "dev/audit/rounds/round11/D7/s1/m7_prototypes.py")
    m7 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m7)
    m7.apply(r / PKG, list(names))


#: D7-s1-05's eight clone arms and D7-s1-06's two layer arms, by the seam whose group carries each.
SEAM_ARMS = {
    "kstep": ("note", "step"),      # R11-SEAM-kernel-step: drift.py and plan_step.py are the owners
    "klayer": ("layer", "curr"),    # R11-SEAM-kernel-layering: drift.py, const.py and currency.py
    "avail": ("avail",),            # R11-SEAM-entity-service: entity.py
    "owners": ("day", "entry"),     # R11-SEAM-money: price_model.py and ledger.py
    "fdjac": ("fdjac",),            # R11-SEAM-learners: sysid.py
    "notice": ("notice",),          # R11-SEAM-actuation-release: legionella.py
    "reader": ("reader",),          # R11-SEAM-inputs-freshness: inputs.py (with the clock arm)
}


def kernel(r: Path) -> None:
    """All ten of D7 s1's arms in one tree, as revision 1 planned them in one group. Kept so the
    per-seam arms below can be read against it: the seven SEAM_ARMS together are this arm."""
    for names in SEAM_ARMS.values():
        _m7(r, names)


ARMS = {**{k: (lambda r, v=v: _m7(r, v)) for k, v in SEAM_ARMS.items()},
        "fabric": fabric, "ceiling": ceiling, "imports": imports, "kernel": kernel, "hub": hub, "sysid": sysid, "circ": circ, "reach": reach, "tasks": tasks, "clock": clock, "topk": topk}


SEVEN = ("hub", "sysid", "circ", "reach", "tasks", "clock", "topk")
SEAMS = tuple(SEAM_ARMS)
PLANNED = SEAMS + ("imports", "hub", "sysid", "circ", "reach", "clock", "topk", "fabric")
CASES = {
    "planned": PLANNED,                                             # every planned move (revision 2)
    "floor": tuple(a for a in PLANNED if a != "topk"),              # ADR-006 part 2 dropped
    "floor-no-fabric": tuple(a for a in PLANNED if a not in ("topk", "fabric", "imports")),  # and ADR-007 unrealised
    "with-tasks": PLANNED + ("tasks",),                             # the control: the withdrawn task-set arm
    "one-copy-short": tuple(a for a in PLANNED if a not in ("topk", "notice")),  # the floor, one clone arm unrealised
    "no-circ": tuple(a for a in PLANNED if a != "circ"),           # planned, circ not banked (decided 2026-11-18)
    "floor-no-circ": tuple(a for a in PLANNED if a not in ("topk", "circ")),  # the floor, circ not banked
}
CASES["no-tasks"] = CASES["planned"]                                # revision 1's name for the same tree
CASES["full"] = CASES["with-tasks"]                                 # revision 1's name for the same tree


def main(argv: list[str]) -> int:
    if os.environ.get("ARCHSCORE_ABLATE"):
        raise SystemExit("ARCHSCORE_ABLATE is set: a gain that appears only without the counters did not happen")
    names = list(SEVEN)
    if "--only" in argv:
        names = argv[argv.index("--only") + 1].split(",")
    if "--case" in argv:
        runs = [list(CASES[c]) for c in argv[argv.index("--case") + 1].split(",")]
    else:
        runs = [names] if "--combined" in argv else [[n] for n in names] + ([names] if "--only" not in argv else [])
    with tempfile.TemporaryDirectory(prefix="r11-plan-") as tmp:
        fork = score.tree_of(FORK, Path(tmp) / "fork")
        base = vector.measure(fork)
        for i, run in enumerate(runs):
            tree = Path(tmp) / f"arm{i}"
            shutil.copytree(fork / "custom_components", tree / "custom_components")
            for name in run:
                ARMS[name](tree)
            for path in (tree / PKG).glob("*.py"):
                py_compile.compile(str(path), doraise=True)
            print("ARM", "+".join(run))
            print(score.report(base, vector.measure(tree)), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
