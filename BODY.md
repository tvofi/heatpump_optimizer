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

**Repair round 3** (review of 3f7777a59, `blocked`, ci-red). The statistic and the recorded value are unchanged. The round-2 head added `dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py`, which turned two required lanes red:
- `tests / fast (3.14)`: `tests/harness_headers.py`'s depth-seam check refused `ROOT = HERE.parents[3]`. The harness now inlines the canonical `repo_root` (byte-identical to `tools/audit/repo_root.py`'s) and roots itself with `repo_root(__file__)`.
- `tests / closures`: `INERT READS UNDER-APPROXIMATED`, because `harness_headers.py`'s child scan reads every harness and the committed `inert_reads` did not list the new one. `tests/closures.json` now lists it under `tests/harness_headers.py`. `tools/pr/ci_predict.py --apply-inert` predicted nothing here (the read is a child's, seen only under `strace -f`), so the entry was written by hand and checked against a Linux `strace` recording (below).
- The review's three carried findings on `tests/ci_ratchet.py`:
  - The two docstring citations named `dev/audit/harnesses/r10_hotfix_ci_critpath_3.py`, which does not exist; both now name `.../r10_hotfix_ci_critpath_3/replay.py`.
  - `OTHER_WORK_FRACTION`'s level had no self-test check (the 1/3 -> 1/2 mutant passed 52/52). A new check prices a job at 30.0 in fourteen runs, 12.0 in one and 9.0 in one: a third reads 12.3, a half would read 30.3, a quarter 9.3, so the level is pinned from both sides.
  - `window_work_minutes`' docstring now discloses that success-only pricing lets a failing chain job under-read, and a record taken across such a stretch is recorded low. On this PR's runs.json, `tests / ci-ratchet` concluded `failure` in all 16 newest runs, so it prices 0: the newest window reads 20.75, and 21.7 with those 16 failures read as successes. After merge, ci-ratchet's first success starts pricing again; the reviewer measured the second post-merge push at 22.35, under 21.983 + 1.3 = 23.283 (not re-derived here).

## Head

543fa4f7ac4cb52d879297f4d2c7eb81a9e45d2e, one commit on the PR head 3f7777a59bc0f95fc47885e68e3f6d4e39e60d55, at merge base c3a279e3252a8b57bb00b5a677318cd4fe20387f. origin/main re-read unmoved at c3a279e32 (2026-11-04T08:12:18Z); `git merge-tree --write-tree origin/main HEAD` is clean, so no merge and a single prepr.sh run.

## Mutation proof

`python3 tests/ci_ratchet.py --self-test`: 53 checks, 0 failed at head. Each mutant applied alone and restored by copy:
- `OTHER_WORK_FRACTION = 1 / 3` -> `1 / 2`: 1 FAIL, "the other-work floor sits at a third of the window median (12.3: a half would read 30.3, a quarter 9.3) -- got 30.3".
- `OTHER_WORK_FRACTION = 1 / 3` -> `1 / 4`: 1 FAIL, the same check, "-- got 9.3".
- Round 2's four mutants (floor median -> max, priced `!= "skipped"`, no-conclusion refusal off, floor dropped) touch unchanged lines and checks; the reviewer re-ran them at 3f7777a59, each killed.
- The harness repair's mutant is the round-2 head itself: `tests/harness_headers.py` at 3f7777a59 prints `1 of 112 HARNESS HEADER CHECKS FAILED` on the depth seam `replay.py:40: ROOT = HERE.parents[3]`; at head, `ALL 112 HARNESS HEADER CHECKS PASSED`.

## Null control

- **Harness headers, both ends:** `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`, exit 1 at 3f7777a59 (the CI red, reproduced locally), exit 0 at head.
- **INERT read, both ends:** `python3 tests/closure.py record --out-dir R tests/harness_headers.py` under `strace` (Linux, `/usr/bin/strace` present), then `python3 tests/closure.py check --in-dir R --partial`:
  - with this head's `tests/closures.json`: rc 0, "committed closures cover every file this run touched";
  - the same recording against the closures.json without the new entry: rc 1, `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py`, the CI red.
  - This is one script's recording, not a full re-derivation; CI's Linux recording is authoritative.
