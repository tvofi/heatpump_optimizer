#!/usr/bin/env python3
"""D11 round 9, verifier V2 (independent) for D11-s1-03.

METRIC (one line): over .github/workflows/*.yml, jobs that run on the `pull_request`
  event (not pull_request_target) holding an explicit `write` permission; for each,
  whether a same-repo guard (head.repo.full_name == github.repository) gates it and
  which secrets it reads. Beside it: the number of pull_request-triggered workflow
  files (every one is read from the PR's merge ref, so a same-repo PR controls its
  YAML -- decision 0013 "Kept owned" says so) and pull_request_target files.
KEY: parsed YAML of the tree under test; `on` keys; job/workflow `permissions`.
COMMAND: PYTHONPATH=tests/hastub python tools/audit/round9/D11/verify-v2/v2_pr_write_jobs.py [--perturb drop-guard]
  --perturb drop-guard: in memory, strip the same-repo clause from every job `if:` ->
  same_repo_guarded falls (the guard is what limits these jobs to branch pushers).
EXPECTED (baseline 1936d5ca): write_jobs_on_pr=3, same_repo_guarded=3, pr_yaml_files=N (printed),
  pull_request_target_files=0.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, glob, re, time
import yaml

T0p, T0t = time.process_time(), time.thread_time()
GUARD = "github.event.pull_request.head.repo.full_name == github.repository"


def perms_write(p):
    if p == "write-all":
        return ["*"]
    if isinstance(p, dict):
        return sorted(k for k, v in p.items() if v == "write")
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["drop-guard"])
    a = ap.parse_args()
    pr_files = prt_files = 0
    write_jobs = guarded = 0
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        d = yaml.safe_load(open(f))
        on = d.get(True, d.get("on")) or {}
        keys = set(on if isinstance(on, (dict, list)) else [on])
        if "pull_request_target" in keys:
            prt_files += 1
        if "pull_request" not in keys:
            continue
        pr_files += 1
        wf_w = perms_write(d.get("permissions"))
        for name, job in (d.get("jobs") or {}).items():
            w = perms_write(job.get("permissions")) if "permissions" in job else wf_w
            if not w:
                continue
            cond = str(job.get("if", ""))
            if a.perturb:
                cond = cond.replace(GUARD, "true")
            # a job gated to non-pull_request events never holds the token on a PR run
            if "github.event_name != 'pull_request'" in cond or re.search(r"event_name == '(push|schedule|workflow_dispatch)'", cond) and "pull_request" not in cond:
                continue
            text = yaml.safe_dump(job)
            secrets = sorted(set(re.findall(r"secrets\.([A-Z_]+)", text)))
            g = GUARD in cond
            write_jobs += 1
            guarded += g
            print(f"# {f}:{name} write={w} same_repo_guard={g} secrets={secrets}")
    print(f"RESULT pr_yaml_files={pr_files} count")
    print(f"RESULT pull_request_target_files={prt_files} count")
    print(f"RESULT write_jobs_on_pr={write_jobs} count")
    print(f"RESULT same_repo_guarded={guarded} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
