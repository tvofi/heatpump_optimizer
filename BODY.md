Part 1 of R10-TICK-LEVELS (carries 0-6, 8; carry 7, the topic-family barrier, and carries 9-12 are later parts), repair round 2 after the fix review's `blocked` verdict at d7e67e0d786c73315e769345cb6fbefba1c5434d. The tick's PR levels in one seam, `tools/audit/seat/orchestrator_tick.py`. Part of #201.

Carry 0 is the umbrella for 1-5 and 8 and needed no code of its own. APPROVAL-OWED (8922cbf97) and REVIEW STALLED (3a15e84a4) were already delivered and are not rebuilt.

What changed since the first round: `REVIEW OWED` skips the record branch (carry 1). A new `owed_levels` pass puts every open PR the pass can read in exactly one bucket (train, verdict-pending, fixer-round, waiting-on #M, verdicted, review-owed, owed, unreadable) from data the pass already reads, plus one `ls-remote` over the handoff refs and no new GitHub call, and prints one `OWED <kind> #N <head12> <reason>` line per owed PR (carries 2-6). Carry-8 defects are fixed (P82 gate-race line, a reviewer's `merge_train.py --self-test` no longer a second train, a null `started_at` is stuck). Repairs this round, by the review's findings:
- Block 1: the T3 seat mutant's anchor in `tools/audit/seat/r10_ledger_mutants.py` followed the `lg.review_owed(...)` call's new tail (the `getattr(rr, "RECORD_BRANCH", None)):` line and the `self.line` under it), so it plants exactly once and is killed.
- Block 2: fixtures pin the null controls and the survivors the review listed (below).
- O3: a failed git read in the blocked arm (`_handoff_newer` returning None) is now bucket `unreadable`, printed as `UNREADABLE: owed buckets (#N: ...)`, never `OWED fixer-round`.
- O4: the claim is narrowed. Every open PR the pass can read is in exactly one bucket; a draft, a PR with no head, the record branch and a PR whose comments were not read are counted on the count line's `; not bucketed: ...` tail instead, and a test pins the line.
- Class-open (ci_predict `self_test_hosts`): a host is a script whose source runs the self-test near the file by the `--self-test` flag or by a quoted `"self-test"` argv element (the subcommand spelling tests/entities.py uses for tests/lane_skip.py); comments and `self_test` table keys are not hosts. Each pair the rule still drops is classified below.

## Head

36924c5c7a9aa58c53977623f146c6b4924047ac (code head, `origin/main` merged in at d7582ed404a87603bd02fefda610d7ebbe4181e1; `tools/pr/prepr.sh` ran once at this head, after that merge). The first-round head c9993ab55cbbac35cc440713d61ad9cc30b2cfa6 is its ancestor, so `handoff/r10-tick-levels-p1` moves by fast-forward.

## Approval

`dev/governance/roles/standing-dispatch.md` is unchanged this round: still one added sentence (a `record/autofix` PR is never dispatched a reviewer), 38 lines against a 39 cap and 505 tokens against 509 (`node tools/policy/policy_lint.mjs --budgets`). Policy: it merges on tvofi's approving review or under mandate 6329234399. No budget is raised.

## Mutation proof

Driver `ev/mutants_driver.py` of the review (extended with M33-M36 below), each mutant applied to one predicate, `python3 tools/audit/seat/orchestrator_tick.py --self-test` (or `tools/pr/ci_predict.py --self-test`) run, then restored. At the head, with the new fixtures, each of the review's survivors is red:
- M06 `return "train"` deleted: `null: a DIRTY, red PR in train ...`
- M10 blocked arm's newer-handoff exemption: `blocked arm: a handoff tip newer than the verdict ...`
- M11 `verdicted`: `null: a DIRTY, red PR with a merge verdict at its head ...`
- M12 `verdict-pending`: `null: ... on the dispatch record is verdict-pending ...`
- M13 waiting-on file overlap, M14 waiting-on after-edge: `null: ... sharing a file ...` and `null: ... whose group is after an open group ...`
- M15 the DIRTY arm (anchor widened to the arm's two lines; the review's one-line pattern matched twice): 6 checks red
- M21 BODY-AHEAD's `in_head` conjunct: `BODY-AHEAD: a code handoff that is not in the head ...`
- M24 FIRE-OWED's `FIRE_GRACE_MIN` grace: `carry 5 FIRE-OWED ...` (a payload younger than the grace prints nothing)
- M27 `self.owed_levels(S, prs)` deleted from the PRS pass: `a tick's PRS pass runs the level ...` (drives `prs()`, not `owed_levels`)
- M29 the record-branch skip in `owed_levels`: `O4: the count line names what it leaves out ...`
- M30 critical-path ordering: `the critical-path group's OWED line prints before ...`
- M33 (new) the O3 `newer is None` arm deleted: `O3: an unreadable handoff ref is UNREADABLE ...`
- M34 (new) the `not bucketed` tail deleted: the O4 check
- M35 (new) the quoted-`"self-test"` alternative dropped from the host rule: `ci_predict self-test: 1 failed` (the lane_skip-shape case)
- M36 (new) the old `self[-_]test` word restored: `ci_predict self-test: 3 failed`
- T3 itself: `python3 tools/audit/seat/r10_ledger_mutants.py --self-test` is `135 checks, 0 failed` (it was 1 failed); the other `r10_*_mutants.py --self-test` whose plant target this diff changes: none (only the ledger one plants in orchestrator_tick.py or ledger.py; the roster_ops, mandate_guard and stamp_round ones run 0 failed unchanged; deeplink and roster_sync take no `--self-test` flag and plant elsewhere).
The review's other mutants (M01-M05, M07-M09, M16-M20, M22, M23, M25, M26, M28, M31) stay red as before (review `ev/mutants.txt`).

## Null control

Unmutated tree: `orchestrator_tick self-test: 272 checks, 0 failed` (261 at the reviewed head; 244 at the base). New nulls: a DIRTY, red PR with a queue verdict at its head and no merge verdict prints no OWED and counts `train 1`; with a merge verdict, `verdicted 1`; on the dispatch record, `verdict-pending 1` (off it, one `OWED dirty` line); sharing a file with a lower open PR, or in a group after an open group, `waiting-on 1` (disjoint files, or no open PR in that group, one `OWED dirty` line); a blocked verdict 9 h old beside a handoff tip 30 min old is `fixer-round 1`, beside one 600 min old, one `OWED fixer-round` line; a failed handoff `ls-remote` is `unreadable 1` and an UNREADABLE line naming the PR. A mixed board of a clean PR, the record PR, a draft and a PR with unread comments prints `buckets: review-owed 1; not bucketed: comments unread 1, draft 1, record branch 1` and no OWED line. `ci_predict self-test`: a host that runs the file by `--self-test` or by a quoted `"self-test"` element is predicted; a comment saying "self-test" and a `('<file>', 'self_test')` table key are not.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 272 checks, 0 failed (rule: the count of `check(...)` arms plus the file's other sections the instrument prints).
- `python3 tools/audit/seat/r10_ledger_mutants.py --self-test`: 135 checks, 0 failed.
- `python3 tools/pr/ci_predict.py --self-test`: 0 failed.
- `python3 /tmp/ev/hosts_diff2.py .` (the review's harness, extended to print each dropped pair's nearest self-test line and whether the head kept it): old rule 24 host pairs, the head's rule 14; `tests/lane_skip.py <- tests/entities.py` is KEPT. The 10 pairs lost are all prose or a table: dev/audit/rounds/round3/D6/claims.py and round4/D6/claims.py <- tests/harness_headers.py (comments naming claims.py, an instrument-self-tests remark), tests/hastub/homeassistant/const.py <- tests/entities.py (a comment naming homeassistant/const.py), tests/nightly_status.py, tools/audit/archscore/gate.py and tools/ci/gate.py <- tests/entities.py (a string at 29525-29529 and CI-job text; entities.py only checks the CI invocation string `python -I -S tests/nightly_status.py`), tests/throwaway_git.py, tools/audit/judge_batch.py and tools/coverage/coverage_tree.sh <- tests/entities.py (the `_SHELL_NOT_A_STEP` table at 29036-29040, whose `("tests/throwaway_git.py", "self_test")` key names a function; entities.py imports `throwaway_git_env` and `judge_batch.run`, never a self-test), tools/audit/seat/ledger.py <- tests/entities.py (the `ledger.py landed` string fixture, the first-round false host).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; `node tools/policy/policy_lint.mjs`: 0 errors; `--budgets`: standing-dispatch.md within its caps.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: MODE: SCOPED -- 2 script(s) run.
- Toolchain: numpy 2.5.4, scipy 1.18.1 against tests/requirements-ci.txt (cloud-setup --check OK); no golden is touched, CI stays the authority.

## Red checks

At the reviewed head d7e67e0d786c73315e769345cb6fbefba1c5434d, the whole check-run set (55 runs, one page):
- governance / instrument-self-tests (job 126655674435): this diff's own. Cause: the first-round diff rewrote the `lg.review_owed(...)` call site that the T3 seat mutant in r10_ledger_mutants.py anchored on (`FAIL T3_review_owed_silent: anchor occurs once in tools/audit/seat/orchestrator_tick.py`, then `r10_ledger_mutants self-test: 135 checks, 1 failed`), repaired in this round. The cheaper detector exists: `python3 tools/audit/seat/r10_ledger_mutants.py --self-test`, about 2 s, which `tools/pr/prepr.sh` and `ci_predict` do not run for a changed plant target; its standing cost is that 2 s per diff touching a plant target. A second instance (#2865, #3200) is routed to R10-FRICTION-RECORDS, not built here.
- gate (runs 126678757606 and 126677715719) and pr-contract / pr-contract (126678318527 and 126677286569): downstream of the one red above (the aggregate gate, and the contract's own refusal naming it); no cause of their own.
- tests / nightly-status (job 126655674359): main's, not this diff's (this diff reaches nothing nightly_status reads; the review reached the same conclusion).
Every other concluded run at that head is success or skipped. The check-runs at this round's head do not exist yet; the next run's set is the proof.

## Forward-carry

none

## Interpretation notes

- Carry 5's last clause (reconcile the dispatch seat's fired-session ledger against the cloud run list, RETURN-MISSING) is not built: no cloud run list source exists in the tree; it is already the roster group's own carry text.
- The FIRED ledger and payload directory have no tree producer; the tick reads them through `--fired-log` and `--payload-dir`, FIRED lines as `<UTC stamp> FIRED <text>`.
- Carry 2's "waiting-on" reads roster after-edges and file overlap with a lower-numbered open PR (delivery rows and claim files excluded).
- Carry 4's "split" is recognised only as a `## Re-cut` section in the body.
- The recurrence finding (a seat mutant's anchor red twice) is R10-FRICTION-RECORDS's; nothing built here.

## Friction

none
