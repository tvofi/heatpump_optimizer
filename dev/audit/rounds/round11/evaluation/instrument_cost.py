#!/usr/bin/env python3
"""Cost of each instrument object objective.json lists, by decision 0018 section 3 (its lines, the hotfix groups naming it).

Usage: python3 dev/audit/rounds/round11/evaluation/instrument_cost.py --repo . --ref <graded sha> --start <window start ref> --end <window end ref> --roster <REF:PATH>
One TSV line per object: object, implementation, lines at --ref, lines at --start (0: absent), first-parent commits touching it in
start..end, roster groups naming its basename (id, brief or files), and how many of those are hotfix groups. Then `OBJECTS <n>`.
An instrument guide `tools/audit/seat/instruments/<name>.md` is costed on the tracked file whose basename is <name>; a guide
with no such file is costed on itself and says so. Yield is not printed: nothing logs a refusal with its outcome.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="."); ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--start", required=True); ap.add_argument("--end", required=True); ap.add_argument("--roster", required=True)
    a = ap.parse_args()
    sys.path.insert(0, str(Path(a.repo) / "tools/audit"))
    import check_scopes as cs
    tree = [t for t in git(a.repo, "ls-tree", "-r", "--name-only", a.ref).split("\n") if t]
    spec = json.loads(git(a.repo, "show", f"{a.ref}:dev/audit/config/objective.json"))
    objs = sorted(cs.match(tree, spec["objects"]["instrument"]))
    by_base = {}
    for t in tree:
        by_base.setdefault(t.rsplit("/", 1)[-1], []).append(t)
    groups = json.loads(git(a.repo, "show", a.roster))["groups"]
    texts = [(g["group"], str(g.get("kind")), g["group"] + " " + str(g.get("brief")) + " " + " ".join(map(str, g.get("files") or []))) for g in groups]
    def lines(ref, p):
        r = subprocess.run(["git", "-C", a.repo, "show", f"{ref}:{p}"], capture_output=True)
        return r.stdout.count(b"\n") if r.returncode == 0 else 0
    print("object\timplementation\tlines\tlines_at_start\twindow_commits\troster_groups\thotfix_groups")
    for o in objs:
        impl, note = o, ""
        if o.startswith("tools/audit/seat/instruments/") and o.endswith(".md"):
            name = o.rsplit("/", 1)[-1][:-3]
            cands = [c for c in by_base.get(name, []) if c != o] or [c for c in by_base.get(name.replace("shims_", ""), []) if c != o]
            pref = [c for c in cands if c.startswith(("tools/", "tests/", ".claude/"))]
            impl = (pref or cands or [o])[0]
            note = "" if impl != o else " (no tracked file of that basename: the guide itself)"
        base = impl.rsplit("/", 1)[-1]
        pat = re.compile(r"(?<![\w.-])" + re.escape(base) + r"(?![\w-])")
        named = [(g, k) for g, k, t in texts if pat.search(t)]
        hot = [g for g, k in named if k == "hotfix" or "HOTFIX" in g]
        commits = len([l for l in git(a.repo, "log", "--first-parent", "--oneline", f"{a.start}..{a.end}", "--", impl).split("\n") if l])
        print(f"{o}\t{impl}{note}\t{lines(a.ref, impl)}\t{lines(a.start, impl)}\t{commits}\t{len(named)}\t{len(hot)}")
    print(f"OBJECTS {len(objs)}")


if __name__ == "__main__":
    main()
