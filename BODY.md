Keys the synthetic fixture's replay cost budget by runner class. The class signal is the run's own BLAS ruler: the median reference-solve `ref_ms` that each `cost` line prints. This round admits a fourth class, ref24, on its own CI readings. The class also keys `loop_cpu_ratio`, because ref24 reads 0.1282, over the shared 0.1278. A ruler in no band is still refused by name, and no default budget is assumed. The refusal is now probed in every gap between bands and at the two rulers CI read that no band admits. Closes #3129.

## Re-cut note

This is repair round 4 of #3174. Under the past-three rule this body is retaken whole, and round history is deleted. The finding: CI replay job 125461180429 (run 41498701363, at `acec536b`) ran on a runner whose ruler reads `ref_ms` 23.77-24.31. That is in no band of `COST_RUNNER_CLASSES`. So `cycle_cost` and its three doubled-arm checks failed on `runner class unknown`, and `pr-contract` failed because the body did not name `tests / replay`. The ruling for the later review: "CI exposed a runner class the r3 harness never ran; repair of the named band seam only".

What changed against `acec536b` is `tests/replay.py` only, in the band seam:
- `COST_RUNNER_CLASSES` gains `ref24` (22.64, 25.53).
- `COST_CLASS_BUDGETS` gains `ref24` `cpu_ratio` 3.630 and `loop_cpu_ratio` 0.1813.
- `COST_CLASS_READINGS` rows now name their metric and gain that job's two readings.
- New `COST_RULERS_REFUSED` (28.01, 34.35).
- `control:cycle_cost:runner_class_unknown` probes every gap between bands, a ruler under the lowest band, `COST_RULERS_REFUSED`, and NaN.
- The comments state the rule and the census.

No band is widened. No `*_budgets.json` is touched, nothing is refactored, and no existing budget moves.

**Why a band of its own, and not a wider band or a fallback.** The data says the per-class cost ratio is not a function of the ruler. ref24, the fastest ruler, reads synthetic `cpu_ratio` 2.5671, which falls between ref46 (2.27-2.42) and ref30 (2.61-2.81). The 28.0 runner (job 125000687320) sits 2.5 % under the ref30 floor, yet reads 1.8924, 0.67-0.72x of ref30's ratios. Grade that runner on ref30's 3.934 and its doubled arm, 3.8922, is not over budget. A widened band would therefore hide exactly the 2x regression the lane exists to see. Interpolating or borrowing a neighbour fails the same way. So the sound rule keeps r3's refusal: a class is admitted only on its own cited readings, and anything else fails closed by name. The standing cost is one red lane per new runner SKU. Its own `cost` lines are the readings that admit it.

## Head

`4de0f6565221868a0da1b5c88626f052e88d0eda` fast-forwards `acec536b4ba1dc000126671f1f727defd21f1925` by three commits. Every local figure below was taken on that head. `git merge-tree --write-tree origin/main HEAD` reports no conflict against origin/main `871a20da138592ac892f4652a4f82992a6626783`, nor against `b8e823699981866383f1afa54ce708ded3419316` (read 2026-11-02T20:16:14Z), so main was not merged, as the brief allows a merge only on a conflict. Main's delta `871a20da..b8e82369` is 17 files of triage batches and delivery rows. It touches no `custom_components/` file and no replay file, so nothing the figures measure moved. Merge base: `38dcb6c5dbade5206f2fae885334483082f36d10`.

## Red checks

I read the whole check-run set at `acec536b` through the PR's `get_check_runs`: total_count 55, one page. Three concluded failure.
- `tests / replay` (job 125461180429). Four checks failed: `cycle_cost` and `sees a doubled cycle` cpu, memory and loop, each with `runner class unknown: ref_ms 23.83 lies in no band of COST_RUNNER_CLASSES`. Cause: a runner SKU that the r3 readings never sampled. Process state: the refusal worked as designed, failing closed at first sight and by name. Cheaper detector: none exists. A runner's SKU is assigned at job start and is unknowable before CI runs, and the 22-job census found no earlier ref24 reading at current code. The refusal is the detector, and its standing cost is one red per new class. Answered here by admitting the class on that job's readings.
- `pr-contract / pr-contract` (job 125483440211): `check tests / replay is red and ## Red checks does not name it`. Answered by this section.
- `gate` (jobs 125483784051, 125484217523): `FAIL pr-contract / pr-contract`. It follows pr-contract and has no cause of its own.

