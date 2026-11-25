import json
M = json.load(open("mutants.json"))
HDR = """#!/usr/bin/env python3
# Metric: {metric}
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_{key}.py
# EXPECTED RESULT: {expected}
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g47 (4 vCPU Xeon @ 2.30GHz). Values are exact (no wall/CPU numbers).
# Instrumented symbol: custom_components.heatpump_optimizer.thermal_model:{fn} (line {line}).
# Perturbation: the gate's one-line mutant `{old}` -> `{new}` applied in memory (g47_mut.load re-compiles the module source with that one line
#   replaced; nothing on disk changes). Direction: see EXPECTED. Null control: `controls` inputs where the edit cannot matter must show 0 differing.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import g47_mut
INF, NAN = float("inf"), float("nan")
"""
P = {}
def add(key, fn, metric, expected, body):
    P[key] = (fn, metric, expected, body)
D = "dict"
# --- dhw_coil_draw_reduction
add("d2463d81efddd380", "dhw_coil_draw_reduction", "count of inputs (draw_kw in {0.0,-0.0,nan,tiny}, finite setpoint/inlet/wood, plus a non-finite setpoint) where (reduced, coil) differs between baseline and the `draw<=0 -> draw<0` mutant",
 "inputs_differing=1 (only dhw_setpoint=inf with draw 0: baseline (0.0,0.0), mutant nan); finite inputs 0 -> equivalent-candidate for finite inputs",
 """inputs = [dict(draw_kw=d, wood_temp=w, dhw_setpoint=s, inlet_temp=i) for d in (0.0, -0.0, 1e-300, -1e-300) for w in (5.0, 10.0, 45.0, 90.0) for s in (20.0, 48.0, 60.0) for i in (5.0, 10.0, 20.0)]
inputs += [dict(draw_kw=0.0, wood_temp=60.0, dhw_setpoint=INF, inlet_temp=10.0), dict(draw_kw=0.0, wood_temp=NAN, dhw_setpoint=50.0, inlet_temp=10.0)]
controls = [dict(draw_kw=d, wood_temp=60.0, dhw_setpoint=50.0, inlet_temp=10.0) for d in (0.5, 2.0, 7.0)]""")
add("0aa9e2e025b11284", "dhw_coil_draw_reduction", "count of inputs where (reduced, coil) differs when the t_in <= setpoint cap is dropped (t_in is local; the next use is max(0, setpoint - t_in))",
 "inputs_differing=0 -> equivalent-candidate",
 """inputs = [dict(draw_kw=d, wood_temp=w, dhw_setpoint=s, inlet_temp=i) for d in (0.5, 3.0) for w in (5.0, 30.0, 60.0, 95.0, INF, NAN) for s in (8.0, 10.0, 12.0, 30.0, 55.0) for i in (5.0, 10.0, 12.0)]
controls = [dict(draw_kw=2.0, wood_temp=10.0, dhw_setpoint=55.0, inlet_temp=10.0)]""")
add("41063896cdb5ea71", "dhw_coil_draw_reduction", "outcome of dhw_coil_draw_reduction when dhw_setpoint == inlet_temp (span clamp 1e-6 dropped): baseline (0.0, draw) vs mutant exception",
 "inputs_differing>=1: baseline (0.0, draw_kw); mutant RAISES ZeroDivisionError at setpoint == inlet_temp",
 """inputs = [dict(draw_kw=2.0, wood_temp=w, dhw_setpoint=s, inlet_temp=10.0) for w in (10.0, 40.0, 60.0) for s in (10.0, 10.0 + 1e-9, 10.0 - 1e-3, 9.0, 12.0)]
controls = [dict(draw_kw=2.0, wood_temp=40.0, dhw_setpoint=s, inlet_temp=10.0) for s in (30.0, 48.0, 60.0)]""")
# --- learner_newton_step
LN = "dict(current=1.0, base_u=BU, capacity=CAP, residual=RES, delta_t=DT, dt_hours=0.25, trust_region=0.1, alpha=0.2)"
def ln(bu="0.5", cap="2.0e4", res="0.1", dt="10.0"):
    return LN.replace("BU", bu).replace("CAP", cap).replace("RES", res).replace("DT", dt)
