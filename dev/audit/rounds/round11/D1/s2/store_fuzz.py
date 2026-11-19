"""D1-s2 round 11, D1.M2: store-corruption fuzz over every d1-stores line.

Metric (one line): per store, of N seeded structural mutants of the healthy
payload loaded through the real loaders on a real asyncio loop, how many
(a) raise out of a cycle, (b) leave a spawned task raising, (c) fail a
best-effort cycle step on BOTH cycle 1 and cycle 2 (the failure repeats), or
(d) add more than one WARNING+ log template over the healthy control.
Count key: the cycle's own outcome (``HeatPumpOptimizerCoordinator._async_update_data``
raising / returning), the coordinator's ``_best_effort_cycle_step`` fence, and the
records the ``heatpump_optimizer`` loggers emit -- never an input attribute.

Command:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/s2/store_fuzz.py [--stores a,b] [--n 200] [--seed 11] [--control] [--real-solve K]
Expected: printed RESULT lines; controls: healthy payload -> 0 everywhere;
--control (positive control) -> cycle_fail>=1 and repeat_fence>=1.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export). Machine: macOS arm64, shared box.

Mutation operators (seeded random.Random(seed ^ hash(store))): type swap of a
leaf, delete a key, NaN/inf/-inf token (orjson refuses -> doc dropped),
the strings "NaN"/"inf", negative and huge (1e14, below store.ABSURD) numbers,
wrap in list / dict (wrong nesting), replace a dict/list by a string,
null, empty container, truncate a list, truncate the JSON text,
top-level non-dict, bool where a number goes, far-past / far-future ISO
instant where a string instant goes.

The solve is memoised (d1s2_lib): first real, later reused; --real-solve K
re-runs K seeded mutants per store with a real in-process solve each cycle.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1s2_lib as L  # noqa: E402  (sets the thread pin first)

import argparse  # noqa: E402
import asyncio  # noqa: E402
import copy  # noqa: E402
import json  # noqa: E402
import logging  # noqa: E402
import random  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402

import finite_boundary as FB  # noqa: E402  (tests/; healthy payloads + LOADERS)

logging.disable(logging.NOTSET)
L._pkg_log.addHandler(L.CAP)

KEYPFX = f"{L.const.DOMAIN}_{L.ENTRY_ID}_"
CONSTRUCTOR_LOADED = {"thermal_learning", "price_model", "ledger", "accuracy", "energy",
                      "manual_plan", "snapshots", "dhw_profile", "dhw_draws",
                      "dhw_legionella", "boost", "away"}
LATE = ("notifier", "debug", "pump_duty", "duty_switch", "off_restore")


def _iso(h):
    from datetime import timedelta
    return (L.T0 + timedelta(hours=h)).isoformat()


#: finite_boundary's seeds leave these three empty (no boost, no plan, away
#: off), so a fuzz over them corrupts nothing (round-10 C1). Populated with a
#: running hold each, in the shape their savers write (boost._store_payload,
#: ManualOverride.to_dict, away._override_payload).
POPULATED = {
    "boost": {"dhw": {"until": _iso(2)}, "block_space": {"until": _iso(1)},
              "space_settle": {"until": _iso(3), "boosted_h": 1.5}},
    "manual_plan": {"space_slots": [{"start": _iso(1), "end": _iso(3)}, {"start": _iso(5), "end": _iso(6)}],
                    "dhw_slots": [], "expires_at": _iso(12), "created_at": _iso(-1)},
    "away": {"active": True, "return_time": _iso(24), "migrated_helpers": True},
}


def healthy():
    L.dtu.freeze(L.T0)
    try:
        L.storage_stub._VERSIONS.clear()
        disk = FB._healthy_payloads()
        vers = dict(L.storage_stub._VERSIONS)
    finally:
        L.dtu.freeze(None)
    out = {}
    for key, payload in disk.items():
        name = key[len(KEYPFX):] if key.startswith(KEYPFX) else key
        out[name] = (key, POPULATED.get(name, payload), vers.get(key, 1))
    return out


def paths(obj, path=()):
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from paths(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from paths(v, path + (i,))


def setp(root, path, value):
    if not path:
        return value
    cur = root
    for s in path[:-1]:
        cur = cur[s]
    cur[path[-1]] = value
    return root


def delp(root, path):
    cur = root
    for s in path[:-1]:
        cur = cur[s]
    if isinstance(cur, dict):
        del cur[path[-1]]
    else:
        cur.pop(path[-1])
    return root


OPS = ["type_swap", "delete", "nan_token", "inf_token", "str_nan", "str_inf", "negative",
       "huge", "wrap_list", "wrap_dict", "str_for_container", "null", "empty", "truncate_list",
       "truncate_text", "top_level", "bool", "instant_far"]


def mutate(rng, payload):
    """Return (op, path, json_text) for one seeded mutant."""
    op = rng.choice(OPS)
    data = copy.deepcopy(payload)
    allp = [p for p, _ in paths(data) if p]
    if not allp:
        allp = [()]
    path = rng.choice(allp)
    cur = data
    for s in path:
        cur = cur[s]
    if op == "type_swap":
        new = (str(cur) if isinstance(cur, (int, float)) and not isinstance(cur, bool)
               else (12.5 if isinstance(cur, str) else ([cur] if isinstance(cur, dict) else {"x": cur})))
        data = setp(data, path, new)
    elif op == "delete" and path:
        data = delp(data, path)
    elif op in ("nan_token", "inf_token"):
        data = setp(data, path, float("nan") if op == "nan_token" else float("inf"))
    elif op == "str_nan":
        data = setp(data, path, "NaN")
    elif op == "str_inf":
        data = setp(data, path, "-Infinity")
    elif op == "negative":
        data = setp(data, path, -abs(cur) - 1.0 if isinstance(cur, (int, float)) and not isinstance(cur, bool) else -1.0)
    elif op == "huge":
        data = setp(data, path, rng.choice([1e14, -1e14, 2**53, 1e12]))
    elif op == "wrap_list":
        data = setp(data, path, [cur])
    elif op == "wrap_dict":
        data = setp(data, path, {"v": cur})
    elif op == "str_for_container":
        data = setp(data, path, "garbage")
    elif op == "null":
        data = setp(data, path, None)
    elif op == "empty":
        data = setp(data, path, {} if isinstance(cur, dict) else [] if isinstance(cur, list) else "")
    elif op == "truncate_list":
        lists = [p for p, v in paths(data) if isinstance(v, list) and v]
        if lists:
            path = rng.choice(lists)
            cur = data
            for s in path:
                cur = cur[s]
            del cur[rng.randrange(len(cur)):]
    elif op == "truncate_text":
        text = json.dumps(data)
        return op, path, text[: rng.randrange(1, max(2, len(text)))]
    elif op == "top_level":
        data = rng.choice([[], "x", 3, [data]])
        path = ()
    elif op == "bool":
        data = setp(data, path, True)
    elif op == "instant_far":
        data = setp(data, path, rng.choice(["1970-01-01T00:00:00+00:00", "2999-01-01T00:00:00+00:00",
                                            "2026-01-20T12:00:00", "not-a-date-but-long-enough"]))
    return op, path, json.dumps(data)


async def scenario(name, key, text, version, *, control=False):
    """Load ``text`` as store ``name`` through the real loaders, run two cycles."""
    L.storage_stub._DISK.clear()
    L.storage_stub._VERSIONS.clear()
    if text is not None:
        L.storage_stub._DISK[key] = text
        L.storage_stub._VERSIONS[key] = version
    out = {"load_exc": [], "c1": None, "c2": None, "tasks": [], "w_load": [], "w_c1": [], "w_c2": [],
           "fence_c1": [], "fence_c2": []}
    hass = L.SchedHass(L.base_states())
    m0 = L.mark()
    coord = L.HeatPumpOptimizerCoordinator(hass, L.FakeEntry(data=L.base_config()))
    out["tasks"] += await L.drain(hass)
    for late in LATE:
        try:
            await FB.LOADERS[late](coord)
        except Exception as e:  # noqa: BLE001
            out["load_exc"].append(f"{late}: {type(e).__name__}: {e}")
    out["tasks"] += await L.drain(hass)
    out["w_load"] = [L.template(r) for r in L.since(m0)]
    L.price_stub(coord)
    if control:  # positive control: a cycle-path step and the payload build fail
        coord._record_accuracy = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("control"))
        real = coord._build_data_dict
        calls = {"n": 0}

        def boom(*a, **k):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("control build failure")
            return real(*a, **k)
        coord._build_data_dict = boom
    for cyc in ("c1", "c2"):
        m = L.mark()
        f0 = len(L.FENCED)
        try:
            d = await coord._async_update_data()
            out[cyc] = "ok" if isinstance(d, dict) else f"bad payload {type(d).__name__}"
        except Exception as e:  # noqa: BLE001
            out[cyc] = f"{type(e).__name__}: {str(e)[:160]}"
        out["tasks"] += await L.drain(hass)
        out["w_" + cyc] = [L.template(r) for r in L.since(m)]
        out["fence_" + cyc] = L.FENCED[f0:]
        L.dtu.freeze(L.T0 + timedelta_minutes(15))
    L.dtu.freeze(L.T0)
    try:
        out["nf_model"] = FB._scan_model(coord)
        out["nf_pub"] = FB._scan_published(coord)
    except Exception as e:  # noqa: BLE001
        out["nf_model"] = [f"scan raised {e!r}"]
        out["nf_pub"] = []
    try:
        await coord.async_shutdown()
    except Exception:  # noqa: BLE001
        pass
    await L.drain(hass, 5)
    return out


def timedelta_minutes(m):
    from datetime import timedelta
    return timedelta(minutes=m)


def run_one(name, key, text, version, real_solve=False, control=False):
    L.reset_globals()
    ps = L.patches(real_solve)
    for p in ps:
        p.start()
    L.dtu.freeze(L.T0)
    try:
        return asyncio.run(scenario(name, key, text, version, control=control))
    finally:
        L.dtu.freeze(None)
        for p in ps:
            p.stop()


def classify(res, ctrl):
    """Defect kinds for one mutant against the healthy control ``ctrl``."""
    kinds = []
    if res["load_exc"]:
        kinds.append("loader_raise")
    if res["c1"] != "ok" or res["c2"] != "ok":
        kinds.append("cycle_fail")
    if res["tasks"]:
        kinds.append("task_raise")
    f1 = {f.split(" :: ")[0] for f in res["fence_c1"]} - {f.split(" :: ")[0] for f in ctrl["fence_c1"]}
    f2 = {f.split(" :: ")[0] for f in res["fence_c2"]} - {f.split(" :: ")[0] for f in ctrl["fence_c2"]}
    if f1 & f2:
        kinds.append("repeat_fence")
    base = set(ctrl["w_load"]) | set(ctrl["w_c1"]) | set(ctrl["w_c2"])
    extra = (set(res["w_load"]) | set(res["w_c1"])) - base
    if len(extra) > 1:
        kinds.append("log_multi")
    rep = (set(res["w_c2"]) - base) & (set(res["w_c1"]) | set(res["w_load"]))
    if rep and "c2" not in str(rep) and any(t.startswith(("ERROR", "WARNING")) for t in rep):
        kinds.append("log_repeat")
    if res.get("nf_model") or res.get("nf_pub"):
        kinds.append("nonfinite_live")
    return kinds, sorted(extra)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stores", default="")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--real-solve", type=int, default=0)
    ap.add_argument("--dump", default="")
    a = ap.parse_args()
    proc0, thr0 = time.process_time(), time.thread_time()
    H = healthy()
    names = [s for s in a.stores.split(",") if s] or sorted(H)
    missing = [s for s in names if s not in H]
    print(f"RESULT healthy_stores={len(H)} count  (missing={missing})")
    totals = {}
    dump = {}
    for name in names:
        key, payload, version = H[name]
        ctrl = run_one(name, key, json.dumps(payload), version)
        nul = run_one(name, key, None, version)
        ck, _ = classify(ctrl, nul)
        print(f"CTRL {name}: healthy c1={ctrl['c1']} c2={ctrl['c2']} tasks={len(ctrl['tasks'])} "
              f"fences={len(ctrl['fence_c1'])}/{len(ctrl['fence_c2'])} kinds_vs_empty={ck}")
        if a.control:
            pc = run_one(name, key, json.dumps(payload), version, control=True)
            kinds, _ = classify(pc, ctrl)
            print(f"RESULT control_{name}_kinds={','.join(kinds) or 'none'}")
            continue
        rng = random.Random(a.seed ^ zlib.crc32(name.encode()))
        counts = {}
        examples = {}
        for i in range(a.n):
            op, path, text = mutate(rng, payload)
            res = run_one(name, key, text, version, real_solve=(i < a.real_solve))
            kinds, extra = classify(res, ctrl)
            for k in kinds:
                counts[k] = counts.get(k, 0) + 1
                examples.setdefault(k, []).append({"i": i, "op": op, "path": list(map(str, path)),
                                                   "c1": res["c1"], "c2": res["c2"], "tasks": res["tasks"][:2],
                                                   "load_exc": res["load_exc"][:2],
                                                   "fence": (res["fence_c1"] + res["fence_c2"])[:3],
                                                   "extra": extra[:4], "text": text[:300],
                                                   "nf": (res.get("nf_model", []) + res.get("nf_pub", []))[:3]})
        totals[name] = counts
        dump[name] = examples
        print(f"RESULT {name}_mutants={a.n} count")
        for k in ("loader_raise", "cycle_fail", "task_raise", "repeat_fence", "log_multi", "log_repeat", "nonfinite_live"):
            print(f"RESULT {name}_{k}={counts.get(k, 0)} count")
        for k, ex in examples.items():
            e = ex[0]
            print(f"  EX {name}/{k}: op={e['op']} path={e['path']} c1={e['c1']!s:.120} tasks={e['tasks']} "
                  f"load_exc={e['load_exc']} fence={e['fence']} extra={e['extra']} nf={e.get('nf')}")
    if a.dump:
        with open(a.dump, "w") as fh:
            json.dump({"totals": totals, "examples": dump}, fh, indent=1, default=str)
    print(f"RESULT thread_factor={L.thread_factor(proc0, thr0):.3f}")
    print(f"RESULT load1={L.load_avg():.2f}")
    print(f"RESULT swapins={L.swapins()}")


if __name__ == "__main__":
    main()
