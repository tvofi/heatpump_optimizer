R10-HOTFIX-CI-CRITPATH-3. main's required `gate` has been red on every push from 8f286293b on `tests / ci-ratchet`: `GREW critical_path_minutes: 40.817 (budget 34.267, band 1.3)`. 8f286293b is a diff of seven `dev/programme/delivery/*.md` rows, which cannot move CI work.

**What was measured.** Runner queueing is not the cause: `run_minutes` already removes each job's queue. No job's work grew either. Each heavy lane draws hosted runners of different speed on the same work. On a slow/quick pair of `fast` logs (c3a279e32 against c7aa12165), both running the same 31 scripts on 3 lanes, the per-script ratio had a median of 1.85 (range 1.6–2.9), and the CPU-bound reference solve read 45.0 ms against 18.8 ms. The fleet is **not two-speed**: over the 40 runs this PR carries, `tests / closures` reads 1117–1613 s, 2040–2401 s, and values in between. The critical path is a max over three ~18-minute lanes, so the median of per-run paths sat on slow draws.

**Fix: change the statistic, not raise the budget.** `critical_path_minutes` is now `window_work_minutes` over the newest `PUSH_WINDOW` (16) push runs:
- Each job is priced at its fastest **`success`** run in the window. A run under a third of the job's window **median** did other work (for example a consumed proof) and never prices the job.
- Prices are summed along each run's own critical chain (`run_chain`), and the longest chain is kept.
- A record keeps the largest value any 16 consecutive runs of a wider window read.

**Repair round 2** (review of 563c8e6db, `claim-refuted`). The round-1 floor was keyed on the window **maximum**. One run of a lane above 3x its fastest lifted the floor over every genuine fast run, which moved the grade +6.95 with no work grown.
- The floor is now the median of the job's `success` runs.
- Cancelled and failed jobs never price, and a ran job with no conclusion refuses.
- The round-1 claim "a slow host draw moves it only if every one of 16 runs drew slow" was false. The docstring now states what the minimum costs:
  - Losing the fastest draws reprices the job on a mid host.
  - 15 of 16 runs drawing slow moves the grade as growth would.
  - Growth reads only once it fills most of the window.

Candidates measured on the same 40 runs with the replay's perturbations. The figures are a scratch run of `replay.py`'s arms with the pricing rank swapped. Only A and B are in the committed harness: A is its `retired` arm and B is production.

| statistic | 25-window range | 3.2x outlier on `fast` | +300 s on closures, all 16 runs | verdict |
|---|---|---|---|---|
| A: max-keyed floor, minimum price (round 1) | 20.817–22.0 | **+6.95** | +2.283 | lost: one outlier moves it |
| **B: median-keyed floor over `success`, minimum price** | 19.967–21.983 | **+0.0** | +3.233 | **taken** |
| C: same floor, second-fastest price | 21.95–27.7 | +0.0 | **+0.0** | lost: blind to closures growth (a mid-host `fast` price dominates the chain) |
| D: same floor, lower-quartile price | 23.283–30.583 | +0.0 | **+0.0** | lost: same blindness, wider spread |
| M: same floor, median price | 33.008–40.583 | +0.0 | +5.0 | lost: reads the host draw again (the original red) |

B is the reviewer's variant. Measured here, it reproduces the reviewer's figures: 20.75 unmoved under the outlier, and +3.23 under +300 s on every closures run.

**Detection lag, disclosed (k = the newest runs carrying the growth; new / retired round-1 statistic):**
- +300 s on `tests / closures`: k=1, 4, 8 read +0.0/+0.0; k=12 reads +1.383/+1.383; k=15 and 16 read +3.233/+2.283.
- +300 s on `tests / fast (3.14)`: nothing moves until k=15, which reads +5.0/+4.05.

