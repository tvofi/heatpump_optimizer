

CLS = co.HeatPumpOptimizerCoordinator
WHEN = co.dt_util.now().replace(day=15, hour=12, minute=0, second=0, microsecond=0)


def drive(fn, actual_kw, pending_extra=None):
    """One settled 0.25 h interval through _accumulate_energy; returns (ledger lines booked, saves scheduled, totals)."""
    c = coord()
    saves = []
    c._schedule_ledger_save = lambda: saves.append(1)
    pending = {"when": WHEN, "price": 1.5, "spot_price": 1.0, "power": 0.0, "dhw_power": 0.0,
               "space_reason": "cheap", "dhw_reason": "idle", **(pending_extra or {})}
    fn(c, SimpleNamespace(actual_power_kw=actual_kw), 0.25, pending)
    month = c._ledger.as_dict()["months"] if hasattr(c._ledger, "as_dict") else c._ledger.months
    lines = sorted(k for m in (month.values() if isinstance(month, dict) else month) for k in m.get("lines", {}))
    return lines, len(saves), round(c._energy_totals["total_energy_kwh"], 6)


MUT = recompile(CLS, "_accumulate_energy", "if energy <= 0:", "if False:")
for name, kw in (("zero_energy", 0.0), ("no_meter_zero_plan", None)):
    b, m = drive(CLS._accumulate_energy, kw), drive(MUT, kw)
    print(f"RESULT {name}_lines_baseline={len(b[0])} count {b[0]}")
    print(f"RESULT {name}_lines_mutant={len(m[0])} count {m[0]}")
    print(f"RESULT {name}_total_kwh_delta={m[2] - b[2]}")
    print(f"RESULT {name}_saves baseline={b[1]} mutant={m[1]}")
print(f"RESULT inputs no-price zero-energy: baseline={drive(CLS._accumulate_energy, 0.0, {'price': None})} mutant={drive(MUT, 0.0, {'price': None})}")
print(f"RESULT null_delta={int(drive(CLS._accumulate_energy, 2.0) != drive(MUT, 2.0))} count")
tail()
