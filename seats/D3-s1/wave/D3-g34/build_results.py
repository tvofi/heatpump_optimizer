#!/usr/bin/env python3
# Box D3-g34's record builder (not a harness): for each key of keys.tsv whose gate record exists under gates/,
# write results/<key>.json from the gate verdict, the key's mutant, its probe's executed output (re-run here)
# and the step-4 answer below. Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/build_results.py [key ...]
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Writes only results/ under its own directory.
import json, os, re, subprocess, sys
from pathlib import Path

W = Path(__file__).resolve().parent
S1 = W.parent.parent


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
REL = "dev/audit/rounds/round11/D3/s1/wave/D3-g34"
BASE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
FEAT = ("tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', "
        "'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced "
        "baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers)")
REACH = ("identify() is harness-only at the baseline (sysid.py:1826-1835, :2306-2313): production arms with a declared "
         "plant and finishes through identify_slab, so the consequence is a wrong or unpinned result on the harness "
         "path tests/features.py and the D2/D7 harnesses drive, not a published production value")

# Step-4 answer per key: what the probe showed, the check that should have failed, and (candidates) the title.
SPEC = {
    "b8d5ec03e8eba5c7": dict(
        title="No check pins identify()'s rows<5 refusal when a >2 h gap leaves <5 intervals of >=6 samples",
        lacks="a case with >= 6 usable samples whose dt filter (dt <= 1e-3 h or > 2 h) leaves fewer than 5 rows, "
              "asserting the 'not enough usable intervals' refusal",
        prop="identify() refuses with 'not enough usable intervals' whenever fewer than 5 rows survive the dt filter"),
    "756f3bebd6a42efc": dict(
        title="No check pins identify()'s 0.1 floor on thermal_mass_prior in the gains-prior width",
        lacks="an identify() case with SysIdConfig.thermal_mass_prior below 0.1 (0.05, or 0.0 where the mutant "
              "raises ZeroDivisionError)",
        prop="the intercept prior's width uses max(thermal_mass_prior, 0.1), so a sub-0.1 prior neither raises nor "
             "narrows the ridge"),
    "3918ca4fedbfc5bb": dict(
        equiv="the rows >= 5 guard at sysid.py:1942 precedes the line, so len(rows) - n_cols >= 1 and the max(.., 1) "
              "clamp is the identity on every input that reaches it",
        lacks="none reachable: an input with rows <= 4 is refused at :1942 before :1979"),
    "84372c0eb1502d14": dict(
        title="No check pins identify()'s k_hat >= 0 clamp in the curvature correction",
        lacks="an identify() case whose first unregularised pass gives a negative UA/C slope (a noisy, drifting window) "
              "and asserts the curvature-corrected noise estimate uses k_hat = 0",
        prop="the EIV curvature correction never uses a negative first-pass slope"),
    "20f72103eda78713": dict(
        title="No check pins identify()'s skip of zero-interval triples in the noise estimate",
        lacks="an identify() case with two same-phase samples at one timestamp (h_prev = 0) asserting they do not enter "
              "the second-difference noise estimate",
        prop="a same-phase triple whose first interval is <= 1e-6 h never enters sigma2"),
    "50daaa57683189c5": dict(
        title="No check pins the h_prev <= 1e-6 h boundary of identify()'s noise-estimate skip",
        lacks="an identify() case with two same-phase samples exactly 3600 us (1e-6 h) apart",
        prop="a same-phase triple whose first interval is <= 1e-6 h never enters sigma2, the boundary included"),
    "4eeb366191982f92": dict(
        title="No check pins identify()'s three-triple minimum for the sensor-noise estimate",
        lacks="an identify() case with exactly three in-phase second differences asserting sigma2 is estimated "
              "(the EIV correction applied)",
        prop="sigma2 is estimated from three or more in-phase second differences, three included"),
    "a9bc37e9ba781833": dict(
        equiv="the rows >= 5 guard at sysid.py:1942 precedes the line, so n_rows - 1 >= 4 and the max(.., 1.0) clamp "
              "is the identity on every input that reaches it",
        lacks="none reachable"),
    "44bb0ce0b258242c": dict(
        title="No check pins identify()'s noise refusal at the sigma2 == spread/9 tie",
        lacks="an identify() case at sigma2 == x1_spread2/9 exactly (constructible in float64: dyadic temps, three "
              "triples) asserting the window is not refused as noise-dominated",
        prop="the noise refusal fires only when sigma2 strictly exceeds a ninth of the delta column's spread"),
    "b97b45a6162a2f00": dict(
        equiv="at sigma2 == 0 the second conjunct reads 0 > x1_spread2/9, false for every non-negative variance; "
              "a NaN sigma2 is false under both comparisons",
        lacks="none: no input separates `sigma2 > 0.0` from `sigma2 >= 0.0` here"),
    "6b6a8493668dde1c": dict(
        equiv="at sigma2 == 0 the mutant subtracts 0.0 from gram[0, 0] and 0.0 * sum(1/dt) (finite, dt > 1e-3 h) "
              "from rhs[0], which leaves both bit-identical",
        lacks="none: subtracting an exact zero is inert"),
    "10665a84dc064489": dict(
        title="No check pins identify()'s collinear-regressor refusal; without it a rank-1 fit completes",
        lacks="an identify() case whose power column is exactly proportional to (Tout - T) asserting completed=False "
              "with 'step gave insufficient excitation' (the mutant completes with an arbitrary UA/C split)",
        prop="a rank-deficient two-column fallback is refused, never reported as a completed identification"),
    "d7421c10ed63c281": dict(
        title="No check reaches identify()'s two-column fallback with full rank 2",
        lacks="an identify() case whose 4-column solve is singular (power constant, collinear with the intercept) but "
              "whose 2-column fallback has rank 2, asserting completed=True (UA 2.0, C 4.0)",
        prop="the two-column fallback adopts a full-rank (rank 2) fit and refuses only rank < 2"),
    "07227ec96c3e14de": dict(
        title="No check pins identify()'s 'fit gave implausible signs' refusal",
        lacks="an identify() case whose fit gives UA/C <= 1e-6 (a room running away from outdoor) asserting "
              "completed=False with 'fit gave implausible signs'",
        prop="a fit with non-positive UA/C or 1/C is refused by the sign guard, by that reason"),
    "3e78e62aa0f2e687": dict(
        equiv="the mutant differs only when the fitted 1/C equals 1e-6 exactly; 1602 inputs (+-300 floats around "
              "1e-6 as the true coefficient, 1000 random exact-model series, a negative-UA plant) never land on it, "
              "and at the tie the result would still be a refusal (C = 1e6 fails the plausible-bounds box)",
        lacks="none found: no input tried lands the fitted value on 1e-6"),
    "87c3101b5663f17b": dict(
        equiv="the mutant differs only when the fitted UA/C equals 1e-6 exactly; 1602 inputs (+-300 floats around "
              "1e-6 as the true coefficient, 1000 random exact-model series, a negative-UA plant) never land on it, "
              "and at the tie the result would still be a refusal (tau = 1e6 h fails the plausible-bounds box)",
        lacks="none found: no input tried lands the fitted value on 1e-6"),
}


