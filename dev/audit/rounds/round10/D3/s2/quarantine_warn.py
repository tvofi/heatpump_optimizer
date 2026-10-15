#!/usr/bin/env python3
"""D3-s2-01 harness: the on-load quarantine warning is pinned by nothing.

Metric: number of store loaders (ledger.MonthlyLedger.from_dict,
snapshots.SnapshotRing.from_dict) whose "Quarantined N malformed ..." WARNING
fires exactly when a malformed record is dropped and stays silent on a clean
load.  Count key: the log records the production logger delivers.
Also printed: tests that name the warning text (grep, the gap itself).

Command (repo root, clean baseline tree):
    PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python \
        dev/audit/rounds/round10/D3/s2/quarantine_warn.py [--mutate]
Expected: loaders_correct=2 (exact) and tests_naming_warning=0 (exact);
with --mutate (the M26/M35 guard negation `if dropped:` -> `if not (dropped):`
applied in memory to both from_dict) loaders_correct=0 (direction: to_zero),
while mutants.py recorded that every gate script in the closure still passes.
Baseline 17f1c55fad1b; machine tvofi macOS arm64, shared box B2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob, inspect, logging, sys, textwrap, time

sys.path.insert(0, ".")
from custom_components.heatpump_optimizer import ledger, snapshots

MUT = "--mutate" in sys.argv


class Cap(logging.Handler):
    def __init__(self):
        super().__init__()
        self.msgs = []

    def emit(self, r):
        if r.levelno >= logging.WARNING:
            self.msgs.append(r.getMessage())


def patched(cls, mod):
    fn = cls.__dict__["from_dict"].__func__
    if not MUT:
        return fn
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count("if dropped:") == 1
    src = src.replace("if dropped:", "if not (dropped):")
    src = src.replace("@classmethod\n", "")
    ns = {}
    exec(compile(src, "<mut>", "exec"), vars(mod), ns)
    return ns["from_dict"]


def quarantine_msgs(mod, fn, cls, data):
    h = Cap()
    mod._LOGGER.addHandler(h)
    try:
        fn(cls, data)
    finally:
        mod._LOGGER.removeHandler(h)
    return [m for m in h.msgs if m.startswith("Quarantined")]


cases = []
# ledger: one well-formed month, plus one malformed (lines not a dict)
good_month = {"lines": {}, "meta": {}}
cases.append(("ledger", ledger, ledger.MonthlyLedger,
              {"months": {"2026-01": good_month}},
              {"months": {"2026-01": good_month, "2026-02": {"lines": 3}}}))
# snapshots: one dict snapshot, plus one non-dict
snap = {"taken_at": "2026-01-01T00:00:00+00:00", "accuracy": None, "learners": {}}
cases.append(("snapshots", snapshots, snapshots.SnapshotRing,
              {"snapshots": [snap]}, {"snapshots": [snap, "junk"]}))

correct = 0
for name, mod, cls, clean, bad in cases:
    fn = patched(cls, mod)
    on_clean = quarantine_msgs(mod, fn, cls, clean)
    on_bad = quarantine_msgs(mod, fn, cls, bad)
    ok = (not on_clean) and len(on_bad) == 1 and "Quarantined 1 " in on_bad[0]
    correct += ok
    print(f"  {name}: clean-load warnings={len(on_clean)} malformed-load warnings={on_bad} ok={ok}")

naming = [p for p in glob.glob("tests/*.py") + glob.glob("tests/*.mjs")
          if "Quarantined" in open(p, encoding="utf-8", errors="replace").read()]
print(f"RESULT loaders_correct={correct} of_{len(cases)}")
print(f"RESULT tests_naming_warning={len(naming)} files {naming}")
print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
