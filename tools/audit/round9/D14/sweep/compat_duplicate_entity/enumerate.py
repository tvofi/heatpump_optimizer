#!/usr/bin/env python3
"""Enumerator, class "compatibility duplicate entity enabled by default".

Widens D8-s3-03's seam_rule to every sensor class in sensor.py whose
docstring/comment says it duplicates another entity's value, then checks
whether it ships with `_attr_entity_registry_enabled_default = False`.

Run: python3 tools/audit/round9/D14/sweep/compat_duplicate_entity/enumerate.py
"""
import re
import sys

PKG = "custom_components/heatpump_optimizer"


def main() -> int:
    src = open(f"{PKG}/sensor.py").read()
    # Widen: any class whose docstring says it republishes another
    # entity's value verbatim (duplicate/"the same number"/"the same
    # value" language), independent of the specific wording D8-s3-03 used.
    hits = []
    for m in re.finditer(r"class (\w+Sensor)\(([^)]*)\):\n(?:    \"\"\"(.*?)\"\"\")?", src, re.S):
        cls, bases, doc = m.groups()
        doc = doc or ""
        if re.search(r"is the .*(temperature|indoor|value)|duplicat|byte.duplicate|same number", doc, re.I):
            hits.append((cls, bool(doc)))
    print(f"RESULT candidate_duplicate_classes={len(hits)}")
    for cls, _ in hits:
        m = re.search(rf"class {cls}\(.*?\n(.*?)(?=\nclass |\Z)", src, re.S)
        body = m.group(1) if m else ""
        enabled_default_false = "_attr_entity_registry_enabled_default = False" in body
        print(f"  {cls} enabled_by_default={not enabled_default_false}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
