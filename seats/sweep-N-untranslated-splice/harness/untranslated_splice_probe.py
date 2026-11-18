#!/usr/bin/env python3
"""Probe each Python N-untranslated-splice instance: render the sv and de
template HA would show, with the placeholder value the integration's own code
produces, and fail when an English fragment of that value survives.
Usage: untranslated_splice_probe.py SEAM   (exit 1 = instance reproduced)
"""
import json, sys
from pathlib import Path
sys.path.insert(0, ".")
P = Path("custom_components/heatpump_optimizer")
# Load the pure modules without the package __init__ (which needs homeassistant).
import types
for name, path in (("custom_components", "custom_components"),
                   ("custom_components.heatpump_optimizer", str(P))):
    if name not in sys.modules:
        m = types.ModuleType(name); m.__path__ = [path]; sys.modules[name] = m


def produce(seam):
    if seam in ("dhw_windows_set_thermal", "dhw_windows_apply", "dhw_windows_simulate", "quiet_windows"):
        from custom_components.heatpump_optimizer.dhw_schedule import parse_windows, DHWWindowError
        try:
            parse_windows("25:99-26:00")
        except DHWWindowError as err:
            return str(err)
    if seam == "manual_plan":
        from custom_components.heatpump_optimizer.manual_plan import ManualPlanError, build_override
        import datetime as dt
        try:
            build_override(dhw_slots="nope", space_slots=None,
                           expires_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
                           now=dt.datetime.now(dt.timezone.utc))
        except ManualPlanError as err:
            return str(err)
        except Exception as err:  # signature drift: say so rather than pass
            return f"PROBE-ERROR {type(err).__name__}: {err}"
    # literals copied from the producing line the enumerator names
    return {
        "store_version": "it was saved at version 3 and this release reads 2",
        "pump_write_ignored": "number.pump_dhw_target: 45 (set by the optimizer: 52)",
        "price_feed_stale": "Error fetching Tibber prices: timeout",
        "simulate_failed": "invalid_plan: no feasible schedule",
        "diagnose_failed": "solver worker unavailable",
    }[seam]


SEAMS = {  # seam: (section, key, field, placeholder)
    "dhw_windows_set_thermal": ("exceptions", "set_thermal_params_invalid_dhw_windows", "message", "error"),
    "dhw_windows_apply": ("exceptions", "apply_schedule_invalid_dhw_windows", "message", "error"),
    "dhw_windows_simulate": ("exceptions", "simulate_plan_invalid_windows", "message", "error"),
    "quiet_windows": ("exceptions", "apply_schedule_invalid_quiet_windows", "message", "error"),
    "manual_plan": ("exceptions", "manual_plan_invalid_slots", "message", "error"),
    "simulate_failed": ("exceptions", "simulate_plan_failed", "message", "error"),
    "diagnose_failed": ("exceptions", "diagnose_interval_failed", "message", "error"),
    "store_version": ("issues", "store_version", "description", "detail"),
    "pump_write_ignored": ("issues", "pump_write_ignored", "description", "detail"),
    "price_feed_stale": ("issues", "price_feed_stale", "description", "error"),
}
EN_WORDS = {"invalid", "expected", "error", "fetching", "prices", "saved", "version", "release",
            "reads", "set", "by", "the", "optimizer", "no", "feasible", "schedule", "solver",
            "worker", "unavailable", "time", "slots", "must", "be", "list", "objects", "got", "datetime"}


def main():
    seam = sys.argv[1]
    sec, key, field, ph = SEAMS[seam]
    value = produce(seam)
    bad = []
    for lang in ("sv", "de"):
        tpl = json.loads((P / f"translations/{lang}.json").read_text())[sec][key][field]
        if "{" + ph + "}" not in tpl:
            continue
        text = tpl.replace("{" + ph + "}", value)
        en = sorted({w.strip(".,:()'\"").lower() for w in value.split()} & EN_WORDS)
        if en:
            bad.append(f"{lang}: {text[:160]!r} carries English {en}")
    print(f"{seam}: value={value!r}")
    for b in bad:
        print("  FAIL", b)
    sys.exit(1 if bad else 0)


main()
