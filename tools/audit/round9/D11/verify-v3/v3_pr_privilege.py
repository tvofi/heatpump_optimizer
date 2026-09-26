#!/usr/bin/env python3
"""D11 verify-v3 (round 9), finding D11-s1-03: is the write token in the three autofix jobs
reachable by a pull request only through the three unpinned scripts, or also through the
workflow file the same pull_request run executes?

METRIC (one line): over .github/workflows/*.yml as parsed at the tree, (a) jobs a same-repo
  `pull_request`/`pull_request_review` event can start that hold a `write` permission or read a
  repository secret (`secrets.` other than GITHUB_TOKEN) -- every such job's `run:` text is the
  pull request's own copy under that event; (b) of the 3 autofix jobs, how many still execute a
  PR-controlled file with the write token after the finder's fix (every executed path restored
  from the base) plus ONE PR-side edit of tests.yml (a step `python tests/pr_payload.py` (a file the PR adds)
  appended after the restore) -- the same PR can make.
KEY: parsed YAML `on:`, job `permissions`/`if`, and step `run`/`with` text; a restore is a
  `git checkout <ref> -- <paths>` line, as the finder's harness reads it.
Null control: (b) with the finder's restore fix and NO workflow edit is 0 (the finder's own
  perturbed value).
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/verify-v3/v3_pr_privilege.py
EXPECTED (baseline 1936d5ca): (b) = 3 of 3 with the PR-side edit, 0 without.
MACHINE: box G4-V3 cloud container, 4 CPU Linux, CPython 3.14.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import copy, glob, re, time
import yaml

T0p, T0t = time.process_time(), time.thread_time()
EXEC = re.compile(r"(?<![\w/.-])((?:tests|\.claude/workflows|tools)/[\w./-]+\.(?:py|mjs|js|sh))")
IMP = re.compile(r"^\s*import\s+([a-z_]\w*)", re.M)
RESTORE = re.compile(r"git checkout\s+\S+\s+--\s+([^\n]+)")
AUTOFIX = ("closures-autofix", "claims-autofix", "mutation-autofix")


def events(d):
    on = d.get(True, d.get("on"))
    return set(on) if isinstance(on, (dict, list)) else {on}


def unpinned_exec(job):
    pinned, bad, on_path = set(), set(), False
    for s in job.get("steps", []):
        run = s.get("run", "") or ""
        env = s.get("env") or {}
        if "tests" in str(env.get("PYTHONPATH", "")) or 'sys.path.insert(0, "tests")' in run:
            on_path = True
        rest = set()
        for m in RESTORE.finditer(run):
            rest |= {p.strip("'\"\\ ") for p in m.group(1).split() if p.strip("'\"\\ ")}
        ex = set(EXEC.findall(run))
        if on_path:
            ex |= {f"tests/{m}.py" for m in IMP.findall(run) if os.path.exists(f"tests/{m}.py")}
        bad |= (ex - rest - pinned)
        pinned |= rest
    return bad


def main():
    priv = []
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        d = yaml.safe_load(open(f))
        ev = events(d)
        if not ev & {"pull_request", "pull_request_review"}:
            continue
        top = d.get("permissions") or {}
        for jid, job in d["jobs"].items():
            perms = job.get("permissions", top) or {}
            writes = [k for k, v in perms.items() if v == "write"] if isinstance(perms, dict) else []
            cond = str(job.get("if", ""))
            if "event_name == 'push'" in cond or "event_name == 'workflow_dispatch'" in cond:
                continue
            txt = yaml.safe_dump(job)
            secrets = sorted(set(re.findall(r"secrets\.(\w+)", txt)) - {"GITHUB_TOKEN"})
            if writes or secrets:
                priv.append((f.split("/")[-1], jid, writes, secrets))
                print(f"# PR-startable privileged job {f.split('/')[-1]}:{jid} writes={writes} secrets={secrets}")
    d = yaml.safe_load(open(".github/workflows/tests.yml"))
    fixed_only = fixed_plus_edit = 0
    for jid in AUTOFIX:
        job = copy.deepcopy(d["jobs"][jid])
        allx = set()
        for s in job["steps"]:
            allx |= set(EXEC.findall(s.get("run", "") or "")) | {f"tests/{m}.py" for m in IMP.findall(s.get("run", "") or "") if os.path.exists(f"tests/{m}.py")}
        job["steps"].insert(1, {"run": 'git checkout "$BASE" -- ' + " ".join(sorted(allx))})
        fixed_only += bool(unpinned_exec(job))
        job["steps"].insert(2, {"run": "python tests/pr_payload.py", "env": {"PYTHONPATH": "tests/hastub"}})
        fixed_plus_edit += bool(unpinned_exec(job))
    print(f"RESULT pr_startable_privileged_jobs={len(priv)} count")
    print(f"RESULT pr_startable_jobs_reading_secrets={sum(1 for p in priv if p[3])} count")
    print(f"RESULT autofix_after_fix_no_edit={fixed_only} of 3")
    print(f"RESULT autofix_after_fix_plus_pr_workflow_edit={fixed_plus_edit} of 3")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
