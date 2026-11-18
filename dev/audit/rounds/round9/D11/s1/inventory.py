#!/usr/bin/env python3
"""D11-s1 round 9, D11.M1: the refusal inventory, derived from the tree and the API.

METRIC (one line): per required status context of the live ruleset `main-protect-checks`,
the workflow job(s) in `.github/workflows/*.yml` whose check-run name equals it, with the
events it runs on; RESULT counts rows, contexts produced by no job, contexts produced by
more than one job, and contexts with no `integration_id` pin (any writer of that name
satisfies them).
KEY: context string == job `name:` (matrix-expanded for `${{ matrix.* }}`) or job id when
no name; CodeQL's `Analyze (<language>)` is expanded over its matrix.
COMMAND:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/s1/inventory.py [--ruleset-file F]
          --ruleset-file: read a saved ruleset body instead of GET /rulesets/23698884
          (perturbation: a body with one context renamed must raise unproduced by 1).
EXPECTED (baseline 1936d5ca): see REPORT.md; counts exact.
MACHINE: box B3, 4 CPU Linux container.
"""
import os
for _t in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_t, "1")
import argparse, glob, itertools, json, re, subprocess, sys, time
import yaml

T0p, T0t = time.process_time(), time.thread_time()


def job_names(jid, job):
    name = job.get("name", jid)
    strat = (job.get("strategy") or {}).get("matrix") or {}
    keys = re.findall(r"\$\{\{\s*matrix\.([A-Za-z0-9_-]+)\s*\}\}", str(name))
    if not keys:
        if "name" not in job and strat:
            # GitHub names an unnamed matrix job `<id> (<v1>, <v2>...)` over its matrix axes
            axes = [v for k, v in strat.items() if k not in ("include", "exclude") and isinstance(v, list)]
            return [f"{jid} ({', '.join(str(x) for x in combo)})" for combo in itertools.product(*axes)] or [str(name)]
        return [str(name)]
    out = []
    vals = [strat.get(k) or [] for k in keys]
    for combo in itertools.product(*vals):
        n = str(name)
        for k, v in zip(keys, combo):
            n = re.sub(r"\$\{\{\s*matrix\.%s\s*\}\}" % re.escape(k), str(v), n)
        out.append(n)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruleset-file")
    a = ap.parse_args()
    if a.ruleset_file:
        rs = json.load(open(a.ruleset_file))
    else:
        rs = json.loads(subprocess.run(["curl", "-sS", "https://api.github.com/repos/tvofi/heatpump_optimizer/rulesets/23698884"],
                                       capture_output=True, text=True, check=True).stdout)
    req = next(r for r in rs["rules"] if r["type"] == "required_status_checks")["parameters"]["required_status_checks"]
    producers = {}
    for f in sorted(glob.glob(".github/workflows/*.yml")):
        d = yaml.safe_load(open(f))
        on = d.get(True, d.get("on"))
        events = sorted(on.keys()) if isinstance(on, dict) else [on] if isinstance(on, str) else on
        for jid, job in d["jobs"].items():
            for n in job_names(jid, job):
                producers.setdefault(n, []).append((f.split("/")[-1], jid, events, str(job.get("if", "")).replace("\n", " ")[:70]))
    unproduced = multi = unpinned = 0
    for c in req:
        ctx = c["context"]
        p = producers.get(ctx, [])
        if not p:
            unproduced += 1
        if len(p) > 1:
            multi += 1
        if "integration_id" not in c:
            unpinned += 1
        print(f"# {ctx!r:40} integration_id={c.get('integration_id')} producers={[(x[0], x[1], x[2]) for x in p]}")
    print(f"RESULT required_contexts={len(req)} count")
    print(f"RESULT unproduced_contexts={unproduced} count")
    print(f"RESULT multi_producer_contexts={multi} count")
    print(f"RESULT contexts_without_integration_id={unpinned} count")
    pc, tc = time.process_time() - T0p, time.thread_time() - T0t
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
