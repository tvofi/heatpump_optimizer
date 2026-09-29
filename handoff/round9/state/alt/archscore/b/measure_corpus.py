#!/usr/bin/env python3
"""Measure the full vector at every corpus commit, its first parent, and the last 20 main merges.

    python3 measure_corpus.py [--repo /home/user/heatpump_optimizer]

Trees: ../a2/corpus.tsv (sha, parent) plus the first-parent chain of origin/main from
7952d8f9 back 20 merges. One detached worktree (wt/) is checked out per tree; each
measurement runs measure_vec.py in a fresh process (the a3 loader caches per root) and is
cached in vec/<sha12>.json. The worktree is removed at the end.
"""
import csv, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else "/home/user/heatpump_optimizer"
WT = HERE / "wt"
VEC = HERE / "vec"
VEC.mkdir(exist_ok=True)


def git(*a, cwd=REPO):
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True).stdout.strip()


def shas():
    out = []
    with open(HERE.parent / "a2" / "corpus.tsv") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            out += [r["parent"], r["sha"]]
    chain = git("rev-list", "--first-parent", "-21", "7952d8f9").split()
    out += chain
    full = []
    for s in out:
        s = git("rev-parse", s)
        if s not in full:
            full.append(s)
    return full, chain


def main():
    todo, chain = shas()
    (HERE / "trajectory_chain.txt").write_text("\n".join(chain) + "\n")
    if not WT.exists():
        git("worktree", "add", "--detach", str(WT), todo[0])
    try:
        for i, s in enumerate(todo):
            dst = VEC / f"{s[:12]}.json"
            if dst.exists():
                continue
            git("checkout", "-q", "--detach", "--force", s, cwd=WT)
            git("clean", "-qfdx", cwd=WT)
            r = subprocess.run([sys.executable, str(HERE / "measure_vec.py"), str(WT)],
                               capture_output=True, text=True)
            dst.write_text(r.stdout if r.returncode == 0 else json.dumps({"_error": r.stderr[-600:]}))
            print(i, len(todo), s[:12], "ok" if r.returncode == 0 else "ERR", flush=True)
    finally:
        git("worktree", "remove", "--force", str(WT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
