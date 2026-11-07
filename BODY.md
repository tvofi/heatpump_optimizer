Six carries the s11 verifier found stranded, numbered 1-6 everywhere in this body: carry 1 field_coverage `attribution`, carry 2 the pre-bash.sh hook, carry 3 the agreement.mjs bootstrap, carry 4 the real-day `loop_cpu_ratio` budget, carry 5 the record-owed ledger kind (`RECORD-OWED:`), carry 6 the `CARRY:` arm of `review_owed`. Carries 1-3 were delivered on main before this branch (commits in Figures); carry 4 is delivered on main and measured here, with its tree comment corrected; carries 5 and 6 are built here.

This head is a merge resolution: origin/main f2a015142714383722bf49d7ab20d8398ec9674c merged into the PR head 87b00d3ec3779e826faac670e624062401356d5d (merge, no re-cut or rebase), plus one comment commit. The reviewed code of round 3 is otherwise unchanged. Resolution, per file:

- `tools/audit/seat/r10_ledger_mutants.py` (the one textual conflict, in the `T3_review_owed_silent` / `T4_no_escalation` entries). Against the merge base each side changed exactly one of the two entries: the branch re-anchored T3 on its new `lg.git_recarry(...)` call and `flag=not text.startswith("CARRY:")`; main re-anchored T4 on its new `aging, group_of, last_open)` argument. The branch's T4 and main's T3 are byte-identical to the base. Resolved as the union: the branch's T3 and main's T4. Both anchors occur once in the merged `orchestrator_tick.py` (lines 758-759 and 1075-1076), which `--self-test` checks.
- `tests/replay.py`, `tools/audit/seat/ledger.py`, `tools/audit/seat/orchestrator_tick.py`: auto-merged by git, read merged. One semantic conflict, in `tests/replay.py`: the branch's carry-4 sentence said the residual margin "is" 2.8 % over the floor 0.1245 (half the 0.249 budget), and main's R10-REPLAY-COST-BUDGET round 3, ten lines below it, re-derives that budget to 0.2154. A textual union kept a false present-tense claim, so 0b1a4bb6f keeps every reading and figure of the sentence and states the margin in the past tense, against the 0.249 budget of that recording, naming round 3 as its re-derivation. No code line changed.

How the union was verified: for each of the four files, every line either side added against the merge base (`git diff <base> <side> -- <file>`, `+` lines) was searched for verbatim (`grep -qxF`) in the merged file; none was missing. The only lines dropped are the base's T3 and T4 anchors, each replaced by one side.

Repair round 3 of fix review `blocked 95c7e604 class-open` (verdict/3241). The one finding: `review_owed` took a dispatched head as a prior even after a blocked verdict at that head. bus.sh appends every dispatch and refuses a verdict whose head has no dispatch, so a blocked verdict's head is always in the dispatch record; a PR blocked and then moved only by a clean merge of main printed an unflagged `CARRY:` in place of `REVIEW OWED`. Built in this diff: a head is a prior only while its newest verdict is a merge, or it is dispatched with no verdict yet (`newest` in `review_owed`, tools/audit/seat/ledger.py). Failing test first: 9d16d843a adds the fixture (a blocked head that is also in the dispatch record, and the null control, a dispatched head whose newest verdict is a merge); bcbdcfb37 is the fix, with plant C15 and C9/C14 re-anchored in `tools/audit/seat/r10_ledger_mutants.py`.

Rounds 1 and 2 (still in the diff): the blocked-verdict-carried defect, the unpinned predicates M3-M12 each with a mutant, `owed_unactioned.py` `key_of` keying `RECORD-OWED:` on the head12, and carry 4's `tests/replay.py` comment.

