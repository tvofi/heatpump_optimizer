"""D0-s2 enumerator (round 11): the universe of D0.M4/M5/M6 in this seat's cells, one item per line.

= every line of `tools/audit/enumerate.py d0-grid` whose price axis is one of the seat's four
(winter_typical, winter_extreme, winter_narrow, winter_moderate), then D0.md step 4's "coordinator
captures": each tests/golden.py:coordinator_scenarios() config at each of the four prices, weather
winter_cold, 24 h, as `coord/<scenario>/<price>/winter_cold`.
Command: python3 dev/audit/rounds/round11/D0/s2/enum_cells.py      (prints 1200 + 20 = 1220 at 92d38ecb)
Not a measuring harness: it prints names, no RESULT lines.
"""
import os
import subprocess
import sys

PRICES = ("winter_typical", "winter_extreme", "winter_narrow", "winter_moderate")
COORD = ("coord_minimal", "coord_dhw", "coord_two_zone", "coord_grid_fee", "coord_all_features")


def main():
    grid = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d0-grid"], capture_output=True,
                          text=True, check=True).stdout.split()
    for line in grid:
        if line.split("/")[0] in PRICES:
            print(line)
    for name in COORD:
        for p in PRICES:
            print(f"coord/{name}/{p}/winter_cold")


if __name__ == "__main__":
    main()
