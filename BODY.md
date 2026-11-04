R10-HOTFIX-CI-CRITPATH-3. main's required `gate` has been red on every push from 8f286293b on `tests / ci-ratchet`: `GREW critical_path_minutes: 40.817 (budget 34.267, band 1.3)`. 8f286293b is a diff of seven `dev/programme/delivery/*.md` rows, which cannot move CI work.

**What was measured (the orchestrator's hypothesis, re-measured).** Neither of the two suspects holds:
- **Runner queueing is not it.** `run_minutes` already removes each job's queue, and the per-run critical paths it prints are work.
- **No job's work grew.** Each heavy lane is drawn onto a hosted runner that is about 1.9x faster or slower on the same work:
  - `tests / closures` "Re-record the closures" takes 1060–1400 s or 2200–2300 s. On a push it is always the full re-derive (`closure-scope` is skipped).
  - `tests / fast (3.14)` "Run the suite" takes 1034–1163 s or 1880–1986 s.
  - `tests / arch-instrument` takes 1035–1107 s or 1820–1891 s.
  - One slow/quick pair of `fast` logs (c3a279e32 against c7aa12165) both ran 3 lanes and the same 31 scripts. Their per-script ratio has a median of 1.85 (range 1.6–2.9), and the CPU-bound reference solve read 45.0 ms against 18.8 ms.
- **The median read the host draw.** The critical path is a max over three ~18-minute lanes, each slow in roughly 2 runs of 3, so the window's median sat on a slow draw. The last *green* runs already read 39.1–40.1 (907d29f0e, 5e9c39294, c7aa12165).

**Fix (brief arm 2: the statistic, not a raise).** `critical_path_minutes` is now `window_work_minutes` over the newest `PUSH_WINDOW` (8 → 16) push runs, which reads work rather than host speed:
- Each job is priced at its fastest run in the window.
- A run whose work is under a third of that job's window maximum did other work, such as a consumed proof (`tests / coverage` at 4–6 s), and never prices the job.
- Prices are summed along each run's own critical chain (`run_chain`, the walk-back that `run_minutes` already used), and the longest chain is kept.
- A job that grows does so on every host, so its minimum moves. A slow host draw moves it only if every one of 16 runs drew slow.
- A record keeps the largest value that any 16 consecutive runs of its wider window read.
- `run_minutes` is unchanged; its walk is factored into `_walk`, which `run_chain` shares.

The budget is re-recorded at 22.0, a lowering. `critical_path_minutes_band` stays 1.3 and is not widened.

Alternatives considered:
- (1) Cut a job's work. There is no growth to pay.
- (3) Raise to the measured 40.817. That would grade the host fleet, and the next fleet shift would redden main again.
- Window minimum of `run_minutes` alone. All three lanes would have to draw a fast host in one run; that happened in 4 of 14 runs, so `(10/14)^8` ≈ 7% false red.
- Keep the window at 8. Older 8-run windows read 29.8 and 31.2, where one lane drew slow in all 8 runs.

## Head

27d410595fc2db70ea9819669786e1609c4d813d, at merge base c3a279e3252a8b57bb00b5a677318cd4fe20387f (origin/main, unmoved at the prepr.sh run; 2026-11-04 UTC). There was no second prepr.sh run because main had not moved.

## Mutation proof

`python3 -I tests/ci_ratchet.py --self-test` is 48 checks, 0 failed at head. Each production line was mutated on its own and restored by copy:
- `price[name] = min(...)` → `max(...)` (price the host draw): 4 FAIL.
  - "an all-umbrella window ... (its fastest run's 31) -- got 38.0"
  - "a window of slow host draws grades the work, not the draw (32.1, its median 63.9) -- got 63.9"
  - "the grade reads the newest PUSH_WINDOW runs, a record the largest of its every PUSH_WINDOW-run window (32.1, 63.9)"
  - "derive grades the newest window and a --record derive writes the largest window"
- Other-work floor dropped (`min(seen)`): 1 FAIL, "a run under a third of the job's window maximum did other work and never prices it (63.9, not 5.3) -- got 31.2".
- Record reads only the newest window (`if stat == "record"` → `if False`): 2 FAIL, the record check and the derive check.
- `PUSH_WINDOW = 8`: 2 FAIL, "--gather-runs keeps the newest PUSH_WINDOW (16) ... -- n=8" and "a window of slow host draws grades the work ... -- got 63.9".
- Chain links dropped in `_walk` (`pred = None`): 5 FAIL. The grade read 31.8 instead of 32.1, and the 5-minute growth read 36.8 instead of 37.1.

## Null control

The same statistic was run over every 16 consecutive runs of the 28 completed ci.yml push runs on main, 41345365297 (56630e7e6) to 41577822624 (c3a279e32). That span covers 2026-11-01 to 11-03, green to red. The only CI-bearing merge in it is dfb4ce2b5's action pin bump, which changes no job's work: quick runs fall on both sides of it.
- The old median read 34.275 → 39.367, going red with no work added.
- `window_work_minutes` read 19.95–22.0 over the same windows, and fell rather than grew toward the newest.
- **Planted perturbation:** +300 s added to every `tests / closures` run raises the 8-run windows by exactly 5.0 min wherever the closures chain is the longest, for example 20.0 → 24.017 at the window starting at b8e823699.
- In-tree pins of the same pair are the self-test checks "a window of slow host draws grades the work, not the draw" (null) and "a job grown by 5 minutes on every host grows the grade by 5 (37.1)" (perturbation).
- `dev/audit/harnesses/r10_u9a_ratchet_nulls.py` reads the same at both ends: `script_runs_per_push=54`, and its critical-path arm refuses with "carries no jobs list" at origin/main and at head alike. That arm's fixtures predate the jobs requirement; this PR does not change that.

## Figures

- Self-test 48/0, and every mutation above: `python3 -I tests/ci_ratchet.py --self-test`
- Per-run work, chain, and the grade/record of 19.95/22.0: `python3 tests/ci_ratchet.py --gather-runs runs.json --window 28` (CI's gh token; this seat assembled the same `runs.json` from the jobs API), then `critical_path_minutes(Path("runs.json"))` and `critical_path_minutes(Path("runs.json"), "record")` from `tests/ci_ratchet.py`.
- Sliding windows, old median against new: `window_work_minutes(runs[i:i+16])` and the median of `run_minutes` over the same slice, from `tests/ci_ratchet.py`.
- Per-step and per-job durations, the ~1.9x split and the 4-of-14 quick paths: the jobs API's `steps[].started_at/completed_at`, read through `tools/audit/seat/ci_critpath.py`'s rule (duration = end − start).
- Per-script ratio 1.85 and the reference solve 45.0/18.8 ms: run.sh's "wall clock" table and the solve-time guard lines in the job logs of `fast` jobs 125725515225 (c3a279e32) and 125112098863 (c7aa12165).
- Architecture score: `python3 tools/audit/archscore/score.py --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f`
- `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED.
- `tools/pr/prepr.sh` reported rc=0 and MODE: SCOPED; `python3 tests/closure.py select` scoped the gate to `tests/entities.py`.

## Raise justification

This row is a lowering: `critical_path_minutes` goes 34.267 → 22.0 under a new statistic. `critical_path_minutes_band` stays 1.3, and no row rises. The commit message carries the re-record reason.
- Payments tried: (1) cutting a grown job's work, refused because no job grew (uniform 1.6–2.9x per-script host ratio, same scripts, same 3 lanes); (2) fixing the statistic, taken; (3) raising to 40.817 under mandate 6329234399, refused because it would grade the host fleet.
- Architecture score: dS +0.0000 NULL

## Red checks

`tests / ci-ratchet`, and with it `gate`, red on main from 8f286293b. This is the third red of this ratchet: CRITPATH-1, CRITPATH-2 at 05c0d6d5d, and this one. This body names the trigger only; a separate root-cause seat owns the analysis.
- **The cheaper detector:** a host-speed invariance fixture in `ci_ratchet.py --self-test`, which runs in about 1 s locally and in the job's own self-test step. It feeds the statistic the same work on hosts 2x apart and requires the grade not to move. It is added here, and the median it replaces fails it ("got 63.9").
- **The fleet shift itself has no cheaper detector:** only push runs on hosted runners measure it, and the ratchet is that measurement.

## Forward-carry

none

## Friction

none
