"""R9-CI-2b: does tests/closures.json merge on GitHub, which runs no merge driver?

    python3 dev/audit/harnesses/r9_ci2b_closures_merge.py pairs [N]
    python3 dev/audit/harnesses/r9_ci2b_closures_merge.py heads REF [REF ...]

Every 3-way merge here is `git merge-file` over the three blobs of
tests/closures.json, so no `merge.*` driver config can take part: this is
the merge GitHub computes `mergeStateStatus` from.

`pairs`: each of the last N (default 120) first-parent merges of a pull
request that changed tests/closures.json is a real edit (M^1 -> M). Every
ordered pair (j, k) is replayed as a branch that made edit j and a main that
made edit k on one base (M_k^1), and merged twice: as written then, and as
this tree's writer writes it -- tests/closure.py's `stable_seconds` against
the base and `write_closures`' layout. A pair whose two edits set one
non-timing key to two values is counted apart: no layout may merge it.

`heads`: each REF against origin/main from their merge base, as written and
in the layout (the four PRs DIRTY on 2026-10-08 were 2054, 2053, 2025, 2010:
fetch `refs/pull/<n>/head` first).

    RESULT pairs=<n> semantic=<n> conflicts_as_written=<n> conflicts_layout=<n>
    RESULT head=<ref> as_written=<clean|conflict> layout=<clean|conflict>

A null control is built in: with the layout off (`as_written`) the same
pairs conflict, and a pair that conflicts in the layout is printed.
"""
from __future__ import annotations

import itertools
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
import closure  # noqa: E402  (the production writer under test)

CJ = "tests/closures.json"


def git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True,
                          capture_output=True, text=True).stdout


def blob(rev: str, path: str = CJ) -> str | None:
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def conflicts(b: str, o: str, t: str) -> bool:
    with tempfile.TemporaryDirectory() as td:
        p = []
        for n, x in (("b", b), ("o", o), ("t", t)):
            p.append(os.path.join(td, n))
            Path(p[-1]).write_text(x)
        return subprocess.run(["git", "merge-file", "-p", "--quiet", p[1], p[0], p[2]],
                              capture_output=True).returncode != 0


def in_layout(base: dict, side: dict) -> str:
    """`side` as this tree's writer would have written it on top of `base`."""
    side = json.loads(json.dumps(side))
    for k, r in side.get("recorded", {}).items():
        if isinstance(r, dict) and "seconds" in r:
            r["seconds"] = closure.stable_seconds(
                base.get("recorded", {}).get(k, {}).get("seconds"), r["seconds"])
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "c.json"
        closure.write_closures(out, side)
        return out.read_text()


def leaves(d, pre=()):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(leaves(v, pre + (k,)))
    elif isinstance(d, list) and all(isinstance(x, str) for x in d):
        for x in d:
            out[pre + ("\0", x)] = True
    else:
        out[pre] = json.dumps(d)
    return out


def apply(base: dict, a: dict, b: dict) -> dict:
    """`base` with the key-level edit a -> b applied."""
    lb, la, lbb = leaves(base), leaves(a), leaves(b)
    for k in set(la) | set(lbb):
        if la.get(k) != lbb.get(k):
            if k in lbb:
                lb[k] = lbb[k]
            else:
                lb.pop(k, None)
    out: dict = {}
    for k, v in lb.items():
        cur = out
        if len(k) >= 2 and k[-2] == "\0":
            for p in k[:-3]:
                cur = cur.setdefault(p, {})
            cur.setdefault(k[-3], []).append(k[-1])
        else:
            for p in k[:-1]:
                cur = cur.setdefault(p, {})
            cur[k[-1]] = json.loads(v)
    return out


def semantic(b: dict, o: dict, t: dict) -> bool:
    lb, lo, lt = leaves(b), leaves(o), leaves(t)
    for k in set(lb) | set(lo) | set(lt):
        if (len(k) >= 2 and k[-2] == "\0") or k[-1] == "seconds":
            continue
        if lo.get(k) != lb.get(k) and lt.get(k) != lb.get(k) and lo.get(k) != lt.get(k):
            return True
    return False


def pairs(n: int) -> int:
    edits = []
    for line in git("log", "--first-parent", "--merges", "--format=%H %s",
                    "-n", str(n), "origin/main").splitlines():
        h, s = line.split(" ", 1)
        a, b = blob(h + "^1"), blob(h)
        if s.startswith("Merge pull request") and a and b and a != b:
            edits.append((s.split()[3], json.loads(a), json.loads(b)))
    count = sem = c0 = c1 = 0
    for (pj, aj, bj), (pk, ak, bk) in itertools.permutations(edits, 2):
        ours = apply(ak, aj, bj)
        count += 1
        if semantic(ak, ours, bk):
            sem += 1
            continue
        written = [json.dumps(x, indent=1) + "\n" for x in (ak, ours, bk)]
        c0 += conflicts(*written)
        base = in_layout(ak, ak)
        lay = conflicts(base, in_layout(ak, ours), in_layout(ak, bk))
        c1 += lay
        if lay:
            print(f"layout conflict: branch {pj} against main {pk}")
    print(f"RESULT pairs={count} semantic={sem} conflicts_as_written={c0} "
          f"conflicts_layout={c1}")
    return 0


def heads(refs: list[str]) -> int:
    for ref in refs:
        mb = git("merge-base", ref, "origin/main").strip()
        b, o, t = blob(mb), blob(ref), blob("origin/main")
        if None in (b, o, t):
            print(f"RESULT head={ref} as_written=missing layout=missing")
            continue
        B, O, T = (json.loads(x) for x in (b, o, t))
        w = "conflict" if conflicts(b, o, t) else "clean"
        lay = "conflict" if conflicts(in_layout(B, B), in_layout(B, O),
                                      in_layout(B, T)) else "clean"
        print(f"RESULT head={ref} as_written={w} layout={lay}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "pairs":
        raise SystemExit(pairs(int(sys.argv[2]) if len(sys.argv) > 2 else 120))
    if len(sys.argv) >= 3 and sys.argv[1] == "heads":
        raise SystemExit(heads(sys.argv[2:]))
    print(__doc__)
    raise SystemExit(2)
