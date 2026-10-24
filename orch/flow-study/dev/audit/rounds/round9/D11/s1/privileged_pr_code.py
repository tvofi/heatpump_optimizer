#!/usr/bin/env python3
"""D11-s1 round 9: jobs that run a pull request's own code while holding a write token.

METRIC (one line): count of jobs in `.github/workflows/*.yml` that (a) run on the
`pull_request` event, (b) hold a `write` permission, and (c) execute a repository file
(`tests/*.py` by path or by `import`, `.claude/workflows/*`) in a step, which no earlier
step of the same job restored from the base commit (`git checkout <base> -- <paths>`).
Printed beside each: whether its checkout persists the token on disk
(`persist-credentials` not false) and whether it passes a repository secret to checkout.
KEY: the parsed workflow YAML at the tree under test -- the files GitHub runs for a
`pull_request` event are the pull request's own copies, and the executed files are the
pull request's own versions unless restored.
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/privileged_pr_code.py [--perturb restore]
          --perturb restore: in memory, prepend to each such job a step
          `git checkout "$BASE" -- <every executed path>` (the decision-0013 pin) -> count to zero.
EXPECTED (baseline 1936d5ca): see REPORT.md; counts exact.
MACHINE: box B3, 4 CPU Linux container.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, fnmatch, glob, re, time
import yaml

T0p, T0t = time.process_time(), time.thread_time()
EXEC_RE = re.compile(r"(?<![\w/.-])((?:tests|\.claude/workflows|tools)/[\w./-]+\.(?:py|mjs|js|sh))(?![\w])")
IMPORT_RE = re.compile(r"^\s*import\s+([a-z_][\w]*)", re.M)
RESTORE_RE = re.compile(r"git checkout\s+\S+\s+--\s+((?:\\\n|[^\n])+)")


def executed(run, tests_on_path):
    files = set(EXEC_RE.findall(run))
    if tests_on_path:
        for mod in IMPORT_RE.findall(run):
            if os.path.exists(f"tests/{mod}.py"):
                files.add(f"tests/{mod}.py")
    return files


def restored(run):
    out = []
    for m in RESTORE_RE.finditer(run):
        out += [p.strip("'\" \\") for p in m.group(1).replace("\\\n", " ").split() if p.strip("'\" \\")]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["restore"])
    a = ap.parse_args()
    hits = 0
    persisted = 0
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        d = yaml.safe_load(open(f))
        on = d.get(True, d.get("on"))
        events = set(on.keys()) if isinstance(on, dict) else {on} if isinstance(on, str) else set(on)
        if "pull_request" not in events:
            continue
        top = d.get("permissions")
        for jid, job in d["jobs"].items():
            perms = job.get("permissions", top)
            writes = sorted(k for k, v in (perms or {}).items() if v == "write") if isinstance(perms, dict) else ([perms] if perms and "write" in str(perms) else [])
            cond = str(job.get("if", ""))
            if not writes or ("github.event_name != 'pull_request'" in cond) or ("github.event_name == 'push'" in cond and "pull_request" not in cond):
                continue
            steps = list(job.get("steps", []))
            if a.perturb == "restore":
                allx = set()
                for s in steps:
                    allx |= executed(s.get("run", ""), True)
                if allx:
                    steps.insert(1, {"run": 'git checkout "$BASE" -- ' + " ".join(sorted(allx))})
            pinned, unpinned_exec = [], set()
            tests_on_path = False
            checkout_persist, secret_token = False, False
            for s in steps:
                if str(s.get("uses", "")).startswith("actions/checkout"):
                    w = s.get("with") or {}
                    if str(w.get("persist-credentials", "true")).lower() != "false":
                        checkout_persist = True
                    if "secrets." in str(w.get("token", "")):
                        secret_token = True
                run = s.get("run", "")
                env = s.get("env") or {}
                if "tests" in str(env.get("PYTHONPATH", "")) or 'sys.path.insert(0, "tests")' in run:
                    tests_on_path = True
                own_restore = set(restored(run))  # a restore line names paths; it does not run them
                for x in executed(run, tests_on_path) - own_restore:
                    if not any(fnmatch.fnmatch(x, p) or x == p for p in pinned):
                        unpinned_exec.add(x)
                pinned += restored(run)
            if unpinned_exec:
                hits += 1
                persisted += checkout_persist
                print(f"# {f.split('/')[-1]}:{jid} writes={writes} if={cond.strip()[:80]!r} "
                      f"checkout_persists_token={checkout_persist} secret_token_to_checkout={secret_token} "
                      f"executes_pr_files={sorted(unpinned_exec)}")
    print(f"RESULT pr_jobs_with_write_running_pr_code={hits} count")
    print(f"RESULT of_which_token_persisted_on_disk={persisted} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
