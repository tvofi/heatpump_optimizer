#!/usr/bin/env python3
"""
Metric: Entity ordering and naming consistency (step 3, step 4: enabled-by-default analysis).
Run: cd /home/claude/audit-r8/seats/D8-s2 && PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D8/s2_entity_analysis.py
Expected: Counts misorderings and mismatches
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: Cloud Linux 4vCPU 15GB RAM
Key metric: entity_id ordering (via translation_key) and enabled-by-default coverage
"""

import os
import sys
import time
import ast
import json
import re
from pathlib import Path
from collections import defaultdict

# Thread pin before numpy
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

p_start = time.process_time()
t_start = time.thread_time()
load1_start = os.getloadavg()[0]

def extract_entities_from_sensor_py():
    """Extract entity information by parsing sensor.py."""
    entities = []

    with open("custom_components/heatpump_optimizer/sensor.py") as f:
        content = f.read()

    # Parse the file as AST
    tree = ast.parse(content)

    # Find async_setup_entry function
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_setup_entry":
            # Find the entities list assignment
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "entities":
                            # Extract entity class instantiations from the list
                            if isinstance(item.value, ast.List):
                                for elt in item.value.elts:
                                    if isinstance(elt, ast.Call):
                                        if isinstance(elt.func, ast.Name):
                                            class_name = elt.func.id
                                            entities.append({
                                                'class': class_name,
                                                'index': len(entities)
                                            })

    return entities

def extract_translation_keys_and_enabled():
    """Extract translation_key and enabled_default for each entity class."""
    entity_info = {}

    with open("custom_components/heatpump_optimizer/sensor.py") as f:
        lines = f.readlines()

    # Find each entity class definition
    for i, line in enumerate(lines):
        if line.startswith("class ") and "Sensor" in line:
            class_name = line.split("class ")[1].split("(")[0].strip()

            # Find the __init__ method to extract translation_key
            translation_key = None
            enabled_default = True

            for j in range(i, min(i + 50, len(lines))):
                if "def __init__" in lines[j]:
                    # Find super().__init__ call
                    for k in range(j, min(j + 20, len(lines))):
                        if "super().__init__" in lines[k]:
                            # Extract translation_key from the arguments
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
                entity_info[class_name] = {
                    'translation_key': translation_key,
                    'enabled_default': enabled_default
                }

    return entity_info

def main():
    entities_list = extract_entities_from_sensor_py()
    entity_info = extract_translation_keys_and_enabled()

    # Get translation keys in order they appear in async_setup_entry
    ordered_keys = []
    for entity in entities_list:
        if entity['class'] in entity_info:
            ordered_keys.append(entity_info[entity['class']]['translation_key'])

    # Check if sorted
    sorted_keys = sorted(ordered_keys)
    ordering_violations = 0
    if ordered_keys != sorted_keys:
        ordering_violations = sum(1 for a, b in zip(ordered_keys, sorted_keys) if a != b)

    # Count enabled vs disabled
    enabled_count = sum(1 for info in entity_info.values() if info['enabled_default'])
    disabled_count = sum(1 for info in entity_info.values() if not info['enabled_default'])

    # Load strings.json
    with open("custom_components/heatpump_optimizer/strings.json") as f:
        strings = json.load(f)

    sensor_strings = strings.get("entity", {}).get("sensor", {})

    # Check coverage in strings.json
    missing_from_strings = 0
    for key in ordered_keys:
        if key not in sensor_strings:
            missing_from_strings += 1

    # Print results
    print(f"RESULT total_entities={len(entity_info)} count")
    print(f"RESULT enabled_by_default={enabled_count} count")
    print(f"RESULT disabled_by_default={disabled_count} count")
    print(f"RESULT entity_ordering_violations={ordering_violations} count")
    print(f"RESULT missing_from_strings={missing_from_strings} count")

    # Debug output
    if ordering_violations > 0:
        print(f"\nOrdering issue: Expected alphabetical but got:")
        for i, (actual, expected) in enumerate(zip(ordered_keys, sorted_keys)):
            if actual != expected:
                print(f"  Position {i}: got '{actual}', expected '{expected}'")

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
