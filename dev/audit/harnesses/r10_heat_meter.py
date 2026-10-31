#!/usr/bin/env python3
"""Before/after probe for #2261: a delivered-heat kWh counter, read per span.

What the group landed. ``heat_energy.HeatEnergyMeter`` reads a configured
``total_increasing`` heat counter per span, the span closing on elapsed time
inside the interval learners' sample bounds; ``flow_meter.read_heat_output_kw``
yields to it (counter, then thermal power, then flow); on a counter install the
per-cycle COP fold stops at the span (``COP_REFUSED_SPAN_OPEN``) and
``coordinator._async_learn_heat_span`` folds heat over electricity on the two
counters' deltas through ``_fold_cop_evidence``. The defect it closes is the
owner's report on #2261: a point thermal power reading, sampled once a refresh,
reads a cycling pump as either its full output or nothing, so short compressor
runs are lost and the COP it implies is wrong by the duty. Re-run this probe
when ``_fold_measured_cop``, ``_fold_cop_evidence``, ``_cop_reference_curve``,
``_async_learn_heat_span`` or ``heat_energy`` changes.

The input, identical at both trees: the #2753 harness's direct plant (supply on
a ``50 - 0.8 x outdoor`` degC weather curve, true COP ``TRUE_K`` times the
model's own law at that supply), now cycling: the compressor runs ``DUTY`` of
each 30 min refresh at ``RUN_KW`` of heat, so the interval average is
``DUTY x RUN_KW``, the electric draw that over the true COP, and the plan asks
the average at the model's COP. The thermal power meter is read at the refresh
instant, on in a deterministic ``DUTY`` share of them. Each outdoor point runs
``CYCLES`` refreshes on a stub carrying only the attributes these methods read.

Arms, each printed per tree as ``ARM <name> spread=<max-min> folds=<n>
<outdoor>=<scale>``, every scale a ``repr`` so an equality across trees is
bitwise:
- ``point``: the thermal power meter alone. The defect's own shape, and a null
  for the head: the point path is unchanged, so it must print the same at both.
- ``counter``: a heat counter and an electric counter beside the point meter.
  The base has no counter key and reads the point meter; the head reads the
  counter's span and should sit at ``TRUE_K`` at every outdoor point.
- ``commanded``: no heat reading at all. The null control for an install with
  neither key: byte-identical at both trees.
- ``reset``: the counter arm with the heat counter planted back to zero every
  ``RESET_EVERY`` refreshes. The head refuses each reset span and re-baselines,
  so it reads ``TRUE_K`` on fewer folds; the base reads as ``point``.
- ``integer``: the counter arm with the heat counter floored to whole kWh; at
  this load each span expects more than one step, so it reads ``TRUE_K`` too.

One more line per tree, ``CLAMP``: the #2698 carry, "clamp means reset" kept.
The void path runs ``reanchor_heat_loss`` at zero confidence on both learners,
so over a grid of stored values far outside their bounds it resets nothing and
returns the configuration (every value 1); its null, the same grid at a
converged learner's confidence, resets some. Expected identical at both trees.

At the head only, ``EPS`` lines: an integer-kWh counter at 0.6, 1.5, 2.2 and
3.0 kW on the 30 min cadence, under the shipped resolution bound and under the
design's 0.5 (the dr3-eps-at-span re-measure): the spans it closes, the spans
the bound keeps, their mean and spread in kW, and the span lengths.

Expected: at the head ``counter``, ``reset`` and ``integer`` each scale within
the step bound of ``TRUE_K`` with spread near zero, ``point`` and ``commanded``
identical to the base's; at the base ``counter``, ``reset`` and ``integer``
equal ``point``. Run: ``python3 dev/audit/harnesses/r10_heat_meter.py
[BASE_SHA]`` from the repository root; BASE_SHA defaults to the merge base with
origin/main.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

TRUE_K = 0.9
CYCLES = 600
DUTY = 0.4
RUN_KW = 9.0
RESET_EVERY = 37
OUTDOORS = (-15.0, -10.0, -5.0, -2.0, 5.0, 8.0, 12.0)

PROBE = r'''
import ast
import asyncio
import math
import sys
from datetime import timedelta
sys.path[:0] = [sys.argv[1] + "/tests/hastub", sys.argv[1] + "/custom_components"]
from heatpump_optimizer import coordinator as cm
from heatpump_optimizer import flow_lift
from heatpump_optimizer.accuracy import MeasuredCop
from heatpump_optimizer.defrost import DefrostWindow
from heatpump_optimizer.pump_signals import PumpSignals
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from homeassistant.util import dt as dt_util

try:
    from heatpump_optimizer import heat_energy
except ImportError:
    heat_energy = None
Coord = cm.HeatPumpOptimizerCoordinator
TRUE_K, CYCLES, DUTY, RUN_KW, RESET_EVERY = (
    float(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]))
OUTDOORS = ast.literal_eval(sys.argv[7])
CADENCE_H = 0.5
T0 = dt_util.now()


class Gate:
    _learn_measured_cop = Coord._learn_measured_cop
    _fold_measured_cop = Coord._fold_measured_cop
    _commanded_power = Coord._commanded_power
    _commanded_split = Coord._commanded_split
    _cop_reference_curve = Coord._cop_reference_curve
    _COP_CURVE_SHARE = Coord._COP_CURVE_SHARE
    _apply_cop_scale = Coord._apply_cop_scale
    if hasattr(Coord, "_fold_cop_evidence"):
        _fold_cop_evidence = Coord._fold_cop_evidence

    def __init__(self, outdoor):
        self._measured_power = None
        self._current_action = {}
        self._pump_signals = PumpSignals()
        self._defrost_window = DefrostWindow()
        self._thermal_params = ThermalParameters()
        self._thermal_model = ThermalModel(self._thermal_params)
        self._current_state = ThermalState(room_temperature=21.0, outdoor_temperature=outdoor)
        self._cop_scale = 1.0
        self._cop_samples = 0
        self._cop_ratio_ewma = None
        self._measured_cop = MeasuredCop()
        self._immersion_active = False
        self._flow_bias = flow_lift.FlowCurveBias()
        self._last_house_sample = None
        self._last_house_sample_time = None

    def _learning_frozen(self, *keys, room_air=True):
        return None

    def _observe_cop_health(self, observed_cop, dhw_curve=False):
        return None

    def _fold_capacity_envelope(self, observed_cop, heat_kw=None):
        return None

    async def _async_learn_house_heat_loss(self, interval, span_heat_kw=None):
        return True

    async def _async_learn_lower_floor_loss(self, interval, span_heat_kw=None):
        return True


def walk(arm):
    law = ThermalModel(ThermalParameters())
    out, folds = {}, 0
    for outdoor in OUTDOORS:
        gate = Gate(outdoor)
        supply = 50.0 - 0.8 * outdoor
        true_cop = TRUE_K * law.compute_cop_dhw(outdoor, supply)
        avg_heat = DUTY * RUN_KW
        avg_elec = avg_heat / true_cop
        heat_cum = elec_cum = 0.0
        counter = arm in ("counter", "reset", "integer") and heat_energy is not None
        for i in range(CYCLES):
            at = T0 + timedelta(hours=CADENCE_H * i)
            gate._current_action = {"power": avg_heat / gate._thermal_model.compute_cop(outdoor)}
            gate._measured_power = avg_elec
            on_now = math.floor((i + 1) * DUTY) > math.floor(i * DUTY)
            point = None if arm == "commanded" else (RUN_KW if on_now else 0.0)
            gate._flow_bias.observe_temps(supply, supply - 5.0, heat_output_kw=None if counter else point)
            if counter:
                if arm == "reset" and i and i % RESET_EVERY == 0:
                    heat_cum = 0.0
                read = math.floor(heat_cum + 1e-9) if arm == "integer" else heat_cum
                heat_energy.meter_of(gate).observe_counters(
                    at, 1000.0 + read if arm != "reset" else read, 500.0 + elec_cum, configured=True,
                    cadence_h=CADENCE_H,
                    bounds_h=(cm.HOUSE_LOSS_MIN_SAMPLE_HOURS, cm.HOUSE_LOSS_MAX_SAMPLE_HOURS),
                    max_heat_kw=30.0,
                )
            gate._last_house_sample, gate._last_house_sample_time = gate._current_state, at
            before = gate._cop_samples
            gate._learn_measured_cop()
            if counter:
                clean = {"cop": gate._measured_cop.refusal == cm.COP_REFUSED_SPAN_OPEN}
                asyncio.run(cm._async_learn_heat_span(gate, clean))
            folds += gate._cop_samples - before
            heat_cum += avg_heat * CADENCE_H
            elec_cum += avg_elec * CADENCE_H
        out[outdoor] = gate._cop_scale
    return out, folds


print("TREE_HAS_COUNTER", heat_energy is not None)


def eps_row(kw, eps, cycles=400):
    """An integer-kWh counter at ``kw`` on a 30 min cadence: (spans, kept, mean kW, sd)."""
    saved, heat_energy.HEAT_RESOLUTION_EPS = heat_energy.HEAT_RESOLUTION_EPS, eps
    try:
        meter, heat, spans = heat_energy.HeatEnergyMeter(), 0.0, []
        for i in range(cycles):
            meter.observe_counters(
                T0 + timedelta(hours=CADENCE_H * i), 1000.0 + math.floor(heat + 1e-9), None, configured=True,
                cadence_h=CADENCE_H, bounds_h=(cm.HOUSE_LOSS_MIN_SAMPLE_HOURS, cm.HOUSE_LOSS_MAX_SAMPLE_HOURS),
                max_heat_kw=30.0,
            )
            if meter.closed is not None:
                spans.append(meter.closed)
            heat += kw * CADENCE_H
        kept = [sp for sp in spans if heat_energy.resolution_refusal(sp, kw * sp.hours) is None]
        rates = [sp.heat_kwh / sp.hours for sp in kept]
        mean = sum(sp.heat_kwh for sp in kept) / sum(sp.hours for sp in kept) if kept else float("nan")
        sd = (sum((r - mean) ** 2 for r in rates) / len(rates)) ** 0.5 if rates else float("nan")
        hours = sorted({round(sp.hours, 3) for sp in spans})
        return len(spans), len(kept), round(mean, 4), round(sd, 3), hours
    finally:
        heat_energy.HEAT_RESOLUTION_EPS = saved


# The dr3-eps-at-span re-measure: the resolution bound at the real span (a
# 30 min cadence closes one-hour spans). The shipped bound and the design's
# 0.5 side by side; 0.5 refusing 1.5 kW is the reason for the deviation.
if heat_energy is not None:
    for eps in (heat_energy.HEAT_RESOLUTION_EPS, 0.5):
        for kw in (0.6, 1.5, 2.2, 3.0):
            print("EPS %r kW %r spans=%d kept=%d mean=%r sd=%r hours=%r" % (eps, kw, *eps_row(kw, eps)))

# Carry (#2698, kept by mandate): "clamp means reset" is orthogonal to the
# earned basis. The void path zeroes both learners' samples before it takes
# ``house_loss_confidence``, so ``reanchor_heat_loss`` runs at (0, 0), where
# both clamp branches (``if a and not``, ``if b and not``) are skipped. The
# grid spans stored scales and ratios far past their bounds, both nameplate
# moves, one zone and two.
from heatpump_optimizer import thermal_model as tm
conf0 = (cm.house_loss_confidence(0), cm.house_loss_confidence(0))
bounds = dict(scale_bounds=(cm.HOUSE_HEAT_LOSS_SCALE_MIN, cm.HOUSE_HEAT_LOSS_SCALE_MAX),
              ratio_bounds=(cm.LOWER_FLOOR_LOSS_RATIO_MIN, cm.LOWER_FLOOR_LOSS_RATIO_MAX))


def clamp_grid(conf):
    grid = resets = 0
    far = 0.0
    for scale in (0.05, 0.3, 1.0, 3.0, 20.0):
        for ratio in (0.05, 1.0, 20.0):
            for then, now in (((0.2, 0.1), (0.1, 0.3)), ((0.2, 0.0), (0.4, 0.0)), ((0.1, 0.1), (0.3, 0.02))):
                got = tm.reanchor_heat_loss(then, now, scale, ratio, conf, **bounds)
                grid += 1
                resets += got[2] or got[3]
                far = max(far, abs(got[0] - 1.0), abs(got[1] - 1.0) if now[1] > 0 else 0.0)
    return grid, resets, far


# Null control: the same grid at a converged learner's confidence does reset,
# so the clamp branches are live and the zero above is the void's doing.
conf_full = (cm.house_loss_confidence(10 ** 6), cm.house_loss_confidence(10 ** 6))
print("CLAMP void confidence=%r grid=%d resets=%d max|value-1|=%r" % (conf0, *clamp_grid(conf0)))
print("CLAMP null confidence=%r grid=%d resets=%d" % (conf_full, *clamp_grid(conf_full)[:2]))
for arm in ("point", "counter", "commanded", "reset", "integer"):
    scales, folds = walk(arm)
    spread = max(scales.values()) - min(scales.values())
    print("ARM", arm, "spread=%.4f" % spread, "folds=%d" % folds,
          " ".join("%g=%r" % kv for kv in scales.items()))
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
    out = Path(tempfile.mkdtemp(prefix="r10hm-"))
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
    args = [str(TRUE_K), str(CYCLES), str(DUTY), str(RUN_KW), str(RESET_EVERY), repr(OUTDOORS)]
    rc = 0
    base_tree = _tree_from(base, root)
    for label, tree in (("head " + head[:12], root), ("base " + base[:12], base_tree)):
        run = subprocess.run(
            [sys.executable, "-I", "-c", PROBE, str(tree), *args],
            capture_output=True, text=True, env={**os.environ, "PYTHONHASHSEED": "0"},
        )
        print("TREE", label, "rc=%d" % run.returncode)
        sys.stdout.write(run.stdout)
        if run.returncode:
            sys.stdout.write(run.stderr[-2000:])
            rc = 1
    shutil.rmtree(base_tree, ignore_errors=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
