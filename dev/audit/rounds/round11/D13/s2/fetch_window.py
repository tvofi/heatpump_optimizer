#!/usr/bin/env python3
"""D13-s2 window snapshot: every merged pull request first-parent in the window, with
its body, title, author and EVERY issue comment and review (all pages).

Measures: nothing by itself; it writes the population M3 and M6 read, so the judge can
re-run block_classes.py / friction_keys.py offline against the same bytes, or re-fetch.

Command (from the export root, needs `gh` authenticated; network):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D13/s2/fetch_window.py \
        --since v7.1.0 --head 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 \
        --out dev/audit/rounds/round11/D13/s2/window.json
Population rule: `git log --first-parent <since>..<head>`, each commit mapped to its pull
request by `/repos/<slug>/commits/<sha>/pulls` (policy_lint.mjs enumerateMerges, API
mode; resolvePrFromCommit takes rows[0]), keeping only rows whose merge_commit_sha equals
the commit (a stamp or direct push maps to none). Failures are counted in api_failures.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B8.
Expected: RESULT merges=<n> (exact for the window), RESULT api_failures=0.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

SLUG = "tvofi/heatpump_optimizer"


def gh_lines(path, tries=4):
    """All pages of an array endpoint, one compact JSON element per line."""
    for i in range(tries):
        p = subprocess.run(["gh", "api", "--paginate", path, "--jq", ".[]"],
                           capture_output=True, text=True)
        if p.returncode == 0:
            return [json.loads(l) for l in p.stdout.splitlines() if l.strip()]
        import time
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"{path}: {p.stderr.strip()[:200]}")


def gh_obj(path, tries=4):
    for i in range(tries):
        p = subprocess.run(["gh", "api", path], capture_output=True, text=True)
        if p.returncode == 0:
            return json.loads(p.stdout)
        import time
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"{path}: {p.stderr.strip()[:200]}")


def first_line(body):
    # web-fix-wave.js parseVerdict: trim the body, then take its first line.
    return str(body or "").strip().split("\n")[0]


def keep(body):
    """Full text only for a `Fix review:` first line (the verdict population)."""
    return str(body or "") if first_line(body).lower().startswith("fix review") else None


def one(commit):
    sha, subject = commit
    out = {"sha": sha, "subject": subject}
    try:
        rows = gh_lines(f"repos/{SLUG}/commits/{sha}/pulls")
    except Exception as e:  # noqa: BLE001
        out["error"] = f"commits/pulls: {e}"
        return out
    rows = [r for r in rows if r.get("merge_commit_sha") == sha] or []
    if not rows:
        out["pr"] = None
        return out
    n = rows[0]["number"]
    out["pr"] = n
    try:
        pr = gh_obj(f"repos/{SLUG}/pulls/{n}")
        comments = gh_lines(f"repos/{SLUG}/issues/{n}/comments?per_page=100")
        reviews = gh_lines(f"repos/{SLUG}/pulls/{n}/reviews?per_page=100")
    except Exception as e:  # noqa: BLE001
        out["error"] = f"pr {n}: {e}"
        return out
    out.update({
        "title": pr.get("title") or "",
        "author": (pr.get("user") or {}).get("login"),
        "head_ref": (pr.get("head") or {}).get("ref"),
        "merged_at": pr.get("merged_at"),
        "body": pr.get("body") or "",
        "comments": [{"i": i, "id": c["id"], "user": (c.get("user") or {}).get("login"),
                      "created_at": c.get("created_at"), "first": first_line(c.get("body")),
                      "body": keep(c.get("body"))}
                     for i, c in enumerate(comments)],
        "reviews": [{"i": i, "id": r["id"], "user": (r.get("user") or {}).get("login"),
                     "submitted_at": r.get("submitted_at"), "state": r.get("state"),
                     "first": first_line(r.get("body")), "body": keep(r.get("body"))}
                    for i, r in enumerate(reviews)],
    })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    log = subprocess.run(["git", "log", "--first-parent", "--format=%H%x09%s",
                          f"{a.since}..{a.head}"], capture_output=True, text=True, check=True)
    commits = [tuple(l.split("\t", 1)) for l in log.stdout.splitlines() if "\t" in l]
    with ThreadPoolExecutor(a.jobs) as ex:
        rows = list(ex.map(one, commits))
    fails = [r for r in rows if "error" in r]
    merges = [r for r in rows if r.get("pr") and "error" not in r]
    snap = {"since": a.since, "head": a.head, "first_parent_commits": len(commits),
            "api_failures": [r["error"] for r in fails], "merges": merges,
            "non_pr_commits": [r["sha"] for r in rows if "error" not in r and not r.get("pr")]}
    with open(a.out, "w") as f:
        json.dump(snap, f)
    print(f"RESULT first_parent_commits={len(commits)} commits")
    print(f"RESULT merges={len(merges)} pull_requests")
    print(f"RESULT api_failures={len(fails)} reads")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    sys.exit(main())
