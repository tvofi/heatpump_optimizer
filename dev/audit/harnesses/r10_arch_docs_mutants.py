#!/usr/bin/env python3
"""R10-ARCH-DOCS (#2395): each predicate line of the machinery-edge and due-marker checks, mutated, against doc_claims.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_arch_docs_mutants.py

THE RULE. MUTANTS below is one row per predicate of `machinery_edge_findings` and `due_marker_findings` in
tests/doc_claims.py: the exact source text of the test, and what replaces it so the predicate can never fire. A row
whose text is not in the file exactly once is an error, not a skip, so a predicate renamed away from its mutant is
seen. The mutated source is executed in a child with `__file__` set to the real path; nothing is written to the tree.
A mutant is killed when the child prints a FAIL line or dies. The baseline, unmutated, must print none.

Prints one line per mutant with the checks that failed, then `RESULT baseline_fails=`, `RESULT mutants=` and
`RESULT killed=`. Exit 1 unless the baseline is clean and every mutant is killed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path



def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
TARGET = ROOT / "tests" / "doc_claims.py"
MUTANTS = (
    ("due marker", 'for r in rows if r["due"] and r["scope"] == "wiring"]', 'for r in rows if False]'),
    ("verb", "if verb not in MACHINERY_VERBS:", "if False:"),
    ("store as actor", 'if nodes[a][1] == "store":', "if False:"),
    ("writes ends at a store", 'elif (verb == "writes") != (nodes[b][1] == "store"):', "elif False:"),
    ("arrow with no row", "sorted(drawn - cited)]", "()]"),
    ("row with no arrow", "sorted(cited - drawn)]", "()]"),
    ("quoted text in the cited file", "elif quote not in src:", "elif False:"),
    ("cited file tracked", 'if src is None:\n            out.append(f"{a} -{v}-> {b}: cites', 'if False:\n            out.append(f"{a} -{v}-> {b}: cites'),
    ("cited file is the actor's", '!= a.split()[0]:', '!= a.split()[0] and False:'),
    ("one script per node", 'if k == "script" and len(_FILE.findall(n)) != 1]', 'if False]'),
    ("the entry is a seat", ' or kind[entries[0]][0] != "seat":', ' or False:'),
    ("one entry", 'if len(entries) != 1 or kind[entries[0]][0] != "seat":', "if False:"),
    ("one arrow per line", "if not m or m.group(1) not in nodes or m.group(3) not in nodes:", "if False:"),
    ("node names unique", "if list(name.values()).count(n) > 1})]", "if False})]"),
)
RUNNER = ("import sys; sys.argv = [sys.argv[1]]; sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0]); "
          "exec(compile(sys.stdin.read(), sys.argv[0], 'exec'), {'__name__': '__main__', '__file__': sys.argv[0]})")


def fails(src: str) -> list[str]:
    r = subprocess.run([sys.executable, "-c", RUNNER, str(TARGET)], input=src, capture_output=True, text=True, cwd=ROOT)
    out = [line.strip()[5:].split("  [")[0] for line in r.stdout.splitlines() if line.strip().startswith("FAIL ")]
    return out or ([f"died rc={r.returncode}: {r.stderr.strip().splitlines()[-1][:120]}"] if r.returncode else [])


def main() -> int:
    src = TARGET.read_text()
    base = fails(src)
    print(f"baseline: {len(base)} FAIL line(s)")
    killed = 0
    for what, old, new in MUTANTS:
        if src.count(old) != 1:
            print(f"ERROR {what}: {old!r} is in the file {src.count(old)} time(s), not once")
            return 2
        got = fails(src.replace(old, new))
        killed += bool(got)
        print(f"{'killed  ' if got else 'SURVIVED'} {what}: {'; '.join(got) or '-'}")
    print(f"RESULT baseline_fails={len(base)}")
    print(f"RESULT mutants={len(MUTANTS)}")
    print(f"RESULT killed={killed}")
    return 0 if not base and killed == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
