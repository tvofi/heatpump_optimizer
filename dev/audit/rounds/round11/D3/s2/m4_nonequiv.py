#!/usr/bin/env python3
"""D3-s2 D3.M4: is a surviving mutant behaviourally distinct (non-equivalent)?

Metric: per probed survivor, 1 when the production symbol's output on the
named probe input differs between the baseline line and the mutated line
(the mutation applied in memory to a fresh copy of the module source), else 0.
Count key: the value the production symbol RETURNS (or the exception it
raises) on the probe -- never an input attribute.
Instrumented symbols:
  custom_components/heatpump_optimizer/inputs.py:setpoint_step / async_write_setpoint path (_on_step)
  custom_components/heatpump_optimizer/ledger.py:roll_receipts
  custom_components/heatpump_optimizer/store.py:_sanitize
  custom_components/heatpump_optimizer/sensor.py:_gap_energy_rate
  custom_components/heatpump_optimizer/accuracy.py:plan_promise
Perturbation: --identity applies each probe's mutation as old->old (a null
mutant): every RESULT distinct_<probe> must read 0 (the null control); without
it they read 1 for a non-equivalent survivor.
Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/m4_nonequiv.py [--identity]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; box B2. Expected: exact 0/1 per probe.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import importlib
import math
import sys
import time
import types
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, ".")
import harness  # noqa: E402,F401  (installs the hastub namespace)

PKG = "custom_components.heatpump_optimizer"
IDENT = "--identity" in sys.argv


def mutated(modname, old, new):
    """A copy of PKG.modname with `old` replaced by `new` exactly once."""
    base = importlib.import_module(f"{PKG}.{modname}")
    src = open(base.__file__).read()
    assert src.count(old) == 1, (modname, old, src.count(old))
    if IDENT:
        new = old
    m = types.ModuleType(f"{PKG}.{modname}", base.__doc__)
    m.__file__ = base.__file__
    m.__package__ = PKG
    exec(compile(src.replace(old, new), base.__file__, "exec"), m.__dict__)
    return base, m


def outcome(fn, *a):
    try:
        return ("ok", fn(*a))
    except Exception as exc:  # noqa: BLE001
        return ("raise", type(exc).__name__)


class _St:
    def __init__(self, attrs):
        self.attributes = attrs
        self.state = "21.0"


class _States:
    def __init__(self, m):
        self.m = m

    def get(self, e):
        return self.m.get(e)


class _H:
    def __init__(self, m):
        self.states = _States(m)


def probe_setpoint_step():
    base, mut = mutated(
        "inputs",
        "return step if step is not None and step > 0.0 else DEFAULT_SETPOINT_STEP",
        "return step if step is not None and step >= 0.0 else DEFAULT_SETPOINT_STEP")
    h = _H({"climate.hp": _St({"target_temp_step": 0.0})})

    def drive(m):
        return m._on_step(21.3, m.setpoint_step(h, "climate.hp"), "nearest")
    return outcome(drive, base), outcome(drive, mut)


def probe_roll_receipts():
    base, mut = mutated(
        "ledger",
        "for old in sorted(kept)[: max(0, len(kept) - KEEP_MONTHS)]:",
        "for old in sorted(kept)[: (0)]:")
    n = base.KEEP_MONTHS + 3
    reports = {f"20{20 + i // 12:02d}-{i % 12 + 1:02d}": {"month": "x", "lines": {}}
               for i in range(n)}
    led = types.SimpleNamespace(months={})

    def drive(m):
        kept, _ = m.roll_receipts(led, reports, "2099-01", lambda k: {})
        return len(kept)
    return outcome(drive, base), outcome(drive, mut)


def probe_sanitize():
    base, mut = mutated("store", "    if isinstance(value, tuple):", "    if False:")

    def drive(m):
        out = m._sanitize({"a": (1.0, float("nan"))})
        return repr(out)
    return outcome(drive, base), outcome(drive, mut)


def probe_gap_rate():
    base, mut = mutated("sensor", "    if rate is None or rate <= 0.0:\n        rate = _as_float(data.get(\"current_price\"))",
                        "    if rate is None or rate < 0.0:\n        rate = _as_float(data.get(\"current_price\"))")

    def drive(m):
        return m._gap_energy_rate({"recent_kwh_price": 0.0, "current_price": 1.7}, {})
    return outcome(drive, base), outcome(drive, mut)


def probe_plan_promise():
    base, mut = mutated("accuracy",
                        "    if steps < 1 or (dhw and len(dhw) < steps):",
                        "    if False:")
    t = datetime(2026, 1, 10, 22, 0, tzinfo=timezone.utc)

    def drive(m):
        # one room point: steps = min(.., len(room)-1=0, ..) = 0
        r = m.plan_promise(t, 0.25, [21.0], [1.0], [], [1.0])
        return None if r is None else sorted(r)
    return outcome(drive, base), outcome(drive, mut)


def probe_sample_from_dict():
    base, mut = mutated("accuracy", '''        raw = data.get("t")\n        if not raw:''',
                        '''        raw = data.get("t")\n        if False:''')

    def drive(m):
        return [m.AccuracySample.from_dict(d) for d in
                ({}, {"t": None}, {"t": ""}, {"t": 0}, {"t": []})]
    return outcome(drive, base), outcome(drive, mut)


def probe_take_fresh_handover():
    base, mut = mutated(
        "__init__",
        "    if payload is None or stamped_at is None:\n        return None\n    try:",
        "    if False:\n        return None\n    try:")
    from datetime import datetime as _dt

    def drive(m):
        res = []
        for pl, st in ((None, None), ({"p": 1}, None), (None, _dt.now(timezone.utc)),
                       ({"p": 1}, _dt.now(timezone.utc))):
            h = types.SimpleNamespace(data={})
            m._plan_handovers(h)["e"] = pl
            m._handover_stamps(h)["e"] = st
            res.append(m._take_fresh_handover(h, "e", 5.0))
        return res
    return outcome(drive, base), outcome(drive, mut)


def _tracker_drive(m, actual, predicted):
    t = m.AccuracyTracker()
    t0 = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
    t.note_lead_prediction(t0, 3.0, predicted)
    t.score_lead_predictions(t0 + timedelta(minutes=5), actual, window_hours=0.5)
    t.note_lead_prediction(t0 + timedelta(hours=1), 3.0, 21.0)
    t.score_lead_predictions(t0 + timedelta(hours=1, minutes=5), 21.5, window_hours=0.5)
    return repr(t.sigma(3.0)), len(t.lead_pending)


def probe_score_nan_actual():
    base, mut = mutated("accuracy",
                        "        if not np.isfinite(actual_temp):\n            return",
                        "        if False:\n            return")
    return (outcome(_tracker_drive, base, float("nan"), 21.0),
            outcome(_tracker_drive, mut, float("nan"), 21.0))


def probe_note_nan_predicted():
    base, mut = mutated("accuracy",
                        "        if not np.isfinite(predicted_temp):\n            return",
                        "        if False:\n            return")
    return (outcome(_tracker_drive, base, 21.0, float("nan")),
            outcome(_tracker_drive, mut, 21.0, float("nan")))


def probe_score_nan_pending():
    """accuracy.py:269: a NaN prediction that reached lead_pending some other
    way than note_lead_prediction (whose own guard, :238, refuses one)."""
    base, mut = mutated("accuracy",
                        "            if not np.isfinite(predicted):\n                continue",
                        "            if False:\n                continue")

    def drive(m):
        t = m.AccuracyTracker()
        t0 = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
        t.lead_pending.append((t0, 3.0, float("nan")))
        t.score_lead_predictions(t0 + timedelta(minutes=5), 21.0, window_hours=0.5)
        return repr(t.sigma(3.0)), dict(t.lead_counts)
    return outcome(drive, base), outcome(drive, mut)


PROBES = {"setpoint_step_zero": probe_setpoint_step,
          "roll_receipts_retention": probe_roll_receipts,
          "sanitize_tuple_nan": probe_sanitize,
          "gap_rate_zero_recent": probe_gap_rate,
          "plan_promise_zero_steps": probe_plan_promise,
          "sample_from_dict_falsy_t": probe_sample_from_dict,
          "take_fresh_handover_none": probe_take_fresh_handover,
          "score_lead_nan_actual": probe_score_nan_actual,
          "note_lead_nan_predicted": probe_note_nan_predicted,
          "score_nan_pending_direct": probe_score_nan_pending}


def main():
    c0 = time.process_time()
    distinct = 0
    for name, fn in PROBES.items():
        b, m = fn()
        d = int(b != m)
        distinct += d
        print(f"  {name}: baseline={b!r} mutant={m!r}")
        print(f"RESULT distinct_{name}={d} (0/1)")
    print(f"RESULT distinct_total={distinct} of {len(PROBES)} probes")
    print(f"RESULT thread_factor={(time.process_time() - c0) / max(time.thread_time(), 1e-9):.2f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
