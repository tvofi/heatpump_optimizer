#!/usr/bin/env python3
"""R11-CI-CASE-SELECT P2: each plan rule, fail-safe and the run.sh wiring against a mutant.

    python3 dev/audit/harnesses/case_select_p2_mutants.py            # all
    python3 dev/audit/harnesses/case_select_p2_mutants.py M3 M7      # named

Run from the branch's worktree. Each mutant is one text substitution that must
apply exactly once, made in a copy of `tests/` under a temp directory (the
branch's own tree is never edited), followed by that copy's
`tests/case_select.py --self-test`. M0 is the unmutated copy and must pass
every check. A mutant is KILLED when the self-test exits non-zero AND one of
its aimed checks (a substring of a FAIL line) is red; any other red reads
OFF-TARGET. Prints one line per mutant, then `RESULT survivors=<n>`; exits 1
when any survived or went off target, or M0 failed.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CS = "tests/case_select.py"
RUN = "tests/run.sh"

MUTANTS = {
    "M0": (CS, None, None, None),
    "M1": (CS, 'elif units & set(rec["files"]):', "elif False:", "plan (i)"),
    "M2": (CS, 'elif rec["hash"] != s.hash:', "elif False:", "an edited span runs"),
    "M3": (CS, 'if header_hash != e["header_hash"]:', "if False:", "a header edit with the table's blob"),
    "M4": (CS, "for sid in _closure(direct, users) - direct:", "for sid in set():", "plan (iii)"),
    "M5": (CS, "for sid in _closure(set(rule), needs) - set(rule):", "for sid in set():", "plan (v)"),
    "M6": (CS, 'needs[s.id] |= set(e["spans"].get(s.id, {}).get("needs", ())) & ids', "pass",
           "a recorded need the static rule cannot see"),
    "M7": (CS, '                sets.add("@random")  # a draw moves', '                pass  # a draw moves',
           "an RNG consumer pulls in every earlier consumer"),
    "M8": (CS, '            elif isinstance(n.func, ast.Attribute) and n.func.attr in INPLACE and _root(n.func.value):\n'
               '                muts.add(_root(n.func.value))',
           '            elif False:\n                pass', "the later span that reads what it binds"),
    "M9": (CS, '        rule[sid] = "sample"', '        pass', "plan (iv)"),
    "M10": (CS, 'if event != "pull_request":', "if False:", "an event that is not pull_request"),
    "M11": (CS, "if f in FULL_FILES or f.startswith(FULL_PREFIXES))", "if False)", "tests/harness.py changed"),
    "M12": (CS, '"tests/case_closures.json", "tests/run.sh"', '"tests/run.sh"', "the table changed"),
    "M13": (CS, "    if table is None:\n", "    if False:\n", "no table runs"),
    "M14": (CS, "    if e is None:\n        return full(", "    if False:\n        return full(", "no entry"),
    "M15": (CS, "    if not spans:\n        return full(", "    if False:\n        return full(", "no span runs"),
    "M16": (CS, 'if e["blob"] not in (base_blob, head_blob):', "if False:", "a blob that is neither"),
    "M17": (CS, "    if twice:\n", "    if False:\n", "an ambiguous id"),
    "M18": (CS, 'if n.func.id in ("exec", "eval") and len(n.args) < 2 and not n.keywords:', "if False:",
            "an exec in the module namespace"),
    "M19": (CS, 'and inner.func.id in ("globals", "vars") and not inner.args:', "and False:",
            "a write through globals()"),
    "M20": (CS, "if any(full == r or full.startswith(r + \".\") for r in _STATE_ROOTS):", "if False:",
            "an RNG setter bound to a plain name"),
    "M21": (RUN, 'if [ -n "$SCOPE_RUN" ] && [ "$#" -eq 2 ]', 'if false && [ "$#" -eq 2 ]',
            "run.sh: a scoped run sends a case script through the gate"),
    "M22": (RUN, "tests/case_select.py) ;; tests/*.py", "tests/*.py", "keyed on the case script"),
    "M23": (CS, "    if not seed or fraction <= 0:\n", "    if fraction <= 0:\n", "sample: one seed"),
}
# M23 mutates the sampler, which lives beside case_select.
SAMPLER = {"M23": "tests/case_sample.py"}


def one(name: str) -> tuple[str, str]:
    path, old, new, aim = MUTANTS[name]
    path = SAMPLER.get(name, path)
    with tempfile.TemporaryDirectory(prefix=f"cs-p2-{name}-") as tmp:
        shutil.copytree(ROOT / "tests", Path(tmp) / "tests", symlinks=True,
                        ignore=shutil.ignore_patterns("__pycache__", "golden", "mutation_ledger"))
        shutil.copytree(ROOT / "tools" / "merge", Path(tmp) / "tools" / "merge")
        if old is not None:
            target = Path(tmp) / path
            text = target.read_text()
            if text.count(old) != 1:
                return name, f"UNAPPLIED ({text.count(old)} matches in {path})"
            target.write_text(text.replace(old, new))
        r = subprocess.run([sys.executable, str(Path(tmp) / CS), "--self-test"], capture_output=True,
                           text=True, cwd=tmp, env=dict(os.environ, PYTHONPATH=str(Path(tmp) / "tests" / "hastub")))
        fails = [ln.strip()[len("FAIL "):] for ln in r.stdout.splitlines() if ln.strip().startswith("FAIL ")]
    if old is None:
        return name, "PASS" if r.returncode == 0 and not fails else f"BASELINE RED rc={r.returncode} {fails[:3]}"
    if r.returncode == 0:
        return name, "SURVIVED"
    hit = [f for f in fails if aim in f]
    return name, (f"KILLED rc={r.returncode} by: {hit[0][:110]}" if hit
                  else f"OFF-TARGET rc={r.returncode} {fails[:2]} {r.stderr[-200:]}")


def main(argv: list[str]) -> int:
    names = argv or list(MUTANTS)
    bad = 0
    for n in names:
        name, verdict = one(n)
        print(f"{name:4} {verdict}", flush=True)
        bad += not (verdict.startswith("KILLED") or verdict == "PASS")
    print(f"RESULT survivors={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
