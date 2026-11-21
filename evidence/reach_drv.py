# exec tests/entities.py's N-log-flood section (from the Counter import to the next
# "# ---" section line) under a recording R; prints each check's verdict.
import sys, ast, re, subprocess, tempfile, os, json, hashlib, io, asyncio  # r7: the section reads the module-level asyncio import
from pathlib import Path
path = sys.argv[1]
sys.path[:0] = [str(Path(path).parent), str(Path(path).parent / "hastub")]
lines = open(path).read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("from collections import Counter  # noqa: E402"))
end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("# THE RECORD JOB'S WINDOW CACHE WIRING"))
from throwaway_git import throwaway_git_init, throwaway_git_environ  # noqa
class Rec:
    def __init__(s): s.out = []
    def check(s, name, cond, detail=""):
        s.out.append((name, bool(cond), detail))
R = Rec()
ns = dict(globals()); ns["R"] = R
exec(compile("\n" * start + "\n".join(lines[start:end]), path, "exec"), ns)
for n, ok, d in R.out:
    print(("ok  " if ok else "FAIL"), n[:60], "" if ok else str(d)[:300])
