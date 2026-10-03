R9-EG-A2 (lane EG, classes P2 and P3). Closes #1775.

This PR does three things:
- **One copy per formula and helper.** It consolidates the duplicates the brief sampled across `thermal_model`, `inputs`, `store`, `sysid`, `dhw_planner`, `config_flow` and `optimizer`.
- **One loss per physics step.** `ThermalModel._substeps_and_loss` replaces `_stability_substeps` and returns the loss each step was judged with, so the step does not compute it a second time.
- **A gap-tolerant C3 in the architecture score.** Per tvofi's decision, in the score's copy only, a clone window is any two statements of a block, in order (`counters.gapped_clones`). Interleaved junk can no longer split a clone, whatever its spelling. This replaces the statement-dropping C3, which every review round beat with a new spelling.

## Head

227172ac51b36042d1d604594bf9c92a5c011073 (merge base `origin/main` 1ccd0b1d5e2e2f21260d1b685271ac97fc7cb28f, measured 2026-10-03T16:02Z)

## Mutation proof

- **Production consolidation.** Inlining `_two_zone_rates` back into `_simulate_step_two_zone` makes `python3 tests/structure.py` print `FAIL duplication_copies 39 > 38 (+1)`.
- **C3.** With `ARCHSCORE_ABLATE=C3`, 26 of the 28 interleaving attempts read IMPROVES. The other two are 04b, which is inadmissible on coord_footprint, and 04f, whose string junk the shared census already skips as a docstring. With the round-2 statement-dropping C3, the five new GAMEs 04x to 04zb read IMPROVES (+10.77 to +14.15); with this C3 they read NULL. Both runs used `calibrate.py --only`.
- **Ledger.** Every one of the 32 sites this diff adds now has a disposition in `tests/mutation_ledger/`:
  - 30 `killed_by` anchors covering 31 sites. Each was driven by hand on an export of the branch, applying the table's own kill rule: the run must be red and must name a check the baseline does not. The reason field of each entry gives the driver and the check that failed.
  - 1 `survivor_triage` equivalent.
- **Five survivors closed with checks.** These five survived until this PR added a check in `tests/features.py`; with the check in place, each mutant fails it:
  - `_within_ceiling` CLAMP_DROP
  - `_tank_decay` CLAMP_DROP
  - `_r2_confidence` R² clip
  - `_r2_confidence` strict 1e-9 floor
  - `_substeps_and_loss` strict 1e-6 buffer floor

## Null control

- **Physics parity.** Base vs head, 0 of 2880 arrays differ bitwise. The base is an export of `origin/main` 1ccd0b1d5. The harness is the round-1 reviewer's `mypar2.py` with only its path changed (my scratch `h/parity2.py`, sha1 a08a07c7c55faf673ec0d762041f5f7d6e5ae218, compared by `h/compare.py`). It covers two-zone and wood combinations, up to 15 substeps, and scalar vs batch, where the difference is 0.0. Its control re-associates one sum in `_two_zone_rates`, which changes 218 of 2880 arrays.
- **Production calls.** Every one of the 20 scenarios is at or under 1.0009x of `origin/main`. The 3.11 emulation of `stress.py`'s channel (my scratch `h/calls311.py`, sha1 664c14a7b42901906146d78014850f8793301a3d) uses `sys.setprofile` for `sys.monitoring` over `stress.calls_population`. On the two-zone delta it reproduces CI's per-scenario `thermal_model.py` growth at the round-2 head exactly, for example summer/2z/space +23121. Using the table's own verdict, `stress.calls_drift`, 0 scenarios are over.
- **Calibration.** At `origin/main` the KNOWN-OPEN three read IMPROVES. At the head, `calibrate.py --record` reads RED TEAM 44/44 NULL or inadmissible, with no SENSITIVE line. The one planted verdict that moved is explained under Figures.
- **Goldens.** `env_drift.py --all 1ccd0b1d5` prints NO UNCLAIMED DRIFT for 56 scenarios.

## Figures

- **Structure.** duplication_copies 59 -> 38, functions_cc_over_15 34 -> 33, max_cc 48 -> 45, max_method_loc 385 -> 377. Measured with `python3 tests/structure.py` at the head against `tests/structure_budgets.json`. The reasons are in commit 9b794c342.
- **Score.** `PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff origin/main` gives dS +2.9509, from the gap census's duplication_copies 87 -> 69. With `ARCHSCORE_ABLATE=C3` it gives +5.5519, from the shared census's 59 -> 38. No score metric rises.
- **Planted verdict that moved.** `a1_G2_dedupe` goes GOOD/IMPROVES -> NULL. After G2 the two fabric learners still share 12 ordered statement pairs, so under any gap they remain one clone class. The detail is in `tools/audit/archscore/ABOUT.md`.
- **Corpus.** No corpus verdict moved; 81 vectors were re-measured. The matcher cost 228 s, against 208 s for the previous C3, measured with `calibrate.py --measure-corpus --jobs 4`, one run each.
- **Ledger.** 0 completeness problems and 0 added unpinned sites, with 4803 unpinned against 4852 at the merge base. These figures come from `tests/mutation_table.py`'s own pre-baseline functions, run in `main()`'s order by a scratch harness of mine that is not in the tree (sha1 d3fe581361c2bc41b53a66882df201afbb446e8a).
- **Equivalent survivor.** `_padded_nonneg` CMP_BOUND: `PYTHONPATH=tests/hastub python3 tools/audit/round9/EG/a2/padded_equiv.py` finds 0 of 15120 inputs differing, and its tie-only control differs on 288 of 288 ties.
- **Scoped gate.** `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=1ccd0b1d5 ./tests/run.sh` reports `MODE: SCOPED -- 25 script(s) run`. 21 scripts are green; the four red are listed under Red checks.

## Red checks

- **`fast (3.14)`: `stress.py` production calls.** At c0f81ac9, 20 of 20 scenarios were over 1.05x, the worst 1.176x. The cause was the new helpers running twice per step and once per sub-step. It is answered by the one-loss step above, now at most 1.0009x. The cheaper detector is that same call channel, which I could not run locally because 3.11 has no `sys.monitoring`. The emulation above runs in about 3 minutes and would have caught it before the push.
- **`mutation`: refused.**
  - First, on two (later four) ledger entries the consolidation moved. The cheaper detector is the table's completeness check, which takes seconds.
  - Then on 27 new sites with no result, and the pin step timed out at 60 minutes. There is no cheaper detector for kills short of driving each mutant. The hand drive took about 2 hours on 4 workers, because `--pin-killed` refuses on a machine whose `features.py` baseline is red.
- **Local only, not from this diff.** These four fail on this machine (3.11.5, Accelerate): `features.py` R9-F2.1 P3, which gives the same two values at `origin/main`; `entities.py` and `harness_headers.py`, which use a 3.12 f-string; and two `stress.py` checks, `sys.monitoring` and the CPU factor on a loaded machine. CI is the authority.

## Forward-carry

none: no not-started brief (R9-EG-A3, R9-EG-A4, R9-EG-B11) rests on C3, the KNOWN-OPEN cases or the duplication figure. The score's new C3 and its limits are documented in `tools/audit/archscore/ABOUT.md`, where the score is read.

## Friction

- fixer.md: cost: `mutation_table.py --pin-killed` refuses wherever `features.py`'s baseline is red for the environment, and CI's pin step timed out at 32 sites. A seat on a Mac has no supported way to pin.
- gate-scoping.md: unclear: `stress.py`'s production-call channel needs 3.12+ (`sys.monitoring`), so a 3.11 seat cannot run the check that turned this PR red.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
