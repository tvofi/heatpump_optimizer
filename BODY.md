R11-PRE-STANDING-SCRIPTS part 1: the `cp-owed` beat row (carry 4, the owner's directive tvofi 2026-11-09, "never let the critical path or outside PRs slip, ever"; triage `dev/programme/triage/s6-batch141.md` P515), built to the approved design (`design/R11-PRE-STANDING-SCRIPTS` 375ce7ff3f, `Design review: approve` at be6cc24cae), section 1's first seam. The new module `tools/audit/seat/owed_watch.py` owns the fired-ledger read, the "a seat is on it" predicate and every owed-by-grace arm. The tick's `_fired`, `_seat_on` and `payloads` (FIRE-OWED) bodies moved into it unchanged. The tick's methods now delegate to it, and the tick's `verdict_kind` reads its verdict line through `owed_watch.FIX_VERDICT`, the one copy of that grammar (the agreement lane refused it written twice). So `orchestrator_tick.py` shrinks and gains no arm (design section 5, L5: "no new arm, ever; it shrinks by extraction"). The beat row `cp-owed` (`beat_jobs.py`, `beatd.jobs.json`, every 300 s, no class lock) writes one `CP-OWED <arm> <subject>` line to the digest for each critical-path or outside step past its grace.

The watched set is computed, never hand-kept. It is every open roster group `roster_lib.is_outside` is true for, plus every group `roster_lib.critical_path_read` publishes at the roster ref (`roster_lib.reader_ref`), plus their open pull requests (`group_for_branch`, else `group_for_pr`). An unreadable critical-path file is `cp-owed: UNREADABLE`, never an empty set. The eight arms and their graces are carry 4's, verbatim: merge verdict at the head with no approval 10 min, approved and unmerged 45, blocked with no fire since 15, a head with no reviewer dispatch 25, UNFIRED, DESIGN-REVIEW OWED 10, FIXER-OWED, and SEAT-SILENT 90.

Decisions, each with its reason:
- The carry states no grace for UNFIRED or FIXER-OWED. UNFIRED takes `FIRE_GRACE_MIN` (15), because it is the same step as FIRE-OWED: published, not fired. FIXER-OWED takes the design-review step's 10 (a verdict is in and the next seat is not dispatched).
- "After a step" compares a FIRED line's leading UTC stamp with the step's commit time. An unstamped line is never "after" anything, so a stale ledger line cannot silence a newer step.
- UNFIRED and SEAT-SILENT clear on a return ref moved since the step (handoff, handoff-wip family, handoff-body, design, design-verdict, verdict/<n>, probe/rev-<n>-*) as well as on a FIRED line. SEAT-SILENT keys on refs, never on a session's status (carry 17's dead session read `running`).
- DESIGN-REVIEW OWED is P510's predicate: no design verdict names the tip. A `seat-refused` verdict counts as no review. A tip whose note opens `Design blocked:` is excluded (design verdict note dr2-blocked-tip-owed).
- Rank: the design's note reads "critical path, then outside, then hotfix". This uses `roster_lib.dispatch_rank` instead, which puts a hotfix first, then critical path or outside: that function is "the one order every queue reader applies" and carries the owner's ruling (triage P420) that a hotfix outranks outside work. Inside one rank, the critical path comes ahead of outside, then the oldest step. That ordering is the rank half of carry 1, and it is pinned by two cases and two mutants.

## Head

`b02d5b3aabcf4dfed82c6a68d7068c45243f7a1a`, measured 2026-11-15 on this branch's base `origin/main` `98847b99d7bb3238686efd6869f805c89c6d1ff1`. At the handoff `origin/main` is `5825e1346c14eecace5c87c046558774145a94dc`, and `git merge-tree --write-tree origin/main HEAD` reports no conflict (its ledger merge driver resolves `tests/closures.json`).

## Mutation proof

Failing test first. The new `beat_jobs_selftest.py` cases run against the base's `beat_jobs.py` crash with `AttributeError module 'beat_jobs_under_test' has no attribute 'cp_owed'`: the base has no row. `owed_watch.py` does not exist at the base.

In-tree mutants, each a source edit in a temp copy and each expected to fail a named case:
- `python3 -I tools/audit/seat/owed_watch.py --self-test`: 14 in-file mutants, one or more per arm, plus the grace comparison and the two rank keys. Every mutant prints `ok   mutant <name> killed by: <case>`. Each arm's mutant drops or inverts that arm's predicate and fails its `planted <arm>: one line at grace 0` case. The exceptions are `unfired`, `design_blocked` and `seat_refused`, which fail their null or seat-refused cases, and `grace_ignored`, which fails `null merge-no-approval: inside its grace prints nothing`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: the three new row mutants (`cp_owed_filter_dropped`, `cp_owed_rc_ignored`, `cp_owed_ledger_optional`) are killed by the three row cases they name.

