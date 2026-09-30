<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJVHEwMvj85Q4HPSTggsr6zPY)_

Fixes #1747. Round-9 endgame PR R9-EG-B8 (lane EG), with the carry from R9-F9.3's review.

Before: with the heat pump's DHW mode blocked and prices mostly negative, the co-optimisation replan planned hot water anyway. On the `wood_coil` golden scenario with prices shifted by -2.0 it shipped 9.22 kWh of DHW heat through a heating-only mode, and the reported tank-floor breach read 0.629 K instead of 20.81 K. Separately, a fresh install held the shipped DHW draw pattern raw, with three hours below the learner's intensity floor, so the first restart rewrote the whole hourly profile. Every later restart moved a clamped profile again, because one clip-and-divide pass is not idempotent.

After: the replan receives the same block as the first DHW build, so a blocked plan ships no hot water and the breach stays visible. `normalize_profile` is now a projection: every hour is in [0.2, 3.5], the mean is 1, and normalising its own output returns it unchanged. The learner seeds its profile through that projection, so a restart loads exactly what was saved.

How: `_co_optimize` passes `blocked=h.dhw_blocked` into its `_build_dhw_requirements` call. After this change `space_demand` is the only keyword the two builds differ in. `normalize_profile` keeps its one-pass result whenever that result already has mean 1, which is bit-identical to before whenever nothing clamps. Where the clamp moves the mean, it bisects for the scale that gives mean 1. A profile that is already in the domain with mean 1 is returned as it is. The non-finite and wrong-length fallbacks now return the projected default. `DhwProfileLearner.__init__` seeds `hourly_profile` through `normalize_profile`.

Design choice, stated per `fixer.md` step 11: a peaky day now keeps both rules. Its peaks sit on the 3.5 ceiling and the other hours carry the whole daily volume. The old test asserted that such a day lands below mean one ("the clamp wins"), and I have rewritten that check. The profile docstrings already state the volume rule this restores ("the profile decides *when*, never *how much*").

## Head

`03bb26f1` is the code head. Every figure below was measured there, against merge base `3dfebc16` (origin/main at 2026-09-30T14:05Z). The resume note and this body ride in one transport commit stacked above the code head, touching only `handoff/` paths, and are not part of the pull request.

## Mutation proof

My own mutants, from `run_mutants.sh` (sha1 `94517ed3`). Each applies one edit to a worktree at the code head and runs `tests/features.py`. The mutants ran at `e6d7b737`, whose non-finite check the next commit repaired. That check is red in every arm for that reason alone, and it is also listed under Red checks.
- M1, delete `blocked=h.dhw_blocked,` from the replan: red on `a DHW-blocked plan ships no hot water when mostly negative prices tempt the co-optimisation replan (#1747)` (9.22 kWh shipped, breach 0.629 K) and on `and every DHW build that solve made was told the mode is blocked` (`[True, False]`).
- M2, seed the learner raw (`params.dhw_hourly_draw_pattern.copy()`): red on `a restart loads the DHW profile the learner saved, unchanged` (moved by up to 0.0961), on `and the projection keeps the daily volume while respecting the clamp` (fresh min 0.1039), and on `a stored profile is normalised to average one, or refused whole`.
- M3, skip the bisection (`if False:`): red on the same three checks (learned mean 0.9375; a restart moves it).
- M4, always divide, dropping the mean-1 identity branch: red on `a restart loads the DHW profile the learner saved, unchanged`.

`mutation_table.py --scope changed --base origin/main`: `3577 unpinned site(s) of 4083 candidate sites, 3578 at the ratchet base 3dfebc16`; `0 survivor(s) of 3 evaluated = 0.0%, cap 20.0%`; `MUTATION TABLE PASSED` (rc 0). All three sites are in `normalize_profile`: `dhw_learning.py` BOOLOP (the usable test) and GUARD_OFF (the mean-1 bisection guard) were killed by `tests/features.py`, and RETURN_DEL was killed by `tests/guard_pins.py`. The null control `NULL_COMMENT` survived every driver.

## Null control

The base with the new tests is `features.py` at 3dfebc16 production code plus this branch's `tests/features.py` at `82b1a27f`. Exactly the four new checks were red: `4 of 3601 FEATURE CHECKS FAILED`. The unmodified probe at the base ships DHW heat at -2.0 and -3.0, and ships none at 0.0 and -1.0, where the replan is not adopted. The control arm, which gives the replan the block, ships none at every shift. The idempotence fuzz at the base reads `restart_moved=19475` of 20002. Its null at the head reads 0.

## Figures

- Probe `b8_replan_blocked.py` (sha1 `e29cc879`), from `handoff/audit-r9-alt`, run with `PYTHONPATH=tests/hastub:custom_components:tests python b8_replan_blocked.py` under `OPENBLAS_CORETYPE=Haswell` with 1 thread:
  - base `3dfebc16`, as-is, delta -2.0: `shipped_dhw_kwh=9.22 dhw_steps=16 dhw_floor_breach_c=0.629 build_calls_blocked_arg=[True, '<omitted>']`
  - base, as-is, delta -3.0: `shipped_dhw_kwh=8.63 dhw_steps=13 dhw_floor_breach_c=0.04`
  - head `03bb26f1`, as-is, at every delta in {0, -1, -2, -3}: `shipped_dhw_kwh=0.00`, breach 20.927 / 20.876 / 20.81 / 20.81, `build_calls_blocked_arg=[True, True]`. This is identical to the control arm at both ends.
