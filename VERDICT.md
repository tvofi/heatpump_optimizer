Fix review: blocked 2fd46f26d7b35ff196d24b5e163048ed1f904cf7 class-open: cloud_relay.sh body-only move skips the review freeze, but update_pr.sh with code - still moves a DIRTY or rowless head

bus-nonce: d88fd7dd30d693d96b8fb37fa9874491

Round 2 (delta review of the blocked verdict `b283c082`, mutation-vacuous). I judged the whole diff since that verdict, from detached worktrees at `2fd46f26d7b35ff196d24b5e163048ed1f904cf7`, using the finder's mutants (`verdict/3089:evidence/own-mutants.diff`) and not the fixer's account.

## Block

Round 1's block is settled: both of the finder's mutants now turn their self-tests red (Evidence). One seam is still open, and the body states it as a design point without guarding it: "The hold applies; the review freeze does not, because the head under review does not move."

`handoff_arm` skips `review_freeze` whenever `bonly` is set, which means the handoff tip is already in the head. It then runs `update_pr.sh <branch> - <body>`. But `update_pr.sh` with code `-` keeps the head where it is only when main needs no merge and the row is present. Two cases in the predicate's domain move the head and push:

- **The PR is `DIRTY` and the local merge succeeds.** This is the documented case where GitHub cannot run the `claimnotes` driver (`claim-files.md`, `fix-review.md` 13), so only the claim files conflict. `[ "$ST" != DIRTY ] || MAIN=1` merges main, the merge resolves, and the run pushes through the full prepr. In-tree row, passing at this head: "update_pr: a DIRTY pull request still absorbs main, through the full prepr" (`upd - -`, pushes 2 to 3, main now in fix/v; `ev/null-update_pr.txt`).
- **A contained head that lacks its delivery row.** `ensure_row` adds the row and the run pushes `--row-only`. Row: "update_pr: a head that only gains its row pushes once, asking for --row-only" (`upd - -`).

The relay's side of this is also a passing row: "a new body at a contained head holding a merge verdict runs update_pr once, body-only" (code `-`; `ev/null-cloud_relay.txt`). Put together, the two rows mean a head with a merge verdict, or with a reviewer dispatched, is moved by the relay with no `cloud-handoff-release` entry and no `HELD-*` line. Stopping exactly that is the freeze's job. I showed this by composing the two in-tree rows, which take the same argument shape (`<branch> - <body>`). I did not run one end-to-end fixture, because the relay self-test stubs `update_pr.sh`.

A merge-tree conflict is safe: the run stops on the conflict and pushes nothing (the new `update_pr-6` rows).

Owed: when the relay passes `-`, the run must not move the head. For example, a body-only flag (or env) that `handoff_arm` passes and `update_pr.sh` honours by refusing when `H != LIVE` after the merges and the row. Alternatively, `handoff_arm` applies the freeze unless the update is guaranteed body-only. Add one row per case (DIRTY with a clean local merge, and a missing row) under a merge verdict, showing no push and the head unmoved. Add a harness mutant that drops the guard, and a null control: an unfrozen PR still absorbs main when DIRTY.

## Findings

- Body-only relay moves bypass the review freeze on a DIRTY-but-locally-clean or rowless contained head; `update_pr.sh -` then merges main or adds the row and pushes under a merge verdict or a dispatched review (see Block). Carry: R10-FLOW-BODY-ONLY
- The body's `## Red checks` was not retaken for this head. It says "none. At the PR's live head `1cab0b51` ... `tests / nightly-status` is green there. The new head has no runs until it is pushed". The `handoff-body/r10-flow-body-only` tip `92fcc376a` (`Code: f0a0ee4f6e65`, 06:59Z) predates this head (07:02Z). At `2fd46f26`, `tests / nightly-status` (id 126439441851) concluded **failure**. Per its log, this is main's state: `NIGHTLY FAILED: slow failed 1 night ago`, scheduled run 41555367389 at main `b8e8236`, pinned `c3a279e3` (`ev/nightly-status-log.txt`). The diff touches only seat tools, instrument docs, a harness and the row, none of which the slow lane reads, so the red is not this branch's (`fix-review.md` 11). The next body must name it as inherited and must cite only figures taken at the head it names. Carry: R10-FLOW-BODY-ONLY

