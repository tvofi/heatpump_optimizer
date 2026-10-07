Fix review: merge bb3634f62bbf0ae86967df3eb44f330d551156b1

Round 3. Seat r9c-rev-2012, fresh detached worktree at bb3634f62bbf0ae86967df3eb44f330d551156b1. Delta judged: 7cef1c32..bb3634f62bbf0ae86967df3eb44f330d551156b1 (d1e37730, 8fe1ca12, f607a349 + the orchestrator's no-ff merge). origin/main has moved to 59b5ac6e (not contained); git merge-tree --write-tree origin/main bb3634f62bbf0ae86967df3eb44f330d551156b1 exits 0. Live head at posting: bb3634f62bbf0ae86967df3eb44f330d551156b1.

RESULT self-tests at head: moved_paths 9/0, open_pr 1/0, handoff_push 1/0, tmp_paths 42/0, merge_train 49/0, handover_prompt 13/0, bus 45/0, state_docs and record_row all passed (selftests.txt)
RESULT tmp_paths --check (python3 -I): 0 refused, 0 stale allow entries, with dev/governance/decisions/ now in scope
RESULT the carries' command `python3 tools/audit/seat/moved_paths.py tools/audit/seat/*`: rc 0, 26 hits in 25 files, 14 FALLBACK + 12 STALE? -- matches the body; each STALE? checked against its disposition (lifted .claude/rules/ whose copy exists; merge_train:160 and roster_edit BRIEF_LINT_OLD split fallbacks; tmp_paths docs/decisions old-home scope + its self-test; tmp_paths:19 exclusion of the now-absent tools/audit/handoff/, inert because dev/archive/ is outside the scan scope) (carry_cmd.txt)
RESULT plant open_pr.sh ROW_DIR=docs/delivery: 1 checks, 1 failed (plant_openpr.txt)
RESULT plant handoff_push.sh ROW_DIR=docs/delivery: 1 checks, 1 failed (plant_handoff.txt)
RESULT plant moved_paths expand() without the directory walk: self-test rc 1, IsADirectoryError on the directory arm (plant_walk_full.txt)
RESULT plant moved_paths walk ignoring the tracked set: 9 checks, 2 failed (plant_tracked.txt)
RESULT plant moved_paths without the all-tracked-dir planned-move clause: 9 checks, 1 failed (plant_planned.txt)
RESULT plant tmp_paths scope back to docs/decisions only: 42 checks, 1 failed, the lifted-home case (plant_tmp.txt)
RESULT comment/fixture re-points in INSTRUMENTS.md, record_row.py, roster_lib.py, state_docs.py: text only plus state_docs self-test fixtures; state_docs self-test passes.
RESULT check-runs at head when posted: 14 success, 10 skipped, 1 neutral, 6 in_progress (CodeQL, browser, closures, coverage, env-matrix, fast 3.14), budget-raise-gate cancelled; red delivery-status and nightly-status are main's, answered in the body. The gate lanes were still running: this verdict does not certify them, and the merge train's CI step owes their green.
RESULT not re-measured by me: prepr --self-test 186/7 (orchestrator reports it reproduces on clean main); tests/entities.py (no homeassistant module locally; the body cites ALL 2191 PASSED, and CI fast lane owes it).

bus-nonce: 66ab5005b1e0a717f98806df77c6c659
