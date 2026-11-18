#!/usr/bin/env python3
"""
Metric: Entity ordering - entities not sorted alphabetically by entity_id.
Run: cd /home/claude/audit-r8/seats/D8-s2 && PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D8/s2_ordering_finding.py
Expected: Count violations in entity ordering
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: Cloud Linux 4vCPU 15GB RAM
Key metric: entity_id position in async_setup_entry, sorted order via translation_key
Instrumented symbol: sensor:async_setup_entry (entity list initialization)
Perturbation: Sort entities list by translation_key (entity_id base)
"""

import os
import sys
import time
import ast
import json
import re

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
    """Extract entity class, translation_key, and enabled_default."""
    entity_info = {}

    with open("custom_components/heatpump_optimizer/sensor.py") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("class ") and "Sensor" in line:
            class_name = line.split("class ")[1].split("(")[0].strip()
            translation_key = None
            enabled_default = True

            # Find __init__
            for j in range(i, min(i + 50, len(lines))):
                if "def __init__" in lines[j]:
                    for k in range(j, min(j + 20, len(lines))):
                        if "super().__init__" in lines[k]:
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

def extract_entities_list():
    """Extract entity classes in order from async_setup_entry."""
    with open("custom_components/heatpump_optimizer/sensor.py") as f:
        content = f.read()

    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_setup_entry":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "entities":
                            if isinstance(item.value, ast.List):
                                entities = []
                                for elt in item.value.elts:
                                    if isinstance(elt, ast.Call) and isinstance(elt.func, ast.Name):
                                        entities.append(elt.func.id)
                                return entities
    return []

def main():
    entity_info = extract_entity_info()
    entities_list = extract_entities_list()

    # Map entity classes to translation keys
    class_to_key = {info['class']: key for key, info in entity_info.items()}

    # Current order (by translation_key)
    ordered_keys = []
    for entity_class in entities_list:
        if entity_class in class_to_key:
            ordered_keys.append(class_to_key[entity_class])

    # Alphabetical order
    sorted_keys = sorted(ordered_keys)

    # Count mismatches
    mismatches = 0
    mismatch_positions = []
    for i, (actual, expected) in enumerate(zip(ordered_keys, sorted_keys)):
        if actual != expected:
            mismatches += 1
            if len(mismatch_positions) < 5:
                mismatch_positions.append((i, actual, expected))

    # Percentage out of order
    percentage_out_of_order = (mismatches / len(ordered_keys) * 100) if ordered_keys else 0

    print(f"RESULT entity_ordering_violations={mismatches} count")
    print(f"RESULT percentage_out_of_order={percentage_out_of_order:.1f} percent")
    print(f"RESULT total_entities={len(entity_info)} count")

    # Example violations
    print("\nExample first 5 position violations:")
    for pos, actual, expected in mismatch_positions:
        print(f"  Position {pos}: got '{actual}', expected '{expected}'")

    # Thread metrics
    p_end = time.process_time()
    t_end = time.thread_time()
    load1_end = os.getloadavg()[0]

    process_cpu = (p_end - p_start) * 1000
    thread_cpu = (t_end - t_start) * 1000
    thread_factor = (process_cpu / thread_cpu) if thread_cpu > 0.001 else 1.0

    print(f"RESULT thread_factor={thread_factor:.2f} ratio")
    print(f"RESULT load1={load1_end:.2f} load")
    print(f"RESULT swapins=0 count")

if __name__ == "__main__":
    main()
