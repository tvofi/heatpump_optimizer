"""Round 5 D1 seat-a: non-finite store corruption reaching the real solve.

WHAT IT MEASURES (metric definition, one line): with the healthy payloads
the production writers wrote, one corrupt value seeded per run (NaN in the
DHW profile's ``hourly_profile``, infinity in the accuracy store's peak
tracker ``window_sum``, infinity in the draw-stats ``open_kwh``), loaded
through the real loaders on a real loop, then ONE REAL solve cycle (the
real optimizer, real process worker -- nothing stubbed), the harness
counts NaN leaf paths in the published ``coordinator.data`` payload after
cycle 1 and cycle 2, checks whether the corrupt value is still in the
store after the cycles (persistence), and re-runs scenario A with a
one-line in-memory quarantine patch (``np.isfinite`` gate in
``DhwProfileLearner.normalize_profile``) under which the NaN count must
drop to zero.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round5/D1/seat-a/nonfinite_drill.py

EXPECTED at baseline 1cc89e020fff9040a9d0090a27bf22bc1dd497f0 (Apple M1,
CPython 3.11, measured 2026-09-20):
  healthy_nan_cycle1=0 (null control)
  dhw_profile_nan_nan_cycle1=220, cycle2=220 (all 24 dhw_usage_profile
  entries NaN, repeated: the next cycle does not repair)
  dhw_profile_nan_store_after still contains the seeded NaN (persistence)
  quarantined_nan_cycle1=0 (the in-memory isfinite gate moves 220 -> 0)
  tariff_healthy_threshold_cycle1=4.1 (finite; the corrupt-peak scenarios
  leave the 4-peak-averaged threshold finite, so no disarm claim is made)
  perturbation_moved_number=True

Timings are provisional (shared box); counts are final. The solve runs in
a real child process and a real executor thread, so thread_factor is the
residual (process_cpu - deliberate_thread_cpu)/thread_cpu.
"""
from __future__ import annotations

import asyncio
import json
import math
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import d1a_lib as L  # noqa: E402

from homeassistant.util import dt as dt_util  # noqa: E402

import store_fuzz as SF  # noqa: E402

EID = SF.EID  # build_healthy writes under this entry id


def result(name, value, unit=""):
    line = f"RESULT {name}={value}"
    if unit and unit not in line:
        line += f" {unit}"
    print(line, flush=True)


