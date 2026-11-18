Part 2 of R11-OUTSIDE-HONEST-STARTS-RUNS-P3. The finding is from Bankaifan's outside pull request 3529, with thanks. This part answers roster carries 2, 4, 5 and 6, and merges origin/main into pull request 3529. The one code change is the P2 mutants spec, re-anchored at main (carry 5). Carries 2 and 4 are already built on main. Carry 6 reproduces, but no change inside the candidate stage can hold the property it states: it is routed as a decision, with the numbers.

### The brief's carries

- **Carry 0 and Carry 1** (the clamped default start price, owner ruling Q2): built by part 1, #3697, merged at 332da69b74. Not rebuilt here; the roster lists them pending until a mark-carry lands.
- **Carry 2 and Carry 4** (item 1d1c10a9, item ad4f75a0: the `median_off_s` headroom cut after a duty change, said to be not built). **Already built on main** by R10-DUTY-SWITCH-PLANNER-PRICE at 4a8115bc10:
  - `duty_legs.lost_share` is p x off seconds over the step.
  - `duty_legs.availability` charges the step a hot-water-to-heating change falls in.
  - `duty_legs.space_headroom` bounds a duty-cycle install's heating there at avail x p_max - dhw.
  - The candidate stage applies it per candidate. `_best_runs` rescopes each candidate through `_space_scope` and clips it to its own bound.
  - It is pinned on the engaged (priced) solve's shipped plan by the `tests/features.py` check `on the duty-cycle install the solved heating in every charged step is at most avail x p_max - dhw, and a charged step exists`.
  - On a clamped install the cut lands in `duty_legs.delivered_space`, not the bound, and is pinned by the checks beside it.
  - The "not built" sentence is the contributor's note (`docs/design/2026-11-12-honest-starts-and-runs/design.md`, "Duty-switch price"). It describes their own build, against a base before 4a8115bc10. Measured under `## Null control`. Nothing is built here.
