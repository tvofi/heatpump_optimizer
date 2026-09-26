#!/usr/bin/env bash
# D14 sweep, class "error-translating try opened after the call it should cover".
# Finding: D1-s2-55 (verified, medium -- _run_in_process calls _ensure_worker() (which can raise
# a bare OSError from subprocess.Popen) BEFORE the try: block that translates transport failures
# into ProcessWorkerUnavailable, so a Popen failure bypasses _await_optimize's fallback-to-
# in-process-solve path entirely and propagates as an unhandled exception).
# Enumerator: every risky call assigned right before a try: whose except clause exists
# specifically to translate that call's failures, checking whether the call sits inside or
# outside the try it should be covered by.
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
grep -n "_ensure_worker()\|raise ProcessWorkerUnavailable\|except ProcessWorkerUnavailable\|def _run_in_process\|def _await_process\|def _await_optimize" custom_components/heatpump_optimizer/coordinator.py
