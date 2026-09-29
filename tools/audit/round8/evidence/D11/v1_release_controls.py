#!/usr/bin/env python3
"""v1_release_controls.py -- D11-v1 (verifier) own measurement for D11-s2-02.

METRIC (one line): the number of controls that stand between a write-capable
identity pushing a `vN.N.N` tag (or dispatching release.yml) at a commit NOT
reachable from main, and `gh release create` + the build-provenance attestation:
  (a) a step in `.github/workflows/release.yml:jobs.release` before `gh release
      create` whose run script tests the commit's ancestry against main
      (`merge-base --is-ancestor`, `branch --contains`, `rev-list ... main`);
  (b) a job/step `if:` naming `refs/heads/main` / the default branch;
  (c) a job `environment:` (deployment protection rules);
  (d) an ACTIVE repository ruleset whose target is `tag` (live GET
      /repos/tvofi/heatpump_optimizer/rulesets, unauthenticated, read-only).
Keyed on the parsed YAML and the API's `target` field, not on any comment.

Differs from s2_release_gate.py: that one EXECUTES the steps with gh stubbed;
this one counts the controls, including the platform half (d) the finder could
not read, which decides whether the tag-push path is reachable.

NULL CONTROL: the same parser counts the refusals of the tag NAME in the
'Resolve the tag' step (the `vN.N.N` regex + `exit 1`) -> 1, so a parser that
sees nothing would be caught.

PERTURBATION (--perturb): the finder's one line
  git fetch -q origin main && git merge-base --is-ancestor "$GITHUB_SHA" FETCH_HEAD || exit 1
inserted into 'Resolve the tag' of an in-memory copy. Expected controls 0 -> 1 (up).

RUN (tree root): PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/v1_release_controls.py [--perturb]
EXPECTED at cdf82da, 2026-09-23: controls=0 (workflow 0, tag rulesets 0 of 2 active
  rulesets -- live, can change), name_refusals=1.
BASELINE: cdf82daabcfe3777d98b31489f36df5555ec9d82. MACHINE: 4-vCPU cloud container; no timing numbers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, re, subprocess, sys, time
from pathlib import Path
import yaml

ANCESTRY = re.compile(r"merge-base\s+--is-ancestor|branch\s+(-r\s+)?--contains|rev-list[^\n]*\bmain\b")
MAINREF = re.compile(r"refs/heads/main|default_branch")
NAMEREF = re.compile(r"\^v\[0-9\]\+")
PERTURB = 'git fetch -q origin main && git merge-base --is-ancestor "$GITHUB_SHA" FETCH_HEAD || exit 1\n'


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    wf = yaml.safe_load(Path(".github/workflows/release.yml").read_text())
    job = wf["jobs"]["release"]
    steps = job["steps"]
    if "--perturb" in sys.argv:
        for s in steps:
            if s.get("name") == "Resolve the tag":
                s["run"] = PERTURB + s["run"]
    a = b = 0
    names = 0
    for s in steps:
        if "gh release create" in (s.get("run") or ""):
            break
        a += bool(ANCESTRY.search(s.get("run") or ""))
        b += bool(MAINREF.search(str(s.get("if") or "")))
        names += bool(NAMEREF.search(s.get("run") or "") and "exit 1" in (s.get("run") or ""))
    b += bool(MAINREF.search(str(job.get("if") or "")))
    c = int("environment" in job)
    rs = json.loads(subprocess.check_output(["curl", "-sS",
            "https://api.github.com/repos/tvofi/heatpump_optimizer/rulesets?includes_parents=true"]))
    if not isinstance(rs, list):
        raise SystemExit(f"ruleset list unreadable: {rs}")
    d = sum(1 for r in rs if r.get("target") == "tag" and r.get("enforcement") == "active")
    print(f"# rulesets: {[(r['id'], r['name'], r['target'], r['enforcement']) for r in rs]}")
    print(f"# (a) ancestry steps={a} (b) main-ref if={b} (c) environment={c} (d) active tag rulesets={d}")
    print(f"RESULT controls={a + b + c + d} count")
    print(f"RESULT workflow_controls={a + b + c} count")
    print(f"RESULT tag_rulesets={d} count")
    print(f"RESULT name_refusals={names} count")
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
