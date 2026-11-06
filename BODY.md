## Re-cut

This body replaces the earlier one, whose figures were false ("0 of 51" offenders, "ref53 has no new draw"). Nothing in it is carried from that body: every figure below was re-derived at the code head by the commands under `## Figures`. The code is unchanged by this re-cut. The scope is only the round-3 blocked finding of the fix review (verdict/3234): a ref46 runner whose ruler drifts to ref_ms >= 49.60 was graded on ref53's cpu budget 2.081 and went red (CI job 127046649273, run 41966183843, cpu_ratio 2.256). Every other finding of that verdict moves to `## Forward-carry`.

The border fix is the grading unit. The lane grades a job on the median of its rulers over the clean run and the three doubled arms (`job_rulers`), not on one run's ruler, and the classes are cut by a stated rule from every committed CI draw (`derive_cost_classes`). Job 127046649273's own runs read 47.28-50.94; its median is 50.07, inside ref47 (42.96-51.12), whose budget is 3.3424.

## Head

Code head: 130769e1db383e4c6e98b01c4a90b31173693cb7 (the handoff code, `origin/main` 7e8939d38 merged in; the merge touches only `dev/programme/delivery/3239.md` and the roster). The PR head 4512d770 differs from it only by this re-cut's body-only churn and the delivery row. Everything below was measured on a checkout at 130769e1.

## Mutation proof

Mutant, applied in a script and not committed: `draw_rulers` returns each job's single clean-run ruler instead of the pooled median (the pre-fix grading). Result: `control:cycle_cost:class_rule`, `control:cycle_cost:draws` and `control:cycle_cost:lane_prints_notice` go red (3 of 36 controls). Unmutated: 36 controls, none failing.
The draw also fails the old code. At 009edde6, `class_budget('synthetic-dhw-only.json', 50.94)` returns cpu_ratio 2.081, and 2.2558 offends `cpu_ratio 2.256 over its budget 2.081`, the CI job's own message.

## Null control

The block draw, graded at 130769e1 with `replay_draws.py grade --job 127046649273`:
- clean: passes, in class ref47 (ruler 50.07, loop_ref_ms 159.5), cpu_ratio 2.2558 under 3.3424.
- doubled arms, each still red: cpu `cpu_ratio 4.444 over its budget 3.342`; loop `loop_cpu_ratio 0.2063 over its budget 0.1527`; memory `peak_kib 3861 over its budget 2686`.
- each doubled arm graded as if it were the clean run (`--clean-from cpu|loop|memory`) is refused on its own metric.
Moved over the border, the draw is still refused and named, which is what `control:cycle_cost:draws` pins: at `--ruler 51.5` (class ref53) the clean run reads `cpu_ratio 2.256 over its budget 2.076`. A job whose median ruler is >= 51.12 is therefore graded as ref53, and ref53's population (11 jobs, cpu 1.4437-1.4926, all 2026-10-31 to 2026-11-02) is not that runner's. That residual is not claimed fixed; it shows in `control:cycle_cost:draws` as a named null.

## Figures

- `python3 tools/audit/seat/replay_draws.py grade --job 127046649273` prints the clean pass in ref47 at ruler 50.07 and the three doubled arms refused, with the budgets quoted above.
- `python3 tools/audit/seat/replay_draws.py grade --job 127046649273 --ruler 51.5` prints the moved-draw refusal, `cpu_ratio 2.256 over its budget 2.076`.
- `python3 tools/audit/seat/replay_draws.py grade --job 127046649273 --clean-from cpu` prints each doubled arm refused when graded as clean.
- Offenders over the committed draws: `python3 -c "import sys; sys.path.insert(0,'tests'); import replay as R; print(len(R.draw_offenders(R.cost_draws())))"` prints 0, over 116 synthetic clean jobs / 217 job-fixture groups / 565 runs in `tests/replay_cost_draws.tsv` (created 2026-10-31T02:21Z to 2026-11-06T09:07Z). This is the committed set, not a window of the 800 most recent runs; the verdict counted 78 in-window jobs and I have not re-listed them.
- Class populations of the synthetic clean cpu_ratio by the job's ruler, same set: ref23 18 jobs 1.9586-3.5974; ref28 2; ref31 33 1.7608-3.0694; ref38 2; ref40 2; ref47 48 jobs 2.2558-2.4762; ref53 11 jobs 1.4437-1.4926. Only 127046649273 sits in ref47 at a ruler >= 49.5.
- Controls: a script calling `replay.controls()` at 130769e1 printed `36 controls; failing: []`, including `ok control:cycle_cost:class_rule`, `ok control:cycle_cost:draws`, `ok control:cycle_cost:band_edges` and `ok control:cycle_cost:lane_prints_notice`.
- `python3 tools/audit/carry_audit.py check --body <body> --branch fix/r10-replay-cost-budget-r2` and `HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh --body-check <body>` are run on this body; their lines are in the return message.

## Red checks

The head's check runs (60 over all pages, runs 42214980826 and 42216249923 at 4512d770):
- `gate` failed twice (jobs 127883402959 at 12:07Z and 127887727966 at 12:17Z). Its log reads `FAIL run(s) [42214980826] at this head are still being judged; their gate decides`: it refuses while the ci.yml run is in progress, and no test failed. Cheaper detector: none needed; the gate re-runs when ci.yml concludes. This is not a finding about the code.
- Everything else concluded success or skipped; `tests / coverage`, `tests / closures`, `tests / fast (3.14)` and `governance / instrument-self-tests` were still in progress when read. `tests / replay` concluded success (job 127882978123). `tests / nightly-status`, red at 009edde6, is success at this head.
No code-scanning alert is open on the head (`CodeQL` and the three `codeql / Analyze` checks succeeded).

## Forward-carry

- Loop-ruler outlier: job 127310664875 (run 42046303116, PR 3198) read clean `loop_cpu_ratio 0.0594` at `loop_ref_ms 279.78` (others 131-176) and the lane refused it, `budget 0.1278 cannot see a 2x cycle`; destination tests/replay.py. Carry: R10-REPLAY-COST-2
- The earlier body's window figures (51 jobs, 8 main offenders) do not reproduce: the verdict re-derives 78 jobs, 13 main offenders; the committed draw set and its window grading are in tests/replay.py with `tools/audit/seat/replay_draws.py window`, to be re-run on a listed window with job ids cited. Carry: R10-REPLAY-COST-2
- The ref24 raise as the centring rule's value, with no control pinning each class budget to the rule over the readings; destination tests/replay.py (the `cycle_cost:class_rule` control now pins the tables to `derive_cost_classes`; whether that closes it is for the carry). Carry: R10-REPLAY-COST-2
- `fallback_budget`'s docstring ("the largest class budget measured for each keyed metric") versus its code, which keeps COST_BUDGETS' loop figure; destination tests/replay.py. Carry: R10-REPLAY-COST-2
- The stale comment above `COST_CLASS_BUDGETS` ("69-72 %"); destination tests/replay.py. Carry: R10-REPLAY-COST-2
- Three surviving mutants of the earlier head (band edges `<=` to `<`, ref24 edge back at 22.64, dropped `print(out['notice'])`); not re-run against 130769e1; destination tests/replay.py. Carry: R10-REPLAY-COST-2
- The AWAY_COVERED pin and the export.py credential-refusal pin are built, not carried: `ok control:away:covered_names_are_committed`, `ok AWAY_COVERED names committed fixtures`, `ok recorder:unsupported_scheme_refusal_prints_none_of_the_url`; destination tests/replay.py. Carry: R10-REPLAY-COST-2

## Friction

none
