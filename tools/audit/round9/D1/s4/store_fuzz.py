#!/usr/bin/env python3
"""D1-s4 M2: seeded store-corruption fuzz of the defrost and flow-bias learners.

Metric (one line): of N seeded mutants of a healthy DefrostDerate store payload,
the count whose loaded learner still holds a duty cell outside [0, 1] (or
non-finite) after 24 healthy zero-duty folds per bucket -- a value observe_duty
can never produce and never washes out.  Count key: the value
``DefrostDerate.from_dict`` delivers into ``instance.duty`` (the production
seam), not any attribute of the mutated input.

Command:  PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D1/s4/store_fuzz.py
          [--perturb]   sanitize duty cells on load (non-finite -> 0, clip [0,1]);
                        stuck_duty must go to zero.
          [--perturb-label]  a version-2 payload is never labelled ``migrated``:
                        v2_one_bad_cell_flagged_migrated must go to zero.
Expected (baseline, exact for the seed): stuck_duty = 11 of 250 (all keys),
          duty_targeted_stuck = 53, 42 of them pinned at DERATE_MIN, all 53 silent
          (the same 250 mutation draws aimed at "duty"),
          sibling_factors_stuck = 0 (the same draws aimed at the re-clamped
          "factors" grid -- the sibling control), flow_bias_bad = 0,
          load_exceptions = 0.  --perturb: every stuck count = 0.
          v2_one_bad_cell_flagged_migrated = 226 of 250, measured buckets discarded =
          2712 (= 226 x 12: one bad cell voids all twelve buckets' measured duty).
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1  Machine: box B6 (4 CPU, 15 GiB)
Instrumented: custom_components.heatpump_optimizer.defrost:DefrostDerate.from_dict,
              DefrostDerate.observe_duty, DefrostDerate.factor;
              custom_components.heatpump_optimizer.flow_lift:FlowCurveBias.from_dict
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import copy
import logging
import math
import random
import sys
import time

sys.path.insert(0, "tests/hastub")
sys.path.insert(0, ".")

t_proc0, t_thr0 = time.process_time(), time.thread_time()

from custom_components.heatpump_optimizer import defrost as D  # noqa: E402
from custom_components.heatpump_optimizer import flow_lift as F  # noqa: E402

PERTURB = "--perturb" in sys.argv
N = 250
SEED = 9104


class _Count(logging.Handler):
    def __init__(self):
        super().__init__()
        self.n = 0

    def emit(self, record):
        self.n += 1


LOG = _Count()
logging.getLogger("custom_components.heatpump_optimizer").addHandler(LOG)
logging.getLogger("custom_components.heatpump_optimizer").setLevel(logging.DEBUG)

if PERTURB:
    _orig = D.DefrostDerate.from_dict.__func__

    def _sanitized(cls, data):
        inst = _orig(cls, data)
        inst.duty = [
            [min(1.0, max(0.0, v)) if math.isfinite(v) else 0.0 for v in row]
            for row in inst.duty
        ]
        return inst

    D.DefrostDerate.from_dict = classmethod(_sanitized)

NT, NH = len(D.TEMP_EDGES) - 1, len(D.HUMIDITY_EDGES) - 1


def healthy():
    return {
        "version": 2,
        "factors": [[0.9 for _ in range(NH)] for _ in range(NT)],
        "counts": [[15 for _ in range(NH)] for _ in range(NT)],
        "duty": [[0.05 for _ in range(NH)] for _ in range(NT)],
        "duty_counts": [[20 for _ in range(NH)] for _ in range(NT)],
        "duty_events": [[3 for _ in range(NH)] for _ in range(NT)],
    }


BAD_SCALARS = ["nan", "inf", "-inf", "NaN", "1e308", 1e300, -1e300, -5.0, 50.0,
               "abc", None, [], {}, True, 2 ** 70, "", "0x10"]
KEYS = ["factors", "counts", "duty", "duty_counts", "duty_events", "version"]


def mutate(rng, payload, target_key=None):
    op = rng.choice(["cell", "cell", "cell", "type", "drop", "nest", "trunc", "whole"])
    key = target_key or rng.choice(KEYS)
    p = copy.deepcopy(payload)
    if op == "whole":
        return rng.choice(["x", 3, [], None, [p]]), op, key
    if op == "drop":
        p.pop(key, None)
    elif op == "type":
        p[key] = rng.choice(["x", 3.0, None, {}, {"a": 1}])
    elif op == "nest" and isinstance(p.get(key), list):
        p[key][rng.randrange(NT)] = rng.choice([0.1, "row", {"r": 1}])
    elif op == "trunc" and isinstance(p.get(key), list):
        p[key] = p[key][: rng.randrange(NT)]
    elif isinstance(p.get(key), list):
        t, h = rng.randrange(NT), rng.randrange(NH)
        p[key][t][h] = rng.choice(BAD_SCALARS)
    return p, op, key


def centres():
    return [(tc, hc) for tc in D.TEMP_CENTERS for hc in D.HUMIDITY_CENTERS]


def run_defrost(target_key=None):
    rng = random.Random(SEED if target_key is None else SEED + 1)  # same stream for factors and duty
    exc = stuck = pinned_min = silent = 0
    for _ in range(N):
        mut, op, key = mutate(rng, healthy(), target_key)
        before = LOG.n
        try:
            inst = D.DefrostDerate.from_dict(mut)
            for tc, hc in centres():
                f = inst.factor(tc, hc)
                assert math.isfinite(f)
            for _cycle in range(24):  # the "next cycles": healthy zero-duty folds
                for tc, hc in centres():
                    inst.observe_duty(tc, hc, 0.0, 0)
                    inst.observe(tc, hc, 1.0)
        except Exception:  # noqa: BLE001
            exc += 1
            continue
        grid = inst.factors if target_key == "factors" else inst.duty
        hi = D.DERATE_MAX if target_key == "factors" else 1.0
        lo = D.DERATE_MIN if target_key == "factors" else 0.0
        bad = any(not math.isfinite(v) or v > hi or v < lo for row in grid for v in row)
        if bad:
            stuck += 1
            if LOG.n == before:
                silent += 1
            if any(abs(inst.factor(tc, hc) - D.DERATE_MIN) < 1e-12 for tc, hc in centres()):
                pinned_min += 1
    return exc, stuck, pinned_min, silent


def run_flow():
    rng = random.Random(SEED + 2)
    bad = exc = 0
    base = {"bias_k": 1.2, "samples": 40}
    for _ in range(N):
        p = copy.deepcopy(base)
        op = rng.choice(["cell", "drop", "whole", "type"])
        k = rng.choice(["bias_k", "samples"])
        if op == "cell":
            p[k] = rng.choice(BAD_SCALARS)
        elif op == "drop":
            p.pop(k)
        elif op == "type":
            p[k] = rng.choice([{}, [1], "x"])
        else:
            p = rng.choice(["x", 3, None, [p]])
        try:
            fb = F.FlowCurveBias.from_dict(p)
            fb.observe(45.0, 44.0)
        except Exception:  # noqa: BLE001
            exc += 1
            continue
        if (not math.isfinite(fb.bias_k) or abs(fb.bias_k) > F.FLOW_BIAS_CLAMP_K
                or fb.samples < 0):
            bad += 1
    return exc, bad


exc, stuck, pinned, silent = run_defrost()
fexc, fstuck, _fp, _fs = run_defrost("factors")
dexc, dstuck, dpinned, dsilent = run_defrost("duty")
hexc, hstuck, _hp, _hs = 0, 0, 0, 0
inst = D.DefrostDerate.from_dict(healthy())  # null control: the healthy payload
if any(not math.isfinite(v) or v > 1 or v < 0 for r in inst.duty for v in r):
    hstuck = 1
flexc, flbad = run_flow()


def run_mislabel():
    """v2 payloads (version=2, factors intact) whose measured half one bad cell voids:
    how many come back flagged ``migrated`` -- the pre-v5.3.0 upgrade label, logged as such --
    and how many measured buckets that discards."""
    rng = random.Random(SEED + 3)
    flagged = discarded_buckets = 0
    for _ in range(N):
        p = healthy()
        key = rng.choice(["duty", "duty_counts"])
        t, h = rng.randrange(NT), rng.randrange(NH)
        p[key][t][h] = rng.choice(["abc", None, [], {}, "nan-ish", "1e5"])
        inst = D.DefrostDerate.from_dict(p)
        if MISLABEL_FIX and inst.migrated and p.get("version") == 2:
            inst.migrated = False
        if inst.migrated:
            flagged += 1
        discarded_buckets += sum(1 for row in inst.duty_counts for c in row if c == 0)
    return flagged, discarded_buckets


MISLABEL_FIX = "--perturb-label" in sys.argv
mis_flagged, mis_discarded = run_mislabel()

# The NaN cell in one bucket, spelled out: what the plan multiplies by.
one = healthy()
one["duty"][2][1] = "nan"
nan_inst = D.DefrostDerate.from_dict(one)
tc, hc = D.TEMP_CENTERS[2], D.HUMIDITY_CENTERS[1]
for _ in range(200):
    nan_inst.observe_duty(tc, hc, 0.0, 0)
healthy_inst = D.DefrostDerate.from_dict(healthy())
for _ in range(200):
    healthy_inst.observe_duty(tc, hc, 0.0, 0)

print(f"MODE perturb={PERTURB} perturb_label={MISLABEL_FIX} N={N} seed={SEED}")
print(f"RESULT load_exceptions={exc} count")
print(f"RESULT stuck_duty={stuck} count")
print(f"RESULT stuck_duty_pinned_at_derate_min={pinned} count")
print(f"RESULT stuck_duty_silent={silent} count")
print(f"RESULT duty_targeted_stuck={dstuck} count")
print(f"RESULT duty_targeted_pinned_at_derate_min={dpinned} count")
print(f"RESULT duty_targeted_silent={dsilent} count")
print(f"RESULT sibling_factors_stuck={fstuck} count")
print(f"RESULT sibling_factors_load_exceptions={fexc} count")
print(f"RESULT healthy_null_control_stuck={hstuck} count")
print(f"RESULT flow_bias_load_exceptions={flexc} count")
print(f"RESULT flow_bias_bad={flbad} count")
print(f"RESULT v2_one_bad_cell_flagged_migrated={mis_flagged} count")
print(f"RESULT v2_one_bad_cell_measured_buckets_discarded={mis_discarded} count")
print(f"RESULT nan_bucket_factor_after_200_zero_folds={nan_inst.factor(tc, hc):.4f} ratio")
print(f"RESULT healthy_bucket_factor_after_200_zero_folds={healthy_inst.factor(tc, hc):.4f} ratio")
pc, tcpu = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tcpu if tcpu else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = 0
    with open("/proc/vmstat") as fh:
        for line in fh:
            if line.startswith("pswpin"):
                sw = int(line.split()[1])
    print(f"RESULT swapins={sw}")
except OSError:
    print("RESULT swapins=unknown")
