#!/bin/sh
# The seat interpreter: the venv tools/audit/seat/seat_venv.sh builds.
# Installed into a seat's bin directory by `seat_venv.sh --install-shims <dir>`.
# Exports HPO_TYPING_PYTHON to venv-ha only when that interpreter exists and
# the variable is unset -- never overriding a value the seat set (#1951).
STATE="${HPO_STATE_DIR:-$HOME/.local/state/hpo}"
HA="$STATE/venv-ha/bin/python"
if [ -z "${HPO_TYPING_PYTHON+x}" ] && [ -x "$HA" ]; then
  export HPO_TYPING_PYTHON="$HA"
fi
exec "$STATE/venv-ci/bin/python3" "$@"
