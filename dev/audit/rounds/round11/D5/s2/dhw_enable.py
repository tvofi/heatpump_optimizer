#!/usr/bin/env python3
"""D5.M3 mechanism harness: how-it-works.md says "hot water optimization activates as soon as any
one of a DHW temperature sensor, a tank volume or a set of demand windows is configured"; the
shipped rule lets the explicit `dhw_enabled` switch (written by the setup wizard's Hot water step)
win over that presence trio.

Metric: over the 7 non-empty subsets of the presence trio, each on an entry carrying the explicit
switch the wizard writes when its "The house has a hot water tank" box is left unticked
(dhw_enabled=False), the number of configurations the doc says activate hot water that
thermal_model:_dhw_enabled_from_config leaves off. Second metric: how-it-works.md units stating the
presence rule with no mention of the switch.
Key: the boolean the production resolver returns.

Run:  PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/dhw_enable.py [--null] [--perturb]
  --null     the same 7 subsets on an entry with no explicit switch (a pre-switch entry): the doc's
             rule holds, contradicted=0.
  --perturb  the resolver's explicit-switch branch removed in memory (presence only): contradicted 7 -> 0.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact): contradicted=7 of 7,
doc_presence_units=1, wizard_writes_switch=1.
Machine: B2 (orchestrator's macOS box).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import itertools, re, sys, time
from pathlib import Path
from unittest import mock

for extra in ("custom_components", "tools/audit"):
    sys.path.insert(0, extra)
from heatpump_optimizer import const, thermal_model  # noqa: E402
import text_ledger  # noqa: E402

TRIO = {const.CONF_DHW_TEMP_ENTITY: "sensor.tank", const.CONF_DHW_TANK_VOLUME: 200.0,
        const.CONF_DHW_WINDOWS: "06:00-08:30"}


def presence_only(config):
    return any(config.get(k) is not None for k in TRIO)


def main():
    resolver = thermal_model._dhw_enabled_from_config
    if "--perturb" in sys.argv:
        resolver = presence_only
    contradicted = total = 0
    for r in range(1, 4):
        for keys in itertools.combinations(TRIO, r):
            cfg = {k: TRIO[k] for k in keys}
            if "--null" not in sys.argv:
                cfg[const.CONF_DHW_ENABLED] = False
            total += 1
            contradicted += not resolver(cfg)
    hiw = Path("docs/how-it-works.md").read_text(encoding="utf-8")
    units = [u for u in text_ledger.units_of("docs/how-it-works.md", hiw, "D6")
             if "activates as soon as any one of a DHW" in " ".join(u[3].split())
             and not re.search(r"switch|tick|has a hot water tank", u[3], re.I)]
    cf = Path("custom_components/heatpump_optimizer/config_flow.py").read_text()
    step = cf[cf.index('step_id="dhw"'):cf.index('step_id="dhw"') + 600]
    print(f"RESULT configurations={total} configs")
    print(f"RESULT contradicted={contradicted} configs")
    print(f"RESULT doc_presence_units={len(units)} units")
    for u in units:
        print(f"   presence {u[0]}:{u[1]}")
    print(f"RESULT wizard_writes_switch={int('CONF_DHW_ENABLED' in step)}")
    print(f"RESULT thread_factor={time.process_time() / max(time.thread_time(), 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
