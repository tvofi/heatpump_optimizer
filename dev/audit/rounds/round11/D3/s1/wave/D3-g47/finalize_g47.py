#!/usr/bin/env python3
"""Write results/<key>.json for one gated key: python3 finalize_g47.py <key>. Classification table below is from the executed probes."""
import csv, json, subprocess, sys
from pathlib import Path
W = Path(__file__).resolve().parent
S1 = W.parent.parent
M = json.loads((W / "probes" / "mutants.json").read_text())
ROWS = {r["key"]: r for r in csv.DictReader(open(W / "keys.tsv"), delimiter="\t")}
EQ, CAND = "equivalent-candidate", "candidate"
# key: (class if survived, title/claim text, severity, inputs tried, should_fail, result)
T = {
"d2463d81efddd380": (EQ, "draw<=0 -> draw<0 is unobservable for every finite input: at draw 0 the arithmetic returns (0.0,0.0) too; only dhw_setpoint=inf (config bound 40..65) makes the mutant return (nan,nan)",
  "draw in {0,-0,+-1e-300} x wood {5,10,45,90} x setpoint {20,48,60} x inlet {5,10,20}; plus setpoint=inf; wood=nan", "tests/features.py: dhw_coil_draw_reduction(0.0,..)==(0.0,0.0) (holds under the mutant for finite inputs)"),
"0aa9e2e025b11284": (EQ, "the t_in<=setpoint cap is dead: t_in is local and only enters max(0, setpoint - t_in)",
  "draw {0.5,3} x wood {5,30,60,95,inf,nan} x setpoint {8,10,12,30,55} x inlet {5,10,12}: 180 inputs, 0 differ", "none: equivalent"),
"41063896cdb5ea71": (CAND, "dhw_coil_draw_reduction: the 1e-6 span floor has no test; at dhw_setpoint == inlet_temp the unclamped span raises ZeroDivisionError where the baseline returns (0.0, draw)",
  "setpoint in {inlet, inlet+1e-9, inlet-1e-3, 9, 12} x wood {10,40,60}", "tests/features.py (executes line 3004 on the traced baseline): a dhw_coil_draw_reduction call with dhw_setpoint == inlet_temp asserting (0.0, draw) - no check reads it"),
"b27ac4781778a34a": (CAND, "learner_newton_step: no test pins the capacity==1e-6 tie of `capacity <= 1e-6`; at the tie the baseline returns None and the mutant a step",
  "capacity in {1e-6, 1e-6-1e-12}; controls 1e-6+1e-9, 2e4, 0.0", "tests/boost_drift_replay.py / features.py / entities.py (closure scripts tracing line 3073): learner_newton_step(capacity=1e-6) is None"),
"bed063118e10d683": (CAND, "learner_newton_step: no test pins the base_u==1e-6 tie of `base_u <= 1e-6`; baseline None, mutant a step",
  "base_u in {1e-6, 1e-6-1e-12}; controls 1e-6+1e-9, 0.5, 0.0", "tests/boost_drift_replay.py / features.py / entities.py: learner_newton_step(base_u=1e-6) is None"),
"721aca562f60ab2c": (CAND, "learner_newton_step: the np.isfinite(target) guard is untested; with a non-finite residual or capacity the baseline returns None but the mutant returns (nan, nan), which the callers would store as the learner state",
  "residual nan/inf/-inf, delta_t 0/nan/-0, capacity inf/nan (callers guard residual finiteness and delta_t>=6, not capacity/base_u)", "tests/boost_drift_replay.py, features.py, entities.py: learner_newton_step(residual=nan or capacity=nan) is None"),
"09412cb43997a47f": (CAND, "mold_safe_room_floor: the 0.3 lower fRsi clamp is untested; frsi<0.3 gives a different floor and frsi=0 raises ZeroDivisionError (config flow bounds frsi to 0.3..0.98, the function's own clamp is the second line)",
  "frsi in {0.29, 0.1, 0.0, -0.2}", "tests/entities.py / features.py: mold_safe_room_floor(frsi=0.1) equals the frsi=0.3 floor"),
"4c3cfbe1e4ad2a14": (CAND, "mold_safe_room_floor: the 0.98 upper fRsi clamp is untested; frsi in {0.99,1,1.5,2} changes the floor",
  "frsi in {0.99, 1.0, 1.5, 2.0 at outdoor -15}", "tests/entities.py / features.py: mold_safe_room_floor(frsi=1.5) equals the frsi=0.98 floor"),
"28b6107a17d9b814": (EQ, "the 0 % lower RH clamp is dead: negative RH gives e<0 which takes the same -100.0 return as e==0; nan gives the same nan either way",
  "RH {0,-0,-1,-50,-1e9,nan,inf,-inf} and RH -5 at room {-30,0,40}: 11 inputs, 0 differ", "none: equivalent"),
"5b6489f7860d73b1": (CAND, "mold_safe_room_floor: the 100 % upper RH clamp is untested; RH 100.5/101/120/inf changes the floor (the coordinator caller already limits RH to (0,100], so only the function contract is unpinned)",
  "RH {100.5, 101, 120, inf}", "tests/entities.py / features.py: mold_safe_room_floor(indoor_rh_percent=120) equals the 100 % floor"),
"1111a3e5d9c44e3f": (CAND, "mold_safe_room_floor: the e==1e-9 tie of `e <= 1e-9` is untested; at the bit-exact tie baseline returns the -100.0 sentinel, mutant -191.9 (an ulp walk found the tie at all 6 room temperatures; the consumer maximum()s the floor with the per-step minimum, so the value is masked there)",
  "6 room temps, RH walked +-64 ulps onto e==1e-9 exactly; plus RH 1e-9..1e-6", "tests/entities.py / features.py: mold_safe_room_floor at e==1e-9 returns -100.0"),
"67a0550ee998a213": (CAND, "mold_safe_room_floor: the e<=1e-9 'bone-dry' guard is untested; at RH 0 the baseline returns -100.0 and the mutant -192.8 (the coordinator caller excludes RH<=0, and the consumer maximum()s the floor, so the delta is masked downstream)",
  "RH {0, -3, 1e-12} x outdoor {-20,-5,10}", "tests/entities.py / features.py: mold_safe_room_floor(indoor_rh_percent=0.0) == -100.0"),
"75b300b2bc47485f": (CAND, "mold_safe_room_floor: the 0.05 floor on surface_rh_limit is untested; limit<0.05 changes the floor and limit==0 raises ZeroDivisionError (the only call passes the constant 0.8, so the clamp pins the function contract)",
  "limit {0.04, 0.01, 0.0, -0.1}", "tests/entities.py / features.py: mold_safe_room_floor(surface_rh_limit=0.0) is finite"),
"92c063e90dafcc35": (EQ, "hp_temp>flow_set -> >= is unobservable: region 3 is continuous with region 2's 0.0 at hp_temp == flow_set (round-4 D2-03 design), 25 inputs, 0 differ",
  "wood {20,30,40,43,44.5,44.999} x floor {0,15,20,35} at hp==flow_set==45, plus 60/60", "none: equivalent by continuity"),
"6fa8436f09ad7e06": (CAND, "wood_share: the 1e-6 span floor is untested; at floor_temp == flow_set (region 2) the unclamped span raises ZeroDivisionError where the baseline returns 0.0 (floor_temp is min(T_upper,T_slab), so a bit-exact tie is measure-zero)",
  "floor_temp in {45, 45+1e-9, 46, 60} at flow_set 45", "tests/features.py: wood_share(wood 40, hp 60, flow_set 45, floor_temp 45) == 0.0"),
}
def main(key):
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    line, old, new = M[key]
    r = ROWS[key]
    cls, claim, tried, should = T[key]
    verdict = g.get("verdict")
    gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end")}
    rec = {"key": key, "site": f"custom_components/heatpump_optimizer/thermal_model.py:{line} {r['kind']}",
           "patch": f"{old.strip()} -> {new.strip()}", "function": r["function"], "cluster": r["cluster"], "gate": gate, "provisional": True}
    probe = f"dev/audit/rounds/round11/D3/s1/wave/D3-g47/probes/probe_{key}.py"
    cmd = f"PYTHONPATH=tests/hastub python3 {probe}"
    if verdict == "KILLED":
        rec.update({"class": "killed", "killed_by": g.get("killed_by"), "failing_lines": g.get("fail_lines") or g.get("failed_scripts")})
    elif verdict == "TIMEOUT":
        rec.update({"class": "timeout", "cap_s": g.get("cap_s")})
    else:
        out = subprocess.run(["python3", probe], capture_output=True, text=True, cwd=S1.parents[5], env={**__import__("os").environ, "PYTHONPATH": "tests/hastub"}).stdout
        res = [l for l in out.splitlines() if l.startswith("RESULT")]
        rec.update({"class": cls, "probe": {"path": probe, "command": cmd, "results": res, "inputs_tried": tried}, "should_fail": should})
        if cls == CAND:
            rec.update({"title": claim.split(":")[0] if False else claim[:110], "claim": claim, "step": "D3.M3", "scope": "D3-s1",
                        "class_guess": "new", "severity_claimed": "low", "stop_rule_class": "hygiene",
                        "metric_definition": next((l for l in open(probe) if l.startswith("# Metric:")), "").replace("# Metric: ", "").strip(),
                        "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe],
                        "evidence_command": cmd,
                        "perturbation": f"line {line}: {old.strip()} -> {new.strip()}; the full GATE_SCOPE=full GOLDEN_MODE=drift gate stays green; the probe's number moves under it",
                        "null_control": "probe controls (inputs where the edit cannot matter) show null_control_differing=0"})
        else:
            rec["note"] = claim
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1))
    print(key, rec["class"])
main(sys.argv[1])
