#!/usr/bin/env python3
"""r10_machinery_ratchet_mutants.py -- one mutant per predicate of the machinery ratchet, against its own self-test (R10-MACHINERY-RATCHETS).

Copies ``tools/audit/machinery_ratchet.py`` and ``tests/throwaway_git.py``
into a temporary directory at the same relative paths, applies each mutant
below to the COPY (the tree is never written, so an interrupted run leaves
nothing mutated), and runs ``python3 -I <copy> --self-test``. A mutant is
killed when that exits non-zero; the failing check names are printed.

    python3 dev/audit/harnesses/r10_machinery_ratchet_mutants.py

The unmutated copy runs first as the null control: it must pass, or every
kill below is the runner's and not the mutant's. A mutant whose text no
longer occurs exactly once prints ``stale`` rather than a verdict. The rows
are the approved design's mutation targets plus the design review's R6
(the added-by-its-own-merge test and the subject-number match) and the
counting rule's -M, -w and rename-destination choices. Exit 0 only when the
control passes and every row is killed.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
PROGRAM = "tools/audit/machinery_ratchet.py"
COPIED = (PROGRAM, "tests/throwaway_git.py")

# (name, the text replaced, its replacement) -- each must occur exactly once.
MUTANTS = (
    ("product-prefix", "    return path.startswith(PRODUCT_PREFIXES)",
     "    return path.startswith(PRODUCT_PREFIXES[:1])"),
    ("production-gt-0", "    if product > 0:\n", "    if product >= 0:\n"),
    ("record-all-paths", "    if all(is_record(p) for p in paths):",
     "    if any(is_record(p) for p in paths):"),
    ("cap-plus-band-ge", "measured[c] > doc[c] + doc[c + BAND_SUFFIX]",
     "measured[c] >= doc[c] + doc[c + BAND_SUFFIX]"),
    ("cap-without-band", "measured[c] > doc[c] + doc[c + BAND_SUFFIX]", "measured[c] > doc[c]"),
    ("pr-mode-no-drop-oldest", "            if len(rows) >= w:\n",
     "            if len(rows) >= w + (candidate is not None and not candidate[\"exempt\"]):\n"),
    ("pr-mode-candidate-ignored",
     "            (skipped if candidate[\"exempt\"] else rows).append(candidate)", "            pass"),
    ("threshold-ge", "    if not gain > THRESHOLD:", "    if not gain >= THRESHOLD:"),
    ("evidence-not-checked",
     "    if _git(repo, \"cat-file\", \"-e\", f\"{rev}:{entry['evidence']}\", check=False).returncode != 0:",
     "    if False:"),
    ("absent-at-p-not-checked", "    if _entries(_doc_at(repo, p, budgets), pr):", "    if False:"),
    ("subject-number-not-matched", "and e.get(\"pr\") == pr]", "and True]"),
    ("subject-number-not-parsed", "int(mt.group(1)) if mt else None", "None"),
    ("no-rename-detection", "\"diff\", \"-M\", \"-w\"", "\"diff\", \"--no-renames\", \"-w\""),
    ("no-whitespace-ignore", "\"diff\", \"-M\", \"-w\"", "\"diff\", \"-M\""),
    ("rename-charged-to-source", "rows.append((n(added), n(deleted), [src, dst], dst))",
     "rows.append((n(added), n(deleted), [src, dst], src))"),
    ("gain-measured-as-cost", "else (after - before) / before", "else (before - after) / before"),
)


def run(tmp: Path) -> tuple[int, list[str]]:
    r = subprocess.run([sys.executable, "-I", str(tmp / PROGRAM), "--self-test"],
                       capture_output=True, text=True)
    fails = [ln.strip() for ln in (r.stdout + r.stderr).splitlines() if ln.strip().startswith("FAIL")]
    if r.returncode != 0 and not fails:
        fails = [((r.stdout + r.stderr).strip().splitlines() or ["(no output)"])[-1]]
    return r.returncode, fails


def main() -> int:
    source = (ROOT / PROGRAM).read_text()
    with tempfile.TemporaryDirectory(prefix="mr-mutants-") as d:
        tmp = Path(d)
        for rel in COPIED:
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, tmp / rel)
        rc, fails = run(tmp)
        print(f"control  unmutated: rc={rc}" + (f" {fails}" if fails else ""))
        if rc != 0:
            print("RESULT control failed: every kill below would be the runner's")
            return 1
        killed = survived = stale = 0
        for name, old, new in MUTANTS:
            if source.count(old) != 1:
                stale += 1
                print(f"stale    {name}: its text occurs {source.count(old)} times")
                continue
            (tmp / PROGRAM).write_text(source.replace(old, new, 1))
            rc, fails = run(tmp)
            if rc != 0:
                killed += 1
                print(f"killed   {name}: {len(fails)} failing: " + " | ".join(f[5:] for f in fails[:3]))
            else:
                survived += 1
                print(f"SURVIVED {name}")
        (tmp / PROGRAM).write_text(source)
    print(f"RESULT {len(MUTANTS)} mutants: {killed} killed, {survived} survived, {stale} stale")
    return 0 if killed == len(MUTANTS) else 1


if __name__ == "__main__":
    sys.exit(main())
