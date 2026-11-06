Six carries the s11 verifier found stranded, numbered 1-6 everywhere in this body: carry 1 field_coverage `attribution`, carry 2 the pre-bash.sh hook, carry 3 the agreement.mjs bootstrap, carry 4 the real-day `loop_cpu_ratio` budget, carry 5 the record-owed ledger kind (`RECORD-OWED:`), carry 6 the `CARRY:` arm of `review_owed`. Carries 1-3 were delivered on main before this branch (commits in Figures); carry 4 is delivered on main and measured here, with its tree comment corrected; carries 5 and 6 are built here.

Repair round 2 of fix review `blocked e81028cc mutation-vacuous`. The owner's ruling is that round 10 defers no defect, so every finding of that verdict is built in this diff:

- a blocked verdict carried: `review_owed` took every verdict line's head as a prior. Priors are now the heads of `merge` verdicts and the dispatched heads only (fix-review.md step 12, orchestrator.md section 11);
- the predicates and wiring the verdict found unpinned (its M3, M4, M5, M7, M8, M9, M10, M11) each have a fixture that fails when the predicate is mutated. The plants sit in the ledger's in-tree mutant harness `tools/audit/seat/r10_ledger_mutants.py`, so a later seat can rerun them;
- the harness's own `T3_review_owed_silent` is re-anchored on the new call text, which is the red `governance / instrument-self-tests` of round 1;
- carry 4's comment in `tests/replay.py` claimed the loop spread was "0.137-0.227 ... edges 9-10 % inside". It now states the CI readings and the residual margin.

Found while building and fixed here: `owed_unactioned.py` had `RECORD-OWED:` in its `FAMILY` but no arm in `key_of`. Every board carrying a `RECORD-OWED` line therefore raised `Unreadable` ("an owed line names no topic or pull request"). It now keys `#<N>` on the head12 and leaves out the growing minutes, as `REVIEW STALLED` does.

Not edited, for the owner: `dev/governance/roles/standing-tick.md` states the ancestor-recarry test in prose and is policy; it could name the `CARRY:` line.

files: tools/audit/seat/ledger.py, tools/audit/seat/orchestrator_tick.py, tools/audit/seat/beat_jobs.py, tools/audit/seat/beat_jobs_selftest.py, tools/audit/seat/owed_unactioned.py, tools/audit/seat/r10_ledger_mutants.py, tests/replay.py (comment only), dev/programme/delivery/3241.md

## Head

