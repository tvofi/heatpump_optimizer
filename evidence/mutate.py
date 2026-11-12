#!/usr/bin/env python3
"""Reviewer's mutant driver: one worktree per mutant at the head, one exact string replaced once, the owning self-test run."""
import subprocess, sys, pathlib, shutil
HEAD = "b372f8e935365aaecbe6e74c68d3954e5a3ca1b1"
REPO = "/home/user/heatpump_optimizer"
TRAIN = ["python3", "-I", "tools/audit/seat/merge_train.py", "--self-test"]
M = {
 "m1-outside-prefix-dropped": ("tools/audit/seat/merge_train.py", 'any(str(ln).startswith("OUTSIDE: ") and f" at {h}: " in str(ln) for ln in lines)', 'any(f" at {h}: " in str(ln) for ln in lines)', TRAIN),
 "m2-train-cross-false": ("tools/audit/seat/merge_train.py", "cross = _outside_gate().cross_repository(facts, self.repo)", "cross = False", TRAIN),
 "m3-mergepr-cross-false": ("tools/audit/seat/merge_pr.sh", "cross = mod.cross_repository(facts, repo)", "cross = False", ["bash", "tools/audit/seat/merge_pr.sh", "--self-test"]),
 "m4-fixture-words-restored": ("tools/audit/seat/merge_train.py", '"the prior owner review\'s body at " + H0', '"Outside read: " + H0', ["python3", "-I", "tools/pr/outside.py", "--self-test"]),
 "m5-doubled-remote": ("tools/audit/seat/merge_train.py", "        held: list = []\n\n        def carried(pr, head):", '        held: list = []\n        git("remote", "add", "origin", str(gd))\n        def carried(pr, head):', TRAIN),
 "m6-prefix-anywhere": ("tools/audit/seat/merge_train.py", 'str(ln).startswith("OUTSIDE: ") and f" at {h}: "', '"OUTSIDE: " in str(ln) and f" at {h}: "', TRAIN),
 "m7-train-cross-inverted-stub": ("tools/audit/seat/merge_train.py", "            return REAL_OUTSIDE.cross_repository(facts, repo)", "            return True", TRAIN),
 "m8-mergepr-cross-true": ("tools/audit/seat/merge_pr.sh", "cross = mod.cross_repository(facts, repo)", "cross = True", ["bash", "tools/audit/seat/merge_pr.sh", "--self-test"]),
 "m10-outside-cross-false": ("tools/pr/outside.py", '    return f["head_repo"] != repo', "    return False", ["python3", "-I", "tools/pr/outside.py", "--self-test"]),
 "m9-train-cross-true": ("tools/audit/seat/merge_train.py", "cross = _outside_gate().cross_repository(facts, self.repo)", "cross = True", TRAIN),
}
name = sys.argv[1]
path, old, new, cmd = M[name]
wt = f"/tmp/mut-{name}"
subprocess.run(["git", "-C", REPO, "worktree", "add", "-q", "--detach", wt, HEAD], check=True)
f = pathlib.Path(wt, path); s = f.read_text()
assert s.count(old) == 1, (name, s.count(old))
f.write_text(s.replace(old, new))
r = subprocess.run(cmd, cwd=wt, capture_output=True, text=True)
out = r.stdout + r.stderr
fails = [l for l in out.splitlines() if l.startswith("FAIL")]
summ = [l for l in out.splitlines() if "self-test:" in l]
res = "KILLED" if (fails or r.returncode != 0) else "SURVIVED"
with open(f"/tmp/rv/ev/mut_{name}.txt", "w") as o:
    o.write(f"mutant {name} at {HEAD}\n{path}: {old!r} -> {new!r}\ncmd: {' '.join(cmd)}\nrc={r.returncode}\nRESULT {name}: {res}, {len(fails)} FAIL line(s), summary {summ[-1:] }\n\n")
    o.write("\n".join(l[:400] for l in fails) + "\n--- tail\n" + "\n".join(out.splitlines()[-12:]) + "\n")
print(f"RESULT {name}: {res}, {len(fails)} FAIL, rc={r.returncode}, {summ[-1:]}")
subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", wt])
