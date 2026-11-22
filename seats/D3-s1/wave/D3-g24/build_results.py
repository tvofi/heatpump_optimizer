#!/usr/bin/env python3
# Box D3-g24's per-key record builder (step 3 of the box brief). For each key of keys.tsv whose gate is
# recorded in gates/<key>.json it writes results/<key>.json from: the gate record, the mutant dict
# (state/results/<src>/<key>.json), the probe's captured output probes/out/<key>.txt (re-taken by
# `--probe`), the traced-baseline reach of the line (state/baselines-D3-u1b.json `reach.hits`), and the
# classification below (the step-4 answer, which the probe's executed numbers decide).
# Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g24/build_results.py [--probe] [key ...]
import json, os, re, subprocess, sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parents[1]


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
F = "custom_components/heatpump_optimizer/optimizer.py"
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g24"
FG = "dev/audit/rounds/round11/D3/s1/fullgate.py"

# Per key: the probe's verdict and the step-4 answer. `moved` names the RESULT that must be > 0 for a
# candidate (read from the probe output, never asserted here); `eq_reason` says why a non-moving or
# unreachable move is an equivalent-candidate.
C = {
 "1dcb273b03f63a4e": dict(metric="mutant_replay_moved", base_metric="null_replay_moved", extra=["mutant_guess_outside_bounds_mutant", "mutant_whole_moved"],
   inputs="3 DHW scenarios (power_caps_extra 3/2/1 kW, 12 h/15 min): the captured _solve_space call replayed with warm_start None, init_base x2-0.5, warm = init_base x1.5, init_base + p_max, init_base - p_max/2, all -1 kW (18 replays), plus the whole optimize() per scenario",
   eq_reason="the mutated guess leaves its bounds (guess_outside_bounds_mutant > 0) yet no returned plan, status or score moves: the starts are projected/re-scoped downstream before anything is shipped",
   assertion="a _solve_space case seeded with a warm start outside [0, p_max] asserting the returned plan/status equal the clipped-start solve (would not fail: equivalent)"),
 "c679a9939ee7b3ee": dict(metric="mutant_replay_moved", base_metric="null_replay_moved", extra=["mutant_guess_outside_bounds_mutant", "mutant_whole_moved"],
   inputs="as 1dcb273b03f63a4e (18 replays incl. warm starts above the cap-limited headroom, 3 whole solves)",
   eq_reason="the guess exceeds the headroom bound on 15 replays yet the returned plan, status and score never move",
   assertion="a warm start above the power_caps_extra headroom asserting the solve's result (would not fail: equivalent)"),
 "41d866cef7ea4115": dict(metric="mutant_cases_moved", base_metric="null_cases_moved",
   inputs="25 _stash_cases.CASES: price_known of size n-1, n, n+1, 0; pv_surplus n-1, n, n+1, 0, int; lambda 0/neg/pos x sigma None/empty/pos/zero/neg/inf/NaN; int and -0.0 prices; denormal lambda*sigma",
   eq_reason="at size == n the pad is np.zeros(0) and the concatenation equals the input (values and dtype)",
   assertion="none can fail: equivalent"),
 "fa3bb379b762e2a9": dict(metric="mutant_cases_moved", base_metric="null_cases_moved",
   inputs="the 25 _stash_cases.CASES (see 41d866cef7ea4115)",
   eq_reason="at size == n the pad is np.zeros(0); the float concatenation equals the input",
   assertion="none can fail: equivalent"),
 "ce5b92d704397d85": dict(metric="mutant_cases_moved", base_metric="null_cases_moved", extra=["reach_mutant_moved", "reach_null_moved"],
   inputs="the 25 _stash_cases.CASES plus a whole HeatPumpOptimizer.optimize (6 h, price_risk_lambda 0.5, ForecastSeries without price_sigma)",
   candidate=dict(
     title="No check solves with price_risk_lambda > 0 and no price_sigma; _stash_price_horizon's and->or is unseen",
     claim="Mutant ce5b92d704397d85 (optimizer.py:4717 `and` -> `or`) survives the full gate, yet HeatPumpOptimizer.optimize with price_risk_lambda=0.5 and a ForecastSeries carrying no price_sigma (its default None) returns an optimal plan on the baseline and raises IndexError under the mutant.",
     severity="low",
     consequence="optimize() raises for a caller using the dataclass default price_sigma=None with risk pricing on; the coordinator always passes an array (coordinator.py:1599, 7258), so no Home Assistant user path reaches it",
     metric="cases of _stash_cases.CASES whose _stash_price_horizon outcome moves under the mutant (+ whole-solve raise flag)",
     property="With price_sigma None the risk premium is skipped whatever price_risk_lambda is (optimizer.py:4717)",
     direction="up", stop="bug", cls="I1"),
   assertion="tests/features.py executes line 4717 on its traced baseline but has no case with price_risk_lambda > 0 and price_sigma None asserting the prices pass through untouched (and optimize does not raise)"),
 "dd2b698bc1d5d4b8": dict(metric="mutant_cases_moved", base_metric="null_cases_moved",
   inputs="the 25 _stash_cases.CASES (lambda 0 with sigma pos/inf/NaN/None, negative lambda included)",
   eq_reason="at lambda == 0 the risk term is 0*sigma (0, or NaN for inf sigma, which np.any(risk > 0) skips), so prices are returned untouched in both arms",
   assertion="none can fail: equivalent"),
 "aab0b73e229ad900": dict(metric="mutant_cases_moved", base_metric="null_cases_moved", extra=["reach_mutant_moved", "reach_null_moved"],
   inputs="the 25 _stash_cases.CASES plus a whole optimize (6 h, lambda 0.5, price_sigma zero except NaN on one unpublished step)",
   candidate=dict(
     title="No check feeds a NaN price_sigma on an unpublished step; risk > 0 -> >= 0 turns the plan failed unseen",
     claim="Mutant aab0b73e229ad900 (optimizer.py:4720 `risk > 0.0` -> `>= 0.0`) survives the full gate, yet with price_risk_lambda=0.5 and price_sigma zero except NaN on one unpublished step, optimize returns an optimal plan on the baseline and 'failed (no usable starting point)' under the mutant (a NaN added into the solve's prices).",
     severity="low",
     consequence="a NaN sigma reaching the solve turns the plan failed; the coordinator's sigma comes from price_model.extend_price_series (zero on known steps, PriceShapeModel.sigma elsewhere) and no NaN source was shown",
     metric="cases of _stash_cases.CASES whose _stash_price_horizon outcome moves under the mutant (+ whole-solve status flag)",
     property="The risk premium is added only where it is positive; a zero or non-finite risk leaves the prices untouched (optimizer.py:4720)",
     direction="up", stop="bug", cls="P1"),
   assertion="tests/features.py (the only closure script whose traced baseline executes line 4720) has no case with an all-zero or non-finite risk asserting the price array is returned untouched"),
 "7cb1bac951ddeb9e": dict(metric="mutant_cases_moved", base_metric="null_cases_moved", extra=["mutant_parity_breaks"],
   inputs="81 cases: 3 row_cost variants (same COP, split COP, refill derate) x coef +/-/0 x 9 end temperatures (end == cap, cap=-0/end=+0, +/-1 ulp, NaN, +/-inf, far below/above), compared bit for bit",
   eq_reason="np.where(d >= 0, d, 0) differs from the > form only at d == +/-0.0, where it returns a signed zero that the row's builtin sum absorbs bit for bit",
   assertion="none can fail: equivalent"),
 "9bfc2c6d1bfe66bd": dict(metric="mutant_cases_moved", base_metric="null_cases_moved", extra=["reach_refused_is_none"],
   inputs="12 refused vectors (None, zeros, the 1e-9 tie, 1 ulp either side, NaN, negative, cap ties) via a stubbed simulate_trajectory, plus the real ThermalModel.simulate_trajectory's refused slot",
   eq_reason="moves only for refused None (TypeError), which ThermalModel.simulate_trajectory never returns (np.zeros(n_steps) at thermal_model.py:4370; reach_refused_is_none=0): unreachable through production",
   assertion="a stubbed refused=None case would fail, but no production caller can produce one: the guard is dead code"),
 "56de38e47369b2b7": dict(metric="mutant_cases_moved", base_metric="null_cases_moved",
   inputs="the 12 _tighten_core cases",
   candidate=dict(
     title="No check refuses exactly 1e-9 kW at a step; _tighten_buffer_caps' > 1e-9 -> >= is unseen",
     claim="Mutant 56de38e47369b2b7 (optimizer.py:5123 `refused > 1e-9` -> `>= 1e-9`) survives the full gate, yet with a step refusing exactly 1e-9 kW _tighten_buffer_caps leaves the caps and returns False on the baseline and tightens that step's cap 3.0 -> 1.998 kW and returns True (one more re-solve) under the mutant.",
     severity="low",
     consequence="at the exact 1e-9 kW tie a step's buffer cap is tightened and a repair re-solve spent; a refusal of exactly 1e-9 kW is a float tie",
     metric="cases of _tighten_core.cases() whose (changed, caps, logged count) moves under the mutant",
     property="A step is tightened only when its refused heat exceeds 1e-9 kW strictly (optimizer.py:5123)",
     direction="up", stop="bug", cls="I1"),
   assertion="tests/features.py and tests/validate.py execute line 5123 on their traced baselines; neither feeds a refused value at the 1e-9 boundary"),
 "df066a5f3f3d3e0f": dict(metric="mutant_cases_moved", base_metric="null_cases_moved",
   inputs="the 12 _tighten_core cases, incl. a cap c with float(c) - 1e-9 == new_cap exactly (found by nextafter search)",
   candidate=dict(
     title="No check sets a cap with new_cap == cap - 1e-9; _tighten_buffer_caps' < -> <= is unseen",
     claim="Mutant df066a5f3f3d3e0f (optimizer.py:5139 `<` -> `<=`) survives the full gate, yet at a cap c with c - 1e-9 == new_cap exactly _tighten_buffer_caps returns False on the baseline and True (cap lowered by 1e-9 kW, one more re-solve) under the mutant.",
     severity="low",
     consequence="at the float tie a repair round is spent re-solving for a 1e-9 kW cap change, the cost the line's own comment says the margin avoids",
     metric="cases of _tighten_core.cases() whose (changed, caps, logged count) moves under the mutant",
     property="A cap counts as changed only when the new cap is below the old by more than 1e-9 kW (optimizer.py:5139)",
     direction="up", stop="bug", cls="I1"),
   assertion="tests/features.py (the only closure script whose traced baseline executes line 5139) has no tie case asserting changed False"),
 "bbcded8a73c6a2f1": dict(metric="mutant_cases_moved", base_metric="null_cases_moved",
   inputs="the 12 _tighten_core cases",
   candidate=dict(
     title="No check reads the tightened-step count _tighten_buffer_caps logs; > 1e-9 -> >= is unseen",
     claim="Mutant bbcded8a73c6a2f1 (optimizer.py:5145 `refused > 1e-9` -> `>= 1e-9` in the debug count) survives the full gate, yet with one step refusing exactly 1e-9 kW beside one refusing 0.5 kW the logged count is 1 on the baseline and 2 under the mutant.",
     severity="low",
     consequence="a DEBUG log line over-counts tightened steps at the 1e-9 kW tie; no plan or published value moves",
     metric="cases of _tighten_core.cases() whose (changed, caps, logged count) moves under the mutant",
     property="The debug line counts the steps the loop tightened, the same > 1e-9 predicate as line 5123",
     direction="up", stop="hygiene", cls="P2"),
   assertion="tests/features.py executes line 5145 but no check reads the debug count"),
 "0f03bb94bcab1682": dict(metric="mutant_downstream_moved", base_metric="null_downstream_moved", extra=["mutant_return_moved"],
   inputs="127 cases: window 15/60 min x dt 0.25/0.5/1.0/0.75/1 min x starts 00:00, 07:00, 12:00, 12:15, 12:45, 23:30 x masks off/on; dt 1e-9/0/-0.25; start None",
   eq_reason="the return moves (0 -> one whole window of steps) on every aligned start, but every consumer partitions by offset % per_window (tariff._window_partition), so PeakBilling, the capacity penalty and _grid_report never move",
   assertion="an _window_offset_steps unit asserting 0 at an aligned start would fail; no check through _peak_billing can (equivalent at the observable output)"),
 "f54d3d4c7351ac76": dict(metric="mutant_downstream_moved", base_metric="null_downstream_moved", extra=["mutant_return_moved", "reach_optimize_dt0_raises_before", "reach_offset_calls_at_dt0"],
   inputs="the 127 _window_core cases (dt 1e-9, 0, -0.25 included) plus optimize(time_step_minutes=0)",
   eq_reason="moves only at dt == 0 (ZeroDivisionError), and optimize with time_step_minutes=0 already raises on the baseline before any offset is computed: unreachable through production",
   assertion="none through production; a direct _window_offset_steps(dt=0) call separates"),
 "0270b5efaac478d2": dict(metric="mutant_cases_moved", base_metric="null_cases_moved", extra=["reach_optimize_empty_results"],
   inputs="21 cases: a real 6 h plan, its first step alone and the plan emptied x clocks at/1 us/half a step/one step/one step + 1 s before the first start, step 1, mid step 3, last start, past the end; plus 3 degenerate optimize() calls",
   eq_reason="moves only on an empty result (IndexError instead of the idle action); the one production caller (coordinator.py:6464) passes the result optimize() just returned, and optimize raises on every degenerate input tried instead of returning an empty plan (reach_optimize_empty_results=0)",
   assertion="none through production; a direct call with an empty OptimizationResult separates"),
 "68ee8d20663ac601": dict(metric="mutant_cases_moved", base_metric="null_cases_moved",
   inputs="the 21 _action_core cases, incl. now == starts[0] on a multi-step and a one-step plan",
   eq_reason="at now == starts[0] the pre-horizon branch picks i = 0 (gap 0 <= one step), which is the step the loop picks too",
   assertion="none can fail: equivalent"),
}


