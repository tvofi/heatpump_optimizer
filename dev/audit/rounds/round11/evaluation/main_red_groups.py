#!/usr/bin/env python3
"""Roster groups whose brief records a red main, and the job each hotfix among them names.

Usage: python3 dev/audit/rounds/round11/evaluation/main_red_groups.py --repo . --roster <SHA:PATH>
Prints one line per group (id, kind, stage, the brief's sentence about the red), then the count, the hotfix groups among
them and how many of those name the `instrument-self-tests` job (`instrument[- ]self-tests` in the brief). The cause is the brief's own word: a lead for a gate's reds, never
a cause record.
"""
import argparse, json, re, subprocess


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--repo", default="."); ap.add_argument("--roster", required=True)
    a = ap.parse_args()
    groups = json.loads(subprocess.run(["git", "-C", a.repo, "show", a.roster], capture_output=True, text=True).stdout)["groups"]
    pat = re.compile(r"main (is |was |went |goes )?red|red on main|main red|MAIN-RED|main's (gate|push)", re.I)
    hits = []
    for g in sorted(groups, key=lambda g: g["group"]):
        b = " ".join(str(g.get("brief")).split())
        if pat.search(b + g["group"]):
            m = re.search(r"(.{0,120})(main (?:is |was |went )?red|red on main)(.{0,200})", b, re.I)
            hits.append(g["group"])
            print(g["group"], g.get("kind"), (g.get("resume") or {}).get("stage"), "|", m.group(0) if m else b[:240])
    hot = [h for h in hits if "HOTFIX" in h]
    ist = [g["group"] for g in groups if g["group"] in hot and re.search(r"instrument[- ]self-tests", str(g.get("brief")), re.I)]
    print(f"GROUPS {len(hits)} HOTFIX {len(hot)} NAMING_SELF_TESTS {len(ist)}")


if __name__ == "__main__":
    main()
