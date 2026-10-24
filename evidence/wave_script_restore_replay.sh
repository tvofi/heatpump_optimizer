set -e; RUNNER_TEMP=$(mktemp -d)
git diff --name-only -z "$(git hash-object -t tree /dev/null)" "$PINNED" -- \
  '.claude/workflows/*.mjs' \
  '.claude/workflows/*.py' \
  '.claude/workflows/vendor' \
  'tools/audit/*.sh' \
  'tools/audit/record-predicate' \
  'tools/audit/round6/D11/fix/codeowners_gap.py' \
  'tests/coverage_ratchet.py' \
  'tests/delivery_status.py' \
  'tests/entities.py' \
  'tests/gate_lock.py' \
  'tests/issue996_count.py' \
  'tests/nightly_ha.py' \
  'tests/replay.py' \
  'tests/structure.py' \
  'tests/throwaway_git.py' \
  'tools/audit/round4/D11/d11lib.py' \
  'tools/audit/round4/D11/governance_cost.py' \
  'tools/audit/seat/gh_read.py' \
  'tools/audit/seat/merge_train.py' \
  'tools/audit/seat/queue_pre_flight.py' \
  'tools/audit/seat/ref_privacy.py' \
  'tools/audit/seat/tmp_paths.py' \
  'tools/policy/*.mjs' \
  'tools/policy/*.py' \
  'tools/pr/*.py' \
  'tools/policy/vendor' \
  'tools/pr/*.sh' \
  'tools/seat/*.sh' \
  'tools/coverage/*.sh' \
  'tools/release/stamp.py' \
  'dev/audit/*.sh' \
  'tools/policy/record-predicate' \
  'dev/audit/rounds/round6/D11/fix/codeowners_gap.py' \
  'tests/layout.py' \
  'dev/audit/rounds/round4/D11/d11lib.py' \
  'dev/audit/rounds/round4/D11/governance_cost.py' > "$RUNNER_TEMP/pinned.list"
test -s "$RUNNER_TEMP/pinned.list"
git checkout "$PINNED" --pathspec-from-file="$RUNNER_TEMP/pinned.list" --pathspec-file-nul