def nan_paths(value, out, path="data"):
    if isinstance(value, float) and math.isnan(value):
        out.append(path)
    elif isinstance(value, dict):
        for k, v in value.items():
            nan_paths(v, out, f"{path}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            nan_paths(v, out, f"{path}[{i}]")


async def run_scenario(healthy, corrupt_key, corrupt_doc, storage_mod,
                       coord_mod, tag, config=None):
    """Load one corrupt store, run two REAL cycles, report."""
    from harness import FakeEntry

    storage_mod._DISK.clear()
    for k, v in healthy.items():
        storage_mod._DISK[k] = json.dumps(v)
    storage_mod._DISK[corrupt_key] = json.dumps(corrupt_doc)

    hass = L.LoopHass()
    L.seed_states(hass)
    entry = FakeEntry(data=dict(config or L.base_config(EID)), entry_id=EID)
    hass.bind_loop(asyncio.get_running_loop())
    coord = coord_mod.HeatPumpOptimizerCoordinator(hass, entry)
    loaders = [t for t in hass.tasks if not t.done()]
    if loaders:
        await asyncio.wait(loaders, timeout=60)

    out = {}
    for cycle in (1, 2):
        try:
            payload = await coord._async_update_data()
            paths: list[str] = []
            nan_paths(payload or {}, paths, f"c{cycle}")
            out[f"nan_cycle{cycle}"] = len(paths)
            out[f"nan_paths_cycle{cycle}"] = paths[:6]
            thr = (payload or {}).get("peak_threshold_kw", "absent")
            out[f"threshold_cycle{cycle}"] = thr
        except Exception as err:  # UpdateFailed counts as a failed cycle
            out[f"nan_cycle{cycle}"] = -1
            out[f"exc_cycle{cycle}"] = repr(err)[:100]
    # Did the cycles rewrite the corrupt store, and with what?
    doc_after = json.loads(storage_mod._DISK.get(corrupt_key, "null"))
    out["store_after"] = doc_after
    await coord.async_shutdown()
    await hass.shutdown_executor()
    for k, v in out.items():
        if k.startswith("nan_paths") or k == "exc_cycle2":
            continue
        if k == "store_after":
            result(f"{tag}_store_after", json.dumps(doc_after)[:160])
        else:
            result(f"{tag}_{k}", v)
    if out.get("nan_paths_cycle1"):
        result(f"{tag}_nan_paths_cycle1", "|".join(out["nan_paths_cycle1"][:4]))
    if out.get("exc_cycle2"):
        result(f"{tag}_exc_cycle2", out["exc_cycle2"])
    return out


async def main() -> int:
    dt_util.freeze(L.START)
    import importlib

    coord_mod = importlib.import_module("heatpump_optimizer.coordinator")
    from homeassistant.helpers import storage as storage_mod

    healthy = await SF.build_healthy(coord_mod)

    # Null control: healthy stores, real solve.
    good = await run_scenario(
        healthy, f"heatpump_optimizer_{EID}_dhw_profile",
        healthy[f"heatpump_optimizer_{EID}_dhw_profile"],
        storage_mod, coord_mod, "healthy",
    )

    # Scenario A: NaN inside the stored DHW hourly profile.
    prof = json.loads(json.dumps(healthy[f"heatpump_optimizer_{EID}_dhw_profile"]))
    prof["hourly_profile"][6] = float("nan")
    a = await run_scenario(
        healthy, f"heatpump_optimizer_{EID}_dhw_profile", prof,
        storage_mod, coord_mod, "dhw_profile_nan",
    )

    # Scenario B: infinity in the accuracy store's peak tracker.
    acc = json.loads(json.dumps(healthy[f"heatpump_optimizer_{EID}_accuracy"]))
    acc["peaks"]["window_sum"] = float("inf")
    b = await run_scenario(
        healthy, f"heatpump_optimizer_{EID}_accuracy", acc,
        storage_mod, coord_mod, "peak_inf",
    )

    # Scenario C: infinity as the draw stats' open occurrence energy.
    draws = json.loads(json.dumps(healthy[f"heatpump_optimizer_{EID}_dhw_draws"]))
    draws["open_kwh"] = float("inf")
    draws["open_label"] = "06:00-08:30"
    draws["open_date"] = L.START.date().isoformat()
    c = await run_scenario(
        healthy, f"heatpump_optimizer_{EID}_dhw_draws", draws,
        storage_mod, coord_mod, "draws_inf",
    )

    # Perturbation: the one-line quarantine (in memory), scenario A re-run.
    from heatpump_optimizer.dhw_learning import DhwProfileLearner

    orig_normalize = DhwProfileLearner.normalize_profile

    def quarantining_normalize(self, profile):
        import numpy as np

        default = self._params.dhw_hourly_draw_pattern.copy()
        if len(profile) != 24:
            return default
        try:
            if not all(
                isinstance(v, (int, float))
                and np.isfinite(np.float64(v))
                for v in profile
            ):
                return default  # quarantine: non-finite -> reset, one branch
            cleaned = [
                float(np.clip(v, 0.05, 4.0)) for v in profile
            ]
            avg = float(np.mean(cleaned))
        except (TypeError, ValueError):
            return default
        if avg <= 0:
            return default
        return [
            float(np.clip(v / avg, 0.05, 4.0)) for v in cleaned
        ]

    DhwProfileLearner.normalize_profile = quarantining_normalize
    try:
        q = await run_scenario(
            healthy, f"heatpump_optimizer_{EID}_dhw_profile", prof,
            storage_mod, coord_mod, "quarantined",
        )
    finally:
        DhwProfileLearner.normalize_profile = orig_normalize

    # Scenario D: an infinite recorded peak, capacity tariff enabled. The
    # published peak_threshold_kw is the money seam: healthy -> finite
    # (the tariff shapes load), corrupt -> inf (the term is disarmed).
    tariff_cfg = dict(L.base_config(EID))
    tariff_cfg.update(
        {"peak_tariff_enabled": True, "peak_tariff_price_per_kw": 45.0}
    )
    acc_key = f"heatpump_optimizer_{EID}_accuracy"
    acc_peaks = json.loads(json.dumps(healthy[acc_key]))
    acc_peaks["peaks"]["month"] = L.START.strftime("%Y-%m")
    acc_peaks["peaks"]["peaks"] = [5.2, 4.8, 4.1]
    d0 = await run_scenario(
        healthy, acc_key, acc_peaks, storage_mod, coord_mod,
        "tariff_healthy", config=tariff_cfg,
    )
    acc_inf = json.loads(json.dumps(acc_peaks))
    acc_inf["peaks"]["peaks"][0] = float("inf")
    d1 = await run_scenario(
        healthy, acc_key, acc_inf, storage_mod, coord_mod,
        "tariff_inf_peak", config=tariff_cfg,
    )

    # Perturbation for scenario D: isfinite gate in PeakTracker.from_dict.
    from heatpump_optimizer.tariff import PeakTracker

    orig_peak = PeakTracker.from_dict.__func__

    @classmethod
    def _gated_peak(cls, data):
        tracker = orig_peak(cls, data)
        tracker.peaks = [p for p in tracker.peaks if math.isfinite(p)]
        return tracker

    PeakTracker.from_dict = _gated_peak
    try:
        d2 = await run_scenario(
            healthy, acc_key, acc_inf, storage_mod, coord_mod,
            "tariff_inf_quarantined", config=tariff_cfg,
        )
    finally:
        PeakTracker.from_dict = orig_peak

    conds = L.box_conditions()
    result("load1", conds["load1"])
    result("concurrent_test_processes", conds["concurrent_test_processes"])
    moved = (
        isinstance(a.get("nan_cycle1"), int)
        and a.get("nan_cycle1", 0) > 0
        and q.get("nan_cycle1") == 0
    )
    result("perturbation_moved_number", moved)
    th0 = d0.get("threshold_cycle1")
    th1 = d1.get("threshold_cycle1")
    th2 = d2.get("threshold_cycle1")
    result(
        "tariff_disarmed_by_corruption",
        bool(isinstance(th0, float) and math.isfinite(th0)
             and isinstance(th1, float) and math.isinf(th1)
             and isinstance(th2, float) and math.isfinite(th2)),
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
