Keys the synthetic fixture's replay `cpu_ratio` budget by runner class. The class signal is the run's own BLAS ruler: the median reference-solve `ref_ms` that its `cost` line already prints, never a runner name. Each class's budget is centred on that class's own CI lane readings. A run whose ruler falls in no band is refused by name, and no default budget is assumed. It keeps the two pins and the re-centred owner `cpu_ratio` 337.8 from the earlier rounds. Closes #3129.

## Head

bf2653335d31357918a4d8ba81947557652ee3a4: a99f68d54b94d7f46031b9a996420c0bf2bf5b51 (the fix, a fast-forward of 6ba3033f34810c8a4e311cb2eba8cbb3b78ab627) with origin/main ea59e9a09de56447326ae71d8a45fec81c3cc275 merged into it (read 2026-11-02T16:14:39Z). Main moved after the first clean `prepr.sh` run, so this handoff follows the rule for a moved main and merges it. `git merge-tree` had reported no conflict. Main's delta since a9c149289922 touches no file under `custom_components/` and no replay file, so the cycle code the cited readings measured is unchanged. Merge base is now ea59e9a09de56447326ae71d8a45fec81c3cc275. Every figure below that runs locally was re-taken on this merged head.

## Re-cut note

This is repair round 3 of #3174. It answers `verdict/3174` round 2: "Fix review: blocked 6ba3033f class-open: the nightly slow lane runs the same budgets on a third runner class, which reads synthetic cpu_ratio 1.451-1.493, and the new 3.614 cannot see a 2x cycle there". The ruling: one `cpu_ratio` budget cannot serve classes that read about 1.45 and about 2.3-2.8. It is either blind to a 2x on the fast class or red on the slow one. The fix keys the budget by class.

What changed against 6ba3033f is `tests/replay.py` only:
- New `COST_RUNNER_CLASSES`: three `ref_ms` bands.
- New `COST_CLASS_BUDGETS`: the synthetic `cpu_ratio` per class.
- New `COST_CLASS_READINGS`: the cited lane readings each class's budget is centred on.
- New `class_budget(name, ref_ms)`, which `run_fixture` now grades through.
- Two new controls: `cycle_cost:class_budgets` and `cycle_cost:runner_class_unknown`.
- The synthetic `cpu_ratio` 3.614 is removed from `COST_BUDGETS`.
- The comment above `COST_BUDGETS` now quotes the loop spread that was measured.

Unchanged: synthetic `loop_cpu_ratio` 0.1278 and `peak_kib` 2686, and every owner fixture budget (`cpu_ratio` 337.8, `peak_kib` 3740, `loop_cpu_ratio` 0.249). No `*_budgets.json` is touched and no budget is raised. The new class budgets are narrower than 3.614 on two classes. On ref30, 3.934 is wider than 3.614, but it is centred on that class's own readings and stays under that class's doubled arms (5.53, 5.70). The base's 2.173 was red on that class.

## Red checks

At 6ba3033f I read the whole check-run set through the PR's `get_check_runs`: 55 runs on one page (total_count 55). Every run concluded `success` or `skipped`. None concluded failure, timed_out or cancelled, so there is nothing new to answer.

Inherited from #3167: replay job 125160076828 of run 41405222589 read `synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 2.81 over its budget 2.173]`.
- Cause: a budget recorded for one runner class.
- Process state: recorded-on-one-class.
- Cheaper detector: none is needed. The lane's own `record:` line already prints the figure.
- Countermeasure: this PR keys the budget by class. That run's class (ref30) reads WITHIN its own budget (Figures).

## Mutation proof

**Per class, the planted 2x.** The planted mutant is the lane's own `cpu doubled` arm (`--inject-cost cpu`), which CI ran on each class. Its readings go through the production `class_budget` + `cost_offenders` at this head. Each class's doubled arm reads over its own class's budget:
- ref30: 5.701 and 5.5315 read `cpu_ratio 5.701 over its budget 3.934` and `cpu_ratio 5.532 over its budget 3.934`.
- ref46: 4.6473 and 4.7775 read `over its budget 3.357`.
- ref53: 2.8848, 2.841 and 2.9251 read `over its budget 2.081`. At 6ba3033f's single 3.614 the same three read nothing (NOT SEEN).