## Evidence

- RESULT own-mutant B (`ev/own-mutants.diff`, `cloud_relay.sh` `[ -z "$bonly" ]` changed to `true`): `cloud_relay self-test: 332 checks, 3 failed`, rc=1. The failing rows are the two "contained head holding a merge verdict" rows and the "reviewer dispatched" row (`ev/own-B-cloud_relay.txt`). KILLED.
- RESULT own-mutant A (`update_pr.sh` `|| MAIN=1` changed to `|| :`): `pr_args self-test: 168 checks, 2 failed`, rc=1. Both "main conflicting with the head while gh answers CLEAN / an error" rows fail (`ev/own-A-update_pr.txt`). KILLED.
- Null at the head: `cloud_relay self-test: 332 checks, 0 failed`, rc=0. The null-control rows "a handoff tip the verdicted head does not hold is still HELD-VERDICT (null control)" and "and runs no update and owes handoff-held" both show `ok` (`ev/null-cloud_relay.txt`). `update_pr.sh --self-test`: `delivery_row self-test: 6 checks, 0 failed` and `pr_args self-test: 168 checks, 0 failed`, rc=0 (`ev/null-update_pr.txt`). The body's 332/0, 6/0 and 168/0 re-derive.
- Harness entries: `cloud_relay-57` and `update_pr-6` match mutants B and A byte for byte.
- RESULT harness, the PR's in-tree `dev/audit/harnesses/r10_seat_selftests_mutants.py`, run with the body's 19 ids in a worktree of its own at the head: each mutant's unmutated step passed and all 19 were KILLED, `RESULT survivors=0`, rc=0 (`ev/harness.txt`). This includes `cloud_relay-57` (3 failed) and `update_pr-6`. The body's "all 19 KILLED" re-derives.
- CI: `merge_train.py classify 2fd46f26... --pr 3089` reported `GREEN 2fd46f26d7b35ff196d24b5e163048ed1f904cf7 pending: none red: none`, rc=0, at 07:46:39Z (`ev/classify.txt`). The whole check-run set, all pages, is 55 runs (`ev/check-runs.tsv`). The only concluded failure is `tests / nightly-status`, which is main's inherited red (Findings). `pr-contract / pr-contract` is green, in runs 126454259652 and 126455070877, both started after that red concluded. `gate`, `prelude` and `budget-raise-gate` are green. Under `fix-review.md` 11, nightly-status is not this PR's, and the green post-red pr-contract is the evidence for the trigger, so this is not a root-cause block.
- `git merge-tree --write-tree origin/main 2fd46f26`: rc=0, tree `d1c79cf39`, no conflicts and no MERGE-CLAIM lines (`ev/merge-tree.txt`). origin/main is `c3a279e32` and equals the merge base.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0 (`ev/structure.txt`). No `*_budgets.json` is in the three-dot diff.
- VERSION, the manifest, `RELEASE_NOTES.md` and both claim files: the diff against origin/main is empty.
- `python3 tests/closure.py select --diff <merge-base>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (`ev/closure-select.txt`).
- `python3 tests/throwaway_git.py --check`: 0 sites refused, 0 stale allow entries.
- No host path in added lines. The only added `push` text is the `app_push.sh` stub inside pr_args.sh's throwaway fixture origin, so there is no new production push site.
- The delivery row `dev/programme/delivery/3089.md` is in the three-dot diff. `## Head` names `2fd46f26d7b35ff196d24b5e163048ed1f904cf7`.
- Roles diff since the merge base: empty. Review packet: no refusals; carry_audit at the head reports 0 bad destinations.
- Not re-derived: the architecture score `dS +0.0000 NULL` (CI `arch-score` is green at this head) and the body's prepr rc=0.
- The head was still `2fd46f26d7b35ff196d24b5e163048ed1f904cf7` when this verdict was written (`git ls-remote origin refs/heads/fix/r10-flow-body-only` at review end). `handoff-body/r10-flow-body-only` is still `92fcc376a`.