add("b27ac4781778a34a", "learner_newton_step", "returned (target, updated) of learner_newton_step at capacity == 1e-6 exactly vs just above (baseline None at the tie, mutant a step)",
 "inputs_differing=1: baseline None, mutant a (target, updated) tuple at capacity=1e-6 exactly",
 f"""inputs = [{ln(cap='1e-6')}, {ln(cap='1e-6 - 1e-12')}]
controls = [{ln(cap='1e-6 + 1e-9')}, {ln(cap='2e4')}, {ln(cap='0.0')}]""")
add("bed063118e10d683", "learner_newton_step", "returned (target, updated) of learner_newton_step at base_u == 1e-6 exactly (baseline None, mutant a step)",
 "inputs_differing=1: baseline None, mutant tuple at base_u=1e-6 exactly",
 f"""inputs = [{ln(bu='1e-6')}, {ln(bu='1e-6 - 1e-12')}]
controls = [{ln(bu='1e-6 + 1e-9')}, {ln(bu='0.5')}, {ln(bu='0.0')}]""")
add("721aca562f60ab2c", "learner_newton_step", "returned value of learner_newton_step for non-finite residual/delta_t/capacity inputs (baseline None, mutant a non-finite step or an exception)",
 "inputs_differing>=1: baseline None; mutant returns (nan, nan) / (inf-clipped) or raises",
 f"""inputs = [{ln(res='NAN')}, {ln(res='INF')}, {ln(res='-INF')}, {ln(dt='0.0')}, {ln(dt='NAN')}, {ln(cap='INF')}, {ln(cap='NAN')}, {ln(dt='-0.0', res='0.0')}]
controls = [{ln()}, {ln(res='-0.3')}, {ln(dt='-4.0')}]""")
# --- mold_safe_room_floor
MF = "dict(room_temp_c=RT, indoor_rh_percent=RH, outdoor_temp_c=OT, frsi=FR, surface_rh_limit=LIM)"
def mf(rt="21.0", rh="55.0", ot="-5.0", fr="0.7", lim="0.8"):
    return MF.replace("RT", rt).replace("RH", rh).replace("OT", ot).replace("FR", fr).replace("LIM", lim)
add("09412cb43997a47f", "mold_safe_room_floor", "floor (degC) mold_safe_room_floor returns for frsi below the 0.3 clamp",
 "inputs_differing>=1 (frsi 0.1/0.0/-0.2: baseline floor uses 0.3, mutant a far larger/ill-defined floor, frsi=0 raises)",
 f"""inputs = [{mf(fr='0.29')}, {mf(fr='0.1')}, {mf(fr='0.0')}, {mf(fr='-0.2')}]
controls = [{mf(fr='0.3')}, {mf(fr='0.5')}, {mf(fr='0.9')}]""")
add("4c3cfbe1e4ad2a14", "mold_safe_room_floor", "floor (degC) for frsi above the 0.98 clamp",
 "inputs_differing>=1 (frsi 0.99/1.0/1.5: baseline floor uses 0.98, mutant the raw frsi)",
 f"""inputs = [{mf(fr='0.99')}, {mf(fr='1.0')}, {mf(fr='1.5')}, {mf(fr='2.0', ot='-15.0')}]
controls = [{mf(fr='0.3')}, {mf(fr='0.7')}, {mf(fr='0.98')}]""")
add("28b6107a17d9b814", "mold_safe_room_floor", "floor for indoor_rh_percent <= 0 and non-finite (lower RH clamp dropped; negative RH gives e<0 and the same -100 return)",
 "inputs_differing=0 -> equivalent-candidate",
 """def _m(rh, rt=21.0): return dict(room_temp_c=rt, indoor_rh_percent=rh, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8)
inputs = [_m(r) for r in (0.0, -0.0, -1.0, -50.0, -1e9, NAN, INF, -INF)] + [_m(-5.0, t) for t in (-30.0, 0.0, 40.0)]
controls = [_m(55.0), _m(100.0)]""")
add("5b6489f7860d73b1", "mold_safe_room_floor", "floor for indoor_rh_percent above 100 (upper RH clamp dropped)",
 "inputs_differing>=1 (RH 100.5/120: baseline caps at 100 %, mutant a higher floor)",
 f"""inputs = [{mf(rh='100.5')}, {mf(rh='101.0')}, {mf(rh='120.0')}, {mf(rh='INF')}]
controls = [{mf(rh='55.0')}, {mf(rh='100.0')}, {mf(rh='0.0')}]""")
add("1111a3e5d9c44e3f", "mold_safe_room_floor", "floor at e == 1e-9 hPa exactly (`e <= 1e-9` -> `e < 1e-9`): baseline -100.0 vs the dew-point branch",
 "inputs_differing>=1 only if an RH makes rh*svp == 1e-9 bit-exactly (searched by ulp walk); else equivalent-candidate",
 """import math
from custom_components.heatpump_optimizer import thermal_model as _t
inputs = []
for rt in (-10.0, 0.0, 5.0, 10.0, 21.0, 30.0):
    svp = _t.saturation_vapor_pressure(rt)
    pct = 1e-9 / svp * 100.0
    for _ in range(0, 1):
        cands = {pct}
        x = pct
        for _i in range(64):
            x = math.nextafter(x, 0.0); cands.add(x)
        x = pct
        for _i in range(64):
            x = math.nextafter(x, 1.0); cands.add(x)
        for c in sorted(cands):
            e = min(max(c, 0.0), 100.0) / 100.0 * svp
            if e == 1e-9:
                inputs.append(dict(room_temp_c=rt, indoor_rh_percent=c, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8))
                break
print(f"SEARCH exact-tie inputs found: {len(inputs)} of 6 room temperatures")
inputs += [dict(room_temp_c=21.0, indoor_rh_percent=r, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8) for r in (1e-9, 1e-8, 1e-7, 1e-6)]
controls = [dict(room_temp_c=21.0, indoor_rh_percent=r, outdoor_temp_c=-5.0, frsi=0.7, surface_rh_limit=0.8) for r in (0.0, 30.0, 70.0)]""")
add("67a0550ee998a213", "mold_safe_room_floor", "floor at indoor_rh_percent == 0 (e == 0): baseline the sentinel -100.0; mutant (guard off) runs dew_point_for_pressure on the clamped 1e-9 hPa",
 "inputs_differing>=1: baseline -100.0; mutant about -169 degC at outdoor -5, frsi 0.7",
 f"""inputs = [{mf(rh='0.0')}, {mf(rh='-3.0')}, {mf(rh='0.0', ot='-20.0')}, {mf(rh='0.0', ot='10.0')}, {mf(rh='1e-12')}]
controls = [{mf(rh='55.0')}, {mf(rh='20.0')}, {mf(rh='95.0')}]""")
add("75b300b2bc47485f", "mold_safe_room_floor", "floor for surface_rh_limit < 0.05 and == 0 (`max(limit, 0.05)` clamp dropped)",
 "inputs_differing>=1 (limit 0.01/0.04: baseline uses 0.05, mutant a lower dew point->higher floor; limit 0.0 raises ZeroDivisionError)",
 f"""inputs = [{mf(lim='0.04')}, {mf(lim='0.01')}, {mf(lim='0.0')}, {mf(lim='-0.1')}]
controls = [{mf(lim='0.05')}, {mf(lim='0.8')}, {mf(lim='1.0')}]""")
# --- wood_share
WS = "dict(wood_temp=WT, hp_temp=HT, flow_set=FS, floor_temp=FL, margin=3.0)"
def ws(wt="40.0", ht="35.0", fs="45.0", fl="20.0"):
    return WS.replace("WT", wt).replace("HT", ht).replace("FS", fs).replace("FL", fl)
