#!/usr/bin/env python3
"""Baseline step 1 (git only, read-only): one JSON row per PR merged on main's
first-parent line in a window, with its bus timeline. Usage:
  collect_git.py REPO SINCE_ISO UNTIL_ISO ROSTER_JSON > merges.json
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PD_DATA = _os.environ.get("PD_DATA", _os.path.join(_HERE, "..", "data")) + "/"
PD_REPO = _os.environ.get("PD_REPO", _os.path.abspath(_os.path.join(_HERE, "..", "..", "..", "..", "..", "..")))
PD_STATE = _os.environ.get("PD_STATE", _os.path.expanduser("~/.local/state/hpo"))
import json, re, subprocess, sys
from datetime import datetime, timezone

repo, since, until, roster_path = sys.argv[1:5]

def git(*a):
    r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def ts(s): return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())

roster = json.load(open(roster_path))
groups = roster["groups"] if isinstance(roster, dict) and "groups" in roster else roster
if isinstance(groups, dict): groups = list(groups.values())
by_pr, by_topic = {}, {}
for g in groups:
    if not isinstance(g, dict): continue
    r = g.get("resume") or {}
    if r.get("pr"): by_pr[int(r["pr"])] = g
    b = (r.get("branch") or "")
    if b.startswith("handoff/"): by_topic[b[len("handoff/"):]] = g
    by_topic.setdefault(g["group"].lower(), g)

refs = {}
out = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/")
for line in out.split():
    refs[line[len("origin/"):]] = 1

def ref_log(ref):
    o = git("log", "--format=%ct\t%H\t%s", "origin/" + ref)
    if o is None: return []
    rows = []
    for l in o.strip().splitlines():
        c, h, s = l.split("\t", 2)
        rows.append((int(c), h, s))
    return rows[::-1]

VERD = re.compile(r"verdict: #(\d+) Fix review: (merge|blocked) ([0-9a-f]{7,40})(?: ([a-z0-9-]+):)?")
log = git("log", "--first-parent", "--format=%ct\t%H\t%P\t%s", "--since=" + since, "--until=" + until, "origin/main")
rows = []
for l in log.strip().splitlines():
    c, h, parents, subj = l.split("\t", 3)
    m = re.match(r"Merge pull request #(\d+) from ([^/\s]+)/(\S+)", subj)
    if not m: 
        rows.append({"sha": h, "t_merge": int(c), "pr": None, "subject": subj, "kind": "direct"}); continue
    pr, owner, branch = int(m.group(1)), m.group(2), m.group(3)
    ps = parents.split()
    head = ps[1] if len(ps) > 1 else None
    files = (git("diff", "--name-only", ps[0], h) or "").split()
    topic = re.sub(r"^fix/", "", branch); topic = re.sub(r"-pr$", "", topic)
    g = by_pr.get(pr) or by_topic.get(topic) or by_topic.get(re.sub(r"-p\d+$", "", topic))
    if branch.startswith("record/") or (files and all(f.startswith(("dev/programme/delivery/", "dev/programme/")) for f in files)):
        kind = "record"
    elif branch.startswith("dependabot/"): kind = "bot"
    elif "hotfix" in branch: kind = "hotfix"
    elif g: kind = "group"
    else: kind = "flyin"
    # branch-own commits: head's history not on main at merge
    own = (git("log", "--format=%ct\t%H\t%P\t%an\t%s", f"{ps[0]}..{head}") or "").strip().splitlines() if head else []
    absorbs = sum(1 for x in own if len(x.split("\t")[2].split()) > 1)
    botc = sum(1 for x in own if x.split("\t")[4].startswith("ci: "))
    rowc = sum(1 for x in own if x.split("\t")[4].startswith("record: the delivery row"))
    first_commit = min((int(x.split("\t")[0]) for x in own), default=None)
    review = [(c2, VERD.search(s)) for c2, _, s in ref_log(f"review/{pr}")] if f"review/{pr}" in refs else []
    verdict = [(c2, VERD.search(s)) for c2, _, s in ref_log(f"verdict/{pr}")] if f"verdict/{pr}" in refs else []
    def pack(v): return [{"t": c2, "v": m2.group(2), "head": m2.group(3), "cls": m2.group(4)} for c2, m2 in v if m2]
    hb = ref_log(f"handoff-body/{topic}") if f"handoff-body/{topic}" in refs else []
    rows.append({
        "sha": h, "t_merge": int(c), "pr": pr, "branch": branch, "owner": owner, "topic": topic, "kind": kind,
        "head": head, "group": g["group"] if g else None, "size": g.get("size") if g else None,
        "gkind": g.get("kind") if g else None, "lane": g.get("lane") if g else None,
        "files": files, "n_own": len(own), "absorbs": absorbs, "bot_commits": botc, "row_commits": rowc,
        "t_first_commit": first_commit,
        "review": pack(review), "verdict": pack(verdict),
        "handoff_body": [c2 for c2, _, _ in hb],
    })
json.dump(rows, sys.stdout)
