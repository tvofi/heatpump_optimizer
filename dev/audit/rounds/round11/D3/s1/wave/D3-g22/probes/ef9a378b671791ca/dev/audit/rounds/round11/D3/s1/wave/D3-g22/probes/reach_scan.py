#!/usr/bin/env python3
# Metric: the shapes and values the four instrumented HeatPumpOptimizer methods receive in real solves
#   (features.py's v5.3.0 January scenario: plain, space-blocked, DHW-blocked, 3.6 kW cap, 0.05 kW cap, PV surplus).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes/reach_scan.py
# EXPECTED: one RESULT line per counted shape relation (see the RESULT names); counts, exact.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g22 (4 vCPU Xeon @ 2.10GHz).
# Instrumented symbols: optimizer.HeatPumpOptimizer._power_to_displace_schedule, ._publish_breach_reports,
#   ._pv_self_consumed, ._pv_surplus_list, ._safety_release_steps (wrapped, arguments recorded, then delegated).
# Perturbation: none (this is the reach census the probes cite; each probe carries its own perturbation).
import g22_rig as rig  # noqa: E402  (sets the thread pin and sys.path first)
from g22_rig import np, HeatPumpOptimizer  # noqa: E402
from unittest import mock  # noqa: E402

rec = {k: [] for k in ("disp", "breach", "pvsc", "pvsl", "rel")}
orig = {n: getattr(HeatPumpOptimizer, n) for n in (
    "_power_to_displace_schedule", "_publish_breach_reports", "_pv_self_consumed", "_pv_surplus_list",
    "_safety_release_steps")}


def w_disp(self, power, outdoor, fa=None):
    rec["disp"].append((len(power), len(outdoor), float(np.min(outdoor)), self.config.dt_hours,
                        self.model.params.ecl110_pid_tau_hours))
    return orig["_power_to_displace_schedule"](self, power, outdoor, fa)


def w_breach(self, result, caps, sb, db, n_steps, tmin, off_steps=None, quiet_actions=None):
    out = orig["_publish_breach_reports"](self, result, caps, sb, db, n_steps, tmin, off_steps, quiet_actions)
    traj = result.sensor_trajectory(self.model.params.two_zone_enabled)
    req = self._dhw_requirement
    d = result.dhw_temp_trajectory
    rec["breach"].append(dict(caps=caps is not None, sb=sb, db=db, n=n_steps, traj=len(traj), tmin=len(tmin),
                              req=None if req is None else len(req), dtraj=len(d) if d else 0,
                              dmargin=None if (req is None or not d) else
                              float(np.max(np.asarray(req, float) - np.asarray(d, float)[1:len(req) + 1])),
                              info={k: v for k, v in result.predictive_info.items() if "breach" in k}))
    return out


def w_pvsc(self, power, dt):
    s = self._pv_surplus
    rec["pvsc"].append((len(power), None if s is None else len(s),
                        None if s is None else int(np.sum((s > 0) & (s <= 1e-6)))))
    return orig["_pv_self_consumed"](self, power, dt)


def w_pvsl(self, n):
    s = self._pv_surplus
    rec["pvsl"].append((n, None if s is None else len(s)))
    return orig["_pv_surplus_list"](self, n)


def w_rel(self, result, temp_min_bounds, space_pins, dhw_pins):
    room = result.sensor_trajectory(self.model.params.two_zone_enabled)
    rec["rel"].append((len(result.power_schedule), len(room), len(temp_min_bounds)))
    return orig["_safety_release_steps"](self, result, temp_min_bounds, space_pins, dhw_pins)


opt, run = rig.january()
n = opt.config.n_steps
pv = np.zeros(n); pv[20:28] = 3.0
arms = {"plain": {}, "space_blocked": {"space_blocked": True}, "dhw_blocked": {"dhw_blocked": True},
        "cap3.6": {"power_caps_extra": np.full(n, 3.6)}, "cap0.05": {"power_caps_extra": np.full(n, 0.05)},
        "pv": {"pv_surplus": pv}, "pins_off": {"space_pins": np.where(np.arange(n) < 8, 0.0, np.nan)}}
with mock.patch.multiple(HeatPumpOptimizer, _power_to_displace_schedule=w_disp, _publish_breach_reports=w_breach,
                         _pv_self_consumed=w_pvsc, _pv_surplus_list=w_pvsl, _safety_release_steps=w_rel):
    for name, kw in arms.items():
        before = {k: len(v) for k, v in rec.items()}
        try:
            run(**kw)
            print(f"ARM {name}: ok " + " ".join(f"{k}+{len(v) - before[k]}" for k, v in rec.items()))
        except Exception as e:  # a pins argument the record may not take
            print(f"ARM {name}: {type(e).__name__}: {e}")
for k, v in rec.items():
    for row in v:
        print(f"REC {k} {row}")
print(f"RESULT disp_calls={len(rec['disp'])} count")
print(f"RESULT disp_outdoor_shorter_than_power={sum(1 for r in rec['disp'] if r[1] < r[0])} count")
print(f"RESULT disp_alpha_over_1={sum(1 for r in rec['disp'] if r[3] / r[4] > 1)} count")
print(f"RESULT breach_calls={len(rec['breach'])} count")
print(f"RESULT breach_traj_eq_n={sum(1 for r in rec['breach'] if r['traj'] == r['n'])} count")
print(f"RESULT breach_dhw_req_none_with_traj={sum(1 for r in rec['breach'] if r['db'] and r['req'] is None and r['dtraj'])} count")
print(f"RESULT breach_dhw_planned_longer_than_req_after_trim="
      f"{sum(1 for r in rec['breach'] if r['db'] and r['req'] is not None and r['dtraj'] - 1 > r['req'])} count")
print(f"RESULT breach_dhw_traj_eq_req={sum(1 for r in rec['breach'] if r['req'] is not None and r['dtraj'] == r['req'])} count")
print(f"RESULT pvsc_calls={len(rec['pvsc'])} count")
print(f"RESULT pvsc_power_longer_than_surplus={sum(1 for r in rec['pvsc'] if r[1] is not None and r[0] > r[1])} count")
print(f"RESULT rel_calls={len(rec['rel'])} count")
print(f"RESULT rel_room_not_n_plus_1={sum(1 for r in rec['rel'] if r[1] != r[0] + 1)} count")
print(f"RESULT rel_bounds_shorter_than_power={sum(1 for r in rec['rel'] if r[2] < r[0])} count")
rig.tail()
