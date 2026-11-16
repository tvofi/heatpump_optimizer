#!/usr/bin/env python3
"""First design-review verdict per group, from the design-verdict bus and its archive tags (git only).

Usage: python3 dev/audit/rounds/round11/evaluation/design_verdicts.py --repo . --window FROM..UNTIL
Each ref `design-verdict/<GROUP>` (a remote head or an `archive/design-verdict/` tag) holds one commit per verdict, subject
`... Design review: approve|revise ...`. Prints groups whose first verdict falls in the window, how many of those were
`approve`, and the verdict count per group (2 or more is a re-review).
"""
import argparse, datetime, re, subprocess


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--repo", default="."); ap.add_argument("--window", required=True)
    a = ap.parse_args()
    lo, hi = (datetime.datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() for x in a.window.split("..", 1))
    git = lambda *x: subprocess.run(["git", "-C", a.repo, *x], capture_output=True, text=True).stdout
    refs = {}
    for l in git("for-each-ref", "--format=%(refname)", "refs/tags/archive/design-verdict", "refs/remotes/origin/design-verdict").split("\n"):
        if l:
            refs.setdefault(l.rsplit("/", 1)[-1].upper(), l)
    n = first_ok = total = 0; multi = []
    for g, ref in sorted(refs.items()):
        log = [l.split("\t", 1) for l in git("log", "--reverse", "--format=%ct\t%s", ref).split("\n") if "Design review:" in l]
        vs = [(t, re.search(r"Design review:\s*(approve|revise)", s).group(1)) for t, s in log if re.search(r"Design review:\s*(approve|revise)", s)]
        if not vs:
            continue
        t0 = int(vs[0][0])
        if not (lo <= t0 <= hi):
            continue
        n += 1; first_ok += vs[0][1] == "approve"; total += len(vs)
        if len(vs) > 1:
            multi.append(f"{g}:{len(vs)}")
    print(f"groups with a design verdict in the window: {n}; first verdict approve: {first_ok}/{n}; verdicts: {total}; re-reviewed: {','.join(multi) or '-'}")


if __name__ == "__main__":
    main()