- Diff mutants, run per file with the self-test that owns the file (`python3 -I tools/audit/seat/mutant_run.py --diff 98847b99d7bb...HEAD --report-only --path P --cmd C`). prepr.sh draws only the first 40 mutants in file order, so it never reaches `owed_watch.py`:
  - `beat_jobs.py` with `beat_jobs.py --self-test --no-mutants`: 0 survivors.
  - `owed_watch.py` and `orchestrator_tick.py` with `sh -c 'python3 -I tools/audit/seat/owed_watch.py --self-test && python3 tools/audit/seat/orchestrator_tick.py --self-test'`: 86 survivors. 77 are at or below `owed_watch.py`'s `SELF_TEST_MARK` line, and 9 are above it (Unpinned sites). The first pass of this run left 88 survivors in `owed_watch.py`. The cases added since (read_world over a throwaway origin, fixture topics apart from group ids, fire-only clears, the age and grace edges, the CLI) killed every predicate survivor above the mark.
  - `beat_jobs_selftest.py` with the full `beat_jobs.py --self-test`: 4 survivors (Unpinned sites).

## Null control

- `owed_watch.py --self-test`: the planted world with every step answered prints nothing at grace 0. Each arm's planted step inside its grace prints nothing. A class-open `revise` at the design tip is a review, a `Design blocked:` tip is not owed, and a return ref newer than a dispatch clears UNFIRED.
- `beat_jobs.py --self-test`: `cp-owed null: nothing owed writes no byte`.
- The moved code against the tick's own fixtures: `python3 tools/audit/seat/orchestrator_tick.py --self-test` prints `319 checks, 0 failed` at the base and at this head. The FIRE-OWED case, the three seat-on cases (carry 6 a, b and c) and the family and BLOCKED.md seat cases now run through `owed_watch`.

## Figures

