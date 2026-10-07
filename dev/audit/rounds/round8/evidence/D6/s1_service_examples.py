#!/usr/bin/env python3
"""
Metric: number of services.yaml `example:` values, fed together as one
payload per service, that the real voluptuous schema in
heatpump_optimizer/services.py (SERVICE_SCHEMA_*) accepts vs. rejects.
Command: PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
  python3 tools/audit/round8/D6/s1_service_examples.py
Expected: RESULT lines; 0 rejected examples if services.yaml and the schemas
agree, run from the tree root.
Baseline SHA: cdf82daabcfe3777d98b31489f36df5555ec9d82
Instrumented symbol: heatpump_optimizer.services.SERVICE_SCHEMA_* (voluptuous
Schema objects), driven directly, not through FakeHass.
Perturbation: edit one field's `example:` in services.yaml to a value outside
its schema's bound (e.g. house_thermal_mass: example: -1, below the >= 0.01
floor) and rejected_count must increase by exactly one, naming that service.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
          "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(v, "1")

import sys
import yaml
import voluptuous as vol

sys.path.insert(0, "tests/hastub")
sys.path.insert(0, "custom_components")

from heatpump_optimizer import services as S

SCHEMAS = {
    "run_optimization": S.SERVICE_SCHEMA_RUN_OPTIMIZATION,
    "set_mode": S.SERVICE_SCHEMA_SET_MODE,
    "set_away": S.SERVICE_SCHEMA_SET_AWAY,
    "set_thermal_parameters": S.SERVICE_SCHEMA_SET_THERMAL_PARAMS,
    "simulate_plan": S.SERVICE_SCHEMA_SIMULATE_PLAN,
    "apply_schedule": S.SERVICE_SCHEMA_APPLY_SCHEDULE,
    "assign_entity": S.SERVICE_SCHEMA_ASSIGN_ENTITY,
    "apply_topology": S.SERVICE_SCHEMA_APPLY_TOPOLOGY,
    "apply_manual_plan": S.SERVICE_SCHEMA_APPLY_MANUAL_PLAN,
    "clear_manual_plan": S.SERVICE_SCHEMA_CLEAR_MANUAL_PLAN,
    "restore_learned_snapshot": S.SERVICE_SCHEMA_RESTORE_SNAPSHOT,
    "diagnose_interval": S.SERVICE_SCHEMA_DIAGNOSE_INTERVAL,
}

doc = yaml.safe_load(open("custom_components/heatpump_optimizer/services.yaml", encoding="utf-8"))

checked = 0
rejected = []
skipped_no_example = []


def extract_examples(fields):
    payload = {}
    for name, spec in (fields or {}).items():
        if isinstance(spec, dict) and "example" in spec:
            payload[name] = spec["example"]
    return payload


for svc, schema in SCHEMAS.items():
    entry = doc.get(svc, {})
    payload = extract_examples(entry.get("fields"))
    if not payload and (entry.get("fields") or {}):
        skipped_no_example.append(svc)
        continue
    checked += 1
    try:
        schema(payload)
    except vol.Invalid as exc:
        rejected.append((svc, payload, str(exc)))

print(f"RESULT services_checked={checked} services")
print(f"RESULT services_rejected={len(rejected)} services")
for svc, payload, err in rejected:
    print(f"  REJECTED {svc}: payload={payload} error={err}")
print(f"RESULT services_skipped_no_example={len(skipped_no_example)} services", skipped_no_example)

load1 = os.getloadavg()[0]
print(f"RESULT load1={load1} load")
print("RESULT thread_factor=1.0 ratio")
