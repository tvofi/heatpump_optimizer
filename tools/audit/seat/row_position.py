#!/usr/bin/env python3
"""Where a pull request's delivery row sits relative to its merge verdict.

    python3 dev/audit/harnesses/row_position.py [--limit N] [--repo O/R]

Measures the friction `bus.sh dispatch` now refuses (R9-RCA-1990 class E): a
`dev/programme/delivery/<N>.md` row written AFTER the merge verdict moves the
head off the one the reviewer measured, and `app_approve --carry` refuses a
commit of the branch's own, so it costs a re-review. The rule, per pull request:

  * V = the SHA the newest `Fix review: merge <V>` comment names.
  * R = the commit that ADDED `dev/programme/delivery/<N>.md`, read off the live
    head H (`git log --diff-filter=A`).
  * R is an ancestor of V  -> `row-before-verdict` (the row was present at the
    review; the norm).
  * R is not an ancestor of V but is in H -> `row-AFTER-verdict` (the friction).
  * no V -> `no-merge-verdict`; no R -> `no-row-in-head`.

Reads GitHub through `gh` and the object store through `git`; needs both. It is
a census, like `tests/delivery_status.py`: the window is the newest `--limit`
pull requests by number, and its answer moves with the live state it reads.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter


def sh(*argv: str) -> str:
    return subprocess.run(argv, capture_output=True, text=True).stdout.strip()


def rc(*argv: str) -> int:
    return subprocess.run(argv, capture_output=True, text=True).returncode


def newest_merge_verdict(repo: str, number: int) -> str:
    """The SHA the newest `Fix review: merge <sha>` comment on #number names."""
    lines = sh("gh", "api", "--paginate",
               f"repos/{repo}/issues/{number}/comments?per_page=100",
               "--jq",
               '.[] | select(.body | startswith("Fix review: merge ")) '
               '| .body | split("\\n")[0]').splitlines()
    return lines[-1].split()[3] if lines else ""


def row_commit(head: str, number: int) -> str:
    """The commit that added the row file, within the head (empty when none)."""
    return sh("git", "log", "--diff-filter=A", "--format=%H", "-1", head,
              "--", f"dev/programme/delivery/{number}.md")


def classify(repo: str, number: int, head: str) -> tuple[str, str, str]:
    """``(kind, row-sha, verdict-sha)`` for one pull request."""
    sh("git", "fetch", "-q", "origin", head)
    v = newest_merge_verdict(repo, number)
    r = row_commit(head, number)
    if not v:
        return "no-merge-verdict", r, ""
    if not r:
        return "no-row-in-head", r, v
    if rc("git", "merge-base", "--is-ancestor", r, v) == 0:
        return "row-before-verdict", r, v
    return "row-AFTER-verdict", r, v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
    ap.add_argument("--limit", type=int, default=60,
                    help="the newest N pull requests, any state")
    args = ap.parse_args()
    pulls = json.loads(sh("gh", "pr", "list", "--repo", args.repo,
                          "--state", "all", "--limit", str(args.limit),
                          "--json", "number,state,headRefOid"))
    pulls.sort(key=lambda p: -p["number"])
    counts: Counter[str] = Counter()
    after: list[tuple[int, str]] = []
    for p in pulls:
        kind, _r, _v = classify(args.repo, p["number"], p["headRefOid"])
        counts[kind] += 1
        if kind == "row-AFTER-verdict":
            after.append((p["number"], p["state"]))
    print(f"window: the newest {len(pulls)} pull requests on {args.repo}")
    for kind, n in counts.most_common():
        print(f"  {n:3d}  {kind}")
    print("row-AFTER-verdict:", after)
    return 0


if __name__ == "__main__":
    sys.exit(main())
