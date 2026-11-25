#!/usr/bin/env python3
"""Write results/<key>.json for every key of keys.tsv that has a gates/<key>.json (D3-g43). Idempotent."""
import csv, json, os, re, sys
W = "/root/audit-r11-D3-s1/dev/audit/rounds/round11/D3/s1/wave/D3-g43"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g43"
keys = list(csv.DictReader(open("/root/keys.tsv"), delimiter="\t"))

BATCH_TRIED = ("battery of 144 scenarios x 4 schedules: configs novalve/single-tank valve/two-tank 4-way (+wood)/valve_upper_direct_slab/"
               "smart_read two-tank/single-zone valve; states hot/cold/mid buffer, hot/cold wood, slab colder than upper floor, "
               "buffer just below the floor temperature, hot floors with cold buffer at zero power, ext heat, pmax 0/6/9, mild weather, "
               "dt 1 h/0.25/1e-4/1e-6/1e-7/0/-0.25, start_hour None/7/18, a 24-entry gains profile, valve targets")

CLS = {
 "f2ab25c56b407ef9": ("equivalent-candidate", "carnot_ref = (ref+273.15)/max(ref+273.15-t_out, 1.0) is >0 for any physical ref, so `<= 1e-9` and `< 1e-9` differ only at carnot_ref == 1e-9 bit-exactly. 576-point grid (ref 25..55, cop_reference_temp -7..12, outdoor -30..30, flow ref-1..60 and NaN): 0 moved; a scan of 4001 floats around ref=-273.15+1e-9 found none with ref+273.15 == 1e-9 exactly.", None),
 "d9a65b3770e6860a": ("equivalent-candidate", "two-zone fast path `if n_sub == 1` -> `if False`: the loop path with n_sub == 1 does one _simulate_step_two_zone at dt/1 and divides the refused sums by 1; bit-identical. 108 step scenarios (n_sub histogram 1:38, 2:62, 7:4, 25:4) x six configs: 0 moved.", None),
 "97bd985754f1099b": ("killed", "single-zone fast path `if n_sub == 1` -> `if False`: the loop path precomputes cop/q_solar once and divides refused by 1; bit-identical. Same 108-scenario step battery: 0 moved.", None),
 "7b46514aedc0a8cf": ("equivalent-candidate", "`start_hour is not None and gains_profile is not None` -> `or`: hour_i then also exists when no profile is set, but it only reaches internal_gains_at, which returns the constant when profile is None (thermal_model.py:3535-3537). " + BATCH_TRIED + ": 0 moved.", None),
 "876be7bf2f538255": ("equivalent-candidate", "`if p.two_zone_enabled and throttled` -> `or`: the extra branch only computes ua_rad/ua_floor, which are read only under the two-zone throttled branch. " + BATCH_TRIED + ": 0 moved.", None),
 "e5a0d6a548f12244": ("equivalent-candidate", "`min(drawn, max(available, 0))` -> `min(drawn, available)` in the non-wood branch: " + BATCH_TRIED + ": 0 moved, including hot floors (45 C) over a 40 C buffer at zero power, where available < 0 and drawn == 0.", None),
 "1108e8140e06404e": ("equivalent-candidate", "`/ max(dt, 1e-6)` -> `/ dt` in avail_hp (wood branch): differs only for dt <= 1e-6. " + BATCH_TRIED + ": 0 moved, dt=0 and dt=1e-7 included; production dt_hours is the plan step (>0).", None),
 "806f3255b74936a9": ("equivalent-candidate", "`/ max(dt, 1e-6)` -> `/ dt` in avail_wood: moves only at dt=0 (NaN from 0/0 or inf), 4 scenarios; every dt >= 1e-6 gives 0 moved. dt is the positive plan step in every production caller.", None),
 "daf153fda85092ff": ("equivalent-candidate", "`/ max(dt, 1e-6)` -> `/ dt` in avail (non-wood): moves only at dt=0 (2 scenarios, max abs diff 2.55e8 = inf/NaN propagation); every dt >= 1e-6 gives 0 moved. dt is the positive plan step in every production caller.", None),
 "cc34cacdd80553ed": ("candidate", None, dict(
     title="simulate_trajectory_batch drops the wood-tank trajectory and the two-tank physics when the wood-array guard is off, and no check fails",
     severity="medium", line=4553,
     claim="With `if initial_state.wood_tank_temperature is not None:` replaced by `if False:`, the batch trajectory of a two-tank 4-way install returns wood=None and its room/slab/buffer arrays diverge from the scalar simulate_trajectory by up to 52.8 K, while the full GATE_SCOPE=full gate stays as red as the null.",
     should="tests/features.py `_grad_parity`: the batched-vs-scalar bitwise cells never use a two_tank 4-way layout (wood_tank_top_entity set with wood_furnace_enabled) with a throttled valve, so np.array_equal(batch['wood'], scalar wood) and the room/buffer arrays are never compared on that layout.")),
 "a3f2b00cc4aa527e": ("candidate", None, dict(
     title="Batch two-tank supply temperature max(T_wood, T_buf) is unpinned: dropping the clamp moves trajectories by 50 K",
     severity="medium", line=4668,
     claim="Replacing `np.maximum(T_wood, T_buf)` by `T_wood` in simulate_trajectory_batch's valve supply moves the batch trajectories of two-tank installs by up to 50.5 K and breaks batch-vs-scalar parity by the same amount, yet the full gate stays as red as the null.",
     should="tests/features.py `_grad_parity` bitwise parity cell with a two-tank layout whose wood tank is colder than the buffer (T_wood < T_buf) and whose valve is throttled; the supply branch `two_tank and T_wood is not None` is never evaluated with T_wood < T_buf.")),
 "a486806b8f4ff4d7": ("candidate", None, dict(
     title="Batch floor_temp = min(T_upper, T_slab) is unpinned: the min is never exercised with the slab colder than the upper floor",
     severity="medium", line=4679,
     claim="Replacing `np.minimum(T_upper, T_slab)` by `T_upper` moves the batch trajectories by up to 8.9 K when the slab is colder than the upper floor, breaking batch-vs-scalar parity, yet the full gate stays as red as the null.",
     should="tests/features.py `_grad_parity` (and tests/optimality.py's batch use): a cell with slab_temperature < upper_floor_temperature on a throttled two-zone valve; every existing cell starts with the slab warmer than the upper floor.")),
 "f2706cbdb16a8f66": ("candidate", None, dict(
     title="Batch two-tank hp stored-heat term max(0, T_buf - floor_temp) is unpinned",
     severity="medium", line=4695,
     claim="Replacing `np.maximum(0.0, T_buf - floor_temp)` by `0.0` in the two-tank avail_hp moves the batch trajectories by up to 53.4 K and breaks batch-vs-scalar parity, yet the full gate stays as red as the null.",
     should="tests/features.py `_grad_parity`: a two-tank 4-way throttled valve cell with T_buf > floor_temp; no existing cell uses that layout.")),
 "6462c28df2f973e0": ("candidate", None, dict(
     title="Batch two-tank hp draw clamp max(avail_hp, 0) is unpinned",
     severity="low", line=4702,
     claim="Replacing `np.maximum(avail_hp, 0.0)` by `avail_hp` moves the batch trajectories by 0.0166 K (4 scenarios: two-tank, buffer just below the floor temperature at zero power) and breaks parity with the scalar path, yet the full gate stays as red as the null.",
     should="tests/features.py `_grad_parity`: a two-tank cell at zero power with the buffer at or below the floor temperature so avail_hp < 0.")),
 "7068e39e4608027f": ("candidate", None, dict(
     title="Batch two-tank wood draw clamp max(avail_wood, 0) is unpinned",
     severity="low", line=4699,
     claim="Replacing `np.maximum(avail_wood, 0.0)` by `avail_wood` moves the batch trajectories by 0.0041 K (2 scenarios: two-tank, wood tank just below the floor temperature at zero power) and breaks parity with the scalar path, yet the full gate stays as red as the null.",
     should="tests/features.py `_grad_parity`: a two-tank cell where the wood tank is at or below the floor temperature so avail_wood < 0.")),
}


