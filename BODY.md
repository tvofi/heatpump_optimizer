R10-HOTFIX-GATE-STALE-JOBS part 2 (hotfix). Carry 1 (e67341cc) verified already built by #3205 and needs no code; carry 2 (e350d851) fixed in tools/ci/codescan_wait.py; carry 3 (d0916ca4) recorded as not buildable with evidence.

## Head

4f478a78c9c72d1976e9eefe03421df96ce287f0

## Mutation proof

Mutant: in `tools/ci/codescan_wait.py` `source`, `if settled(jobs):` replaced by `if True:`. `python3 -I tools/ci/codescan_wait.py --self-test` then prints BAD for checks 18 (own run: lagging step row polled, then read) and 19 (still lagging at the bound FAILs), 2 failed of 20; restored, 0 failed. The tools/ site is outside mutation-autofix; the self-test is the in-tree mutant harness.

## Null control

At the base (origin/main 4b7e1770ba81fa02a8dda531463eba68e987ff59) the own-run path read the listing once: self-test check 18's input (step row with no conclusion) returns [] and the leg is dropped unread (the mutant above reproduces that). Nulls kept: check 19 a listing still lagging past the bound FAILs, never passes; check 20 a settled stand-down (step skipped) is not waited for; checks 1-17 unchanged. For carry 1: a really failed unit stays red with no wait, a truly pending unit past the bound stays red, and a skipped unit is unchanged, all in gate.py's self-test.

## Figures

- `python3 -I tools/ci/gate.py --self-test` at origin/main 4b7e1770ba81fa02a8dda531463eba68e987ff59: 57 checks, 0 failed.
- `python3 dev/audit/harnesses/r10_gate_stale_jobs/harness.py` at origin/main 4b7e1770ba81fa02a8dda531463eba68e987ff59: mismatches 0 of 9, including prelude listed unfinished and own ABSENT re-read, real reds unwaited, and the past-the-bound case still FAIL.
- `python3 -I tools/ci/codescan_wait.py --self-test` at 4f478a78c9c72d1976e9eefe03421df96ce287f0: 20 checks, 0 failed.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` reads MODE: FULL (a gate file); CI runs the full suite.

## Red checks

none

## Forward-carry

- e67341cc: built by #3205 bc806747b; verified above; the orchestrator drops the roster carry. Carry: R10-HOTFIX-GATE-STALE-JOBS | dismissed: built by 3205 and verified here
- e350d851: closed in this diff. Carry: R10-HOTFIX-GATE-STALE-JOBS | dismissed: fixed in this diff
- d0916ca4: not built. pr-contract needs every unit job (ci.yml), so the red list is read after all units completed; the RCA (r10-gate-stale-jobs.md section 3) found 0 lagging listings in 143 probes and no evidence check-runs lag. A red absent from one listing still turns the gate red (gate re-reads its own units, per #3205) and is listed on the next pr-contract run at that head, so it cannot merge; only the body-answer is deferred. Read from the code, not measured; no endpoint is known to be fresher, so a bounded re-read would have nothing to assert against. Carry: R10-HOTFIX-GATE-STALE-JOBS | dismissed: unmeasured, cannot fail open

## Friction

none
