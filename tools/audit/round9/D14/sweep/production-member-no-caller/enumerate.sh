#!/usr/bin/env bash
# D14 sweep, class "production member reached by no production code".
# Findings: D7-s3-01 (verified, low -- AST-reachability dead class members; DefrostDerate.samples
# is kept alive in every name-based static view by a field-name collision with
# AccuracyTracker.samples, and only the dynamic sentinel shows it dead), D7-s3-72 (verified, low --
# ThermalModel._step_* scratch attributes written every step but never read by a consumer).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
echo "--- family A: static AST reachability (existing D7-s3 harness) ---"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D7/s3/reach.py --list
echo "--- family A, dynamic confirmation (catches the samples/samples name collision) ---"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D7/s3/sentinel.py 2>&1 | grep '^SENTINEL dead'
echo "--- family B: write-only ThermalModel._step_* scratch attributes ---"
PYTHONPATH=tests/hastub python3 tools/audit/round9/D7/leads/l3_write_only_scratch.py 2>&1 | grep -E '^member|^RESULT write_only_members'
