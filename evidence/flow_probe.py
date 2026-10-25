"""R10-RATIO-ANCHOR (#2239): per-zone heat loss after a reload that re-anchors.

The finder's harness (tools/audit/round10/study-reseed/reparam_sites.py on
study/r10-reseed at 2c42ba4a0, sections 6 and 7) stopped running against
main when learner_newton_step lost its max_step_fraction keyword; this keeps
those two arms, on the same owner-shaped state (scale 1.567, ratio 1.922,
310/147 samples) and the stock two-zone house, and adds the G-ID-3 arm.

Metric: |effective / learned - 1| per zone, effective = what the real
coordinator applies after ``_async_load_thermal_learning`` (or
``_apply_learner_payloads``) over a store the coordinator itself wrote.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_ratio_anchor.py [--scale S] [--ratio R]

Arms:
  reseed_both     both nameplates set to the learned values (U*s, L*r*s)
  reseed_split    both nameplates scaled alike (U*s, L*s): the split kept
  snapshot        a pre-reseed snapshot restored onto reseed_both's config
  meter_add       the same nameplates, a power meter added: RESULT prints
                  the scale, ratio and samples the load leaves
  scale_reset     the fix review's rows (verdict/2698 at 1132f8777): an edit
                  whose joint solve puts the scale outside its bounds.
                  lower_rel_err is the lower zone against the same edit over
                  a store whose scale never learned and whose ratio holds the
                  same lower-zone measurement (ratio s*r); rows whose s*r is
                  outside the ratio bounds have no such store and print the
                  state the load leaves
Perturbation: --ratio 1.0 -- with no learned split every zone row reads 0
    on any tree (the defect needs a ratio to misattribute).
Null control: --scale 1.0 --ratio 1.0: the nameplates are already right,
    every zone row reads 0 and meter_add's learners are already at 1.0.
    scale_reset's rows are fixed and ignore both flags; its in-bounds row
    (s 1.2, r 1.1, edit x1.1, x0.9) resets nothing on any tree.
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import logging
import os
import sys
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


ROOT = repo_root(__file__)
os.chdir(ROOT)
sys.path[:0] = [str(ROOT / "tests" / "hastub"), str(ROOT / "tests"), str(ROOT / "custom_components")]
logging.disable(logging.CRITICAL)

from harness import FakeEntry, FakeHass  # noqa: E402
from profiles import house  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402


class MemStore:
    """In-memory stand-in for homeassistant.helpers.storage.Store."""

    def __init__(self, data=None):
        self.data = copy.deepcopy(data)

    async def async_load(self):
        return copy.deepcopy(self.data)

    async def async_save(self, data):
        self.data = copy.deepcopy(data)

    async def async_wait_for_read(self):
        return None


def coordinator(cfg, store):
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    c._thermal_learning_store = store
    return c


def zones(c):
    p, s = c._thermal_params, c._house_heat_loss_scale
    return p.upper_floor_heat_loss * s, p.lower_floor_heat_loss * c._lower_floor_loss_ratio * s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.567)
    ap.add_argument("--ratio", type=float, default=1.922)
    a = ap.parse_args()
    s, r = a.scale, a.ratio
    cfg = dict(house(two_zone=True, dhw=False), lower_floor_temp_entity="sensor.lower_floor")
    U, L = cfg["upper_floor_heat_loss"], cfg["lower_floor_heat_loss"]
    src = coordinator(cfg, MemStore({}))
    src._apply_house_heat_loss_scale(s)
    src._apply_lower_floor_loss_ratio(r)
    src._house_heat_loss_samples, src._lower_floor_loss_samples = 310, 147
    asyncio.run(src._async_save_thermal_learning())
    stored = src._thermal_learning_store.data
    learned = (U * s, L * r * s)
    both = dict(cfg, upper_floor_heat_loss=U * s, lower_floor_heat_loss=L * r * s)
    split = dict(cfg, upper_floor_heat_loss=U * s, lower_floor_heat_loss=L * s)
    print(f"scale={s} ratio={r} U={U} L={L}")

    def report(label, c):
        got = zones(c)
        for zone, g, w in zip(("upper", "lower"), got, learned):
            print(f"RESULT {label}.{zone}_rel_err={abs(g / w - 1.0):.4f}  ({g * 1000:.1f} vs learned {w * 1000:.1f} W/K)")

    for label, ccfg in (("reseed_both", both), ("reseed_split", split)):
        c = coordinator(ccfg, MemStore(stored))
        asyncio.run(c._async_load_thermal_learning())
        report(label, c)

    c = coordinator(both, MemStore(stored))
    asyncio.run(c._async_load_thermal_learning())
    c._apply_house_heat_loss_scale(1.0)
    c._apply_lower_floor_loss_ratio(1.0)
    c._apply_learner_payloads({"thermal_learning": copy.deepcopy(stored)})
    report("snapshot", c)

    from heatpump_optimizer.thermal_model import probe_install, heat_loss_basis
    fcfg = dict(cfg, flow_meter_entity="sensor.flow")
    cap = probe_install(fcfg)
    print(f"RESULT flow_add.probe measured_power={cap.measured_power} frequency={cap.frequency} basis_before={heat_loss_basis(cfg)} basis_after={heat_loss_basis(fcfg)}")
    c = coordinator(fcfg, MemStore(stored))
    asyncio.run(c._async_load_thermal_learning())
    print(f"RESULT flow_add.scale={c._house_heat_loss_scale:.4f} ratio={c._lower_floor_loss_ratio:.4f} "
          f"samples={c._house_heat_loss_samples}/{c._lower_floor_loss_samples}")
    c = coordinator(dict(cfg, heat_pump_power_entity="sensor.hp_power"), MemStore(stored))
    asyncio.run(c._async_load_thermal_learning())
    print(f"RESULT meter_add.scale={c._house_heat_loss_scale:.4f} ratio={c._lower_floor_loss_ratio:.4f} "
          f"samples={c._house_heat_loss_samples}/{c._lower_floor_loss_samples}")

    def load(ss, rr, samples, fu, fl):
        src = coordinator(cfg, MemStore({}))
        src._apply_house_heat_loss_scale(ss)
        src._apply_lower_floor_loss_ratio(rr)
        src._house_heat_loss_samples, src._lower_floor_loss_samples = samples
        asyncio.run(src._async_save_thermal_learning())
        c = coordinator(dict(cfg, upper_floor_heat_loss=U * fu, lower_floor_heat_loss=L * fl),
                        MemStore(src._thermal_learning_store.data))
        asyncio.run(c._async_load_thermal_learning())
        return c

    for ss, rr, fu, fl in ((0.5, 0.8, 1.8, 1.4), (0.4, 1.6, 1.5, 1.2), (2.0, 2.5, 0.6, 0.5),
                           (2.6, 1.3, 0.7, 0.9), (2.6, 1.3, 0.8, 0.6), (1.2, 1.1, 1.1, 0.9)):
        c = load(ss, rr, (310, 147), fu, fl)
        row = (f"scale_reset[s={ss},r={rr},edit=({fu},{fl})] scale={c._house_heat_loss_scale:.4f} "
               f"ratio={c._lower_floor_loss_ratio:.4f} samples={c._house_heat_loss_samples}/"
               f"{c._lower_floor_loss_samples}")
        if 0.3 <= ss * rr <= 3.0:
            twin, got = zones(load(1.0, ss * rr, (0, 147), fu, fl))[1], zones(c)[1]
            row += f" lower_rel_err={abs(got / twin - 1.0):.4f} ({got * 1000:.1f} vs {twin * 1000:.1f} W/K)"
        print("RESULT " + row)


if __name__ == "__main__":
    main()
