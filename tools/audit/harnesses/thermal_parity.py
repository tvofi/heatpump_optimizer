"""Thermal-model parity across two trees, with two-zone and the wood tank on.

Metric, one line: the number of thermal_model output arrays that differ
bitwise between two trees over one fixed grid, and, inside each tree, the
number of scalar-vs-batch row pairs that are not bitwise equal (the batch
twin's contract, `simulate_trajectory_batch`'s docstring).

Why it is kept: round-9 reviewers of thermal_model refactors (R9-EG-A2) built
this twice in seat scratch (`mypar2.py`, `parity2.py`, `compare.py`), and a
temp cleanup deleted both copies. A refactor that claims "no behaviour change"
is answered by it: capture at the base, capture at the head, compare.

The grid: two_zone x wood tank x mixing valve (None, manual, smart_read) x
weather (given, none) x three parameter draws, one of them a stiff slab, 96
steps at 0.25 h; per cell the batch path over four schedules, each schedule
through the scalar path, the DHW path, and the stability sub-step count over
twenty wind/precipitation draws. Every random draw is seeded.

    # from the root of each tree under test, with that tree's own hastub:
    PYTHONPATH=tests/hastub python3 tools/audit/harnesses/thermal_parity.py capture <out.npz>
    PYTHONPATH=tests/hastub python3 tools/audit/harnesses/thermal_parity.py capture <ctl.npz> --perturb
    python3 tools/audit/harnesses/thermal_parity.py compare <base.npz> <head.npz> [<ctl.npz>]

Copy this file into the tree under test (tools/audit/README.md: a harness
measures the tree it is run from only if it resolves the root from the cwd,
which this one does -- it imports `custom_components` from sys.path[0] = cwd).

Perturbation (the harness's own null control): `--perturb` scales
`ThermalParameters.inter_zone_transfer` by (1 + 2**-40) in memory after the
draws, a one-ulp-scale change that only the two-zone cells read. Against an
unperturbed capture of the same tree it must report differing > 0, every one
a two-zone key; against a second unperturbed capture, differing = 0.

Expected at origin/main 12dbd3a5 on the M1 (numpy 2.4.6, python 3.14.7):
  capture: RESULT arrays=2880, effective_configs=12
  compare of two plain captures: base_head_differing=0, scalar_batch_unequal_pairs=0 of 1872
  compare with --perturb as the control: control_differing=1200, control_differing_not_two_zone=0
  the unequal-pairs count's own control: one batch room cell moved one ulp in a copy of a
  capture reads base_head_differing=1 and head_scalar_batch_unequal_pairs=1
"""

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import itertools  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

N = 96
SCALAR_STORE = {0: "room", 1: "slab", 2: "upper", 3: "lower", 4: "buffer", 5: "refused", 6: "wood"}


