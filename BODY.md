R10-CARRY-RESIDUE part 2: the carry audit, bus round counter, body_push/relay and standing-tick items the round-3 re-cut routed here.

Code: 0e751cc72e56b153ed6483074358c50407fbd5cf

## Head

0e751cc72e56b153ed6483074358c50407fbd5cf, measured at merge base 7812357d5f9dee605cb9af6dabe01a24a4d35655 (origin/main at 2026-11-08, `git merge-tree --write-tree origin/main HEAD` prints only a tree id, no CONFLICT line).

## Head note

Repair of the round-2 verdict `Fix review: blocked 061a828e18df8ba29a95827fb0e11cd3b7f963b4 ci-red`. Change: `tools/audit/seat/ledger.py` `KINDS` gains `"carry-fold": "derived"` (the kind `cloud_relay.sh` `carry_fold_arm` writes as a level line); then origin/main (7812357d5) merged in, cleanly. New head 0e751cc72e56b153ed6483074358c50407fbd5cf; every figure and `prepr.sh` below were re-run at it.

## Merge resolution

The round-1 verdict blocked 6b5d99b5c on a content conflict in `tools/audit/carry_audit.py` `landed()` with #3318 (merge 17e621f08). Main added the own-group carry-status arm (`own_group`, `own_carry_status`, `# mut:ownstatus`, the `statuses` argument and the `CARRY-STATUS` print); this head replaced the landing predicate so a source lands only through a group's carries. The resolution keeps both, in that order: an own-group item naming one of its carries by index is a status line and `continue`s before any landing test; every other item takes this head's predicate (`r["id"]` in brief or carries, a source token in carries only). The `landed()` docstring now states the source rule. No other file conflicted; `cloud_dispatch.py` auto-merged. `git merge-tree --write-tree origin/main HEAD` now prints only the tree id (9e89e536f) at 30986c09c, no CONFLICT line.

## Carry dispositions

- Carry 0: covered here. `dev/governance/roles/standing-tick.md` names the unflagged `CARRY: #<pr> <sha>` line beside the ancestor-recarry test, inside the file's budget (25 lines, `policy_lint.mjs` clean). A policy edit: it waits for the owner's approving review (see Approval).
- Carry 1: fixed in `carry_audit.landed()`. A source token (`--pr`, `--topic`) lands an item only through a group's carries, never its brief; an item id still lands through either. The brief names the PRs it was cut from, which is why `--pr '#3234'` hid every missing carry.
- Carry 2: same edit as carry 0.
- Carry 3: `body_push.sh` exits 4 when CARRY-LANDED is the refusal (the earlier arms exit before it) and every refusal prints `body_push: REFUSED <KIND>`; `cloud_relay.sh` gains `carry_fold_arm` (run each pass after `handoff_arm`), see carry 14. The carry named a `handoff-wip/<topic>-carries` ref; none is needed, because the refused body is already kept on `handoff-wip/<topic>-body`.
- Carry 4: `bus.sh blocked_rounds` counts distinct blocked heads on `verdict/<pr>`.
- Carry 5: `set-resume --field pr` per done group lacking `resume.pr`; precondition: count measured at the roster seat's own base, each `pr` read from `dev/programme/delivery/<N>.md`. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 6: one `edit-brief` per live group naming the old handoff phrase; precondition: the phrase count over live briefs reads 0 afterwards. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 7: `set-stage <G> absorbed --into <host>`; precondition: `carry_audit.py roster` then reports REROUTED. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 9: duplicate of carry 5. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 10: duplicate of carry 6. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 11: duplicate of carry 7, and the absorbed-group lint is built only after those data edits land. Roster DATA edit on the roster branch this seat may not write; it waits for the orchestrator's roster seat with its precondition kept. Nothing was written or guessed here.
- Carry 8: plant C6 now fails with FAIL lines (see Mutation proof).
- Carry 12: same as carry 8.
- Carry 13: same edit as carry 0.
- Carry 14: `carry_fold_arm` reads each `handoff-wip/<topic>` BLOCKED.md and, only when its refusal kinds are exactly CARRY-LANDED and `handoff-wip/<topic>-body` is kept, runs `carry_fold.py` on that body and then `body_push.sh` from a worktree at `handoff/<topic>`. Any other block prints `OWED carry-fold ...` and goes on the level. The fixer prompt (`cloud_dispatch.py`) tells a fixer to push the exit-4 output as BLOCKED.md.
- Carry 15: the review packet reports it, but the group holds carries 0 to 14 on `origin/handoff/audit-r10-roster`; nothing is owed under that number.

