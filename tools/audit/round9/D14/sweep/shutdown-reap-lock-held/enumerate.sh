#!/usr/bin/env bash
# D14 sweep, class "shutdown reap waits on the lock a solve holds".
# Finding: D1-s2-05 (verified, medium -- _run_in_process holds _PROCESS_LOCK for the entire
# pickle dump/load exchange with the solve worker (a potentially long-running solve);
# _shutdown_process_pool acquires the same lock first, before checking whether the worker needs
# reaping, so HA's shutdown handler blocks behind an in-flight solve instead of reaping promptly).
set -euo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../../../.." && pwd)"
grep -n "_PROCESS_LOCK\|threading\.Lock()\|threading\.RLock()" custom_components/heatpump_optimizer/*.py