def probe(key):
    rel = f"{REL}/probes/probe_{key[:8]}.py"
    env = dict(os.environ, PYTHONPATH="tests/hastub")
    out = subprocess.run([sys.executable, rel], cwd=ROOT, env=env, text=True, capture_output=True, timeout=1800).stdout
    res = dict(re.findall(r"^RESULT (\w+)=(.*)$", out, re.M))
    cases = re.findall(r"^CASE (\S+): differs=(\d)", out, re.M)
    return rel, res, cases


def build(key, row):
    m = json.loads((S1 / "state/results" / row["src"] / f"{key}.json").read_text())["mutant"]
    g = json.loads((W / "gates" / f"{key}.json").read_text())
    sp = SPEC[key]
    rec = {"key": key, "site": f"{m['file'].split('/')[-1]}:{m['line']} {m['kind']}",
           "file": m["file"], "line": m["line"],
           "patch": f"{m['old'].strip()} -> {m['new'].strip()}", "function": row["function"], "cluster": row["cluster"],
           "m4_source": row["m4_source"],
           "gate": {k: g.get(k) for k in ("verdict", "killed_by", "gate_rc", "failed_scripts", "more_fails_than_null",
                                         "wall_s", "child_cpu_s", "load1_start", "load1_end", "cap_s", "provisional")},
           "gate_record": f"{REL}/gates/{key}.json", "gate_log": f"{REL}/gates/{key}.log",
           "gate_command": f"PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src {row['src']} --key {key}"}
    v = g.get("verdict")
    if v == "KILLED":
        log = (W / "gates" / f"{key}.log").read_text(errors="replace")
        lines = [ln for ln in log.splitlines() if re.match(r"^\s*(FAIL|>>> FAILED|\d+ of \d+ .*FAILED)", ln)]
        rec.update(cls="killed", fail_lines=lines[:40])
    elif v == "TIMEOUT":
        log = W / "gates" / f"{key}.log"
        last = re.findall(r"^#{10} (.+?) #{10}$", log.read_text(errors="replace"), re.M) if log.exists() else []
        rec.update(cls="timeout", last_script=last[-1] if last else None)
    else:
        rel, res, cases = probe(key)
        moved = int(res.get("cases_differing", "0").split()[0])
        rec["probe"] = {"path": rel, "command": f"PYTHONPATH=tests/hastub python3 {rel}",
                        "first_case": res.get("first_case"), "baseline_value": res.get("outcome_baseline"),
                        "mutant_value": res.get("outcome_mutant"), "cases_differing": res.get("cases_differing"),
                        "null_differing": res.get("null_differing"),
                        "inputs_tried": [f"{n} (differs={d})" for n, d in cases if not re.match(r"(ulp|rand)", n)]
                        + ([f"{sum(1 for n, _ in cases if re.match(r'(ulp|rand)', n))} tie-search inputs (ulp-300..+300, rand0..999), "
                            f"{sum(int(d) for n, d in cases if re.match(r'(ulp|rand)', n))} differ"]
                           if any(re.match(r"(ulp|rand)", n) for n, _ in cases) else []),
                        "thread_factor": res.get("thread_factor"), "load1": res.get("load1")}
        rec["should_fail"] = f"{FEAT}; it lacks {sp['lacks']}"
        if moved and "title" in sp:
            rec["cls"] = "candidate"
            rec["finding"] = {
                "title": sp["title"], "step": "D3.M3", "scope": "D3-s1",
                "claim": (f"Mutant {key} at sysid.py:{m['line']} ({m['kind']}) survives the full gate ({v}), yet "
                          f"identify() moves on {res.get('first_case')}: baseline {res.get('outcome_baseline')}, "
                          f"mutant {res.get('outcome_mutant')} ({res.get('cases_differing')} separating inputs, "
                          f"null {res.get('null_differing')})."),
                "mechanism": f"Check that should have failed (D3.M4): {rec['should_fail']}. Reach: {REACH}.",
                "class_guess": "I1", "severity_claimed": "low", "stop_rule_class": "hygiene",
                "metric_definition": "count of probe inputs on which SystemIdentification.identify's SysIdResult repr differs between baseline and mutant",
                "phenomenon_property": sp["prop"],
                "seam_rule": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\\tSURVIVED\\t'",
                "instrumented_symbol": "custom_components.heatpump_optimizer.sysid:SystemIdentification.identify",
                "harness_paths": ["dev/audit/rounds/round11/D3/s1/fullgate.py", rel],
                "evidence_command": f"PYTHONPATH=tests/hastub python3 {rel}",
                "evidence_value": res.get("cases_differing"),
                "perturbation": {"change": f"sysid.py:{m['line']} `{m['old'].strip()}` -> `{m['new'].strip()}` in memory "
                                           f"(probe) and on disk under the full gate ({rec['gate_command']})",
                                 "expected_direction": "up", "observed_value": res.get("cases_differing")},
                "null_control": {"command": f"PYTHONPATH=tests/hastub python3 {rel}",
                                 "value": f"null_differing={res.get('null_differing')}",
                                 "note": "null cases where the edited line cannot change the result; the gate's own null "
                                         f"is {REL}/gates/null.json"},
                "proposed_fix_scope": "tests only: a tests/features.py identify() check at the separating input above that pins the baseline result",
                "files": [m["file"], "tests/features.py"],
            }
        else:
            rec["cls"] = "equivalent-candidate"
            rec["equivalence"] = sp.get("equiv", "no input tried separates the arms")
    rec["class"] = rec.pop("cls")
    return rec


def main():
    rows = {}
    lines = (W / "keys.tsv").read_text().splitlines()
    hdr = lines[0].split("\t")
    for ln in lines[1:]:
        if ln.strip():
            r = dict(zip(hdr, ln.split("\t")))
            rows[r["key"]] = r
    want = sys.argv[1:] or list(rows)
    (W / "results").mkdir(exist_ok=True)
    for key in want:
        if not (W / "gates" / f"{key}.json").exists():
            continue
        rec = build(key, rows[key])
        (W / "results" / f"{key}.json").write_text(json.dumps(rec, indent=1) + "\n")
        print(f"RECORD {key} {rec['gate']['verdict']} {rec['class']}")


if __name__ == "__main__":
    main()
