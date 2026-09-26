#!/usr/bin/env python3
"""Enumerator, class "persisted future instant trusted without bound".

Round 9, D14 sweep (thread S7). Widens the two findings' seam_rules
(D1-s1-04: fromisoformat in {drift,snapshots,curve_learning,comfort_learning}.py;
D1-s3-05: boost.py's `until`) to every restored instant in the package that
gates a staleness/expiry decision against `now` with no upper (or lower)
bound clamp on the stored value itself.

Run: python3 tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/enumerate.py
"""
import re
import subprocess
import sys

PKG = "custom_components/heatpump_optimizer"

# Every `datetime.fromisoformat(...)` call in the package (the raw
# candidate set: any of these COULD be an unbounded persisted instant).
CANDIDATES = subprocess.run(
    ["grep", "-rn", "fromisoformat", PKG],
    capture_output=True, text=True, check=True,
).stdout.strip().splitlines()

# Sites the two round-9 findings already name.
KNOWN_INSTANCE = {
    f"{PKG}/drift.py:148",
    f"{PKG}/snapshots.py:74",
    f"{PKG}/curve_learning.py:111",
    f"{PKG}/comfort_learning.py:256",
    f"{PKG}/boost.py:166",
}

# A restored instant is IN this class when the code that follows compares
# it to `now` to gate a staleness window, an expiry, or a "don't redo this
# for N days" cooldown, with no check that the stored value itself sits in
# a sane range (not more than a bounded amount ahead of or behind `now`).
# It is OUT of the class (not applicable) when the parsed value is used for
# a one-shot lookup keyed by clock time (a price slot, a learned-day key)
# rather than a persisted gate that widens under clock skew, or when it is
# immediately validated against `now` before being trusted (manual_plan's
# service-input path, disposed separately as its own class).

def site(line: str) -> str:
    path, rest = line.split(":", 1)
    lineno = rest.split(":", 1)[0]
    return f"{path}:{lineno}"


def main() -> int:
    seams = []
    for line in CANDIDATES:
        s = site(line)
        seams.append(s)
    print(f"RESULT candidate_fromisoformat_sites={len(seams)}")
    for s in sorted(set(seams)):
        tag = "KNOWN" if s in KNOWN_INSTANCE else "widen"
        print(f"  {tag} {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
