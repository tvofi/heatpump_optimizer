#!/usr/bin/env python3
# Metric: what HeatPumpOptimizerCoordinator.month_channel_totals returns for a ledger channel, through the production
#   ledger (ledger.py:MonthlyLedger.line): None = "no data" (the docstring's contract) or a (kWh, SEK) tuple.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g11/probes/probe_d4b32336.py
# Expected: through MonthlyLedger every arm agrees (moved_production=0 count): MonthlyLedger.line returns
#   {"kwh": 0.0, "sek": 0.0} for an empty month, a dict that is never falsy, so the guard never fires on the baseline
#   either (fresh_ledger baseline (0.0, 0.0)). Only a stub ledger returning {} or None moves (None -> (0.0, 0.0) /
#   AttributeError), which the production ledger never returns.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g11 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.month_channel_totals
#   (line 8457, `        if not entry:`), over custom_components.heatpump_optimizer.ledger:MonthlyLedger.
# Perturbation: mutant d4b32336085935df, `if not entry:` -> `if False:`, in memory (the method recompiled from its own
#   source, called on a SimpleNamespace carrying a real MonthlyLedger). Direction: none through production
#   (equivalent-candidate); the stub arms show the guard's only reachable effect.
# Null control: a booked line (add 3.5 kWh / 4.2 SEK this month), where both arms return (3.5, 4.2).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, sys, textwrap
from pathlib import Path

ROOT = Path.cwd()  # run from the repository root (harness contract)
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").is_file(), "run from the repository root"
sys.path.insert(0, str(ROOT))
from custom_components.heatpump_optimizer import coordinator as co  # noqa: E402


def mutate(fn, old, new, name=None):
    """Recompile fn's own source with the one-line mutant, in the module namespace (in memory)."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == 1, f"anchor moved: {old!r}"
    ns = dict(co.__dict__)
    exec(compile(src.replace(old, new, 1), co.__file__, "exec"), ns)
    return ns[name or fn.__name__]


def tail_results(t0_cpu, t0_thr):
    import time
    pc, tc = time.process_time() - t0_cpu, time.thread_time() - t0_thr
    print(f"RESULT thread_factor={pc / tc if tc > 0 else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for ln in open("/proc/vmstat"):
            if ln.startswith("pswpin "):
                sw = int(ln.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw} count")

import time
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import mock
from custom_components.heatpump_optimizer.ledger import MonthlyLedger

CLS = co.HeatPumpOptimizerCoordinator
MUT = mutate(CLS.month_channel_totals, "if not entry:", "if False:")
NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)


def call(fn, ledger, line="space"):
    me = SimpleNamespace(_ledger=ledger)
    with mock.patch.object(co.dt_util, "now", lambda: NOW):
        try:
            return fn(me, line)
        except Exception as err:  # noqa: BLE001
            return type(err).__name__


t0, t1 = time.process_time(), time.thread_time()
fresh = MonthlyLedger()
other_month = MonthlyLedger()
other_month.add(datetime(2025, 12, 15, tzinfo=timezone.utc), "space", kwh=1.0, sek=1.0)
other_line = MonthlyLedger()
other_line.add(NOW, "dhw", kwh=1.0, sek=1.0)
restored_junk = MonthlyLedger.from_dict({"months": {"2026-01": {"lines": {"space": "junk"}, "meta": {}}}})
moved = 0
for name, led in {"fresh_ledger": fresh, "other_month_only": other_month, "other_line_only": other_line,
                  "restored_non_dict_entry": restored_junk}.items():
    b, m = call(CLS.month_channel_totals, led), call(MUT, led)
    moved += int(b != m)
    print(f"RESULT {name}_baseline={b} mutant={m}")
print(f"RESULT moved_production={moved} count")
for name, entry in {"stub_empty_dict": {}, "stub_none": None}.items():
    stub = SimpleNamespace(line=lambda month, line, e=entry: e)
    print(f"RESULT {name}_baseline={call(CLS.month_channel_totals, stub)} mutant={call(MUT, stub)}  (not a production ledger)")
booked = MonthlyLedger()
booked.add(NOW, "space", kwh=3.5, sek=4.2)
print(f"RESULT null_moved={int(call(CLS.month_channel_totals, booked) != call(MUT, booked))} count")
tail_results(t0, t1)
