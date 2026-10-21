"""Review rounds, first-pass yield and verdict classes per reviewed pull request, by roster size.

Read-only; run in a clone that has fetched the review bus and the roster branch:

    git fetch origin '+refs/heads/review/*:refs/remotes/origin/review/*' handoff/audit-r10-roster
    python3 review_rounds.py [--since 2026-10-10T00:00Z] [--json out.json]

Source: refs/remotes/origin/review/<N> (one commit per proposed verdict, as review_baseline.py
reads them). A pull request's size and kind come from the roster group whose resume names it
(any roster file under dev/programme/rosters/ at origin/main, plus the round roster branch).
"""
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict

VERDICT = re.compile(r"Fix review: (merge|blocked) [0-9a-f]{40}\s*\[?([a-z-]+)?")
PRNUM = re.compile(r"#?(\d{3,5})")


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout


def rosters():
    files = [f for f in git("ls-tree", "-r", "--name-only", "origin/main", "dev/programme/rosters").split()
             if f.endswith(".json")]
    docs = [json.loads(git("show", f"origin/main:{f}")) for f in files]
    try:
        docs.append(json.loads(git("show", "origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json")))
    except subprocess.CalledProcessError:
        pass
    return docs


def pr_map(docs, pr_keys):
    out = {}
    for d in docs:
        for g in d.get("groups", []) if isinstance(d, dict) else []:
            r = g.get("resume") or {}
            vals = []
            for k in pr_keys:
                v = r.get(k) if isinstance(r, dict) else None
                if v is None:
                    continue
                vals += v if isinstance(v, list) else [v]
            for v in vals:
                m = PRNUM.search(str(v))
                if m:
                    out[int(m.group(1))] = (g.get("group"), g.get("size"), g.get("kind"))
    return out


def verdicts():
    refs = git("for-each-ref", "refs/remotes/origin/review", "--format=%(refname:short)").split()
    for ref in refs:
        pr = ref.rsplit("/", 1)[1]
        if not pr.isdigit():
            continue
        for line in reversed(git("log", "--format=%cI|%s", ref).splitlines()):
            stamp, subject = line.split("|", 1)
            m = VERDICT.search(subject)
            if m:
                yield int(pr), dt.datetime.fromisoformat(stamp), m.group(1), m.group(2) or ""


def main(argv):
    since = None
    if "--since" in argv:
        since = dt.datetime.fromisoformat(argv[argv.index("--since") + 1].replace("Z", "+00:00"))
    keys = (argv[argv.index("--pr-keys") + 1].split(",") if "--pr-keys" in argv else ["pr", "prs"])
    pmap = pr_map(rosters(), keys)
    per = defaultdict(list)
    for pr, when, v, cls in verdicts():
        if since and when < since:
            continue
        per[pr].append((when, v, cls))
    rows = []
    for pr, vs in per.items():
        vs.sort()
        g, size, kind = pmap.get(pr, (None, None, None))
        blocks = [c for _, v, c in vs if v == "blocked"]
        merged = any(v == "merge" for _, v, _ in vs)
        gaps = [(b[0] - a[0]).total_seconds() / 3600 for a, b in zip(vs, vs[1:]) if a[1] == "blocked"]
        rows.append({"pr": pr, "group": g, "size": size or "?", "kind": kind or "?", "verdicts": len(vs),
                     "first": vs[0][1], "blocks": blocks, "merged_verdict": merged,
                     "rework_h": [round(x, 2) for x in gaps]})
    by = defaultdict(list)
    for r in rows:
        by[r["size"]].append(r)
    print(f"reviewed PRs {len(rows)}; mapped to a roster group {sum(1 for r in rows if r['group'])}")
    for size in ["S", "M", "L", "XL", "?"]:
        rs = by.get(size, [])
        if not rs:
            continue
        fpy = sum(1 for r in rs if r["first"] == "merge") / len(rs)
        nb = [len(r["blocks"]) for r in rs]
        rw = sorted(x for r in rs for x in r["rework_h"])
        med = rw[len(rw) // 2] if rw else None
        print(f"size {size:2}: n={len(rs):3} FPY={fpy:.2f} blocks/PR={sum(nb)/len(rs):.2f} "
              f"max={max(nb)} rework_h median={med} n_rework={len(rw)}")
    cls = Counter(c for r in rows for c in r["blocks"])
    print("block classes:", dict(cls.most_common()))
    cls_by = defaultdict(Counter)
    for r in rows:
        for c in r["blocks"]:
            cls_by[r["size"]][c] += 1
    for s, c in cls_by.items():
        print(f"  {s}: {dict(c.most_common(8))}")
    if "--json" in argv:
        json.dump(rows, open(argv[argv.index("--json") + 1], "w"), default=str, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