## Mutation proof

Each mutant is a `sed` edit to `tests/replay.py`, made at the head. The probe is `PYTHONPATH=tests/hastub python3 -B -c "import sys; sys.path.insert(0,'tests'); import replay; [print(n, ok, d[:120]) for n, ok, d in replay.controls() if 'class' in n]"`. After each run the file was restored and compared with `cmp` against the head copy, and a `cmp` hit on the mutant itself was checked so that no edit is vacuous.

**Per class: a budget that cannot see its own planted 2x.** The planted 2x is each class's `cpu doubled` arm from CI, held in `COST_CLASS_READINGS`. Each mutant loosens one class's budget past its own doubled arm:
- K24, `s/"ref24": {"cpu_ratio": 3.630,/"ref24": {"cpu_ratio": 5.3,/`: `FAIL control:cycle_cost:class_budgets [(23.83, ['cpu_ratio 2.567: budget 5.3 cannot see a 2x cycle; re-record 3.63'], [])]`. **Killed.**
- K24L, which drops ref24's loop key so it falls back to the shared 0.1278 (`s/, "loop_cpu_ratio": 0.1813}/}/`): `FAIL ... [(23.83, ['loop_cpu_ratio 0.1282 over its budget 0.1278'], ...)]`. **Killed.**
- K24B, which deletes the ref24 band: `FAIL control:cycle_cost:class_budgets [(23.83, ['no recorded budget: ...'])...]` and `FAIL control:cycle_cost:runner_class_unknown`. **Killed.**
- K30, ref30 3.934 to 5.76: `FAIL ... [(30.32, ['cpu_ratio 2.81: budget 5.76 cannot see a 2x cycle; re-record 3.974'], [])...]`. **Killed.**
- K46, ref46 3.357 to 4.83: `FAIL ... [(45.65, ['cpu_ratio 2.325: budget 4.83 cannot see a 2x cycle; re-record 3.287'], [])...]`. **Killed.**
- K53, ref53 2.081 to 2.96: `FAIL ... [(52.76, ['cpu_ratio 1.456: budget 2.96 cannot see a 2x cycle; re-record 2.06'], [])...]`. **Killed.**
- M1, one budget 3.614 for every class: `FAIL ... [(52.76, ['cpu_ratio 1.456: budget 3.614 cannot see a 2x cycle; ...'])...]`. **Killed.**

**Unknown class.**
- M4, an unknown class falls back to ref46 (`s/... and c in keyed), None)/... and c in keyed), "ref46")/`): `FAIL control:cycle_cost:runner_class_unknown bad=[] good=[]`. **Killed.**
- W30, ref30 widened down over the 28.0 runner (`s/"ref30": (28.72, 32.69)/"ref30": (26.0, 32.69)/`). At `834d0074` this **survived** (33 of 33 ok), because no control pinned a known foreign ruler. `4de0f656` adds `COST_RULERS_REFUSED`, and it now reads `FAIL control:cycle_cost:runner_class_unknown bad=[] good=[]`. **Killed.** This is a disclosed self-correction within this round.
- W46, ref46 widened down to 33.0, and W30u, ref30 widened up to 35.0, over the 34.35 ruler: both read `FAIL control:cycle_cost:runner_class_unknown`. **Killed.**

## Null control

- **Head unmutated:** `33 of 33 controls ok` (the probe above, counting every control).
- **The failing job, base against head.** I put the four `cost` lines of job 125461180429 through the production `class_budget` + `cost_offenders`:
  - At `acec536b`, all four read `runner class unknown`. That is the CI red, reproduced.
  - At the head, the clean run reads `[]`. `cpu doubled` reads `cpu_ratio 5.209 over its budget 3.63`, `memory doubled` reads `peak_kib 3861 over its budget 2686`, and `loop doubled` reads `loop_cpu_ratio 0.2603 over its budget 0.1813`.
  - The owner fixture's clean 269.8155 at `ref_ms` 24.06 reads `[]` at both (unkeyed, 337.8).
- **The census, every reading.** I graded all 22 jobs at the head (Figures).
  - The 19 jobs whose rulers lie in a band read `within`, and each `cpu doubled` arm reads `seen` (over its class budget).
  - The three outside every band read `REFUSED`, both clean and doubled: 28.01 (job 125000687320), 34.35 (nightly job 123225871060) and 22.16 (nightly job 121370544228, 10-26, older cycle code, not admitted).
  - Had a band been widened to fit these, at least one of them would read `NOT SEEN`. 28.01 graded on ref30's 3.934 gives 3.8922 < 3.934.
