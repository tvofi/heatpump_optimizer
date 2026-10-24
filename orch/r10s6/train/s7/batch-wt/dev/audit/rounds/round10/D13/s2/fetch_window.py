#!/usr/bin/env python3
"""D13-s2 window fetcher (exposure: GitHub API, read-only).

Run: python3 dev/audit/rounds/round10/D13/s2/fetch_window.py <since-ref> <until-sha> <out.json>
Population: first-parent merge commits in since..until (git rev-list --first-parent --merges),
each mapped to its pull request by GET /commits/<sha>/pulls (the API mode of policy_lint.mjs
enumerateMerges). Per PR: /pulls/<n> body, /issues/<n>/comments, /pulls/<n>/reviews (paginated).
Prints RESULT merges, prs, api_failures. Counts only; no timing.
"""
import json, subprocess, sys
since, until, out = sys.argv[1:4]
REPO = "tvofi/heatpump_optimizer"
def api(path):
    r = subprocess.run(["gh", "api", "--paginate", path], capture_output=True, text=True)
    if r.returncode:
        return None
    dec, s, items, i = json.JSONDecoder(), r.stdout.strip(), [], 0
    while i < len(s):
        obj, j = dec.raw_decode(s, i); i = j
        while i < len(s) and s[i].isspace(): i += 1
        items.append(obj)
    if len(items) == 1: return items[0]
    if all(isinstance(x, list) for x in items): return [y for x in items for y in x]
    return items
shas = subprocess.run(["git", "rev-list", "--first-parent", "--merges", f"{since}..{until}"],
                      capture_output=True, text=True, check=True).stdout.split()
fail, prs = [], {}
for sha in shas:
    pulls = api(f"/repos/{REPO}/commits/{sha}/pulls")
    if not isinstance(pulls, list):
        fail.append(sha); continue
    hit = [p for p in pulls if p.get("merge_commit_sha") == sha] or pulls[:1]
    if not hit: fail.append(sha); continue
    p = hit[0]; n = p["number"]
    com = api(f"/repos/{REPO}/issues/{n}/comments?per_page=100")
    rev = api(f"/repos/{REPO}/pulls/{n}/reviews?per_page=100")
    if com is None or rev is None: fail.append(sha); continue
    prs[n] = {"sha": sha, "title": p.get("title"), "author": (p.get("user") or {}).get("login"),
              "body": p.get("body") or "",
              "comments": [{"body": c.get("body"), "created_at": c.get("created_at")} for c in com],
              "reviews": [{"body": c.get("body"), "submitted_at": c.get("submitted_at")} for c in rev]}
json.dump({"since": since, "until": until, "merges": shas, "api_failures": fail, "prs": prs}, open(out, "w"))
print(f"RESULT merges={len(shas)} count"); print(f"RESULT prs={len(prs)} count"); print(f"RESULT api_failures={len(fail)} count")
