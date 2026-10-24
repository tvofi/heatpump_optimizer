#!/usr/bin/env bash
# Verifier-3 probe (D10-03): does the bare root alias actually swallow type
# errors that the coordinator alias catches? Consequence demonstration, not
# just a reveal_type echo.
# RUN: bash tools/audit/round4/D10/verify3/probe_alias_v3.sh   (from worktree root)
set -u
B=/private/tmp/hpo-d10-mypy13
ROOT=$(pwd)
TMP=$(mktemp -d /private/tmp/hpo-d10-v3probeXXXX)
mkdir -p "$TMP/probe"

# a deliberately wrong call on runtime_data in each alias scope
cat > "$TMP/probe/err_probe.py" <<'PY'
from custom_components.heatpump_optimizer import (
    HeatPumpOptimizerConfigEntry as RootEntry,
)
from custom_components.heatpump_optimizer.coordinator import (
    HeatPumpOptimizerConfigEntry as CoordEntry,
)

def bad_root(entry: RootEntry) -> None:
    entry.runtime_data.no_such_attribute_anywhere()

def bad_coord(entry: CoordEntry) -> None:
    entry.runtime_data.no_such_attribute_anywhere()
PY

(cd "$ROOT" && env -u MYPYPATH -u PYTHONPATH "$B/venv/bin/python" -m mypy --strict \
  --no-error-summary --no-incremental --cache-dir "$TMP/cache" --python-version 3.13 \
  "$TMP/probe/err_probe.py" > "$TMP/probe_out.txt" 2>&1)
echo "== errors on a bogus attribute via each alias =="
cat "$TMP/probe_out.txt"
root_errs=$(grep -c 'bad_root' "$TMP/probe_out.txt" || true)
coord_errs=$(grep -c 'bad_coord' "$TMP/probe_out.txt" || true)
echo "RESULT root_alias_errors_on_bogus_attr=$root_errs"
echo "RESULT coordinator_alias_errors_on_bogus_attr=$coord_errs"
rm -rf "$TMP"
