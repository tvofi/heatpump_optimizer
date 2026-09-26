#!/usr/bin/env python3
"""D13 / round 9 / s1 -- build the window snapshot every s1 harness reads.

Not a measurement: it reads `main`'s first-parent history over
D13_SINCE..D13_HEAD (default v6.6.0..1936d5ca, the round-9 baseline) and, for
each first-parent commit, the REST API: /commits/<sha>/pulls (the API mode of
policy_lint.mjs's enumerateMerges; ALL rows kept, not only rows[0]), then per
pull request /pulls/<n>, /issues/<n>/comments and /pulls/<n>/reviews (both
paginated), and the check-runs LISTING (paginated, pages decoded and joined)
at the merge commit and at the pull request's head. Writes window.json.gz
beside this file (trimmed: bodies of comments/reviews to 600 chars, check runs
to name/status/conclusion/start/end/app). Read-only GETs.

COMMAND: PYTHONPATH=tests/hastub python3 tools/audit/round9/D13/s1/fetch_window.py
Prints RESULT api_failures=<n>; a snapshot built with a non-zero count is not
evidence.
"""
import concurrent.futures as cf
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r9lib as L  # noqa: E402

R = f"repos/{L.REPO}"


def trim_c(c, at):
    return {"user": (c.get("user") or {}).get("login"),
            "at": c.get(at), "body": (c.get("body") or "")[:600],
            "state": c.get("state"), "commit_id": c.get("commit_id")}


def runs(sha):
    pages = L.api(f"{R}/commits/{sha}/check-runs?per_page=100", paginate=True)
    if pages is None:
        return None
    out = []
    for p in pages:
        for c in p.get("check_runs", []):
            out.append({"name": c["name"], "status": c.get("status"),
                        "conclusion": c.get("conclusion"),
                        "started_at": c.get("started_at"),
                        "completed_at": c.get("completed_at"),
                        "app": (c.get("app") or {}).get("slug")})
    return out


def pr_payload(n):
    p = L.api(f"{R}/pulls/{n}")
    if p is None:
        return None
    com = L.api(f"{R}/issues/{n}/comments?per_page=100", paginate=True)
    rev = L.api(f"{R}/pulls/{n}/reviews?per_page=100", paginate=True)
    return {
        "number": n, "title": p.get("title"),
        "author": (p.get("user") or {}).get("login"),
        "body": p.get("body") or "", "merged_at": p.get("merged_at"),
        "merge_commit_sha": p.get("merge_commit_sha"),
        "head_sha": (p.get("head") or {}).get("sha"),
        "comments": None if com is None else
        [trim_c(c, "created_at") for pg in com for c in pg],
        "reviews": None if rev is None else
        [trim_c(c, "submitted_at") for pg in rev for c in pg],
        "comment_pages": None if com is None else len(com),
        "runs_head": runs((p.get("head") or {}).get("sha")),
    }


def main():
    log = L.git("log", "--first-parent", "--format=%H%x09%P%x09%cI%x09%s",
                f"{L.WINDOW_SINCE}..{L.WINDOW_HEAD}")
    commits = []
    for line in log.splitlines():
        sha, parents, date, subj = line.split("\t", 3)
        commits.append({"sha": sha, "parents": parents.split(), "date": date,
                        "subject": subj})
    with cf.ThreadPoolExecutor(4) as ex:
        pulls = list(ex.map(lambda c: L.api(f"{R}/commits/{c['sha']}/pulls"),
                            commits))
    for c, rows in zip(commits, pulls):
        c["pulls"] = None if rows is None else [
            {"number": r["number"], "merge_commit_sha": r.get("merge_commit_sha"),
             "merged_at": r.get("merged_at")} for r in rows]
    nums = sorted({r["number"] for c in commits for r in (c["pulls"] or [])})
    with cf.ThreadPoolExecutor(4) as ex:
        prs = dict(zip(nums, ex.map(pr_payload, nums)))
        mruns = list(ex.map(lambda c: runs(c["sha"]), commits))
    for c, rr in zip(commits, mruns):
        c["runs"] = rr
    snap = {"since": L.WINDOW_SINCE, "head": L.WINDOW_HEAD,
            "commits": commits, "prs": {str(k): v for k, v in prs.items()},
            "api_failures": len(L.FAILURES),
            "failures": L.FAILURES[:50]}
    with gzip.open(L.SNAPSHOT, "wt") as fh:
        json.dump(snap, fh, separators=(",", ":"))
    L.result("first_parent_commits", len(commits))
    L.result("pull_numbers", len(nums))
    L.result("snapshot_bytes", os.path.getsize(L.SNAPSHOT), "bytes")
    L.result("api_failures", len(L.FAILURES))


if __name__ == "__main__":
    main()