## Mutation proof

- Carry 1 (carry_audit.py is byte-identical to its 30986c09c state, so the proof stands): `landed()`'s source check read against `group_text(dests, tok)` (brief included) instead of `group_text(dests, tok, False)`: `python3 tools/audit/carry_audit.py --self-test` goes `402 checks, 1 failed` (FAIL "landed: the source named only in the group's brief does not land it (#3234, before)"); restored: `402 checks, 0 failed`.
- Merge resolution (main's arm kept): `if tok == own and own_carry_status(...)` (`# mut:ownstatus`) replaced by `if False:`: the same self-test goes `402 checks, 2 failed` (FAIL "landed: an own-group item naming one of its carries by index lands nothing and is a status line", FAIL "landed: the group is read from pr_group when the source names no topic"); restored: `0 failed`. So the resolution keeps #3318's pins live under this head's predicate.
- Carry 4: dropping `sort -u` in `blocked_rounds`: `bash tools/audit/seat/bus.sh --self-test` adds FAIL "five re-posts at one head count as one round and dispatch (#3247)" (fixture: five re-posts at one head).
- Carry 14: replacing the `# mut:foldonly` test with only the kept-body test: `bash tools/audit/seat/cloud_relay.sh --self-test` goes `384 checks, 6 failed` (the mixed-block and no-refusal-line arms); restored: `0 failed`.
- Carry 8: `python3 tools/audit/seat/r10_roster_ops_mutants.py C6` was `rc=1 fails=0` with a KeyError tail before the fix; now `rc=1 fails=3` (FAIL "triage gate fixture restored", "drop-carry with no carry refused", "drop-carry of the last entry leaves the key empty"). The fix is `refuses()` in the `roster_edit.py` self-test treating a crash as no refusal, plus `.get("carry")` in the fixture-restored check.

## Null control

- Carry 1: the same source in a group's carries lands the item (`landed(...) == []`); `#25581` still does not land `#2558`.
- Carry 4: three distinct blocked heads are three rounds and refuse without a `## Re-cut` note (dispatch of #35 fixture).
- Carry 14: `CARRY-LANDED` plus `BODY-LINT` in one BLOCKED.md folds nothing and prints its line; a BLOCKED.md with no refusal line likewise.
- Carry 8: unmutated `roster_edit.py --self-test`: `242 checks, 0 failed`.
- `body_push.sh --self-test` pins exit 4 for the landed arm and exit 1 for pred, lint and packet, and that each prints its `REFUSED` kind.

## Figures

All at 0e751cc72e56b153ed6483074358c50407fbd5cf, 2026-11-08 (UTC). Null control for the repair: with `"carry-fold": "derived",` removed from `KINDS` only, `python3 -I tools/audit/seat/ledger.py --self-test` prints `FAIL every kind cloud_relay.sh writes is a ledger kind (census of level_line and ledger_open)` and `101 checks, 1 failed`; restored it prints `101 checks, 0 failed`.

Every `tools/audit/seat` / `tools/audit` self-test the diff reaches (the diff's files: bus.sh, body_push.sh, cloud_dispatch.py, cloud_relay.sh, ledger.py, roster_edit.py, carry_audit.py; plus carry_fold.py and r10_ledger_mutants.py, which read them), each exit 0:

- `python3 -I tools/audit/seat/ledger.py --self-test` : 101 checks, 0 failed.
- `python3 -I tools/audit/carry_audit.py --self-test` : 402 checks, 0 failed.
- `bash tools/audit/seat/body_push.sh --self-test` : 36 checks, 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test` : 393 checks, 0 failed.
- `bash tools/audit/seat/bus.sh --self-test` : 161 checks, 0 failed.
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` : 129 checks, 0 failed.
- `python3 -I tools/audit/seat/roster_edit.py --self-test` : 242 checks, 0 failed.
- `python3 -I tools/audit/seat/carry_fold.py --self-test` : 6 checks, 0 failed.
- `python3 -I tools/audit/seat/r10_ledger_mutants.py --self-test` : 194 checks, 0 failed.
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at 0e751cc72e56b153ed6483074358c50407fbd5cf: `rc=0`; `ci predict` predicts no red against 7812357d5f9d; `closures` skipped (PREPR_SKIP_CLOSURES), `diff mutants` skipped (MUTANT_CMD unset; the null control above is the proof). origin/main unmoved since the merge, so no second run.

## Unpinned sites

At the new head `prepr.sh` step 6d reports "the diff adds no unpinned mutation site". The dispositions below are the 444f489ad run's, kept for the sites that run listed:

- `carry_audit.py:1880` and `:1882` (CONST_SWAP on the fixture's group index / done-set): equivalent. Moving the brief to a group the item does not name leaves the expected `1 missing`; the real kill is the mutation proof above.
- `roster_edit.py:1523` (RETURN_DEL, CONST_SWAP on `refuses()`'s crash arm) and `:1759` (CONST_SWAP on the group index): the arm runs only when an op crashes, so only the C6 plant reaches it. Killed there, not by the normal self-test: `r10_roster_ops_mutants.py C6` above, an in-tree harness.

## Red checks

Check-runs of 061a828e18df8ba29a95827fb0e11cd3b7f963b4 (the PR head under review), read once via get_check_runs, 55 runs. The repaired head has no check-runs yet; each red below is answered for 061a828e and the repair is the single `KINDS` entry.

- `governance / instrument-self-tests` (run 42527535100, job 128874739574, failure): this diff caused it. `ledger.py --self-test` printed `101 checks, 1 failed`, the census `every kind cloud_relay.sh writes is a ledger kind`, because `carry_fold_arm` writes `level_line carry-fold` and `KINDS` lacked it. Repaired: `KINDS` has `carry-fold`; `ledger self-test: 101 checks, 0 failed` at the new head, with the null control above. Cheaper detector: that one command (seconds); `prepr.sh` does not run it, only `governance.yml` does. Standing cost of closing the gap: one line in the `prepr.sh` self-test list, seconds per run; not built here, outside this repair's scope, left to the orchestrator.
- `gate` (job 128876390290, failure; run 42527535264): the aggregate of the red above (it decides on `governance / instrument-self-tests`); clears with it.
- `gate` (job 128879330618, cancelled), `tests / ci-ratchet` (128879330832), `tests / coverage` (128875307010), `tests / coverage-ratchet` (128879277746), `tests / graders-head-copy` (128879277641), `tests / lane-proofs` (128879277788), `tests / closures` (128875307045), `tests / closures-autofix` (128879329875): all `cancelled`, all in run 42527535100, none a failure of their own. The run was cancelled at 22:13:30-22:13:41Z, about a minute after `instrument-self-tests` failed at 22:12:44Z: the gate's supersession of a run whose decider was already red. They did not execute to a verdict, so they are re-run at the repaired head; no cause to repair beyond the ledger entry.

## Forward-carry

- The roster data edits above stay with the orchestrator's roster seat. Carry: dismissed: already carries 5, 6, 7, 9, 10 and 11 of this group, no new finding
- `standing-tick.md` line: policy, awaits the owner's review. Carry: dismissed: it is in this diff, nothing to carry

## Approval

Pending, not given: `dev/governance/roles/standing-tick.md` (the `CARRY:` line, 4 lines changed) is a policy edit and merges only on the owner's approving review at its head.

## Friction

none