- **Carry 3** (item 2e78177c): three live checks on a test fork need `gh`, an App key and a fork pull request. That is an orchestrator act; see `## Forward-carry`.
- **Carry 5** (item 72ce280b, P2's mutants file): re-anchored at main.
  - Enumerator: the entries of `dev/audit/harnesses/r11_honest_starts_runs_mutants.json` whose `old` occurs other than once in its `file` (the refusal rule of `mutant_run.py`'s spec mode). 5 at the merge base, 0 at the head.
  - `ENGAGED_COST_ARM`, `ENGAGED_CLAMP_ARM`, `UNPRICED_DESCENT` and `UNPRICED_DESCENT_COST_ARM` named `opt.config.cycling_cost > 0`, which #3697 rewrote to `opt.config.start_price > 0`. Each now names the same mutation on the moved line.
  - `IDENTITY_GUARD` is dropped. It mutated `_commit_runs`' early return for an engaged solve with no start price, which #3697 deleted (its body, "What was deleted"), so there is no line left to mutate.
  - The spec's other 49 entries are byte-identical.
- **Carry 6** (item 2d9b0f43): the two-descent solve scoring above one of its arms alone. **Reproduces at the merge base**, in 1 of 12 cells. No change inside the stage holds the property (`## Figures`), so nothing is built; the decision is routed under `## Forward-carry`.
- **Carry 7** (item be94cc35): a `finding-propagation.md` `unclear`. This is a policy and instrument carry for the round-end proposal triage, not this part's. It is restated under `## Friction`.

### Pull request 3529, merged with main

- Branch: `handoff/r11-outside-honest-starts-runs-p3-3529`, head 345d32d62de2677080b66c8035540c09e5d7d3d9. It is a merge of origin/main 7c2f4c30ca into the pull request's head 1f9daef4d9.
- **Result:** the merge's tree is origin/main's, plus the contributor's later wording in their design note. `git diff --stat origin/main 345d32d62d` prints one file, `docs/design/2026-11-12-honest-starts-and-runs/design.md`, 2 lines.
- **Rule:** main where its merged group builds the row; the contributor's where main has nothing and no other group owns it; a union where both carry content.
- **A brief premise did not hold.** Groups A (#3602, #3693, #3697) and C (#3670) are merged. Group B, R11-OUTSIDE-HONEST-DHW-RUNS, is not: `refs/heads/handoff/r11-outside-honest-dhw-runs` is at 684f554faf and no first-parent merge on main names it. So the contributor's hot-water rows have a live owner, and are not carried into this merge.

| file | kept from main | kept from the contributor | why |
|---|---|---|---|
| `runs.py` | all | none | Main's runs module (#3602) builds the count, the commit, the bands and the run and pause lengths (`MIN_RUN`, `MIN_PAUSE`). The contributor's `Store`, `commit_store`, `charge_shares` and `ChargeCosts` are the hot-water store program, group B's. Its start count's hot-water and duty-stop arguments are part 6, which the approved design drops (ruling a). |
| `optimizer.py` | all | none | Main has the candidate stage (`_relaxed_plans`, `_commit_runs`, `_best_runs`, `_resolved_runs`), `_engaged` on `start_price`, `SolveInputs.compressor_running` and the `_fd_rows` free-variable gradient. Main deleted `cycling_penalty`, `cycling_penalty_batch`, `_relaxed_starts` and `_scores_rounded` too, and keeps the three projection functions the design keeps. The contributor's `_settled_space`, `_held_round` and `_TRIM_SHARES` (combi hold and settle) and `_charge_runs` (`charge_running`) are group B's. `_start_term_off` is replaced by `_descent_pair` (design: no mutable solve state). `_failed_guess` is not carried: main's failure path ships the guess, and `_realize_joint` projects it before publication. The engaged-cap `dhw_floor_breach_c` extension is a hot-water shortfall, group B's. |
| `dhw_planner.py` | all | none | `_under_floor_off`, `_commit_charges`, `_stored_charges`, `_charge_costs` and `ChargeRuns` are group B's, which owns the tank dynamics (design ruling c3). |
| `draw_range.py` | all | none | Main's metered floor (#3670: `floor_kw`, `floor_since`, `update_floor`, `solve_band(applies_floor=...)`) serves the contributor's floor store and `learned_min_kw`, keyed and lapsing. The contributor's `when_s` arguments and `floor_source` are served by main's `min_source` and `min_samples`. |
| `store.py` | all | none | Main persists `draw/floor_kw` and `draw/floor_since`. The contributor's `draw/floor/#/0` and `#/1` belong to the per-sample store main does not have. |
| `duty_switch.py` | all | none | `planner_fields` and `planner_pairs` supply the pairs (`duty_switch_stop_probability`, `duty_switch_off_seconds`). `running_now` reads `running_signal`'s settled class. `planner_reading` and `duty_stop_to_space`/`duty_stop_to_dhw` are part 6, dropped by the design (ruling a). |
| `early_cutoff.py` | all | none | Main imports `MIN_RUN` and `MIN_PAUSE` from `runs.py`, the contributor's move under main's names. The contributor's `from .runs import MIN_OFF, MIN_ON` would not import on main's runs module. |
| `coordinator.py` | all | none | Main passes `compressor_running=duty_switch.running_now(...)`, which uses the executing step as the fallback (design note n5). The contributor's `_running_fields`, spread into the same `SolveInputs` call, would pass `compressor_running` twice. `charge_running` is group B's. `_solve_band`'s `engaged=cycling_cost > 0` is ruling c2's question, which #3670 answered with `applies_floor=levels_clamped(config)`. |
| `thermal_model.py` | all | none | Main keeps `project_planned_levels`, `_onto_band` and `project_space_against`, which the contributor deleted. The design keeps them for candidate 1 and the tank channel, and `optimizer.py` imports them. |
| `tests/features.py`, `tests/golden/claimed_drift.txt`, `tests/deployment_shape.py`, `tests/closures.json`, `tests/structure_budgets.json`, `docs/architecture.md` | all | none | The contributor's checks import their API (`_start_term_off`, `runs.commit_store`); main's groups landed their own. Their claim lines quote their whole build's figures, which the design restates rather than merges. Their budget re-record is of their tree. |
| `tests/mutation_ledger/killed_by/` | all | none | The contributor deleted 24 pins. A pin whose function survives on main is never deleted by hand (design note n2). Main's ledger is kept whole, with the conflicted rows included. |
| `dev/audit/rounds/round4/D6/claims.json`, `claims.md`, `claims.py` | all | none | `claims.json` and `claims.md` were regenerated with `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` on the merged tree (rc 0). They come out byte-identical to main's: `git diff` after the run printed nothing. |
| `docs/design/2026-11-12-honest-starts-and-runs/design.md` | the rest | `_settled_space` for `_settled`, twice | The note is a dated record of the contributor's build. Their head renamed the function the note names, and main carries the earlier copy. |

The contributor's `.claude/` and governance files were not touched by the pull request. Every other path is main's, by the merge.

## Head

- Code head: 5fc3e07bb23d7d8f60efb58441b15ae0e3c6626b on `handoff/r11-outside-honest-starts-runs-p3-p2`.
- Merge base and origin/main tip at measurement: 7c2f4c30cab5610cf8f5b040c326836ab544d27d. `git merge-tree --write-tree origin/main HEAD` reports no conflict.
- The #3529 merge head is 345d32d62de2677080b66c8035540c09e5d7d3d9.

prepr: passed rc=0 at 5fc3e07bb23d7d8f60efb58441b15ae0e3c6626b (`PREPR_SKIP_CLOSURES=1`; the last run also `PREPR_SKIP_CODE=1`, its delta since the code-checked run at the same head, whose one refusal was this body, text-only)

## Mutation proof

**Carry 5, the re-anchored entries.**
- Command: `PYTHONPATH=tests/hastub python3 tools/audit/seat/mutant_run.py --spec <the four re-anchored entries of dev/audit/harnesses/r11_honest_starts_runs_mutants.json> --cmd "env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'from types import SimpleNamespace as _DspNS' '# --- #3616: an implausible slab seed'"`, at the head.
- Result: `SURVIVED NULL`, `KILLED ENGAGED_COST_ARM`, `KILLED ENGAGED_CLAMP_ARM`, `KILLED UNPRICED_DESCENT`, `KILLED UNPRICED_DESCENT_COST_ARM`, rc 0. The NULL run (no edit) surviving is the driver's own control: a command that failed on the unedited tree would have ended the run at rc 3.

**Diff mutants (prepr step 6d).** None are drawn: the diff adds no `.py` line outside `tests/` and `dev/`.

## Null control

**Carries 2 and 4.** The control removes the cut: `duty_legs.lost_share` returns 0.0 (a detached worktree at 7c2f4c30ca, that one line changed).
- Command: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'from types import SimpleNamespace as _DspNS' '# --- #3616: an implausible slab seed'`.
- Unmodified tree: `ALL 163 FEATURES BLOCK PASSED`.
- With the cut removed: `19 of 163 FEATURES BLOCK FAILED`. The failures include `on the duty-cycle install the solved heating in every charged step is at most avail x p_max - dhw, and a charged step exists` (`[None]`) and `the co-optimisation reads the charged bound ...`.
- So the cut is live on main, and its checks detect its absence.

**Carry 5.** The enumerator printed `5` on the merge base's spec and `0` at the head.
- Command: `python3 -c "import json; d=json.load(open('dev/audit/harnesses/r11_honest_starts_runs_mutants.json')); print(sum(open(e['file']).read().count(e['old'])!=1 for e in d))"`.
- On the base the five were `ENGAGED_COST_ARM`, `ENGAGED_CLAMP_ARM`, `IDENTITY_GUARD`, `UNPRICED_DESCENT` and `UNPRICED_DESCENT_COST_ARM`, each with 0 occurrences.

**Carry 6.** The harness's own null rows (an empty pair) print `one plan across the arms True, descents per space solve [1]` for all three installs, and `null cells that moved or descended twice 0`, under every tree variant below.

## Figures

**Carry 6, measured.**
- Command: `PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py descents` (its arms: both descents, the operand's alone, the unpriced one alone).
- Trees: the merge base 7c2f4c30ca, and two variants of it in a detached worktree. Published objective per cell.
- Rule: a cell is "above" where both > min(operand, unpriced).

| tree | cells above | the cell(s) |
|---|---|---|
| merge base | 1 of 12 | modulating clamped, price phase 30, -4 degC: both 38.1123, operand 38.0075, unpriced 38.1123 |
| `_avoid_priced_switches` gate `switch_weight(...) > 0` removed | 1 of 12 | duty-cycle, price phase 30, -4 degC: both 37.4775, operand 37.4775, unpriced 37.2344 |
| the same gate widened to "or any relaxed plan of the solve held a priced switch" | 1 of 12 | the same duty-cycle cell, the same three figures |

**Why it reproduces.** Each stage call ships the lower of its relaxed plans, but the solve makes passes after the stage, so the end depends on which plan the stage picked.
- Spy on `_commit_runs`, one score per stage call: both 38.173, 38.1123; operand alone 38.3087, 38.1521, 38.0075.
- The operand arm's plan holds a priced switch, so `_avoid_priced_switches` runs its hot-water candidate, and that third pass reaches 38.0075.
- The both arm's plan holds none, so the gate skips the pass.

**Why no gate fixes it.** Both variants lower the shipped (both) objective on that cell to 37.994 and leave the other 11 equal to the base. But each moves the "above" cell to the duty-cycle cold day, where the unpriced arm alone now runs the pass from a different incumbent and ends lower.
- So "the solve ships no higher than either descent alone" is not held by construction by any single-path solve.
- Holding it means carrying each relaxed plan through `_co_optimize` and `_avoid_priced_switches` and shipping the lower final objective. That cost is not measured here; it is the decision routed under `## Forward-carry`.
- No production line is changed in this pull request.

**Scoped gate.** `python3 tests/closure.py select --diff 7c2f4c30cab5610cf8f5b040c326836ab544d27d --workdir <tmp>` at the head prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.` The one changed file is a harness spec, which no measured closure contains. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. The #3529 merge head selects the same way (`MODE: SCOPED -- 0 script(s) run`), with one changed file, the design note.

<!-- figure-block: scope-line mb=7c2f4c30cab5610cf8f5b040c326836ab544d27d head=5fc3e07bb23d7d8f60efb58441b15ae0e3c6626b -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

- Carry 6 (item 2d9b0f43): the solve's published objective can sit above one descent arm alone. Measured at 7c2f4c30ca in 1 of 12 harness cells; the two gate variants under `## Figures` each move it to another cell. The one fix that holds the property by construction carries each relaxed plan through `_co_optimize` and `_avoid_priced_switches` and ships the lower final objective, at roughly a second pass per priced-stop solve (not measured). The alternative is to accept per-stage-call lowest as the stage's contract. Decision: orchestrator, with that cost measured first; the gate widening, which lowers the one base cell to 37.994 and moves no other shipped plan, can ride with it. Lands in the round-11 roster on `handoff/audit-r10-roster`, beside `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-INTAKE-R10-RESIDUE
- Carry 3 (item 2e78177c): three live checks on a test fork (update-branch identity, `app_approve` end to end, class-O `commit_id`) need `gh`, an App key and a fork pull request. That is an orchestrator act; this cloud seat has none of the three. Lands in the round-11 roster on `handoff/audit-r10-roster`, beside `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-INTAKE-R10-RESIDUE
- Pull request 3529: the merge result is on `handoff/r11-outside-honest-starts-runs-p3-3529` at 345d32d62d, not on the contributor's fork. How it reaches #3529 is the orchestrator's decision. Lands in the round-11 roster on `handoff/audit-r10-roster`, beside `dev/programme/rosters/wave-r10-groups.json`. Carry: R11-INTAKE-R10-RESIDUE

## Friction

- finding-propagation.md: unclear: a dependency on a handed-off, unmerged predecessor (P2's mutants file) has no tree to land a carry in (roster carry 7, item be94cc35). It is a policy and instrument question for the round-end proposal triage, not this part. Carry: R11-INTAKE-R10-RESIDUE
