Six carries the s11 verifier found stranded, numbered 1-6 everywhere in this body: carry 1 field_coverage `attribution`, carry 2 the pre-bash.sh hook, carry 3 the agreement.mjs bootstrap, carry 4 the real-day `loop_cpu_ratio` budget, carry 5 the record-owed ledger kind (`RECORD-OWED:`), carry 6 the `CARRY:` arm of `review_owed`. Carries 1-3 were delivered on main before this branch (commits in Figures); carry 4 is delivered on main and measured here, with its tree comment corrected; carries 5 and 6 are built here.

Repair round 3 of fix review `blocked 95c7e604 class-open` (verdict/3241). The one finding: `review_owed` took a dispatched head as a prior even after a blocked verdict at that head. bus.sh appends every dispatch and refuses a verdict whose head has no dispatch, so a blocked verdict's head is always in the dispatch record; a PR blocked and then moved only by a clean merge of main printed an unflagged `CARRY:` in place of `REVIEW OWED`. Built in this diff: a head is a prior only while its newest verdict is a merge, or it is dispatched with no verdict yet (`newest` in `review_owed`, tools/audit/seat/ledger.py). Failing test first: 9d16d843a adds the fixture (a blocked head that is also in the dispatch record, and the null control, a dispatched head whose newest verdict is a merge); bcbdcfb37 is the fix, with plant C15 and C9/C14 re-anchored in `tools/audit/seat/r10_ledger_mutants.py`.

Rounds 1 and 2 (still in the diff): the blocked-verdict-carried defect, the unpinned predicates M3-M12 each with a mutant, `owed_unactioned.py` `key_of` keying `RECORD-OWED:` on the head12, and carry 4's `tests/replay.py` comment.

