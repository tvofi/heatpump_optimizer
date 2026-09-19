#!/usr/bin/env python3
"""D13 / round 5 -- CI seconds per merge: the governance loop against the gate.

METRIC (one line). For each merge in the window: the sum of the GitHub-reported
durations of the check runs at that merge's head, split into `governance` and
`gate` seconds by the job that produced the run; reported as median and mean
seconds per merge and as `governance_share` = governance / (governance + gate).

THE GOV SET IS RE-DERIVED FROM THE WORKFLOW FILES AT THE WINDOW, not carried
from `round4/D11/governance_cost.py`. Its `GOV` names a job that no longer
exists (`record-status`) and omits two that do (`.github/workflows/governance.yml`
defines `delivery-status` and `delivery-status-publish`), so a carried set both
misses seconds and classifies by a name that has been renamed out from under
it. The rule used here, applied to the pinned tree, is:

  1. every job defined in `.github/workflows/governance.yml` is governance;
  2. a job defined in any other workflow is governance when at least one of its
     `run:` blocks names a `.claude/workflows/` script -- the job exists to
     police the policy corpus rather than the code (this picks up `briefs`,
     whose single step is `node .claude/workflows/brief_lint.mjs`);
  3. every other job is the gate.

`--gov stale` swaps in round 4's literal set so the two shares print side by
side; that arm is the measurement of what the carried set costs.

WHICH HEAD. Two arms, because they are different populations and a governance
share quoted without saying which one is unreadable:
  `merge`  the merge commit on `main` -- what the process pays AFTER the merge
           lands, which is the push-triggered run and the only one that can be
           red on main;
  `prhead` the pull request's `headRefOid` -- what the process pays BEFORE the
           merge lands, which is where `pr-contract` actually runs (it is
           `pull_request`-only and reports `skipped` at every merge commit).

Durations are the ones GitHub reports (`completed_at - started_at`), so they are
contention-immune: no wall clock on this box is read and no `load1` or
`thread_factor` applies. A run that did not conclude (skipped, in progress) is
excluded, never summed as a negative or as a zero.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 /tmp/heatpump-orch/audit-r5-D13/h5_cost.py
  ... --gov stale            # round 4's carried set, same window
  ... --pop prhead|merge|both

PERTURBATION AND DIRECTION. `--gov briefs-drop` removes `briefs` from the
governance set (a config change in this harness's own derived set, which is the
set the number is keyed on): `governance_share` must FALL on both populations,
because `briefs` runs at every merge. The control is `--gov stale`, which must
print a share strictly below the derived one, since the derived set is a
superset of the carried one apart from the phantom `record-status`.

MACHINE: any; API durations and counts, no timing claim on this box.
"""

import datetime
import json
import os
import re
import statistics
import subprocess
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d13lib as L  # noqa: E402

# Round 4's carried set, quoted verbatim so the difference is measured and not
# described: `governance_cost.py:GOV`.
STALE_GOV = {"policy-docs", "env-matrix", "wave-script", "pr-contract",
             "record", "record-status", "briefs"}

POLICY_SCRIPT = ".claude/workflows/"


def workflow_files():
    out = subprocess.run(["git", "-C", str(L.ROOT), "ls-files",
                          ".github/workflows"], capture_output=True, text=True)
    return [f for f in out.stdout.split() if f.endswith((".yml", ".yaml"))]


def read_tree(path):
    out = subprocess.run(["git", "-C", str(L.ROOT), "show",
                          f"{L.BASELINE_SHA}:{path}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"cannot read {path} at {L.BASELINE_SHA}: "
                         f"{out.stderr.strip()[:200]}")
    return out.stdout


def jobs_of(text):
    """[{name, runs_policy_script}] for one workflow file, by indentation.

    A job is a 2-space-indented mapping key under `jobs:` whose name is a legal
    job id; the job's body runs until the next such key. Parsed by hand rather
    than with PyYAML so the answer does not depend on a library version, and so
    the RUN TEXT is visible for rule 2.

    `runs_policy_script` reads `run:` blocks ONLY. A comment inside a job that
    mentions a `.claude/workflows/` script is not a step that runs one, and the
    first draft of this parser classified the `browser` job as governance on
    exactly such a comment (`tests.yml:387`, which sits in `browser`'s body and
    names `check-wave-script.mjs`). The gate/`browser` job would then have been
    charged to the governance set, which is the same class of error as the
    carried set's phantom `record-status`, one level down.
    """
    lines = text.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.rstrip() == "jobs:")
    except StopIteration:
        return []
    jobs, cur, buf = [], None, []
    for l in lines[start + 1:]:
        if l.strip() and not l.startswith(" "):
            break
        m = (l.startswith("  ") and not l.startswith("   ")
             and l.rstrip().endswith(":")
             and re.fullmatch(r"[A-Za-z0-9_-]+", l.strip()[:-1]))
        if m:
            if cur:
                jobs.append((cur, "\n".join(buf)))
            cur, buf = l.strip()[:-1], []
        elif cur is not None:
            buf.append(l)
    if cur:
        jobs.append((cur, "\n".join(buf)))
    return [{"name": n, "runs_policy_script": POLICY_SCRIPT in run_text(b)}
            for n, b in jobs]


def run_text(body):
    """The job body reduced to its `run:` blocks (inline value or block scalar)."""
    out, lines = [], body.split("\n")
    for i, l in enumerate(lines):
        m = re.match(r"^(\s*)(- )?run:\s*(.*)$", l)
        if not m:
            continue
        indent, inline = len(m.group(1)), m.group(3)
        out.append(inline)
        if inline and inline not in ("|", ">", "|-", ">-"):
            continue
        for l2 in lines[i + 1:]:
            if l2.strip() and (len(l2) - len(l2.lstrip())) <= indent:
                break
            out.append(l2)
    return "\n".join(out)


