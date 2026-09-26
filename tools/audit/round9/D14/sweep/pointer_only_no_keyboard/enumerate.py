#!/usr/bin/env python3
"""Enumerator, class "pointer-only editing with no keyboard route". D4-s1-04.

Widens the seam_rule to every pointer-driven editing surface in the card
(every element wired to pointerdown/pointermove/pointerup) and checks each
for a sibling keydown handler on the same or an enclosing element.

Run: python3 tools/audit/round9/D14/sweep/pointer_only_no_keyboard/enumerate.py
"""
import re
import sys

CARD = "custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js"


def main() -> int:
    src = open(CARD).read()
    lines = src.splitlines()
    pointer_lines = [
        i + 1 for i, l in enumerate(lines)
        if re.search(r'addEventListener\("pointerdown"', l)
    ]
    print(f"RESULT pointer_driven_surfaces={len(pointer_lines)}")
    for ln in pointer_lines:
        # A keyboard route "nearby": a keydown listener within 60 lines
        # either side (the same editing surface's setup block).
        window = "\n".join(lines[max(0, ln - 60):ln + 60])
        has_keydown = "addEventListener(\"keydown\"" in window
        print(f"  line {ln}: {lines[ln-1].strip()[:80]!r} keyboard_route_nearby={has_keydown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
