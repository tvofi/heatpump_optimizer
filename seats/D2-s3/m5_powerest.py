"""D2.M5 power-entity-own-estimate: what each COP-side learner takes from an
interval whose power entity is metered against one that is the pump's own
estimate (CONF_POWER_SOURCE = estimate).

Drives the production fold tail HeatPumpOptimizerCoordinator._fold_cop_evidence
(unbound, on a duck-typed holder carrying the config) for 200 identical
intervals per arm: commanded 2.0 kW, modelled COP 3.0, the power entity reading
0.8 kW and a thermal power entity reading 6.4 kW (so the observed COP 8.0 is a
vendor's model, not the plant's). probe_install(config).cop_sample decides
whether the interval is a measured COP.

Metric (one line): per learner, whether it moved/recorded under each arm:
  cop_scale_moved (|scale-1|), measured_cop_records, health_observations,
  capacity_envelope_folds. Identity (brief): the pump_estimate arm moves none.
Recorded owner ruling quoted in thermal_model.InstallCapability.cop_sample
(tvofi, 2026-11-07): "Training on estimated power should be good enough and
better than nothing though so retain that" -- the COP scale training on an
estimate is ruled, so only the measured-COP record, the health watch and the
capacity envelope are held to the identity here.
Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m5_powerest.py
      --perturb-measured : InstallCapability.cop_measured ignores power_estimated
      (the guard removed): the estimate arm's measured_cop_records must go up.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer

import argparse
import sys
from types import SimpleNamespace

sys.path.insert(0, "custom_components")
import harness  # noqa: F401,E402
import heatpump_optimizer.coordinator as cm  # noqa: E402
from heatpump_optimizer import const, thermal_model  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-measured", action="store_true")
A = ap.parse_args()

cm._publish_params = lambda coord, /, **f: None
if A.perturb_measured:
    def _cm(self, dhw):
        return self.measured_heat and self.cop_electric() and not self.heat_estimated and (self.heat_sees_dhw or not dhw)
    thermal_model.InstallCapability.cop_measured = _cm


def arm(source):
    cfg = {const.CONF_POWER_ENTITY: "sensor.hp_power",
           const.CONF_POWER_SOURCE: source,
           const.CONF_THERMAL_POWER_ENTITY: "sensor.hp_heat",
           const.CONF_THERMAL_POWER_SOURCE: const.METER_SOURCE_METER}
    counts = {"measured_cop_records": 0, "health_observations": 0, "capacity_envelope_folds": 0}
    h = SimpleNamespace(_cop_scale=1.0, _cop_samples=0, _config=cfg)
    h._measured_cop = SimpleNamespace(record=lambda *a: counts.__setitem__("measured_cop_records", counts["measured_cop_records"] + 1))
    h._observe_cop_health = lambda *a: counts.__setitem__("health_observations", counts["health_observations"] + 1)
    h._fold_capacity_envelope = lambda *a: counts.__setitem__("capacity_envelope_folds", counts["capacity_envelope_folds"] + 1)
    h._apply_cop_scale = lambda s: cm.HeatPumpOptimizerCoordinator._apply_cop_scale(h, s)
    refusals = 0
    for _ in range(200):
        r = cm.HeatPumpOptimizerCoordinator._fold_cop_evidence(h, 2.0, 0.8, 6.4, (3.0, False, None))
        refusals += r is not None
    counts["cop_scale_moved"] = round(abs(h._cop_scale - 1.0), 4)
    counts["refusals"] = refusals
    counts["cop_measured"] = thermal_model.probe_install(cfg).cop_measured(False)
    return counts


res = {}
for name, src in (("metered", const.METER_SOURCE_METER), ("pump_estimate", const.METER_SOURCE_ESTIMATE)):
    res[name] = arm(src)
    print(f"CELL power-entity-own-estimate power_source={name} " + " ".join(f"{k}={v}" for k, v in res[name].items()))
e = res["pump_estimate"]
print(f"RESULT estimate_measured_cop_records={e['measured_cop_records']} count")
print(f"RESULT estimate_health_observations={e['health_observations']} count")
print(f"RESULT estimate_capacity_envelope_folds={e['capacity_envelope_folds']} count")
print(f"RESULT estimate_cop_scale_moved={e['cop_scale_moved']} ratio")
footer()
