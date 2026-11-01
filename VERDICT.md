Fix review: blocked b283c082dd86080164a684ae52905cdbdebd387a mutation-vacuous: cloud_relay.sh handoff_arm body-only freeze bypass and update_pr.sh merge-tree conflict arm survive their mutants

bus-nonce: b27f1dd8d127549878139457e6a35bde

Round 1. Reviewed from detached worktrees at `b283c082dd86080164a684ae52905cdbdebd387a`; the head was still `b283c082dd86080164a684ae52905cdbdebd387a` when this verdict was written (git ls-remote).

## Block

The PR adds two production rules that no fixture row tests. A mutant of each, planted by this reviewer, leaves its self-test at 0 failed (diff in `ev/own-mutants.diff`).

- **Mutant B, `tools/audit/seat/cloud_relay.sh` handoff_arm** (`if [ -z "$bonly" ] && ! grep ... review_freeze` changed to `if true && ...`): body-only moves go back under the review freeze. `bash tools/audit/seat/cloud_relay.sh --self-test` reports `305 checks, 0 failed`, rc=0 (`ev/own-B-cloud_relay.txt`). The body states this rule as a design point: "The hold applies; the review freeze does not, because the head under review does not move". It is also R4's main use case: a body fix on a clean head that holds a merge verdict, or has a reviewer dispatched (`review_freeze` prints VERDICT or REVIEW), must still be applied body-only. Under the mutant, that body is held as `handoff-held` until the PR merges or is listed in `cloud-handoff-release`. None of the body-only fixture rows sets a verdict ref or a `dispatched` entry for the head, so the guard is never exercised.
- **Mutant A, `tools/audit/seat/update_pr.sh` part (a)** (`git merge-tree --write-tree origin/main HEAD >/dev/null 2>&1 || MAIN=1` changed to `... || :`): a conflicting main is no longer merged unless GitHub says DIRTY. `bash tools/audit/seat/update_pr.sh --self-test` reports `delivery_row ... 6 checks, 0 failed` and `pr_args self-test: 166 checks, 0 failed`, rc=0 (`ev/own-A-update_pr.txt`). The DIRTY row covers only the gh-reported arm. The body's own rule is "an unread merge state counts as not DIRTY, because merge-tree is the local proof either way", yet no row has merge-tree conflict while gh reports CLEAN, UNKNOWN or unread. The existing `update_pr-1` mutant goes the other way (always merge), so it does not pin this arm.

Owed, for each: one fixture row that the mutant turns red, and a harness entry for it (`cloud_relay-46`, `update_pr-6` or the next free ids). For B: a contained head with a merge verdict ref (or a `dispatched` line) for that head, plus a new body. The body-only update runs once, and no `handoff-held` line is written. Null control: a non-contained handoff at the same head is still HELD. For A: a fixture whose origin/main conflicts with fix/v while the gh stub answers CLEAN (and one answering an error). main is merged, so the run stops on the conflict and pushes nothing.

## Findings

- Mutant B (cloud_relay.sh body-only review-freeze bypass) survives the self-test; the rule is untested (see Block). Carry: R10-FLOW-BODY-ONLY
- Mutant A (update_pr.sh merge-tree conflict arm, gh not DIRTY) survives the self-test; the rule is untested (see Block). Carry: R10-FLOW-BODY-ONLY
- The body's `## Forward-carry` says every carry it marks owed "stays in the group's own brief, `dev/programme/rosters/wave-r10-groups.json` stage R10-FLOW-BODY-ONLY". On the live roster ref, `handoff/audit-r10-roster` at `3f6dc470f` (2026-11-01 15:00 +0100), that group is `carries-open` with 5 carries, and none of them is an owed item. The orchestrator had already re-homed each one to a live group before this PR opened: P22/exit 75, the level before the serial loop, the ledger disposition and V64 to R10-RELAY-HANDOFF-ARM (not-started); V115 and `--roster-ref` to R10-BODY-CONTRACT (not-started); card 7 and card 4's prepr-reuse half to R10-OPENER-REUSE / R10-DISPATCH-AT-HANDOFF (not-started); ref_privacy's home-directory refusal to R10-SEAT-IDENTITY-GUARDS (not-started). The destinations are live, but the body names the wrong one. Re-word the Forward-carry to name the actual groups when the body is next pushed. Carry: R10-FLOW-BODY-ONLY

## Evidence

- RESULT pr-mutants: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-8 cloud_relay-9 cloud_relay-39 ... cloud_relay-45 update_pr-1 ... update_pr-5`: all 14 KILLED, `RESULT survivors=0`, rc=0 (`ev/mutants.txt`; the harness checks each unmutated step first). This matches the body's mutation proof.
- RESULT own-mutants: 2 planted, 2 survived (Block).
- CI at the head: `merge_train.py classify b283c082dd86080164a684ae52905cdbdebd387a` returned `GREEN ... pending: none red: none`, rc=0 (`ev/classify.txt`). Live check runs (MCP get_check_runs): 55 runs on one page; none concluded failure. The body's `## Red checks` names main's `tests / nightly-status`, which is green at this head, and says no check went red on the branch. That agrees with the live set.
- `git merge-tree --write-tree origin/main b283c082dd86080164a684ae52905cdbdebd387a`: exit 0, with no conflicts and no claim-file driver lines (origin/main `93d171a66`).
- VERSION, the manifest and RELEASE_NOTES.md: no change in the three-dot diff. `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to origin/main (two-dot diff empty).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc=0 (`ev/structure.txt`).
- `python3 tests/closure.py select --diff <merge-base>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` (`ev/closure-select.txt`). The body says `MODE: SCOPED`; it states no count.
- `python3 tests/throwaway_git.py --check`: 0 sites refused.
- No new production git push site. The only added `git ... push` text is the `app_push.sh` stub written into pr_args.sh's throwaway fixture origin. Body-only PATCHes through `body_patch.sh`.
- The delivery row `dev/programme/delivery/3089.md` is in the three-dot diff. `## Head` names `b283c082dd86080164a684ae52905cdbdebd387a`.
- Row-only path (no defect found): `RO=--row-only` is now set whenever HEAD's only parent is the live head. A fast-forwarded code commit would also qualify, but app_push.sh's `row_only_verdict` requires the diff to be exactly `A dev/programme/delivery/<N>.md`, so prepr still runs for code.
- pr-contract re-runs on body edits: ci.yml lists `edited` in its pull_request types.
- Roles diff since the merge base (`dev/governance/roles/`): empty.
- Body figures re-derived: the self-test tallies (cloud_relay 305/0 and pr_args 166/0 at the unmutated head, from my mutant-A run and the harness's null steps), the mutant list, structure, scope mode and throwaway_git. The architecture score `dS +0.0000 NULL` and the prepr rc=0 were not re-run (CI's arch-score check is green at this head); this is evidence, not a finding.
- Review packet: `ev/review-packet.md` (no refusals; carry_audit 1 routed).