- Idempotence fuzz `idem_fuzz.py` (sha1 `37db122a`), 20002 profiles (the shipped pattern, the peaky day, and four random families), with `PYTHONPATH=tests/hastub:custom_components python idem_fuzz.py`:
  - base: `RESULT cases=20002 restart_moved=19475 worst_move=5.037e-01 out_of_range=0 mean_off_1=19142 default_moved=1`
  - head: `RESULT cases=20002 restart_moved=0 worst_move=0.000e+00 out_of_range=0 mean_off_1=0 default_moved=0`
- Class enumerator (`fixer.md` step 8), `kwarg_seams.py` (sha1 `25ec2ea2`), with `python3 kwarg_seams.py custom_components/heatpump_optimizer/optimizer.py`. It lists every `self.<method>(...)` called from two or more sites in one module where a keyword the method defaults is passed at one site and omitted at another. It found `seams=11` at the base and `seams=10` at the head. The seam closed in this diff is `_build_dhw_requirements omits blocked` at the replan. The ten that remain:
  - `_build_dhw_requirements omits space_demand` at the first build. This is by design: the first plan is made before the space profile is known (`_co_optimize` docstring).
  - `_build_result` omits `dhw_cost`, `dhw_power`, `dhw_temps` and `predictive_info` in `_optimize_space_only`. This is a space-only solve with no DHW plan.
  - `_compute_baseline_power` omits `coil_dhw_temp` and `coil_draws` in `_optimize_space_only`. The coil is a DHW input.
  - `_deferred_energy_cost` omits `include_dhw` in `_optimize_space_only`. No DHW store.
  - `_settlement_caps` omits `dhw_cap` in `_terminal_cost` and `_optimize_space_only`. The cap belongs only to the DHW deferred-energy path (`include_dhw=True`).
- Scoped gate at `e6d7b737`: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`, run on a Linux cloud box with CPython 3.14.7, the pinned `tests/requirements-ci.txt`, `OPENBLAS_CORETYPE=Haswell`, 1 thread and `HPO_TYPING_PYTHON` on the pinned typing venv. It printed `MODE: SCOPED -- 22 script(s) run, 5 scoped out.` and `3 TEST SCRIPT(S) FAILED`: `env_drift.py --claims-only` and `--all` (INHERITED CLAIMS) and `features.py` (the non-finite check). All three are answered under Red checks and re-run green at the code head:
  - `python3 tests/features.py`: `ALL 3601 FEATURE CHECKS PASSED`
  - `python3 tests/env_drift.py --all 3dfebc169096e53a5d3713a019de2b525174bc27`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, with 5 `CLAIMED coord_*: 48 leaves moved`
  - `python3 tests/env_drift.py --claims-only 3dfebc16…`: `claims hygiene: … ok`
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`
  - The other scoped scripts passed at `e6d7b737`, and the commit above it touches only `tests/features.py` and the claim file: `ALL 87 STRESS CHECKS PASSED`, `ALL 84 OPTIMALITY CHECKS PASSED`, `ALL 25 BACKTEST CHECKS PASSED`, `ALL 9 typing-ruler checks PASSED` (the pinned census under `HPO_TYPING_PYTHON`), `ALL 56 FINITE BOUNDARY CHECKS PASSED`, `ALL 9 GUARD PIN CHECKS PASSED`, `ALL 1990 ENTITY CHECKS PASSED`, and `ALL CARD CHECKS PASSED`.
- Golden drift: `tests/golden/claimed_drift.txt` claims all five `coord_*` captures. Every moved leaf is a cell of the published `dhw_usage_profile`: 24 in `data` and 24 in the `predictive_insight` sensor attribute, so 48 per capture. No plan, cost or power leaf moves. Hours 01-03 go from 0.103896 up to 0.2, and every other hour goes down by the same factor (0.207792 to 0.205263). I measured this with `env_drift.py --all` against `3dfebc16` with the inherited list emptied, and listed the moved keys per capture with `env_drift._diff_leaves` over `golden.capture_coordinator`. No solver scenario moves, and no golden scenario is DHW-blocked.

## Red checks

- `INHERITED CLAIMS` (`env_drift.py --claims-only` and `--all`, local gate at `e6d7b737`): main's claim list, written for R9-F2.4, carried into the branch. I have not waited for the `claims-autofix` bot, because this diff moves claimable fixtures. The list is rewritten for this diff at `03bb26f1`. `ci-autofix.md` names this case; no cheaper detector is owed.
- `features.py` at `e6d7b737`: `one non-finite entry quarantines the stored hourly profile to the default pattern`. I repointed its expected value at the learner's seed, and `_DhwUsage` overwrites that seed with a flat profile, so the check compared against the flat profile. It was fixed in `03bb26f1`. A cheaper detector exists: running the one section the edit touched before running the whole file. It costs nothing standing, and I name it rather than build it.

## Forward-carry

`.claude/workflows/wave-r9-groups.json` on `handoff/audit-r9-fixplan`, group R9-EG-B5 (commits `63048314` and `d13d6726`). When EG-B5 turns this call site into a planner call, the replan must keep the block. The brief names the two `features.py` checks that pin it and the keyword-seam class. brief_lint on that roster against a fresh main reads `TOTAL: 0 error(s)`.

## Friction

- `defect-root-cause.md`: contradiction: the roster brief asks the fixer for the Root cause section on #1747, while `CLAUDE.md` and `root-cause.md` place root cause in its own seat, and the roster entry has `rca: false`. I have not posted it. A draft is in the resume note for the orchestrator to route.
- `fixer.md` step 5: cost: `features.py` takes about 6 minutes a run on the cloud box, so the four targeted mutants cost two parallel pairs of about 12 minutes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_012YiD7pT3UzZ6qWHVyEP3T7
