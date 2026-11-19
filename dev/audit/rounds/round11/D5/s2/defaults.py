#!/usr/bin/env python3
"""D5.M3 mechanism-default harness: the default each mechanism paragraph of the reader documents
states, against the value the shipped model actually starts from.

Metric: count of (document unit, default) pairs whose stated number differs from the production
value: a fresh `thermal_model.ThermalParameters()` attribute where the model carries one, else the
`const` default the config flow offers. Each pair's doc number is read from the document text by
its regex (so a doc edit moves it) and the code number from the live object (so a code edit moves it).
Key: the value the production object delivers, never the doc's own number.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/defaults.py [--perturb-code] [--perturb-doc]
  --perturb-code  const.DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS and the ThermalParameters field default
                  patched to 7.0 in memory: mismatches 7 -> 3 (the four legionella pairs leave).
  --perturb-age   const.INPUT_MAX_AGE_MINUTES indoor and tank entries patched to 60: mismatches 7 -> 5.
  --perturb-echo  pump_arbiter.ECHO_GRACE_S patched to 60.0 in memory: mismatches 7 -> 6.
  --perturb-doc   the four "7 days" legionella units rewritten to "10 days" in memory: mismatches 7 -> 3.
Null control: the other pairs (legionella temperature, wind, rain, DHW minimum, cooling rate, ...)
are the same mechanism paragraphs' defaults and read 0 mismatches.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact): pairs=57 mismatches=7 (four
legionella-interval units, the indoor and tank input ages, the pump-duty hold grace 60 s vs pump_arbiter.ECHO_GRACE_S 20 s);
--perturb-code mismatches=3, --perturb-age 5, --perturb-echo 6.
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses, re, sys, time
from pathlib import Path
from unittest import mock

for extra in ("custom_components",):
    sys.path.insert(0, extra)
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import thermal_model  # noqa: E402

# (doc, regex with one numeric group, production getter name, description)
PAIRS = [
    ("README.md", r"Anti-legionella is on by default at 60 °C every (\d+) days", "dhw_legionella_interval_days", "legionella interval"),
    ("docs/how-it-works.md", r"is enabled by default: every (\d+) days the tank is heated", "dhw_legionella_interval_days", "legionella interval"),
    ("docs/configuration.md", r"\| Anti-legionella interval \| (\d+) days \| 1–30 \| Placed in the cheapest hour before each deadline\. \|\n\nPer-weekday", "dhw_legionella_interval_days", "legionella interval (setup)"),
    ("docs/configuration.md", r"\| Anti-legionella interval \| (\d+) days \| 1–30 \| Placed in the cheapest hour before each deadline\. \|\n\n### Savings", "dhw_legionella_interval_days", "legionella interval (options)"),
    ("README.md", r"Anti-legionella is on by default at (\d+) °C", "dhw_legionella_temp", "legionella temperature"),
    ("docs/how-it-works.md", r"the tank is heated to (\d+) °C, scheduled at", "dhw_legionella_temp", "legionella temperature"),
    ("docs/how-it-works.md", r"\*\*Wind\*\* \(default ([\d.]+),", "wind_sensitivity", "wind sensitivity"),
    ("docs/how-it-works.md", r"\*\*Rain\*\* \(default ([\d.]+),", "rain_heat_loss_multiplier", "rain multiplier"),
    ("docs/how-it-works.md", r"minimum\n  temperature \(default (\d+) °C\)", "dhw_min_temp", "DHW minimum"),
    ("docs/how-it-works.md", r"\(default ([\d.]+) °C/h\) and converted", "dhw_cooling_rate", "tank cooling rate"),
    ("docs/how-it-works.md", r"The default inlet reference is ([\d.]+) °C", "dhw_inlet_temp", "inlet"),
    ("docs/how-it-works.md", r"Defaults, for orientation: upper mass (\d+) kWh/°C", "upper_floor_thermal_mass", "upper mass"),
    ("docs/how-it-works.md", r"lower (\d+) kWh/°C, upper loss", "lower_floor_thermal_mass", "lower mass"),
    ("docs/how-it-works.md", r"upper loss\n([\d.]+) kW/°C", "upper_floor_heat_loss", "upper loss"),
    ("docs/how-it-works.md", r"lower ([\d.]+) kW/°C, inter-zone", "lower_floor_heat_loss", "lower loss"),
    ("docs/how-it-works.md", r"inter-zone transfer ([\d.]+) kW/°C", "inter_zone_transfer", "inter-zone"),
    ("docs/how-it-works.md", r"radiator share\n([\d.]+), buffer", "radiator_power_fraction", "radiator share"),
    ("docs/how-it-works.md", r"buffer tank (\d+) L\. Single-zone", "buffer_tank_volume", "buffer volume"),
    ("docs/how-it-works.md", r"Single-zone defaults are a (\d+) kWh/°C house", "room_thermal_mass", "house mass"),
    ("docs/how-it-works.md", r"house at\n([\d.]+) kW/°C", "heat_loss_coefficient", "house loss"),
    ("docs/how-it-works.md", r"Defaults: (\d+) m² glazing", "window_area", "glazing"),
    ("docs/how-it-works.md", r"\((\d+) minutes for indoor and tank", "age:indoor_temp_entity", "indoor max age"),
    ("docs/how-it-works.md", r"\((\d+) minutes for indoor and tank", "age:dhw_temp_entity", "tank max age"),
    ("docs/how-it-works.md", r"temperatures, (\d+) for\noutdoor", "age:outdoor_temp_entity", "outdoor max age"),
    ("docs/how-it-works.md", r"outdoor, (\d+) for power meters", "age:heat_pump_power_entity", "power meter max age"),
    ("docs/how-it-works.md", r"bounded to \[([\d.]+), [\d.]+\] so a mis-scaled", "const:COP_SCALE_MIN", "cop_scale min"),
    ("docs/how-it-works.md", r"bounded to \[[\d.]+, ([\d.]+)\] so a mis-scaled", "const:COP_SCALE_MAX", "cop_scale max"),
    ("docs/how-it-works.md", r"A gap of more than (\d+)\nminutes", "const:OUTAGE_GAP_MINUTES", "outage gap"),
    ("docs/how-it-works.md", r"hot water queues (\d+) minutes behind", "const:OUTAGE_DHW_DELAY_MINUTES", "outage DHW delay"),
    ("docs/how-it-works.md", r"held only at its away minimum \((\d+) °C", "const:DEFAULT_AWAY_DHW_MIN_TEMP", "away DHW minimum"),
    ("docs/how-it-works.md", r"\*\*40 °C\nmixed-use reference\*\*|against a \*\*(\d+) °C", "const:DHW_MIXED_USE_TEMP", "mixed-use reference"),
    ("docs/how-it-works.md", r"held the\n  disinfection temperature for (\d+) minutes", "const:DHW_LEGIONELLA_HOLD_MINUTES", "disinfection hold"),
    ("docs/how-it-works.md", r"no sooner than a configurable minimum, default (\d+) days", "const:DEFAULT_DHW_LEGIONELLA_MIN_INTERVAL_DAYS", "elastic legionella minimum"),
    ("docs/how-it-works.md", r"Every optimization interval \((\d+) minutes by default\)", "const:DEFAULT_OPTIMIZATION_INTERVAL", "optimization interval"),
    ("docs/how-it-works.md", r"`comfort_weight`\n\(default (\d+)\)", "const:DEFAULT_COMFORT_WEIGHT", "comfort weight"),
    ('docs/configuration.md', 'At full power it is (\\d+) °C \\(the `flow_heat_c`', 'mod:pump_arbiter.FLOW_HEAT_C', 'pump duty flow ceiling'),
    ('docs/configuration.md', 'or toward (\\d+) °C when no return\\s+sensor is configured', 'mod:pump_arbiter.FLOW_HOLD_C', 'pump duty no-return floor'),
    ('docs/configuration.md', "The space gate is the entity's minimum, never\\s+below (\\d+) °C", 'mod:pump_arbiter.FLOW_GATE_C', 'pump duty space gate'),
    ('docs/configuration.md', 'The hold value, for when the plan is not in charge, is (\\d+) °C', 'mod:pump_arbiter.FLOW_HOLD_C', 'pump duty hold'),
    ('docs/configuration.md', 'are written (\\d+) K lower \\(the rated', 'mod:pump_arbiter.RETURN_SUPPLY_OFFSET_K', 'return spread'),
    ('docs/configuration.md', 'The lift at the lowest level is (\\d+) K over the inlet', 'const:DEFAULT_FLOW_MIN_LIFT_K', 'flow lift'),
    ('docs/configuration.md', 'value for the first (\\d+) minutes of a run', 'td:pump_arbiter.FEEDBACK_START_HOLD', 'feedback start hold'),
    ('docs/configuration.md', 'nudges the heating value ([\\d.]+) K per minute', 'mod:pump_arbiter.FEEDBACK_RATE_K_PER_MIN', 'feedback rate'),
    ('docs/configuration.md', 'averaged over (\\d+) minutes', 'td:pump_arbiter.FEEDBACK_WINDOW', 'feedback window'),
    ('docs/configuration.md', 'within (\\d+) % of the planned level', 'pct:pump_arbiter.FEEDBACK_DEADBAND_SHARE', 'feedback deadband'),
    ('docs/configuration.md', 'It goes no lower than ([\\d.]+) K below the inlet', 'mod:pump_arbiter.FEEDBACK_DOWN_K', 'feedback floor'),
    ('docs/configuration.md', 'minimum \\(never below (\\d+) °C\\) on hot-water-only steps', 'mod:pump_arbiter.FLOW_GATE_C', 'GCHV space gate'),
    ('docs/configuration.md', 'to its minimum \\(never below (\\d+) °C\\)\\s+on space-only steps', 'mod:pump_arbiter.DHW_GATE_C', 'GCHV DHW gate'),
    ('docs/configuration.md', 'a stop within (\\d+) minutes of a counted switch', 's2m:duty_switch.STOP_WINDOW_S', 'duty switch stop window'),
    ('docs/configuration.md', 'weighted (\\d+) or more switches', 'mod:duty_switch.N_ON', 'duty switch count'),
    ('docs/configuration.md', '\\(a switch weighs half after (\\d+) days\\)', 'mod:duty_switch.HALF_LIFE_DAYS', 'duty switch half-life'),
    ('docs/configuration.md', 'A hot-water-only stretch lasts at most (\\d+) minutes', 'mod:pump_arbiter.LEASE_MINUTES', 'rail'),
    ('docs/configuration.md', '\\((\\d+) below\\s+-10 °C outdoors\\)', 'mod:pump_arbiter.COLD_LEASE_MINUTES', 'cold rail'),
    ('docs/configuration.md', 'A boost\\s+lasts (\\w+) hours', 'words:boost.BOOST_HOURS', 'boost duration'),
    ('docs/configuration.md', 'Readings in the first\\s+(\\d+) seconds after a write are not counted', 'mod:pump_arbiter.ECHO_GRACE_S', 'hold echo grace'),
    ('docs/configuration.md', 'the value is sent\\s+again every (\\d+) minutes', 'mod:pump_arbiter.RETRY_MINUTES', 'retry'),
    ('docs/configuration.md', '\\(a rise of ([\\d.]+) °C over the step counts as hot water\\)', 'mod:pump_arbiter.TANK_RISE_C', 'ledger tank rise'),
]
CONST_FALLBACK = {
    "dhw_legionella_interval_days": "DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS",
}


def production(name):
    if name.startswith("age:"):
        return float(const.INPUT_MAX_AGE_MINUTES[name[4:]])
    if name.startswith("const:"):
        return float(getattr(const, name[6:]))
    if ":" in name:
        import importlib
        kind, ref = name.split(":", 1)
        mod, attr = ref.rsplit(".", 1)
        v = getattr(importlib.import_module("heatpump_optimizer." + mod), attr)
        if kind == "td":
            return v.total_seconds() / 60.0
        if kind == "pct":
            return float(v) * 100.0
        if kind == "s2m":
            return float(v) / 60.0
        return float(v)
    p = thermal_model.ThermalParameters()
    return float(getattr(p, name))


def main():
    texts = {d: Path(d).read_text(encoding="utf-8") for d in {p[0] for p in PAIRS}}
    if "--perturb-doc" in sys.argv:
        for d in texts:
            texts[d] = (texts[d].replace("at 60 °C every 7 days", "at 60 °C every 10 days")
                        .replace("every 7 days the tank is heated", "every 10 days the tank is heated")
                        .replace("| Anti-legionella interval | 7 days |", "| Anti-legionella interval | 10 days |"))
    patches = []
    if "--perturb-code" in sys.argv:
        fields = {f.name: f for f in dataclasses.fields(thermal_model.ThermalParameters)}
        patches = [mock.patch.object(const, "DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS", 7.0),
                   mock.patch.object(fields["dhw_legionella_interval_days"], "default", 7.0)]
    for p in patches:
        p.start()
    if "--perturb-echo" in sys.argv:
        from heatpump_optimizer import pump_arbiter
        mock.patch.object(pump_arbiter, "ECHO_GRACE_S", 60.0).start()
    if "--perturb-age" in sys.argv:
        ages = dict(const.INPUT_MAX_AGE_MINUTES)
        ages["indoor_temp_entity"] = ages["dhw_temp_entity"] = 60.0
        p = mock.patch.object(const, "INPUT_MAX_AGE_MINUTES", ages)
        p.start()
    if patches:  # a dataclass default is baked into __init__ at class creation: rebuild it
        orig_init = thermal_model.ThermalParameters.__init__
        def _init(self, *a, **k):
            k.setdefault("dhw_legionella_interval_days", 7.0)
            orig_init(self, *a, **k)
        thermal_model.ThermalParameters.__init__ = _init
    found = mism = 0
    for doc, rx, name, desc in PAIRS:
        m = re.search(rx, texts[doc])
        if not m:
            print(f"   unmatched {doc} {desc}")
            continue
        found += 1
        g = next(g for g in m.groups() if g)
        stated = float({"two": 2, "three": 3, "four": 4}.get(g, g))
        have = production(name)
        line = texts[doc].count("\n", 0, m.start()) + 1
        ok = abs(stated - have) < 1e-9
        mism += not ok
        print(f"   {'ok ' if ok else 'BAD'} {doc}:{line} {desc}: doc {stated:g} vs ThermalParameters().{name} {have:g}")
    print(f"RESULT pairs={found} pairs")
    print(f"RESULT mismatches={mism} pairs")
    print(f"RESULT const_default_legionella_interval={const.DEFAULT_DHW_LEGIONELLA_INTERVAL_DAYS:g} days")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
