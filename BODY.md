Part of #201. R10-FLOW-BODY-ONLY parts (a) to (c), the Lean flow pre-study's K12: ruling R4 made true in the tool, so a body fix no longer moves a clean head. Built on #3037 (V147, the `Code:` trailer), which merged as `460d7754f`.

The group's carries, numbered as the roster's `carry` list numbers them (from 1):

- Carry 1 (K12) and the brief's parts (a) to (c): built here, below.
- Carry 2 (`app_approve.sh --carry` until this lands): released once this merges; a body-only move no longer needs a carry.
- Carry 3 (seam with R10-ORCH-MACHINERY): the body-only path is `update_pr.sh <branch> - <body>`, one call whose state is its arguments and exit code, so the beat's handoff job can call it unchanged. `ledger.py` exists, but this diff writes no ledger disposition for the handoff-body ref (the relay keeps `cloud-handoff-bodied`); owed.
- Carry 4 (self-test hygiene): (a) the new mutants take per-file ids inside their instrument's block (`cloud_relay-39` to `-45` after `cloud_relay-38`; `update_pr-1` to `-5` after `pr_args-1`); (b) the new update_pr rows reuse pr_args.sh's `throwaway_git_init` origin and the relay rows its bare-origin fixture; (c) no new git push site: body-only PATCHes through `body_patch.sh`; (d) `## Red checks` below.
- Carry 5 (P22): half built. A failed body-only run is keyed on `<topic> <code-sha> <body-sha>`, so a body-only repair re-triggers it, and its reason is kept (#3037's `.why`). Exit 75 for "checked out elsewhere" and worktree-in-use, and OWED lines for content refusals: owed.
- Carry 6 (the level written before the serial update loop): owed.
- Carry 7 (`--roster-ref` in body_patch.sh's contract arm): owed.
- Carry 8 (card 7, the generated figure block): owed; it now has the body-only transport it builds on.
- Carry 9 (hold part (a) behind the merge-queue probe): lifted by carry 10.
- Carry 10 (train-path branch of part (a)): built.
- Carry 11 (V115, `trackedFiles()` at a revision): not built. Body-only mode runs `body_patch.sh` from update_pr.sh's own worktree, which is checked out at the head it gates, so its contract resolves the head's paths; the lint change itself stays owed.
- Carry 12 (V64 not built in #2858): stands; built under carry 13.
- Carry 13 (auto-open on handoff): owed.
- Carry 14 (V147): landed in #3037.
- Carry 15 (ref_privacy.py's home-directory refusal on a cloud seat): owed; this diff does not touch ref_privacy.py.
- Carry 16 (V191, a body-only handoff skipped in silence): closed by part (c). A body-only handoff is now applied, or owed as `handoff-update` with its reason, or as `handoff-body-stale`.
- Carry 17 (#3037 review): M2 and M5 are killed by new fixture rows (`cloud_relay-42`, `-43`); the two instrument guides document the `Code:` trailer, `cloud-handoff-failed.why`, `handoff-body-stale` and the body-only path.
- Carry 18 (P321): landed in #3037.
- Carry 19 (card 4, prepr reuse): the re-run half is built. An update whose code sha the head already holds is body-only (no push, no prepr), and one that only adds the row asks `--row-only`. The other half, a code sha new to the PR whose fixer passed prepr, still runs the full prepr. There is no host-side record of a PRE-PR rc=0 keyed by tree; owed.
- Carry 20 (structure.py on the reuse path, #3052): the built half takes no main merge past prepr. A body-only run leaves the head unmoved, and a row-only head adds one row file, so neither changes a counted class. Main is merged only when the PR is DIRTY or the merge conflicts, and that head runs the full prepr (fixture row "a DIRTY pull request still absorbs main, through the full prepr"). The carry's rule binds the owed half of carry 19.

As built:

- Part (a), `tools/audit/seat/update_pr.sh`: origin/main is merged only when `gh pr view --json mergeStateStatus` says `DIRTY` or `git merge-tree --write-tree origin/main HEAD` fails. An unread merge state counts as not DIRTY, because merge-tree is the local proof either way. The `## Head` note names a main merge only when one happened.
- Part (b), the same script: when the merges and the row leave the head exactly where origin had it, nothing is pushed. This happens when the code sha is already in the head (or is `-`), main is clean and the row is present. `body_patch.sh` then runs the body contract at that head, from the run's worktree, and PATCHes the body; `update_pr: BODY-ONLY:` says so. body_patch's refusal (a head that moved) is the run's. With `-`, a `handoff/<topic>` tip the head lacks refuses. A head that is the live head plus one commit asks `--row-only`; it no longer depends on the code sha being `-`.
- Part (c), `tools/audit/seat/cloud_relay.sh` `handoff_arm`: a PR whose head holds its handoff tip, and whose `handoff-body/<topic>` tip this relay has not applied and names that tip in `Code:`, gets `update_pr.sh <branch> - <body>` once per body move. `cloud-handoff-bodied` records `<topic> <body-sha>` for every body applied, by an update or by a body-only run. A pass that finds no such file records every contained topic's body and runs nothing (the seed), so the first pass does not re-body every open PR. A contained body with no `Code:` line is recorded and left alone. The hold applies; the review freeze does not, because the head under review does not move. No reviewer is dispatched for a body-only move.
- `dev/audit/harnesses/r10_seat_selftests_mutants.py`: `cloud_relay-9` follows the new containment line, and `cloud_relay-8` is re-cut. On main its pattern matched 0 times, because the freeze block now sits between the hold and the ledger; the mutant now puts a silent ledger test ahead of the hold.

Alternatives not taken:

- A commit-time rule for "this body is new" (carry 16's wording). Carry 18 rules out clock comparisons between runner and host, and a re-body of an unchanged head is legitimately newer. The applied-body record needs no clock.
- Body-only only for code `-`, as the brief words it. A code sha the head already holds leaves the same unmoved head, and refusing it would keep card 4's re-run cost (carry 19).
- Running `body_patch.sh` from the main checkout: V115's shape. Its lint resolves cited paths in the caller's tree, so a body citing a file the PR adds is refused.

## Head

`3d1c850bb0d2f14159f94f6e3e9ecfe0be7bf39d`, cut from origin/main `92588d581fde4ce287af3db5e8bb61461dc28015` (unmoved through the measurements). The mutants, self-tests and gate were run on this tree; the update_pr mutants were also run by hand at its parent `6f88eab66`, which differs only in the relay fixture's seed row and the harness's `cloud_relay-8`.

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py <id>...`, each id after its unmutated step passed (the harness's per-mutant null control):

- `update_pr-1`, main always merged: red on "with main ahead and a clean merge-tree, the head sha is identical before and after (R4)" and four rows that follow it.
- `update_pr-2`, DIRTY ignored: red on "a DIRTY pull request still absorbs main, through the full prepr".
- `update_pr-3`, no body-only branch: red on "a body-only run (code -, row present) PATCHes the body at the unmoved head ..." and "a code sha the head already holds runs no push and no prepr", among seven.
- `update_pr-4`, the `-` containment test made true: red on "code - with a handoff tip the head lacks refuses, and patches no body".
- `update_pr-5`, body_patch's refusal ignored: KILLED (the moved-head row).
- `cloud_relay-39`, the applied-body test dropped: red on "a new body ... runs update_pr once, body-only" (3 checks).
- `cloud_relay-40`, no seed: red on "a pass with no bodied record seeds it ... and runs nothing".
- `cloud_relay-41`, the code sha passed instead of `-`: red on the body-only rows.
- `cloud_relay-42`, #3037's M2 (`tail` to `head`): red on "a failed update's handoff-update line ends in the last of its REFUSE lines".
- `cloud_relay-43`, #3037's M5 (no replay): red on "and the update's whole output reaches the relay's stderr".
- `cloud_relay-44`, the failure not keyed on the body sha: red on "a failed body-only run is recorded on topic, code and body sha".
- `cloud_relay-45`, a successful run not recorded: red on "a new body ... runs update_pr once".
- `cloud_relay-8` (re-cut) and `cloud_relay-9` (re-anchored): KILLED.

## Null control

- update_pr: a new code sha is merged and pushed through the full prepr, main still unmerged (pr_args.sh check "null control: a new code sha is merged and pushed through the full prepr, main still unmerged").
- update_pr: a head that only gains its row still pushes once, with `--row-only` ("a head that only gains its row pushes once, asking for --row-only"). The pre-existing row-only rows pass unchanged, one renamed for the new rule: a head merging new code never asks.
- relay: a body already applied runs nothing on the next pass ("a body already applied runs nothing on the next pass (null control)"). A contained body with no `Code:` line runs nothing. Every pre-existing handoff-arm row passes unchanged.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test`: its last line reports 0 failed.
- `bash tools/audit/seat/update_pr.sh --self-test`: delivery_row's and pr_args's tallies each report 0 failed.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-8 cloud_relay-9 cloud_relay-39 cloud_relay-40 cloud_relay-41 cloud_relay-42 cloud_relay-43 cloud_relay-44 cloud_relay-45 update_pr-1 update_pr-2 update_pr-3 update_pr-4 update_pr-5`: each line KILLED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`; `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`, the script `scope.run` names, passes, and so do the `run_always` lines (`tests/env_drift.py --claims-only`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: 0 sites refused.
- `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh <this body>` at the head: `rc=0`. origin/main did not move between that run and the handoff, so it was not re-run.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL` (shell and harness files only).

## Red checks

- `tests / nightly-status`: red on main's ancestry and graded on main. This diff touches nothing it reads, so it is the orchestrator's on main.

No check went red on this branch: prepr's `ci predict` step predicts no closures, fast, governance or instrument red against the merge base.

## Forward-carry

- Every carry the list above marks owed stays in the group's own brief, `dev/programme/rosters/wave-r10-groups.json` stage R10-FLOW-BODY-ONLY. That covers carries 3 (ledger disposition), 5 (exit 75, OWED content refusals), 6, 7, 8, 11, 13, 15, and 19's new-code-sha half with carry 20's structure rule. Carry: R10-FLOW-BODY-ONLY

## Friction

none
