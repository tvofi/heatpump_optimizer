#!/usr/bin/env python3
"""R10-CI-SLIM: the gate stays satisfiable on a production-only, a
machinery-only and a mixed diff, from the check-run names.

    python3 dev/audit/harnesses/r10_ci_slim/gate_satisfiable.py [--workflows DIR]

THE RULE. For every name gate.REQUIRED can hold, the job that reports it (its
unit's workflow file: the job whose key, or whose `name:` up to " (", is the
name up to " (") must not carry a job-level `if:` that reads the prelude's
`machinery` or `pins` input: such a job could end SKIPPED, and gate.gate reads
a SKIPPED source as a failure. A stand-down is step-level, so the job reports
success. Each name the slimming idles WHOLE (instrument-self-tests,
mutation-pins, mutation-autofix) must be outside REQUIRED.

Then, per diff, the prelude's own outputs (prelude.machinery, prelude.pins_due,
codeql_scope.decide over the same changed list, the tree's tests/closures.json)
are printed, and gate.gate judges a run whose every required name is listed
`completed/success` -- what a step-level stand-down and a CodeQL stand-in
report -- with each idled-whole job listed `skipped`. PASS is expected on all
three.

NULL CONTROL: the same static rule over a copy of tests.yml in which
arch-instrument's stand-down is moved to the job level reports that name, and
gate.gate over a run listing it `skipped` FAILs naming it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

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
sys.path.insert(0, str(ROOT / "tools" / "ci"))
sys.path.insert(0, str(ROOT / "tools" / "pr"))
import gate as G  # noqa: E402
import prelude as P  # noqa: E402
import codeql_scope as Q  # noqa: E402

UNIT_FILE = {"tests": "tests.yml", "codeql": "codeql.yml", "governance": "governance.yml",
             "hassfest": "hassfest.yml", "validate": "validate.yml", "arch-score": "arch-score.yml",
             "budget-raise-gate": "budget-raise-gate.yml", "pr-contract": "pr-contract.yml"}
IDLED_WHOLE = {"governance / instrument-self-tests", "tests / mutation-pins", "tests / mutation-autofix"}
READS = re.compile(r"inputs\.(machinery|pins)\b")


def jobs_of(wf_dir: Path, unit: str, override: dict | None = None) -> dict:
    text = (override or {}).get(unit) or (wf_dir / UNIT_FILE[unit]).read_text()
    return yaml.safe_load(text)["jobs"]


def job_for(jobs: dict, name: str):
    stem = name.split(" (")[0]
    for key, job in jobs.items():
        if key == stem or str(job.get("name", "")).split(" (")[0] == stem:
            return key, job
    return None, None


def skippable_required(wf_dir: Path, override: dict | None = None) -> list[str]:
    bad = []
    for name in G.gate_required():
        unit, n = name.split(" / ", 1)
        key, job = job_for(jobs_of(wf_dir, unit, override), n)
        if job is None:
            bad.append(f"{name}: no job found")
        elif READS.search(str(job.get("if", ""))):
            bad.append(f"{name}: job-level if reads {READS.search(str(job['if'])).group(0)}")
    return bad


def run_for(kind_jobs: dict):
    return [{"name": k, "status": "completed", "conclusion": c, "id": 1} for k, c in kind_jobs.items()]


def judge(names_ok: list[str], skipped: list[str]) -> tuple[bool, list[str]]:
    env = {"GITHUB_SHA": "M", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "100", "GITHUB_RUN_ATTEMPT": "1"}
    ev = {"action": "synchronize", "pull_request": {"number": 7, "base": {"ref": "main"}, "head": {"sha": "H"}}}
    ctx = P.context("pull_request", ev, env)
    jobs = {n: ("completed", "success") for n in names_ok}
    jobs.update({n: ("completed", "skipped") for n in skipped})
    api = {"prelude": {"conclusion": "success", "kind": "code", "pr": "7"}, "jobs": jobs, "runs_at_head": [],
           "live_pr": {"head_sha": "M", "base_ref": "main", "state": "open", "same_repo": True},
           "open_pr_heads": set(), "reaches_cc": True}
    return G.gate(ctx, api)


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflows", default=str(ROOT / ".github" / "workflows"))
    a = ap.parse_args(argv)
    wf = Path(a.workflows)
    ok = True
    bad = skippable_required(wf)
    print(f"required names whose job-level if reads machinery/pins: {bad or 'none'} "
          f"(over {len(G.gate_required())} names)")
    ok &= not bad
    overlap = sorted(IDLED_WHOLE & set(G.gate_required()))
    print(f"idled-whole names inside REQUIRED: {overlap or 'none'}")
    ok &= not overlap
    cc = "custom_components/heatpump_optimizer/coordinator.py"
    script = next(iter(json.loads((ROOT / "tests" / "closures.json").read_text())["closures"]))
    diffs = {"production-only": [cc, script], "machinery-only": ["tools/ci/gate.py", "dev/programme/HANDOVER.md"],
             "mixed": [cc, "tools/ci/gate.py"]}
    pr_cc = G.REQUIRED["pr-cc"]
    for label, files in diffs.items():
        # A tree before C7 has neither function: every lane runs and pins measure.
        mach = getattr(P, "machinery", lambda f: True)(files)
        legs = {leg: Q.decide(leg, "pull_request", files)[0] for leg in Q.LEGS}
        skipped = sorted(IDLED_WHOLE) if not mach else []
        good, why = judge(list(pr_cc), skipped)
        print(f"{label}: files={files} machinery={mach} pins_due(delta=files)={getattr(P, "pins_due", lambda f: True)(files)} legs={legs} "
              f"-> gate {'PASS' if good else 'FAIL ' + '; '.join(why)}")
        ok &= good
    # Null control: a job-level stand-down on a required job is caught, and its SKIPPED fails the gate.
    doc = yaml.safe_load((wf / "tests.yml").read_text())
    doc["jobs"]["arch-instrument"]["if"] = f"({doc['jobs']['arch-instrument']['if']}) && inputs.machinery != 'false'"
    mutant = yaml.safe_dump(doc)
    caught = skippable_required(wf, {"tests": mutant})
    good, why = judge([n for n in pr_cc if n != "tests / arch-instrument"], ["tests / arch-instrument"])
    print(f"null control: job-level stand-down on arch-instrument -> {caught}; gate -> "
          f"{'PASS' if good else 'FAIL ' + '; '.join(why)}")
    ok &= bool(caught) and not good
    print("GATE SATISFIABLE" if ok else "GATE NOT SATISFIABLE")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
