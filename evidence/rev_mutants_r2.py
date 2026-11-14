#!/usr/bin/env python3
"""Reviewer's round-2 mutants for PR 3430 at ba0ed526cc3b0a4b62a4e05b165710237e3bd123 (builder: the fix reviewer, not the finder).
Each edits one file of a scratch worktree, runs tests/doc_claims.py, records FAIL lines, restores. Null = baseline."""
import subprocess, sys, os
from pathlib import Path
W = Path(sys.argv[1]); ENV = dict(os.environ, PYTHONPATH="tests/hastub")
def run():
    r = subprocess.run([sys.executable, "tests/doc_claims.py"], cwd=W, env=ENV, capture_output=True, text=True)
    out = [l.strip()[5:].split("  [")[0][:150] for l in r.stdout.splitlines() if l.strip().startswith("FAIL ")]
    return out or ([f"died rc={r.returncode}: {r.stderr.strip().splitlines()[-1][:140]}"] if r.returncode else [])
T = "tests/doc_claims.py"; D = "dev/README.md"
M = [
 ("N1 one-script rule accepts a script node naming no file", T, 'if k == "script" and len(_FILE.findall(n)) != 1]', 'if k == "script" and len(_FILE.findall(n)) > 1]'),
 ("N2 one-script rule dropped", T, 'if k == "script" and len(_FILE.findall(n)) != 1]', 'if False]'),
 ("N3 actor-file rule back to any basename in the label (round-1 shape)", T, '!= a.split()[0]:', 'not in kind[a][1]:'),
 ("N4 actor-file rule: substring of the first line", T, '!= a.split()[0]:', 'not in a:'),
 ("N5 entry kind: anything but a store", T, 'kind[entries[0]][0] != "seat":', 'kind[entries[0]][0] == "store":'),
 ("N6 page: round-1 block reinstated (state_docs.py writes roster branch, cited to roster_sync.py)", D,
  ('    docs -->|"writes"| sdoc\n', '| state_docs.py | writes | state documents and plan page |'),
  ('    docs -->|"writes"| sdoc\n    docs -->|"writes"| roster\n', '| state_docs.py | writes | roster branch | `tools/audit/seat/roster_sync.py`: `roster_edit.write_roster(` |\n| state_docs.py | writes | state documents and plan page |')),
 ("N7 page: a live node regrouped to two scripts, rows renamed with it", D, ("state_docs.py", ), ("state_docs.py, roster_sync.py",)),
 ("N8 source: the cited line removed from postmerge.py", "tools/audit/seat/postmerge.py", '/roster_sync.py", "--repo", repo, "--apply"', '/roster_sync.py",  "--repo", repo, "--apply"'),
 ("N9 source: the cited line removed from roster_edit.py", "tools/audit/seat/roster_edit.py", 'refspec = f"{head}:refs/heads/{branch}"', 'refspec  = f"{head}:refs/heads/{branch}"'),
 ("N10 page: seats node made a script shape (entry stays, a seat row then owes the one-script rule)", D, 'post -->|"runs"| rsync\n', 'rsync -->|"runs"| post\n'),
]
base = run(); print(f"null (baseline): {len(base)} FAIL line(s) {base}")
surv = 0
for what, f, old, new in M:
    p = W / f; src = p.read_text(); mut = src
    if what.startswith("N7"):
        # only inside the machinery figure's node label and the table's actor/target cells
        a = 'docs["state_docs.py"]'
        if src.count(a) != 1: print(f"ERROR {what}: anchor {src.count(a)}"); continue
        mut = src.replace(a, 'docs["state_docs.py, roster_sync.py"]').replace("| state_docs.py |", "| state_docs.py, roster_sync.py |")
    else:
        olds = old if isinstance(old, tuple) else (old,); news = new if isinstance(new, tuple) else (new,)
        bad = [o for o in olds if src.count(o) != 1]
        if bad: print(f"ERROR {what}: anchor count {[src.count(o) for o in olds]}"); continue
        for o, n in zip(olds, news): mut = mut.replace(o, n)
    p.write_text(mut)
    try: got = run()
    finally: p.write_text(src)
    surv += not got
    print(f"{'killed  ' if got else 'SURVIVED'} {what}: {' ;; '.join(got[:3]) or '-'}")
print(f"RESULT rev2_mutants={len(M)}"); print(f"RESULT rev2_survivors={surv}")
