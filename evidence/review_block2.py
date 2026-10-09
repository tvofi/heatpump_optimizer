"""Reviewer's TARGETED block run of PR #2074's seven RCA-1565 entities.py checks.

Round 2. Executes the tree's OWN source region (entities.py's RCA-1565 block,
verbatim, located by its text markers) against a named tree, so no check is
re-implemented here. The preamble supplies the names the block reads; `_workflow_job`
and the `_TESTS_YML` assignment are lifted from entities.py itself, verbatim, by
line marker -- the two new wiring pins key on them, so a hand-written copy would be
my instrument, not the tree's.

usage: review_block2.py <worktree> <label>
"""
import re
import sys
from pathlib import Path

WT = Path(sys.argv[1])
LABEL = sys.argv[2] if len(sys.argv) > 2 else str(WT)
START = '_mut_seed = getattr(_mut, "seed_pool_seconds", None)'
END = "# R9-F10.12 (A): the mutant phase's wall-clock budget."
WJ_START = "def _workflow_job(text: str, name: str) -> str:"
YML_START = "_TESTS_YML = (pathlib.Path(__file__).resolve().parents[1]"

ent_path = WT / "tests" / "entities.py"
src = ent_path.read_text().splitlines(keepends=True)


def _span(pred, after=0):
    n = next(k for k, ln in enumerate(src) if k >= after and ln.startswith(pred))
    return n


i = _span(START)
j = next(n for n, ln in enumerate(src) if n > i and ln.startswith(END))
block = "".join(src[i:j])
wj = _span(WJ_START)
wj_end = next(n for n in range(wj, len(src)) if src[n].startswith("_tests_workflow"))
wj_src = "".join(src[wj:wj_end])
ym = _span(YML_START)
yml_src = "".join(src[ym:ym + 2])
print(f"# {LABEL}: entities.py lines {i + 1}..{j} ({j - i} source lines)")
print(f"# lifted _workflow_job from lines {wj + 1}..{wj_end}; "
      f"_TESTS_YML from {ym + 1}..{ym + 2}")
print(f"# mutation_table.py seed_pool_seconds present = "
      f"{'def seed_pool_seconds' in (WT / 'tests' / 'mutation_table.py').read_text()}")
print(f"# tests.yml --pool-seconds occurrences = "
      f"{(WT / '.github' / 'workflows' / 'tests.yml').read_text().count('--pool-seconds')}")

sys.path.insert(0, str(WT / "tests"))
sys.path.insert(0, str(WT / "tests" / "hastub"))
import contextlib as _mutb_contextlib  # noqa: E402
import io as _mutb_io  # noqa: E402
import pathlib  # noqa: E402
import shutil as _mut_shutil  # noqa: E402
import tempfile as _tempfile  # noqa: E402
import mutation_table as _mut  # noqa: E402
from harness import Results  # noqa: E402

R = Results(f"RCA-1565 block (reviewer targeted run: {LABEL})")
ns = dict(__name__="__review_block__", __file__=str(ent_path), R=R, _mut=_mut,
          _mut_shutil=_mut_shutil, _mutb_io=_mutb_io,
          _mutb_contextlib=_mutb_contextlib, _tempfile=_tempfile, Path=Path,
          pathlib=pathlib, _re=re, re=re)
ns["_MUT_BODY"] = Path(_mut.__file__).read_text()
for _frag in (wj_src, yml_src):
    exec(compile(_frag, str(ent_path), "exec"), ns)
try:
    exec(compile(block, str(ent_path), "exec"), ns)
except Exception as exc:  # noqa: BLE001
    import traceback
    traceback.print_exc()
    print(f"RESULT targeted-block[{LABEL}]: EXCEPTION {type(exc).__name__}: {exc}")
    sys.exit(2)
print(f"RESULT targeted-block[{LABEL}]: {R.failures} of {R.checks} failed")
