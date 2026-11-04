R10-HOTFIX-GATE-STALE-JOBS. `tools/ci/gate.py` judged this run's own required jobs from a stale jobs-API listing and published `PENDING (this run)` red for jobs that had already finished.

Cause, reproduced from the evidence, not assumed: in run 41870314676 the `gate` job (126746152523) started 17:37:25Z. `gate` needs `pr-contract`, which needs every unit (`tests`, `codeql`, `governance`, `hassfest`, `validate`, `kernel-points`, `arch-score`, `budget-raise-gate`; `.github/workflows/ci.yml`, job `pr-contract`'s `needs:`). So every job of this run's units had finished before `gate` started: the jobs API gives `tests / mutation` completed_at 17:35:07Z and `tests / closures` completed_at 17:36:51Z, both success. Yet the gate log at 17:37:43Z prints `FAIL tests / mutation: PENDING (this run)` and `tests / closures: PENDING (this run)`. The listing lagged the jobs. Run 41870522291 lists no failed job when read now (`get_job_logs failed_only`), so it was not re-read; the brief quotes its four lines.

Fix: `judge()` now re-reads when every reason is this run's own job read as unfinished (`lagging()`), every `POLL_S` (60 s), inside the existing `GATE_WAIT_MAX_S` (720 s) bound and the existing `sleep`/`now` injection. Such a job never reads as success: past the bound the verdict is still the same `FAIL ... PENDING (this run)`. Any other reason beside it (a real failure, a skip, an absence) breaks the loop at once, as before. The reason text has one owner, `OWN_PENDING`, which `gate()` writes and `lagging()` reads.

Alternatives, and why each lost:
- Treat this run's own non-completed unit as passed, since its needs ran it: unsound. An in_progress job has no conclusion, and a lag that hides a failure would read as success.
- Pass `toJSON(needs)` from the workflow: `gate` needs only `prelude` and `pr-contract`, so the unit jobs' results are not in its `needs` context. Making every unit a direct need changes the workflow graph and the pinned `ci.yml` for a read-lag problem.
- A separate shorter retry bound: the evidence shows lag past 2 min (a 17:39:52Z listing still had them in_progress), so a short bound would not have cleared it; one shared bound also keeps the timeout fit check (`GATE_WAIT_MAX_S + POLL_S + 120 <= timeout-minutes * 60`) unchanged.

## Head

a6305aa29908af0fa348a07fb2c46ab9699aa436, on base d7582ed404a87603bd02fefda610d7ebbe4181e1 (`origin/main` at 2026-11-04T18:02:27Z, the base I was given; main had not moved at the last `prepr.sh` run).

## Mutation proof

Each mutant applied with `sed` to `tools/ci/gate.py`, `python3 -I tools/ci/gate.py --self-test` run, then restored (restored tree: `gate self-test: 41 checks, 0 failed`):

- Predicate reverted to the old `if ok or why != [deferral(waiting)] or ...`: red, `run 41870314676 shape: own jobs read in_progress, then completed -> one re-read, PASS` and `null: own jobs still pending past the bound stay red, the wait inside the bound`.
- `lagging()` body replaced with `return False`: the same two checks red (2 FAIL lines).
- `all(` replaced with `any(` in `lagging()`: red, `null: a unit really failed beside a lagging one stays red, no wait` (got a wait and a PASS on the next frame, which is the defect a looser predicate would bring).

`tools/` sites are outside `mutation-autofix`'s lane; the in-tree mutant harness is the self-test above plus `dev/audit/harnesses/r10_ci_gate_core.py mutants`.

## Null control

The four checks the self-test adds, against the fixed tree:
- a unit really failed beside a lagging one: FAIL, `naps == []` (no wait);
- own jobs pending in every frame: FAIL `tests / mutation: PENDING (this run)`, waited, total wait <= `GATE_WAIT_MAX_S`;
- a skipped own unit: FAIL `tests / browser: SKIPPED (this run)`, `naps == []`;
- the reproduced shape (stale, then fresh): PASS after exactly one `POLL_S` nap.
On the unmodified tree the first check of that set fails (the defect), the rest are unchanged.

## Figures

- `python3 -I tools/ci/gate.py --self-test`: `gate self-test: 41 checks, 0 failed` at the head; 2 failed under each of the first two mutants, 1 under the third.
- `python3 dev/audit/harnesses/r10_ci_gate_core.py replay`: `GATE-REPLAY2 rc 0`, output IDENTICAL to `1371a0a6:measure/rev/gate_replay2.txt` (the recorded replay is the null control: behaviour on every other scenario unchanged).
- `python3 dev/audit/harnesses/r10_ci_gate_core.py mutants`: `RESULT mutants=16 survivors=0`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff <merge-base>`: `MODE: FULL` (reason: `tools/ci/gate.py` changes the gate itself); left to CI per `fixer.md` step 5.
- Timestamps above: `mcp list_workflow_jobs` on run 41870314676 and `get_job_logs` on job 126746152523.

## Red checks

none

## Forward-carry

none

## Friction

none
