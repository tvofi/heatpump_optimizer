#!/usr/bin/env python3
"""review-2074c arm driver: applies one mutation to the worktree on disk, runs
the targeted block (ev/review_block3.py), restores with
`git checkout HEAD -- <files>`, and confirms `git diff --quiet HEAD`.

Every mutation is the body's own arm, named in RCA S7's table.
"""
import pathlib
import re
import subprocess
import sys

WT = pathlib.Path("/Users/timmalmstrom/hpo-seats/review-2074c/wt")
EV = pathlib.Path("/Users/timmalmstrom/hpo-seats/review-2074c/ev")
PY = str(pathlib.Path.home() / ".local/state/hpo/venv-ci/bin/python3")
MT = WT / "tests" / "mutation_table.py"
YML = WT / ".github" / "workflows" / "tests.yml"


def sh(*a):
    return subprocess.run(a, cwd=WT, capture_output=True, text=True)


def run(label):
    p = subprocess.run([PY, "-I", str(EV / "review_block3.py"), label],
                       cwd=WT, capture_output=True, text=True)
    red = re.findall(r"^  FAIL (.*)$", p.stdout, re.M)
    m = re.search(r"RESULT block-ran: (\d+) checks, (\d+) failures", p.stdout)
    return p.returncode, (m.groups() if m else ("?", "?")), red, p.stdout + p.stderr


def restore():
    sh("git", "checkout", "HEAD", "--", str(MT), str(YML))
    dirty = sh("git", "diff", "--quiet", "HEAD").returncode
    return "clean" if dirty == 0 else "DIRTY"


ARMS = {}

# E -- `if: always()` removed from the actions/cache/save step (adjacency pin)
def arm_E():
    t = YML.read_text().splitlines(keepends=True)
    i = next(n for n, ln in enumerate(t)
             if "actions/cache/save@" in ln and n + 1 < len(t)
             and t[n + 1].strip() == "if: always()")
    assert i == 1237, f"expected the save at line 1238, found {i+1}"
    del t[i + 1]
    YML.write_text("".join(t))
    return [str(YML)]

# C -- `--pool-seconds` deleted from BOTH nightly lanes
def arm_C():
    t = YML.read_text().splitlines(keepends=True)
    hits = [n for n, ln in enumerate(t) if '--pool-seconds "$RUNNER_TEMP' in ln]
    assert len(hits) == 2, f"expected 2 pool-seconds lines, got {hits}"
    for n in reversed(hits):
        del t[n]
    YML.write_text("".join(t))
    return [str(YML)]

# D -- the seed call site reverted to recorded_seconds()
def arm_D():
    t = MT.read_text()
    old = "        own_s = seed_pool_seconds(recorded_seconds(), prior_pool)\n"
    assert t.count(old) == 1
    MT.write_text(t.replace(old, "        own_s = recorded_seconds()\n"))
    return [str(MT)]

# A -- seed_pool_seconds's fold neutered
def arm_A():
    t = MT.read_text()
    old = "        out[s] = max(out.get(s, 0.0), sec)\n"
    assert t.count(old) == 1
    MT.write_text(t.replace(old, "        pass\n"))
    return [str(MT)]

# B -- baseline_refusal's timeout arm neutered
def arm_B():
    t = MT.read_text()
    old = "    timeouts = [s for s in red if baseline[s].timed_out]\n"
    assert t.count(old) == 1
    MT.write_text(t.replace(old, "    timeouts = []\n"))
    return [str(MT)]

# REVERT -- the merge base's mutation_table.py over the fix
def arm_REVERT():
    base = sh("git", "merge-base", "origin/main", "HEAD").stdout.strip()
    blob = subprocess.run(["git", "show", f"{base}:tests/mutation_table.py"],
                          cwd=WT, capture_output=True, text=True).stdout
    MT.write_text(blob)
    return [str(MT)]


ARMS = {"E": arm_E, "C": arm_C, "D": arm_D, "A": arm_A, "B": arm_B,
        "REVERT": arm_REVERT}

which = sys.argv[1:] or list(ARMS)
log = []
for name in which:
    touched = ARMS[name]()
    rc, counts, red, out = run(name)
    state = restore()
    log.append(f"ARM {name} (touched {', '.join(p.split('/')[-1] for p in touched)})"
               f"\n  exit={rc}  {counts[0]} checks / {counts[1]} failures"
               f"\n  red checks: {red}\n  restore: {state}")
    (EV / f"block_{name}.txt").write_text(out)
print("\n".join(log))
