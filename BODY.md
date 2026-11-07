Beat-only dispatch (P404) and one window for rules 4 and 5 (P403), from triage batch 132 (dev/programme/triage/s6-batch132.md). The record flush dispatched nightly.yml with no input, so every nightly lane ran to reach the one-minute record-autofix job. Rule 5 read tag..origin/main while rule 4 read tag..HEAD, so a merge past HEAD after a flush timeout refused rows (v7.1.5 run 1, #3271).

Changes: nightly.yml gains `workflow_dispatch.inputs.lanes` (choice all|beat, default all); mutation-nightly, mutation-ledger, mutation-ledger-push, slow and nightly-ha append `&& inputs.lanes != 'beat'`; record-autofix's `if` is unchanged. stamp.py `RECORD_BEAT_PAYLOAD` posts `lanes=beat`; the hand form is `gh workflow run nightly.yml -f lanes=beat`. `tests/delivery_status.py --head REV` (default origin/main) ends its window; `disposition_gate` passes the stamp head. tests/entities.py gets `inputs.lanes` in its `_gh_eval` contexts, a pin that every heavy job skips on lanes=beat and record-autofix does not, and the `--head` window checks. Alternative considered: a separate workflow file for the beat; rejected because REQUIRED_LANES and the record-writer environment are keyed to nightly.yml.

Closes: none.

## Head

45510e0e1693b0e903275db93f777eaf28d133f5

## Mutation proof

- Dropping `--head` from `disposition_gate_argv`: stamp self-test FAIL "rows gate: the stamp's head is passed to the instrument, one window with rule 4" and "rows gate: disposition_gate forwards its head to the command".
- Dropping lanes=beat from `RECORD_BEAT_PAYLOAD`: FAIL "record beat: the dispatch payload carries lanes=beat on main" and "record beat: dispatch_record_beat posts lanes=beat".
- Deleting every `&& inputs.lanes != 'beat'` from nightly.yml: tests/entities.py FAIL "lanes=beat skips every heavy nightly lane and runs record-autofix; no input runs every lane".
Each mutant was run against the committed tree and restored; `git status --short` clean afterwards.

## Null control

A dispatch with no input (hand probe, lanes empty) runs every lane in REQUIRED_LANES and record-autofix (entities check above, `_NS_HAND`); schedule and push still evaluate as before (the existing derivation check passes with `inputs.lanes` = all). `--head` at the tip (M2) returns the same merges as the default origin/main window, and the default equals head=origin/main (three delivery_status head-window checks in tests/entities.py).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py`: all entity checks pass at the head above.
- `python3 tools/release/stamp.py --self-test`: pass.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `bash tools/pr/prepr.sh`: rc=0 at the head above; origin/main at 4b5d771bd had not moved since the run (git rev-parse origin/main), so no second run. Closures step skipped: the diff touches a workflow, MODE: FULL, CI re-records.
- Not measured: the before/after runner-minutes of one beat-only dispatch. This seat has no workflow-dispatch right and no token; the first stamp after merge should be measured by the runs jobs API (`GET /repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs`) and its job list should show only record-autofix running.
- Savings estimate is the triage's, unmeasured here.

## Red checks

none

## Forward-carry

none

## Friction

none
