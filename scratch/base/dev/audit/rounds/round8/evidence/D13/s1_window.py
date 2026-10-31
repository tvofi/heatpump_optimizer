#!/usr/bin/env python3
"""D13 / round 8 / seat s1 -- the window: every first-parent merge on main and its API record.

METRIC: window_merges = distinct pull-request numbers returned by
`/commits/<sha>/pulls` (the API mode of policy_lint.mjs:enumerateMerges) over
`git log --first-parent SINCE..HEAD`; first-parent commits with no pull request
are counted as `stamps`. Writes the window JSON every other s1 harness reads:
per PR the body, title, author, merged_at, merge sha, head sha, issue comments
and reviews (both endpoints, paginated), and the check-run listings at the
merge commit and the head via d11lib.check_runs.
COMMAND (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/s1_window.py [--since c310541] [--head cdf82da]
EXPECTED at baseline cdf82da (exact; closed window): first_parent_commits=92
  window_merges=88 stamps=4 api_failures=0
MACHINE: any (network-bound; no timing claim). WINDOW: c310541 (the v6.6.6
stamp, the shallow clone's oldest first-parent commit) .. cdf82da (baseline).
OUTPUT: $D13S1_TMP/window.json (default /home/claude/audit-r8/tmp/D13-s1/window.json)
PERTURBATION: --since 6e2a0f2 (the v6.6.10 stamp) shrinks window_merges.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s1_gh as G  # noqa: E402
L = G.L

TMP = os.environ.get("D13S1_TMP", "/home/claude/audit-r8/tmp/D13-s1")


def git(*a):
    return subprocess.run(["git"] + list(a), capture_output=True, text=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="c310541")
    ap.add_argument("--head", default="cdf82daabcfe3777d98b31489f36df5555ec9d82")
    ap.add_argument("--out", default=os.path.join(TMP, "window.json"))
    a = ap.parse_args()
    lines = git("log", "--first-parent", "--format=%H%x09%cI%x09%s", f"{a.since}..{a.head}").splitlines()
    commits = [dict(zip(("sha", "date", "subject"), l.split("\t", 2))) for l in lines]
    prs, stamps = [], []
    seen = set()
    for c in commits:
        rows = L.api(f"repos/{L.REPO}/commits/{c['sha']}/pulls")
        if rows is None:
            continue
        if not rows:
            stamps.append(c)
            continue
        n = rows[0]["number"]
        if n in seen:
            continue
        seen.add(n)
        pr = L.api(f"repos/{L.REPO}/pulls/{n}") or {}
        comments = G.flat(L.api(f"repos/{L.REPO}/issues/{n}/comments?per_page=100", paginate=True))
        reviews = G.flat(L.api(f"repos/{L.REPO}/pulls/{n}/reviews?per_page=100", paginate=True))
        head = (pr.get("head") or {}).get("sha")
        prs.append({
            "pr": n, "sha": c["sha"], "subject": c["subject"], "committed": c["date"],
            "title": pr.get("title"), "author": (pr.get("user") or {}).get("login"),
            "merged_at": pr.get("merged_at"), "merge_commit_sha": pr.get("merge_commit_sha"),
            "head_sha": head, "body": pr.get("body") or "",
            "comments": [{"body": x.get("body"), "created_at": x.get("created_at"),
                          "user": (x.get("user") or {}).get("login")} for x in comments],
            "reviews": [{"body": x.get("body"), "submitted_at": x.get("submitted_at"),
                         "state": x.get("state"), "user": (x.get("user") or {}).get("login")}
                        for x in reviews],
            "runs_merge": L.check_runs(c["sha"]) or [],
            "runs_head": (L.check_runs(head) or []) if head else [],
        })
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump({"since": a.since, "head": a.head, "commits": commits,
                   "stamps": stamps, "prs": prs}, fh)
    print(f"window {a.since}..{a.head[:10]}  -> {a.out}")
    L.result("first_parent_commits", len(commits))
    L.result("window_merges", len(prs))
    L.result("stamps", len(stamps))
    L.result("api_calls_uncached", G.CALLS[0])
    L.footer()


if __name__ == "__main__":
    main()
