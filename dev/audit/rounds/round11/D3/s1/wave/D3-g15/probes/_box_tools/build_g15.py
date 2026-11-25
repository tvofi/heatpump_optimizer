#!/usr/bin/env python3
"""Box D3-g15's record builder (out of tree, the box's own tool; not a harness).

  python3 build_g15.py key <key>     write results/<key>.json from gates/<key>.json + the probe output
  python3 build_g15.py report        write REPORT.json and REPORT.md from every results/<key>.json

Probe outputs are read from $HOME/probe-out/probe_<key>.out (each probe run from the baseline probe tree,
`PYTHONPATH=tests/hastub python3 <probe>`), never re-derived here.
"""
import json
import os
import re
import sys
from pathlib import Path

HOME = Path(os.environ["HOME"])
TR = HOME / "audit-r11-D3-s1"
S1 = TR / "dev/audit/rounds/round11/D3/s1"
W = S1 / "wave/D3-g15"
REL_S1 = "dev/audit/rounds/round11/D3/s1"
REL_W = f"{REL_S1}/wave/D3-g15"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
F = "custom_components/heatpump_optimizer/dhw_planner.py"
MACHINE = "box D3-g15: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on the box"
FULLGATE = f"{REL_S1}/fullgate.py"


def probe_cmd(key):
    return f"PYTHONPATH=tests/hastub python3 {REL_W}/probes/probe_{key}.py"


def gate_cmd(key):
    return f"PYTHONPATH=tests/hastub python3 {FULLGATE} run --src complete --key {key}"


