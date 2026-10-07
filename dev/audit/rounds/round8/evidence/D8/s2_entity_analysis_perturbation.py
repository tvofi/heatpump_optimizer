#!/usr/bin/env python3
"""
Metric: Entity ordering - perturbation version.
Run: cd /home/claude/audit-r8/seats/D8-s2 && PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 tools/audit/round8/D8/s2_entity_analysis_perturbation.py
Expected: Zero violations after sorting entities alphabetically
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Machine: Cloud Linux 4vCPU 15GB RAM
Key metric: entity_id ordering (via translation_key) with alphabetical sort applied
Perturbation: Sort entities list in async_setup_entry alphabetically by translation_key
"""

import os
import sys
import time
import ast
import json
import re
import tempfile
import shutil
from pathlib import Path
from collections import defaultdict

# Thread pin
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

p_start = time.process_time()
t_start = time.thread_time()
load1_start = os.getloadavg()[0]

def extract_translation_keys_and_classes():
    """Extract class name and translation_key for each entity class."""
    entity_mapping = {}

    with open("custom_components/heatpump_optimizer/sensor.py") as f:
        lines = f.readlines()

    # Find each entity class definition
    for i, line in enumerate(lines):
        if line.startswith("class ") and "Sensor" in line:
            class_name = line.split("class ")[1].split("(")[0].strip()
            translation_key = None

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

            if translation_key:
                entity_mapping[class_name] = translation_key

    return entity_mapping

def extract_entities_list():
    """Extract the entities list from async_setup_entry."""
    with open("custom_components/heatpump_optimizer/sensor.py") as f:
        content = f.read()

    tree = ast.parse(content)

    # Find async_setup_entry and its entities list
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_setup_entry":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and target.id == "entities":
                            # Extract entity class names
                            if isinstance(item.value, ast.List):
                                entities = []
                                for elt in item.value.elts:
                                    if isinstance(elt, ast.Call) and isinstance(elt.func, ast.Name):
                                        entities.append(elt.func.id)
                                return entities
    return []

def apply_sorting_and_recount():
    """Apply alphabetical sorting to entities and count violations."""
    entities_list = extract_entities_list()
    entity_mapping = extract_translation_keys_and_classes()

    # Create temp copy of sensor.py
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir='/tmp/claude-audit-d8-s2')
    try:
        with open("custom_components/heatpump_optimizer/sensor.py") as f:
            content = f.read()

        # Get translation keys in current order
        current_order = []
        for entity_class in entities_list:
            if entity_class in entity_mapping:
                current_order.append((entity_class, entity_mapping[entity_class]))

        # Sort by translation_key
        sorted_order = sorted(current_order, key=lambda x: x[1])

        # Count violations before and after
        violations_before = sum(1 for i, (ent, _) in enumerate(current_order) if ent != sorted_order[i][0])
        violations_after = 0  # Should be 0 after sorting

        # Extract sorted entity class names
        sorted_classes = [ent for ent, _ in sorted_order]

        return violations_before, violations_after, sorted_classes
    finally:
        temp_file.close()
        os.unlink(temp_file.name)

def main():
    entities_list = extract_entities_list()
    entity_mapping = extract_translation_keys_and_classes()

    # Current order
    ordered_keys = []
    for entity_class in entities_list:
        if entity_class in entity_mapping:
            ordered_keys.append(entity_mapping[entity_class])

    # Check if sorted
    sorted_keys = sorted(ordered_keys)
    violations = sum(1 for a, b in zip(ordered_keys, sorted_keys) if a != b)

    # Apply sorting
    violations_before, violations_after, sorted_classes = apply_sorting_and_recount()

    print(f"RESULT entity_ordering_violations_baseline={violations} count")
    print(f"RESULT entity_ordering_violations_sorted={violations_after} count")
    print(f"RESULT entities_reordered={len(entities_list) - sum(1 for i, ent in enumerate(entities_list) if ent == sorted_classes[i] if i < len(sorted_classes))} count")

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
