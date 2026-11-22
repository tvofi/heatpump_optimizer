

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
