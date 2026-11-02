Fix review: blocked 6ba3033f34810c8a4e311cb2eba8cbb3b78ab627 class-open: the nightly slow lane runs the same budgets on a third runner class, which reads synthetic cpu_ratio 1.451-1.493, and the new 3.614 cannot see a 2x cycle there

bus-nonce: 6a26343db7e7a370cb911b882a4c07b4

This is round 2 of PR #3174 (R10-REPLAY-COST-BUDGET, issue 3129). It is a delta review at head `6ba3033f34810c8a4e311cb2eba8cbb3b78ab627`, judged through the three-dot diff against merge base a9c149289922, which is origin/main. The diff touches only `tests/replay.py` and `dev/programme/delivery/3174.md`. I worked from a detached worktree at the head, with a second one at the base. dev/governance/roles/ has not changed since the merge base. The harnesses are the finder's: the lane's own `cost` lines from the CI `replay` job, and the `--one` runs used by verdict/3174 and verdict/3078.

## Block

**class-open: nightly.yml `slow`, the scheduled full run of `python3 tests/replay.py`.** It applies these same `COST_BUDGETS` on a runner class that the body neither measured nor dispositioned.

The body says "Only these three jobs were readable for the owner fixture and the synthetic after 2026-10-31". That is not so for the synthetic fixture. The scheduled nightly `slow` jobs for 2026-10-31, 11-01 and 11-02 are readable:
- job 124414072168 of run 41159630948
- job 124725704090 of run 41264951784
- job 125036077984 of run 41369286061

Their cycle code differs from this base only in learner_progress.py, replay_doc.py and snapshots.py, so the coordinator cycle is the same. Their readings (ev/nightly_slow_*.txt):
- `ref_ms` is 52.4-53.3 and `loop_ref_ms` is 156-166.
- Synthetic `cpu_ratio` reads 1.4563, 1.451 and 1.4926.
- The lane's `cpu doubled` arm reads 2.8848, 2.841 and 2.9251.

Production `cost_offenders` at the head budgets (ev/budget_check.txt):
- Each clean nightly reading returns `cpu_ratio 1.45x: budget 3.614 cannot see a 2x cycle; re-record 2.05-2.11`.
- Each doubled arm reads under 3.614, so the lane's `cycle_cost sees a doubled cycle cpu` check would also FAIL.
- At the base budget 2.173, all three are WITHIN, and those nightlies passed with `ALL 93 replay checks PASSED`.

So merging this head turns the next scheduled nightly red on the synthetic fixture. On that class the budget no longer catches a real 2x cpu regression, which fails ASK (2) there. These are the "timed slow lanes" that the head's own comment above `COST_BUDGETS` says the base's 2.173 was centred on (its 1.391 low edge, `tests/replay.py:457-458`). The re-centring dropped them without saying so.

The class does not fit one 2x band as recorded:
- sqrt(2) x the geometric midpoint of 1.451 and 2.81 is 2.856.
- The nightly cpu-doubled arm at 2.841 then reads under it.
- So a re-cut needs a decision, not a re-derivation: per-class budgets, a paired reference, or tvofi's call on which classes the lane grades.

## Findings

- The owner fixture has never been read on the nightly class. It joined after the 2026-11-02 00:50 nightly (its head 78dd34354 has no owner fixture). The re-cut owes that reading against the 337.8 budget's floor of 168.9 before the owner budget is re-recorded. Carry: R10-REPLAY-COST-BUDGET
- The body says synthetic `loop_cpu_ratio` is "flat across both classes" at 0.0901-0.0907. Other CI readings say otherwise:
  - this head's own replay job (class B, `loop_ref_ms` 155.3) reads 0.1023;
  - the nightly class reads 0.093-0.1026.

  Everything I read stays within 0.1278 (the largest, 0.1026, is 80 % of the cap), and every `loop doubled` arm is over it (0.1792-0.2015). The 0.7 % flatness figure does not hold, and the re-cut should quote the spread it measures. Carry: R10-REPLAY-COST-BUDGET
- On a box outside every CI class, synthetic `loop_cpu_ratio` at unchanged code reads over the new 0.1278. This container read 0.1595-0.1779 at base and 0.1363-0.1405 at head, interleaved (ev/local_runs.txt). The body records this. The lane runs only in CI: `tests/run.sh:480` skips `replay.py`, and only tests.yml `replay` and nightly.yml `slow` invoke it. Carry: dismissed: a box outside every CI class is not one the lane grades; recorded in the body and in the comment above COST_BUDGETS, and the base-vs-base null the brief asks for is the CI readings, which are within

## Evidence

