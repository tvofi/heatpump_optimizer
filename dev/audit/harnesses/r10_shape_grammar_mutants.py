#!/usr/bin/env python3
"""R10-996-RUNNER-CLAIMS: the shape-claim pins against one-line mutants of env_drift.py.

    python3 dev/audit/harnesses/r10_shape_grammar_mutants.py            # all
    python3 dev/audit/harnesses/r10_shape_grammar_mutants.py R13 R14    # named

Run from a clean checkout of the branch: each mutant rewrites the committed
tests/env_drift.py in place and restores its bytes, and a dirty file refuses
first. The pins are tests/entities.py's own block, from `_R996_MSG = ` up to
`# The instance counter.`, executed in a child against the file as it stands
(every R.check counted). M0 is the null control: the unmutated file, where
every pin must pass. R1..R17 are the fix review's seventeen mutants of #2843
(review/2843, evidence/mutate.py), re-keyed to this file's lines; R10 drops
the `path.startswith(prefix)` guard in shaped_leaves, which `_diff_leaves`
makes unreachable from judge_drift (an equivalent mutant, expected SURVIVED).
Prints `RESULT pins=<n> fails=<n>` for M0, one line per mutant, `KILLED` or
`SURVIVED`, then `RESULT mutants=<n> killed=<n>`; exit 1 when M0 fails or any
mutant but R10 survives.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
    check=True).stdout.strip())
TARGET = "tests/env_drift.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutant_guard  # noqa: E402 -- restores the mutated file on a kill (SIGTERM/SIGINT) and refuses a leftover mutant
EQUIVALENT = {"R10"}

MUTANTS = {
    "R1": ("            and self.paths.fullmatch(leaf) is not None\n", ""),
    "R2": ("and new in self.tos and old not in self.tos", "and new in self.tos"),
    "R3": ("and new in self.tos and old not in self.tos", "and old not in self.tos"),
    "R4": ("            and (self.froms is None or old in self.froms)\n", ""),
    "R5": ("isinstance(old, str) and isinstance(new, str)\n            and ", ""),
    "R6": ("        matched |= hits\n", ""),
    "R7": ("        shape_hits |= matched\n", ""),
    "R8": ("    claimed_hits.extend(sorted(shape_hits))\n", ""),
    "R9": ("        elif not loose:\n", "        elif True:\n"),
    "R10": ("if path.startswith(prefix) and shape.matches", "if shape.matches"),
    "R11": ("    if froms is not None and froms & tos:\n", "    if False:\n"),
    "R12": ("_SHAPE_LITERAL = re.compile(r\"'[^'\\s|#\\\\]*'\")",
            "_SHAPE_LITERAL = re.compile(r\".*\")"),
    "R13": (r'.replace(r"\[\*\]", r"\[\d+\]")', r'.replace(r"\[\*\]", r".*")'),
    "R14": (r'.replace(r"\*", r"[^.\[\]]*"))', r'.replace(r"\*", r".*"))'),
    "R15": ("        scope_problem = (may_drift_error(may_drift, claims)\n"
            "                         or shape_claim_error(claims))",
            "        scope_problem = (may_drift_error(may_drift, claims))"),
    "R16": ("    if name.startswith(SHAPE_CLAIM_MARKER):\n        return (\n"
            "            f\"SHAPE CLAIM MATCHED",
            "    if False:\n        return (\n            f\"SHAPE CLAIM MATCHED"),
    "R17": ("match = _SHAPE_LINE.fullmatch(line)", "match = _SHAPE_LINE.match(line)"),
}

# The child: the entities.py block, its R replaced by a counter, run against
# tests/env_drift.py as it stands on disk.
CHILD = r'''
import ast as _ast_af, contextlib as _d7_contextlib, io as _d7_io, sys
from pathlib import Path
sys.path.insert(0, "tests")
import env_drift as _env_drift
class _R:
    n = 0
    fails = []
    def check(self, name, ok, detail=""):
        self.n += 1
        if not ok:
            self.fails.append(name)
            print("FAIL", name, "|", detail)
R = _R()
lines = Path("tests/entities.py").read_text().splitlines()
def _at(prefix):
    return next(i for i, l in enumerate(lines) if l.startswith(prefix))
exec(compile("\n".join(lines[_at("_R996_MSG = "):_at("# The instance counter.")]),
             "tests/entities.py", "exec"))
print(f"RESULT pins={R.n} fails={len(R.fails)}")
'''


def pins() -> str:
    # Bytecode-free: a mutant can share the clean file's size and mtime
    # second, so a cached env_drift .pyc would stand in for the mutant. -B
    # writes none, and an empty cache prefix leaves none to read.
    with tempfile.TemporaryDirectory() as cache:
        proc = subprocess.run(
            [sys.executable, "-B", "-c", CHILD], cwd=ROOT, capture_output=True,
            text=True, env={"PYTHONPATH": "tests/hastub", "PATH": "/usr/bin:/bin",
                            "PYTHONPYCACHEPREFIX": cache},
        )
    out = (proc.stdout + proc.stderr).strip().splitlines()
    result = [line for line in out if line.startswith("RESULT pins=")]
    return result[0] if result else "CRASH " + (out[-1] if out else "no output")


def main(names: list[str]) -> int:
    path = ROOT / TARGET
    mutant_guard.arm([TARGET], root=ROOT)
    clean = path.read_bytes()
    src = clean.decode()
    null = pins()
    print(f"M0 {null}")
    bad = not null.endswith(" fails=0")
    chosen = names or list(MUTANTS)
    killed = 0
    try:
        for name in chosen:
            old, new = MUTANTS[name]
            if src.count(old) != 1:
                print(f"{name}: anchor count {src.count(old)} NOT APPLIED")
                bad = True
                continue
            path.write_text(src.replace(old, new))
            got = pins()
            path.write_bytes(clean)
            dead = not got.endswith(" fails=0")
            killed += dead
            print(f"{name}: {got} {'KILLED' if dead else 'SURVIVED'}")
            if not dead and name not in EQUIVALENT:
                bad = True
    finally:
        path.write_bytes(clean)
    print(f"RESULT mutants={len(chosen)} killed={killed}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
