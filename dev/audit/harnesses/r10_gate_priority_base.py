#!/usr/bin/env python3
"""Run the gate lease's priority cases against a BASE ``tests/gate_lock.py``.

    python3 dev/audit/harnesses/r10_gate_priority_base.py [BASE_REF]

The cases live in the head's ``tests/gate_lock.py`` and take the module under
test as an argument (``_priority_cases(g)``), so the same arms can be driven
against another revision's copy. This loads ``BASE_REF``'s (default
``origin/main``) and prints each case's verdict. On a base that predates the
priority channel the ordering arms fail -- the base lease ignores both the
environment and a ticket's priority -- while the renew guard and the
concurrency control pass at both ends.

Exit 0 when the base shows at least one failure: the demonstration is live.
Exit 1 when every case passes at the base, which means the ref is not a
baseline and the failing-first evidence is void; the harness says so rather
than printing a green that proves nothing.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
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


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str]) -> int:
    ref = argv[1] if len(argv) > 1 else "origin/main"
    shown = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:tests/gate_lock.py"],
                           capture_output=True, text=True)
    if shown.returncode != 0:
        print(f"r10_gate_priority_base: no tests/gate_lock.py at {ref}: "
              f"{(shown.stderr or shown.stdout).strip()[:200]}")
        return 1
    with tempfile.TemporaryDirectory() as td:
        base_path = Path(td) / "gate_lock_base.py"
        base_path.write_text(shown.stdout)
        base = _load("gate_lock_base", base_path)
    head = _load("gate_lock_head", ROOT / "tests" / "gate_lock.py")
    rows = head._priority_cases(base)
    for name, ok, detail in rows:
        print(("PASS" if ok else "FAIL"), "|", name, "|", detail)
    failed = [name for name, ok, _ in rows if not ok]
    print(f"{ref}: {len(failed)} of {len(rows)} priority cases FAILED")
    if not failed:
        print("r10_gate_priority_base: every case passes at the base -- this ref "
              "is not a baseline, so the failing-first evidence is void")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