# Per key: the step-4 answer, decided from the executed probe (see each probe's header and output).
# class_if_survived: candidate | equivalent-candidate. metric: the RESULT names quoted as baseline/mutant.
A = {
 "0e752f692873e876": dict(
    cls="equivalent-candidate", base="moved_in_range", mut="neg_n_mutant",
    reading="identical on every n_steps >= 0 (14 inputs); separates only at n_steps=-1 (baseline empty arrays, "
            "mutant ValueError), and optimize() hands the planner min(len(prices), len(outdoor), config.n_steps) >= 0 "
            "(reach_min_n_steps=96): unreachable through production",
    tried="n_steps -1/0/1/2/96/192 x cycle step None/0/middle/last; a production optimize() spy",
    should="none through production; only a direct call with a negative n_steps separates (tests/features.py drives "
           "_dhw_legionella_ceilings directly at line 12099 but never with n_steps < 0)"),
 "3e26ea9048504c31": dict(
    cls="equivalent-candidate", base="direct_n0_step0_baseline", mut="direct_n0_step0_mutant",
    reading="identical on n_steps >= 1 (12 inputs); separates only for a direct call at n_steps=0 WITH a cycle step "
            "(no-op -> IndexError); through the caller the due stage's own `n_steps > 0` guard returns step None at "
            "n_steps 0 (reach_n0_plan_moved=0), optimize() raises IndexError at n_steps 0 in both arms, and "
            "coordinator.py:6379 refuses a solve with fewer than 4 price steps: unreachable through production",
    tried="n_steps 0/1/2/96 x cycle step None/0/middle/last; _dhw_legionella_plan at n_steps 0 for hours_since "
          "20/150/400; optimize() on a 0-step horizon, both arms",
    should="none through production; only a direct call with n_steps 0 and a cycle step separates"),
 "77d5e6c8ea98273a": dict(
    cls="equivalent-candidate", base="decay0_baseline", mut="decay0_mutant",
    reading="identical for every in-range decay (24 inputs: cooling 0.05/0.3/3.0 C/h, dt 0.25/1 h, draws 0 and 3 kW); "
            "separates only at decay 0 (UA*dt/C >= 1: dt 9 h at the 3 C/h cap; baseline returns, mutant "
            "ZeroDivisionError), while production's smallest decay at a 1 h step is 0.88 (separate tank) and 0.81 "
            "(combi store) and the step is 15 min: unreachable through production",
    tried="cooling rate 0.05/0.3/3.0 C/h x dt 0.25/1.0 h x draws 0/3 kW x cycle step middle/last; dt 9 h at 3 C/h",
    should="none through production; only a direct call at a step of >= 8.3 h separates"),
 "a1ebeff0870dfa76": dict(
    cls="candidate", base="tie_runup_steps_baseline", mut="tie_runup_steps_mutant",
    reading="at an exact tie need == boost_top (16 of 601 draws scanned at the crossing, in-range parameters) the "
            "baseline keeps the run-up (6 steps; ceiling at step 39 60 C, requirement 60 C), the mutant cuts it "
            "(0 steps; 55 C, 20 C); off the tie no draw separates (moved_near_tie=16 = the ties; moved_random=0)",
    tried="draw at the cycle step bisected to the need == 60 C crossing and +-300 floats (601 inputs), "
          "200 L tank 55/60 C, cooling 0.1 C/h, 4 kW run, 0 C outdoor; a 30-configuration sweep (sweep_configs_with_ties) found ties in 16 "
          "of them; 60 seeded random draws",
    should="tests/features.py (executes line 784 on its traced baseline; its check 'legionella ceilings: with the "
           "rating at the charge limit no step's ceiling moves ...' at line 12109 drives _dhw_legionella_ceilings "
           "directly) lacks an assertion at the need == boost_top boundary that the run-up is kept",
    title="No check pins the legionella run-up walk at need == boost top (`>` vs `>=`)",
    severity="low", direction="to_zero",
    claim_metric="run-up steps the ceilings stage writes at an exact need == boost_top tie: baseline 6, mutant 0",
    metric_definition="count of run-up floor steps _dhw_legionella_ceilings writes when the walk's first need equals the boost top exactly",
    phenomenon="At need == boost_top the pump can still carry the ramp, so the run-up walk continues and writes its floors and ceilings",
    null="off-tie draws (scanned floats that are not exact ties, and 60 seeded random draws): 0 inputs differ",
    fix="tests only: a features.py check at an exact need == boost_top draw (the probe's tie_draw_kw) pinning the run-up the baseline writes"),
 "f1549576a94b99be": dict(
    cls="candidate", base="req_at_boost_steps_baseline", mut="req_at_boost_steps_mutant",
    reading="with a draw the pump cannot carry (20 kW-equivalent for the hour before the cycle on a 4 kW pump) the "
            "baseline cuts the walk at once (run-up max 0 C, 0 steps required at the 60 C boost top), the mutant "
            "walks on: run-up floors up to 139.13 C (20 above the boost top), 20 steps whose folded requirement is "
            "the 60 C boost top, 21 boost-top ceilings instead of 1; no draw: identical",
    tried="200 L tank 55/60 C, 4 kW run, cycle at step 40 of 96, draws 0 (null) and 20 kW on steps 36-40",
    should="tests/features.py (executes line 784; the legionella-ceilings check at line 12109) lacks a case where "
           "the pump cannot carry the ramp asserting no run-up floor exceeds the boost top and the walk stops",
    title="No check pins the legionella run-up cut when the pump cannot carry the ramp",
    severity="medium", direction="up",
    claim_metric="steps whose folded DHW requirement is the 60 C boost top: baseline 0, mutant 20",
    metric_definition="count of steps before the cycle whose min(max(floor, run-up), ceiling) reaches the boost top, under a draw the pump cannot carry",
    phenomenon="The legionella run-up never asks for more than the boost top: where the pump cannot carry the ramp the walk stops",
    null="zero draws (the guard never fires): null_moved=0",
    fix="tests only: a features.py check with a heavy pre-cycle draw asserting max(runup_temps) <= boost top and no boost-top ceiling before the walk's cut"),
 "1d455987c970dfde": dict(
    cls="equivalent-candidate", base="moved_under_tie", mut="moved_near_tie",
    reading="374 exact ties need == everyday found over 30 in-range configurations; at every one both arms agree "
            "(min(boost_top, everyday) is the value the ceiling already holds; each m is visited once); 60 random "
            "inputs agree: equivalent",
    tried="cooling 0.05/0.1/0.3/1/3 C/h x outdoor -10/0/7 C x run 2/4 kW, draw bisected to the need == 55 C crossing "
          "+-50 floats (1414 inputs, 374 ties); 60 seeded random draws and steps",
    should="none: equivalent at the tie by construction"),
 "7cd9b966a3bd0008": dict(
    cls="candidate", base="tie_runup_steps_baseline", mut="tie_runup_steps_mutant",
    reading="when the availability floor at a walk step equals that step's need exactly the baseline stops the walk "
            "(2 run-up steps at a tie on step 38), the mutant walks on (5 steps), raising the folded requirement "
            "before the cycle by 14.0886 C summed; every one of the 5 walk steps separates at its tie; a floor 1e-9 "
            "C higher: identical",
    tried="200 L tank 55/60 C, 4 kW run, cycle at step 40 of 96, floor 20 C with the tie placed on each walk step 39..35; null +1e-9 C",
    should="tests/features.py (executes line 793 on its traced baseline) lacks an assertion at need == floor that the walk stops there",
    title="No check pins the legionella run-up stop at need == availability floor (`<=` vs `<`)",
    severity="low", direction="up",
    claim_metric="run-up steps written with the floor tied to the walk's need at step 38: baseline 2, mutant 5",
    metric_definition="count of run-up floor steps _dhw_legionella_ceilings writes when one step's availability floor equals the walk's need there",
    phenomenon="Where the availability floor already meets the ramp's need the run-up walk stops; no run-up floor is written below it",
    null="the same floor raised 1e-9 C: null_moved=0",
    fix="tests only: a features.py check with floor_temps[m] equal to the baseline run-up at m pinning the run-up steps"),
 "8e9a502f439ceeeb": dict(
    cls="equivalent-candidate", base="ties_exact", mut="ties_moved",
    reading="8 exact ties temp == everyday (everyday set to the coast-down value 1..8 steps after the cycle); at every "
            "one both arms agree (max(everyday, everyday) into a ceiling already at everyday, and the next decay "
            "falls below it); 40 random inputs agree: equivalent",
    tried="cycle at step 40 of 96, everyday limit set to the exact coast-down value k = 1..8 steps after it; 40 seeded random cooling rates, limits and steps",
    should="none: equivalent at the tie by construction"),
 "f9c1b49fde6e1d52": dict(
    cls="equivalent-candidate", base="moved", mut="coast_steps_written_baseline",
    reading="147 inputs (everyday limit 15/40/55/59 C, cooling 0.05/0.3/3 C/h, horizons 96x15 min, 192x15 min, 24x1 h, "
            "cycle step first/middle/last two, and a combi store) give identical outputs; the coast-down past the "
            "limit writes max(everyday, temp<everyday) = everyday, so the break only saves iterations: equivalent",
    tried="everyday 15/40/55/59 C x cooling 0.05/0.3/3.0 C/h x (n, dt) (96, 0.25)/(192, 0.25)/(24, 1.0) x cycle step 0/mid/n-2/n-1; combi store 330 L at steps 10/48/90",
    should="none: equivalent (the break is an early exit)"),
 "79ba0b9f6b3cf22d": dict(
    cls="equivalent-candidate", base="interval0_baseline", mut="interval0_mutant",
    reading="separates only at an interval of exactly 0 days (baseline no cycle, mutant overdue cycle at step 1); "
            "every positive interval (16 inputs incl. 0.01 d) agrees; the options flow's selector floor is 1 day "
            "and the set_parameters service refuses 0 (accepts from 0.01): unreachable through production",
    tried="interval 0, 0.01, 1, 7, 30 d x hours_since 0/20/150/1000 h; the flow selector and service schema bounds",
    should="none through production; only a direct ThermalParameters(dhw_legionella_interval_days=0) separates"),
 "56d2279a568e8891": dict(
    cls="equivalent-candidate", base="n0_hours_since_400_baseline", mut="n0_hours_since_400_mutant",
    reading="identical on n_steps >= 1 (15 inputs); at n_steps 0 an overdue clock separates (baseline no cycle, "
            "mutant ValueError from an empty argmin), but optimize() at n_steps 0 already fails in the baseline "
            "(IndexError; mutant ValueError) and coordinator.py:6379 refuses any solve with fewer than 4 price "
            "steps: unreachable through production",
    tried="n_steps 0/1/2/96 x hours_since 0/20/150/167.9/168/400 h; optimize() on a 0-step horizon, both arms",
    should="none through production; only a direct call at n_steps 0 separates"),
 "31c1881164f2dcdf": dict(
    cls="candidate", base="tie_step_baseline", mut="tie_step_mutant",
    reading="when the flat-out ramp ends step 0 exactly on the reach threshold 59.999999 C (6 exact ties in 3606 "
            "scanned initial temperatures over 6 in-range configurations) the baseline calls step 0 reachable and "
            "places the cycle on the cheap step 0, the mutant calls it unreachable and places it on step 1; off the "
            "tie no input separates",
    tried="initial tank temperature bisected to the ramp[1] == 59.999999 C crossing, +-300 floats, outdoor -10/0/7 C x run 2/4 kW, hours_since 150 h, price 0.1 at step 0",
    should="tests/features.py (executes line 626 on its traced baseline) lacks an assertion at ramp == legionella_temp - 1e-6 that the step counts as reachable",
    title="No check pins the legionella reach threshold as inclusive (`>=` vs `>`)",
    severity="low", direction="up",
    claim_metric="placed cycle step when the ramp ends step 0 exactly on the reach threshold: baseline 0, mutant 1",
    metric_definition="the step _dhw_legionella_due places the cycle on when the simulated ramp hits legionella_temp - 1e-6 exactly at step 0's end",
    phenomenon="A tank whose simulated ramp reaches the disinfection threshold exactly counts as able to be there (the reach test is inclusive)",
    null="scanned initial temperatures that are not exact ties: moved_off_tie=0",
    fix="tests only: a features.py check at the probe's tie input pinning the placed step"),
 "7640e80a994db479": dict(
    cls="candidate", base="edge_solve_due_baseline", mut="edge_solve_due_mutant",
    reading="with the hard deadline exactly at the horizon's end (hours_since 144 h of a 168 h interval: deadline_step "
            "96 == n_steps, a 15-minute window the clock crosses once per interval) the baseline plans no cycle in "
            "this solve, the mutant buys it now: _dhw_legionella_due False -> True (step 1), the production "
            "optimize()'s published predictive_info dhw_legionella_due False -> True, planned hot water "
            "4.6915 -> 4.8211 kWh (+0.1295 kWh); deadline n+1 and n-1: identical",
    tried="hours_since 143.75 / 144 / 144.25 h on 96 x 15 min (deadline n+1, n, n-1), direct and through optimize()",
    should="tests/features.py (executes line 628 on its traced baseline) lacks a check at deadline_step == n_steps that the cycle is left to the elastic branch",
    title="No check pins the legionella hard-deadline branch at deadline == horizon end (`<` vs `<=`)",
    severity="low", direction="up",
    claim_metric="published dhw_legionella_due with the deadline exactly at the horizon's end: baseline False, mutant True",
    metric_definition="predictive_info['dhw_legionella_due'] of one optimize() whose legionella deadline step equals n_steps",
    phenomenon="A legionella deadline at or past the horizon's end leaves the cycle to the elastic branch; only a deadline inside the horizon forces it",
    null="hours_since 143.75 h and 144.25 h (deadline n+1, n-1): null_moved=0, null_solve_moved=0",
    fix="tests only: a features.py check at hours_since = interval - horizon pinning due False with elastic off"),
 "5224cce5f7a150cb": dict(
    cls="equivalent-candidate", base="moved", mut="inputs_tried",
    reading="432 inputs over every hard-deadline branch (124 reachable, 156 overdue reachable, 8 unreachable) agree: "
            "in this branch reach_step < n_steps, so min(..., n_steps - 1) never binds: equivalent",
    tried="n_steps 4/96/192 x hours_since 0/100/150/167/168/170/400/2000 h x initial tank 20/45/55/59.5/60/65 C x Off window none/step 0/band, seeded random prices",
    should="none: equivalent by the branch invariant"),
 "c124ea447555a04a": dict(
    cls="equivalent-candidate", base="moved", mut="inputs_tried",
    reading="432 inputs over every hard-deadline branch agree: reach_step is an np.where index or n_steps, never "
            "negative, so max(reach_step, 0) never binds (the carried u1d answer's negative reach_step does not "
            "occur): equivalent",
    tried="n_steps 4/96/192 x hours_since 0/100/150/167/168/170/400/2000 h x initial tank 20/45/55/59.5/60/65 C x Off window none/step 0/band, seeded random prices",
    should="none: equivalent by the branch invariant"),
 "8fb9093f7470e6aa": dict(
    cls="equivalent-candidate", base="moved", mut="inputs_tried",
    reading="432 inputs over every hard-deadline branch agree: the branch runs only when deadline_step < n_steps, so "
            "min(deadline_step + 1, n_steps) never binds: equivalent",
    tried="n_steps 4/96/192 x hours_since 0/100/150/167/168/170/400/2000 h x initial tank 20/45/55/59.5/60/65 C x Off window none/step 0/band, seeded random prices",
    should="none: equivalent by the branch invariant"),
}


