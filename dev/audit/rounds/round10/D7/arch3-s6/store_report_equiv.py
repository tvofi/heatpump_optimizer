#!/usr/bin/env python3
"""ARCH3-s6 (round 10, D7): the store's public report rules answer as the copies they replace.

P3 replaces three copies of "a field is declared and inside its declaration" (store.admitted,
store._log_off_domain, debugger.store_report), two of "the store key names this DOMAINS entry"
(store._store_name, tools/replay/debug_ingest.domain_suffix) and two of "the next load would scrub
this document" (debugger: json-equality of _sanitize; debug_ingest: != of _sanitize) with
store.off_domain / store.store_name / store.quarantines. This differential drives the OLD
expressions (re-stated verbatim below from origin/main d749c986d) and the NEW functions over the
same inputs and counts disagreements.

Metric:   mismatches = number of (input, rule) pairs where old and new answers differ.
Corpus:   every DOMAINS entry's key under a real-shaped store key and a foreign key; per entry a
          clean document built from its own declarations' bounds, plus N random JSON-shaped
          documents with poisoned leaves (nan, +-inf, 1e300, 2**64), poisoned keys, out-of-domain
          numbers, unknown keys and nested lists (seeded).
Command:  PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round10/D7/arch3-s6/store_report_equiv.py [--n N] [--perturb]
Perturbation: --perturb swaps the new quarantines() for one that ignores poisoned KEYS (drops the
          `_poisoned(k)` filter); mismatches must rise above 0 (direction up), proving the corpus
          reaches the rule. Null control: the unperturbed run must read mismatches=0.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import time

sys.path[:0] = ["tests/hastub", "custom_components"]

from heatpump_optimizer import store  # noqa: E402

DOMAIN = "heatpump_optimizer"


def _wire(v):  # debugger._wire's role in json.dumps(default=...): stringify the unknown
    return str(v)


def old_dumps(v):
    return json.dumps(v, default=_wire)


def old_name(key, domains):
    hits = [s for s in domains if key.endswith("_" + s)]
    return max(hits, key=len) if hits else None


def old_off(key, data):
    return list(dict.fromkeys(
        "/".join(map(str, path))
        for path, _k, domain, value in store.stored_fields(old_name(key, store.DOMAINS) or "", data)
        if domain is None or not store.in_domain(domain, value)
    ))


def old_log_off(key, data):
    name = old_name(key, store.DOMAINS)
    return [
        "/".join(map(str, path)) for path, _k, domain, value in store.stored_fields(name or "", data)
        if domain is None or not store.in_domain(domain, value)
    ] if name else []


def old_admitted(name, payload):
    return all(d is not None and store.in_domain(d, v) for _p, _k, d, v in store.stored_fields(name, payload))


POISON = [float("nan"), float("inf"), -float("inf"), 1e300, 2 ** 64, 1e15]
PLAIN = [0, 1, -3, 0.5, 21.0, 1e14, "x", "2026-01-01T00:00:00+00:00", True, None]


def rnd_value(r, depth=0):
    roll = r.random()
    if depth < 3 and roll < 0.25:
        return {rnd_key(r): rnd_value(r, depth + 1) for _ in range(r.randint(0, 4))}
    if depth < 3 and roll < 0.40:
        return [rnd_value(r, depth + 1) for _ in range(r.randint(0, 4))]
    return r.choice(POISON) if roll < 0.55 else r.choice(PLAIN)


def rnd_key(r):
    return r.choice(["a", "b", "rate", "1000000000000000", "nan", "1e300", "0", "k"])


def main(argv):
    t_cpu, t_thr = time.process_time(), time.thread_time()
    n = int(argv[argv.index("--n") + 1]) if "--n" in argv else 400
    quarantines = store.quarantines
    if "--perturb" in argv:
        def quarantines(payload):  # noqa: F811 - the perturbed rule
            def scrub(v):
                if isinstance(v, dict):
                    return {k: scrub(x) for k, x in v.items()}
                if isinstance(v, list):
                    return [scrub(x) for x in v]
                return None if store._poisoned(v) else v
            return scrub(payload) != payload
    r = random.Random(20261015)
    keys = [f"{DOMAIN}_entry_1_{name}" for name in store.DOMAINS] + [
        "not_a_store", f"{DOMAIN}_foreign_nope", f"{DOMAIN}_x_price_model_accuracy"]
    docs = []
    for name in store.DOMAINS:
        docs.append({k: 1.0 for k in store.DOMAINS[name] if isinstance(k, str) and "*" not in k})
    docs += [{rnd_key(r): rnd_value(r) for _ in range(r.randint(1, 6))} for _ in range(n)]
    # a poisoned map key, explicitly (json would refuse it as a key; a dict in memory carries it)
    docs.append({float("nan"): 1.0, "a": 1.0})
    docs.append({1e15: 1.0})
    mismatch, pairs = 0, 0
    for key in keys:
        for doc in docs:
            pairs += 4
            mismatch += old_off(key, doc) != list(dict.fromkeys(store.off_domain(key, doc)))
            mismatch += old_log_off(key, doc) != (store.off_domain(key, doc) if store.store_name(key) else [])
            mismatch += old_name(key, store.DOMAINS) != store.store_name(key)
            q_old = old_dumps(store._sanitize(doc)) != old_dumps(doc)
            mismatch += q_old != quarantines(doc)
    for name in store.DOMAINS:
        for doc in docs:
            pairs += 1
            mismatch += old_admitted(name, doc) != store.admitted(name, doc)
    print(f"RESULT pairs={pairs} count")
    print(f"RESULT mismatches={mismatch} count")
    cpu, thr = time.process_time() - t_cpu, time.thread_time() - t_thr
    print(f"RESULT thread_factor={cpu / thr if thr else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
