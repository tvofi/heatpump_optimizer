"""R10-TARIFF census: the weekday cyclic range is spelled in two modules.

grid_fee._parse_cyclic_range owns the cyclic range for the grid-fee rules
(D7-s2-59). dhw_schedule._parse_day_selector parses a hot-water weekday
range with its own wrap, ``(lo + k) % 7 for k in range((hi - lo) % 7 + 1)``.
This drives both with every ordered pair of weekdays, each spelt in its own
module's tokens, and counts the pairs whose day sets differ.

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_weekday_range_twins.py [--perturb|--identity]

``--perturb`` drops the wrap's ``+ 1`` in a copy of dhw_schedule's parser
(a range one day short), which must read disagreements above 0.
``--identity`` drives grid_fee against itself, the null control: 0.
"""
from __future__ import annotations

import sys

from heatpump_optimizer import dhw_schedule, grid_fee

GRID = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
DHW = dhw_schedule._DAY_TOKENS


def _short_wrap(token: str) -> list[int]:
    lo, hi = (DHW.index(p) for p in token.split("-"))
    return sorted((lo + k) % 7 for k in range((hi - lo) % 7))


def main() -> None:
    if "--identity" in sys.argv:
        other = lambda a, b: sorted(grid_fee.parse_day_range(f"{GRID[a]}-{GRID[b]}"))  # noqa: E731
    elif "--perturb" in sys.argv:
        other = lambda a, b: _short_wrap(f"{DHW[a]}-{DHW[b]}")  # noqa: E731
    else:
        other = lambda a, b: dhw_schedule._parse_day_selector(f"{DHW[a]}-{DHW[b]}")  # noqa: E731
    pairs = [(a, b) for a in range(7) for b in range(7)]
    bad = [
        (a, b) for a, b in pairs
        if sorted(grid_fee.parse_day_range(f"{GRID[a]}-{GRID[b]}")) != other(a, b)
    ]
    print(f"RESULT pairs={len(pairs)} disagreements={len(bad)} first={bad[:3]}")


if __name__ == "__main__":
    main()
