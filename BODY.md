Root-cause record for the `gate` reds that read a finished job as unfinished, beside R10-HOTFIX-GATE-STALE-JOBS. It changes no production code. It adds `dev/audit/rca/r10-gate-stale-jobs.md` and the finder's harness, under `dev/audit/`, which `tests/closure.py`'s INERT list covers.

**Cause.** The Actions jobs listing lags the run graph, and `gate` reads it once and treats not-completed as a verdict. The ordering is sound and no upstream wait lags.

**Process state (d).** The premise that the listing shows what `needs` saw is unstated and fails with the platform: 19 of 21 attempts sit inside or within 66 min of a declared GitHub Actions incident. Nothing noticed the 10-30 cluster.

**Cost test: build.** About 47 min of waiting against at least 224 min lost, over 8 days. **Countermeasure:** a bounded re-read over every listing-lag reason, plus a printed lag line. **Refused:** a status-page read or health lane, another endpoint, a train re-run, a new bug class.

## Head

9b0df6105c67a009bce09feea9f4dffe8079a86a

## Mutation proof

The harness is the only code here. Both mutants are of a scratch copy, and both were restored by discarding the copy.

- The fix's predicate: with `lagging()` at handoff `a6305aa29` returning False, `harness.py` printed `mismatches 4 of 9` against 3 of 9 unmutated. The new BAD line is `41870314676 proof`.
- The harness's own predicate: with the listing never stale (`if clock[0] < stale.get(n, 0):` to `if False:`) over origin/main, it printed `mismatches 2 of 9` against 4 of 9. The `past the bound` shape turned BAD with `got PASS`.

## Null control

`harness.py`'s two null shapes, a fresh listing and a real red over a fresh listing, wait 0 s and answer PASS and FAIL `failure` on origin/main and on the handoff alike. The live probe (`probe.py`) made 143 listings over 18 polls and found 0 stale, so it detected nothing and settles nothing about other endpoints.

## Figures

Measured at origin/main `d7582ed404a87603bd02fefda610d7ebbe4181e1`, read 2026-11-04.

- Harness: `python3 -I dev/audit/harnesses/r10_gate_stale_jobs/harness.py` printed `mismatches 4 of 9` on this tree (rc 1, the defect present). Given an export of handoff `a6305aa29` as its argument it printed `mismatches 3 of 9`.
- Class count: `python3 -I dev/audit/harnesses/r10_gate_stale_jobs/tally.py dev/audit/harnesses/r10_gate_stale_jobs/reasons.jsonl` printed `scanned runs 1000 red gate attempts 383`, with `only-PENDING-this-run` 6, `only-prelude-None` 12, `ABSENT-this-run` 1 and `PENDING-plus-other` 2. The rule: `scan.py` over runs whose latest conclusion is `failure` or whose `run_attempt` exceeds 1, 2026-10-28 to 2026-11-04, every red `gate` attempt's Judge-step stdout. 37 of 1037 candidates stayed unread and first-attempt cancelled runs were not read, so these are floors.
- False reds, 14, and recovery, 170 min 4 s over 10 of them: `python3 -I dev/audit/harnesses/r10_gate_stale_jobs/recover.py dev/audit/harnesses/r10_gate_stale_jobs/reasons.jsonl`. A false red is an attempt with every stale job's true conclusion `success`.
- Scope: `python3 tests/closure.py select --diff d7582ed404a87603bd02fefda610d7ebbe4181e1` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`

## Red checks

none

## Forward-carry

- Handoff `a6305aa29` re-reads own PENDING only; `FAIL prelude: None` (10 false reds) and own ABSENT (1) still go red with no re-read. Carry: R10-HOTFIX-GATE-STALE-JOBS
- `tools/ci/codescan_wait.py`'s own-run path has no poll, so a leg whose step row lags may read as stood down and go unread. Read from the code, not measured. Carry: R10-HOTFIX-GATE-STALE-JOBS
- `.github/workflows/pr-contract.yml`'s red list keeps only completed failures, so a lagging red may be left off what the body must answer. Read from the code, not measured. Carry: R10-HOTFIX-GATE-STALE-JOBS

## Friction

none
