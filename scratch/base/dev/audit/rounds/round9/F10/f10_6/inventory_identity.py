#!/usr/bin/env python3
"""F10.6 null control: the ratcheted inventory is the same under REF's grader.

    python3 tools/audit/round9/F10/f10_6/inventory_identity.py origin/main

Runs `inventory()` from this tree's tests/mutation_table.py and from REF's
copy (compiled from `git show`, bound to this tree's paths, no file written)
over the same production tree, and prints each side's count, the first 12 hex
of sha1 over every (anchor, kind, old, new), and the ledger's unpinned count.
A grader that let CMP_BOUND into the default inventory would print two
different lines.
"""
import hashlib
import subprocess
import sys
import types
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as head  # noqa: E402


def graded(ref: str) -> types.ModuleType:
    src = subprocess.run(["git", "show", f"{ref}:tests/mutation_table.py"],
                         capture_output=True, text=True, check=True).stdout
    mod = types.ModuleType("mutation_table_ref")
    mod.__file__ = str(Path("tests/mutation_table.py").resolve())
    sys.modules[mod.__name__] = mod
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    return mod


def line(name: str, mt: types.ModuleType) -> str:
    sites = mt.inventory()
    digest = hashlib.sha1(repr([(s["anchor"], s["kind"], s["old"], s["new"])
                                for s in sites]).encode()).hexdigest()[:12]
    loose = len(mt.unpinned_sites(head.load_budgets(), sites))
    return f"RESULT inventory {name} sites={len(sites)} sha1={digest} unpinned={loose}"


print(line("head", head))
print(line(sys.argv[1], graded(sys.argv[1])))
