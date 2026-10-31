#!/usr/bin/env python3
"""#3051 round 2: the P206/P211 lease sites the review named each die alone.

Written by the R10-PREPR-CAP fixer, round 2. Each mutant is applied to a COPY
of the files it touches (never the tree), and the check that pins it is run
against the copy:

  M-remark   tests/gate_lock.py flock_wrap's `except RenewRefused` arm drops
             the re-mark of the held witness after `release`;
             `gate_lock.py --accept` must FAIL `a bounded give-up on re-queue
             keeps the witness; the next wrap queues again`.
  M-nomap    tests/run.sh leased() loses its `if [ -e "$one.waited" ]` block;
             entities.py's `_gl_run_sh_wait_unrun` must turn `map` red.
  M-word     tests/run.sh run_always's lane branch loses the SKIP word;
             `_gl_run_sh_wait_unrun` must turn `word` red.

`_gl_run_sh_wait_unrun` is run alone: its source and `_gl_stub_tree`'s are
read from the copy's entities.py and executed, with `_closure.ROOT` pointing
at the copy, so the check run is the committed one, not a re-implementation.
Null control: M0, nothing mutated, must print failed=0; a mutant whose
pattern is not found exactly once aborts. Metric:

  RESULT mutant=<name> failed=<n> verdict=killed|SURVIVED
  RESULT mutants=<n> survived=<n>

    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_prepr_cap_lease_mutants.py
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FILES = ("tests/gate_lock.py", "tests/run.sh", "tests/entities.py", "tests/closures.json")
MUTANTS = [
    ("M0", None, "", "", None),
    ("M-remark", "tests/gate_lock.py",
     "        _mark_held(lock_dir, label)  # a bounded give-up below still held it once\n", "",
     "gate"),
    ("M-nomap", "tests/run.sh",
     '      if [ -e "$one.waited" ]; then\n        WAIT_UNRUN="$s"\n        return 0\n      fi\n', "",
     "map"),
    ("M-word", "tests/run.sh", '    [ -z "$WAIT_UNRUN" ] || word=SKIP\n', "", "word"),
]


def gate_accept(copy: Path) -> int:
    """FAIL lines of the copy's `gate_lock.py --accept`."""
    # The copy's own directory is first on sys.path; the tree's tests/ lends
    # `harness` (Results) and nothing the mutants touch.
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(
        (str(ROOT / "tests/hastub"), str(ROOT / "tests")))}
    env = {k: v for k, v in env.items() if not k.startswith(("HPO_GATE", "HPO_SLOT"))}
    out = subprocess.run([sys.executable, str(copy / "tests/gate_lock.py"), "--accept"],
                         capture_output=True, text=True, timeout=600, env=env).stdout
    if "gate lock acceptance checks" not in out:
        return -1
    return sum(1 for ln in out.splitlines() if ln.lstrip().startswith("FAIL"))


def run_sh_checks(copy: Path) -> dict[str, bool]:
    """entities.py's `_gl_run_sh_wait_unrun`, run alone against the copy."""
    sys.path.insert(0, str(copy / "tests"))
    try:
        import gate_lock
        src = (copy / "tests/entities.py").read_text()
        ns = dict(_closure=types.SimpleNamespace(ROOT=copy), _gate_lock=gate_lock, _re=re,
                  _tempfile=tempfile, _os=os, _subprocess=subprocess, _time=time,
                  Path=Path, sys=sys)
        for fn in ("_gl_stub_tree", "_gl_run_sh_wait_unrun"):
            m = re.search(r"(?ms)^def %s\(.*?(?=^\S)" % fn, src)
            if m is None:
                raise SystemExit(f"{fn} not found in entities.py")
            exec("from __future__ import annotations\n" + m.group(0), ns)
        return {k: ok for k, (ok, _d) in ns["_gl_run_sh_wait_unrun"]().items()}
    finally:
        sys.path.pop(0)
        sys.modules.pop("gate_lock", None)


def main() -> int:
    survived = 0
    for name, rel, old, new, pin in MUTANTS:
        with tempfile.TemporaryDirectory() as tds:
            copy = Path(tds)
            for f in FILES:
                (copy / f).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / f, copy / f)
            if rel is not None:
                text = (copy / rel).read_text()
                if text.count(old) != 1:
                    raise SystemExit(f"{name}: pattern found {text.count(old)} times in {rel}")
                (copy / rel).write_text(text.replace(old, new))
            failed = 0
            if pin in (None, "gate"):
                failed += gate_accept(copy)
            if pin in (None, "map", "word"):
                failed += sum(1 for ok in run_sh_checks(copy).values() if not ok)
        killed = failed > 0
        verdict = ("clean" if failed == 0 else "DIRTY") if rel is None else (
            "killed" if killed else "SURVIVED")
        survived += rel is not None and not killed
        print(f"RESULT mutant={name} failed={failed} verdict={verdict}", flush=True)
        if rel is None and failed != 0:
            print("RESULT null control M0 failed: the unmutated copy is red", flush=True)
            return 1
    print(f"RESULT mutants={len(MUTANTS) - 1} survived={survived}")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
