#!/usr/bin/env python3
# Metric: (weekday days, weekday quarter days) learned by one PriceShapeLearner.fold, rows as pull_prices' ingress delivers them vs raw
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g31/probes/probe_6743e8b3d654cd32.py
# EXPECTED RESULT ingress_cases_differ=0 count (of 5)  (exact: counts; tolerance 0)
# EXPECTED RESULT direct_cases_differ=3 count (of 5): a non-finite quarter makes the hour mean nan and the day is not learned (1 -> 0)  (exact: counts; tolerance 0)
# EXPECTED RESULT nonfinite_rows_after_tibber_ingress=0  (exact: counts; tolerance 0)
# EXPECTED RESULT nonfinite_rows_after_entity_ingress=0  (exact: counts; tolerance 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g31 (Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:_entries_by_day (via hourly_from_entries -> PriceShapeLearner.fold) (price_model.py line 586).
# Perturbation: `if not np.isfinite(value):` -> `if False:` applied in memory (the function recompiled from its own source, attached
#   with mock.patch.object for the mutant arm); the gate's tree is never edited. Direction: none through ingress; days learned 1 -> 0 on raw rows only.
# Null control: an all-finite quarter day: (1,1) both arms.
# Count key: the value the production symbol returns (or the learner state it writes), never an input attribute.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap, time, warnings
_T0 = (time.process_time(), time.thread_time())
from unittest import mock


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
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import price_model as pm  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)


def mutant(func, line, old, new):
    """``func`` recompiled from its own source with file line ``line`` mutated (in memory only)."""
    lines, start = inspect.getsourcelines(func)
    i = line - start
    assert lines[i].rstrip("\n") == old, f"anchor line {line} moved: {lines[i]!r}"
    lines[i] = new + "\n"
    src = textwrap.dedent("".join(lines))
    ns = dict(pm.__dict__)
    exec(compile(src, pm.__file__, "exec"), ns)
    return ns[func.__name__]


def same(a, b):
    """Exact equality that treats nan == nan and compares arrays and exceptions."""
    if isinstance(a, BaseException) or isinstance(b, BaseException):
        return type(a) is type(b)
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.array_equal(np.asarray(a), np.asarray(b), equal_nan=True)
    if isinstance(a, float) and isinstance(b, float):
        return (a == b) or (np.isnan(a) and np.isnan(b))
    return a == b


def call(fn, *args, **kw):
    try:
        return fn(*args, **kw)
    except Exception as err:  # the mutant may raise where the baseline does not
        return err


LINE, OLD, NEW = 586, "        if not np.isfinite(value):", "        if False:"
MUT = mutant(pm._entries_by_day, LINE, OLD, NEW)
DAY = "2026-01-14"  # a Wednesday


def quarter_rows(bad=None, hourly=False):
    """One complete local day of rows; ``bad`` = (hour, minute, value) replaces one total."""
    rows = []
    for h in range(24):
        for mnt in ((0,) if hourly else (0, 15, 30, 45)):
            v = 0.4 + 0.05 * h + 0.01 * mnt / 15
            if bad and bad[0] == h and bad[1] == mnt:
                v = bad[2]
            rows.append({"total": v, "starts_at": f"{DAY}T{h:02d}:{mnt:02d}:00+01:00"})
    return rows


def learned(rows):
    """(weekday days learned, weekday quarter days learned) after one PriceShapeLearner.fold."""
    lr = pm.PriceShapeLearner()
    lr.fold(rows)
    return lr.model.days[pm.PROFILE_WEEKDAY], lr.model.quarter_days[pm.PROFILE_WEEKDAY]


def arms(rows):
    b = learned(rows)
    with mock.patch.object(pm, "_entries_by_day", MUT):
        m = learned(rows)
    return b, m


def tibber(rows):
    """The rows as pull_prices' Tibber ingress delivers them (prices_from_tibber_payload)."""
    payload = {"data": {"viewer": {"homes": [{"currentSubscription": {"priceInfo": {
        "today": [{"total": r["total"], "startsAt": r["starts_at"], "level": "NORMAL"} for r in rows],
        "tomorrow": []}}}]}}}
    out = pm.prices_from_tibber_payload(payload)
    return out if isinstance(out, list) else []


cases = {
    "quarter_nan_at_17:30": quarter_rows((17, 30, float("nan"))),
    "quarter_inf_at_03:15": quarter_rows((3, 15, float("inf"))),
    "quarter_-inf_at_00:00": quarter_rows((0, 0, -float("inf"))),
    "hourly_nan_at_17": quarter_rows((17, 0, float("nan")), hourly=True),
    "quarter_all_finite(null)": quarter_rows(),
}
prod_diff = direct_diff = 0
for name, rows in cases.items():
    b, m = arms(rows)
    pb, pmut = arms(tibber(rows))
    direct_diff += int(b != m)
    prod_diff += int(pb != pmut)
    print(f"RESULT direct_{name} learned(days,quarter_days) baseline={b} mutant={m}")
    print(f"RESULT ingress_{name} learned(days,quarter_days) baseline={pb} mutant={pmut}")
nonfinite_after_ingress = sum(not np.isfinite(r["total"]) for rows in cases.values() for r in tibber(rows))
ent = pm.apply_price_adjustments([{"total": float("nan"), "starts_at": f"{DAY}T00:00:00+01:00"}], 1.25, 0.1)
print(f"RESULT direct_cases_differ={direct_diff} count (of {len(cases)})")
print(f"RESULT ingress_cases_differ={prod_diff} count (of {len(cases)})")
print(f"RESULT nonfinite_rows_after_tibber_ingress={nonfinite_after_ingress} count")
print(f"RESULT nonfinite_rows_after_entity_ingress={len(ent)} count")


_cpu, _thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
print(f"RESULT thread_factor={_cpu / _thr if _thr > 0 else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    _sw = next(int(x.split()[1]) for x in open("/proc/vmstat") if x.startswith("pswpin "))
except (OSError, StopIteration):
    _sw = 0
print(f"RESULT swapins={_sw}")