standing-tick.md (the verdict's second point): `dev/governance/roles/standing-tick.md` states the ancestor-recarry test in prose that the `CARRY:` line implements, and is policy. This is the third round for the finding, so the drafting is not done here (the rule bars a fourth round on one finding); it is carried to R10-CARRY-RESIDUE-2 below, whose destination is `dev/governance/roles/standing-tick.md`. The owner approves a policy change before merging.

files: tools/audit/seat/ledger.py, tools/audit/seat/orchestrator_tick.py, tools/audit/seat/beat_jobs.py, tools/audit/seat/beat_jobs_selftest.py, tools/audit/seat/owed_unactioned.py, tools/audit/seat/r10_ledger_mutants.py, tests/replay.py (comment only), dev/programme/delivery/3241.md

## Head

bcbdcfb377d78433b122370bb21dc29b66371cfa. Everything below was re-measured by me at this head (worktrees at bcbdcfb, at 9d16d843a and at the merge base dc0a170b671814be196a54b1c71e29449f54d6d7). origin/main has since moved to 7e8939d38cedb2976acc80a4ad7875cb545bd588; `git diff dc0a170b6 7e8939d38 --stat` touches only dev/programme/delivery/3239.md and dev/programme/rosters/wave-r10-groups.json, neither read by anything this diff changes, and `git merge-tree --write-tree origin/main bcbdcfb` is conflict-free. The head is not re-merged, so it stays the one the brief named.

## Mutation proof

The instrument is `python3 tools/audit/seat/r10_ledger_mutants.py <plant>`: one exact replacement, the owner's `--self-test`, the file restored byte for byte. Run at the head, every row is red (rc=1 with a FAIL line); my output:

| plant | mutation | owner | rc / fails | failing check |
|---|---|---|---|---|
| C15_blocked_dispatched_prior | drop the `h not in newest` exclusion (new) | ledger.py | 1 / 1 | a blocked verdict's head in the dispatch record is no prior |
| C9_blocked_prior_carries | priors from every verdict line | ledger.py | 1 / 2 | null control: a blocked verdict's head is no prior, whatever its class; and the C15 row |
| C14_dispatched_not_prior | dispatched heads dropped from the priors | ledger.py | 1 / 1 | a dispatched head is a prior too |
| C1_recarry_conflict_unchecked | drop `resolved.strip()` | ledger.py | 1 / 1 | hand-resolved conflict prints REVIEW OWED |
| C2_recarry_side_merge | drop second-parent-in-main test | ledger.py | 1 / 1 | side-branch merge prints REVIEW OWED |
| C3_record_owed_strict | `>=` to `>` | ledger.py | 1 / 1 | record PR open exactly 30 minutes |
| C11_recarry_no_ancestor | drop `--is-ancestor` guard | ledger.py | 1 / 1 | a prior that is no ancestor carries nothing |
| C12_recarry_any_commit | any single-parent commit carries | ledger.py | 1 / 2 | head plus row prints REVIEW OWED |
| C13_record_owed_unapproved | approval ignored | ledger.py | 1 / 1 | the C3 row |
| C4_tick_no_recarry | delete the `recarry` argument | orchestrator_tick.py | 1 / 1 | CARRY / RECORD-OWED row |
| C5_tick_carry_flagged | `flag=True` | orchestrator_tick.py | 1 / 1 | the same row |
| C6_tick_no_record_owed | loop iterates nothing | orchestrator_tick.py | 1 / 1 | RECORD-OWED flagged |
| T3_review_owed_silent | REVIEW OWED loop body `pass` | orchestrator_tick.py | 1 / 6 | the round-1 four and more |
| C7_beat_family_no_record | drop from `FAMILY` | beat_jobs.py | 1 / 1 | printers' literals |
| C8_owed_family_no_record | drop from `FAMILY` | owed_unactioned.py | 1 / 1 | keyed on head12 |
| C10_record_owed_unkeyed | delete the `key_of` arm | owed_unactioned.py | 1 / 1 | the C8 row |

`python3 tools/audit/seat/r10_ledger_mutants.py` printed `plants: 63, without a FAIL line: none` (rc=0). `python3 tools/audit/seat/r10_ledger_mutants.py --null` printed `rc=0 fails=0` for beat_jobs.py, bus.sh, cloud_relay.sh, ledger.py, orchestrator_tick.py and owed_unactioned.py.

Failing test first, re-run by me: `ledger.py --self-test` at 9d16d843a (the parent of the fix, test added, code of 95c7e604) printed `FAIL a blocked verdict's head in the dispatch record is no prior` and `ledger self-test: 91 checks, 1 failed`; at bcbdcfb it prints `ledger self-test: 91 checks, 0 failed`.

## Null control

At the merge base dc0a170b671814be196a54b1c71e29449f54d6d7, the unmodified tree (my run):

- `ledger.py --self-test`: 77 checks, 0 failed;
- `orchestrator_tick.py --self-test`: 272 checks, 0 failed;
- `owed_unactioned.py --self-test`: 46 checks, 0 failed;
- `beat_jobs.py --self-test`: 107 checks, 0 failed;
- `r10_ledger_mutants.py --self-test`: 135 checks, 0 failed.

`git grep -cE "CARRY:|RECORD-OWED|record_owed|git_recarry" dc0a170b671814be196a54b1c71e29449f54d6d7 -- tools/audit/seat/ledger.py || echo NONE` printed NONE: carries 5 and 6 are absent at the base. The round-3 row's own null control is in the tree: a dispatched head whose newest verdict is a merge (alone, or after an earlier blocked one) still carries, beside the rows where a blocked newest verdict does not.

## Figures

- `python3 tools/audit/seat/ledger.py --self-test`: 91 checks, 0 failed.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 275 checks, 0 failed.
- `python3 tools/audit/seat/owed_unactioned.py --self-test`: 47 checks, 0 failed.
- `python3 tools/audit/seat/beat_jobs.py --self-test`: 107 checks, 0 failed.
- `python3 tools/audit/seat/r10_ledger_mutants.py --self-test`: 180 checks, 0 failed.
- Scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 4 script(s) run, 29 scoped out`; scope.run names tests/debug_collect.py, tests/doc_claims.py, tests/entities.py, tests/features.py. Run with `PYTHONPATH=tests/hastub`: ALL 162 DEBUG COLLECT CHECKS PASSED, ALL 296 checks PASSED, ALL 2632 ENTITY CHECKS PASSED, ALL 4876 FEATURE CHECKS PASSED; run_always: claims hygiene: origin/main ok, ALL 118 closure shrink pins PASSED, layout self-test: ok, ALL 112 HARNESS HEADER CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `r10_ledger_mutants.py` is not a gate script (it sits in `inert_reads` of tests/entities.py), so no closure change; CI runs it in `governance / instrument-self-tests`.
- Carry 4: tests/replay.py's budget 0.249 and its comment, unchanged since round 2; the readings in the comment (0.128 ref30, 0.189 ref24, 0.1339, 0.1418, 0.1433) are from CI logs of the jobs the comment cites, read in round 2 and not re-read in round 3. The residual margin 0.128 / 0.1245 = 1.028.
- Carry 1 delivered: df9bfd301. Carry 2 delivered: 408644f7f. Carry 3 delivered: 82f333b9c.

## Red checks

Previous PR head 95c7e60422baf9333ae6e25fad972865698a4215: `python3 tools/audit/seat/merge_train.py classify 95c7e60422baf9333ae6e25fad972865698a4215 --pr 3241` printed `GREEN 95c7e60422baf9333ae6e25fad972865698a4215 pending: none red: none`. I also read the check-runs of #3241 (68 total, page 2 empty): none concluded `failure`, including `governance / instrument-self-tests`, `pr-contract / pr-contract` and `gate`, all `success`. No red concluded at 95c7e604, so none is owed an answer.

This head bcbdcfb377d78433b122370bb21dc29b66371cfa: `merge_train.py classify bcbdcfb377d78433b122370bb21dc29b66371cfa --pr 3241` printed `WAIT bcbdcfb377d78433b122370bb21dc29b66371cfa pending: gate red: none`. No check has concluded red yet.

Earlier head e81028cc (round 1's reds, still answered): `governance / instrument-self-tests`, root-cause-detectable: the diff moved the call text `T3_review_owed_silent` anchors on; the cheaper detector is `python3 tools/audit/seat/r10_ledger_mutants.py --self-test` (seconds, no standing cost), run before this handoff (Figures). `pr-contract / pr-contract`, derived: it refused a red the body did not name; answered by this section. `gate`, derived from those two.

## Forward-carry

- `dev/governance/roles/standing-tick.md` should name the `CARRY:` line beside its ancestor-recarry test; a policy edit, owner approval before merging. Carry: R10-CARRY-RESIDUE-2

## Friction

none
