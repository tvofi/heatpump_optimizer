Hotfix R10-HOTFIX-ROSTER-DRAIN-REPLAY. `beat_jobs.py` `roster_drain` saved its done set (`roster-done.json`, `roster-queue-lines.json`, `roster-hold.json`) only after the whole queue: beatd kills the row at its `timeout_s` in `beatd.jobs.json`, so a pass with more pending ops than fit replayed every applied op on the next pass (the orchestrator observed drop-carry ops re-landing on handoff/audit-r10-roster, 2026-11-10). Fix: a `save()` after every op that is marked done (each `ctx.remember` is an atomic write and only on change), and `ROSTER_PASS_BUDGET_S`: no op starts past it, so the kill does not land mid-queue; the self-test pins it at most half the row's `timeout_s`, leaving an op started just before it as long again.

Alternatives: (1) save only, no bound — a kill still replays the op it lands in, and a drop-carry replay is the observed harm, so the bound is kept; (2) an op count cap per pass — a count does not track the op's duration, the time budget does; (3) reading `timeout_s` from `beatd.jobs.json` at run time — couples a row to beatd's table file at every pass; a constant pinned against the table by the self-test gives one source checked at every self-test run.

The root cause is owed in its own seat, the orchestrator's R10-RCA-ROSTER-DRAIN-REPLAY (the defect reached a live state document), and is not written here.

Residual: the digest lines of the ops a killed pass applied are not written (`write_job` stays at the pass end); with the bound a kill needs one op to outlast half the timeout. Carry: dismissed: digest-only loss, the done set is the state that must survive, and the bound makes the kill the exception.

## Head

b4660fa4f9632632f4ff9d69e9f344b28800309c, merge base 5d09dedf69eb9fe9bcab6bd9e5ddbde04a387ecb (origin/main at 5d09dedf69eb9fe9bcab6bd9e5ddbde04a387ecb, 2026-11-10T08:42Z).

## Mutation proof

Deleted the per-op `save()` after `holds.pop(key, None)` and the `if ctx.clock() - start >= ROSTER_PASS_BUDGET_S: break` lines, ran `python3 -I tools/audit/seat/beat_jobs.py --self-test --no-mutants`, restored:

    FAIL roster-drain: a pass killed mid-queue keeps its applied ops; the next applies each once
    FAIL roster-drain: a pass past ROSTER_PASS_BUDGET_S starts no op; the next pass resumes
    beat_jobs self-test: 112 checks, 2 failed

The same edits stay in the self-test's MUTANTS (`roster_saved_at_pass_end`, `roster_pass_unbounded`, plus `roster_budget_over_timeout` raising the constant to 451), each killed by its named case in `python3 -I tools/audit/seat/beat_jobs.py --self-test`.

## Null control

Failing test first, at the merge base with only the self-test changed: the two cases above and `roster-drain: ROSTER_PASS_BUDGET_S is at most half the row's timeout_s` FAIL (`beat_jobs self-test: 112 checks, 3 failed`), while the new `roster-drain null: a pass that completes applies each op exactly once` passes — a pass that is not killed applied each op once before the fix too, so the killed-pass case separates the defect from a working drain. No finder harness exists for this hotfix (orchestrator observation); the self-test case is the harness, run at both ends above.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test` at the head: 192 checks, 0 failed (mutants included).
- `python3 -I tools/audit/seat/beat_jobs.py --self-test --no-mutants` with the self-test alone at the merge base: 112 checks, 3 failed (the three cases above).
- Class seams, rule `grep -nE "ctx\.remember\(|atomic\(" tools/audit/seat/beat_jobs.py` (a row's persisted memory, by row), against the property "a loop of non-idempotent side effects whose done record is written after the loop":
  - `roster_drain`: closed in this diff.
  - `tick_digest` (`tick.json`), `audit_dispatch` (`audit-dispatch.json`): digest-only output, rewritten only on change; a replay re-derives the same lines. Not the class.
  - `plan_beat` (`plan-page.json`): one state_docs push per pass, no queue; a replay re-pushes the current state (no move, no `pushed` line). Not the class.
  - `head_watch` (`heads.tsv`): one gh read before the loop; the loop is in-process with no subprocess, far inside its `timeout_s`. Not the class.
  - `gantt`, `pulse`, `fold`, `write_job`, `atomic` itself: input snapshots or digest files, rewritten whole each pass. Not the class.
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: MODE: SCOPED, no script selected; the beat_jobs self-test runs in CI's governance workflow.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

none

## Friction

none
