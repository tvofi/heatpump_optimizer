"""Probes for arm A's beyond-finding seams: a learned multiplier with no anchor
survives an options edit of the nameplate it was fitted against.

Property: after an options edit of nameplate X -> Y with a learned multiplier s
stored (fitted against X), the reloaded effective product must equal the
learned X*s (the #86 re-anchor law the house scale obeys). An unanchored
multiplier gives Y*s instead.

Arms:
  cop      heat_pump_cop_nominal 3.5 -> 4.2, stored cop_scale 0.8.
  aperture window_area 10 -> 15, stored solar_aperture scale 1.6 (n above the
           sample floor so the scale is in force).
  house    (guarded control) heat-loss nameplates x1.5, stored house scale 1.4:
           the re-anchor must hold the effective UA.

Run (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P3/probe_anchor.py [--null]
--null: the edit is a no-op (Y = X); every arm must print rel_err 0.
A probe FAILS (exit 1) when rel_err > 1e-3 on cop or aperture; house must pass.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import copy  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
from profiles import house  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.const import SOLAR_APERTURE_MIN_SAMPLES  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402


class MemStore:
    def __init__(self, data=None):
        self.data = copy.deepcopy(data)

    async def async_load(self):
        return copy.deepcopy(self.data)

    async def async_save(self, data):
        self.data = copy.deepcopy(data)

    async def async_wait_for_read(self):
        return None


def coordinator(cfg, store=None):
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    c._thermal_learning_store = store or MemStore({})
    return c


def rel(a, b):
    return abs(b / a - 1.0)


async def reload(cfg_a, cfg_b, mutate):
    a = coordinator(cfg_a)
    mutate(a)
    store = MemStore(a._thermal_learning_payload())
    b = coordinator(cfg_b, store)
    await b._async_load_thermal_learning()
    return a, b


async def main(null):
    cfg = house(two_zone=False, dhw=False)
    fails = 0

    k = 1.0 if null else 1.2
    cfg_b = dict(cfg, heat_pump_cop_nominal=cfg.get("heat_pump_cop_nominal", 3.5) * k)

    def set_cop(c):
        c._apply_cop_scale(0.8)
    a, b = await reload(cfg, cfg_b, set_cop)
    ea = a._thermal_params.cop_nominal * a._cop_scale
    eb = b._thermal_params.cop_nominal * b._cop_scale
    e = rel(ea, eb)
    fails += e > 1e-3
    print(f"RESULT cop rel_err={e:.4f} (learned {ea:.3f}, after edit {eb:.3f}; scale {b._cop_scale:.3f})")

    k = 1.0 if null else 1.5
    cfg_b = dict(cfg, window_area=cfg.get("window_area", 10.0) * k)

    def set_ap(c):
        c._solar_aperture.update(n=float(SOLAR_APERTURE_MIN_SAMPLES + 5), scale=1.6)
    a, b = await reload(cfg, cfg_b, set_ap)
    ea = a._thermal_params.window_area * a._solar_aperture["scale"]
    eb = b._thermal_params.window_area * b._solar_aperture["scale"]
    e = rel(ea, eb)
    fails += e > 1e-3
    print(f"RESULT aperture rel_err={e:.4f} (learned {ea:.3f}, after edit {eb:.3f}; scale {b._solar_aperture['scale']:.3f})")

    k = 1.0 if null else 1.25
    base_u = coordinator(cfg)._thermal_params.heat_loss_coefficient
    cfg_b = dict(cfg, house_heat_loss_coefficient=base_u * k)

    def set_house(c):
        c._apply_house_heat_loss_scale(1.4)
        c._house_heat_loss_samples = 200
    a, b = await reload(cfg, cfg_b, set_house)
    ea = coord_mod._effective_house_heat_loss(a._thermal_params, a._house_heat_loss_scale)
    eb = coord_mod._effective_house_heat_loss(b._thermal_params, b._house_heat_loss_scale)
    e = rel(ea, eb)
    print(f"RESULT house_control rel_err={e:.4f} (learned {ea:.4f}, after edit {eb:.4f}; scale {b._house_heat_loss_scale:.3f}) -- guarded, must be ~0")
    print(f"RESULT failing_probes={int(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true")
    sys.exit(asyncio.run(main(ap.parse_args().null)))
