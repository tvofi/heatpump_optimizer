"""D1-s2 round 11, D1.M2: the d1-stores `upgrade` lines LEDGER v1->2 and defrost STORE_VERSION v1->2.

Metric (one line): for each upgrade line, the healthy previous-version record
(built from this release's healthy payload by removing what the newer version
adds) loaded by this release through the real loaders and two real cycles on a
real asyncio loop -- (control) does it migrate (ledger: the old reference
basis stamped on months with a savings line; defrost: ``defrost_store_migrated``
published) -- then 200 seeded mutants of that old record, classified exactly
as store_fuzz.py classifies a store mutant (loader_raise, cycle_fail,
task_raise, repeat_fence, log_multi, log_repeat, nonfinite_live).
Count key: as store_fuzz.py.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/upgrade_fuzz.py [--n 200]
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
import random  # noqa: E402
import time  # noqa: E402

import store_fuzz as SF  # noqa: E402
from heatpump_optimizer import ledger as ledger_mod  # noqa: E402


def ledger_v1(payload):
    old = copy.deepcopy(payload)
    for month in (old.get("ledger", {}).get("months") or {}).values():
        (month.get("meta") or {}).pop(ledger_mod.REFERENCE_BASIS_META, None)
    return old


def defrost_v1(payload):
    old = copy.deepcopy(payload)
    d = old.get("defrost") or {}
    old["defrost"] = {"version": 1, "factors": d.get("factors"), "counts": d.get("counts")}
    return old


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    H = SF.healthy()
    lines = [("LEDGER_STORE_VERSION v1->2", "ledger", ledger_v1, 1, None),
             ("defrost STORE_VERSION v1->2", "thermal_learning", defrost_v1, None, "defrost")]
    for label, name, make_old, store_version, subtree in lines:
        key, payload, version = H[name]
        old = make_old(payload)
        sv = store_version or version
        ctrl = SF.run_one(name, key, json.dumps(old), sv)
        migrated = None
        if name == "ledger":
            L.reset_globals()
            months = (json.loads(json.dumps(old)).get("ledger", {}).get("months") or {})
            migrated = sum(1 for m in months.values() if "savings_baseline" in (m.get("lines") or {}))
        print(f"CTRL {label}: c1={ctrl['c1']} c2={ctrl['c2']} tasks={ctrl['tasks']} fences={ctrl['fence_c1']} "
              f"months_to_stamp={migrated} extra_warnings={sorted(set(ctrl['w_load']))[:3]}")
        rng = random.Random(a.seed ^ len(label))
        counts, ex = {}, {}
        for i in range(a.n):
            if subtree:
                op, path, text = SF.mutate(rng, old[subtree])
                doc = copy.deepcopy(old)
                try:
                    doc[subtree] = json.loads(text)
                except ValueError:
                    doc[subtree] = text  # a truncated sub-document arrives as a string
                text = json.dumps(doc)
                path = (subtree,) + tuple(path)
            else:
                op, path, text = SF.mutate(rng, old)
            res = SF.run_one(name, key, text, sv)
            kinds, extra = SF.classify(res, ctrl)
            for k in kinds:
                counts[k] = counts.get(k, 0) + 1
                ex.setdefault(k, (op, list(map(str, path)), res["c1"], extra[:3], res.get("nf_model", [])[:2]))
        tag = label.split()[0].lower()
        print(f"RESULT {tag}_mutants={a.n} count")
        for k in ("loader_raise", "cycle_fail", "task_raise", "repeat_fence", "log_multi", "log_repeat", "nonfinite_live"):
            print(f"RESULT {tag}_{k}={counts.get(k, 0)} count")
        for k, e in ex.items():
            print(f"  EX {tag}/{k}: {e}")
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
