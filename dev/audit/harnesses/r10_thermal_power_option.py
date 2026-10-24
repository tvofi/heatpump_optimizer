#!/usr/bin/env python3
"""Before/after probe for #1955 fold (e): the optional thermal power entity.

What the group landed. ``flow_meter.read_heat_output_kw`` answers a configured
heat meter's reading ahead of the flow meter; ``_fold_measured_cop`` takes a
measured heat as COP evidence (``flow_meter.cop_evidence``), judged at the
supply the pump ran at (``flow_meter.space_reference_cop``). The defect it
closes is ``flow_lift.py``'s module docstring: on a direct plant the efficiency
learner folds the lift-driven COP drop into ``cop_scale``, so the scale walks
with the weather. Re-run this probe when ``_fold_measured_cop``,
``_cop_reference_curve``, ``cop_evidence``, ``space_reference_cop`` or
``ThermalModel._cop_law`` changes.

The input, identical at both trees: a direct plant whose supply follows a
weather curve (``50 - 0.8 x outdoor`` degC), whose true COP is ``TRUE_K`` times
the model's own law at that supply at every outdoor temperature, delivering a
fixed 9 kW that the plan asks for at its own price. Each outdoor point folds
``FOLDS`` intervals through the tree's own ``_fold_measured_cop`` on a stub
carrying only the attributes that method reads; the outdoor points sit outside
the frost band, which hands its intervals to the defrost derate.

Arms, each printed per tree as ``ARM <name> spread=<max-min> <outdoor>=<scale>``
with every scale a ``repr`` so an equality across trees is bitwise:
- ``metered``: this cycle's heat (9 kW) is on the flow-bias holder, the way a
  configured heat meter leaves it. The fix reads it; the merge base ignores it.
- ``commanded``: no heat reading. The null control: the byte-identical claim
  for an install without the key, so it must print the same at both trees.

Expected: ``metered`` spread near zero with every scale at ``TRUE_K`` at the
head, and the same spread as ``commanded`` at the base; ``commanded`` identical
at both trees. Run: ``python3 dev/audit/harnesses/r10_thermal_power_option.py
[BASE_SHA]`` from the repository root; BASE_SHA defaults to the merge base with
origin/main.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

TRUE_K = 0.9
FOLDS = 400
OUTDOORS = (-15.0, -10.0, -5.0, -2.0, 5.0, 8.0, 12.0)

PROBE = r'''
import sys
sys.path[:0] = [sys.argv[1] + "/tests/hastub", sys.argv[1] + "/custom_components"]
from heatpump_optimizer import flow_lift
from heatpump_optimizer.accuracy import MeasuredCop
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
from heatpump_optimizer.defrost import DefrostWindow
from heatpump_optimizer.pump_signals import PumpSignals
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

TRUE_K, FOLDS, OUTDOORS = float(sys.argv[2]), int(sys.argv[3]), eval(sys.argv[4])


class Gate:
    _learn_measured_cop = Coord._learn_measured_cop
    _fold_measured_cop = Coord._fold_measured_cop
    _commanded_power = Coord._commanded_power
    _commanded_split = Coord._commanded_split
    _cop_reference_curve = Coord._cop_reference_curve
    _COP_CURVE_SHARE = Coord._COP_CURVE_SHARE
    _apply_cop_scale = Coord._apply_cop_scale

    def __init__(self):
        self._measured_power = None
        self._current_action = {}
        self._pump_signals = PumpSignals()
        self._defrost_window = DefrostWindow()
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
        self._current_state = ThermalState(room_temperature=21.0, outdoor_temperature=OUTDOORS[0])
        self._cop_scale = 1.0
        self._cop_samples = 0
        self._cop_ratio_ewma = None
        self._measured_cop = MeasuredCop()
        self._immersion_active = False
        self._flow_bias = flow_lift.FlowCurveBias()

    def _learning_frozen(self, *keys):
        return None

    def _observe_cop_health(self, observed_cop, dhw_curve=False):
        return None

    def _fold_capacity_envelope(self, observed_cop, heat_kw=None):
        return None


def walk(metered):
    gate, law = Gate(), ThermalModel(ThermalParameters())
    out = {}
    for outdoor in OUTDOORS:
        supply = 50.0 - 0.8 * outdoor
        gate._current_state.outdoor_temperature = outdoor
        true_cop = TRUE_K * law.compute_cop_dhw(outdoor, supply)
        for _ in range(FOLDS):
            gate._current_action = {"power": 9.0 / gate._thermal_model.compute_cop(outdoor)}
            gate._measured_power = 9.0 / true_cop
            gate._flow_bias.observe_temps(supply, supply - 5.0, heat_output_kw=9.0 if metered else None)
            gate._learn_measured_cop()
        out[outdoor] = gate._cop_scale
    return out


for arm, metered in (("metered", True), ("commanded", False)):
    scales = walk(metered)
    spread = max(scales.values()) - min(scales.values())
    print("ARM", arm, "spread=%.4f" % spread, " ".join("%g=%r" % kv for kv in scales.items()))
'''


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


def _tree_from(sha: str, root: Path) -> Path:
    """The merge base's production package and HA stub, unpacked into a temp dir."""
    out = Path(tempfile.mkdtemp(prefix="r10tp-"))
    blob = subprocess.run(
        ["git", "-C", str(root), "archive", sha, "custom_components", "tests/hastub"],
        check=True, capture_output=True,
    ).stdout
    tar_path = out / "tree.tar"
    tar_path.write_bytes(blob)
    with tarfile.open(tar_path) as tar:
        tar.extractall(out, filter="data")
    tar_path.unlink()
    return out


def main() -> int:
    root = repo_root(__file__)
    base = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(
        ["git", "-C", str(root), "merge-base", "origin/main", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    head = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    rc = 0
    for label, tree in (("head " + head[:12], root), ("base " + base[:12], _tree_from(base, root))):
        run = subprocess.run(
            [sys.executable, "-I", "-c", PROBE, str(tree), str(TRUE_K), str(FOLDS), repr(OUTDOORS)],
            capture_output=True, text=True, env={**os.environ, "PYTHONHASHSEED": "0"},
        )
        print("TREE", label, "rc=%d" % run.returncode)
        sys.stdout.write(run.stdout)
        if run.returncode:
            sys.stdout.write(run.stderr[-2000:])
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
