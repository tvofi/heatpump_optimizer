#!/usr/bin/env python3
"""Planted control for the finder's denominator (COMMON.md, "The denominator"; group R11-PRE-FINDER-CONTRACT).

Metric: of two planted coverage rows, one with no denominator and one carrying enumerator, universe and
examined, how many the driver's `denominatorGaps` (.claude/workflows/audit-find.js, DISPATCH block) passes
and how many the start evaluation's reader counts as carrying the pair (dimension_read.py's
WITH_EXAMINED_UNIVERSE, read at the evaluation sha, never copied into this tree).
Run:      python3 dev/audit/harnesses/r11_denominator_planted.py [--eval-sha SHA]   (from the repository root)
Expected: RESULT driver_refuses_bare=1, driver_passes_full=1, reader_rows=2, reader_counted=1, reader_counts_bare=0
Null:     the full row is the null control of the bare one: same seat shape, same step, the pair added.
Baseline: the head of the pull request that lands the denominator; the driver half fails at a driver
          without `denominatorGaps` (it prints driver_missing=1).
"""
import argparse, json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tests"))
from throwaway_git import throwaway_git_init  # noqa: E402

BARE = {"step": "D1.M1", "evidence": "read every file of the step"}
FULL = {"step": "D2.M1", "enumerator": "git ls-files custom_components | head -3", "universe": 3, "examined": 3,
        "not_reached": [], "redispatched": [], "evidence": "read every file of the step"}


def driver(root):
    src = open(os.path.join(root, ".claude/workflows/audit-find.js"), encoding="utf-8").read()
    blk = re.search(r"// DISPATCH:BEGIN[\s\S]*?// DISPATCH:END", src)
    if not blk or "denominatorGaps" not in blk.group(0):
        print("RESULT driver_missing=1")
        return None
    js = blk.group(0) + "\nconst out = {};\n" + "".join(
        f"out[{json.dumps(k)}] = denominatorGaps({{ dim: {json.dumps(r['step'][:2])}, steps: ['M1'] }}, {{ coverage: [{json.dumps(r)}] }}, []);\n"
        for k, r in (("bare", BARE), ("full", FULL))) + "console.log(JSON.stringify(out))\n"
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def reader(root, sha):
    with tempfile.TemporaryDirectory() as d:
        script = os.path.join(d, "dimension_read.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(subprocess.run(["git", "-C", root, "show", f"{sha}:dev/audit/rounds/round11/evaluation/dimension_read.py"],
                                   capture_output=True, text=True, check=True).stdout)
        repo = os.path.join(d, "repo")
        os.makedirs(os.path.join(repo, "dev/audit/rounds/round99"))
        rep = {"reports": {"D1-s1": {"dimension": "D1", "coverage": [BARE]}, "D2-s1": {"dimension": "D2", "coverage": [FULL]}}}
        json.dump(rep, open(os.path.join(repo, "dev/audit/rounds/round99/reports-B1.json"), "w"))
        json.dump({"groups": []}, open(os.path.join(repo, "roster.json"), "w"))
        env = throwaway_git_init(repo, "-q")
        for c in (["add", "-A"], ["commit", "-qm", "planted"]):
            subprocess.run(["git", *c], cwd=repo, env=env, check=True)
        out = subprocess.run([sys.executable, "-I", script, "--repo", repo, "--ref", "HEAD", "--round", "99", "--roster", "HEAD:roster.json"],
                             capture_output=True, text=True, check=True).stdout
    tot = re.search(r"ROWS (\d+) WITH_EXAMINED_UNIVERSE (\d+)", out)
    per = {l.split("\t")[0]: int(l.split("\t")[11]) for l in out.splitlines() if re.match(r"D\d+\t", l)}
    return int(tot[1]), int(tot[2]), per.get("D1", 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-sha", default="c6ce415b7711d76cf6c08f926f30da91f7bda924")
    a = ap.parse_args()
    root = os.getcwd()
    gaps = driver(root)
    if gaps is not None:
        print(f"RESULT driver_refuses_bare={int(bool(gaps['bare']))} count")
        print(f"RESULT driver_passes_full={int(gaps['full'] == [])} count")
        print(f"GAPS bare={json.dumps(gaps['bare'])}")
    rows, counted, bare = reader(root, a.eval_sha)
    print(f"RESULT reader_rows={rows} count")
    print(f"RESULT reader_counted={counted} count")
    print(f"RESULT reader_counts_bare={bare} count")


if __name__ == "__main__":
    main()