- **ref24 budget placement.** 2.5671 / 3.630 and 0.1282 / 0.1813 are each 70.7 %, inside (budget / 2, budget]. The class's `ref_ms` spread within the job is 2.3 %. The band is the extremes widened 5 % each way, and it is disjoint from ref30 (28.72).

## Figures

- **Readings source.** Each reading is the `cost {...}` line of a job log. Re-take one with `gh api repos/tvofi/heatpump_optimizer/actions/jobs/125461180429/logs`, keeping lines holding `cycles over` and `doubled:`. Job 125461180429 read:
  - clean `cpu_ratio` 2.5671 and `loop_cpu_ratio` 0.1282 at `ref_ms` 23.83;
  - `cpu doubled` 5.2086 at 23.99;
  - `memory doubled` `peak_kib` 3860.7 at 24.31;
  - `loop doubled` 0.2603 at 23.77;
  - owner fixture 269.8155 at 24.06.
- **Band rule.** min / 1.05 floored and max x 1.05 ceiled to 0.01, over every clean and doubled `ref_ms` of the cited job: 23.77 and 24.31 give 22.64-25.53.
- **Budget rule.** sqrt(2) x the geometric midpoint of the class's clean extremes, the rule every budget in the file uses. One job gives sqrt(2) x 2.5671 = 3.630 and sqrt(2) x 0.1282 = 0.1813. The lane's own `record:` line printed `cpu_ratio=3.63 ... loop_cpu_ratio=0.1813`.
- **Census of 22 jobs.** These are every `tests / replay` job that ran in the 60 most recent `ci.yml` runs (4) plus earlier replay-branch runs (7, from PRs #3174, #3170, #3167 and #3078), and all 11 scheduled nightly `slow` jobs. Each was graded with `PYTHONPATH=tests/hastub python3 -B -c "import sys; sys.path.insert(0,'tests'); import replay as r; s='synthetic-dhw-only.json'; [print(x, r.class_budget(s, x)[1][:1] or r.cost_offenders({'cpu_ratio': c}, r.class_budget(s, x)[0])) for x, c in ((23.83, 2.5671), (28.01, 1.8924), (34.35, 1.8747), (22.16, 1.9455), (47.73, 2.2746), (54.55, 1.4448))]"`, the same call over each job's clean and doubled pair. Result: 19 in band read `within` and `seen`, and three read `REFUSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` at the head.
- Scoped gate, re-run at `4de0f656`, `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out` (`debug_collect`, `entities`, `features`). Every script it names, plus the run_always `env_drift.py --claims-only`, `closure.py selftest`, `layout.py` and `harness_headers.py`, exited 0 under `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`.
- `bash tools/pr/prepr.sh <body>` on the committed clean tree, closures step not skipped: `PRE-PR: 4de0f6565221868a0da1b5c88626f052e88d0eda 00000000000000000000000000 rc=0`. That run was against origin/main `871a20da`. Main has since moved to `b8e82369` with no conflict and nothing this diff reads (Head), and under the brief's merge-only-on-conflict rule there was no merge, so there was no second run.

## Carries

- Carry 1: the owner fixture's budget entry is unchanged at 337.8. Its clean reading on the new ref24 runner, 269.8155 (job 125461180429), reads inside it (Null control).
- Carry 2: the `AWAY_COVERED` and unsupported-scheme pins are untouched. `ok control:away:covered_names_are_committed` is among the 33 of 33 controls at the head.
- Carry 3: the synthetic `cpu_ratio` budget stays keyed by runner class, now four classes. The named fail-closed refusal for an unknown class is unchanged, and it is now probed in every gap and at `COST_RULERS_REFUSED` (Mutation proof: M4, W30, W46, W30u).

## Unpinned sites

None: `prepr.sh` step 6d reads `the diff adds no unpinned mutation site`. The new code is value checks inside `tests/replay.py`'s `controls()`, pinned by the in-tree `sed` mutants above. Every one is killed: K24, K24L, K24B, K30, K46, K53, M1, M4, W30, W46 and W30u.

## Forward-carry

none

## Friction

none
