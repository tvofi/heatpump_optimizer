#!/usr/bin/env python3
"""Mutation and null-control probes for R9-UX-10 (#2016 item 4).

What the group landed. ``ThermalModel.simulate_step`` takes
``measured_heat_kw`` and spends it in place of the ``cop * electrical_power``
it would otherwise infer for Q_hp, on both zone paths; in ``coordinator.py``
``_interval_measured_heat_kw`` decides whether the cycle's published
flow-meter reading may stand in for the interval a learner replays, and
``_replay_interval`` -- the dedupe of the two interval learners' identical
replay block, which ``tools/audit/archscore/planted/perturb/G2_dedupe.py``
carries as a GOOD planted control against the pinned tree -- is the one place
that passes it. Re-run this probe when ``simulate_step``, either zone step,
``_interval_measured_heat_kw``, ``_replay_interval``,
``flow_meter.read_heat_output_kw`` or the R9-UX-10 block of
``tests/features.py`` changes.

Metric BLOCK: the number of failing checks when ``tests/features.py``'s own
R9-UX-10 block runs in the tree, sliced verbatim from its ``_FM_LEARN_KW``
anchor to the file's ``sys.exit``, over a prelude of the fixtures it uses --
also sliced from ``features.py`` (``_METER``/``_t2_coord``,
``_t2_count_saves``, the ``_T2_*``/``_t2_house``/``_t2_drive`` group) rather
than restated here, so a fixture the block depends on cannot drift from the
copy the full run uses.
Metric figures, eleven per tree, each a ``repr`` so an equality is bitwise:
the house heat-loss scale and the replay's prediction on the key-unset arm
(``SCALE_UNSET``, ``ROOM_UNSET``, ``SLAB_UNSET``, ``UPPER_UNSET``,
``LOWER_UNSET``, ``RESIDUAL_UNSET``), which is the byte-identical null control
and must read the same at the head, at the merge base and in every mutant; and
the same on the planted arm (``*_PLANTED``), which is what the substitution
moves. Two of the planted figures are honestly flat and are printed so that
stays visible: the single-zone step's room rate and the two-zone step's lower
floor carry no heat-input term -- ``_single_zone_rates`` puts ``thermal_power``
in the slab's rate and ``_two_zone_rates`` in the slab's and the upper floor's
-- so within one replay, which is what a learner takes, the room and the lower
floor do not move; the slab and the upper floor are where it lands.

Trees, each copied from the checkout into a temp dir:
- ``head``: unchanged;
- ``base``: this head's ``tests/`` over the merge base's (``BASE_SHA``,
  ``UX10_BASE_SHA`` overrides) three production files, where
  ``measured_heat_kw`` does not exist -- the failing-first red, reproducible
  without a checkout of the branch;
- ``m_precedence``: ``flow_meter.read_heat_output_kw``'s precedence predicate
  (``cap.measured_power or cap.frequency``) to ``False``, so a power or a
  frequency signal no longer outranks the meter;
- ``m_flow_ok``: the same function's ``flow.value if flow.ok else None`` to
  ``flow.value``, so a stale, negative or unknown-unit reading is spent;
- ``m_sub_single``: ``_simulate_step_single``'s ``if measured_heat_kw is
  None`` to ``if True``, so the single-zone step keeps inferring Q_hp;
- ``m_sub_two_zone``: the same predicate in ``_simulate_step_two_zone``;
- ``m_veto``: ``_interval_measured_heat_kw``'s whole predicate to ``if
  False:``, so an interval the plan split with hot water, or gave nothing, is
  spent on the house;
- ``m_veto_return_del``: the same function's refusal arm deleted, so it always
  answers the reading;
- ``m_veto_tail_del``: its tail answering ``None`` instead of ``heat_kw``,
  which is what RETURN_DEL on that line does -- the operator replaces the
  statement with ``pass`` and the function then falls off its end to the same
  ``None``, so nothing measured reaches a learner;
- ``m_bound_dhw`` and ``m_bound_space``: the predicate's two comparisons, each
  to its closed twin (``dhw_kw > 0.0`` to ``>=``, ``space_kw <= 0.0`` to
  ``<``), the pair CMP_BOUND*2 on that line;
- ``m_except_return_del``: ``_replay_interval``'s ``return None`` in the
  ``except`` arm to ``pass`` -- EQUIVALENT, and the measurement the
  ``survivor_triage`` row
  ``tests/mutation_ledger/survivor_triage/coordinator.py/_replay_interval.RETURN_DEL.d7923b87.json``
  cites: the function falls off its end and returns the same None;
- ``m_guard_off_house`` and ``m_guard_off_lower``: each learner's
  ``if predicted_state is None:`` to ``if False:``, so the None a raising
  replay returns is spent and the AttributeError escapes the learner.

Expected, as measured on 2026-10-10 under Python 3.14.7 against merge base
7cd5a588c, on the tree that carries this file (the pull-request body names the
head; re-run it to re-derive):
    BLOCK head: rc=0 failing_checks=0   (ALL 8 UX-10 EXTRACT PASSED)
    BLOCK base: rc=0 failing_checks=6
    BLOCK m_precedence: rc=0 failing_checks=1
    BLOCK m_flow_ok: rc=0 failing_checks=1
    BLOCK m_sub_single: rc=0 failing_checks=1
    BLOCK m_sub_two_zone: rc=0 failing_checks=2
    BLOCK m_veto: rc=0 failing_checks=1
    BLOCK m_veto_return_del: rc=0 failing_checks=1
    BLOCK m_veto_tail_del: rc=0 failing_checks=4
    BLOCK m_bound_dhw: rc=0 failing_checks=4
    BLOCK m_bound_space: rc=0 failing_checks=1
    BLOCK m_except_return_del: rc=0 failing_checks=0   (equivalent)
    BLOCK m_guard_off_house: rc=0 failing_checks=1
    BLOCK m_guard_off_lower: rc=0 failing_checks=1
    NULL CONTROL every unset-arm figure, head == base: True (6 figures) |
        unchanged in every mutant: True
    BITES the two-zone upper floor the residual is differenced from,
        head != base: True | and at head, planted != unset: True |
        its residual, planted != unset: True | the single-zone replay's slab,
        planted != unset: True | its room, planted == unset: True |
        the lower floor, planted == unset: True
    UPPER_PLANTED head: 20.943135666666667   (base and every unset arm:
        20.921666666666667; RESIDUAL_PLANTED head -0.043135666666668016
        against RESIDUAL_UNSET -0.021666666666668277)
    SLAB_PLANTED head: 27.0422035   (unset: 27.01)
    SCALE_UNSET and SCALE_PLANTED, every tree: 1.01

Which check kills which mutant. ``m_precedence``, ``m_flow_ok``, ``m_veto``,
``m_veto_return_del``, ``m_veto_tail_del``, ``m_bound_dhw``, ``m_bound_space``
and both ``m_guard_off_*``: the arm check "an outranked, stale, negative,
unreadable, unknown-unit, hot-water or nothing-commanded interval reaches no
learner input", except the two guard mutants, which "a replay that raises
costs the sample and nothing else" kills, and ``m_veto_tail_del`` and
``m_bound_dhw``, which also kill the three that assert a value does arrive.
``m_sub_single``: "the model spends a measured heat output instead of
inferring one from the draw". ``m_sub_two_zone``: "the two-zone step spends it
too" and "the two-zone house replay predicts a different upper floor".
``base``: those four plus "a planted 15 L/min over a 5 K drop reaches the
house heat-loss replay as 5.222035 kW" and "and the lower-floor replay".

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/ux10_flow_into_model.py <out-dir>

It writes ``<variant>.block.txt`` into ``<out-dir>`` and prints one SCALE line
per variant.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
PKG = "custom_components/heatpump_optimizer"
FLOW_METER = f"{PKG}/flow_meter.py"
THERMAL = f"{PKG}/thermal_model.py"
COORD = f"{PKG}/coordinator.py"

PRECEDENCE = """    if (
        not cfg.get(const.CONF_FLOW_METER_ENTITY)
        or cap.measured_power
        or cap.frequency
    ):
