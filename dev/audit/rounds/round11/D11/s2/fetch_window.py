#!/usr/bin/env python3
"""D11-s2 window snapshot: GitHub's own records for every merged pull request
of round 11's window (first-parent merges v10.0.0..<baseline>), written to
api/window.json so the measuring harnesses run offline and a judge can re-fetch.

Metric: none (a fetcher). Run from the export root:
    python3 dev/audit/rounds/round11/D11/s2/fetch_window.py [--base v10.0.0] [--head 92d38ecb64]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B7. Uses `curl` (the
box's proxy authenticates); GITHUB_TOKEN, when set, is sent as a bearer token.

The set of pull requests is taken from `/commits/<sha>/pulls` per merge commit
and compared against the subject's `#N` (D11's trap #677: compare sets, not
totals); both are stored.
"""
import json, os, re, subprocess, sys, time

REPO = "tvofi/heatpump_optimizer"
HERE = os.path.dirname(os.path.abspath(__file__))


def api(path):
    url = path if path.startswith("http") else f"https://api.github.com/repos/{REPO}/{path}"
    cmd = ["curl", "-sS", "-m", "60", "-H", "Accept: application/vnd.github+json"]
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        cmd += ["-H", f"Authorization: Bearer {tok}"]
    for attempt in range(3):
        out = subprocess.run(cmd + [url], capture_output=True, text=True)
        try:
            return json.loads(out.stdout)
        except Exception:
            time.sleep(2)
    return {"_error": out.stderr[:300]}


def pages(path, key=None):
    res, page = [], 1
    while True:
        sep = "&" if "?" in path else "?"
        d = api(f"{path}{sep}per_page=100&page={page}")
        items = d.get(key, []) if key and isinstance(d, dict) else d
        if not isinstance(items, list):
            res.append({"_error": d})
            break
        res += items
        if len(items) < 100:
            break
        page += 1
    return res


def main(argv):
    base = argv[argv.index("--base") + 1] if "--base" in argv else "v10.0.0"
    head = argv[argv.index("--head") + 1] if "--head" in argv else "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
    log = subprocess.run(["git", "log", "--first-parent", "--merges", "--format=%H %P\t%s", f"{base}..{head}"],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    merges = []
    for line in log:
        shas, subj = line.split("\t", 1)
        sha, *parents = shas.split()
        m = re.search(r"#(\d+)", subj)
        assoc = api(f"commits/{sha}/pulls")
        merges.append({"sha": sha, "parents": parents, "subject": subj,
                       "subject_pr": int(m.group(1)) if m else None,
                       "api_prs": [p["number"] for p in assoc] if isinstance(assoc, list) else None})
    prs = {}
    for mg in merges:
        n = mg["subject_pr"] or (mg["api_prs"] or [None])[0]
        if n is None:
            continue
        pr = api(f"pulls/{n}")
        hs = pr.get("head", {}).get("sha")
        prs[str(n)] = {
            "pull": {k: pr.get(k) for k in ("number", "title", "body", "merged_at", "merge_commit_sha",
                                            "created_at", "additions", "deletions")}
                    | {"user": (pr.get("user") or {}).get("login"),
                       "merged_by": (pr.get("merged_by") or {}).get("login"),
                       "head_sha": hs, "head_ref": pr.get("head", {}).get("ref")},
            "reviews": [{"user": (r.get("user") or {}).get("login"), "state": r.get("state"),
                         "commit_id": r.get("commit_id"), "submitted_at": r.get("submitted_at"),
                         "body": (r.get("body") or "")[:400]} for r in pages(f"pulls/{n}/reviews")],
            "comments": [{"user": (c.get("user") or {}).get("login"), "created_at": c.get("created_at"),
                          "body": (c.get("body") or "")[:600]} for c in pages(f"issues/{n}/comments")],
            "commits": [c.get("sha") for c in pages(f"pulls/{n}/commits")],
            "check_runs_at_head": [{"name": c.get("name"), "status": c.get("status"),
                                    "conclusion": c.get("conclusion"), "started_at": c.get("started_at"),
                                    "completed_at": c.get("completed_at"),
                                    "app": (c.get("app") or {}).get("slug")}
                                   for c in pages(f"commits/{hs}/check-runs?filter=all", key="check_runs")] if hs else [],
        }
        sys.stderr.write(f"#{n} reviews={len(prs[str(n)]['reviews'])} runs={len(prs[str(n)]['check_runs_at_head'])}\n")
    out = {"base": base, "head": head, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "merges": merges, "prs": prs}
    os.makedirs(os.path.join(HERE, "api"), exist_ok=True)
    with open(os.path.join(HERE, "api", "window.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"RESULT merges={len(merges)} count")
    print(f"RESULT prs_fetched={len(prs)} count")


if __name__ == "__main__" and "--gates" not in sys.argv:
    main(sys.argv[1:])

# The #3394 disposition lines (delivery-status-tracking.md item 1) were fetched
# beside the window with:
#   python3 -c "import sys,json;sys.path.insert(0,'dev/audit/rounds/round11/D11/s2');import fetch_window as f;
#     cs=f.pages('issues/3394/comments?since=2026-11-14T00:00:00Z'); ..."  -> api/issue3394.json


def fetch_gate_suites():
    """Every `gate` check run at each window head, with its check-suite id:
    api/gate_runs.json. Run: python3 dev/audit/rounds/round11/D11/s2/fetch_window.py --gates"""
    d = json.load(open(os.path.join(HERE, "api", "window.json")))
    out = {}
    for n, p in d["prs"].items():
        hs = p["pull"]["head_sha"]
        runs = pages(f"commits/{hs}/check-runs?filter=all&check_name=gate", key="check_runs")
        out[n] = [{"id": c.get("id"), "suite": (c.get("check_suite") or {}).get("id"), "status": c.get("status"),
                   "conclusion": c.get("conclusion"), "started_at": c.get("started_at"),
                   "completed_at": c.get("completed_at"), "run": (c.get("details_url") or "").split("/runs/")[-1].split("/")[0]}
                  for c in runs]
    json.dump(out, open(os.path.join(HERE, "api", "gate_runs.json"), "w"), indent=1)
    print(f"RESULT gate_heads={len(out)} count")


if __name__ == "__main__" and "--gates" in sys.argv:
    fetch_gate_suites()