def parse(out):
    t = open(out).read() if os.path.exists(out) else ""
    g = lambda pat: (re.search(pat, t) or [None, None])[1]
    return t, g(r"(?:batch|step|grid)_baseline_vs_mutant_max_abs_diff=(\S+)") or g(r"grid_moved=(\S+)"), g(r"parity_mutant=(\S+)"), g(r"scenarios_moved=(\S+)"), g(r"scenarios=(\d+)")


for r in keys:
    k = r["key"]
    gp = f"{W}/gates/{k}.json"
    rp = f"{W}/results/{k}.json"
    if not os.path.exists(gp) or os.path.exists(rp) and "--force" not in sys.argv:
        continue
    g = json.load(open(gp))
    mu = g["mutant"]
    verdict = g.get("verdict")
    cls, why, cand = CLS[k]
    probe = f"{REL}/probes/probe_{k}.py"
    t, diff, par, moved, nsc = parse(f"{W}/probes/out/{k}.txt")
    rec = {
        "key": k, "site": f"{r['file']}:{r['line']} {r['kind']}",
        "patch": f"{mu['old'].strip()} -> {mu['new'].strip()}",
        "function": r["function"], "cluster": r["cluster"],
        "gate": {x: g.get(x) for x in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "more_fails_than_null")},
        "class": "killed" if verdict == "KILLED" else ("timeout" if verdict == "TIMEOUT" else cls),
        "probe": {"path": probe, "command": f"PYTHONPATH=tests/hastub python3 {probe}",
                  "baseline_value": 0, "mutant_value": diff, "metric": "max |baseline - mutant| over the probe's arrays, scenarios moved = " + str(moved),
                  "parity_mutant_vs_scalar": par, "inputs_tried": why or "see probe battery"},
        "should_fail": (cand or {}).get("should") or "none identified: equivalent-candidate",
        "provisional": True,
    }
    if verdict == "KILLED":
        rec["killed_by"] = g.get("killed_by")
        nul = set(l.strip() for l in open(f"{W}/gates/null.log", errors="replace") if "FAIL" in l)
        rec["failing_check_lines"] = [l.strip()[:420] for l in open(f"{W}/gates/{k}.log", errors="replace")
                                      if l.lstrip().startswith("FAIL") and l.strip() not in nul][:6]
        rec["probe"]["inputs_tried"] = "not needed: the full gate kills the mutant"
    if rec["class"] == "candidate":
        rec.update({
            "title": cand["title"], "claim": cand["claim"], "step": "D3.M3", "scope": "D3-s1",
            "class_guess": "N-structure-blind", "severity_claimed": cand["severity"],
            "metric_definition": "max abs difference over the batch trajectory arrays (K) between baseline and the one-line mutant across the probe's scenario battery",
            "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", probe],
            "evidence_command": f"PYTHONPATH=tests/hastub python3 {probe}",
            "perturbation": {"change": rec["patch"] + f" (thermal_model.py:{cand['line']})", "expected_direction": "up", "observed_value": diff},
            "null_control": "the same battery against an unedited scratch copy of the baseline: baseline_vs_baseline diff 0; batch_vs_scalar_parity_baseline=0",
        })
    json.dump(rec, open(rp, "w"), indent=1)
    print("wrote", k, rec["class"])