The red lands 12–16 merges after the cause. The retired median-of-8 moved at k=8 (reviewer's measurement), so the lag roughly doubles. That is the price of reading work instead of host draw.

**Slow fleet, disclosed:** when every fast draw in the newest 15 runs is made 1.9x slower, the grade moves +6.417 (closures), +6.95 (fast) and +5.167 (arch-instrument). A minimum prices the fastest host the window drew; no candidate above both ignores this and still detects growth on every lane.

The budget is re-recorded at **21.983**, a lowering from main's 34.267 (round 1 had 22.0). `critical_path_minutes_band` stays 1.3: its need under a max-recorded budget is how far a window reads past the record of every earlier window, which is 0.55 over the 25 windows.

## Head

e1637032a0f3040b8dadc34647c6b47b7b5c730e, at merge base c3a279e3252a8b57bb00b5a677318cd4fe20387f (origin/main, re-read unmoved at 2026-11-04T07:06:55Z). This was a single prepr.sh run with no merge, because main did not move.

## Mutation proof

`python3 tests/ci_ratchet.py --self-test`: 52 checks, 0 failed at head. Each mutant was applied alone and restored by copy (`cmp` identical):
- floor `statistics.median(seen)` → `max(seen)`: 1 FAIL, "one run of a job past three times its fastest does not move the grade (32.1, not 102.1)".
- `"priced": conclusion == "success"` → `!= "skipped"`: 2 FAIL, "a failed job never prices (32.1, not 15.3)" and "a cancelled job never prices (32.1, not 31.95)".
- the no-conclusion refusal → `if False:`: 1 FAIL, "a ran job with no conclusion refuses (whether it prices is unknown)".
- floor dropped (`min(seen)`): 1 FAIL, "a run under a third of the job's window median did other work and never prices it (63.9, not 5.3)".

Round 1's mutants (min→max, record window, `PUSH_WINDOW = 8`, `pred = None`) touch unchanged lines and checks.

## Null control

- **Harness, at both ends:** `python3 dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py`, with runs.json sha1 5ac806dd6f5e4a80ea8af04ea0b4431a32f153b7.
  - At head it prints `RESULT: holds`, exit 0. The three lanes' 3.2x outlier reads +0.0/+0.0/+0.0.
  - Run against 563c8e6db's `tests/ci_ratchet.py` and `ci_budgets.json`, it prints `RESULT: does NOT hold`, exit 1. The outliers read +0.183 (closures) and +6.95 (fast), the reviewer's figure.
  - At 563c8e6db, the harness's `retired` arm reads identically to production on every line. That check is the arm's own null: it reproduces the statistic it names.
- **Outlier against growth:** an outlier must read +0.0, and +300 s on every run must read ≥ +3.0. Both are asserted. The second is the first's perturbation; a statistic that ignored everything would pass the first and fail the second.
- **Self-test, on synthetic runs:**
  - "a window of slow host draws grades the work, not the draw" is the null.
  - "a job grown by 5 minutes on every host grows the grade by 5 (37.1)" is the perturbation.
  - "one run ... past three times its fastest does not move the grade" is the new null.
- `dev/audit/harnesses/r10_u9a_ratchet_nulls.py`'s critical-path arm still refuses on "carries no jobs list" at both ends. Its fixtures predate the jobs requirement, and this PR leaves it alone. The new replay is the committed harness for the statistic on real runs.

## Figures

- Self-test 52/0 and the four mutants: `python3 tests/ci_ratchet.py --self-test`.
- Grade 20.75 and record 21.983: `critical_path_minutes(Path("dev/audit/harnesses/r10_hotfix_ci_critpath_3/runs.json"))` and the same call with `"record"`, from `tests/ci_ratchet.py`.
- The 25-window range 19.967–21.983, the band need 0.55 (rule: the maximum over windows i of window_i minus the max of windows before i, chronological), the outlier, lag and slow-fleet tables: `replay.py` above.
- runs.json holds the 40 completed ci.yml push runs on main, 41363452534..41577822624. They are the union of the reviewer's ev/runs40.json and the RCA seat's runs.json (its 31 runs are a subset; 0 job-count mismatches on the overlap), cut to the fields `_walk` reads.
- Candidates C, D and M in the table: a scratch variant of the same replay with the price rank swapped, not committed.
- Per-script ratio 1.85 and solve 45.0/18.8 ms: run.sh's wall-clock table and the solve-time guard lines in `fast` jobs 125725515225 (c3a279e32) and 125112098863 (c7aa12165), carried from round 1 and not re-read.
- `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED.
- Architecture score: `python3 tools/audit/archscore/score.py --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f` printed dS +0.0000 NULL.
- Gate scope: `python3 tests/closure.py select --diff c3a279e32...` printed `MODE: SCOPED -- 1 script(s) run`: `tests/entities.py`, which passed. `tools/pr/ci_predict.py` predicted no closures, fast, governance or instrument red.

## Raise justification

No row rises. `critical_path_minutes` is lowered 34.267 → 21.983 under the new statistic, and `critical_path_minutes_band` stays 1.3, so the commit message carries the re-record reason.
- Payments tried: (1) cutting a grown job's work, refused because no job grew; (2) fixing the statistic, taken; (3) raising to 40.817, refused because it would grade the host fleet.
- Architecture score: dS +0.0000 NULL

## Red checks

- **`tests / ci-ratchet`**, and with it `gate`, has been red on main from 8f286293b. This is the ratchet's third host-draw red; root cause is the RCA seat's (r10-rca-ci-critpath-3).
  - **Cheaper detector:** the self-test's host-invariance fixtures, about 1 s locally. This round adds the high-outlier fixture the round-1 body prescribed but lacked.
  - **The fleet shift itself** has no cheaper detector than push runs on hosted runners.
- **`tests / nightly-status`** grades main, not this branch. The diff touches nothing it reads.

## Forward-carry

none

## Friction

none
