#!/usr/bin/env python3
"""Enumerator, class "selector minimum off its own step grid". D4-s2-05.

Every rendered NumberSelector in config_flow.py: does (min - default) fall
on an integer multiple of step? If not, native HTML validity accepts values
off the grid the spinner itself uses (one click lands on min+step, not on
a value that reconciles with min).

Run: python3 tools/audit/round9/D14/sweep/selector_min_off_step_grid/enumerate.py
"""
import re
import sys

CONFIG_FLOW = "custom_components/heatpump_optimizer/config_flow.py"


def main() -> int:
    src = open(CONFIG_FLOW).read()
    seams = []
    for m in re.finditer(
        r"NumberSelectorConfig\(([^)]*)\)", src, re.S
    ):
        body = m.group(1)
        def num(key):
            mm = re.search(rf"{key}\s*=\s*(-?[\d.]+)", body)
            return float(mm.group(1)) if mm else None
        mn, step = num("min"), num("step")
        if mn is None or step is None or step == 0:
            continue
        off_grid = abs((mn / step) - round(mn / step)) > 1e-9
        seams.append((m.start(), mn, step, off_grid))
    print(f"RESULT number_selectors_with_min_and_step={len(seams)}")
    off = [s for s in seams if s[3]]
    print(f"RESULT off_grid={len(off)}")
    for pos, mn, step, off_grid in seams:
        line = src.count("\n", 0, pos) + 1
        print(f"  line {line}: min={mn} step={step} off_grid={off_grid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
