Part 1 of R10-TICK-LEVELS (carries 0-6, 8; carry 7, the topic-family barrier, and carries 9-12 are later parts). The tick's PR levels in one seam, `tools/audit/seat/orchestrator_tick.py`. Part of #201.

Carry 0 is the umbrella for 1-5 and 8 and needed no code of its own. APPROVAL-OWED (8922cbf97) and REVIEW STALLED (3a15e84a4) were already delivered and are not rebuilt.

What changed: `REVIEW OWED` skips the record branch (carry 1). A new `owed_levels` pass puts every open PR in exactly one bucket (train, verdict-pending, fixer-round, waiting-on #M, verdicted, review-owed, owed) from data the pass already reads, plus one `ls-remote` over the handoff refs and no new GitHub call, and prints one `OWED <kind> #N <head12> <reason>` line per owed PR (carries 2-6). The tick's carry-8 defects are fixed: the P82 gate-race line, a reviewer's `merge_train.py --self-test` no longer read as a second train, and a null `started_at` is stuck, with the 2x threshold now one constant.

## Head

c9993ab55cbbac35cc440713d61ad9cc30b2cfa6 (measured at; `origin/main` is c3a279e3252a, unmoved since the branch was cut, so `tools/pr/prepr.sh` ran once, at this head, and is clean: rc=0, the ci predict arm and the closures arm ok).

The earlier head added `tools/audit/seat/open_pr.sh`, `tools/pr/app_approve.sh` and `tools/audit/seat/cloud_relay.sh` to `INERT_EXCEPT` on the premise that `tests/entities.py` runs ledger.py's self-test. It does not: `derive_closures.sh --single tests/entities.py` (recorded in a kept out-dir) shows none of the three in its record, ledger.py's self-test runs only from governance.yml, and `tests/entities.py` then fails "every tracked file is either measured or deliberately classified" for the two it names. Cause of the predicted reds: `ci_predict.self_test_hosts` took `tests/entities.py` for a host because the prose "self-tests" sat twelve lines from a `ledger.py landed` string fixture (line 28492). Repairs: the INERT_EXCEPT entries are reverted (the files are INERT again; `tests/closures.json` is byte-identical to main), and `self_test_hosts` now requires the `--self-test` flag near the file, not the word. ledger.py's self-test is not narrowed.

Mutation proof for that change: with the old regex restored, `python3 tools/pr/ci_predict.py --self-test` goes red on two cases (the INERT-read and the UNDER-SCOPED ones, because the new harness_headers fixture line carries the prose "the self-tests run elsewhere" in the window); with the fix, `ci_predict self-test: 0 failed`. Null control: the hosts that really name `--self-test` near the file are still predicted.

Not established: that recording (and a direct `tests/entities.py` run at the INERT_EXCEPT head) also printed `FAIL a3:roster` (one entity registered against the committed roster), which the d945dddaa run below did not. I did not rerun `tests/entities.py` at this head, and no recording was merged; CI's scoped closures job runs it.

## Approval

`dev/governance/roles/standing-dispatch.md` gains one sentence (a `record/autofix` PR is never dispatched a reviewer) and loses a measurement parenthesis to hold its cap. Policy: it merges on tvofi's approving review or under mandate 6329234399.

## Mutation proof

Each production predicate was mutated in turn and `python3 tools/audit/seat/orchestrator_tick.py --self-test` run (driver kept in scratch). Each mutant turned a named check red:
- drop the record-branch skip in `ledger.review_owed`: `REVIEW OWED: P322 ...`
- `RECUT_BLOCKED` 4, or counting `Fix review: ` of any kind: `OWED buckets: card 8 ...`
- drop the payload-file key in `_fire_names`: `OWED buckets: carry 6 arm (a)`
- drop the PARK arm: `OWED buckets: P279 ...`
- drop the blocked-at-head arm, the DIRTY arm, the BODY-AHEAD arm, the FIRE-OWED arm: the matching `OWED buckets` checks
- drop the gate-race arm: `P82 gate red beside a running sibling`
- null `started_at` returning False; dropping the `--self-test` exclusion: `carry 8 train self-test`

## Null control

Unmutated tree: `orchestrator_tick self-test: 261 checks, 0 failed` (251 before the OWED buckets fixtures; 244 at the base). Nulls inside the fixtures: a fix/ PR beside the record PR still prints REVIEW OWED; a blocked verdict 1 h old prints nothing; two blocked verdicts, three merges, or a recorded `## Re-cut` print nothing; a PARK before the last STARTED stays in `train`; a handoff-wip move or a payload-file FIRED line inside the window is a seat on a red PR, while a fire 9 h old is not; an older body ref and a FIRED line print no BODY-AHEAD; a FIRED payload prints no FIRE-OWED; gate red with nothing running stays NOT REVIEWABLE.

## Figures

- `python3 tools/audit/seat/orchestrator_tick.py --self-test` prints the check counts above.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED -- 2 script(s) run (tests/doc_claims.py, tests/entities.py).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget raised or re-recorded.
- `node tools/policy/policy_lint.mjs`: TOTAL: 0 error(s); `--budgets` within caps (standing-dispatch.md held at its 39-line cap).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at d945dddaa (the base of this repair): rc=0 (its template arm ran red at an earlier head because standing-dispatch.md was over its policy_lint file cap; fixed in the last commit).

## Red checks

none

## Forward-carry

none

## Interpretation notes

The unbuilt clause (carry 5's RETURN-MISSING reconcile) is already the roster group's own carry text, so it needs no new destination; this seat writes no roster branch, so nothing below is landed there.

- Carry 5's last clause (reconcile the dispatch seat's fired-session ledger each sweep against the cloud run list, RETURN-MISSING) is not built: no cloud run list source exists in the tree.
- The FIRED ledger and payload directory have no tree producer (`grep -rn FIRED tools/audit/seat` found none); the tick reads them through `--fired-log` and `--payload-dir`, FIRED lines as `<UTC stamp> FIRED <text>` (the stamp optional). The line format is inferred from the carry's text and needs the dispatch seat to write it.
- Carry 2's "waiting-on" reads roster after-edges and file overlap with a lower-numbered open PR (delivery rows and claim files excluded); roster_lib has no hot-file notion, so overlap is the PRs' own three-dot files.
- Carry 4's "split" is recognised only as a `## Re-cut` section in the body.

## Friction

none
