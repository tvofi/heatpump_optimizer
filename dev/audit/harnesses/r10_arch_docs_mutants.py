#!/usr/bin/env python3
"""R10-ARCH-DOCS (#2395): each predicate line of the machinery-edge and due-marker checks, mutated, against doc_claims.

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_arch_docs_mutants.py

THE RULE. MUTANTS below is one row per predicate of `machinery_edge_findings` and `due_marker_findings` in
tests/doc_claims.py: the exact source text of the test, and what replaces it so the predicate can never fire. A row
whose text is not in the file exactly once is an error, not a skip, so a predicate renamed away from its mutant is
seen. The mutated source is executed in a child with `__file__` set to the real path; nothing is written to the tree.
A mutant is killed when the child prints a FAIL line or dies. The baseline, unmutated, must print none.

LIVE below is the two calls those checks make on the pages themselves. Dropping one cannot fail on a clean page, so
each is shown three ways instead: alone it reads as the baseline; with a defect planted in the text the check reads
the kept call fails by name; with the plant and the dropped call that name is gone.

Prints one line per mutant with the checks that failed, one per live call, then `RESULT baseline_fails=`,
`RESULT mutants=`, `RESULT killed=`, `RESULT live_calls=` and `RESULT live_calls_shown=`. Exit 1 unless the
baseline is clean, every mutant is killed and every live call is shown.
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
    ("a script node names a script (reviewer's N1)", "len(_FILE.findall(n)) != 1]", "len(_FILE.findall(n)) > 1]"),
    ("a script node names no second script", "len(_FILE.findall(n)) != 1]", "len(_FILE.findall(n)) < 1]"),
    ("the cited file is the node's first word, not a part of it (reviewer's N4)", "!= a.split()[0]:", "not in a:"),
    ("a store is no entry (reviewer's P3)", 'if nodes[i][1] != "store" and all(b != n', "if all(b != n"),
    ("the entry is a seat", ' or kind[entries[0]][0] != "seat":', ' or False:'),
    ("one entry", 'if len(entries) != 1 or kind[entries[0]][0] != "seat":', "if False:"),
    ("one arrow per line", "if not m or m.group(1) not in nodes or m.group(3) not in nodes:", "if False:"),
    ("node names unique", "if list(name.values()).count(n) > 1})]", "if False})]"),
)
# The two live calls (reviewer's P7, P8). A mutant that drops the call a check makes on the page itself cannot be
# told from the baseline while the page is clean: both read no finding. So each is run three ways. Alone, it must
# read exactly as the baseline does. With a defect planted in what the check reads (in the child's source, never in
# the tree), the unmutated check must fail by name. With the plant and the mutant together that name must be gone:
# the dropped call is the one that fires.
LIVE = (
    ("the due-marker call on the pages (reviewer's P7)",
     "    due = due_marker_findings(rows)\n", "    due = []\n",
     "    docs = marker_docs()\n    stages = roster_stages()\n    rows = marker_census(docs, stages or {})\n",
     "    docs = marker_docs()\n    stages = roster_stages()\n"
     "    docs = {**docs, MACHINERY_DOC: docs[MACHINERY_DOC] + '\\n- planted [target: '"
     " + sorted(g for g, st in (stages or {}).items() if st == 'done')[0] + ']\\n'}\n"
     "    rows = marker_census(docs, stages or {})\n",
     "no wiring marker names only done groups: each is resolved into a statement of the tree (#2395)"),
    ("the machinery call on the page (reviewer's P8)",
     "    errs = machinery_edge_findings(text, _read_tracked(tree))\n", "    errs = []\n",
     "    text = (ROOT / MACHINERY_DOC).read_text()\n",
     "    text = (ROOT / MACHINERY_DOC).read_text()\n    _planted = '    tloop -->|\"runs\"| relay\\n'\n"
     "    assert text.count(_planted) == 1\n"
     "    text = text.replace(_planted, '    relay -->|\"runs\"| tloop\\n')\n",
     "every arrow is cited, every citation holds in the tree, and the figure has one entry"),
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
    shown = 0
    for what, old, new, plant_old, plant_new, name in LIVE:
        if src.count(old) != 1 or src.count(plant_old) != 1:
            print(f"ERROR {what}: anchors in the file {src.count(old)} and {src.count(plant_old)} time(s), not once each")
            return 2
        alone = fails(src.replace(old, new))
        planted = fails(src.replace(plant_old, plant_new))
        both = fails(src.replace(plant_old, plant_new).replace(old, new))
        ok = alone == base and name in planted and name not in both
        shown += ok
        print(f"{'shown   ' if ok else 'NOT SHOWN'} {what}: alone {len(alone)} FAIL line(s); planted defect, call kept: "
              f"{'; '.join(planted) or '-'}; planted defect, call dropped: {'; '.join(both) or '-'}")
    print(f"RESULT baseline_fails={len(base)}")
    print(f"RESULT mutants={len(MUTANTS)}")
    print(f"RESULT killed={killed}")
    print(f"RESULT live_calls={len(LIVE)}")
    print(f"RESULT live_calls_shown={shown}")
    return 0 if not base and killed == len(MUTANTS) and shown == len(LIVE) else 1


if __name__ == "__main__":
    sys.exit(main())