- **Fraction check:** the new check reads 12.3 at a third and fails at a half (30.3) and a quarter (9.3), above.
- **Replay:** `python3 dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py` at head, runs.json sha1 5ac806dd6f5e4a80ea8af04ea0b4431a32f153b7: `RESULT: holds`, exit 0, every line identical to round 2's (the repair moved its root lookup, not a figure). Against 563c8e6db's ratchet it read `RESULT: does NOT hold` (round 2, re-run by the reviewer).
- **Success-only disclosure:** 20.75 at head; 21.7 with the newest 16 runs' `tests / ci-ratchet` failures read as `success`, a scratch call of `window_work_minutes` on a copy of runs.json.

## Figures

- Self-test 53/0 and the two fraction mutants: `python3 tests/ci_ratchet.py --self-test`.
- Grade 20.75, windows 19.967..21.983, record 21.983, band need 0.55 (rule: the maximum over windows i of window_i minus the max of windows before i, chronological), the outlier, lag and slow-fleet tables: `replay.py` above.
- runs.json: the 40 completed ci.yml push runs on main 41363452534..41577822624, unchanged from round 2 (sha1 above).
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED; 138 s wall at 3f7777a59 in this container (the standing cost of the cheaper detector below).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2602 ENTITY CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Architecture score: `python3 tools/audit/archscore/score.py --diff c3a279e3252a8b57bb00b5a677318cd4fe20387f` printed dS +0.0000 NULL.
- Gate scope: `python3 tests/closure.py select --diff c3a279e32...` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`: `tests/entities.py`, which passed. `tests/harness_headers.py` is not in `scope.run`; it was run by hand above, because a scoped run of one script is what hid the round-2 red.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: "no closures, fast, governance or instrument red predicted", both before and after the repair; it did not predict the round-2 INERT read.
- Carried from round 1, not re-read: per-script ratio 1.85 and solve 45.0/18.8 ms (`fast` jobs 125725515225 and 125112098863).

## Raise justification

No row rises. `critical_path_minutes` stays at 21.983 (lowered from main's 34.267 in round 2) and `critical_path_minutes_band` at 1.3; this round changes no budget.
- Payments tried: (1) cutting a grown job's work, refused because no job grew; (2) fixing the statistic, taken; (3) raising to 40.817, refused because it would grade the host fleet.
- Architecture score: dS +0.0000 NULL

## Red checks

- **`tests / fast (3.14)`**, **`tests / closures`** and **`tests / closures-autofix`** were red at 3f7777a59 (CI run 41790799421), all from the new `replay.py`: its depth root failed `tests/harness_headers.py`, and harness_headers' child read of it was missing from `inert_reads`; closures-autofix failed and repaired nothing. Cause: the scoped local gate ran only `tests/entities.py` (`MODE: SCOPED -- 1 script(s) run`), and `ci_predict.py` cannot see a child's read, so neither instrument named the script that reddens.
  - **Cheaper detector:** `python3 tests/harness_headers.py`, run locally on any diff adding a file under `dev/audit/harnesses/`; 138 s wall here, against a CI round trip. It already exists and needs no build: `tests/run.sh` runs it as a `run_always` line on every gate, scoped or not, and `fixer.md` step 5 already requires a seat to run the `run_always` lines beside `scope.run`. The round-2 head ran `scope.run` alone. Process state: detector existed, not run. No countermeasure is built here, so nothing is carried.
- **`tests / ci-ratchet`**, and with it `gate`, has been red on main from 8f286293b on host draw; this PR is its fix. Root cause is the RCA seat's (r10-rca-ci-critpath-3).
  - **Cheaper detector:** the self-test's host-invariance fixtures, about 1 s locally.
- **`tests / nightly-status`** grades main, not this branch. The diff touches nothing it reads.

## Forward-carry

none

## Friction

none
