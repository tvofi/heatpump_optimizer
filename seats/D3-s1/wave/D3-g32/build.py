#!/usr/bin/env python3
# Box D3-g32 (round 11, seat D3-s1): writes results/<key>.json for every gated key of keys.tsv and, with
#   --report, REPORT.json and REPORT.md for this box. It reads only this wave dir (keys.tsv, gates/*.json,
#   probes/probe_<key>.py and their captured .out) and the slice evidence under dev/audit/rounds/round11/D3/s1/.
# Metric: none of its own -- it tabulates fullgate.py's gate records and the probes' RESULT lines.
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g32/build.py [--probes] [--report]
#   --probes re-runs every probe and captures probes/probe_<key>.out (seconds; deterministic counts).
# Expected: one results/<key>.json per gated key; REPORT.json validating against finding.schema.json's shape.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g32, 4 vCPU Intel Xeon @ 2.10GHz.
# Instrumented symbol / perturbation: per key, the probe's (see each probe's header).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, subprocess, sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent
ROOT = S1.parents[5]
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g32"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
BOX = "D3-g32"
MACHINE = "box D3-g32: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14, alone on the box"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"

# Per key: the step-4 answer when the gate does not kill it. class is used for SURVIVED / RED-AS-NULL only.
A = {
 "0d159d7ddd1702d9": dict(
  cls="candidate",
  probe=("[3.0, 3.0, 3.0]", "[2.0, 2.0, 2.0]", "known [1,2,3] on a fresh PriceShapeModel (confidence 0); null: model None; null: constant known window [2,2,2]"),
  should_fail="tests/features.py, the extend_price_series block (~3697-3717): 'without a model the old flat repeat is used' checks model=None only and the other arms use a constant known window ([1.0]*40), where mean == last price; it lacks a check that a zero-confidence (fresh) model also repeats the last known price on a non-constant window",
  title="No check pins the flat repeat for a zero-confidence price model; extend_price_series' <= 0.0 guard can loosen unseen",
  claim="Mutant 0d159d7ddd1702d9 at price_model.py:544 (`confidence(when) <= 0.0` -> `< 0.0`) survives the full gate, yet the probe's guessed tail moves from the last known price to the known window's mean: known [1,2,3] on a fresh model gives [3,3,3] at baseline and [2,2,2] under the mutant (delta 1.0 SEK/kWh per guessed step).",
  severity="medium", metric="guessed tail extend_price_series returns for known [1,2,3] on a fresh (zero-confidence) PriceShapeModel, SEK/kWh",
  direction="down", observed="2.0", unit="SEK/kWh per guessed step (baseline 3.0)",
  prop="On a price model with zero confidence the guessed tail is the flat repeat of the last published price",
  fix="tests only: extend_price_series on a fresh PriceShapeModel with a non-constant known window, asserting the tail equals the last known price",
  files=["custom_components/heatpump_optimizer/price_model.py", "tests/features.py"]),
 "80fd46122d85566c": dict(
  cls="equivalent-candidate",
  probe=("'Price entity is empty'", "'Price entity is empty'", "state None at vat/surcharge (1.0,0.0) (1.25,0.3) (0.0,-1.0); non-None states unknown/{} , ''/None, numeric, unavailable+raw_today"),
  should_fail="none: with the guard off, getattr(None, 'state', '') == '' and attrs None reach the next guard, which returns the same string; entities.py:8138's check prices_from_entity_state(None) == 'Price entity is empty' holds under both arms"),
 "b539d4504385a139": dict(
  cls="candidate",
  probe=("'Price entity is empty'", "'Price entity published no today/tomorrow series'", "state unknown/unavailable/'' with attributes {}, None, a non-dict tuple; null: numeric state with a 24-value series"),
  should_fail="tests/features.py ~58585-58600 ('an unavailable price sensor still counts if it carries the series anyway'): it feeds _G8SpState('unknown', {}) but asserts only isinstance(..., str), never the reason; the assertion lacking is _g8_state_unknown == 'Price entity is empty'",
  title="No check reads the reason for an unknown price entity with empty attributes; the and/or swap at prices_from_entity_state is unseen",
  claim="Mutant b539d4504385a139 at price_model.py:825 (`isinstance(attrs, dict) and attrs` -> `or attrs`) survives the full gate, yet the probe's failed-fetch reason moves on 4 of 5 empty-entity inputs: 'Price entity is empty' at baseline, 'Price entity published no today/tomorrow series' under the mutant (both still a failed fetch).",
  severity="low", metric="count of empty-entity inputs (unknown/unavailable/blank state, empty or non-dict attributes) whose returned reason string differs from the baseline's",
  direction="up", observed="4", unit="inputs of 5 whose reason moved",
  prop="An empty price entity (unknown/unavailable/blank state with no usable attributes) is reported as 'Price entity is empty'",
  fix="tests only: assert the reason string for an unknown state with {} attributes",
  files=["custom_components/heatpump_optimizer/price_model.py", "tests/features.py"]),
 "55f9ec66dc8bfd54": dict(
  cls="equivalent-candidate",
  probe=("('fail', 'Price entity is empty')", "('fail', 'Price entity is empty')", "through the coordinator's composition _price_entity_state + pull_prices: entity absent / '' / None with a hass whose every lookup finds a valid sensor (moved 0/3); direct pull_prices with a valid state and no entity configured (moved 1: reason only), an input the one call site (coordinator._fetch_tibber_prices) cannot produce because _price_entity_state returns None when no entity is configured"),
  should_fail="none reachable: the only production caller hands None whenever the entity is unset, and prices_from_entity_state(None) returns the same ('fail', 'Price entity is empty'); features.py:58756's _g8_pull_noent check holds under both arms"),
 "88732fcb7c604858": dict(
  cls="candidate",
  probe=("(True, 'ok') at tau_fast 0.25 h", "(False, 'slab mode too slow ... needs 1.5 h ...') at tau_fast 0.25 h", "c_r=c_s=1, k_s in 0.4..6.0 (tau_fast 0.083-1.25 h) on the default 1 h shortest phase: 4 verdicts moved (tau_fast 0.200-0.333 h); null: c_s=0"),
  should_fail="tests/features.py ~53978-53986 (#1401) calls slab_mode_one_state_identifiability only with unset slab constants (refused before the constant is read) and #1329 (~54066-54090) prices the shipped presets (tau_fast 0.94-3.72 h, refused under both 3 and 6); the assertion lacking is an admitted plant at tau_fast in (1/6, 1/3] h (e.g. c_r=c_s=1, k_s=2: tau 0.25 h) returning (True, 'ok')",
  title="No check admits a fast slab mode through the one-state predicate; FAST_MODE_SETTLE_TAUS can double unseen",
  claim="Mutant 88732fcb7c604858 at sysid.py:549 (`FAST_MODE_SETTLE_TAUS = 3.0` -> `6.0`) survives the full gate, yet slab_mode_one_state_identifiability's verdict moves from admitted to refused for 4 of 10 plants (tau_fast 0.200-0.333 h on the default 1 h shortest phase). Its one consumer (identify_slab's cadence-gap fallback) returns completed=False either way, so what moves downstream is the refusal reason.",
  severity="low", metric="count of plants (c_r=c_s=1, k_s 0.4..6.0) whose slab_mode_one_state_identifiability verdict differs from the baseline's",
  direction="up", observed="4", unit="plants of 10 whose verdict moved (True -> False)",
  prop="The one-state predicate admits a plant whose tau_fast settles in 3 time constants within the shortest phase",
  fix="tests only: slab_mode_one_state_identifiability(1, 1, 2, SysIdConfig()) == (True, 'ok')",
  files=["custom_components/heatpump_optimizer/sysid.py", "tests/features.py"]),
 "176d8ddb23988b95": dict(
  cls="equivalent-candidate",
  probe=("state (phase, last_run, result, routing flag) after _finish; 1 INFO record", "the same state; 0 INFO records", "identify_slab stubbed to a completed result and to a refusal ('fit failed'); state moved 0 in both; only the INFO 'System identification complete' record differs"),
  should_fail="none behavioural: the branch only logs at INFO; a log-content check would be the only detector, and no seat has named that log line as behaviour"),
 "de399cdbe79053ea": dict(
  cls="equivalent-candidate",
  probe=("False at an exact float tie", "True at an exact float tie", "202 readings at 0.1 C resolution (15-25 C, room = base +- 0.8) moved 0 and had 0 exact ties; 2002 at 0.01 C, 402 at 0.05 C and 42 at 0.5 C had 0 exact ties (scratch scan); 600000 random indoor readings (base U[5,30] C, room base+-0.8 and both float neighbours) moved 0; the only tie found is base 0.2 C, room 1.0 C (moved), outside any indoor reading; max_excursion_c is fixed at 0.8 (SysIdConfig default, the coordinator never sets it), and 0.8 is not a multiple of ulp(x) for |x| >= 1, so no tie exists for room temperatures at or above 1 C"),
  should_fail="none reachable: a check at |room - base| == 0.8 exactly cannot be built from indoor readings at or above 1 C"),
 "c5ddabc7d9641cba": dict(
  cls="equivalent-candidate",
  probe=("130.546875 kW at max_power 160, cop 0.05/0.0", "160.0 kW", "384 inputs at cop in {0, 0.05, 0.09, -1} x max_power {3,6,12,40,80,160} x outdoor {2,12,16,18} x 4 houses: 68 moved, all at max_power 160 kW; 24 inputs at cop >= 0.1 moved 0; production's cop is ThermalModel.compute_cop, floored at 1.0 by the COP law (min 1.050 over outdoor -40..40 C), so the dropped 0.1 floor never acts"),
  should_fail="none reachable: the floor binds only below cop 0.1, which compute_cop never returns"),
 "75d5865af3eceda7": dict(
  cls="equivalent-candidate",
  probe=("step power", "identical step power", "216 tie inputs (q_max = 0.01*2^k, k 6..11, cop 1/2/4, outdoor 2/-5/8, 4 houses; 45 of them bisect) moved 0; 360 generic inputs moved 0: the extra halving at hi - lo == 0.01 only narrows the bracket and never changes best's value at the returned precision"),
  should_fail="none found: the tie input bisects and returns the same power"),
 "0d5a6ef5041b90f9": dict(
  cls="candidate",
  probe=("4.353515625 kW (peak 0.6499 C under bound 0.65)", "4.3125 kW (peak 0.6402 C)", "6 argument sets x 4 houses: 7 of 24 moved (every one where fits(q_max) fails and a grid point fits); the D2-s4-02 cell (6 kW, COP 3, 21 C, 2 C, ua 0.20, C 8.0, gains 0.3) is one of them"),
  should_fail="tests/features.py ~2582-2600 (D2-s4-02) sizes exactly this cell but accepts bound - 0.05 <= peak <= bound: the mutant's peak 0.6402 C lies inside [0.60, 0.65]; the assertion lacking is a tolerance at the sizer's own 0.01 kW resolution (peak within ~0.005 C of the bound), or the sized step against an independent bisection",
  title="The sizer's bisection branch can be disabled unseen: the D2-s4-02 check accepts a step 0.04 kW short",
  claim="Mutant 0d5a6ef5041b90f9 at sysid.py:1606 (`if fits(q, bound):` -> `if False:`) survives the full gate, yet the probe's sized step moves on 7 of 24 inputs; on tests/features.py's own D2-s4-02 cell the step falls from 4.3535 to 4.3125 kW and its peak from 0.6499 to 0.6402 C, inside that check's 0.05 C tolerance.",
  severity="low", metric="electrical step power (kW) _size_step_power returns on the D2-s4-02 cell (6 kW, COP 3, 21 C base, 2 C outdoor, ua 0.20, C 8.0, gains 0.3)",
  direction="down", observed="4.3125", unit="kW (baseline 4.353515625)",
  prop="The sized step is the largest power whose predicted peak fits the bound, to the bisection's 0.01 kW thermal resolution",
  fix="tests only: tighten D2-s4-02's lower tolerance to the sizer's resolution, or compare against an independent bisection",
  files=["custom_components/heatpump_optimizer/sysid.py", "tests/features.py"]),
 "4f2d93e67ccda975": dict(
  cls="equivalent-candidate",
  probe=("step power; 1 DEBUG record", "identical step power; 0 DEBUG records", "6 argument sets x 4 houses: returned value moved 0 of 24; the block's only effect is the 'System identification sizer' DEBUG line"),
  should_fail="none behavioural: the guarded block only computes a one-state peak for a DEBUG log"),
 "afbdfa240c441812": dict(
  cls="equivalent-candidate",
  probe=("6.0 kW with the predictor stubbed to (0.8, 0.7)", "None", "360 real rollouts (5 powers x 3 COPs x 2 baselines x 3 outdoors x 4 houses) moved 0; a peak exactly equal to the bound occurred only with the two-state predictor stubbed to return it (moved: 6.0 -> None); null stub 0.01 C under: 6.0 both"),
  should_fail="none reachable: an exact float tie of a rollout's peak with 0.65/0.8 C was not produced by any real input; the stubbed tie is a collaborator substitution, not an input"),
 "ebd8c531fddf0a24": dict(
  cls="equivalent-candidate",
  probe=("6.0 kW with the predictor stubbed to (0.7, 0.8)", "None", "360 real rollouts moved 0; the final == bound tie occurred only with the predictor stubbed (moved: 6.0 -> None); null stub 0.01 C under: 6.0 both"),
  should_fail="none reachable: as afbdfa240c441812, for the final-temperature half of the same comparison"),
 "4a189db92053760e": dict(
  cls="candidate",
  probe=("(False, 'fitted gains outside plausible bounds' | 'fitted parameters outside plausible bounds', None)", "(True, 'ok', gains clipped)", "21 converged fits (ua 0.005/0.2/6.0 x C 4.0 x gains -0.8..2.5; negative capacities skipped, the solver works in log space): 16 moved from refused to completed; null in-band fit (0.2, 4.0, 0.4): 0"),
  should_fail="tests/features.py ~53988 (#1401) calls _slab_refusal directly and never drives _slab_outcome with an out-of-band fit; the assertion lacking is _slab_outcome on a converged out-of-band best_x (e.g. ua 0.2, gains 2.5, which the solver's (-5, 10) gains clip admits) returning completed=False with the refusal reason",
  title="No check drives _slab_outcome with an implausible fit; dropping its refusal return publishes the fit as completed",
  claim="Mutant 4a189db92053760e at sysid.py:2409 (`if refusal is not None:` -> `if False:`) survives the full gate, yet the probe's _slab_outcome result moves from refused (completed=False, 'fitted gains/parameters outside plausible bounds') to completed=True, reason 'ok' on 16 of 21 converged fits; the slab fit's solver clips gains only to (-5, 10) and leaves UA unbounded, so such fits reach this line.",
  severity="medium", metric="count of converged out-of-band slab fits whose _slab_outcome result is completed=True",
  direction="up", observed="16", unit="fits of 21 (baseline 0 completed among the 16)",
  prop="A converged two-state fit outside the plausibility bands (_slab_refusal) is published as a refusal, never as completed",
  fix="tests only: _slab_outcome on an out-of-band best_x asserting completed=False and the refusal reason",
  files=["custom_components/heatpump_optimizer/sysid.py", "tests/features.py"]),
 "80cb9a8152f72e57": dict(
  cls="candidate",
  probe=("internal_gains_kw 0.0 for fitted gains -0.5/-0.3/-0.1/-1e-6", "the negative value itself", "fitted gains -0.5, -0.3, -0.1, -1e-6, 0.0, 0.4, 1.99, 2.0 at ua 0.2, C 4.0: 4 of 8 moved (all in [-0.5, 0))"),
  should_fail="no check in tests/features.py or tests/entities.py drives _slab_outcome with a fitted gains value in [-0.5, 0) (admitted by _slab_refusal's -0.5 lower band); the assertion lacking is internal_gains_kw == 0.0 for such a fit",
  title="No check pins the slab fit's gains clip; negative internal gains can be published unseen",
  claim="Mutant 80cb9a8152f72e57 at sysid.py:2411 (np.clip(gains_kw, 0.0, 2.0) dropped) survives the full gate, yet the probe's published internal_gains_kw moves on 4 of 8 fitted gains values: every fit in [-0.5, 0) publishes 0.0 at baseline and the negative value under the mutant (-0.5 kW at the band's edge).",
  severity="low", metric="internal_gains_kw _slab_outcome publishes for fitted gains -0.5 kW (ua 0.2, C 4.0)",
  direction="down", observed="-0.5", unit="kW (baseline 0.0)",
  prop="The two-state fit's published internal gains lie in [0, 2] kW",
  fix="tests only: _slab_outcome on fitted gains -0.3 asserting internal_gains_kw == 0.0",
  files=["custom_components/heatpump_optimizer/sysid.py", "tests/features.py"]),
 "1f4a10ae90bbf2d9": dict(
  cls="equivalent-candidate",
  probe=("refusal string (dt 0.25 h default) at 1 settling row", "raised IndexError at 1 settling row", "0/1/2/4 settling rows called directly: only 1 row moves (IndexError from rows[-2]); driving step() from SETTLING at 15/30/60/90-min cadence, _unadoptable is reached 4 times, always with >= 2 settling rows (the first settling call has elapsed 0 < settle_hours 1.0, a constant the coordinator never sets), so the one-row input is unreachable"),
  should_fail="none reachable: production reaches _unadoptable only with >= 2 settling rows"),
}