def derive_gov():
    """The governance set, from the pinned workflow files, by the rule above."""
    gov, gate, table = set(), set(), {}
    for f in workflow_files():
        text = read_tree(f)
        for j in jobs_of(text):
            table[j["name"]] = (f, j["runs_policy_script"])
            if f.endswith("governance.yml") or j["runs_policy_script"]:
                gov.add(j["name"])
            else:
                gate.add(j["name"])
    return gov, gate, table


def dur(c):
    if not c.get("started_at") or not c.get("completed_at"):
        return None
    a = datetime.datetime.fromisoformat(c["started_at"].replace("Z", "+00:00"))
    b = datetime.datetime.fromisoformat(c["completed_at"].replace("Z", "+00:00"))
    return max(0.0, (b - a).total_seconds())


def measure(merges, gov, pop):
    rows = []
    for m in merges:
        sha = m["merge_sha"] if pop == "merge" else m["prhead"]
        rs = L.check_runs(sha)
        if rs is None or not rs:
            continue
        g = t = 0.0
        rounds = 0
        for c in rs:
            d = dur(c)
            if c["name"] == "pr-contract":
                rounds += 1
            if d is None or c["conclusion"] == "skipped":
                continue
            if c["name"] in gov:
                g += d
            else:
                t += d
        rows.append({"pr": m["number"], "gov": g, "gate": t, "rounds": rounds})
    return rows


def main():
    argv = sys.argv[1:]
    gov_mode = argv[argv.index("--gov") + 1] if "--gov" in argv else "derived"
    pop_arg = argv[argv.index("--pop") + 1] if "--pop" in argv else "both"

    gov, gate, table = derive_gov()
    print(f"jobs derived from the pinned workflow files: "
          f"{len(gov) + len(gate)} "
          f"(governance {len(gov)}, gate {len(gate)})")
    print(f"  governance: {sorted(gov)}")
    print(f"  gate:       {sorted(gate)}")
    print(f"  governance via rule 2 (a .claude/workflows/ step in another file): "
          f"{sorted(n for n in gov if not table[n][0].endswith('governance.yml'))}")
    phantom = sorted(n for n in STALE_GOV if n not in gov and n not in gate)
    print(f"  carried set names {phantom} -- not a job in any workflow file")
    print(f"  carried set omits {sorted(set(gov) - STALE_GOV)}")

    use = gov
    if gov_mode == "stale":
        use = STALE_GOV
    elif gov_mode == "briefs-drop":
        use = set(gov) - {"briefs"}
    print(f"GOV SET IN USE ({gov_mode}): {sorted(use)}")

    commits = L.window_commits()
    merges, blind = L.enumerate_merges(commits)
    for m in merges:
        p = L.pr(m["number"]) or {}
        m["prhead"] = (p.get("head") or {}).get("sha") or ""
        m["title"] = p.get("title") or ""
    print(f"window {L.W0} .. {L.W1}  first-parent commits={len(commits)}  "
          f"merges={len(merges)}  unattributed={len(blind)}")

    pops = ["merge", "prhead"] if pop_arg == "both" else [pop_arg]
    for pop in pops:
        rows = measure(merges, use, pop)
        if not rows:
            print(f"!! no rows for population {pop}")
            continue
        g = [r["gov"] for r in rows]
        t = [r["gate"] for r in rows]
        rounds = [r["rounds"] for r in rows]
        print(f"\npopulation {pop}: merges measured={len(rows)}")
        print(f"  body rounds (pr-contract runs per merge): "
              f"{dict(sorted(Counter(rounds).items()))}")
        print(f"  per-merge governance seconds: median={statistics.median(g):.0f} "
              f"mean={statistics.mean(g):.0f} max={max(g):.0f}")
        print(f"  per-merge gate seconds:       median={statistics.median(t):.0f} "
              f"mean={statistics.mean(t):.0f} max={max(t):.0f}")
        share = sum(g) / (sum(g) + sum(t))
        L.result(f"{pop}_merges", len(rows))
        L.result(f"{pop}_governance_seconds_median", round(statistics.median(g)), "s")
        L.result(f"{pop}_governance_seconds_mean", round(statistics.mean(g)), "s")
        L.result(f"{pop}_gate_seconds_median", round(statistics.median(t)), "s")
        L.result(f"{pop}_gate_seconds_mean", round(statistics.mean(t)), "s")
        L.result(f"{pop}_governance_share", round(share, 4))
        L.result(f"{pop}_body_rounds_mean", round(statistics.mean(rounds), 2))
        L.result(f"{pop}_body_rounds_max", max(rounds))
        L.result(f"{pop}_body_rounds_total", sum(rounds))
        # leave-one-out over the merges: the share with the single most
        # governance-heavy merge dropped, so a share carried by one merge shows.
        worst = max(rows, key=lambda r: r["gov"])
        loo = (sum(g) - worst["gov"]) / ((sum(g) - worst["gov"]) +
                                         (sum(t) - worst["gate"]))
        L.result(f"{pop}_governance_share_leave_one_out", round(loo, 4))
        L.result(f"{pop}_gov_seconds_dropped_by_loo", round(worst["gov"]), "s")
    L.result("gov_set", ",".join(sorted(use)))
    L.result("gov_mode", gov_mode)
    L.footer()


if __name__ == "__main__":
    main()
