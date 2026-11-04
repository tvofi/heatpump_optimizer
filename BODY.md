Part of #201. R10-FLOW-BODY-ONLY parts (a) to (c), the Lean flow pre-study's K12: ruling R4 made true in the tool, so a body fix no longer moves a clean head. Built on #3037 (V147, the `Code:` trailer).

The group's carries, numbered as the roster's `carry` list numbers them (from 1):

- Carry 1 (the Lean flow pre-study, K12): built here, parts (a) to (c) below.
- Carry 2 (`app_approve.sh --carry` until this lands): released once this merges; a body-only move no longer needs a carry.
- Carry 3 (self-test hygiene): (a) this PR's mutants take per-file ids inside their instrument's block (`cloud_relay-50` to `-58`, `update_pr-1` to `-7`); (b) the new rows reuse the fixtures' existing throwaway origins, and `tests/throwaway_git.py --check` refuses 0 sites; (c) no new git push site: body-only PATCHes through `body_patch.sh`; (d) `## Red checks` below.
- Carry 4 (V147, the `Code:` trailer and the stale-body refusal): landed in #3037; part (c) reads that trailer.
- Carry 5 (P321): landed with carry 4 in #3037.

As built:

- Part (a), `tools/audit/seat/update_pr.sh`: origin/main is merged only when `gh pr view --json mergeStateStatus` says `DIRTY` or `git merge-tree --write-tree origin/main HEAD` fails. An unread merge state counts as not DIRTY, because merge-tree is the local proof either way.
- Part (b), the same script: when the merges and the row leave the head exactly where origin had it, nothing is pushed; `body_patch.sh` runs the body contract at that head, from the run's worktree, and PATCHes the body (`update_pr: BODY-ONLY:`). With code `-`, a `handoff/<topic>` tip the head lacks refuses. A head that is the live head plus one commit asks `--row-only`.
- Part (c), `tools/audit/seat/cloud_relay.sh` `handoff_arm`: a PR whose head holds its handoff tip, and whose `handoff-body/<topic>` tip this relay has not applied and names that tip in `Code:`, gets `HPO_UPDATE_BODY_ONLY=1 update_pr.sh <branch> - <body>` once per body move, recorded in `cloud-handoff-bodied`. The hold applies; the review freeze does not, and `update_pr.sh` now guarantees the reason it does not: under `HPO_UPDATE_BODY_ONLY` a run whose merges or row would leave the head other than the live head refuses (`update_pr: REFUSE: body-only update would move the head ...`) and pushes nothing, and the relay records that refusal as owed `handoff-update`.

Alternatives not taken:

- A commit-time rule for "this body is new": runner and host clocks skew, and a re-body of an unchanged head is legitimately newer. The applied-body record needs no clock.
- Body-only only for code `-`: a code sha the head already holds leaves the same unmoved head, and refusing it keeps the prepr re-run cost.
- Running `body_patch.sh` from the main checkout: its lint resolves cited paths in the caller's tree, so a body citing a file the PR adds is refused.
- Round 7's guard in the relay (apply the freeze unless the move is guaranteed body-only): the relay cannot know DIRTY or a missing row without re-deriving what `update_pr.sh` computes after its merges, so it would duplicate that logic. The flag puts the check where `H` and `LIVE` already are: one guard line in `update_pr.sh` plus one env assignment on the relay's launch line.

## Re-cut

Round 7 of R10-FLOW-BODY-ONLY, a minimal re-cut answering `verdict/3089` round 2 (blocked at `2fd46f26`, class-open): `handoff_arm` skipped the review freeze on a body-only move, but `update_pr.sh <branch> - <body>` still moved the head when (a) the PR was `DIRTY` and the local merge of main was clean, or (b) a contained head lacked its delivery row (`ensure_row`, `--row-only` push), so a head holding a merge verdict or a dispatched review could move with no `cloud-handoff-release` entry and no `HELD-*` line. Closed at one seam, `update_pr.sh`'s head check, driven by the relay's `HPO_UPDATE_BODY_ONLY=$bonly` (commit `62673524`); `9da59904` documents the refusal in both instrument guides. The verdict's second finding: `## Red checks` below is retaken from the whole check-run set and names `tests / nightly-status` as main's inherited red. Every figure below was taken in this pass, at the head named under `## Head` or, for the self-tests and harness, at `9da59904`, as that section states.

## Head

