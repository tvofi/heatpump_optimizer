#!/usr/bin/env python3
"""claim_merge_census.py -- the claimnotes driver over its recorded refusals (R10-996-RUNNER-CLAIMS, P196/P209).

Runs ``merge_claim_file`` from ``tests/env_drift.py`` AT A GIVEN REF over each
merge's three texts of ``tests/golden/claimed_drift.txt`` (merge base of the
two sides, the branch, main) and prints one row per merge: scenarios each side
changed against the base, their overlap, and the driver's verdict. For the
three merges main resolved by hand it also compares the driver's claim map
with the one the merge commit recorded.

    python3 dev/audit/harnesses/claim_merge_census.py [driver-ref]

``driver-ref`` defaults to the working tree's ``tests/env_drift.py``; pass a
commit (the merge base) for the baseline driver. Needs the full history
(``git fetch --unshallow``). The case list is P196's (``dev/programme/
triage/s6-batch34.md``), plus #2876's P209 shape where its commits resolve.

A row reads ``resolved`` or ``refused``; ``hand=`` is ``same`` when the
driver's claim map equals the hand resolution's, ``differs`` when not, ``-``
for a PR merge never committed. RESULT lines count the rows.
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

CLAIM = "tests/golden/claimed_drift.txt"
# (label, branch side, main side, hand-resolved merge commit or None)
CASES = (
    ("#2841", "11e8075d", "f6784210c", None),
    ("#2745a", "8d0572dc", "28800999", None),
    ("#2745b", "cc679118", "2563e2922", None),
    ("#2834", "c38903518", "2563e2922", None),
    ("3a07c2eaa", "3a07c2eaa^1", "3a07c2eaa^2", "3a07c2eaa"),
    ("e438816e3", "e438816e3^1", "e438816e3^2", "e438816e3"),
    ("5bf232eac", "5bf232eac^1", "5bf232eac^2", "5bf232eac"),
)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def load_driver(ref: str | None):
    path = ROOT / "tests/env_drift.py"
    if ref is not None:
        tmp = Path(tempfile.mkdtemp()) / "env_drift_at_ref.py"
        tmp.write_text(git("show", f"{ref}:tests/env_drift.py"))
        path = tmp
    spec = importlib.util.spec_from_file_location("env_drift_census", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # dataclass resolves its module by name
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else None
    drv = load_driver(ref)
    resolved = refused = hand_same = hand_diff = 0
    for label, ours_ref, theirs_ref, hand in CASES:
        base_ref = git("merge-base", ours_ref, theirs_ref).strip()
        base, ours, theirs = (git("show", f"{r}:{CLAIM}")
                              for r in (base_ref, ours_ref, theirs_ref))
        b, o, t = (drv.parse_claim_map(x) for x in (base, ours, theirs))
        o_changed = {n for n in set(b) | set(o) if b.get(n) != o.get(n)}
        t_changed = {n for n in set(b) | set(t) if b.get(n) != t.get(n)}
        overlap = {n for n in o_changed & t_changed if o.get(n) != t.get(n)}
        merged = drv.merge_claim_file(base, ours, theirs)
        verdict = "refused" if merged is None else "resolved"
        resolved += merged is not None
        refused += merged is None
        cmp = "-"
        if hand is not None and merged is not None:
            same = drv.parse_claim_map(merged) == drv.parse_claim_map(
                git("show", f"{hand}:{CLAIM}"))
            cmp = "same" if same else "differs"
            hand_same += same
            hand_diff += not same
        print(f"{label:10} ours={len(o_changed):3} theirs={len(t_changed):3} "
              f"overlap={len(overlap):3} {verdict:8} hand={cmp}")
    print(f"RESULT resolved={resolved}")
    print(f"RESULT refused={refused}")
    print(f"RESULT hand_same={hand_same}")
    print(f"RESULT hand_differs={hand_diff}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
