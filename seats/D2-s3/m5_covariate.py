"""D2.M5 covariate-moved: a covariate moved to another sensor must reset or
re-base what it fed. Cells: covariate in {indoor, outdoor, flow, tank}.

Part 1 (the decision): the stored thermal-learning payload is written by the
production anchors (thermal_model.heat_loss_zone_entities) under config A; the
live one under config B, which differs from A only in the cell's entity id
(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_FLOW_METER_ENTITY /
flow temperature, CONF_DHW_TEMP_ENTITY). The production void decision
thermal_model.heat_loss_entity_voids(stored, live) names the learners voided.
  voided[cell] = number of learners the swap resets (identity: >= 1 for every
  covariate a learner reads).
Part 2 (the consequence, outdoor cell): the house heat-loss scale iterated by the
production step (thermal_model.learner_newton_step, alpha
coordinator.HOUSE_LOSS_ALPHA, trust coordinator._LEARNER_TRUST_REGION, then
HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale) to steady state on
outdoor sensor A (reads true), then the sensor moved to B reading +2 K (a sunlit
wall); first-order residual e = -(u_true*(Tin-Tout_true) - u_now*(Tin-Tout_read))*dt/C.
  restored_err = |scale carried into B / scale B converges to - 1| at the swap
  steps_to_2pct = intervals until within 2 % of B's equilibrium (not voided),
                  against the same from a voided learner (1.0)
Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m5_covariate.py
      --perturb-outdoor : CONF_OUTDOOR_TEMP_ENTITY joins thermal_model.HEAT_LOSS_ZONE_ENTITIES
      (voiding the house learner): voided[outdoor] must go up (0 -> 1).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, np

import argparse
import sys

sys.path.insert(0, "custom_components")
import harness  # noqa: F401,E402
import heatpump_optimizer.coordinator as cm  # noqa: E402
from heatpump_optimizer import const, thermal_model  # noqa: E402
from heatpump_optimizer.thermal_model import learner_newton_step  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-outdoor", action="store_true")
A = ap.parse_args()
cm._publish_params = lambda coord, /, **f: None
if A.perturb_outdoor:
    thermal_model.HEAT_LOSS_ZONE_ENTITIES[const.CONF_OUTDOOR_TEMP_ENTITY] = const.HEAT_LOSS_LEARNERS[0]

FLOW_KEY = getattr(const, "CONF_FLOW_TEMP_ENTITY", None) or getattr(const, "CONF_SUPPLY_TEMP_ENTITY", None) or const.CONF_FLOW_METER_ENTITY
KEYS = {"indoor": const.CONF_INDOOR_TEMP_ENTITY, "outdoor": const.CONF_OUTDOOR_TEMP_ENTITY,
        "flow": FLOW_KEY, "tank": const.CONF_DHW_TEMP_ENTITY}
base_cfg = {k: f"sensor.a_{n}" for n, k in KEYS.items()}
voided = {}
for name, key in KEYS.items():
    cfg_b = dict(base_cfg)
    cfg_b[key] = f"sensor.b_{name}"
    stored = {"heat_loss_zone_entities": thermal_model.heat_loss_zone_entities(base_cfg)}
    live = {"heat_loss_zone_entities": thermal_model.heat_loss_zone_entities(cfg_b)}
    v = thermal_model.heat_loss_entity_voids(stored, live)
    voided[name] = len(v)
    print(f"CELL covariate-moved covariate={name} key={key} voided={list(v)}")

# Part 2: outdoor consequence
U_CFG, CAP, DT_H, TIN, TOUT, OFFSET = 0.2, 10.0, 0.5, 21.0, 1.0, 2.0
U_TRUE = U_CFG * 1.0


class Holder:
    pass


def run(start, tout_read, n):
    h = Holder()
    h._house_heat_loss_scale = start
    tr = []
    for _ in range(n):
        cur = h._house_heat_loss_scale
        e = -(U_TRUE * (TIN - TOUT) - U_CFG * cur * (TIN - tout_read)) * DT_H / CAP
        st = learner_newton_step(cur, U_CFG, CAP, e, TIN - tout_read, DT_H,
                                 trust_region=cm._LEARNER_TRUST_REGION, alpha=cm.HOUSE_LOSS_ALPHA)
        if st is not None:
            cm.HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale(h, st[1])
        tr.append(h._house_heat_loss_scale)
    return np.array(tr)


a = run(1.0, TOUT, 3000)
s_a = a[-1]
b_eq = run(1.0, TOUT + OFFSET, 6000)[-1]
carried = run(s_a, TOUT + OFFSET, 3000)
fresh = run(1.0, TOUT + OFFSET, 3000)


def steps_to(tr, tgt):
    hit = np.flatnonzero(np.abs(tr / tgt - 1.0) <= 0.02)
    return int(hit[0]) + 1 if hit.size else len(tr) + 1


restored_err = abs(s_a / b_eq - 1.0)
print(f"CELL covariate-moved covariate=outdoor consequence: scale_A={s_a:.4f} scale_B_eq={b_eq:.4f} "
      f"restored_err={restored_err:.4f} steps_carried={steps_to(carried, b_eq)} steps_voided={steps_to(fresh, b_eq)}")
print(f"RESULT voided_indoor={voided['indoor']} count")
print(f"RESULT voided_outdoor={voided['outdoor']} count")
print(f"RESULT voided_flow={voided['flow']} count")
print(f"RESULT voided_tank={voided['tank']} count")
print(f"RESULT outdoor_restored_err={restored_err:.4f} ratio")
footer()
