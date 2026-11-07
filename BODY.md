Beat-only dispatch (P404) and one window for rules 4 and 5 (P403), from triage batch 132 (dev/programme/triage/s6-batch132.md). The record flush dispatched nightly.yml with no input, so every nightly lane ran to reach the one-minute record-autofix job. Rule 5 read tag..origin/main while rule 4 read tag..HEAD, so a merge past HEAD after a flush timeout refused rows (v7.1.5 run 1, #3271).

Changes: nightly.yml gains `workflow_dispatch.inputs.lanes` (choice all|beat, default all); mutation-nightly, mutation-ledger, mutation-ledger-push, slow and nightly-ha append `&& inputs.lanes != 'beat'`; record-autofix's `if` is unchanged. stamp.py `RECORD_BEAT_PAYLOAD` posts `lanes=beat`; the hand form is `gh workflow run nightly.yml -f lanes=beat`. `tests/delivery_status.py --head REV` (default origin/main) ends its window; `disposition_gate` passes the stamp head. tests/entities.py gets `inputs.lanes` in its `_gh_eval` contexts, a pin that every heavy job skips on lanes=beat and record-autofix does not, and the `--head` window checks. Alternative considered: a separate workflow file for the beat; rejected because REQUIRED_LANES and the record-writer environment are keyed to nightly.yml.

Closes: none.

## Head

01e9c61273753db2526fb19b6b44ece19167128b

## Mutation proof

- Dropping `--head` from `disposition_gate_argv`: stamp self-test FAIL "rows gate: the stamp's head is passed to the instrument, one window with rule 4" and "rows gate: disposition_gate forwards its head to the command".
- Dropping lanes=beat from `RECORD_BEAT_PAYLOAD`: FAIL "record beat: the dispatch payload carries lanes=beat on main" and "record beat: dispatch_record_beat posts lanes=beat".
- Deleting every `&& inputs.lanes != 'beat'` from nightly.yml: tests/entities.py FAIL "lanes=beat skips every heavy nightly lane and runs record-autofix; no input runs every lane".
Each mutant was run against the committed tree and restored; `git status --short` clean afterwards.

## Null control

A dispatch with no input (hand probe, lanes empty) runs every lane in REQUIRED_LANES and record-autofix (entities check above, `_NS_HAND`); schedule and push still evaluate as before (the existing derivation check passes with `inputs.lanes` = all). `--head` at the tip (M2) returns the same merges as the default origin/main window, and the default equals head=origin/main (three delivery_status head-window checks in tests/entities.py).

## Figures

- `PYTHONPATH=tests/hastub python3 tests/entities.py` at 01e9c61273753db2526fb19b6b44ece19167128b: ALL 2650 ENTITY CHECKS PASSED (rc=0).
- `python3 tools/release/stamp.py --self-test` at the same head: stamp_self_test=pass.
- `python3 tests/structure.py` at the same head: STRUCTURE RATCHET PASSED.
- Code change since the earlier handoff 45510e0e: none by this seat; the head differs from it only by main's merged commits (stamp.py, merge_train.py, delivery rows). This body-only re-take pushes no code and ran no `tools/pr/prepr.sh`; the code's last clean run was at 45510e0e.
- Not measured: the before/after runner-minutes of one beat-only dispatch. This seat has no workflow-dispatch right; the first stamp after merge should be measured by the runs jobs API (`GET /repos/tvofi/heatpump_optimizer/actions/runs/<id>/jobs`), whose job list should show only record-autofix running.
- Savings estimate is the triage's, unmeasured here.

## Red checks

- `tests / nightly-status` (check-run 128480692664, run 42397677526): class: inherited main red, not this diff's. It grades the last concluded nightly dispatch on `main`: run 42369836867 at head 08fd676 (2026-11-07 11:50 UTC, before this branch), conclusion `cancelled`; the lanes it lists as failing are mutation-ledger (1) to (4), mutation-ledger-push, mutation-nightly and slow, each `cancelled`, none with a test failure. A cancelled dispatch on main runs main's nightly.yml at 08fd676, which carries neither this diff's `inputs.lanes` nor its `--head` edit, so the diff cannot have reached those lanes. The next concluded main dispatch, run 42382408131 (head a37c58e, 2026-11-07 14:36 UTC), concluded `success` at 18:28 UTC, so a re-run of this check reads green. Cheaper detector: none is owed; the check already names the run and the lanes, and its standing cost is one 9-second job. Verification dispatch of this branch's nightly.yml: none exists (this seat has no workflow-dispatch right); the first beat-only stamp dispatch after merge is the proof, see Figures.
- `pr-contract / pr-contract` (check-run 128492906044): class: body contract. It refused the previous body for the line above (an unnamed red on a check this diff's files feed). This body answers it.
- `gate` (check-runs 128493108261, 128487511325, 128481833681): class: aggregate. Each is red because of another check at this head: 128487511325 and 128481833681 failed with "run(s) [42397677526] at this head are still being judged; their gate decides" (the sibling run still pending then); 128493108261 is red only because of `pr-contract / pr-contract` above. No cause of its own; each clears when its sibling does.

## Forward-carry

none

## Friction

none
