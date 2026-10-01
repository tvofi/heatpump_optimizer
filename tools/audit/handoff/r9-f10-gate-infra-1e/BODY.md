<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: twenty production sites that subtract, compare or add two stamps sharing Home Assistant's one ZoneInfo measured wall clock, so across the autumn fold (02:55 CEST to 02:55 CET, a true hour, a wall zero) and the spring gap (01:59 to 03:01, a true two minutes, a wall 62) they read the wrong duration: the legionella hold credit, refusal window, 12 h boost bound and credited-since-start compare; the drift starvation window; comfort-learning and external-heat decay; sysid's arm interval, phase clock, slab series, adoption gate and fit columns; the three coordinator learner sample gaps and the outage recovery and DHW hold compares; boost's expiry, clamp and two-hour add; away's hours until return; and wood_fuel's typed-slot duration. F10.1d measured fourteen of the fifteen census-missed sites misfiring and left them here.

After: each site goes through `utc_elapsed_seconds` or `utc_shift` (true instants), and `tests/dst_checks.py` has one check per site that goes red when that one line is reverted to wall clock. A guard in the same script keeps `tests/open_meteo.py`'s standalone loader importable, and the stray F10.1d `BODY.md` is gone from main.

The helper `utc_elapsed_seconds` (with `_as_utc`) moved from `accuracy.py` to `drift.py`, and `accuracy.py` re-exports it, because `accuracy` imports `drift` and `drift` needed the helper: a function-local import would have raised `local_imports` past its budget, so I restructured instead of raising it.

## Head

`21f6299d77cca57b285dcef698526b23d53899ba` is the code head these figures were measured at (dst_checks, structure, and the scoped gate were run at its code-equivalent pre-rebase head `cfe512e4`; the rebase onto `origin/main` `661d56f4` was a clean cherry-pick with no conflicts), on a fresh branch with no main merge in its ancestry. Transport commits above it only add this file.

## Mutation proof

For each fix I reverted its one line (every call of the three coordinator learner gaps at once) and ran `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components:tests python3 tests/dst_checks.py`; each mutant failed the check(s) named for that site, 23 of 23 mutants:

- legionella hold minutes: `legionella: a hot-to-hot gap across the fold adds its true 1 minute to the hold`
- legionella refusal window: both `legionella: a credit a true hour after the last is not refused across the fold` and `...a true 2 minutes after the last is refused across the spring gap`
- legionella 12 h bound: `legionella: the 12 h boost bound closes at 12 true hours across the fold`
- legionella credited-since-start: `legionella: a cycle credited a true 20 minutes into the boost counts as credited`
- drift: `drift: a latch starved for a true hour releases on the fold only if the hour passed` and the spring-gap twin
- comfort learning decay, external heat confidence: one named check each
- sysid arm and phase clock: `sysid: arming after a true 30 days is allowed across the autumn fold`, `sysid: the 2 h step ends at 2 true hours across the fold, not the 1 h of wall clock`
- sysid slab series (`_slab_series`), adoption gate (`_unadoptable`), and identify's rate, drift column and curvature pass: `sysid slab series: ...`, `sysid adoption gate: ...`, and `sysid identify: ...` (the three identify lines each fail that one check)
- coordinator house, lower-floor and buffer learners (three sites mutated together), outage recovery and DHW hold: the named learner and outage checks, including the spring-gap NULL CONTROL for the two house learners
- boost active, expire, clamp and set: four named boost checks
- away: `away: hours until a presence end time typed across the fold are the true 4, not the wall 3`
- wood_fuel: `wood fuel: a typed slot across the fold spreads its liters over the true three hours`
- the loader guard: adding `from .accuracy import utc_elapsed_seconds` to `open_meteo.py` fails `open_meteo's loader finds every package module it imports among those it loads`

Only the sysid identify mutants needed a second pass: the first synthetic data returned a refused fit identically both ways, so the check now also requires `completed` and uses the tree's own v4.0.5 step response.

## Null control

The unmodified tree (`origin/main` 661d56f4): the same probes F10.1d recorded (`/mnt/project-files/audit-r9/fix/evidence/1809-f10-1e-probes/`, `probe_*.py`) print `MISFIRE` at each of the fourteen sites. Inside the checks, each fold or spring pair has a plain control: the house and lower-floor learners take no sample across the spring gap (a true 2 minutes, under their floor), the drift latch is not released across the spring gap, and the legionella credit is refused across it. `away.expire_override` was measured clean and left alone (its callers pass fixed-offset stamps).

## Figures

- `git rev-parse handoff/r9-f10-gate-infra-1e-v2~1` prints `21f6299d77cca57b285dcef698526b23d53899ba`, the code head.
- `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components:tests python3 tests/dst_checks.py` prints `ALL 127 DST / QUARTER-GRID CHECKS PASSED` (96 before this change, 31 new).
- `python3 tests/structure.py` prints no `FAIL` and no `STRUCTURE BUDGET(S) BREACHED` (the one breach during development, `local_imports 8 > 7`, was the drift function-local import, removed by moving the helper).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 22 script(s) run, 6 scoped out` at the pre-merge head; every script the scope named passed under `GATE_SCOPE=auto GOLDEN_MODE=drift ./tests/run.sh` except `tests/stress.py`.
- Census instrument: `rg -n --no-heading -f` of `census.rx` (the widened rule, `/mnt/project-files/audit-r9/fix/evidence/1809-f10-1e-probes/census.rx`) over `custom_components/heatpump_optimizer/*.py`; every site it returns that F10.1d probed is fixed here or measured clean; the rule is a static grep and misses sites it does not name, which `tools/audit/bugclasses.json` P7 `barrier_gap` now says.
- Disposition of the two unprobed sites the brief named: sysid `SysIdSample.when` differences (slab series, adoption gate, identify) and wood_fuel's typed-slot duration both misfired and are fixed and checked.

## Red checks

`tests/stress.py` did not run locally: `run.sh` refused it for a gate lease label I had not taken (`flock-wrap refused, f10-1e holds no lease`), an environment error of mine, and CI's own run covers it. `typing_ruler`, `mypy --strict` and real-HA `ha_contract` did not run here (the cloud box has Python 3.11, not the pinned 3.14.2); the Mac or CI shows them. `tests/mutation_table.py --pin-killed` was started twice and did not finish: the first drive ended INCONCLUSIVE (the baseline `tests/harness_headers.py` hit its own 240 s timeout under three parallel jobs, a load artifact; it passes alone), the second ran alone and passed every baseline up to `tests/entities.py` but needs hours of per-mutant driver runs, so I stopped it. The three pins of `_as_utc` and `utc_elapsed_seconds` that lived under `accuracy.py` are deleted because their code moved to `drift.py`; the mutation job will therefore count them (and the new sites) unpinned until `mutation-autofix` records the killed ones, which `ci-autofix.md` says to wait for.

## Forward-carry

`none`. The residual (comparisons of two same-zone stamps inside the repeated autumn hour, such as wood_fuel's `ts < end` steps, are not traced) is recorded in P7's `barrier_gap` in `tools/audit/bugclasses.json`, which is the register that decides the class.

## Friction

`ratchet-budgets: cost: the --pin-killed drive for a 10-file diff costs hours on a 4-core cloud box and its harness_headers baseline sits at the edge of its own 240 s timeout, so a cloud fixer cannot discharge the step before handoff`
