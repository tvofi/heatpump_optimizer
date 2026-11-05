R10-HOTFIX-CI-CRITPATH-5: main's `tests / ci-ratchet` is red on `critical_path_minutes` (23.351 at 788e8ceed, run 42022036882; 23.43 at 7af0c2a79; 23.574 at b707d8932 and at 8bf45e5dc, run 42038071453; budget 21.983, band 1.3). Fifth critical-path hotfix; a root-cause seat is owed, ruled separately.

**Cause.** The chain is `prelude` -> `tests / closures` -> `tests / ci-ratchet`. No job's work grew in the diff: 0ae75bf31..788e8ceed touches only `tools/` shell files (`app_push.sh`, `prepr.sh`, `body_push.sh`, `open_pr.sh`, `pr_args.sh`, `update_pr.sh`, a delivery row). `closures` reference work (host-probed seconds) read 1330 at 0ae75bf31 (run 42007732815) and 1307 at 8bf45e5dc (run 42038071453); its 15-run median is 1318 (range 1191..1455). The ratchet was already at the band edge: replayed from job timings, the window ending at 0ae75bf31 reads 23.287 against the 23.283 limit. A few slower closure draws tipped it over; it is a window draw, not a regression. The `closures` lanes are balanced (`lane-plan --all-scripts`: 1484.4 / 1484.3 / 1484.4 s recorded) at the owner's 3-lane CI cap, so no rebalance exists.

## Head

Code head 8ba10ac7c2bd02b94bd118db293a63dad7b96c24, one change on 8bf45e5dc (origin/main when cut).

## Mutation proof

The change is a workflow edit; no test script reads the step. Mutation on the model instead: reverting the step merge (the two fetches back in sequence) reads 23.519 in the replay below, the merged form 23.236. CI alone grades the real value.

## Null control

Unmodified tree: CI printed GREW 23.574 (run 42038071453). Ratchet refusal control: `compare({'critical_path_minutes':21.983,'critical_path_minutes_band':1.3}, {'critical_path_minutes':23.6})` returns `GREW ... exit 1`, and 23.2 returns `ok`, so the ratchet still refuses growth past budget + band.

## Figures

- Replay of the window from job timings (15 completed runs 42038071453..41964543258 plus 4 older, fetched through the Actions API): `python3` calling `tests/ci_ratchet.py` `window_work_minutes`; newest 16 read 23.519 (CI printed 23.574: its window also holds one cancelled run), the 0ae75bf31 window read 23.287.
- Modelled saving of the concurrent fetch: each run's `tests / ci-ratchet` completion pulled in by `min(gather step, fetch step)`, same function: 23.236. That sits 0.047 under the 23.283 limit and about 0.1 under CI's own offset of +0.055, so it is not trusted to turn the check green alone; hence the re-record.
- Lane balance: `CI=true python3 tests/closure.py lane-plan --all-scripts` (1484.4/1484.3/1484.4 s).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/ci_ratchet.py --self-test`: 65 checks, 0 failed. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. Scope: `MODE: FULL` (the diff touches `.github/workflows/tests.yml`); `tests/entities.py` ran locally with no FAIL/REFUSE lines.

## Raise justification

Payments tried, in order:
1. Real path cut, paid: the ratchet job's two independent network steps (metrics artifacts 24-40 s, push runs 22-40 s, measured per run) now run side by side in one step with per-pid `wait`; the chain's tail job is that job. Models to 23.236 (above), about 0.3 min, insufficient to count on.
2. Rebalance closures lanes: none, already balanced to 0.1 s.
3. A fourth CI lane: refused, the 3-lane cap is the owner's standing rule.
4. Splitting `closures` into shards: `tests / closures` is a required context whose check needs every recording; not verifiable without CI iterations; not attempted.
Architecture score: dS +0.0000 NULL for the diff (score.py --diff). Re-record: `critical_path_minutes` 21.983 -> 23.574, the value CI printed, never a headroom; band 1.3 unchanged. `tests/ci_budgets.json` is a `*_budgets.json` raise, under mandate 6624093439.

## Red checks

`tests / ci-ratchet` on 8bf45e5dc (run 42038071453): GREW critical_path_minutes 23.574, the subject of this PR. No other concluded red read from this seat (Actions API; runs 42038071453 job list).

## Forward-carry

none

## Friction

none