`39e9abd5009448270215222943aa0fd0ac76b1e1`: the PR head `2fd46f26` with origin/main merged four times, clean (`a9c2f90f`, `fad43b04`, `616868bd`, then `8e90d814` as main moved during the pass), the fix commit `62673524` and the instrument-guide commit `9da59904`. main's moves since (`fad43b04..8e90d814`) touch the card, archscore, `thermal_model.py`, budgets and their tests, none of the seat files, so the self-test and harness figures taken at `9da59904` describe this head's seat tools; structure, scope, doc_claims, the architecture score and `prepr.sh` were re-run at this head against origin/main `8e90d814`.

## Mutation proof

Finder's own mutants (`verdict/3089:evidence/own-mutants.diff`): at the head, harness ids `cloud_relay-57` (mutant B) and `update_pr-6` (mutant A) are byte-identical to them and are KILLED (Figures).

The guard this round adds, killed at both seams:

- `update_pr.sh`'s guard line deleted (self-test mutant `mut:bodyonly`, harness `update_pr-7`): red on "update_pr: a relay body-only run on a head lacking its row refuses, the head unmoved and nothing pushed" and "update_pr: a relay body-only run on a DIRTY head whose merge of main is clean refuses, the head unmoved and nothing pushed"; the in-test mutant rows show the head moved (row pushed; main merged into the DIRTY head and pushed).
- The relay's `HPO_UPDATE_BODY_ONLY=$bonly` dropped (harness `cloud_relay-58`): `cloud_relay self-test: 332 checks, 4 failed`, the body-only rows, including "a new body at a contained head holding a merge verdict runs update_pr once, body-only" and "a new body at a contained head with a reviewer dispatched runs update_pr once, body-only", whose stub now records the flag.

## Null control

- The unmutated head: `bash tools/audit/seat/cloud_relay.sh --self-test` reports `332 checks, 0 failed`; `bash tools/audit/seat/update_pr.sh --self-test` reports `delivery_row self-test: 6 checks, 0 failed` and `pr_args self-test: 172 checks, 0 failed` (168 before, plus the two guard rows and their two mutant rows).
- Without the flag the same shapes still move the head: "null control: without HPO_UPDATE_BODY_ONLY a DIRTY pull request still absorbs main, through the full prepr" and "update_pr: a head that only gains its row pushes once, asking for --row-only" pass.
- The relay's non-body-only updates record no flag: the anchored rows matching `^fix/topic-a-pr <sha>$` pass, so the flag does not leak to a code move, which the freeze still holds ("a handoff tip the verdicted head does not hold is still HELD-VERDICT (null control)" passes).

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test`: its last line reports 0 failed.
- `bash tools/audit/seat/update_pr.sh --self-test`: delivery_row's and pr_args's tallies each report 0 failed.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py update_pr-1 update_pr-2 update_pr-3 update_pr-4 update_pr-5 update_pr-6 update_pr-7 cloud_relay-29 cloud_relay-57 cloud_relay-58`: each line KILLED after its unmutated step passed, `RESULT survivors=0` (run as two invocations, the first stopped by the session's background bound after its eighth id; the last two re-run alone, rc=0). `cloud_relay-29` is re-anchored to the launch line this round edits.
- Class enumeration: `grep -n 'update_pr' tools/audit/seat/cloud_relay.sh` returns one production launch (`handoff_arm`'s `pr_own_group "${upd[@]}"` line), the only route passing `-` from the relay; it carries the flag. `update_pr.sh`'s head-moving paths after `H` is taken are the two the verdict names (main merge, `ensure_row`), both before the guard line; the code-sha merge is not reachable with `-`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED`; `scope.run` names `tests/doc_claims.py`, which passes under `PYTHONPATH=tests/hastub`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/throwaway_git.py --check`: 0 sites refused, 0 stale allow entries.
- `tools/pr/prepr.sh <this body>` at the head: `rc=0`.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL` (shell and harness files only).

## Red checks

- `tests / nightly-status` (check run 126439441851), at the PR's live head `2fd46f26`: concluded failure. It is main's inherited red: its log reads `NIGHTLY FAILED: slow failed 1 night ago` for the scheduled run at main (`verdict/3089:evidence/nightly-status-log.txt`), and this diff touches only seat tools, their instrument guides, a harness and the row, none of which the slow lane reads. No cheaper detector is owed: the check reports main's nightly, not this branch.
- The whole check-run set at `2fd46f26`, 55 runs on one page (MCP `get_check_runs`), has no other concluded failure. The head named under `## Head` has no runs until it is pushed to the PR.

## Forward-carry

none

## Friction

none