"""
FLOW_OK = "    return thermal_output_kw(\n        flow.value if flow.ok else None, supply, returned\n    )\n"
SUB_SINGLE = """        pump_heat_kw = (
            cop * electrical_power
            if measured_heat_kw is None
            else measured_heat_kw
        )
        thermal_power = pump_heat_kw + max(0.0, external_heat_kw)
"""
SUB_TWO_ZONE = """        pump_heat_kw = (
            cop * electrical_power
            if measured_heat_kw is None
            else measured_heat_kw
        )
        thermal_power = pump_heat_kw + (0.0 if two_tank else ext)
"""
VETO = ("    if heat_kw is None or dhw_kw > 0.0 or space_kw <= 0.0:\n"
        "        return None\n    return heat_kw\n")

EXCEPT_RETURN = """    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("%s learning simulation failed: %s", label, err)
        return None
"""
PREDICTED_GUARD = """        predicted_state = _replay_interval(
            self, previous_state, previous_power, outdoor, previous_time,
            dt_h, "%s",
        )
        if predicted_state is None:
            return
"""
VETO_BODY = """    if heat_kw is None or dhw_kw > 0.0 or space_kw <= 0.0:
        return None
    return heat_kw
"""

VARIANTS = {
    "head": [],
    "m_precedence": [
        (
            FLOW_METER,
            PRECEDENCE,
            PRECEDENCE.replace(
                "        or cap.measured_power\n        or cap.frequency\n",
                "        or False\n",
            ),
        )
    ],
    "m_flow_ok": [
        (FLOW_METER, FLOW_OK, FLOW_OK.replace("flow.value if flow.ok else None", "flow.value"))
    ],
    "m_sub_single": [
        (THERMAL, SUB_SINGLE, SUB_SINGLE.replace("if measured_heat_kw is None", "if True"))
    ],
    "m_sub_two_zone": [
        (THERMAL, SUB_TWO_ZONE, SUB_TWO_ZONE.replace("if measured_heat_kw is None", "if True"))
    ],
    "m_veto": [(COORD, VETO,
               VETO.replace("if heat_kw is None or dhw_kw > 0.0 or space_kw <= 0.0:",
                          "if False:"))],
    # RETURN_DEL on the predicate's own arm: the refusal deleted, so every
    # interval the plan split or gave nothing is spent on the house.
    "m_veto_return_del": [(COORD, VETO_BODY, "    return heat_kw\n")],
    # RETURN_DEL on the tail: nothing measured reaches a learner.
    "m_veto_tail_del": [(COORD, VETO_BODY, VETO_BODY.replace(
        "        return None\n    return heat_kw\n",
        "        return None\n    return None\n"))],
    # CMP_BOUND, each of the two the predicate holds, one variant each.
    "m_bound_dhw": [(COORD, VETO_BODY, VETO_BODY.replace("dhw_kw > 0.0", "dhw_kw >= 0.0"))],
    "m_bound_space": [(COORD, VETO_BODY, VETO_BODY.replace("space_kw <= 0.0", "space_kw < 0.0"))],
    # RETURN_DEL in the except arm: equivalent, and the survivor_triage row's
    # measurement -- falling off the function's end returns the same None.
    "m_except_return_del": [(COORD, EXCEPT_RETURN, EXCEPT_RETURN.replace(
        "        return None\n", "        pass\n"))],
    # GUARD_OFF on each learner's None test: the prediction a raising replay
    # left is spent, so the AttributeError escapes the learner.
    "m_guard_off_house": [(COORD, PREDICTED_GUARD % "House heat loss",
                           (PREDICTED_GUARD % "House heat loss").replace(
                               "if predicted_state is None:", "if False:"))],
    "m_guard_off_lower": [(COORD, PREDICTED_GUARD % "Lower floor loss",
                           (PREDICTED_GUARD % "Lower floor loss").replace(
                               "if predicted_state is None:", "if False:"))],
}
#: ``base``: the merge base's three production files under this head's tests.
BASE_SHA = os.environ.get("UX10_BASE_SHA", "7cd5a588cbbbef354c00148040da2d720b8a888c")
BASE_FILES = (FLOW_METER, THERMAL, COORD)

DRIVER = r'''
import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
import asyncio as _asyncio
import numpy as np
from dataclasses import replace
from datetime import datetime, timedelta
from harness import FakeState, Results, UTC, minutes_ago
from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass, FakeHass
from homeassistant.util import dt as dt_util
from heatpump_optimizer import const as _fb_const
from heatpump_optimizer import flow_meter as _fm
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as _Coord
from heatpump_optimizer.inputs import InputReader as _fmReader
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState)

NOW = datetime(2026, 2, 1, 12, 0, tzinfo=UTC)
R = Results("ux10 flow meter into the model")
src = open("tests/features.py").read()


def sliced(start_anchor, end_anchor, label):
    start = src.index(start_anchor)
    return src[start:src.index(end_anchor, start)]


ns = dict(globals())
# the fixtures the block uses, sliced from features.py rather than restated
exec(compile(sliced("_METER = {", "def _listeners(", "_METER/_t2_coord"),
             "features.py#_t2_coord", "exec"), ns)
exec(compile(sliced("def _t2_count_saves(coord):", "def _t2_buffer(", "_t2_count_saves"),
             "features.py#_t2_count_saves", "exec"), ns)
exec(compile(sliced("_T2_HOUSE_CFG = {", "def _t2_raise_model(", "_T2_* / _t2_house / _t2_drive"),
             "features.py#_t2_house", "exec"), ns)
exec(compile(sliced("def _t2_raise_model(", "_t2_hl_ok = _t2_house()", "_t2_raise_model"),
             "features.py#_t2_raise_model", "exec"), ns)
exec(compile(sliced("_FM_LEARN_KW = ", 'sys.exit(R.close("FEATURE CHECKS"))', "the R9-UX-10 block"),
             "features.py#ux10", "exec"), ns)
def fig(label, value):
    print(label, repr(value))


fig("SCALE_UNSET", ns["_fm_unset"]._house_heat_loss_scale)
fig("SCALE_PLANTED", ns["_fm_coord"]._house_heat_loss_scale)
fig("ROOM_UNSET", ns["_fm_unset_seen"]["state"].room_temperature)
fig("ROOM_PLANTED", ns["_fm_seen"]["state"].room_temperature)
fig("SLAB_UNSET", ns["_fm_unset_seen"]["state"].slab_temperature)
fig("SLAB_PLANTED", ns["_fm_seen"]["state"].slab_temperature)
fig("UPPER_UNSET", ns["_fm_2z_unset_seen"]["state"].upper_floor_temperature)
fig("UPPER_PLANTED", ns["_fm_2z_seen"]["state"].upper_floor_temperature)
fig("LOWER_UNSET", ns["_fm_lf_seen"]["state"].lower_floor_temperature)
fig("RESIDUAL_UNSET", ns["_fm_2z_unset"]._current_state.upper_floor_temperature
    - ns["_fm_2z_unset_seen"]["state"].upper_floor_temperature)
fig("RESIDUAL_PLANTED", ns["_fm_2z"]._current_state.upper_floor_temperature
    - ns["_fm_2z_seen"]["state"].upper_floor_temperature)
print("RC", R.close("UX-10 EXTRACT"))
'''


def build(variant, root):
    for d in ("custom_components", "tests"):
        shutil.copytree(
            REPO / d, Path(root) / d, ignore=shutil.ignore_patterns("__pycache__")
        )
    if variant == "base":
        for rel in BASE_FILES:
            text = subprocess.run(
                ["git", "show", f"{BASE_SHA}:{rel}"],
                cwd=REPO, capture_output=True, text=True, check=True,
            ).stdout
            (Path(root) / rel).write_text(text)
        return
    for rel, old, new in VARIANTS[variant]:
        f = Path(root) / rel
        s = f.read_text()
        assert s.count(old) == 1, (variant, rel, s.count(old))
        f.write_text(s.replace(old, new))


FIGURES = ("SCALE_UNSET", "SCALE_PLANTED", "ROOM_UNSET", "ROOM_PLANTED",
           "SLAB_UNSET", "SLAB_PLANTED", "UPPER_UNSET", "UPPER_PLANTED",
           "LOWER_UNSET", "RESIDUAL_UNSET", "RESIDUAL_PLANTED")


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    scales = {}
    for v in list(VARIANTS) + ["base"]:
        with tempfile.TemporaryDirectory(prefix="ux10-probe-") as root:
            build(v, root)
            env = dict(os.environ, PYTHONPATH=f"{root}/tests/hastub")
            run = subprocess.run(
                [sys.executable, "-c", DRIVER], cwd=root,
                capture_output=True, text=True, env=env,
            )
        (out / f"{v}.block.txt").write_text(run.stdout + run.stderr)
        fails = [ln for ln in run.stdout.splitlines()
                 if ln.lstrip().startswith("FAIL ")]
        figures = dict(
            (ln.split(" ", 1)[0], ln.split(" ", 1)[1])
            for ln in run.stdout.splitlines()
            if ln.split(" ", 1)[0] in FIGURES
        )
        scales[v] = figures
        print(f"BLOCK {v}: rc={run.returncode} failing_checks={len(fails)}")
        for ln in fails:
            print("   ", ln.strip()[:220])
        if run.returncode not in (0, 1):
            print(run.stderr[-3000:])
        for key in sorted(figures):
            print(f"{key} {v}: {figures[key]}")
    head, base = scales["head"], scales["base"]
    unset = [k for k in head if k.endswith("_UNSET")]
    print(
        "NULL CONTROL every unset-arm figure, head == base:",
        all(head[k] == base[k] for k in unset), f"({len(unset)} figures)",
        "| unchanged in every mutant:",
        all(scales[v][k] == head[k] for v in scales for k in unset),
    )
    print(
        "BITES the two-zone upper floor the residual is differenced from, "
        "head != base:", head["UPPER_PLANTED"] != base["UPPER_PLANTED"],
        "| and at head, planted != unset:",
        head["UPPER_PLANTED"] != head["UPPER_UNSET"],
        "| its residual, planted != unset:",
        head["RESIDUAL_PLANTED"] != head["RESIDUAL_UNSET"],
        "| the single-zone replay's slab, planted != unset:",
        head["SLAB_PLANTED"] != head["SLAB_UNSET"],
        "| its room, planted == unset (the single-zone step's room rate "
        "carries no heat term):", head["ROOM_PLANTED"] == head["ROOM_UNSET"],
        "| the lower floor, planted == unset (it follows the slab a step "
        "later):", head["LOWER_UNSET"] == base["LOWER_UNSET"],
    )


if __name__ == "__main__":
    main()
