R10-RCA-GATE-BUSY-DEFER-2, the root-cause seat for R10-HOTFIX-GATE-BUSY-DEFER (topic r10-gate-busy-defer-2). It ran beside that fixer and did not edit `tools/ci/`. Part of #201. The analysis is `dev/audit/rca/r10-gate-busy-defer-2.md`, indexed in `dev/audit/config/bugclasses.json` as `_rca.R10-RCA-GATE-BUSY-DEFER-2`.

## Re-cut note

Repair round 2, after a blocked verdict (`rca-claim-false`): the first record called #3263's edit/code-run red "designed, not the race", and main's #3276 (`812bb8747`) had fixed it as a defect. This body is re-taken whole at the head below.

- **Stale pin (unchanged finding).** ci.yml restores `tools/ci/*.py` from the payload's `pull_request.base.sha`, and a job re-run replays that payload. So each re-run of a run created before #3246 merged (`355d9965`) ran the pre-fix `gate.py`. The six mutual-deferral gates (#3261, #3265, #3255 pairs, pinned `28482ece`, `f2a01514`, `80016a71`) all ran such a copy. Process state (c).
- **#3263 (corrected).** Run 42338396358's 2-second red is the edit/code-run deferral, a second defect with its own cause. `prelude.judging()` read a deferring edit run's skipped `pr-contract` caller (listed completed under its bare name) as owed, so that run looked busy to every gate at its head, and gate.py's at-once bound dodged the wait cycle that made. #3276 fixed `judging()` and deleted the bound. RCA section 1 gives the cause, section 3 the process state (c: the self-test and #3246's `prelude` scene pinned the at-once red as the specification, not the property "a deferring run is judging") and the cost; the countermeasure is landed by #3276 and scored here.
- **Instrument.** The replay arm's exit code ignored the single-gate class, so it read rc 0 for the at-once red at `294a880d`. `DEFECTS` now counts `C3-AT-ONCE`; a single gate that waited and then deferred is `DEFERRED`, the bounded wait, not a defect. The arm's remaining blindness (the wait cycle itself) is stated in its docstring and RCA section 1.
- **Countermeasure, proposed and not built.** A re-run of a gate whose pinned programs differ from the base tip becomes a ci.yml dispatch (`tools/ci`, the gate fixer's and the orchestrator's).

## Head

`b38e5c08bddba4817e362c450e7369ddd1b819ae`, branch `fix/r10-rca-gate-busy-defer-2`: the reviewed head `d5c4a06b` plus origin/main (merged by the bot as `510b2a108`; origin/main `b4ec2f332` is an ancestor) plus one repair commit. origin/main was `b4ec2f332` at 2026-11-07 15:07Z, at the final `tools/pr/prepr.sh` run, so no further merge was owed. The three-dot diff adds the harness and its fixture, the RCA document, the `_rca` entry, the harness's `tests/closures.json` INERT READS entry and the delivery row.

## Mutation proof

This PR adds no production line. The detector it adds is the `replay` arm, proven against real program copies (`git archive <sha> tools/ci tools/pr`) and two mutants:

- Red on the defect: `replay --ci` at `28482ece`, `f2a01514` and `80016a71` gives rc 1, `DEADLOCK` on the three pairs. At `294a880d` it gives rc 1, `C3-AT-ONCE` on the three edit/code-run scenes.
- Green on the fixes: rc 0 at `812bb8747` and at this head's `tools/ci`, the pairs `DECIDED` (naps 0 and 0 in #3261) and the C3 scenes `DEFERRED` with naps 12.
- Scoring mutant: a copy of the harness with `DEFECTS = ("DEADLOCK", "HALF-DEFERRED")` gives rc 0 at `294a880d`; the unmutated copy, relocated the same way, gives rc 1.
- M17 (busy()'s later-started-gate tie-break deleted) on this head's `gate.py` **survives** the arm, rc 0: under #3276's `judging()` the pair no longer reads each other busy. `gate.py --self-test`'s M17 row pins it; the arm does not replace the self-test. M24 named code #3276 deleted and is not run.

## Null control

- Pre-#3246 programs give rc 1 and #3246's gives rc 0 on the same listings; the fixed program decides the pairs the stale program deadlocks.
- At `294a880d` the C3 scenes read `C3-AT-ONCE` with naps 0, at `812bb8747` and this head `DEFERRED` with naps 12, so the class separates the at-once publication from the bounded wait (`GATE_WAIT_MAX_S` 720 s at `POLL_S` 60 s, the recorded code run still unfinished at 29 minutes).
- The arm refuses, and does not go green, on a fixture whose pair gates did not overlap in time or whose gate never started.
- The compare the countermeasure would run, `git diff --quiet 28482ece 294a880d -- <restored paths>`, gives rc 1; the same sha on both sides gives rc 0.

## Figures

- Replay at each program: `python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci <export>/tools/ci`, with `<export>` from `git archive <sha> tools/ci tools/pr`. rc 1 at `28482ece`, `f2a01514`, `80016a71` and `294a880d`; rc 0 at `812bb8747`; `python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay` at this head prints `RESULT replay ... defects=no`.
- Pins of the 9 recorded gates: `python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py pins` prints `RESULT pins gates=9 stale=6`.
- Fixture: `dev/audit/harnesses/r10_rca_gate_busy_defer_2.json`, sha1 f926d6a67b5582c172f49cb436a09e7ff7b63b70 (`sha1sum`), unchanged by this repair.
- Census (the first handoff's figures, from `python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py census --since 2026-11-07T03:45:14Z --until 2026-11-07T04:50:21Z`). **Re-derived in this repair** at 2026-11-07 after the review's run failed on proxy resets; the same command printed the same three rows: stale `gates=46 {'defer': 21, 'other-red': 1, 'pass': 24}`, 7 PRs, `reruns=36`; fixed `gates=3 {'defer': 3}`, all the at-once edit/code-run red, now #3276-class; unpinned `gates=5`.
- Recurrence, rule pinned at a time: `git log --first-parent --format=%h --since=2026-10-23T00:00:00Z origin/main -- 'tools/ci/*.py' tools/pr/codeql_scope.py tests/closure.py tools/pr/cancel_superseded.py | wc -l` gives 30 at origin/main `b4ec2f332` (15 with `--since=2026-10-31T00:00:00Z`). The same rule over `tools/ci/gate.py tools/ci/prelude.py` since `2026-10-31T00:00:00Z` lists 4 merges (#3276, #3246, #3230, #3205). The count moves with each merge to those paths; the rule is the record.
- Ledger: `python3 tools/audit/fold_ledger.py check` prints `0 violation(s)`, 137 rca entries.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, the script `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2645 ENTITY CHECKS PASSED`; `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Seam enumeration (fixer step 8). Rule: the `git checkout "$PINNED" --` lines in `.github/workflows/ci.yml`, each naming programs a run restores from its payload base. Each returned seam (prelude/gate: `tools/ci/*.py`, `tools/pr/codeql_scope.py`, `tests/closure.py`; cancel-superseded: `tools/pr/cancel_superseded.py`; refresh: `tools/ci/*.py`) is in the class, open, dispositioned in RCA section 3 and covered by the proposed countermeasure 5.2.
- Instrument blindness: the single-gate scenes judge one gate beside a code run listed as recorded, so the replay scores the at-once publication and not the wait cycle `judging()` made; #3276's fixture self-test in `gate.py` pins the cycle (RCA section 1).

## Red checks

Read with `pull_request_read get_check_runs` on PR 3278 at 15:07Z, all 86 check runs in one page, at head `510b2a108` (the bot merge this repair builds on). The repair commit `b38e5c08` had no check runs at the time of writing.

- `tests / nightly-status` failure (run 42383179334, job 128435471085): not this PR's; its diff does not reach what nightly-status reads, and it was red on the previous head too. Answer: the cheaper detector is the nightly job itself, standing cost nil here (`fix-review.md` 11).
- `gate` cancelled (run 42383179334, job 128439401244, with `tests / coverage`, `tests / closures`, `tests / fast (3.14)`, `governance / instrument-self-tests` and the other cancelled lanes): the run was superseded at 15:05:24Z by run 42383590829, whose `gate` job 128439014625 is in progress. Cleared by the newer run, class: superseded run, not a failure of this diff. The earlier head `d5c4a06b` had the edit-gate deferral `gate` red (job 128409314146, run 42374407743, "FAIL run(s) [42372899314, 42373060299] ... still being judged"), cleared when the code runs classified GREEN at 13:25:08Z, and the same `tests / nightly-status` red (job 128405124320, run 42372899314).
- No open `code-scanning alert` at the read.

## Forward-carry

- Carry 1, to the R10-HOTFIX-GATE-BUSY-DEFER fixer (topic r10-gate-busy-defer-2): #3263's red was not designed; #3276 fixed it and RCA section 1 records the cause, process state and cost. `replay --ci <export>` now fails on `C3-AT-ONCE` (dev/audit/rca/r10-gate-busy-defer-2.md, Carries). Carry: #201
- Carry 2, to the orchestrator: the stale-pin re-run countermeasure in `refresh()` and `sweep.py` (RCA 5.2) is a `tools/ci` change for the gate's owner. Until it lands, after any pinned-program merge, dispatch ci.yml (`pr=N base=main`) for each PR whose latest gate is a stale-pinned red (RCA 5.3). Carry: #201

## Friction

- PROMPT.md: contradiction: the payload pins git identity `seat` and the brief says `hpo-fixer` and never `seat`; `hpo-fixer` was used, set in the environment because the exported toolchain sets the author variables to `seat`. Carry: dismissed: identity settled per brief, as on #3246
- frugal-routing-hook: cost: an inline-search budget of 5 per prompt blocked plain reads of files this seat was editing, forcing delegations. Carry: dismissed: seat-harness configuration, outside this repository
