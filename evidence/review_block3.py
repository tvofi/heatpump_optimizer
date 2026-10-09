"""review-2074c's OWN targeted harness (disclosed per fix-review.md step 9:
this is the reviewer's instrument, not the fixer's).

It execs the tree's own RCA-1565 block from tests/entities.py VERBATIM (lines
31594..31800 at c54beab89, sliced out of the file on disk by line marker, never
re-implemented), with the helpers `_workflow_job`, `_TESTS_YML` and `_MUT_BODY`
likewise lifted verbatim from entities.py by line marker.  Because it reads
`.github/workflows/tests.yml` and `tests/mutation_table.py` FROM DISK through
the tree's own expressions, a mutation applied to a file on disk is the arm;
nothing here re-derives a predicate.

usage: python3 -I review_block3.py <label>
"""
import pathlib
import re
import subprocess
import sys

WT = pathlib.Path("/Users/timmalmstrom/hpo-seats/review-2074c/wt")
ENT = WT / "tests" / "entities.py"
LINES = ENT.read_text().splitlines(keepends=True)


def grab(a, b):
    """entities.py's own lines a..b (1-indexed, inclusive), verbatim."""
    return "".join(LINES[a - 1:b])


# locate every helper by its own line marker in the tree, not by a carried number
def find(marker, start=0):
    for i, ln in enumerate(LINES[start:], start + 1):
        if ln.startswith(marker):
            return i
    raise SystemExit(f"marker not found: {marker!r}")


# _workflow_job: its def line to the line before the next top-level statement
WF_START = find("def _workflow_job(text: str, name: str) -> str:")
WF_END = find("_tests_workflow = Path(", WF_START)
WF_TEXT = grab(WF_START, WF_END - 1)

TESTS_YML_START = find("_TESTS_YML = (pathlib.Path(__file__)")
TESTS_YML_TEXT = grab(TESTS_YML_START, TESTS_YML_START + 1)

MUT_BODY_START = find("_MUT_BODY = pathlib.Path(_mut.__file__)")
MUT_BODY_TEXT = grab(MUT_BODY_START, MUT_BODY_START)

REGION_START = find('_mut_seed = getattr(_mut, "seed_pool_seconds", None)')
REGION_END = find("# R9-F10.12 (A): the mutant phase's wall-clock budget.")
REGION = grab(REGION_START, REGION_END - 1)

sys.path.insert(0, str(WT / "tests"))
sys.path.insert(0, str(WT / "tests" / "hastub"))
import mutation_table as _mut            # noqa: E402  the tree's own module
from harness import Results             # noqa: E402

R = Results("review-2074c targeted RCA-1565 block")

ns = {
    "__name__": "review_block3",
    "pathlib": pathlib,
    "Path": pathlib.Path,
    "json": __import__("json"),
    "os": __import__("os"),
    "re": re,
    "_re": re,
    "_mut": _mut,
    "R": R,
    "WT": WT,
    "__file__": str(ENT),
}
# the helpers entities.py itself uses, verbatim, and the module import they need
import tempfile as _tempfile_mod          # noqa: E402
import shutil as _shutil_mod              # noqa: E402
# The four stdlib aliases the block reads (entities.py imports each at module
# level: `import tempfile as _tempfile`, `import shutil as _mut_shutil`,
# `import contextlib as _mutb_contextlib`, `import io as _mutb_io`).  Bound here
# to the same stdlib modules -- a predicate, not a re-implementation.
import contextlib as _mutb_contextlib      # noqa: E402
import io as _mutb_io                      # noqa: E402
ns.update({"_tempfile": _tempfile_mod, "_mut_shutil": _shutil_mod,
           "_mutb_contextlib": _mutb_contextlib, "_mutb_io": _mutb_io})
prelude = (WF_TEXT + "\n" + TESTS_YML_TEXT + "\n" + MUT_BODY_TEXT + "\n")
exec(compile(prelude + REGION, str(ENT), "exec"), ns)

print(f"region: entities.py lines {REGION_START}..{REGION_END - 1} "
      f"({REGION.count('R.check(')} R.check calls)")
print(f"RESULT block-ran: {R.checks} checks, {R.failures} failures")
for name in ns.get("_RCA_NAMES", []):
    pass
sys.exit(1 if R.failures else 0)
