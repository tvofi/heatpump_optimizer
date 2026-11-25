"""D1-s2 round 11, D1.M2: a NaN spelling passes the store-load boundary.

Metric (one line): over every numeric leaf of every d1-stores healthy payload,
the number of single-leaf substitutions by the string "NaN" after which,
loaded through the real loaders and one real cycle on a real asyncio loop,
(a) a non-finite value is reachable from the live model or the published
payload, or (b) a store document on disk no longer decodes (a bare NaN token
the next restart's orjson load refuses, dropping the whole document).
Count key: ``store._sanitize`` output as the loaders receive it, the live
coordinator (finite_boundary._scan_model/_scan_published) and the stub disk's
own decoder (``storage._loads``), never the substituted input.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/nan_boundary.py [--sub NaN|Infinity] [--fix]
Expected at baseline: RESULT nan_boundary_passes=1 (``_poisoned("NaN")`` is
False), RESULT leaves_reaching_* > 0 for --sub NaN; --sub Infinity (null
control, a spelling the boundary scrubs) -> 0; --fix (perturbation: in-memory
``store._poisoned`` that also refuses non-finite) -> 0.
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
import json  # noqa: E402
import math  # noqa: E402
import time  # noqa: E402
from unittest import mock  # noqa: E402

import store_fuzz as SF  # noqa: E402

FB = SF.FB


def numeric_leaves(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from numeric_leaves(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from numeric_leaves(v, path + (i,))
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield path


def undecodable():
    bad = []
    for k, text in L.storage_stub._DISK.items():
        try:
            L.storage_stub._loads(text)
        except ValueError:
            bad.append(k)
    return bad


def _fixed_poisoned(real):
    def p(value):
        if isinstance(value, str):
            try:
                f = float(value)
            except (TypeError, ValueError, OverflowError):
                return False
            return (not math.isfinite(f)) or real(value)
        if isinstance(value, float) and not math.isfinite(value):
            return True
        return real(value)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sub", default="NaN")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--stores", default="")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    H = SF.healthy()
    patch = mock.patch.object(L.store_mod, "_poisoned", _fixed_poisoned(L.store_mod._poisoned)) if a.fix else None
    if patch:
        patch.start()
    print(f"RESULT nan_boundary_passes={int(L.store_mod._sanitize({'x': 'NaN'}) == {'x': 'NaN'})} count")
    names = [s for s in a.stores.split(",") if s] or sorted(H)
    tot_leaves = tot_live = tot_disk = 0
    per = {}
    for name in names:
        key, payload, version = H[name]
        live = disk = 0
        leaves = list(numeric_leaves(payload))
        ex = []
        for path in leaves:
            data = copy.deepcopy(payload)
            SF.setp(data, path, a.sub)
            res = SF.run_one(name, key, json.dumps(data), version)
            lost = undecodable()
            hit_live = bool(res.get("nf_model") or res.get("nf_pub"))
            live += hit_live
            disk += bool(lost)
            if (hit_live or lost) and len(ex) < 3:
                ex.append(("/".join(map(str, path)), (res.get("nf_model", []) + res.get("nf_pub", []))[:2], lost))
        per[name] = (len(leaves), live, disk)
        tot_leaves += len(leaves)
        tot_live += live
        tot_disk += disk
        print(f"STORE {name}: leaves={len(leaves)} live={live} disk_undecodable={disk} ex={ex}")
    if patch:
        patch.stop()
    print(f"RESULT leaves_total={tot_leaves} count")
    print(f"RESULT leaves_reaching_live={tot_live} count")
    print(f"RESULT leaves_making_disk_undecodable={tot_disk} count")
    print(f"RESULT stores_affected={sum(1 for v in per.values() if v[1] or v[2])} count")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