- Head re-read after CI concluded: refs/pull/3174/head and the PR API both read `6ba3033f34810c8a4e311cb2eba8cbb3b78ab627`. The body's `## Head` names it.
- CI: `merge_train.py classify 6ba3033f34810c8a4e311cb2eba8cbb3b78ab627 --pr 3174` exited 0 and printed `GREEN 6ba3033f34810c8a4e311cb2eba8cbb3b78ab627 pending: none red: none` (ev/classify.txt). No check run on this head has a failure, timed_out or cancelled conclusion. `## Red checks` answers #3167's inherited red. Its trigger is answered; the answer itself is not re-judged here.
- This head's replay job 125316010511 is class B (`ref_ms` 46.4) and reads `ALL 179 replay checks PASSED` (ev/head_replay_125316010511.txt):
  - synthetic `cpu_ratio` 2.4235 and `loop_cpu_ratio` 0.1023;
  - owner `cpu_ratio` 245.967;
  - cpu-doubled 4.7775 and loop-doubled 0.2015, both over their caps.
- ASK (1), the cited sources: I opened all three cited jobs myself (ev/ci_replay_*.txt), and every figure in the body and the comment matches the `cost` lines.
  - 125240101580 (run 41434115932) ran the pull/3174 merge commit 5cc311bf of a476a578, as the body says. It read 235.8185 / 2.7543 / 0.0907 at `ref_ms` 30.7.
  - 125160076828 (#3167) read 240.6876 / 2.81 / 0.0903 at `ref_ms` 30.4.
  - 125097530406 (#3078) read 241.9249 / 2.3246 / 0.0901 at `ref_ms` 46.3.
  - The doubled arms read 5.5315, 5.701 and 4.6473 (cpu) and 0.1833, 0.186 and 0.1792 (loop).
  - All three heads carry custom_components identical to the base.
  - The rule re-derives to 337.8, 3.614 and 0.1278.
  - Each budget's floor is under its lowest PR-lane reading. On those two classes, the budgets sit where the readings put them.
- ASK (2), my own mutants in production code at the head (ev/mutant_cpu.diff, ev/mutant_loop.diff), synthetic fixture, interleaved with base and head on this container (ev/local_runs.txt):
  - A worker-side mutant that runs each process-worker job twice (`process_worker.py:84`) reads `cpu_ratio` 2.62, 3.70 and 3.05, against head 2.05, 2.27 and 1.64.
  - A loop-side mutant that spins 12 ms of loop-thread CPU per cycle in `_async_update_data` reads `loop_cpu_ratio` 0.183, 0.216 and 0.219, against head 0.136, 0.141 and 0.140.
  - Both move the metric they target, but rulers on this container swing between 43 and 76 ms. It is not a CI class, so these readings show direction only. Over/under against the budgets rests on the CI doubled arms above.
  - Owner `cpu_ratio`: a clean head `--one` here reads 307.9 at `ref_ms` 48.6, inside 337.8. The worker-side mutant's owner run printed no result line: my JSON parse in ev/local_runs.txt shows an IndexError on empty output. So I have no owner mutant figure of my own. The owner over-budget claim rests on the body's 623.8, which I could not re-derive, and on its being 1.85x the CI owner readings.
- ASK (3), the two pins (ev/pins.txt). Null at the head: `AWAY_COVERED` names a committed fixture (offenders []), and both `control:away:covered_names_are_committed` and `recorder:unsupported_scheme_refusal_prints_none_of_the_url` read ok. Mutants:
  - M1, `AWAY_COVERED` misspelt `owner-2026-10-30-awya.json`: `away_covered_offenders` returns the offender, which main()'s `R.check(... not wrong ...)` turns red. Killed.
  - M2, `away_covered_offenders` returning []: `FAIL control:away:covered_names_are_committed bad=[] good=[]`. Killed.
  - M3, the export refusal as `f"the recorder URL {url} is ..."`: `FAIL recorder:unsupported_scheme_refusal_prints_none_of_the_url` with the canary credential visible. Killed.
  - All three were restored, and the tree is clean.
- ASK (4): the body has no `Carry: R10-REPLAY-COST-BUDGET` line for `loop_cpu_ratio`, and its sections are all present. #3167's red, 2.81 over 2.173, is cleared on the PR lane: 2.81 is within 3.614 and 2.81 x 2 = 5.62 is over it.
- ASK (5), standing checks (ev/standing.txt):
  - `git merge-tree --write-tree origin/main 6ba3033f34810c8a4e311cb2eba8cbb3b78ab627` exits 0 with tree 0e9dff14f.
  - The delivery row is in the three-dot diff.
  - Both claim files are byte-identical to origin/main.
  - VERSION, the manifest and RELEASE_NOTES are untouched.
  - No `*_budgets.json` is touched.
  - No host path appears in the added lines.
- I did not re-run the gate or the mutation table. Both are CI's, cited above.
