#!/bin/bash
# exit 1 iff a named location/redaction check FAILs or the script prints no summary
s=$1; out=$(PYTHONPATH=tests/hastub timeout 900 python3 tests/$s.py 2>&1); rc=$?
echo "$out" | grep -E '^\s*FAIL' | head -5 >&2
if echo "$out" | grep -E 'FAIL' | grep -qE 'the location is redacted|a coordinate (nested|that is not)|the download.s replay half|Download diagnostics fills|DBG-1 Download diagnostics|the value pass searches|never leaves the instance|R10-DIAG|redacted wherever'; then exit 1; fi
echo "$out" | grep -qE 'CHECKS PASSED|checks? (passed|failed)|FAILED|PASSED' || exit 1
exit 0
