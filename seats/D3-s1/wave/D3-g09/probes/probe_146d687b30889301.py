#!/usr/bin/env python3
# Metric: calls to HeatPumpOptimizerCoordinator._schedule_ledger_save made by one _roll_month(when), on a ledger
#   holding a January line, at when = 2026-02-01 00:05 UTC (January closes) and at 2026-01-20 (nothing closes);
#   plus whether January's frozen receipt is in _month_reports (it is in both arms: only the save differs).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_146d687b30889301.py
#   Second metric, at the only caller (coordinator.py:10090 -> _accumulate_energy, which rolls at 10306): saves per
#   settlement that crosses into February, at energy > 0, energy 0, and with a fault injected after the roll
#   (_fold_score_sample raising), and whether January's receipt is frozen before the settlement's last save.
# EXPECTED RESULT saves_close_baseline=1, saves_close_mutant=0; null control: saves_open 0 in both arms.
# EXPECTED RESULT settle_saves_energy_baseline=2, _mutant=1 and settle_saves_zero_baseline=2, _mutant=1: the
#   settlement's own unconditional save (10332 / 10401) still follows the freeze in both arms, so the stored state
#   is the same (equivalent at the caller); settle_saves_fault_baseline=1, _mutant=0: only a settlement that
#   raises after the roll separates the arms.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._roll_month
#   (coordinator.py:10504 `if closed:`), reached from the settlement (coordinator.py:10306).
# Perturbation: mutant 146d687b30889301, `if closed:` -> `if False:`, in memory. Direction: the month-close save
#   goes 1 -> 0: the frozen receipt lives only in memory until some later save, lost on a restart before it.
import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402

C = L.HeatPumpOptimizerCoordinator
MUT = L.mutant(C, "_roll_month", "if closed:", "if False:")


def arm(when, fn):
    c = L.coord()
    c._ledger.add(datetime(2026, 1, 15, 12, tzinfo=timezone.utc), "space", kwh=2.0, sek=3.0)
    saves = []
    c._schedule_ledger_save = lambda: saves.append(1)
    if fn is None:
        c._roll_month(when)
    else:
        with mock.patch.object(C, "_roll_month", fn):
            c._roll_month(when)
    return len(saves), int("2026-01" in c._month_reports)


for label, when in (("close", datetime(2026, 2, 1, 0, 5, tzinfo=timezone.utc)),
                    ("open", datetime(2026, 1, 20, 12, tzinfo=timezone.utc))):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        n, frozen = arm(when, fn)
        print(f"RESULT saves_{label}_{name}={n} january_receipt_frozen={frozen}")


def settle(fn, actual_kw, fault=False):
    c = L.coord()
    c._ledger.add(datetime(2026, 1, 15, 12, tzinfo=timezone.utc), "space", kwh=2.0, sek=3.0)
    log = []
    c._schedule_ledger_save = lambda: log.append("2026-01" in c._month_reports)
    if fault:
        def boom(*a, **k):
            raise RuntimeError("injected after the roll")
        c._fold_score_sample = boom
    sample = types.SimpleNamespace(actual_power_kw=actual_kw)
    pending = {"when": datetime(2026, 2, 1, 0, 5, tzinfo=timezone.utc), "price": 1.0, "spot_price": 1.0,
               "power": actual_kw, "dhw_power": 0.0}
    try:
        if fn is None:
            c._accumulate_energy(sample, 0.25, pending)
        else:
            with mock.patch.object(C, "_roll_month", fn):
                c._accumulate_energy(sample, 0.25, pending)
        err = ""
    except Exception as exc:
        err = type(exc).__name__
    return len(log), int(bool(log) and log[-1]), err


for label, kw, fault in (("energy", 2.0, False), ("zero", 0.0, False), ("fault", 2.0, True)):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        n, frozen_at_last, err = settle(fn, kw, fault)
        print(f"RESULT settle_saves_{label}_{name}={n} receipt_frozen_at_last_save={frozen_at_last} raised={err or '-'}")
L.trailer()