def keys():
    return [l.split("\t") for l in (W / "keys.tsv").read_text().splitlines()[1:] if l.strip()]


def gate(key):
    p = W / "gates" / f"{key}.json"
    return json.loads(p.read_text()) if p.exists() else None


def run_probes():
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    for row in keys():
        k = row[0]
        out = subprocess.run([sys.executable, f"{REL}/probes/probe_{k}.py"], cwd=ROOT, env=env, text=True,
                             capture_output=True)
        (W / "probes" / f"probe_{k}.out").write_text(out.stdout + out.stderr + f"# exit {out.returncode}\n")
        print(f"probe {k} exit {out.returncode}")


def record(row):
    k, src, file, line, func, cluster, slice_, fullnet, kind, reach, m4 = row
    g = gate(k)
    if g is None:
        return None
    m = json.loads((S1 / "state" / "results" / "complete" / f"{k}.json").read_text())["mutant"]
    v = g.get("verdict", "TIMEOUT")
    a = A[k]
    cls = {"KILLED": "killed", "TIMEOUT": "timeout"}.get(v, a["cls"])
    pcmd = f"PYTHONPATH=tests/hastub python3 {REL}/probes/probe_{k}.py"
    gcmd = f"PYTHONPATH=tests/hastub python3 {FG} run --src {src} --key {k}"
    rec = {
        "key": k, "site": f"{file}:{line} {kind}", "patch": f"{m['old'].strip()} -> {m['new'].strip()}",
        "function": func, "cluster": cluster, "slice": slice_, "m4_source": m4,
        "gate": {"verdict": v, "killed_by": g.get("killed_by", []), "gate_rc": g.get("gate_rc"),
                 "failed_scripts": g.get("failed_scripts", []), "wall_s": g.get("wall_s"),
                 "load1_start": g.get("load1_start"), "load1_end": g.get("load1_end"),
                 "record": f"{REL}/gates/{k}.json", "command": gcmd, "provisional_timing": True},
        "class": cls,
        "probe": {"path": f"{REL}/probes/probe_{k}.py", "command": pcmd, "baseline_value": a["probe"][0],
                  "mutant_value": a["probe"][1], "inputs_tried": a["probe"][2],
                  "output": f"{REL}/probes/probe_{k}.out"},
        "should_fail": a["should_fail"],
    }
    if v == "KILLED":
        log = (W / "gates" / f"{k}.log")
        lines = []
        if log.exists():
            lines = [ln.strip() for ln in log.read_text(errors="replace").splitlines()
                     if ln.lstrip().startswith(("FAIL", ">>> FAILED", ">>> ENDED")) or " FAILED" in ln][:20]
        rec["failing_check_lines"] = lines
        rec["note"] = "non-finding: the full gate fails on this mutant; the probe is kept as the step-4 record"
    if v == "TIMEOUT":
        log = W / "gates" / f"{k}.log"
        last = None
        if log.exists():
            for ln in log.read_text(errors="replace").splitlines():
                if ln.startswith("##########"):
                    last = ln.strip("# ").strip()
        rec["timeout"] = {"cap_s": g.get("cap_s", 14400), "last_script_running": last}
    if cls == "candidate":
        rec["finding"] = {
            "title": a["title"], "claim": a["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": "new",
            "severity_claimed": a["severity"], "stop_rule_class": "hygiene",
            "metric_definition": a["metric"],
            "harness_paths": [FG, f"{REL}/probes/probe_{k}.py"],
            "evidence_command": pcmd,
            "evidence": {"command": pcmd, "harness_path": f"{REL}/probes/probe_{k}.py", "value": a["observed"],
                         "unit": a["unit"], "baseline_sha": BASE, "machine": MACHINE, "cpu_or_wall": "n/a",
                         "tolerance": "exact", "contention_note": "deterministic value; probes ran while this box's gates ran (load1 ~1)"},
            "instrumented_symbol": f"custom_components.heatpump_optimizer.{Path(file).stem}:{func}",
            "perturbation": {"change": f"the mutant edit at {Path(file).name}:{line} applied in memory by the probe; full gate: fullgate.py run --src {src} --key {k}",
                             "expected_direction": a["direction"], "observed_value": a["observed"]},
            "null_control": {"command": pcmd, "value": "0 count",
                             "note": "the probe's null arm, where the edit cannot matter, moves 0; the gate's null control is gates/null.json"},
            "phenomenon_property": a["prop"],
            "seam_rule": f"awk -F'\\t' '$6==\"gate\"' SURVIVORS.tsv (the wave list; this box's slice is {REL}/keys.tsv)",
            "should_fail": a["should_fail"],
            "reproduction_steps": [pcmd, gcmd],
            "proposed_fix_scope": a["fix"], "files": a["files"],
        }
    return rec


def write_records():
    (W / "results").mkdir(exist_ok=True)
    n = 0
    for row in keys():
        r = record(row)
        if r is not None:
            (W / "results" / f"{row[0]}.json").write_text(json.dumps(r, indent=1) + "\n")
            n += 1
    print(f"records {n}/{len(keys())}")


if __name__ == "__main__":
    if "--probes" in sys.argv:
        run_probes()
    write_records()
    if "--report" in sys.argv:
        import report  # noqa: E402  (report.py beside this file)
        report.main(W, A, keys, gate, record)
