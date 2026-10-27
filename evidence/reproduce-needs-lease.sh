#!/bin/sh
# re-create the two scope files and reproduce the needs_lease perturbation
set -e
cd "$(dirname "$0")"
printf "tests/entities.py tests/features.py\n" > scope-two-big.scope
printf "tests/stress.py\n" > scope-stress.scope
echo "needs-lease /nonexistent/scope.scope:"; python3 ../rev-2881-wt/tests/gate_lock.py needs-lease /nonexistent/scope.scope
echo "needs-lease empty arg:"; python3 ../rev-2881-wt/tests/gate_lock.py needs-lease ""
echo "needs-lease scope-two-big.scope:"; python3 ../rev-2881-wt/tests/gate_lock.py needs-lease "$PWD/scope-two-big.scope"
echo "needs-lease scope-stress.scope:"; python3 ../rev-2881-wt/tests/gate_lock.py needs-lease "$PWD/scope-stress.scope"
