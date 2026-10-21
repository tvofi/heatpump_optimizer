import sys, shutil, subprocess, tempfile, os
SRC = sys.argv[1]
M = [
 ("RV1 build ignores text_merge drivers (keeps the None stop)", "tools/audit/seat/merge_train.py",
  'code, o = self.run(["git", *drivers, "merge-tree", "--write-tree", last, a["head"]])',
  'code, o = self.run(["git", "merge-tree", "--write-tree", last, a["head"]])', "merge_train"),
 ("RV2 text_merge driver resolves everything (true)", "tools/audit/seat/merge_train.py",
  'f"merge.{n}.driver=git merge-file %A %O %B"', 'f"merge.{n}.driver=true"', "merge_train"),
 ("RV3 text_merge regex matches nothing", "tools/audit/seat/merge_train.py",
  'r"^merge\\..+\\.driver$"', 'r"^merge\\..+\\.nodriver$"', "merge_train"),
 ("RV4 conflicts accepts any rc", "tools/audit/seat/merge_train.py",
  "if code not in (0, 1) or not lines", "if not lines", "merge_train"),
 ("RV5 overlap unreadable arm logs nothing", "tools/audit/seat/merge_train.py",
  'self.log(f"OVERLAP: {self.base} at {tip[:12]}: check runs unreadable; --overlap does not wait")', 'pass', "merge_train"),
 ("RV6 text_merge treats rc 1 as unreadable", "tools/audit/seat/merge_train.py",
  "if code not in (0, 1):\n        return None\n    names", "if code != 0:\n        return None\n    names", "merge_train"),
]
CMD = {"merge_train": ["python3.11", "tools/audit/seat/merge_train.py", "--self-test"],
       "tick": ["python3.11", "tools/audit/seat/orchestrator_tick.py", "--self-test"]}
for name, f, old, new, step in M:
    d = tempfile.mkdtemp(); dst = os.path.join(d, "t"); shutil.copytree(SRC, dst, symlinks=True)
    p = os.path.join(dst, f); s = open(p).read(); n = s.count(old)
    if n != 1: print(f"{name}: NOT APPLIED (count {n})"); continue
    open(p, "w").write(s.replace(old, new))
    outs = []
    for st in ([step] if step != "merge_train" else ["merge_train", "tick"]):
        r = subprocess.run(CMD[st], cwd=dst, capture_output=True, text=True)
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:]
        fails = [l for l in (r.stdout + r.stderr).splitlines() if l.lstrip().startswith(("FAIL", "not ok", "  FAIL"))]
        outs.append(f"{st} rc={r.returncode} {tail} fails={len(fails)}")
    print(f"{name}: " + " | ".join(outs), flush=True)
    shutil.rmtree(d)