def results_of(txt):
    out = {}
    for m in re.finditer(r"^RESULT (\w+)=(\S+)", txt, re.M):
        out[m.group(1)] = m.group(2)
    return out


def reach_scripts(line):
    d = json.loads((S1 / "state/baselines-D3-u1b.json").read_text())
    hits = set()
    for s, v in d.items():
        h = v.get("reach", {}).get("hits", {}).get(F)
        if h and (line in h or str(line) in h):
            hits.add(s)
    return sorted(hits)


def build(key, row, probe):
    src = row["src"]
    mutant = json.loads((S1 / "state/results" / src / f"{key}.json").read_text())["mutant"]
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    pp = W / "probes" / f"probe_{key}.py"
    po = W / "probes" / "out" / f"{key}.txt"
    cmd = f"PYTHONPATH=tests/hastub python3 {REL}/probes/probe_{key}.py"
    if probe or not po.exists():
        po.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, PYTHONPATH="tests/hastub")
        r = subprocess.run(["nice", "-n", "19", sys.executable, str(pp)], cwd=ROOT, env=env, capture_output=True, text=True)
        po.write_text(r.stdout + ("\n[stderr tail]\n" + r.stderr[-2000:] if r.returncode else ""))
    txt = po.read_text()
    res = results_of(txt)
    c = C[key]
    line = int(row["line"])
    gate = {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "wall_s", "load1_start", "load1_end", "failed_scripts", "fail_lines", "summary", "child_cpu_s")}
    gate.update(path=f"{REL}/gates/{key}.json", command=f"PYTHONPATH=tests/hastub python3 {FG} run --src {src} --key {key}", provisional=True)
    rec = {"key": key, "site": f"{F}:{line} {row['kind']}", "patch": f"{mutant['old'].strip()} -> {mutant['new'].strip()}",
           "function": row["function"], "cluster": row["cluster"], "slice": row["slice"], "gate": gate}
    v = g.get("verdict")
    if v == "KILLED":
        rec["class"] = "killed"
        log = (W / "gates" / f"{key}.log")
        lines = []
        if log.exists():
            lines = [ln for ln in log.read_text(errors="replace").splitlines()
                     if re.search(r"^>>> FAILED|^\s*\d+ of \d+ .*FAILED|^FAIL\b|FAIL:", ln)][:40]
        rec["failing_check_lines"] = lines
        rec["non_finding"] = {"claim": f"{rec['site']} {rec['patch']} is pinned by the full gate (KILLED by {', '.join(g.get('killed_by') or [])})",
                              "command": gate["command"], "value": f"gate_rc={g.get('gate_rc')} killed_by={g.get('killed_by')}"}
        return rec
    if v == "TIMEOUT":
        rec["class"] = "timeout"
        log = W / "gates" / f"{key}.log"
        last = None
        if log.exists():
            hs = re.findall(r"^#{10} (.+?) #{10}$", log.read_text(errors="replace"), re.M)
            last = hs[-1] if hs else None
        rec["timeout"] = {"cap_s": g.get("cap_s"), "last_script_running": last}
        return rec
    mv = int(res.get(c["metric"], "0"))
    nb = int(res.get(c["base_metric"], "0"))
    cand = c.get("candidate")
    rec["probe"] = {"path": f"{REL}/probes/probe_{key}.py", "output": f"{REL}/probes/out/{key}.txt", "command": cmd,
                    "metric": c["metric"], "baseline_value": nb, "mutant_value": mv,
                    "extra": {k: res.get(k) for k in c.get("extra", [])},
                    "moving_cases": [ln for ln in txt.splitlines() if ln.startswith("CASE ") and ("moved=1" in ln or "downstream moved=1" in ln)][:6],
                    "inputs_tried": c["inputs"], "thread_factor": res.get("thread_factor"), "load1": res.get("load1")}
    scripts = reach_scripts(line)
    rec["should_fail"] = {"traced_scripts_executing_line": scripts, "assertion_lacking": c["assertion"]}
    if cand and mv > nb and (not c.get("extra") or "reach_mutant_moved" not in c.get("extra", []) or int(res.get("reach_mutant_moved", "0")) > 0):
        rec["class"] = "candidate"
        rec["finding"] = {
            "title": cand["title"], "claim": cand["claim"], "step": "D3.M3", "scope": "D3-s1", "class_guess": cand["cls"],
            "severity_claimed": cand["severity"], "severity_consequence": cand["consequence"], "stop_rule_class": cand["stop"],
            "metric_definition": cand["metric"], "phenomenon_property": cand["property"],
            "seam_rule": "awk -F'\\t' '$6==\"gate\"' dev/audit/rounds/round11/D3/s1/SURVIVORS.tsv",
            "instrumented_symbol": f"custom_components.heatpump_optimizer.optimizer:{row['function']}",
            "harness_paths": [FG, f"{REL}/probes/probe_{key}.py"],
            "evidence_command": cmd,
            "evidence": {"command": cmd, "harness_path": f"{REL}/probes/probe_{key}.py", "value": mv, "unit": "count",
                         "baseline_sha": BASE, "tolerance": "exact", "thread_factor": res.get("thread_factor"), "load1": res.get("load1"),
                         "machine": "box D3-g24: Linux x86_64, nproc 4, Intel Xeon @ 2.10GHz, 16 GB, venv-ci CPython 3.14"},
            "perturbation": {"change": f"{F}:{line} {rec['patch']} applied in memory by the probe; full gate: {gate['command']}",
                             "expected_direction": cand["direction"], "observed_value": mv},
            "null_control": {"command": cmd, "value": f"{c['base_metric']}={nb}", "note": "the baseline method against itself on the same inputs; the full-gate null is gates/null.json"},
            "files": [F], "proposed_fix_scope": f"a check in {scripts[0] if scripts else 'tests/features.py'} pinning the boundary the probe's moving case exercises",
            "reproduction_steps": [cmd, gate["command"]],
        }
    else:
        rec["class"] = "equivalent-candidate"
        rec["equivalent_reason"] = c.get("eq_reason") or "the probe's number does not move on any input tried"
        rec["non_finding"] = {"claim": f"{rec['site']} {rec['patch']} survives the full gate but is equivalent on every input tried: {rec['equivalent_reason']}",
                              "command": cmd, "value": f"{c['metric']}={mv} (null {nb}); " + ", ".join(f"{k}={res.get(k)}" for k in c.get("extra", []))}
    return rec


def main():
    probe = "--probe" in sys.argv
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    rows = (W / "keys.tsv").read_text().splitlines()
    hdr = rows[0].split("\t")
    for ln in rows[1:]:
        row = dict(zip(hdr, ln.split("\t")))
        k = row["key"]
        if want and k not in want:
            continue
        if not (W / "gates" / f"{k}.json").exists():
            continue
        rec = build(k, row, probe)
        (W / "results").mkdir(exist_ok=True)
        (W / "results" / f"{k}.json").write_text(json.dumps(rec, indent=1) + "\n")
        print(f"RECORD {k} {rec['gate']['verdict']} {rec['class']}")


if __name__ == "__main__":
    main()