- `python3 -I tools/audit/seat/owed_watch.py --self-test`: `owed_watch self-test: 73 checks, 0 failed`.
- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: `beat_jobs self-test: 259 checks, 0 failed`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `319 checks, 0 failed` at the base (detached worktree at 98847b99d7) and at this head.
- Live read, run in this checkout: `owed_watch.read_world` against origin's refs and the round-10 roster ref, with `gh pr list` answered `[]` because the cloud seat's gh is refused (the real `cp-owed` printed `cp-owed: UNREADABLE open pull requests: ...` and exit 2, the UNREADABLE path). It watched 11 open outside groups and 0 critical-path groups: the critical-path file at that ref lists only round-10 groups, none open. It printed one line, `CP-OWED DESIGN-REVIEW-OWED R11-OUTSIDE-ROOMS-P2 64m past its 10m grace [OUTSIDE]`, and `git ls-remote origin 'refs/heads/*R11-OUTSIDE-ROOMS-P2*'` lists `design/R11-OUTSIDE-ROOMS-P2` and its designer dispatch with no `design-verdict/` ref, so the line is true. The PR arms were not exercised live in this seat.
- Sibling seams, enumerated by `git grep -n "FIRE_GRACE_MIN\|SEAT_WINDOW_MIN\|FIRED_STAMP\|_seat_on\|_fired(\|fire_names\|def payloads\|\.payloads(" -- tools/audit/seat/` (design section 4). Every tick definition moved and each tick call site now delegates: `_fired`, `_seat_on` (two callers, the body-ahead and red-unowned buckets), `payloads`, and the self-test's `FIRE_GRACE_MIN`. The enumeration also returns `sweep_gantt.recent_fired`, a second fire-ledger stamp reader with its own 12 h window. `verdict_audit.recent_lines` is a third, which the grep does not name but `git grep -n "STAMP.match" -- tools/audit/seat/` does. Neither is in the design's section 4 list, so both are carried below and not moved here.
- `python3 tools/audit/archscore/score.py --diff 98847b99d7bb3238686efd6869f805c89c6d1ff1`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `tests/entities.py` runs the tick's self-test, which now loads `owed_watch.py`. `python3 -I tools/pr/ci_predict.py --base origin/main --apply-inert` wrote its INERT READS entry. The self-test-reads arm (`--only self-test-reads --record-self-tests`) then predicted `SELF-TEST READS UNDER-SCOPED tests/entities.py: tools/audit/seat/owed_watch.py`. Repaired by the route `tests/closure.py`'s `INERT_EXCEPT` documents for `orchestrator_tick.py` and `ci_priority.py`: the file is excepted and joins `closures["tests/entities.py"]`. Both `ci_predict.py --base origin/main` and `--only self-test-reads --record-self-tests` now print `CI PREDICT: no closures, fast, governance or instrument red predicted against 98847b99d7bb`.
- The agreement lane (`agreement_py.py`, then `agreement.mjs --py-json`) prints `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- `tools/ci/selftest_closures.json`: `python3 -I tools/ci/selftest_scope.py record` re-measured, under strace, the steps whose entries name `orchestrator_tick.py`, `beat_jobs.py` or `sweep_template.md`, and the edited `gantt-and-verdict-audit` step. Without this, main's drift step would refuse the tick's new read of `owed_watch.py`. It printed `selftest_scope: recorded 12 step(s) into ...; 0 failed [], 0 broken trace(s)`, and `python3 -I tools/ci/selftest_scope.py static` prints `119 gated step(s), 0 problem(s)`.

<!-- figure-block: scope-line mb=98847b99d7bb3238686efd6869f805c89c6d1ff1 head=b02d5b3aabcf4dfed82c6a68d7068c45243f7a1a -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Brief carries

This part's carries are 0 to 4 of the brief, numbered from 0 as the dispatch rendered them.

- Carry 0 (NOT REVIEWABLE names deferral-only and real; the board flags a disabled Gate sweep): design input. The approved design (section 5, "L5 decision") builds it as the dispatch drain's classes `not-reviewable-real` and `not-reviewable-deferral` in part 3, not in the tick. Carry: R11-PRE-STANDING-SCRIPTS (part 3, named by the approved design)
- Carry 1 (probe-refused classified by reason and ranked by critical path): the rank half is built here. CP-OWED lines are ranked by `dispatch_rank`, critical path first inside a rank, pinned by `rank: inside one rank the critical path is ahead of outside` and its mutant `rank_cp_first`. Classification by reason is the dispatch drain's EXCEPTION classes. Carry: R11-PRE-STANDING-SCRIPTS (part 3, named by the approved design)
- Carry 2 (unrecorded-merge query; HANDOVER line stops naming state_docs): design input, "re-measure first". The design re-measures it in part 4 against `record_beat`'s readback, and any remaining defect goes to R11-PRE-ACK-COMPLETION. Carry: R11-PRE-STANDING-SCRIPTS (part 4, named by the approved design)
- Carry 3 (postmerge / record_beat posts nothing when issue 201 already carries the sha40): not built here. At this base `record_beat.record()` posts unconditionally, with no read of the thread. The design places it with carry 6's readback in part 4 (record_beat.py, postmerge.py). Carry: R11-PRE-STANDING-SCRIPTS (part 4, named by the approved design)
- Carry 4 (the critical-path and outside watch as a tracked beat row): built, the `cp-owed` row and `owed_watch.py`. The planted control fires each of the eight arms at grace 0, the null (each step inside its grace) prints nothing, and there is one or more mutants per arm (Mutation proof).

## Unpinned sites

- `tools/audit/seat/owed_watch.py`, every survivor at or below `SELF_TEST_MARK` (77): self-test fixtures, planted constants and the in-file mutant harness's counters. They are not predicates. The harness's own integrity is the `src.count(old) != 1` refusal, and each in-file mutant must fail its named case. Disposition: test scaffolding, not triaged.
- `owed_watch.py`, equivalent: `sys.path.insert(1, ...)` (index 0 or 1 loads the same sibling); `seat_on`'s closing `return False` deleted (None is falsy, and every caller tests `not`); `_names_group`'s PR sentinel `-1` changed to `-2` (no pull request is negative); `split("/", 2)` for `split("/", 1)` on a roster branch (`fix/<topic>`, one slash) and on a ref family name (no slash before the family); the error message's 120-character tail; argparse's description line.
- `orchestrator_tick.py`'s `_fired` and `_seat_on` wrappers with `return` deleted (drawn by prepr.sh under `beat_jobs.py --self-test`): killed by `orchestrator_tick.py --self-test` in the owed_watch-and-tick pass above.
- `orchestrator_tick.py` self-test fixture `pf2`'s mtime (`FIRE_GRACE_MIN - 5`, as `- 6` or not set): the young payload stays inside its grace either way. Equivalent.
- `beat_jobs_selftest.py`: the UNREADABLE answer's rc 2 as 3 (the row reads any non-zero rc as UNREADABLE), equivalent. Deleting `pre = ...` (an earlier block binds the same name), equivalent. Deleting the `cp-owed null` and table-row `res[...]` assignments drops a case that nothing counts: no in-tree check holds a floor on the harness's case count. Disposition: test scaffolding.

## Red checks

none

## Forward-carry

- dev/programme/rosters/wave-r10-groups.json, group R11-INTAKE-R10-RESIDUE: `sweep_gantt.recent_fired` and `verdict_audit.recent_lines` each read the fire ledger's leading stamp with their own regex and window. They are a second and a third parser of the stamp `owed_watch.fired` now owns. Each should read `owed_watch.fired` and keep its own 12 h window, so one stamp grammar exists. Not moved here because the design's section 4 enumerates only the tick's callers. Carry: R11-INTAKE-R10-RESIDUE

## Friction

- part-cut: contradiction: this seat's brief reads "Part 1 of 4: build carries 0-4". The approved design's section 5 cuts part 1 as carries 4, 5 and 11 (cp-owed, `class_wait_s`, `is_hotfix`), and parts 3 and 4 as the homes of carries 0 to 3. Carries 0 to 3 are answered above by the design's parts. Carries 5 and 11 are not answered here, as the brief says. The renderer cuts parts by carry index, not by the design's part table (PC-1113-07 and 08, carry 14). Carry: R11-PRE-STANDING-SCRIPTS
- gh-refused: cost: the cloud seat's `gh pr list` is refused by the environment's proxy, so the live read of the four PR arms could not run here (Figures). The self-test plants them offline. Carry: dismissed: an environment limit of the cloud seat, and the beat runs on the orchestrator's host, where gh is live