def keys_tsv():
    rows = [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()]
    hdr = rows[0]
    return [dict(zip(hdr, r)) for r in rows[1:] if r and r[0]]


def probe_results(key):
    out = (HOME / "probe-out" / f"probe_{key}.out").read_text()
    res = {}
    for ln in out.splitlines():
        m = re.match(r"^RESULT (\w+)=(.*)$", ln)
        if m:
            res[m.group(1)] = m.group(2).strip()
    return res


def mutant_of(key):
    return json.loads((S1 / "state/results/complete" / f"{key}.json").read_text())["mutant"]


def build_key(key):
    row = next(r for r in keys_tsv() if r["key"] == key)
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    mu = mutant_of(key)
    site = f"{row['file'].split('/')[-1]}:{row['line']} {row['kind']}"
    patch = f"{mu['old'].strip()} -> {mu['new'].strip()}"
    verdict = g.get("verdict")
    gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end")}
    gate.update(failed_scripts=g.get("failed_scripts"), fail_lines=g.get("fail_lines"), summary=g.get("summary"),
                child_cpu_s=g.get("child_cpu_s"), provisional=True, record=f"{REL_W}/gates/{key}.json",
                command=gate_cmd(key))
    rec = dict(key=key, site=site, file=row["file"], line=int(row["line"]), patch=patch, function=row["function"],
               cluster=row["cluster"], slice=row["slice"], m4_source=row["m4_source"], gate=gate)
    a = A[key]
    pr = probe_results(key)
    probe = dict(path=f"{REL_W}/probes/probe_{key}.py", command=probe_cmd(key),
                 baseline_value=f"{a['base']}={pr.get(a['base'])}", mutant_value=f"{a['mut']}={pr.get(a['mut'])}",
                 results=pr, inputs_tried=a["tried"], reading=a["reading"],
                 thread_factor=float(pr.get("thread_factor", "1").split()[0]), load1=float(pr.get("load1", "0")))
    if verdict == "KILLED":
        rec["class"] = "killed"
        log = (W / "gates" / f"{key}.log")
        lines = []
        if log.exists():
            txt = log.read_text(errors="replace").splitlines()
            lines = [l for l in txt if re.match(r"^>>> (FAILED|ENDED BEFORE)", l)][:10]
            lines += [l for l in txt if re.match(r"^\s*FAIL\b", l)][:20]
        rec["killed_failing_lines"] = lines
        rec["probe"] = probe  # written before the verdict; kept as evidence, not owed
        rec["should_fail"] = "n/a: the suite fails on it (" + ", ".join(g.get("killed_by") or []) + ")"
    elif verdict == "TIMEOUT":
        rec["class"] = "timeout"
        log = W / "gates" / f"{key}.log"
        last = None
        if log.exists():
            for l in log.read_text(errors="replace").splitlines():
                m = re.match(r"^#{10} (.+?) #{10}$", l)
                if m:
                    last = m.group(1)
        rec["timeout"] = dict(cap_s=g.get("cap_s", 14400), last_script=last)
        rec["probe"] = probe
    else:
        rec["class"] = a["cls"]
        rec["probe"] = probe
        rec["should_fail"] = a["should"]
        if a["cls"] == "candidate":
            ev_val = pr.get(a["mut"])
            rec["finding"] = dict(
                scope="D3-s1", step="D3.M3", title=a["title"], severity=a["severity"],
                claim=(f"Mutant {key} at {row['file'].split('/')[-1]}:{row['line']} ({patch}) survives the full gate "
                       f"({verdict}), yet the probe moves: {a['claim_metric']}."),
                mechanism=f"{a['reading']}. Check that should have failed (D3.M4): {a['should']}.",
                class_guess="new", severity_claimed=a["severity"], stop_rule_class="hygiene",
                metric_definition=a["metric_definition"],
                instrumented_symbol=f"custom_components.heatpump_optimizer.dhw_planner:{row['function']}",
                phenomenon_property=a["phenomenon"],
                seam_rule="awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv",
                harness_paths=[FULLGATE, f"{REL_W}/probes/probe_{key}.py"],
                evidence_command=probe_cmd(key),
                evidence=dict(command=probe_cmd(key), harness_path=f"{REL_W}/probes/probe_{key}.py",
                              value=ev_val, unit=a["metric_definition"], baseline_sha=BASE, machine=MACHINE,
                              cpu_or_wall="n/a", contention_note="deterministic value; probes ran from a separate "
                              "baseline worktree while this box's gates ran (load1 ~1); gate walls are provisional",
                              tolerance="exact", load1=probe["load1"], thread_factor=probe["thread_factor"]),
                perturbation=dict(change=f"the mutant edit at {row['file'].split('/')[-1]}:{row['line']} ({patch}) "
                                  f"applied in memory by the probe; full gate: fullgate.py run --src complete --key {key}",
                                  expected_direction=a["direction"], observed_value=ev_val),
                null_control=dict(command=probe_cmd(key), value=0, note=a["null"]),
                reproduction_steps=[probe_cmd(key), gate_cmd(key)],
                proposed_fix_scope=a["fix"], files=[row["file"], "tests/features.py"])
    (W / "results").mkdir(parents=True, exist_ok=True)
    (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(f"WROTE results/{key}.json class={rec['class']} verdict={verdict}")


if __name__ == "__main__":
    if sys.argv[1] == "key":
        build_key(sys.argv[2])
    elif sys.argv[1] == "report":
        import build_g15_report
        build_g15_report.main()
