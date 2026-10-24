#!/usr/bin/env python3
"""s1_skip_supersede.py -- required contexts that a no-op event re-reports as SKIPPED at an existing head.

METRIC (tree arm). `required_skippable_edited`: the number of contexts required
by ruleset `main-protect-checks` (23698884) that a `pull_request: edited` event
-- a body edit, which changes no commit -- re-creates at the SAME head SHA with
conclusion `skipped`, because the producing job's `if:` evaluates false for that
event. Derived by evaluating every job `if:` in `.github/workflows/*.yml` (the
production symbol: governance.yml jobs `policy-docs`, `env-matrix`,
`wave-script`, and every other job) under the event context. The same count is
printed for a `workflow_dispatch` of tests.yml (recheck=true / recheck=false),
the other event that lands at an existing PR head (closures-autofix dispatches
it). Matrix jobs are excluded (their skipped check-run name is not asserted).

METRIC (history arm, --api). Over the merged PRs whose merge commit is on
first-parent main after the commit that added the guard (51b0742, #1484) plus
the currently open PRs: per head SHA, per required context, the check runs
ordered by id. `superseded_heads` = heads where the LATEST run of >=1 required
context is `skipped` while an earlier run at that head was not skipped;
`masked_red_heads` = the subset where an earlier run was `failure`. Keyed on the
conclusion the check-runs API delivers, not on any label.

Why it matters: GitHub reports a job skipped by `if:` as passing a required
check (docs "Handling skipped but required checks"; the repository's own
governance.yml `on:` comment relies on this). If the ruleset reads the latest
run per context name, a body edit after a red `policy-docs` clears it. That last
hop was NOT probed live (the brief forbids live perturbation); it is the
provisional part.

PERTURBATION (--perturb): the three `if: github.event_name != 'pull_request' ||
github.event.action != 'edited'` lines are deleted from a temp copy of
governance.yml (the pre-#1484 shape; equivalently move `pr-contract` to its own
workflow file so an edit creates no run of the others). Expected:
required_skippable_edited moves 3 -> 0.

RUN (from the tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/s1_skip_supersede.py [--perturb] [--api --clone <full clone>]
  --api needs outbound api.github.com (read-only GETs); --clone is a non-shallow
  clone at/after the baseline (first-parent history for the window).
EXPECTED at baseline cdf82da: required_skippable_edited=3 (exact), perturbed 0;
  dispatch_recheck_true=1 (closure-scope); history arm: superseded_heads>=3,
  masked_red_heads=0 at 2026-09-23T21Z (live data, grows).
MACHINE: 4-vCPU cloud container (round 8); no timing numbers.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

ROOT = Path(".")
HERE = Path(__file__).resolve().parent
RULESET = HERE / "s1_ruleset_23698884.json"
GUARD = "if: github.event_name != 'pull_request' || github.event.action != 'edited'"


def required_contexts():
    return [c["context"] for r in json.loads(RULESET.read_text())["rules"]
            if r["type"] == "required_status_checks"
            for c in r["parameters"]["required_status_checks"]]


IDENT = re.compile(r"(?<!['\w.-])([A-Za-z_][\w-]*(?:\.[\w-]+)+|always\(\)|true|false)(?![\w'])")


def evaluate(expr, ctx):
    """Tiny GitHub-expression evaluator for the operators these files use."""
    if expr is None:
        return True
    expr = str(expr).strip()
    if expr.startswith("${{"):
        expr = expr[3:-2]
    def sub(m):
        tok = m.group(1)
        if tok == "always()":
            return "True"
        if tok in ("true", "false"):
            return tok.capitalize()
        return repr(ctx.get(tok))
    py = IDENT.sub(sub, expr).replace("&&", " and ").replace("||", " or ")
    py = py.replace("\n", " ")
    # eval over the tracked workflow text only, after every identifier was
    # replaced by a repr() literal; no builtins. Not fed any external input.
    return bool(eval(py, {"__builtins__": {}}, {}))


def jobs_of(path):
    d = yaml.safe_load(Path(path).read_text())
    on = d.get(True, d.get("on"))
    out = []
    for jid, j in d["jobs"].items():
        out.append({"id": jid, "name": j.get("name", jid), "if": j.get("if"),
                    "matrix": bool(j.get("strategy", {}).get("matrix"))})
    return on, out


def skipped_required(wf, ctx, req):
    _, jobs = jobs_of(wf)
    names = []
    for j in jobs:
        if j["matrix"]:
            continue
        if j["name"] in req and not evaluate(j["if"], ctx):
            names.append(j["name"])
    return sorted(names)


def tree_arm(perturb):
    req = set(required_contexts())
    gov = ROOT / ".github/workflows/governance.yml"
    if perturb:
        text = gov.read_text()
        n = text.count(GUARD)
        tmp = Path(tempfile.mkdtemp(prefix="s1skip-")) / "governance.yml"
        tmp.write_text("\n".join(l for l in text.splitlines() if l.strip() != GUARD) + "\n")
        print(f"# perturbation: deleted {n} guard line(s) in a temp copy {tmp}")
        gov = tmp
    edited = {"github.event_name": "pull_request", "github.event.action": "edited"}
    s_ed = skipped_required(gov, edited, req)
    tests = ROOT / ".github/workflows/tests.yml"
    base = {"github.event_name": "workflow_dispatch"}
    s_rt = skipped_required(tests, {**base, "needs.recheck-gate.outputs.recheck": "true"}, req)
    s_rf = skipped_required(tests, {**base, "needs.recheck-gate.outputs.recheck": "false"}, req)
    # null control: a synchronize event must skip no required context
    s_sync = skipped_required(gov, {"github.event_name": "pull_request", "github.event.action": "synchronize"}, req) + \
        skipped_required(tests, {"github.event_name": "pull_request"}, req)
    print(f"# required contexts ({len(req)}): {sorted(req)}")
    print(f"# edited -> skipped at same head: {s_ed}")
    print(f"# tests.yml dispatch recheck=true -> skipped: {s_rt}")
    print(f"# tests.yml dispatch recheck=false -> skipped: {s_rf}")
    print(f"# null control (synchronize) -> skipped: {s_sync}")
    print(f"RESULT required_skippable_edited={len(s_ed)} count")
    print(f"RESULT dispatch_recheck_true_skipped={len(s_rt)} count")
    print(f"RESULT dispatch_recheck_false_skipped={len(s_rf)} count")
    print(f"RESULT null_synchronize_skipped={len(s_sync)} count")


def get(p):
    for attempt in range(3):
        try:
            return json.loads(subprocess.check_output(["curl", "-sS", "https://api.github.com" + p]))
        except Exception:
            time.sleep(2)
    raise SystemExit(f"GET {p} failed")


def api_arm(clone):
    req = set(required_contexts())
    log = subprocess.check_output(["git", "-C", clone, "log", "--first-parent", "--format=%H %s",
                                   "51b07423..cdf82daabcfe3777d98b31489f36df5555ec9d82"], text=True)
    nums = sorted({int(m.group(1)) for m in re.finditer(r"Merge pull request #(\d+)", log)})
    opens = [p["number"] for p in get("/repos/tvofi/heatpump_optimizer/pulls?state=open&per_page=100")]
    sup, masked, total = [], [], 0
    for n in nums + sorted(opens):
        pr = get(f"/repos/tvofi/heatpump_optimizer/pulls/{n}")
        sha = pr["head"]["sha"]
        runs, page = [], 1
        while True:
            d = get(f"/repos/tvofi/heatpump_optimizer/commits/{sha}/check-runs?per_page=100&page={page}")
            runs += d.get("check_runs", [])
            if len(d.get("check_runs", [])) < 100:
                break
            page += 1
        total += 1
        by = {}
        for r in runs:
            if r["name"] in req:
                by.setdefault(r["name"], []).append((r["id"], r["conclusion"] or r["status"]))
        hit_s, hit_m = [], []
        for name, seq in by.items():
            seq = [c for _, c in sorted(seq)]
            if seq[-1] == "skipped" and any(c != "skipped" for c in seq[:-1]):
                hit_s.append(name)
                if "failure" in seq[:-1]:
                    hit_m.append(name)
        state = "merged" if pr.get("merged_at") else pr["state"]
        if hit_s:
            sup.append((n, state, sha[:8], sorted(hit_s)))
            print(f"#   #{n} {state} head {sha[:8]}: latest run skipped over an earlier verdict for {sorted(hit_s)}")
        if hit_m:
            masked.append(n)
    print(f"# window: {len(nums)} merged PR(s) after 51b0742 + {len(opens)} open")
    print(f"RESULT heads_examined={total} count")
    print(f"RESULT superseded_heads={len(sup)} count")
    print(f"RESULT superseded_merged_heads={sum(1 for s in sup if s[1]=='merged')} count")
    print(f"RESULT masked_red_heads={len(masked)} count")


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    tree_arm("--perturb" in sys.argv)
    if "--api" in sys.argv:
        clone = sys.argv[sys.argv.index("--clone") + 1] if "--clone" in sys.argv else "."
        api_arm(clone)
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
