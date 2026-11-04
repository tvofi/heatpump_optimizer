Fix review: blocked 563c8e6db0eec229e3d5b402c263092722905f31 claim-refuted: one run of a heavy lane above 3x its window-fastest lifts the other-work floor over every fast run and moves the grade +6.95 min past the 1.3 band with no work grown

bus-nonce: aba665df86ca0b3a865b9dc16170c83a

Round 1. Head measured: 563c8e6db0eec229e3d5b402c263092722905f31 (authored code head 27d410595), merge base c3a279e3252a8b57bb00b5a677318cd4fe20387f, origin/main unmoved. `git diff <merge-base>...origin/main -- dev/governance/roles/` empty: contract current.

## Block

The body and the new `window_work_minutes` docstring claim the grade reads work, not host speed: "a job that drew a slow host does not move it unless it drew one in every run of the window" / "A slow host draw moves it only if every one of 16 runs drew slow". Planted on the real 16-run window (the 40 newest ci.yml push runs on main, gathered at this review, `ev/runs40.json`), that is false:

- One outlier. The newest run's `tests / fast (3.14)` set to 3.2x the window's fastest `fast` run (one slow or hung draw, nothing else changed): grade 21.717 -> 28.667, +6.95 min, GREW on 22.0 + 1.3. The cause is `floor = max(seen) * OTHER_WORK_FRACTION`: the floor keys on the window **maximum**, the least robust order statistic, so a single slow run past 3x the fastest re-classifies every genuine fast run as "other work" and prices the job on a slow draw. The same shape is already in the data on a lane off the critical chain: `tests / coverage` max 3070 s (a failed run, a9c149289) puts its floor at 1023 s and excludes completed runs of 690-901 s.
- 15 of 16 slow. Each fast draw of `tests / closures` in the newest 15 runs made slow (x1.9, slow draws untouched): 21.717 -> 28.133 (+6.4); `fast` -> 28.667; `arch-instrument` -> 25.933. The fleet is not two-speed (closures reads 1117, 1234, 1245, 1306, 1449, 1608, 1613 s ... 2401 s), so losing the single fastest run reprices on a mid host; "every one of 16 runs drew slow" assumes a two-speed draw the data do not show.
- With the floor taken off the window median instead of the maximum, and only `success` job conclusions pricing, the same single 3.2x outlier moves nothing on any of the three lanes (20.75 -> 20.75) while +300 s on every closures run still moves it +3.23 (ev/perturb_oldmedian_variant.txt; my variant, not a prescription). The repair is local to `window_work_minutes`.

This is the false-red class this PR exists to remove (host draw read as growth), reintroduced through one outlier rather than a median. The self-test pins the floor only against a low "other work" run; it has no high-outlier case, which is the cheap detector the body's own Red-checks section prescribes (feed the statistic the same work with one host far slower; require the grade not to move).

## Findings

- Detection lag, undisclosed: real growth moves a window-minimum only once every pre-growth fast run has aged out. +300 s on `tests / closures` in only the newest k runs reads 21.717 at k = 1, 4, 8; 23.1 at k = 12; 24.95 at k = 15-16 (`fast`: no move until k = 15). The body's planted perturbation adds +300 s to every run of the window, which hides this. The retired median-of-8 also lagged (closures +300 moved only at k = 8), so it is a doubling, not a new defect, but the red now lands 12-16 merges after the cause; the body and docstring should state it. Carry: R10-HOTFIX-CI-CRITPATH-3
- `critical_path_minutes_band` 1.3 was measured on the retired statistic and not re-measured: the new statistic's own window-to-window spread is 19.95-22.0 per the body (2.05) and 20.817-22.0 over the 25 windows of my 40 runs. Recording at the window maximum makes 1.3 above it a plausible margin, but no measurement in the body says so. Carry: R10-HOTFIX-CI-CRITPATH-3
- Cancelled and failed jobs price: `_walk` drops only `skipped`, so a cancelled job truncated above a third of the window maximum would set the job's price low (under-reads the grade, and a record taken over it records too low). No instance moved the grade in the 40 runs (planted: one closures run cancelled at 45% -> no move, because a faster complete run was present). Carry: R10-HOTFIX-CI-CRITPATH-3
- No committed harness exercises the critical-path statistic on real runs: `dev/audit/harnesses/r10_u9a_ratchet_nulls.py`'s critical-path arm refuses at both ends ("carries no jobs list"), per the body. The figures here come from my own instrument (ev/gather.py, an*.py, pert*.py), disclosed as mine. Carry: R10-HOTFIX-CI-CRITPATH-3

## Evidence

- RESULT self-test at head: 48 checks, 0 failed (ev/selftest_head.txt).
- RESULT mutation proof re-run (ev/mutations.txt): min->max 4 FAIL; floor removed 1 FAIL; PUSH_WINDOW 8 2 FAIL; `pred = None` crashes the self-test (TypeError). Matches the body's counts except the last (body: 5 FAIL; here an exception), not vacuous.
- RESULT real data, 40 newest ci.yml push runs on main (41363452534..41577822624, gathered unauthenticated from the public jobs API through gather_runs with a curl runner, ev/gather.py): grade (newest 16) 21.717; record over 40 = 22.0 (window starting 38dcb6c5d). 22.0 reproduces as the maximum; the body's lower end 19.95 lies in older windows I did not fetch (unauthenticated rate limit), not re-derived.
- RESULT old median-of-8 over the same newest 8: 37.959; sliding 8-run medians 33.77-40.91 (ev/windows_and_jobs.txt): the median read red with no growth, confirming the body's diagnosis.
- Runner-speed claim re-derived from job durations, not logs: per lane, completed work is bimodal-plus-middle: closures 1117-1613 s vs 2040-2401 s; fast 1064-1223 vs 1928-2094 (1493-1811 between); arch-instrument 1010-1149 vs 1739-1965. Chains are prelude->closures|fast->ci-ratchet in most runs. Queueing is removed by run_minutes. I did not re-read the per-script wall-clock tables or the 45.0/18.8 ms solve lines: not re-derived.
- Remove the mechanism (price = max): the self-test goes red 4; on real data the lowering 34.267 -> 22.0 is the statistic, earned by the change of statistic, not gamed; the block is on the statistic's robustness, not on the re-record.
- First push after merge: ci-ratchet on the merged tree would gather the 16 newest completed push runs (all pre-merge) and read 21.717 <= 22.0: PASS, so main would go green - as long as no single heavy lane in the window exceeds 3x its fastest.
- RESULT merge-tree vs origin/main c3a279e32: clean, rc 0, tree 888422bcb (ev/merge_tree.txt).
- VERSION, manifest version and notes heading untouched (diff is 3 files: delivery row, ci_budgets.json, ci_ratchet.py).
- Red checks: `tests / nightly-status` red; the diff touches none of what it reads (only its own new delivery row), so it is main's. `tests / ci-ratchet` red on main is named and answered in the body.
- RESULT CI on this head: `merge_train.py classify 563c8e6db0eec229e3d5b402c263092722905f31 --pr 3180` exit 0 at 06:51:35Z: "GREEN 563c8e6db0eec229e3d5b402c263092722905f31 pending: none red: none" (ev/classify.txt). Head and origin/main re-read after: unmoved (563c8e6db, c3a279e32). CI green does not exercise the block: CI grades the statistic on push runs only, and the planted outlier is not in the current window.
