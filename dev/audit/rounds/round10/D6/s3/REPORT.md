# D6-s3 report (round 10, baseline 17f1c55fad1b)

Cells: M1+M2+M3 over manifest.json, services.yaml, strings.json, translations/en.json, translations/sv.json, hacs.json.

## Method
`svc_claims.py` captures the 13 schemas `services:async_register_services` registers, then checks every
services.yaml service/field/required flag/example/select option/number min-max against them, every catalogue
`services.<svc>.fields` entry against the yaml, key parity strings.json vs en/sv (every leaf), and manifest
version/domain/name/requirements against VERSION, const.DOMAIN, hacs.json and importability.
Links: `curl -sI` on manifest documentation and issue_tracker URLs -> 200, 200.

## Results
claims_checked=3741, claims_false=0, stale=0. Unverifiable: hacs.json `homeassistant: 2025.2.0` (no in-tree
minimum to check against; the hastub is not a versioned HA) and manifest `quality_scale: platinum` (D10's domain).
Perturbation control: narrowing SERVICE_SCHEMA_SET_MODE to In(['auto','comfort']) moves claims_false 0 -> 3.

## Findings
None.

## Exposure
None (no docs/ read).
