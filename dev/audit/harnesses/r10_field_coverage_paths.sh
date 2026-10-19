#!/bin/bash
# R10-SEAT-SELFTESTS-CI fold (a finding from R10-ARCHSCORE-COVERAGE's census
# work): does a pull request touching a census input select governance.yml's
# field-coverage step? Reads the step's own pathspec from the workflow at the
# ref given (default HEAD) and runs the step's own predicate,
# `git diff --quiet "$SINCE" HEAD -- <pathspec>`, in a throwaway repository
# over one-file commits. rc 1 from the predicate means "an input changed: run".
#   bash dev/audit/harnesses/r10_field_coverage_paths.sh [<ref>]
# Prints one line per probe file, `RUN` or `SKIPPED`, and exits 1 unless every
# census input reads RUN and the unrelated file (the null control) SKIPPED.
set -uo pipefail
cd "$(git -C "$(dirname -- "$0")" rev-parse --show-toplevel)" || exit 1
REF=${1:-HEAD}
line=$(git show "$REF:.github/workflows/governance.yml" | grep -E 'git diff --quiet "\$SINCE" HEAD -- ') \
  || { echo "no field-coverage predicate in governance.yml at $REF"; exit 2; }
spec=${line#*HEAD -- }; spec=${spec%%; then*}
eval "set -- $spec"   # the workflow's own quoting, as bash reads it there
SPEC=("$@")
. tests/throwaway_git.sh
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
throwaway_git_init "$T/r" -q -b main
throwaway_git_env
g() { git -C "$T/r" "$@"; }
echo seed > "$T/r/seed"; g add seed; g commit -qm seed; BASE=$(g rev-parse HEAD)
bad=0
probe() { # <path> <want RUN|SKIPPED>: one commit on BASE touching <path> alone
  g checkout -q "$BASE"; mkdir -p "$T/r/$(dirname -- "$1")"; echo x > "$T/r/$1"
  g add -A; g commit -qm probe
  if (cd "$T/r" && git diff --quiet "$BASE" HEAD -- "${SPEC[@]}"); then got=SKIPPED; else got=RUN; fi
  [ "$got" = "$2" ] || bad=$((bad + 1))
  echo "$got $1 (want $2)"
}
probe tests/ci_budgets.json RUN
probe tests/ci_ratchet.py RUN
probe tools/audit/archscore/score.py RUN
probe custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js RUN
probe tests/structure_budgets.json RUN
probe README.md SKIPPED
echo "RESULT misread=$bad"
[ "$bad" = 0 ]
