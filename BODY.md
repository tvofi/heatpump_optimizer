R11-OUTSIDE-HONEST-DHW-RUNS, group B of the approved design for outside pull request #3529 by @Bankaifan, with thanks: the finding, the store program and the tail are the contributor's. Their build commit `7eeb7cd676` holds groups A, B and C and conflicts with main, so B is rebuilt, not cherry-picked. Design `design/R11-OUTSIDE-HONEST-DHW-RUNS` at `ce85b10049`, `Design review: approve` at `design-verdict/R11-OUTSIDE-HONEST-DHW-RUNS` `53b01494c8`. No issue is closed: the report is the outside pull request.

The failing case: on an install that can duty-cycle, with a start priced, hot-water levels under the pump's floor still shipped (the planner's linear program has no start term and no lower level). On a solve that plans runs the planner now commits its finished plan (`dhw_planner.commit_charges`): the store program's plan or the lifted plan, each clamped to the rating and shipped only if every charge runs at the floor or above (`charges_run`) and `charge_refusal` passes it on the planner's own walk; the uncommitted plan is the one unconditional fallback. A solve that plans no runs hands the planner nothing and its arrays are the base's.

Bindings of the brief:
1. Ruling b: `charge_refusal` calls `drop_unstartable` on the candidate's own walk; the program is handed `startable_steps` of the uncommitted plan as a per-step boolean through `runs.state_moves`, and `runs.py` reads no temperature.
2. One holder of the tank: the linear program's inline free walk moved to `_DhwPlanContext.coast`, which it and the store program read; `runs.py` holds an opaque scalar.
3. Combi: the rounds of `_combi_flux_exchange` keep their order, cap and convergence test and build with a planner handed no runs to commit; one committed build follows on the settled flux, kept only where the store under the committed plan's own flux falls no further under the requirement than the last round's plan (`_COMBI_COMMIT_SLACK_K`). The contributor's recorded finding for R10-COMBI-TANK (the settle) is not built here, as the note routes it.
4. Pricing: candidates are ranked by energy at the planning prices plus `cycling_cost` times `runs.start_count` of the space plan plus the candidate; no stop term is added.
5. Tie break: `runs.tie_break` is the one function `commit` and the store program call; B owns none. R11-OUTSIDE-HONEST-STARTS-RUNS-P2 merged as pull request #3693; its mutants file is re-anchored here, see `## Forward-carry`.
6. The three body items: the unengaged double heating and the settle are not built (the note's routing); a tail on a clamped install is not shipped and is measured (`tail` arm, Figures); a second level at the floor is built and measured (test 4).

Brief carries:
- Carry 0 (groups B and C were in no roster; hot-water levels under the floor still ship on an install that can duty-cycle): B is built here, the failing case is test 1 and the `fixtures` arm. Group C's half is R11-OUTSIDE-HONEST-METERED-FLOOR's and is not touched.
- Carry 1 (the commit takes the rebuilt start rule as its feasibility check): built, binding 1 above; tests 2a to 2c.
- Carry 2 (a second level at the floor): built, the store program's two levels; test 4.
- Carry 3 (this pull request's own `## Forward-carry` item b2ce461c, landed on this group's row): not built here; the settle and the unengaged combi double heating stay unbuilt by the note's routing, and the `combi` arm measures the unengaged fixture (1 combined step under the floor, as on the base). Carry: dismissed: this line answers carry 3; its one destination is the `## Forward-carry` item b2ce461c below, not a second carry
- Carry 4 (this pull request's own `## Forward-carry` item d364f59d, landed on this group's row): measured, not shipped: the `tail` arm (test 7, `## Figures`) reads the same start count with the tail allowed and refused on all three installs and the combi fixture.

Departures from the note, each made for a measured reason and each open to the reviewer:
- The commit stage is a function beside the store program, not a planner method: as a method it breached `class_excess_loc` and `functions_cc_over_15`, both at zero headroom (`python3 tests/structure.py` at `dd3e60ea2d`: `class_excess_loc` +70, `functions_cc_over_15` +2). decision: orchestrator
- The exchange's rounds build with a second planner handed no `ChargeRuns`, not through a keyword on `_dhw_build`: the keyword's branch took `_build_dhw_requirements` over the complexity cap. Same builds, same count (test 6). decision: orchestrator
- The kernel's action takes whether the cells it leaves were running, and the cell rule whether the arrival charged. The first lets the tail be a pausing action open only to a run; the second holds the ceiling on charging arrivals only, since a paused store over its ceiling is the walk's own coast-down.
- The fill to the ceiling is one action: at the floor or above it is a level any install runs, under the floor it is the tail (duty-cycle only, from `min_run_power` up, a run's last step). A step that must land between a floor and a ceiling a tenth of a kelvin apart (a disinfection step, a ready temperature at the charge limit) is reached by no whole step at either level.
- `_STORE_MARGIN_K` (0.02 K) keeps the program inside its bounds so the rating clamp trims no committed step; the linear store and the walk differ by 0.0011 K at most on the fixtures (`stores` arm).
- A plan that already runs, with no start priced, ships as it is (verdict item r9: this rule ships the uncommitted plan there, not the ranking).
- The external-heat suppression takes a committed charge whole or leaves it whole (`whole_charges`, verdict item r3).

## Head

`684f554faf338e82ef5ac7251533d4701383effe`, measured 2026-11-17 (UTC) on a merge base of `5e2ef89b4e` (`git merge-base origin/main HEAD`), `origin/main` at `5e2ef89b4e` when this was written. It is `36af54c383` with `origin/main` merged in (`65be05a2b1`: `tests/features.py`, both sides appended a block, both kept; `tests/golden/claimed_drift.txt`, main's v10.0.3 stamp header and restored may-drift entries, this branch's two claims, the two may-drift entries suspended again for them) and P2's four mutants re-anchored (`684f554faf`). The production delta is `36af54c383`'s: the added and removed lines of `git diff origin/main HEAD -- custom_components/` equal those of `git diff 2d7161a4b7 36af54c383 -- custom_components/` (`diff` of the two line sets exits 0). Figures below not re-taken at this head name the head they ran at.

prepr: passed rc=0 at 684f554faf338e82ef5ac7251533d4701383effe (`PREPR_SKIP_CLOSURES=1`; the last run after a text-only body edit with `PREPR_SKIP_CODE=1`).

## Mutation proof

CMD A, the group's block: `env PYTHONPATH=tests/hastub:custom_components:tests python3 tools/audit/seat/features_block.py --prelude <the block's prelude, written by --emit-prelude> 'R.section("R11-OUTSIDE-HONEST-DHW-RUNS'`. Unedited head: `ALL 32 FEATURES BLOCK PASSED`, exit 0. On `2d7161a4b7`'s production files the block raises `AttributeError: module 'heatpump_optimizer.optimizer' has no attribute '_charge_runs'` at its first solve (the failing-test-first commit `e6899fb176`).

Sixteen mutants named for the design's mutation targets, `python3 -I tools/audit/seat/mutant_run.py --spec <the sixteen> --cmd <CMD A>` at `9c4f723721` (`git diff --stat 9c4f723721 HEAD` is the harness's timing arm and the rename of the leaf's move rule to `runs.state_moves`, after which CMD A prints `ALL 32 FEATURES BLOCK PASSED` and the `kernel` arm the same digest), in its default `git archive` copy: `SURVIVED NULL` and sixteen `KILLED`, rc 0. The checks each fails:
- the engaged guard (`_charge_runs` returning `None` always): `acceptance: on an install that can duty-cycle ...`, `unengaged ... the optimizer hands the planner no ChargeRuns ...`, and the combi block raises.
- the boolean not handed to the move rule: `ruling b: the store program is handed where the pump would start ...`.
- the start clause removed from `charge_refusal`: `ruling b ...`, `the acceptance refuses a plan whose second charge opens at its start temperature ...`, `the lifted plan ships only through the acceptance ...`.
- the lifted plan exempt from the acceptance: `the lifted plan ships only through the acceptance ...`, `the acceptance refuses a lifted plan whose clamped tail ...`.
- the shortfall clause removed: `the acceptance refuses a lifted plan whose clamped tail ...`, `the acceptance's floor clause passes a walk exactly the tolerance under ...`, `the store program returns no plan where a floor is over the ceiling ...`.
- the floors out of the cell rule: 11 of 32, the first `acceptance: on an install that can duty-cycle ...`.
- the floor level taken from the program: `a second level at the floor ...`, `the tail ...`, `a forced-off step stays off ...`.
- the tail's install guard (tails on every install): `the tail: on an install that can end a run at any moment ...`.
- the ranking's start term removed: `the commit ranks its candidates by energy plus the starts of the combined draw ...`, `at a 5-minute step ...`.
- the ranking's space plan removed: `the commit ranks its candidates ...`.
- the fallback to the uncommitted plan replaced by the lifted plan: `the lifted plan ships only through the acceptance ...`, `the acceptance refuses a lifted plan whose clamped tail ...`.
- the kernel's cheapest-per-cell line (dearest kept): 9 of 32, among them `the generalised kernel's cost equals an exhaustive search's ...`.
- the kernel's action index written as 0: the block raises `ValueError` in the read-back's replay (a kill by exception, not by a check; the exhaustive-search check is the one that reads the index).
- the exchange's rounds built with the committing planner: both `combi:` checks of test 6.
- the exchange's acceptance removed: `combi: the committed build ships where the store under its own flux holds ...`.
- `whole_charges` keeping the mask as it is: `a suppression takes a committed charge whole or leaves it whole ...`.

Every mutant of the diff's added lines (the contract's first 40 raised to all): `mutant_run.py --diff 2d7161a4b7...HEAD --path <file> --cmd <CMD A> --max-mutants 400 --report-only` per production file at `2231093947`, 165 mutants of `dhw_planner.py`, 46 of `runs.py`, 26 of `optimizer.py`, rc 0 each: 18, 14 and 2 survivors. CMD B, group A's leaf checks of `runs.commit` (its block from its section to `_HSR_STEPS = np.arange(96)`), over `runs.py`'s 46: 6 survivors, so 10 of CMD A's 14 are `commit`'s own lines, which the group's block does not drive and group A's does. Three more were killed after that drive by checks added since (`runs.py`'s two flags, the build's call of `whole_charges`; the last re-run alone as a spec: `KILLED SUPPRESSION_WIRING`). The 20 lines that still hold a survivor are each triaged under `## Unpinned sites`.

## Null control

- A solve that plans no runs: `optimizer._charge_runs` returns `None` and `commit_charges` returns the plan object it was given (block check 3). The harness's `fixtures` arm with the planner handed no `ChargeRuns` prints, on this head, the lines the same harness prints in a `git archive` copy of `2d7161a4b7` (Figures), and `env_drift.py --all` finds 54 of 56 fixtures byte-identical to the base.
- `runs.commit`: the sha1 over its masks and band verdicts on 1200 random cases is the base's (`kernel` arm, Figures).
- Kernel: the exhaustive search with the bounds ignored is cheaper than the kernel on 60 of 60 cases, so the agreement at 800 cells is the bounds' (block check, `kernel` arm).
- Ruling b: with no start condition known the program runs once and its plan ships; with one, the same tank takes more than one round (block checks 4 and 5).
- Lifted plan: the fixture whose lift carries less far ships the lifted plan (block check 7).
- Shortfall clause: the same clamped lifted plan passes against no floor (block check 8).
- Pricing: the same two candidates ship the other way with no space plan, and with no start priced (block check on the ranking).
- Tail: the same tank on an install that cannot end a run inside a step ships no step under the floor.
- Combi: an unengaged solve makes no committed build and ships the last round's plan; with the slack taken away the engaged one does too.
- Suppression: on a solve that plans no runs the mask is returned as it is.

## Figures

All on one box (x86_64), at `36af54c383993b5d7bcdffe8b83e1e9ca76b17dc` unless named (the merge and the re-anchor change no production file; the lines naming `684f554faf` were re-taken there) (the harness arms ran at `e9c1d2291d`, before that rename); base `2d7161a4b7`, read from a `git archive` copy with this head's harness file copied in (sha1 `33f36cbb77d490508b2569434ce20616386f5eca`).

- Failing case, `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_dhw_runs.py fixtures`, exit 0. Head: `cycling_cost committed: charges 3, hot-water steps under the floor 0 (not a charge's last 0), combined 0 (0), worst gap 0.439 K, start count combined 3.00 hot water alone 3.00, published starts 3, energy_kwh 42.45, predicted_cost 33.76`; `everything_on committed: charges 3, hot-water steps under the floor 0 (not a charge's last 0), combined 0 (0), worst gap 0.438 K, start count combined 3.00 hot water alone 3.00, published starts 3, energy_kwh 68.64, predicted_cost 61.83`. The same arm with the planner handed no `ChargeRuns`, head: `cycling_cost uncommitted: charges 9, hot-water steps under the floor 14 (not a charge's last 14), combined 11 (11), worst gap 0.557 K, start count combined 5.90 hot water alone 10.50, published starts 4, energy_kwh 40.97, predicted_cost 32.07`; `everything_on uncommitted: charges 5, hot-water steps under the floor 10 (not a charge's last 10), combined 4 (4), worst gap 0.550 K, start count combined 5.66 hot water alone 7.23, published starts 5, energy_kwh 68.83, predicted_cost 61.48`. Base copy, the same command: the two `uncommitted` lines, character for character (`diff` of the two outputs' `uncommitted` lines exits 0).
- Per build (same arm, verdict items r1, r2, s8): `cycling_cost` builds twice; with no space plan the program's plan (3 charges) is the one candidate and ships, with the space plan known its plan has 6 charges and ships; the lifted plan is refused by `charges_run` both times. `everything_on` builds once: the program's plan and the lifted plan are both accepted and the program's ranks lower. Program rounds 1 of 8 in every build.
- Start rule on the fixtures (item s1), `... r11_honest_dhw_runs.py hysteresis`, exit 0: 20 cells (two fixtures, ten hysteresis values from 0.5 to 10 K), 28 builds; rounds 1 or 2; 8 program plans refused for a start and re-run; 0 builds ship the uncommitted plan; `drop_unstartable` removes 0 charges from any shipped plan; 0 shipped steps under the floor that are not a charge's last.
- Linear store against the walk, `... r11_honest_dhw_runs.py stores`, exit 0: largest difference 0.0011 K over the uncommitted and shipped plans of every build (`_STORE_MARGIN_K` is 0.02 K).
- Kernel, `... r11_honest_dhw_runs.py kernel`, exit 0, head and base copy: `runs.commit over 1200 random cases: sha1 c87fe02dd94b0b3ffaa19fd4f709ad8acc1b46dd` on both. Head: the kernel's cost equals the exhaustive search's on 60 of 60 cases at 800 cells, 59 at 400, 53 at 100, 35 at 20, and never beats it; with the bounds ignored the search is cheaper on 60 of 60.
- Combi (item s4), `... r11_honest_dhw_runs.py combi`, exit 0, head: `combi, a start priced: rounds 3, committed builds 1, committed build shipped True, hot-water steps under the floor 0 (not a charge's last 0), combined 0, worst gap -1.617 K, dhw_kwh 20.59`; `combi, cannot duty-cycle: rounds 3, committed builds 1, committed build shipped True, hot-water steps under the floor 0 (not a charge's last 0), combined 0, worst gap -1.887 K, dhw_kwh 20.90`; `combi, null, unengaged: rounds 3, committed builds 0, committed build shipped False, hot-water steps under the floor 1 (not a charge's last 1), combined 1, worst gap -1.768 K, dhw_kwh 20.63`. Base copy: `combi, a start priced: rounds 3, committed builds 0, committed build shipped False, hot-water steps under the floor 1 (not a charge's last 1), combined 1, worst gap -1.737 K, dhw_kwh 20.59`; `combi, cannot duty-cycle: rounds 3, committed builds 0, committed build shipped False, hot-water steps under the floor 0 (not a charge's last 0), combined 0, worst gap -1.818 K, dhw_kwh 20.68`; `combi, null, unengaged: rounds 3, committed builds 0, committed build shipped False, hot-water steps under the floor 1 (not a charge's last 1), combined 1, worst gap -1.768 K, dhw_kwh 20.63`. The unengaged line is the base's.
- Tail (test 7), `... r11_honest_dhw_runs.py tail`, exit 0:
  - `duty-cycle (clamped False, floor 1.5) tail refused: hot-water steps under the floor as planned 0 as shipped 0, start count combined 5.00, energy_kwh 26.04, worst gap 0.881 K`
  - `duty-cycle (clamped False, floor 1.5) tail allowed: hot-water steps under the floor as planned 1 as shipped 1, start count combined 5.00, energy_kwh 25.97, worst gap 0.880 K`
  - `modulating clamped (clamped True, floor 1.5) tail refused: hot-water steps under the floor as planned 0 as shipped 0, start count combined 5.00, energy_kwh 26.04, worst gap 0.881 K`
  - `modulating clamped (clamped True, floor 1.5) tail allowed: hot-water steps under the floor as planned 1 as shipped 0, start count combined 5.00, energy_kwh 26.23, worst gap -0.221 K`
  - `fixed-speed (clamped True, floor 5.5) tail refused: hot-water steps under the floor as planned 4 as shipped 0, start count combined 5.00, energy_kwh 27.50, worst gap -0.203 K`
  - `fixed-speed (clamped True, floor 5.5) tail allowed: hot-water steps under the floor as planned 4 as shipped 0, start count combined 5.00, energy_kwh 27.50, worst gap -0.203 K`
  - `combi fixture (clamped True) tail refused: hot-water steps under the floor as planned 0 as shipped 0, start count combined 6.00, energy_kwh 30.13, worst gap -1.887 K`
  - `combi fixture (clamped True) tail allowed: hot-water steps under the floor as planned 0 as shipped 0, start count combined 6.00, energy_kwh 30.13, worst gap -1.887 K`
- Solve time (item r4), `... r11_honest_dhw_runs.py seconds`, exit 0, CPU seconds, least of five. Head: `cycling_cost` 0.32 committed and 0.17 uncommitted, `everything_on` 3.88 and 3.55. Base copy: 0.18 and 3.40. `tests/stress.py` under the gate lease at `2231093947`: `ALL 116 STRESS CHECKS PASSED`. The `stress` arm of `r11_honest_starts_runs.py` was not run.
- Duty-switch block, three days restated (commit `9c4f723721`). Two-descent arms on the duty-cycle install by outdoor mean, a scan appended to a scratch copy of the block (not in the tree): head at -1 degC `both 29.1234, operand 29.1234, unpriced 29.6649, no operand 29.6649`; at -4 degC, the day the check read before, all four are 35.8049. Base copy at -4 degC: `both 37.4775, operand 37.4775, unpriced 37.8683, no operand 37.7296`.
- P2 merged as pull request #3693. On this head, `python3 -I tools/audit/seat/mutant_run.py --spec <the four re-anchored entries> --cmd <features_block.py from group A's section to this group's, with its emitted prelude>` in its default `git archive` copy: `SURVIVED NULL`, `KILLED OUT_OF_BAND_PENALTY`, `KILLED START_COST_EDGE`, `KILLED REV3_TIE_NOT_ASKED_SIDE_OFF`, `KILLED REV3_TIE_ASKED_SIDE_OFF`, rc 0. Enumerator for the stale entries, the count of `r11_honest_starts_runs_mutants.json` entries whose `old` occurs other than once in its `file`: 4 at `65be05a2b1`, 0 at `684f554faf`.
- Drift: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 2d7161a4b7` at `2231093947`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE`, exit 0; before the two claims were rewritten the same command printed `2 UNCLAIMED DRIFT(S)` (`cycling_cost`, `everything_on`), exit 1. At this head against the new merge base, `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 5e2ef89b4e`: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE: 56 committed fixture(s) still match`, exit 0.
- Scope at this head: `python3 tests/closure.py select --diff 5e2ef89b4e --workdir <dir>`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=5e2ef89b4e ./tests/run.sh` at `684f554faf`: `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`, exit 0 (`ALL 5864 FEATURE CHECKS PASSED`, `ALL 2731 ENTITY CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED`). Before the merge, `python3 tests/closure.py select --diff 2d7161a4b7 --workdir <dir>`: 27 scripts run, 6 scoped out. `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=2d7161a4b7 ./tests/run.sh` at `2231093947`: 24 scripts passed and `tests/features.py`, `tests/entities.py`, `tests/typing_ruler.py` failed (`## Red checks`); the three alone at `9c4f723721`: `ALL 5812 FEATURE CHECKS PASSED`, `ALL 2723 ENTITY CHECKS PASSED`, `ALL 9 typing-ruler checks PASSED`, exit 0 each.
- `python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, governance or instrument red predicted against 2d7161a4b709`, and 79 unpinned sites (`## Unpinned sites`).

<!-- figure-block: scope-line mb=5e2ef89b4e7348b190aa917dc032da73ba04998e head=684f554faf338e82ef5ac7251533d4701383effe -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Architecture score

Architecture score: dS +0.0000 NULL

`python3 tools/audit/archscore/score.py --diff 2d7161a4b7` at the head. `python3 tests/structure.py`: `methods_over_200` 7 to 6, recorded (the linear program's free walk moved to `_DhwPlanContext.coast`); no metric up.

## Unpinned sites

- `custom_components/heatpump_optimizer/dhw_planner.py:318 CONST`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:324 CONST`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:325 CONST`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:330 CONST`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:347 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:349 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:351 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:352 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:358 CMP_BOUND*3`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:360 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:368 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:370 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:373 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:464 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:551 CLAMP_DROP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:553 CLAMP_DROP`: written triage: a survivor (the COP table two knots longer) is equivalent: the extra rows are never interpolated to; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:563 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:571 CMP_BOUND*2`: written triage: a survivor (share >= 0) differs only for a tank exactly on its mark, where the fill's level is 0 and the floor test refuses it; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:580 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:590 CMP_BOUND`: written triage: survivors (the floor's 1e-9 slack, its boundary) are a tie of measure zero; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:591 CMP_BOUND`: written triage: a survivor (level > min_run_power) is a tie of measure zero; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:598 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:615 CMP_BOUND*3`: written triage: survivors (the floor's boundary; cell 0): a tie of measure zero, and cell 0 lies a kelvin under every floor; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:616 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:617 CMP_BOUND`: written triage: survivors (the ceiling's boundary and its 1e-9 slack) are a tie of measure zero; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:618 CLAMP_DROP`: written triage: a survivor (clip to cell 1): cell 0 lies a kelvin under every floor and is never arrived in; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:618 RETURN_DEL`: written triage: a survivor (clip to cell 1): cell 0 lies a kelvin under every floor and is never arrived in; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:624 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:629 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:630 BOOLOP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:630 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:633 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:644 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:646 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:649 RETURN_DEL`: written triage: a survivor (the closing return None) is equivalent, the function ends there; the line's other mutants are killed
- `custom_components/heatpump_optimizer/dhw_planner.py:677 CMP_BOUND*3`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:677 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:679 BOOLOP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:679 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:679 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:683 CLAMP_DROP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:684 CLAMP_DROP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:688 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:691 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:693 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:697 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:699 CLAMP_DROP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:702 CMP_BOUND*2`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:704 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:1950 CMP_BOUND`: written triage: a survivor (gaps >= the tolerance): the base's comparison with its literal named, a tie of measure zero; the line's other mutants are killed
- `custom_components/heatpump_optimizer/optimizer.py:207 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:209 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:2049 CONST`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:2083 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:2087 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:2094 GUARD_OFF`: written triage: a survivor (atol 1e-5): the base's convergence tolerance on a line this diff reflowed; the line's other mutants are killed
- `custom_components/heatpump_optimizer/optimizer.py:2097 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:2106 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:2108 CMP_BOUND`: written triage: a survivor (<) is a tie of measure zero; the line's other mutants are killed
- `custom_components/heatpump_optimizer/optimizer.py:2109 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:155 CLAMP_DROP`: killed by group A's leaf checks of `runs.commit` (Mutation proof, CMD B); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:156 CLAMP_DROP`: written triage: a survivor (clip to cell 1): the base's clip, moved into commit's cell rule; cell 0 is the band's far edge; the line's other mutants are killed
- `custom_components/heatpump_optimizer/runs.py:156 RETURN_DEL`: written triage: a survivor (clip to cell 1): the base's clip, moved into commit's cell rule; cell 0 is the band's far edge; the line's other mutants are killed
- `custom_components/heatpump_optimizer/runs.py:159 CMP_BOUND`: killed by group A's leaf checks of `runs.commit` (Mutation proof, CMD B); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:202 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:217 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:218 CLAMP_DROP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:219 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:221 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:222 CLAMP_DROP`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:224 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:229 RETURN_DEL`: killed by group A's leaf checks of `runs.commit` (Mutation proof, CMD B); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:254 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:256 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:259 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:264 GUARD_OFF`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:272 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:282 CMP_BOUND`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/runs.py:284 RETURN_DEL`: killed by the group's block (Mutation proof, CMD A); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/dhw_planner.py:546` (no site of step 6d's): written triage: a survivor (the assert) is a typing narrowing with no behaviour
- `custom_components/heatpump_optimizer/dhw_planner.py:573` (no site of step 6d's): written triage: a survivor (the level where there is no fill) is read only where a fill was taken
- `custom_components/heatpump_optimizer/dhw_planner.py:605` (no site of step 6d's): written triage: a survivor (the grid one table knot narrower): the top kelvin is headroom over every ceiling
- `custom_components/heatpump_optimizer/dhw_planner.py:610` (no site of step 6d's): written triage: a survivor (the origin's cost 1.0) is a constant on every path, so the cheapest is the same
- `custom_components/heatpump_optimizer/dhw_planner.py:692` (no site of step 6d's): written triage: a survivor (the step of a level refusal): the step is read only for a start refusal
- `custom_components/heatpump_optimizer/runs.py:60` (no site of step 6d's): written triage: a survivor: a type alias, read by annotations only
- `custom_components/heatpump_optimizer/runs.py:64` (no site of step 6d's): written triage: a survivor: a type alias, read by annotations only
- `custom_components/heatpump_optimizer/runs.py:266` (no site of step 6d's): written triage: a survivor (the continue): no destination arrives with no finite cost in the block's cases

## Red checks

none open at the head. Three scripts of the scoped gate went red on a commit of this branch (`2231093947`), each repaired before the handoff:
- `tests/features.py`: seven checks outside the group's block (the combi flux census reading the linear program's source, and six checks of the duty-switch block whose days made no priced switch once hot water was committed). Cheaper detector: none; the block that failed is the cheapest reader of those solves, about ten minutes of the script's fifteen.
- `tests/entities.py`: the P2 owners registry's disposition for the tolerance literal in `_dhw_shortfall`, stale once the literal was named. Cheaper detector: the script itself, under two minutes; it was in the scoped set and was run late, after the mutation drives, which is the order's fault and not the check's.
- `tests/typing_ruler.py`: one `arg-type` on the exchange's shortfall. Cheaper detector: the same mypy on the three changed files, under two minutes; not run before the gate.

## Forward-carry

- R11-OUTSIDE-HONEST-STARTS-RUNS-P2 merged (pull request #3693) with `dev/audit/harnesses/r11_honest_starts_runs_mutants.json`; four of its 54 entries named `runs.py` lines this group rewrites, and on the merge of `origin/main` into this head their `old` text occurred 0 times in `runs.py`: `OUT_OF_BAND_PENALTY` (now the fine in `commit`'s `cells`), `START_COST_EDGE` (now `advance`'s `c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts, _, _, paid in took]) + extra`), `REV3_TIE_NOT_ASKED_SIDE_OFF` and `REV3_TIE_ASKED_SIDE_OFF` (both halves now `runs.tie_break`'s return). Re-anchored in this pull request, same mutation on the moved line (Figures). Enumerator: the entries of that file whose `old` occurs other than once in its `file`; 4 at the merge, 0 after. R11-OUTSIDE-HONEST-STARTS-RUNS-P3 (pull request #3697) carries the harness forward and drives the same spec: it reads the re-anchored entries once this merges. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS-P3
- The settle and the unengaged combi double heating are not built (the note's routing: a group of their own on the candidate stage's seam). `combi` arm: after B the engaged combi fixture ships no combined step under the floor; the unengaged one ships 1, as the base does. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (decision: orchestrator, the note's Decisions routed)
- The clamped tail, test 7's figures (`tail` arm): the start count of the combined draw is the same with the tail allowed and refused on all three installs and the combi fixture, so it saves no start there. Carry: R11-OUTSIDE-HONEST-DHW-RUNS (decision: owner, the note's Decisions routed)
- On the fixed-speed install of `r11_honest_starts_runs.py` (floor 5.5 kW) the planner's run power, 0.8 of the pump's maximum, is under the floor, so the commit stage returns the plan as it is and the optimizer's projection raises it, as at the base (`tail` arm: 4 steps under the floor as planned, 0 as shipped). The floor's value is R11-OUTSIDE-HONEST-METERED-FLOOR's. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR
- On the base and the head alike the two-descent solve scores above one of its arms alone on some days (the scan under Figures: base at -6 degC `both 43.2343, operand 42.8717`; head at -2 degC `both 31.4801, operand 31.4193`), so "ships the lower" holds on the days the block reads and not on every day. Not this group's seam (the candidate stage). Carry: R11-OUTSIDE-HONEST-STARTS-RUNS-P3

## Friction

- `fixer.md`: `unclear`: step 2: `prepr.sh`'s drive mutates the first 40 added lines in file order, which on this diff is `dhw_planner.py`'s first 40 of 237; the survivors that mattered (the build's call of `whole_charges`, the kernel's two flags) were past it and found only by raising `--max-mutants`. Carry: dismissed: one fixer's reading, no second instance
- `gate-scoping.md`: `cost`: `tests/run.sh` keeps no log of a failed script (the lane log is overwritten), so `tests/features.py`'s seven failures cost a second 15-minute run to read. Carry: dismissed: one occurrence, not measured against a second
- `finding-propagation.md`: `unclear`: a dependency on a handed-off, unmerged predecessor (P2's mutants file) has no tree to land a carry in; it is named in this body only. Carry: R11-OUTSIDE-HONEST-STARTS-RUNS-P3
