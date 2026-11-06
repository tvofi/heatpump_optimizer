#!/usr/bin/env python3
"""Every open PR mapped to its latest verdict and the holder it is owed (tvofi 11-06: the sweep's point).

Prints one UNHELD line per PR whose next step nobody visibly holds:
  merge verdict at an older head that the PR head only main-merges onto -> owed to the merge train
  blocked verdict and handoff/<topic> not moved past the blocked sha    -> owed a repair fixer
  no verdict ref at all                                                   -> owed a first reviewer
"Held" means: queued in a live train log, or a fire line in the last 12 h naming the PR/topic.
Run from a checkout of tvofi/heatpump_optimizer with origin fetched.
"""
import json, re, subprocess, sys, time, glob, os

REPO = "tvofi/heatpump_optimizer"
FIRED = sys.argv[1] if len(sys.argv) > 1 else ""
TRAIN_GLOB = sys.argv[2] if len(sys.argv) > 2 else ""


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout


prs = json.loads(sh("gh", "pr", "list", "--repo", REPO, "--state", "open", "--limit", "100",
                    "--json", "number,headRefOid,headRefName,title"))
refs = {}
for line in sh("git", "ls-remote", "origin", "refs/heads/verdict/*", "refs/heads/handoff/*").splitlines():
    sha, ref = line.split("\t")
    refs[ref] = sha
recent = ""
if FIRED and os.path.exists(FIRED):
    cut = time.time() - 12 * 3600
    for l in open(FIRED):
        m = re.match(r"(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?)Z", l)
        if m and time.mktime(time.strptime(m[1][:16], "%Y-%m-%dT%H:%M")) - time.timezone >= cut:
            recent += l
trains = ""
for f in glob.glob(TRAIN_GLOB) if TRAIN_GLOB else []:
    if time.time() - os.path.getmtime(f) < 3 * 3600:
        trains += open(f, errors="replace").read()

SKIP = sys.argv[3] if len(sys.argv) > 3 else ""
skip = set()
if SKIP and os.path.exists(SKIP):  # "#3226 <ruling>" lines: PRs held by an owner ruling, not a seat
    skip = {int(m[1]) for l in open(SKIP) if (m := re.match(r"#(\d+)\s", l))}

for p in prs:
    n, head, br = p["number"], p["headRefOid"], p["headRefName"]
    if n in skip:
        continue
    topic = br.split("/", 1)[-1]
    held = f"#{n}" in recent or topic in recent
    v = refs.get(f"refs/heads/verdict/{n}")
    if not v:
        if not held:
            print(f"UNHELD #{n} no verdict ever: owed a first reviewer once the gate is green ({p['title'][:50]})")
        continue
    subprocess.run(["git", "fetch", "-q", "origin", v], capture_output=True)
    first = sh("git", "show", f"{v}:VERDICT.md").splitlines()[:1]
    m = re.match(r"Fix review: (\w+) ([0-9a-f]{40})", first[0] if first else "")
    if not m:
        continue
    kind, at = m[1], m[2]
    if kind == "merge":
        queued = re.search(rf"#{n}\b", trains) is not None
        if not queued and not held:
            print(f"UNHELD #{n} merge verdict at {at[:8]}, head {head[:8]}: owed to the merge train")
    elif kind == "blocked":
        h = refs.get(f"refs/heads/handoff/{topic}")
        moved = h and h != at and subprocess.run(["git", "merge-base", "--is-ancestor", h, at],
                                                 capture_output=True).returncode != 0
        if head == at and not moved and not held:
            print(f"UNHELD #{n} blocked at {at[:8]}, no repair handoff and no fire in 12 h: owed a repair fixer")
        elif moved and head == at and not held:
            print(f"UNHELD #{n} blocked at {at[:8]}, handoff moved to {h[:8]}: owed update_pr then a reviewer")
