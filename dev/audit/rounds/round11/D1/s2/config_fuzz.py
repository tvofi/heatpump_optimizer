"""D1-s2 round 11, D1.M2: the d1-stores `upgrade` lines of CONFIG_ENTRY_VERSION.

Metric (one line): per earlier config-entry version vN (N=1..6), of 200 seeded
mutants of a healthy all-features entry stamped vN, how many fail
``async_migrate_entry`` (False or raise), fail construction (the setup's
parse), or fail BOTH cycles of ``_async_update_data`` on a real asyncio loop
(a corrupt option turned into a permanent failure). Count key: the
production calls' own outcome.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/config_fuzz.py [--n 200] [--versions 1,2,3,4,5,6]
Expected: RESULT lines per version; healthy control vN -> migrate ok, cycles ok.
--fix (perturbation, in memory): ``async_migrate_entry`` additionally drops every
option whose JSON type is not the type the config flow writes for it (the
healthy record's), so its reader falls back to the default -> build_fail and
permanent_cycle_fail fall to 0.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402

import argparse  # noqa: E402
import asyncio  # noqa: E402
import copy  # noqa: E402
import random  # noqa: E402
import time  # noqa: E402
from datetime import timedelta  # noqa: E402

import golden  # noqa: E402  (tests/)
import heatpump_optimizer as pkg  # noqa: E402

HEALTHY = {**golden.coordinator_scenarios()["coord_all_features"], **L.base_config()}
OPS = ["str_word", "str_nan", "none", "empty", "negative", "huge", "list", "dict", "bool", "delete",
       "num_for_str", "str_of_num"]


def mutate(rng, data):
    d = copy.deepcopy(data)
    k = rng.choice(sorted(d))
    v = d[k]
    op = rng.choice(OPS)
    if op == "delete":
        del d[k]
    else:
        d[k] = {"str_word": "abc", "str_nan": "nan", "none": None, "empty": "", "list": [v], "dict": {"v": v},
                "bool": True, "num_for_str": 42.0,
                "negative": (-abs(v) - 1 if isinstance(v, (int, float)) and not isinstance(v, bool) else -1),
                "huge": 1e14, "str_of_num": str(v)}[op]
    return op, k, d


async def scenario(version, data):
    out = {"migrate": None, "build": None, "c1": None, "c2": None}
    hass = L.SchedHass(L.base_states())
    entry = L.FakeEntry(data=data)
    entry.version = version
    try:
        ok = await pkg.async_migrate_entry(hass, entry)
        out["migrate"] = "ok" if ok else "refused"
    except Exception as e:  # noqa: BLE001
        out["migrate"] = f"{type(e).__name__}: {e}"
    try:
        coord = L.HeatPumpOptimizerCoordinator(hass, entry)
        await L.drain(hass)
        out["build"] = "ok"
    except Exception as e:  # noqa: BLE001
        out["build"] = f"{type(e).__name__}: {str(e)[:120]}"
        return out
    for i, c in enumerate(("c1", "c2")):
        L.dtu.freeze(L.T0 + timedelta(minutes=15 * i))
        try:
            d = await coord._async_update_data()
            out[c] = "ok" if isinstance(d, dict) else "bad"
        except Exception as e:  # noqa: BLE001
            out[c] = f"{type(e).__name__}: {str(e)[:120]}"
        await L.drain(hass)
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    await L.drain(hass, 5)
    return out


FIX = {"on": False}


def _kind(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "num"
    return type(v).__name__


def fixed_migrate(real):
    async def migrate(hass, entry):
        ok = await real(hass, entry)
        for k in list(entry.data):
            if k in HEALTHY and _kind(entry.data[k]) != _kind(HEALTHY[k]):
                del entry.data[k]
        return ok
    return migrate


def run(version, data):
    L.reset_globals()
    ps = L.patches() + L.price_patches()
    if FIX["on"]:
        ps.append(L.mock.patch.object(pkg, "async_migrate_entry", fixed_migrate(pkg.async_migrate_entry)))
    for p in ps:
        p.start()
    L.dtu.freeze(L.T0)
    try:
        return asyncio.run(scenario(version, data))
    finally:
        L.dtu.freeze(None)
        for p in ps:
            p.stop()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--versions", default="1,2,3,4,5,6")
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--fix", action="store_true")
    a = ap.parse_args()
    FIX["on"] = a.fix
    proc0, thr0 = time.process_time(), time.thread_time()
    for v in [int(x) for x in a.versions.split(",")]:
        ctrl = run(v, copy.deepcopy(HEALTHY))
        print(f"CTRL v{v}: {ctrl}")
        rng = random.Random(a.seed * 100 + v)
        counts, ex = {}, {}
        for _ in range(a.n):
            op, k, d = mutate(rng, HEALTHY)
            res = run(v, d)
            kinds = []
            if res["migrate"] != "ok":
                kinds.append("migrate_fail")
            if res["build"] != "ok":
                kinds.append("build_fail")
            elif res["c1"] != "ok" and res["c2"] != "ok":
                kinds.append("permanent_cycle_fail")
            elif res["c1"] != "ok" or res["c2"] != "ok":
                kinds.append("one_cycle_fail")
            for kk in kinds:
                counts[kk] = counts.get(kk, 0) + 1
                ex.setdefault(kk, []).append((op, k, res))
        print(f"RESULT v{v}_mutants={a.n} count")
        for kk in ("migrate_fail", "build_fail", "permanent_cycle_fail", "one_cycle_fail"):
            print(f"RESULT v{v}_{kk}={counts.get(kk, 0)} count")
        for kk, e in ex.items():
            seen = set()
            for op, k, res in e:
                sig = (k, str(res)[:80])
                if sig in seen or len(seen) >= 6:
                    continue
                seen.add(sig)
                print(f"  EX v{v}/{kk}: op={op} key={k} {res}")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