standing-tick.md (the verdict's second point): `dev/governance/roles/standing-tick.md` states the ancestor-recarry test in prose that the `CARRY:` line implements, and is policy. This is the third round for the finding, so the drafting is not done here (the rule bars a fourth round on one finding); it is carried to R10-CARRY-RESIDUE-2 below, whose destination is `dev/governance/roles/standing-tick.md`. The owner approves a policy change before merging.

files: tools/audit/seat/ledger.py, tools/audit/seat/orchestrator_tick.py, tools/audit/seat/beat_jobs.py, tools/audit/seat/beat_jobs_selftest.py, tools/audit/seat/owed_unactioned.py, tools/audit/seat/r10_ledger_mutants.py, tests/replay.py (comment only), dev/programme/delivery/3241.md

## Head

`0b1a4bb6feb941974fc78d1402d5f8f2a23c739e`: 49feb621c merges origin/main f2a0151 into the PR head 87b00d3 with the resolution above, and 0b1a4bb6f is the `tests/replay.py` comment commit. Everything under Figures and Mutation proof was measured by me at this head, or at 49feb621c where it says so (0b1a4bb6f changes only a comment in `tests/replay.py`).

Earlier heads: `87b00d3ec3779e826faac670e624062401356d5d`, `1d5a5ce7f8aafcb3e68ea06df1c6519e11ab8c04` and `bb33e680731fed34616e4e940927fff0aa0d82fa` each merged main into the previous head automatically, with no resolution; `de1a371e2ed49c742ef690d605fbc8e605b853f3` was set without a push; `bcbdcfb377d78433b122370bb21dc29b66371cfa` is the round-3 fix.

## Mutation proof

The instrument is `python3 tools/audit/seat/r10_ledger_mutants.py <plant>`: one exact replacement, the owner's `--self-test`, the file restored byte for byte. The resolution delta's own plants, run by me at 49feb621c:

| plant | mutation | owner | rc / fails |
|---|---|---|---|
| T3_review_owed_silent | REVIEW OWED loop body `pass` (branch's anchor) | orchestrator_tick.py | 1 / 6 |
| T4_no_escalation | escalation loop body `pass` (main's `last_open` anchor) | orchestrator_tick.py | 1 / 4 |
| C4_tick_no_recarry | delete the `recarry` argument | orchestrator_tick.py | 1 / 1 |
| C5_tick_carry_flagged | `flag=True` | orchestrator_tick.py | 1 / 1 |

The whole sweep, `python3 tools/audit/seat/r10_ledger_mutants.py` at 49feb621c, printed `plants: 68, without a FAIL line: none` (rc=0). The round-3 table of the branch's plants stands: C15_blocked_dispatched_prior, C9_blocked_prior_carries, C14_dispatched_not_prior, C1-C8, C10-C13 are each in that sweep and each red.

Failing test first, from round 3 and not re-run here: `ledger.py --self-test` at 9d16d843a printed `FAIL a blocked verdict's head in the dispatch record is no prior`; at bcbdcfb it printed 0 failed.

## Null control

`python3 tools/audit/seat/r10_ledger_mutants.py --null` at 49feb621c printed `rc=0 fails=0` for beat_jobs.py, bus.sh, cloud_relay.sh, ledger.py, orchestrator_tick.py and owed_unactioned.py: every owner self-test is green with no plant, after the merge.

From round 3, at the merge base dc0a170b671814be196a54b1c71e29449f54d6d7: `git grep -cE "CARRY:|RECORD-OWED|record_owed|git_recarry" dc0a170b671814be196a54b1c71e29449f54d6d7 -- tools/audit/seat/ledger.py || echo NONE` printed NONE: carries 5 and 6 are absent at the base.

## Figures

- `python3 tools/audit/seat/r10_ledger_mutants.py --self-test` (49feb621c): `r10_ledger_mutants self-test: 194 checks, 0 failed`, so every anchor, the T3/T4 union included, occurs exactly once.
- `python3 -I tests/replay.py` (49feb621c): `ALL 197 replay checks PASSED`; rerun at 0b1a4bb6f: `ALL 197 replay checks PASSED`.
- Scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 4 script(s) run, 29 scoped out`; scope.run names tests/debug_collect.py, tests/doc_claims.py, tests/entities.py, tests/features.py. Run with `PYTHONPATH=tests/hastub`: ALL 162 DEBUG COLLECT CHECKS PASSED, ALL 296 checks PASSED, ALL 2640 ENTITY CHECKS PASSED, ALL 4876 FEATURE CHECKS PASSED. `tests/doc_claims.py` re-run at 0b1a4bb6f: ALL 296 checks PASSED.
- `python3 tests/structure.py` at 0b1a4bb6f: STRUCTURE RATCHET PASSED. No budget is raised.
- `git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` returned 0: both claim files are byte-identical to origin/main.
- Toolchain: `bash tools/audit/seat/cloud-setup.sh --check` printed OK; numpy 2.5.4 and scipy 1.18.1, equal to tests/requirements-ci.txt.
- `r10_ledger_mutants.py` is not a gate script (it sits in `inert_reads` of tests/entities.py), so no closure change; CI runs it in `governance / instrument-self-tests`.
- Carry 1 delivered: df9bfd301. Carry 2 delivered: 408644f7f. Carry 3 delivered: 82f333b9c.

## Red checks

PR head 87b00d3ec3779e826faac670e624062401356d5d, from its 55 check-runs (I read the whole set):

- `tests / replay` (job 128096022229): `5 of 194 replay checks FAILED`: `owner-2026-10-30-away.json: cycle_cost [loop_cpu_ratio 0.124: budget 0.249 cannot see a 2x cycle; re-record 0.1754]` and four `synthetic-dhw-only.json` cycle_cost checks, each `runner class unknown: ref_ms 39.67 lies in no band of COST_RUNNER_CLASSES`. Both are budgets that main's R10-REPLAY-COST-BUDGET round 3 has since re-derived (owner `loop_cpu_ratio` 0.2154, runner classes by job ruler), and that main version is in this merge; at 49feb621c the lane is `ALL 197 replay checks PASSED` (Figures). Root cause: a real-day CPU reading on a CI runner that no cheaper detector can take; the ruler is the lane itself. This diff changed no budget, only the comment that cited 0.249, now corrected (above).
- `tests / nightly-status` (job 128096019326): concluded red in 12 s. I read only the tail of its log, which holds the post-job cleanup. It reports the nightly workflow's state, which this diff does not change; I did not establish its cause.
- `pr-contract / pr-contract` (job 128103587958): derived. The body named heads up to bcbdcfb and none of these reds. Its cheaper detector is `tools/pr/prepr.sh --body-check` (seconds), run on this body before the handoff.
- `gate` (jobs 128104226309 and 128079493180): derived from the reds above.

`governance / instrument-self-tests` concluded `success` at 87b00d3, so R10-HOTFIX-SELFTEST-TIMEOUT is not owed here. `tools/pr/prepr.sh` could not read code-scanning alerts from this seat (HTTP 403 on code-scanning/analyses), so open alerts are left to `pr-contract`.

origin/main is f2a015142714383722bf49d7ab20d8398ec9674c, unmoved since my `tools/pr/prepr.sh` run (rc=0 at 0b1a4bb6f), so a second run was not needed.

## Forward-carry

- `dev/governance/roles/standing-tick.md` should name the `CARRY:` line beside its ancestor-recarry test; a policy edit, owner approval before merging. Carry: R10-CARRY-RESIDUE-2

## Friction

none
