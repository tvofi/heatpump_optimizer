"""Reviewer's TARGETED block run of PR #2074's five new entities.py checks.

Executes the tree's OWN source region (entities.py's RCA-1565 block, verbatim,
located by its text markers) against a named tree, so no check is re-implemented
here. Used for step 14: revert tests/mutation_table.py to the merge base, run the
block, restore — a pin that passes on both trees is a metric move, not a check.

usage: review_block.py <worktree> <label>
"""
import sys
from pathlib import Path

WT = Path(sys.argv[1])
LABEL = sys.argv[2] if len(sys.argv) > 2 else str(WT)
START = '_mut_seed = getattr(_mut, "seed_pool_seconds", None)'
END = "# R9-F10.12 (A): the mutant phase's wall-clock budget."

src = (WT / "tests" / "entities.py").read_text().splitlines(keepends=True)
i = next(n for n, ln in enumerate(src) if ln.startswith(START))
j = next(n for n, ln in enumerate(src) if n > i and ln.startswith(END))
block = "".join(src[i:j])
print(f"# {LABEL}: entities.py lines {i + 1}..{j} ({j - i} source lines)")
print(f"# mutation_table.py in this tree: "
      f"seed_pool_seconds present = "
      f"{'def seed_pool_seconds' in (WT / 'tests' / 'mutation_table.py').read_text()}")

sys.path.insert(0, str(WT / "tests"))
sys.path.insert(0, str(WT / "tests" / "hastub"))
import contextlib as _mutb_contextlib  # noqa: E402
import io as _mutb_io  # noqa: E402
import shutil as _mut_shutil  # noqa: E402
import tempfile as _tempfile  # noqa: E402
import mutation_table as _mut  # noqa: E402
from harness import Results  # noqa: E402
from pathlib import Path  # noqa: E402,F811

R = Results(f"RCA-1565 block (reviewer targeted run: {LABEL})")
ns = dict(__name__="__review_block__", R=R, _mut=_mut, _mut_shutil=_mut_shutil,
          _mutb_io=_mutb_io, _mutb_contextlib=_mutb_contextlib,
          _tempfile=_tempfile, Path=Path)
try:
    exec(compile(block, str(WT / "tests" / "entities.py"), "exec"), ns)
except Exception as exc:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    print(f"RESULT targeted-block[{LABEL}]: EXCEPTION {type(exc).__name__}: {exc}")
    sys.exit(2)
rc = R.close("RCA-1565 BLOCK CHECKS")
print(f"RESULT targeted-block[{LABEL}]: {R.failures} of {R.checks} failed (exit {rc})")
