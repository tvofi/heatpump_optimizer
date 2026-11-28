# BLOCKED: r11-seam-actuation-writes-mutpin (PR #3897, head 4629847a7903239fb1409edc62dc3fd02419c3a7)

Question: 7 of the 10 sites `tests / mutation` draws at this head are killed by
`tests/features.py` alone, and that driver costs about 1617 s per run, so the
drive cannot fit in 160 minutes without a change to the lane. Should the
orchestrator change the lane (`tests/mutation_table.py` drive scheduling or
`tests.yml`), or approve re-pinning the 2 sites a cheaper driver kills? That
re-pin saves 2 features.py runs and does not make the drive fit.

No commit was made to the PR. Nothing was pinned, because nothing was left to pin.

## Where the 160 minutes go (run 46128197569, job 140928518998)

Read from the job log (`gh api repos/tvofi/heatpump_optimizer/actions/jobs/140928518998/logs`; no egress refusal):

- The ratchet passed: `1391 unpinned site(s) of 8276 candidate sites, 1392 at
  the ratchet base cb2026c3`. No unpinned site was added.
- The drive: `--scope changed --max 10 --jobs 3`, 10 mutants over 8 files.
- `baseline tests/env_drift.py ... 397s` ran from 09:05 to 09:11.
- The first red run of tests/features.py came at about 09:34, then the lazy
  `baseline tests/features.py ... 1697s` (finished 10:02:51), then its null
  control (finished 10:26:03, 1392 s).
- `baseline tests/solar_alignment.py` came only at 11:01:46. The other workers
  spent the time between on features.py mutant runs.
- The job was cancelled at 11:43:50 with the table unwritten.

## Pinning (brief step 2)

`python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3` at
4629847a printed `PIN KILLED -- 0 new unpinned site(s) against cb2026c3...` and
`PIN KILLED: nothing to pin`. The null control for that claim is the ratchet's
own line: an added unpinned site would have printed `ADDED UNPINNED` and refused.

Pinning cannot shrink this job anyway. `sampled_pool` draws from every site on a
changed line, pinned or not. A pin only moves its own killer to the front of
that mutant's driver order (`order_pool_drivers`). The 10 drawn sites are all
already pinned: 9 to `tests/features.py` and 1 to `tests/solar_alignment.py`.
This was reproduced by calling `sampled_pool` with the CI arguments (seed
20260911, per-file 3, max 10). So 9 mutants each pay one features.py run first,
plus that driver's lazy baseline and null control: 11 features.py runs on 3 workers.

## Cheaper killers: measured

Probe: each drawn mutant was applied in its own worktree, with the ledger rows
`invalidated_rows` names hidden as the lane hides them. It was then driven by
every driver in its closure except `tests/features.py`, `tests/stress.py` and
`tests/harness_headers.py`, in the lane's order, stopping at the first kill.
Kills were judged by `mutation_table.killed` against green baselines of every
driver (all `rc=0 failed=0`). The script stays in scratch as a one-off probe.

| site | pin | cheaper killer | runs before a kill or exhaustion, total s |
|---|---|---|---|
| inputs.py:644 GUARD_OFF | features.py | none | 22, 1907 |
| pump_arbiter.py:576 RETURN_DEL | features.py | typing_ruler.py (rc=1 failed=1, 23 s) | 4, 83 |
| coordinator.py:672 RETURN_DEL | features.py | none | 18, 1566 |
| legionella.py:163 GUARD_OFF | features.py | none | 18, 1555 |
| inputs.py:627 BOOLOP | features.py | none | 22, 1941 |
| pump_arbiter.py:1252 BOOLOP | features.py | none | 18, 1606 |
| arbiter_record.py:186 GUARD_OFF | features.py | finite_boundary.py (rc=1 failed=1, 124 s) | 13, 436 |
| pump_arbiter.py:989 GUARD_OFF | features.py | none | 18, 1541 |
| arbiter_record.py:141 RETURN_DEL | solar_alignment.py | solar_alignment.py (1 s) | 1, 1 |
| inputs.py:643 CLAMP_DROP | features.py | none | 22, 1858 |

These are not survivors: each is a measured `killed_by` pin. No survivor was
found, so no survivor triage was owed.

## Numbers (brief step 3)

- 10 sites drawn; 7 are killed only by tests/features.py.
- tests/features.py takes 1616.7 s solo by `recorded_seconds()`. This run's
  pool measured 1697 s for its baseline and 1392 s for its null control.
- Even with both cheaper re-pins, the drive owes 7 mutant runs plus 1 baseline
  plus 1 null control: 9 features.py runs of about 1400–1700 s each, on
  `--jobs 3`. The baseline and null control run only after the first red
  mutant run, one after another on that worker: in this run that was 09:12 to
  10:26, 74 minutes before the null control was settled.
- The cancelled job's log has no per-mutant lines (the table prints at the end),
  so a finish time for the re-pinned drive cannot be predicted from it. The
  2-site re-pin is therefore not claimed to fit. It removes 2 of 11
  features.py runs.

## What would make it fit, none of it this seat's to take

- A lane change: shard or budget the table drive as `mutation-pins` already is
  (`--shard`, `--budget-minutes`), or run the features.py baseline eagerly
  rather than lazily behind the first red mutant run. Either touches
  `tests/mutation_table.py` or `.github/workflows/tests.yml`, outside #3897's
  diff. #3869 hit the same timeout, so the cause is the lane, not this PR.
- Making tests/features.py cheaper: the same lane-level cause.
- Not taken: raising `timeout-minutes`, lowering `--max`, or narrowing
  operators. Each is refused by the brief.

## Comms

`tools/audit/seat/heartbeat.sh` writes `heartbeat/orchestrator`, a ref this
seat may not write, so no heartbeat was pushed. No other in-tree heartbeat,
checkpoint or inbox instrument names a fixer seat.