725767534e36cc9f14e7d532e940bd17437a352b. Everything below was measured at this code head, merged with origin/main at dc0a170b671814be196a54b1c71e29449f54d6d7 (the PR's merge base) at 2026-11-06T08:42Z. origin/main had moved past round 1's base 9315526f; this branch merged it (never rebased) before any measurement, and origin/main was still dc0a170b671814be196a54b1c71e29449f54d6d7 when prepr.sh ran.

## Mutation proof

The instrument is `python3 tools/audit/seat/r10_ledger_mutants.py <plant>`. It applies one exact replacement, runs the owner script's `--self-test`, restores the file byte for byte, and refuses to start on a dirty target. Run at the head, every row is red at the mutant (rc=1 with a FAIL line) and green on the null control (`--null`: every owner rc=0 fails=0):

| plant | the verdict's id | mutation | owner self-test | failing check at the mutant |
|---|---|---|---|---|
| C1_recarry_conflict_unchecked | M3 | drop `resolved.strip()` in `git_recarry` | ledger.py | a main merge with a hand-resolved conflict prints REVIEW OWED |
| C2_recarry_side_merge | M4 | drop the second-parent-in-main test | ledger.py | a clean merge of a side branch prints REVIEW OWED |
| C3_record_owed_strict | M5 | `age >= minutes` to `>` | ledger.py | an approved record PR open 31 or exactly 30 minutes opens an entry; ... |
| C4_tick_no_recarry | M7 | delete the `recarry` argument at the tick's `review_owed` call | orchestrator_tick.py | CARRY and RECORD-OWED: a verdicted head plus one main merge prints CARRY, unflagged, and no REVIEW OWED |
| C5_tick_carry_flagged | M8 | `flag=not text.startswith("CARRY:")` to `flag=True` | orchestrator_tick.py | the same row |
| C6_tick_no_record_owed | M9 | the tick's `record_owed` loop iterates nothing | orchestrator_tick.py | CARRY and RECORD-OWED: an approved record PR open 40 minutes prints RECORD-OWED, flagged |
| C7_beat_family_no_record | M10 | drop `RECORD-OWED:` from beat_jobs.py `FAMILY` | beat_jobs.py | every family literal is one the board's printers print |
| C8_owed_family_no_record | M11 | drop `RECORD-OWED:` from owed_unactioned.py `FAMILY` | owed_unactioned.py | RECORD-OWED: keyed #3235 on its head12, unactioned on the second sweep as its minutes grow |
| C9_blocked_prior_carries | the blocked-carry defect | priors from every verdict line again | ledger.py | null control: a blocked verdict's head is no prior, whatever its class |
| C10_record_owed_unkeyed | the key_of defect | delete the `RECORD-OWED` arm of `key_of` | owed_unactioned.py | the C8 row |
| C11_recarry_no_ancestor | M1 | drop the `--is-ancestor prior head` guard | ledger.py | null control: a prior that is no ancestor of the head carries nothing |
| C12_recarry_any_commit | M2 | any single-parent commit carries | ledger.py | a head plus its row and another file prints REVIEW OWED (null); a code commit on top of a main merge prints REVIEW OWED (null) |
| C13_record_owed_unapproved | M6 | approval ignored | ledger.py | the C3 row |
| C14_dispatched_not_prior | M12 | dispatched heads dropped from the priors | ledger.py | a dispatched head is a prior too |
| T3_review_owed_silent | round 1's red | the tick's REVIEW OWED loop body is `pass` | orchestrator_tick.py | six REVIEW OWED and CARRY rows, including the round-1 four |

Command: `python3 tools/audit/seat/r10_ledger_mutants.py` (all plants, no argument) printed `plants: 62, without a FAIL line: none`. `python3 tools/audit/seat/r10_ledger_mutants.py --null` printed rc=0 fails=0 for all six owners.

## Null control

At the merge base dc0a170b671814be196a54b1c71e29449f54d6d7, the unmodified tree:

- `ledger.py --self-test`: 77 checks, 0 failed;
- `orchestrator_tick.py --self-test`: 272 checks, 0 failed;
- `owed_unactioned.py --self-test`: 46 checks, 0 failed;
- `beat_jobs.py --self-test`: 107 checks, 0 failed;
- `r10_ledger_mutants.py --self-test`: 135 checks, 0 failed.

`git grep -cE "CARRY:|RECORD-OWED|record_owed|git_recarry" dc0a170b671814be196a54b1c71e29449f54d6d7 -- tools/audit/seat/ledger.py || echo NONE` prints NONE. Carries 5 and 6 are absent at the base, so each new row fails there by absence.

Each new row's own null control is in the tree:
- the tick row pairs `CARRY` after a merge verdict with `REVIEW OWED` after a blocked verdict at the same head;
- the conflict and side-branch fixtures each assert that the head is a two-parent merge before they read the result;
- the 30-minute row sits beside the 29-minute row that stays silent.

## Figures

- `python3 tools/audit/seat/ledger.py --self-test`: 89 checks, 0 failed (rule: its own count line).
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: 275 checks, 0 failed.
- `python3 tools/audit/seat/owed_unactioned.py --self-test`: 47 checks, 0 failed.
- `python3 tools/audit/seat/beat_jobs.py --self-test`: 107 checks, 0 failed.
- `python3 tools/audit/seat/r10_ledger_mutants.py --self-test`: 177 checks, 0 failed (CI greps `^r10_ledger_mutants self-test: [1-9][0-9]* checks, 0 failed$`).
- Scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 4 script(s) run, 29 scoped out`. Its scope.run names tests/debug_collect.py, tests/doc_claims.py, tests/entities.py and tests/features.py. Each was run with `PYTHONPATH=tests/hastub`, along with the run_always scripts env_drift.py --claims-only, closure.py selftest, layout.py and harness_headers.py. Results: ALL 162 DEBUG COLLECT CHECKS PASSED, ALL 296 checks PASSED (doc_claims), ALL 2632 ENTITY CHECKS PASSED, ALL 4876 FEATURE CHECKS PASSED, claims hygiene: origin/main ok, ALL 118 closure shrink pins PASSED, layout self-test: ok, ALL 112 HARNESS HEADER CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- The closure question (finding 6). `tests/closures.json` maps gate scripts (`tests/*`) to the files they read. `r10_ledger_mutants.py` is not a gate script: it appears only in `inert_reads` of `tests/entities.py`, the one list holding `orchestrator_tick.py` beside it. No closure entry would make the scoped gate run it. CI runs it in `governance / instrument-self-tests` on every pull request whose `machinery` input is not `'false'`, and any `tools/` diff is machinery. Round 1's red is that job working, so I changed no closure. The miss was local, and Red checks answers it.
- Carry 4, measured from the CI logs of the jobs `tests/replay.py` cites (`mcp get_job_logs`, the owner fixture's `cost` line). I read job 125240101580 (ref30) at `loop_cpu_ratio` 0.128 and job 125461180429 (ref24) at 0.189, the spread's two extremes. The reviewer's evidence holds the middle three: 0.1339 (125160076828), 0.1418 (125097530406) and 0.1433 (125316010511). Every reading is in the band (0.1245, 0.249], so carry 4 is delivered. The residual margin is the ref30 floor reading, 0.128 / 0.1245 = 1.028, 2.8 % over the floor; the ceiling side keeps 1 - 0.189 / 0.249 = 24 %. The tree comment now states that, in place of the contradicted 0.137-0.227. Null control: replay.py's header rule says each figure lies in (budget / COST_DETECTION, budget], and a figure under that floor is red ("under it a budget that could not see a doubling"). Each job I read printed `ok   owner-2026-10-30-away.json: cycle_cost`.
- Carry 1 delivered: `git log -S"'attribution':" --oneline -- tools/policy/field_coverage.mjs` names df9bfd301.
- Carry 2 delivered: 408644f7f (pre-bash.sh, `.claude/settings.json`, policy_lint `HOOK_TOOLS`).
- Carry 3 delivered: 82f333b9c (the `(awaits <path>)` clause and dev/audit/harnesses/agreement_two_pr.mjs).

## Red checks

At the previous head e81028ccef62bed5e4c6b6042f28193bc1d7ce8b, each red with its class and answer:

- `governance / instrument-self-tests`, root-cause-detectable. The diff moved the call text that `r10_ledger_mutants.py`'s `T3_review_owed_silent` anchors on. The cheaper detector is `python3 tools/audit/seat/r10_ledger_mutants.py --self-test`, which takes seconds and has no standing cost. Round 1's pre-PR run missed it because it ran only what `scope.run` named (doc_claims.py, entities.py). That scope covers gate scripts, not the governance instrument self-tests, and the harness reads `orchestrator_tick.py` by text rather than by import. Answer: T3 is re-anchored and killed again (Mutation proof). This head ran the self-test before the handoff (Figures). Its plants now cover every edited site in the tick, so a later edit of that text fails the self-test's anchor check in the same seconds.
- `pr-contract / pr-contract`, derived: it refused a red the body did not name. Answer: this section.
- `gate` (127771703222, 127772016712, 127781394257), derived. The first two ran before their runs concluded; the third failed on pr-contract. Answer: the two above.

At this head: no check run has concluded at handoff. The code reaches CI only when the orchestrator moves the pull request; the reds above are the last head's.

## Forward-carry

none

## Friction

none
