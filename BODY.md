Part of #201. R10-FLOW-BODY-ONLY parts (a) to (c), the Lean flow pre-study's K12: ruling R4 made true in the tool, so a body fix no longer moves a clean head. Built on #3037 (V147, the `Code:` trailer).

The group's carries, numbered as the roster's `carry` list numbers them (from 1):

- Carry 1 (the Lean flow pre-study, K12): built here, parts (a) to (c) below.
- Carry 2 (`app_approve.sh --carry` until this lands): released once this merges; a body-only move no longer needs a carry.
- Carry 3 (self-test hygiene): (a) this PR's mutants take per-file ids inside their instrument's block (`cloud_relay-50` to `-57`, `update_pr-1` to `-6`); (b) the new rows reuse the fixtures' existing throwaway origins, and `tests/throwaway_git.py --check` refuses 0 sites; (c) no new git push site: body-only PATCHes through `body_patch.sh`, and `ref_privacy --check` refuses 0 at the head; (d) `## Red checks` below.
- Carry 4 (V147, the `Code:` trailer and the stale-body refusal): landed in #3037; part (c) reads that trailer.
- Carry 5 (P321): landed with carry 4 in #3037.

As built:

- Part (a), `tools/audit/seat/update_pr.sh`: origin/main is merged only when `gh pr view --json mergeStateStatus` says `DIRTY` or `git merge-tree --write-tree origin/main HEAD` fails. An unread merge state counts as not DIRTY, because merge-tree is the local proof either way.
- Part (b), the same script: when the merges and the row leave the head exactly where origin had it, nothing is pushed; `body_patch.sh` runs the body contract at that head, from the run's worktree, and PATCHes the body (`update_pr: BODY-ONLY:`). With code `-`, a `handoff/<topic>` tip the head lacks refuses. A head that is the live head plus one commit asks `--row-only`.
- Part (c), `tools/audit/seat/cloud_relay.sh` `handoff_arm`: a PR whose head holds its handoff tip, and whose `handoff-body/<topic>` tip this relay has not applied and names that tip in `Code:`, gets `update_pr.sh <branch> - <body>` once per body move, recorded in `cloud-handoff-bodied`. The hold applies; the review freeze does not, because the head under review does not move.

Alternatives not taken:

- A commit-time rule for "this body is new": runner and host clocks skew, and a re-body of an unchanged head is legitimately newer. The applied-body record needs no clock.
- Body-only only for code `-`: a code sha the head already holds leaves the same unmoved head, and refusing it keeps the prepr re-run cost.
- Running `body_patch.sh` from the main checkout: its lint resolves cited paths in the caller's tree, so a body citing a file the PR adds is refused.

## Re-cut

Round 2 of R10-FLOW-BODY-ONLY, answering `verdict/3089` (blocked at `b283c082`, mutation-vacuous): the review's own mutants B (`cloud_relay.sh` `handoff_arm`, `[ -z "$bonly" ]` made `true`, so body-only moves fall back under the review freeze) and A (`update_pr.sh`, the merge-tree conflict arm made `|| :`, so a conflicting main is merged only when gh says DIRTY) survived their self-tests. Commit `0d681c9b4` adds the owed fixture rows and harness entries; `3dbc63846` and `9ddcf3251` renumber this PR's relay mutants to `cloud_relay-50` to `-57` past #3065's `-39` to `-49` and re-cut `cloud_relay-25`/`-22`/`-27` to the merged freeze line. Every figure below was re-taken in this pass at the head named under `## Head`; earlier rounds' figures are dropped.

The verdict's third finding: the items earlier rounds left owed were already re-homed on the roster ref `handoff/audit-r10-roster` by the orchestrator, each to a live group, and stay there: exit 75 (P22), levels before the serial loop, the handoff-body ledger disposition and #3037's M2/M5 guides in R10-RELAY-HANDOFF-ARM; `--roster-ref` in the contract arm, V115 and card 7's figure block in R10-BODY-CONTRACT; card 4's prepr-reuse half in R10-OPENER-REUSE; card 7's dispatch hold in R10-DISPATCH-AT-HANDOFF; ref_privacy's home-directory refusal in R10-SEAT-IDENTITY-GUARDS.

## Head

`f0a0ee4f6e652616e50585bb6a6cc6c176d7fb0f`, a merge of origin/main `c3a279e3` (34 commits past the previous handoff `e624cb10`, merged clean: `git merge-tree` reported no conflict and no claim-file driver lines) into `e624cb10e41a628d0e49645f6f6907c63c795e87`, which contains the PR head `1cab0b51`. origin/main did not move between the merge and the `prepr.sh` run, so it was run once.

## Mutation proof

Finder's harness, at both ends. At `b283c082` the verdict's `ev/own-mutants.diff` left `cloud_relay.sh --self-test` and `update_pr.sh --self-test` at 0 failed (`ev/own-B-cloud_relay.txt`, `ev/own-A-update_pr.txt`). At the head, the same two edits, each planted alone in a copy of the head tree:

- Mutant B (`if [ -z "$bonly" ] && ...` to `if true && ...`): `cloud_relay self-test: 332 checks, 3 failed`, red on "a new body at a contained head holding a merge verdict runs update_pr once, body-only", "and is neither printed HELD nor owed handoff-held", and "a new body at a contained head with a reviewer dispatched runs update_pr once, body-only".
- Mutant A (`... || MAIN=1` to `... || :`), applied from the diff to a head copy: red on "update_pr: main conflicting with the head while gh answers CLEAN is merged: the run stops, patching and pushing nothing" and "... while gh answers an error is merged: ...".

The PR's in-tree harness, `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py` with the ids under `## Figures`, each mutant after its unmutated step passed: all 19 KILLED, `RESULT survivors=0`, rc=0. `cloud_relay-57` is mutant B and `update_pr-6` is mutant A.

## Null control

- The unmutated head: `bash tools/audit/seat/cloud_relay.sh --self-test` reports `332 checks, 0 failed`; `bash tools/audit/seat/update_pr.sh --self-test` reports `delivery_row self-test: 6 checks, 0 failed` and `pr_args self-test: 168 checks, 0 failed`.
- Mutant B's rows: "a handoff tip the verdicted head does not hold is still HELD-VERDICT (null control)" and "and runs no update and owes handoff-held" pass at the head, so the freeze still binds a code move.
- Mutant A's rows: with main clean and gh CLEAN, the head sha is identical before and after (the R4 row), so the new rows red only on a real conflict.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test`: its last line reports 0 failed.
- `bash tools/audit/seat/update_pr.sh --self-test`: delivery_row's and pr_args's tallies each report 0 failed.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-8 cloud_relay-9 cloud_relay-22 cloud_relay-25 cloud_relay-27 cloud_relay-50 cloud_relay-51 cloud_relay-52 cloud_relay-53 cloud_relay-54 cloud_relay-55 cloud_relay-56 cloud_relay-57 update_pr-1 update_pr-2 update_pr-3 update_pr-4 update_pr-5 update_pr-6`: each line KILLED, harness rc=0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`; `scope.run` names `tests/doc_claims.py`, which passes under `PYTHONPATH=tests/hastub`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: 0 sites refused, 0 stale allow entries.
- `tools/pr/prepr.sh <this body>` at the head, closures not skipped: `rc=0`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL` (shell and harness files only).

## Red checks

none. At the PR's live head `1cab0b51` the check-run set is 55 runs on one page (MCP `get_check_runs`), none concluded failure; `tests / nightly-status` is green there. The new head has no runs until it is pushed to the PR.

## Forward-carry

none

## Friction

none
