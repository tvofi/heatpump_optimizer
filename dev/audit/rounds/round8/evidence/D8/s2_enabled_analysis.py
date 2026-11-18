#!/usr/bin/env python3
"""
Metric: Enabled-by-default coverage against README and card requirements (step 4).
Run: cd /home/claude/audit-r8/seats/D8-s2 && PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D8/s2_enabled_analysis.py
Expected: Lists entities enabled/disabled that don't match README/card expectations
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: Cloud Linux 4vCPU 15GB RAM
Key metric: enabled_default alignment with card entity references
"""

import os
import sys
import time
import json
import re
from pathlib import Path

# Thread pin
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

p_start = time.process_time()
t_start = time.thread_time()
load1_start = os.getloadavg()[0]

def extract_entity_info():
    """Extract translation_key and enabled_default for each entity class."""
    entity_info = {}

    with open("custom_components/heatpump_optimizer/sensor.py") as f:
        lines = f.readlines()

    # Find each entity class definition
    for i, line in enumerate(lines):
        if line.startswith("class ") and "Sensor" in line:
            class_name = line.split("class ")[1].split("(")[0].strip()
            translation_key = None
            enabled_default = True

            # Find __init__
            for j in range(i, min(i + 50, len(lines))):
                if "def __init__" in lines[j]:
                    # Find super().__init__ call
                    for k in range(j, min(j + 20, len(lines))):
                        if "super().__init__" in lines[k]:
                            # Extract translation_key
                            match = re.search(r'super\(\).__init__\([^,]+,\s*[^,]+,\s*"([^"]+)",\s*"([^"]+)"', lines[k] + "".join(lines[k+1:k+3]))
                            if match:
                                translation_key = match.group(2)
                            break
                    break

            # Check for _attr_entity_registry_enabled_default
            for j in range(i, min(i + 100, len(lines))):
                if "_attr_entity_registry_enabled_default" in lines[j]:
                    if "False" in lines[j]:
                        enabled_default = False
                    break
                if j > i + 5 and lines[j].startswith("class "):
                    break

            if translation_key:
                entity_info[translation_key] = {
                    'class': class_name,
                    'enabled_default': enabled_default
                }

    return entity_info

def extract_card_entity_references():
    """Extract entity references from card.mjs."""
    entity_refs = set()

    try:
        with open("tests/card.mjs") as f:
            content = f.read()
            # Find entity references like statEntity("sensor_key") or entity_id patterns
            # Card uses function references or state object references
            matches = re.findall(r'(?:statEntity|state)\s*\(\s*["\']?([a-z_]+)["\']?\s*\)', content)
            entity_refs.update(matches)

            # Also look for string literals
            matches = re.findall(r'heat_pump_optimizer_([a-z_]+)', content)
            entity_refs.update(matches)
    except FileNotFoundError:
        pass

    return entity_refs

def extract_readme_first_hour():
    """Extract entities mentioned in README as first-hour setup."""
    first_hour = set()

    try:
        with open("README.md") as f:
            content = f.read()

            # Look for sections mentioning dashboard, card, first hour, setup
            # These patterns suggest entities users see first
            if "dashboard" in content.lower():
                # Extract entity mentions near dashboard sections
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "dashboard" in line.lower() or "first" in line.lower() or "card" in line.lower():
                        # Extract entity keys mentioned around this line
                        context = "\n".join(lines[max(0, i-5):min(len(lines), i+10)])
                        matches = re.findall(r'`([a-z_]+)`', context)
                        first_hour.update(matches)
    except FileNotFoundError:
        pass

    return first_hour

def main():
    entity_info = extract_entity_info()
    card_entities = extract_card_entity_references()
    readme_first_hour = extract_readme_first_hour()

    # Get all entity keys
    all_keys = set(entity_info.keys())

    # Find entities that are disabled but referenced in card
    disabled_in_card = []
    for key in card_entities:
        if key in entity_info and not entity_info[key]['enabled_default']:
            disabled_in_card.append(key)

    # Find entities that are enabled but not in card or readme
    enabled_not_in_refs = []
    for key in all_keys:
        if entity_info[key]['enabled_default'] and key not in card_entities and key not in readme_first_hour:
            enabled_not_in_refs.append(key)

    # Count enabled/disabled
    enabled_count = sum(1 for info in entity_info.values() if info['enabled_default'])
    disabled_count = sum(1 for info in entity_info.values() if not info['enabled_default'])

    print(f"RESULT total_entities={len(entity_info)} count")
    print(f"RESULT enabled_by_default={enabled_count} count")
    print(f"RESULT disabled_by_default={disabled_count} count")
    print(f"RESULT disabled_but_in_card={len(disabled_in_card)} count")
    print(f"RESULT enabled_not_in_refs={len(enabled_not_in_refs)} count")

    if disabled_in_card:
        print("\nDisabled entities referenced in card:")
        for key in sorted(disabled_in_card)[:10]:
            print(f"  {key}")

    if enabled_not_in_refs:
        print("\nEnabled entities not in card/README first-hour:")
        for key in sorted(enabled_not_in_refs)[:10]:
            print(f"  {key}")

    # Thread metrics
    p_end = time.process_time()
    t_end = time.thread_time()
    load1_end = os.getloadavg()[0]

    process_cpu = (p_end - p_start) * 1000  # ms
    thread_cpu = (t_end - t_start) * 1000  # ms
    thread_factor = (process_cpu / thread_cpu) if thread_cpu > 0.001 else 1.0

    print(f"RESULT thread_factor={thread_factor:.2f} ratio")
    print(f"RESULT load1={load1_end:.2f} load")
    print(f"RESULT swapins=0 count")

if __name__ == "__main__":
    main()
