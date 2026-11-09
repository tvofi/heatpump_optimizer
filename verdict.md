Fix review: blocked 9106db4797f1c9b2ab277483977f922982294dd9 defect: bottleneck_check's trip memory is keyed by metric alone, so a breach after an UNREADABLE line for the same metric (or the reverse) is masked by the stale line

bus-nonce: 545f755c666cbcdc9bdaeeafce740724

Round 1 of review for this head. Measured at `9106db4797f1c9b2ab277483977f922982294dd9`, which has the same tree as the handed-off `2fb9b2467` (`git diff 2fb9b2467 9106db479` is empty), with merge base `fdc8d21ad`.

## Block

- `tools/audit/seat/bottleneck_check.py` `remembered()` keys `--memory` on `metric_of(line)`, the line's second word. That word is the same metric for a `BOTTLENECK:` line and a `BOTTLENECK-UNREADABLE:` line, so a change between the two for one metric re-prints the old line verbatim:
  - **UNREADABLE, then a breach:** the digest keeps printing `BOTTLENECK-UNREADABLE: yield -- ...`. The breach and its suggested action never print. Because the line text has not changed, the beat's fold sees nothing new and no wake fires.
  - **A breach, then UNREADABLE:** the stale breach line keeps printing while the source is unreadable. The file's own docstring says "a blind alert is not a quiet one", and this case breaks that.
  - Probe at this head: `ev/memory_kind_probe.txt`. The null control in the same file shows that with a quiet run in between, the next line prints afresh. The defect is the direct change of kind only.
  - No self-test case covers this. The two memory cases (`memory: a still-tripped metric re-prints...` and `memory: a recovery forgets...`) both use `BOTTLENECK:` lines. Keying the memory on the line's first word plus its metric would kill no current check.
  - Production reach: the beat row `bottleneck` in `beat_jobs.py` passes `--memory state/bottleneck.json` and writes both line kinds to the digest. This is the orchestrator's alert path that the owner's proposal 2 asked for.
  - Repair owed: key the memory on (line kind, metric), add a self-test case for each direction, and add a mutant that collapses the key back to the metric alone.

## Findings

- defect: `bottleneck_check.remembered` masks a breach that follows UNREADABLE on the same metric, and the reverse (see Block). This PR owes the fix before merge. Carry: R10-OUTSIDE-INTAKE

## Evidence

- RESULT harness `python3 dev/audit/harnesses/r10_outside_intake_p2_mutants.py` at this head, my run:
  - M0 printed `rc=0 fails=0 verdict=null`.
  - The 18 mutants from `discharged-any-stage` through `beat-missing-key-runs` printed `verdict=killed`. That run hit my 230 s call limit before the `mark-*` rows, and `mutant_guard` restored every file; the worktree was clean afterwards.
  - The three `mark-close-*` mutants, re-run alone, printed `verdict=killed` and `RESULT survived=0`.
  - Files: `ev/p2_mutants.txt` and `ev/p2_mutants_mark.txt`. This matches the body's claim that all 21 owed mutants are killed with M0 null.
- RESULT self-tests at this head (`ev/selftests_a.txt`):
  - `bottleneck_check` printed `ok`, with its 10 rule mutants killed.
  - `merge_throughput` printed `ok`.
  - `replan` printed `self-test: 0 failed`.
  - `plan_page` printed `75 checks, 0 failed`.
  - `roster_lib` printed `72 checks, 0 failed`.
- RESULT replan, both arms (`ev/replan_both_arms.txt`): roster `fcc9a1933aa191d4caf3205d8c1bee3f3a479119`, `--start 2026-11-08T20:20:00Z --slots 20 --seats 20`.
  - base: closure 2026-11-15T07:03:00Z, 49 batches, 6075.0 CI minutes, 324 done / 71 open, no `groups_discharged` key.
  - head: closure 2026-11-15T07:03:00Z, 48 batches, 5962.5 CI minutes, 327 done / 68 open, `groups_discharged` 3.
  - The 3 groups are R10-CI-GRADER-BATCH-STUDY, R10-FRICTION-CI-RED and R10-FRICTION-OTHER-FAMILY. Every figure equals the body's.
  - My base arm was `git archive` of the merge base `fdc8d21ad`, not the body's `17e621f08`. The base figures still match exactly.
- RESULT cheap checks (`ev/cheap_checks.txt`):
  - `selftest_wiring --check` printed `125 self-testing, 125 wired, 0 unwired`.
  - `tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
  - `env_drift.py --claims-only` printed `claims hygiene: origin/main ok`.
  - `closure.py select` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`.
  - The three-dot diff does not touch `VERSION`, `RELEASE_NOTES.md`, the manifest, either claim file or any `*_budgets.json`.
- RESULT scoped scripts and archscore at this head (`ev/scoped_and_arch.txt`):
  - `tests/entities.py` printed `ALL 2668 ENTITY CHECKS PASSED`.
  - `tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `score.py --diff fdc8d21ad` printed `Architecture score: dS +0.0000 NULL`.
  - All three equal the body's figures.
- Merge with main: `git merge-tree --write-tree origin/main 9106db479` at origin/main `19865e5a8` exited 0 (tree `d06c336b8`). There is no conflict.
- Role currency: `git diff fdc8d21ad...origin/main -- dev/governance/roles/` touches only `proposal-triage.md`, so `fix-review.md` is current.
- CI at this head: `merge_train.py classify` exited 1 with `RED 9106db479... pending: none red: gate`, the same on re-run at 01:45:28Z (`ev/classify.txt`).
  - The `pull_request` run 42539680047 has `gate` success (job 128932794887, completed 01:40:53Z) and `pr-contract` success (01:38:01Z).
  - The two red `gate` jobs, 128917441489 (run 42539681502) and 128920205614 (run 42540557389), are edit runs (`KIND: edit`, `WORKSET: arch-score budget-raise-gate`). Job 128920205614's log reads `FAIL run(s) [42539680047] at this head are still being judged; their gate decides`, so the red is an edit-run gate that concluded before the main run finished, not a failing test.
  - The body's `## Red checks` says "At `2fb9b2467` no check has run yet", so it does not name these two reds. The fixer's re-cut owes them a line (`defect-root-cause.md` second trigger: cheaper detector none, the edit gate defers by design). I did not block on this: the block above stands on its own, and a red CI never carries regardless.
- Merge with main, re-checked at origin/main `6457496ab`: `git merge-tree --write-tree` exited 0.
- Enumeration rule: the body names none. The issue is a feature request (proposals 1 and 2), not a defect class with several seams, so step 6's class rule has nothing to return.
- Head: the body's `## Head` names `9106db4797f1c9b2ab277483977f922982294dd9`, which is the head measured here.