**Code mutants.** Each edit was made to `tests/replay.py` with the `sed` shown. Each run was `PYTHONPATH=tests/hastub python3 -B -c "import sys; sys.path.insert(0,'tests'); import replay; [print(n, ok) for n, ok, _ in replay.controls() if 'class' in n]"` with `PYTHONDONTWRITEBYTECODE=1`, and the file was restored with `git checkout tests/replay.py` after each.
- M1, one budget 3.614 for every class (6ba3033f's shape): `sed -i 's/"ref\(30\|46\|53\)": {"cpu_ratio": [0-9.]*}/"ref\1": {"cpu_ratio": 3.614}/'` gives `FAIL control:cycle_cost:class_budgets [(52.76, ['cpu_ratio 1.456: budget 3.614 cannot see a 2x cycle; re-record 2.06'], []), ...]`. **Killed.**
- M2, ref53 graded by ref46's budget: `s/"ref53": {"cpu_ratio": 2.081}/"ref53": {"cpu_ratio": 3.357}/` gives `FAIL control:cycle_cost:class_budgets [(52.76, ['cpu_ratio 1.456: budget 3.357 cannot see a 2x cycle; ...'], [])...]`. **Killed.**
- M5, ref46 graded by ref53's budget: `s/"ref46": {"cpu_ratio": 3.357}/"ref46": {"cpu_ratio": 2.081}/` gives `FAIL control:cycle_cost:class_budgets [(45.65, ['cpu_ratio 2.325 over its budget 2.081'], ...)]`. **Killed.**
- M3, ref30 graded by ref46's budget: `s/"ref30": {"cpu_ratio": 3.934}/"ref30": {"cpu_ratio": 3.357}/` leaves `ok control:cycle_cost:class_budgets`. **Survives, as an equivalent mutant on these readings.** The two CI classes' readings sit 1.17x apart, so each class's band holds the other's clean and doubled readings. That is why 6ba3033f's single 3.614 served both CI classes. The key is load-bearing for ref53 against both CI classes, not for ref30 against ref46. Both bands are kept because the brief centres each class on its own readings, and because a merged ref30/ref46 band would be a fourth recording that no class reads.
- M4, an unknown class falls back to a default: `s/if lo <= ref_ms <= hi and c in keyed), None)/if lo <= ref_ms <= hi and c in keyed), "ref46")/` gives `FAIL control:cycle_cost:runner_class_unknown bad=[] good=[]`. **Killed.**

**The two pins** are unchanged from round 2 and still green at this head: `ok control:away:covered_names_are_committed` and `ok recorder:unsupported_scheme_refusal_prints_none_of_the_url` (33 of 33 controls and 23 of 23 recorder checks ok, in-process). Their killed mutants are round 2's: a misspelt `AWAY_COVERED`, and the URL interpolated into the refusal. Their code is untouched here.

## Null control

- **Base against base, per class.** Every clean reading is the unmodified cycle code on CI: the cited jobs' code differs from this base only outside the coordinator cycle, as the review established. Through the production functions at this head, every clean reading reads WITHIN its class's budget:
  - ref30: 2.81 and 2.7543 against 3.934;
  - ref46: 2.3246 and 2.4235 against 3.357;
  - ref53: 1.4563, 1.451 and 1.4926 against 2.081.

  Each reading is 69-72 % of its budget, so it sits inside (budget / 2, budget]. With the class key removed (M1), the ref53 cleans read `cannot see a 2x cycle`. That is the finding.
- **Unknown-class null.** `class_budget(syn, 30.32)` (the first ref30 reading) returns no refusal. `class_budget` at 37.84 (between the ref30 and ref46 bands) and at NaN returns `runner class unknown: ref_ms 37.84 lies in no band of COST_RUNNER_CLASSES [(28.72, 32.69), (42.99, 49.51), (49.6, 56.78)]; no budget is assumed`.
- **End to end, the real run.** This container is outside every class. `PYTHONPATH=tests/hastub python3 tests/replay.py --one tests/replay/synthetic-dhw-only.json` ran twice: `ref_ms` 36.86 and 34.88, and `cycle_cost` was the named refusal both times. A doubled arm on such a box carries the refusal instead of `over its budget`, so the lane's `sees a doubled cycle cpu` check fails there too. It fails closed.
- **Unaffected owner fixture.** It is not keyed (its readings are flat across the two CI classes), and `class_budget('owner-2026-10-30-away.json', 99.0)` returns the unchanged 337.8 / 3740 / 0.249.

## Figures

- **Source jobs.** Readings are the `cost {...}` lines of each job's log. Re-take one with `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`, keeping the lines holding `cycles over` and `doubled:`. The `ref_ms` values come from the clean and every doubled run of each job, and the synthetic `cpu_ratio` is clean / cpu-doubled:
  - ref30 class: `tests / replay` job 125160076828 (run 41405222589, #3167) read `ref_ms` 30.16-30.43 and 2.81 / 5.701. Job 125240101580 (run 41434115932, #3174 at 5cc311bf) read 30.20-31.12 and 2.7543 / 5.5315.
  - ref46 class: job 125097530406 (run 41389413359, #3078) read 45.15-46.34 and 2.3246 / 4.6473. Job 125316010511 (run 41456836096, #3174 at 6ba3033f) read 46.36-47.15 and 2.4235 / 4.7775.
  - ref53 class: nightly.yml `slow` job 124414072168 (run 41159630948) read 52.76-53.46 and 1.4563 / 2.8848. Job 124725704090 (run 41264951784) read 52.64-54.07 and 1.451 / 2.841. Job 125036077984 (run 41369286061) read 52.09-53.33 and 1.4926 / 2.9251.
- **Band rule.** Each class's `ref_ms` extremes are widened 5 % each way, as min / 1.05 and max x 1.05, rounded outward to 0.01. That gives ref30 28.72-32.69, ref46 42.99-49.51 and ref53 49.60-56.78, and the bands are disjoint. Measured spreads, for scale: within one job 2.4-3.2 %; across a class's jobs 3.2 % (ref30), 4.4 % (ref46) and 3.8 % (ref53). Readings per class: 10 for ref30, 10 for ref46, 12 for ref53.
- **Budget rule.** Each budget is sqrt(2) x the geometric midpoint of that class's clean extremes, the same rule as every other budget in the file. That gives ref30 3.934 (from 2.7543 and 2.81), ref46 3.357 (from 2.3246 and 2.4235) and ref53 2.081 (from 1.451 and 1.4926). No budget is widened past its readings.
- **Owner fixture on ref53, unread.** It joined after the last nightly. If ref53 reads it the way it reads the synthetic fixture (about 0.53-0.6 of ref30), the first nightly to replay it may read under its 168.9 floor. That nightly's `record:` line is the reading to key it on; nothing is recorded here for a class that has not run it.
- **Too few readings.** Each class has two or three jobs. The ref53 class has replayed only the synthetic fixture, because the owner fixture joined after the last nightly. Only what ran is recorded. The bands are therefore narrow, and a ruler outside them fails closed rather than borrow a neighbour's budget.
- **Historic readings not used.** The older nightly comment above `COST_BUDGETS` describes a fast nightly class at `ref_ms` ~22-34. Any part of it outside 28.72-32.69 now fails closed until a reading there is recorded.
- **`loop_cpu_ratio` is not affected.** The seven jobs read 0.0901-0.1026 clean (1.14x, the largest 80 % of 0.1278). Every `loop doubled` arm reads 0.1792-0.2015, over 0.1278. One budget serves every class, so it is not keyed. The comment's earlier "flat across both classes" is replaced by that spread.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scoped gate, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out` (`debug_collect`, `entities`, `features`). Every script it names, plus the run_always `env_drift.py --claims-only`, `closure.py selftest`, `layout.py` and `harness_headers.py`, exited 0 under `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`.
- `bash tools/pr/prepr.sh <body>` at bf265333 on the clean tree, closures step not skipped: `PRE-PR: bf2653335d31357918a4d8ba81947557652ee3a4 00000000000000000000000000 rc=0`; main unmoved since (ea59e9a0), so no second merge.

## Carries

- Carry 1: the owner fixture's budget entry is unchanged at 337.8, centred on its readings 235.8 and 240.7 (ref30) and 241.9 and 246.0 (ref46).
- Carry 2: the `AWAY_COVERED` and unsupported-scheme pins are unchanged and green.
- Carry 3: the synthetic `cpu_ratio` budget is keyed by runner class, with a named fail-closed refusal for an unknown class.

## Forward-carry

none

## Unpinned sites

None: `prepr.sh` step 6d reads `the diff adds no unpinned mutation site`. The new `class_budget` and its controls are value checks in `tests/replay.py`, pinned by the in-tree `sed` mutants M1, M2, M4 and M5 above (M3 is disclosed as equivalent).

## Friction

none