add("92c063e90dafcc35", "wood_share", "wood_share at hp_temp == flow_set exactly (`>` -> `>=`) for wood_temp below flow_set; region 3 at the tie vs region 2's 0.0",
 "inputs_differing=0 if region 3 is continuous (0.0) at hp_temp == flow_set -> equivalent-candidate; else >=1",
 """def _w(wt, hp, fs, fl): return dict(wood_temp=wt, hp_temp=hp, flow_set=fs, floor_temp=fl, margin=3.0)
inputs = [_w(w, 45.0, 45.0, fl) for w in (20.0, 30.0, 40.0, 43.0, 44.5, 44.999) for fl in (0.0, 15.0, 20.0, 35.0)] + [_w(40.0, 60.0, 60.0, 20.0)]
controls = [_w(40.0, 50.0, 45.0, 20.0), _w(40.0, 40.0, 45.0, 20.0)]""")
add("6fa8436f09ad7e06", "wood_share", "wood_share when floor_temp >= flow_set in region 2 (`max(flow_set-floor,1e-6)` clamp dropped): baseline 0.0, mutant ZeroDivisionError at floor == flow_set",
 "inputs_differing>=1: baseline 0.0; mutant RAISES ZeroDivisionError at floor_temp == flow_set (floor_temp > flow_set: -0.0 vs 0.0 sign only)",
 """def _w(wt, hp, fs, fl): return dict(wood_temp=wt, hp_temp=hp, flow_set=fs, floor_temp=fl, margin=3.0)
inputs = [_w(40.0, 60.0, 45.0, fl) for fl in (45.0, 45.0 + 1e-9, 46.0, 60.0)]
controls = [_w(40.0, 60.0, 45.0, 20.0), _w(44.0, 55.0, 45.0, 30.0)]""")
for k, (fn, metric, exp, body) in P.items():
    line, old, new = M[k]
    src = HDR.format(metric=metric, key=k, expected=exp, fn=fn, line=line, old=old.strip(), new=new.strip()) + body + f"\ng47_mut.probe({k!r}, {fn!r}, inputs, controls)\n"
    open(f"probe_{k}.py", "w").write(src)