def capture(out: str, perturb: bool) -> None:
    sys.path.insert(0, os.getcwd())
    from custom_components.heatpump_optimizer.thermal_model import (
        ThermalModel, ThermalParameters, ThermalState)
    res, eff = {}, set()
    rng = np.random.default_rng(11)
    c0, t0 = time.process_time(), time.thread_time()
    for two_zone, wood, valve, wx, cfgi in itertools.product(
            (False, True), (False, True), (None, "manual", "smart_read"), ("given", "none"), range(3)):
        p = ThermalParameters.from_config({})
        p.two_zone_enabled = two_zone
        p.wood_tank_configured = wood
        if wood:
            p.wood_tank_volume = 1500.0
        if valve:
            p.mixing_valve_mode = valve
        p._layout_cache = None
        eff.add((p.two_zone_enabled, p.wood_tank_configured, p.mixing_valve_mode, p.two_tank_modelled))
        r = np.random.default_rng(cfgi)
        p.inter_zone_transfer *= r.uniform(0.5, 2)
        p.slab_heat_transfer *= r.uniform(0.5, 2)
        p.upper_floor_thermal_mass *= r.uniform(0.3, 2)
        p.room_thermal_mass *= r.uniform(0.3, 2)
        if cfgi == 2:
            p.slab_thermal_mass = 0.1
            p.slab_heat_transfer = 5.0
        if perturb:
            p.inter_zone_transfer *= 1 + 2.0 ** -40
        m = ThermalModel(p)
        powers = rng.uniform(0, 3.0, size=(4, N))
        ot = rng.uniform(-15, 10, N)
        if wx == "given":
            wi, ra, so = rng.uniform(0, 12, N), rng.uniform(0, 2, N), rng.uniform(0, 600, N)
        else:
            wi = ra = so = None
        ext = rng.uniform(0, 2, N)
        hum = np.full(N, 78.0)
        st = ThermalState(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=float(ot[0]),
                          upper_floor_temperature=21.2, lower_floor_temperature=20.1, buffer_tank_temperature=48.0,
                          wood_tank_temperature=52.0 if wood else None)
        key = f"{int(two_zone)}{int(wood)}{valve}{wx}{cfgi}"
        for k, v in m.simulate_trajectory_batch(st, powers, ot, wi, ra, so, 0.25, ext, None, hum, 7.0).items():
            if isinstance(v, np.ndarray):
                res[f"{key}_batch_{k}"] = v
        for i in range(powers.shape[0]):
            for j, a in enumerate(m.simulate_trajectory(st, powers[i], ot, wi, ra, so, 0.25, ext, None, hum, 7.0)):
                if isinstance(a, np.ndarray):
                    res[f"{key}_scalar{i}_{j}"] = a
        for j, a in enumerate(m.simulate_trajectory_with_dhw(
                st, powers[0], powers[1] * 0.5, ot, wi, ra, so, start_hour=7.0, dt_hours=0.25,
                external_heat_kw=ext, humidity=hum)):
            if isinstance(a, np.ndarray):
                res[f"{key}_dhw_{j}"] = a
        sub = getattr(m, "_substeps_and_loss", None)
        res[f"{key}_subs"] = np.array([
            sub(float(x), float(y), 0.25)[0] if sub else m._stability_substeps(float(x), float(y), 0.25)
            for x, y in zip(rng.uniform(0, 12, 20), rng.uniform(0, 2, 20))])
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    np.savez(out, **res)
    print(f"RESULT arrays={len(res)}")
    print(f"RESULT effective_configs={len(eff)}")
    print(f"RESULT perturbed={int(perturb)}")
    _tail(tf)


def _diff(x, y) -> list[str]:
    return sorted(k for k in x.files if not (x[k].shape == y[k].shape and np.array_equal(x[k], y[k], equal_nan=True)))


def compare(base: str, head: str, ctl: str | None) -> int:
    a, b = np.load(base), np.load(head)
    if set(a.files) != set(b.files):
        print(f"REFUSE key sets differ: only base {sorted(set(a.files) - set(b.files))[:5]}, "
              f"only head {sorted(set(b.files) - set(a.files))[:5]}")
        return 2
    d = _diff(a, b)
    print(f"RESULT arrays={len(a.files)}")
    print(f"RESULT base_head_differing={len(d)}")
    for k in d[:10]:
        print(f"  differs: {k}")
    if ctl:
        m = np.load(ctl)
        dm = _diff(b, m)
        print(f"RESULT control_differing={len(dm)}")
        print(f"RESULT control_differing_not_two_zone={sum(not k.startswith('1') for k in dm)}")
    for name, z in (("base", a), ("head", b)):
        unequal = pairs = 0
        worst = 0.0
        for k in z.files:
            mm = re.match(r"(.*)_scalar(\d)_(\d)$", k)
            store = mm and SCALAR_STORE.get(int(mm.group(3)))
            if not store or f"{mm.group(1)}_batch_{store}" not in z.files:
                continue
            row, s = z[f"{mm.group(1)}_batch_{store}"][int(mm.group(2))], z[k]
            pairs += 1
            if not np.array_equal(row, s, equal_nan=True):
                unequal += 1
                worst = max(worst, float(np.nanmax(np.abs(row - s))))
        print(f"RESULT {name}_scalar_batch_pairs={pairs}")
        print(f"RESULT {name}_scalar_batch_unequal_pairs={unequal} max_abs={worst:g}")
    return 0


def _tail(tf: float) -> None:
    print(f"RESULT thread_factor={tf:.3f}")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=unavailable")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["capture"] and len(args) in (2, 3):
        capture(args[1], "--perturb" in args[2:])
    elif args[:1] == ["compare"] and len(args) in (3, 4):
        sys.exit(compare(args[1], args[2], args[3] if len(args) == 4 else None))
    else:
        print(__doc__)
        sys.exit(2)
