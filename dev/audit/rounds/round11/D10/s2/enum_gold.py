"""Enumerator for D10-s2's steps D10.M1 and D10.M2: the gold rows of
custom_components/heatpump_optimizer/quality_scale.yaml (the rows under its
'# Gold' comment, up to '# Platinum'), one rule per line. With --checklist it
prints instead the gold rules of Home Assistant's checklist as fetched on
2026-11-16 into rules/tiers.json beside this file (developers.home-assistant
docs/core/integration-quality-scale/_includes/tiers.json), so the two lists
can be diffed (D10-criteria Q1).
Command: python3 dev/audit/rounds/round11/D10/s2/enum_gold.py [--checklist]
"""
import json
import re
import sys
from pathlib import Path

if "--checklist" in sys.argv:
    tiers = json.loads((Path(__file__).parent / "rules" / "tiers.json").read_text())
    for rule in tiers["gold"]:
        print(rule if isinstance(rule, str) else rule["id"])
else:
    text = Path("custom_components/heatpump_optimizer/quality_scale.yaml").read_text()
    gold = text.split("# Gold", 1)[1].split("# Platinum", 1)[0]
    for name in re.findall(r"^  ([a-z][a-z-]*):", gold, re.M):
        print(name)
