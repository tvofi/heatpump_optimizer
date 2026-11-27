# fixer-r11-ci-3885-queue-l4l3: L4 handed off; L3 not started (context rotation)

Question: re-dispatch L3 (W1 + W2) and carry 2's measurement to a fresh fixer context? This seat reached fixer.md's rotation bound (~150 k) after L4.

## Handed off

- L4 is at `handoff/r11-ci-3885-queue-l4` 77f41cbb0d, cut from origin/main 8890fc2bad. Its body is on `handoff-body/r11-ci-3885-queue-l4` 5991e2dd73. Prepr reads `PRE-PR: 77f41cbb0d... rc=0` with `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`.
- What L4 does: `prelude.machinery(rowblind=True)` ignores every path under `dev/programme/delivery/`. A record PR therefore stands down `tests / arch-instrument`, at most 1.9 runner-min per record run (run 45907701622).
- The other lanes a record PR could skip were answered per lane in the body's `## Figures`:
  - closures, env-matrix and instrument-self-tests read rows, per `lane_reads_delivery.recording.json`;
  - fast runs `tests/doc_claims.py` and `tests/entities.py`, whose closures list rows;
  - every other job is unmeasured and runs (fail closed).
- Harness: `dev/audit/harnesses/lane_reads_delivery.py` gained the `inputs.range_base || format(...)` expression. Re-run at 77f41cbb0d, arch-instrument reads `complete`, 3 steps, no row, with the control lane reading its planted row.
- `gh api` works in this container: the run-job listing read through it.

## Next

- L3 (W1 + W2), per design §4 and its Tests list. It touches `tools/ci/prelude.py`, so build it on `handoff/r11-ci-3885-queue-l4` (77f41cbb0d), which is not on main yet. Then push it to `handoff/r11-ci-3885-queue-l3`, with its body on `handoff-body/r11-ci-3885-queue-l3`.
- Carry 2 (env_drift cache after a light push) is unmeasured. Per `tests.yml`, `Restore the drift baseline` runs on pull_request, merge_group and dispatch only, and a push only saves a warmed entry keyed by its own SHA. So the miss to measure is a pull request whose merge base is a light push that never ran env_drift: grep its owning `fast` shard log for `DRIFT BASELINE CACHE`. The carry's own perturbation, reading a push run's log, always reads MISS.
