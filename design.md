# Design: R11-ARCH-fabric-learner (round 11, size L)

Architect note, extended (`dev/governance/roles/designer.md`). Plan of record
`plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75: `PLAN.md`,
`ADR-007-fabric-learning-out-of-the-cycle.md`, `COMPONENTS.md`, `prototypes.py`.
Base 9fe63d00b59f100aea67267ddddc95522e164aa1; code read at `origin/main`
8751943e17ef4d3ec699e7859ae829b4528d8ce7, whose `custom_components/` is the
base's (`git diff --stat 9fe63d00b5 8751943e17 -- custom_components` prints
nothing). The predecessor `R11-SEAM-learners` has no dispatch or handoff ref, so
there is no predecessor head. No production code on this ref; the spike at
63adc6a4a17fd829845905291d486ee59c48b3be (`spike/arm.py`,
`spike/fabric_learning.py`, this ref's first commit) never merges.

**Timing, pending owner confirmation.** `designer.md`: "Start when its last
predecessor dispatches, not when it merges." This seat started before that
dispatch, on `PLAN.md` open point 4 (2026-11-18, orchestrator under mandate).
Step 9's re-read at the predecessor's merge is therefore owed in full (§7).

## 1. Finding

None: a refactor group (ADR-007). No finder harness; the evidence is the
architecture score of the cut, read by the spike's arm (`## Figures`). ADR-007
names the acceptance harness of D2 s3 and D7 s2 (m3_learner_freeze); it is in
neither this tree nor `plan/r11`, so the fixer takes it from the round's export.

## 2. Owning seam

Learners (`COMPONENTS.md`: "parameters fitted from observed intervals"). Owner:
a new learners-seam module `fabric_learning.py`, pure, with no `homeassistant`
import; it reads `const.py` and `thermal_model.py` only, the direction
`COMPONENTS.md` allows ("learners read plant model and kernel").
`coordinator.py` only calls it and keeps every edge: the clock, the freeze
question, the baselines, the apply through `_publish_params`, the sample
counters, the store write. No concern needs two owners.

## 3. Shape

Five functions of values, named in the spike. Each takes no coordinator and
writes nothing it was handed.

| new function (spike) | takes | returns | leaves in the class |
|---|---|---|---|
| fold_buffer_cooling | rate, previous and current tank temperature, hours, bounds | (observed, new rate) or None at a gate | `_async_learn_buffer_cooling`: baseline advance, freeze, throttling valve, apply, counter, log, save |
| fold_internal_gains | profile or None, thermal parameters, interval start, residual, hours | the profile after the fold | `_fold_internal_gains`: the enable flag, `internal_gains_gate_open`, the sunlit gate, the assignment |
| heat_loss_anchors (and its total) | thermal parameters, config, earned basis, ratio | the four stored anchor keys | `_heat_loss_anchors` as one call; `_house_heat_loss_anchor` is deleted |
| reanchor_learned | (scale, samples, ratio, samples), stored nameplate pair, stored basis, live anchors | the four values re-expressed, or None below the gate | `_reanchor_house_heat_loss_scale`: basis restore, the zone-sensor void, the write-back, both applies |
| fold_house_heat_loss | scale, thermal parameters, residual, driving difference, hours | `learner_newton_step`'s pair | all of `_async_learn_house_heat_loss` but the step's two statements |

Moved with them, and imported back by `coordinator.py` under today's names so
no other reader changes: the six buffer constants, `HOUSE_LOSS_ALPHA`,
`HOUSE_LOSS_MAX_STEP`, `_LEARNER_TRUST_REGION`, `house_loss_confidence`,
`_house_loss_terms`, `_learned_zone_temperature`, `_zone_capacity`.

```
cycle -> _async_learn_buffer_cooling -> (clock, baseline, freeze) -> fold_buffer_cooling -> apply, save
cycle -> _close_fabric_interval -> _async_learn_house_heat_loss
           gates, await replay, residual, detector, solar fold
           -> _fold_internal_gains -> fold_internal_gains
           -> fold_house_heat_loss -> apply, counter, save
load | snapshot restore | earned basis -> _reanchor_house_heat_loss_scale
           restore basis, void -> reanchor_learned -> counters, applies
```

**Invariants.** Stored keys, versions and `store.DOMAINS` unchanged. Every
expression keeps its operands and order: the spike moves the lines, it does not
rewrite them. The freeze answer is asked by the coordinator before a fold is
called, wherever ADR-008 puts the predicate; a fold never sees a refused
interval. Applies stay conditional exactly as today: `_publish_params`
replaces the context on every call, so an apply added on an unchanged path is a
behaviour change. Two things do move and no finding names them; they move
because the code that decides them moves:
- the re-anchor's three log records are emitted by the new module's logger,
  text unchanged (they format the law's confidence and void, which the class no
  longer holds). `grep -rn -E 'cannot be expressed|Re-anchored learned' tests/*.py`
  returns comments only: no test reads them.
- the gains fold returns a new list where today it writes the held list in
  place (§7, fixer note).

**What the house fold does not give.** Its gates run across two awaits, feed
the open-window detector between them and end in `log_skip` or `note_freeze`
on coordinator state; its arithmetic already sits in `learner_newton_step`.
Only the step's operands move. `_close_fabric_interval` stays whole.

## 4. Alternatives (lost on the code)

- The baselines (`_last_buffer_temp_sample` and its two fellows,
  `_last_house_sample`, `_last_house_sample_time`) into a learners-seam object:
  three coordinator-side readers remain (`_async_learn_heat_span`'s
  `heat_energy.close_span` call, `_async_learn_interval`, the fold), so the
  object is handed back at each, and `tests/features.py` writes these
  attributes directly. Not measured; `coordinator_attrs` therefore does not
  fall in this cut, against ADR-007's Consequences.
- A learner object owning scale, ratio and counters, the coordinator reading
  through it: the store payload, the learning view, `_void_heat_loss_learners`
  and five `_apply_house_heat_loss_scale` call sites all change owner in one
  pull request, behind a predecessor that edits the same lines.
- The whole house fold as an object handed the replay and the detector as
  callables: the callables close over the coordinator, which `coord_footprint`
  charges ("every function handed it").
- Splitting the house fold's remaining gates into small functions: statements
  fall and no concept gains an owner (`fixer.md` step 17, last sentence).
- Re-anchor logs kept in the class: the function returns seven values so that
  three statements can format them.

## 5. Sibling sites

`grep -n -E '^    (async )?def (_async_learn_|_fold_|_reanchor_|_close_fabric)' custom_components/heatpump_optimizer/coordinator.py`
prints thirteen at the base. Covered: `_reanchor_house_heat_loss_scale`,
`_async_learn_buffer_cooling`, `_async_learn_house_heat_loss`,
`_fold_internal_gains`. Read and left whole: `_close_fabric_interval` (§3),
`_async_learn_interval` (orchestration). Out of scope, not among ADR-007's
thirteen methods: `_async_learn_lower_floor_loss`, `_fold_solar_aperture`,
`_fold_capacity_envelope`, `_fold_measured_cop`, `_fold_cop_evidence`,
`_async_learn_price_shape`, `_fold_score_sample`. The first two are fabric
folds of the same form and would take the same shape; `decision: orchestrator`
whether a later group takes them if the footprint needs more.

## 6. Evidence plan

- Failing tests first, `tests/features.py`, importing the new module's
  functions (an import that fails today): each buffer gate at its edge and both
  envelope directions; the gains fold from None, at a non-finite residual and
  on the clip; the anchors in one and two zones; the re-anchor below the gate,
  at a voiding basis (zero confidence) and on each reset; the house step equal
  to `learner_newton_step` on the fitted zone's terms.
- Unedited and still green: `tests/dst_checks.py`, `tests/rolling.py`,
  `tests/finite_boundary.py`, `tests/boost_drift_replay.py`, and the re-anchor
  and learner blocks of `tests/features.py`, but for its two
  `_house_heat_loss_anchor` readers.
- Harness: m3_learner_freeze at both ends, same values. Null control: with
  the envelope's upward alpha perturbed in the new module, it or the buffer
  test moves.
- Score: `spike/arm.py --at <merge base>` then `score.py --diff` on the branch.
  Null control: `--only module` (the module added, nothing cut) reads no
  footprint change and reads inadmissible, so the fall is the cuts'.
- Goldens: none move; `tests/golden/claimed_drift.txt` and
  `tests/golden/card_claimed_drift.txt` byte-identical. Off the canonical
  environment `tests/golden.py --only coord_` under `GOLDEN_MODE=strict` differs
  from the recordings at the base too; the check is that base and head print
  the same DIFF text in one environment.
- Mutation targets: each gate and the alpha choice in the buffer fold; ridge,
  clip and hour in the gains fold; the two-zone branch of the anchor; the void's
  zeroing and each reset's zeroing in the re-anchor; in the class, the None
  return after each fold and the counters' write-back.
- `tests/structure.py`: `max_class_loc` and `class_excess_loc` fall and are
  re-recorded downward; no budget rises.

## 7. Hot files, serial position, carries

`coordinator.py` (ninth of fourteen, `PLAN.md` "Hot-file order"),
`tests/structure_budgets.json`, `tests/structure.py`, `tests/features.py`; the
fixer waits on `R11-SEAM-learners`. `fabric_learning.py` is a new tracked file:
a measured closure (`tests/closure.py`) in the same pull request. No p1/p2
split: no pinned grader changes. Carry received: ADR-007 part 4, the measured
fall. Carry owed: the fall below, to the orchestrator's running budget.
**Revalidation (step 9):** at the predecessor's merge, re-run the arm at that
SHA. Its edits are exact-text and stop on a moved anchor; a stop, or a fall
other than `## Figures`', is a revision of this note.

### Notes for the fixer

- The gains fold returns a new list. Run `grep -n '_internal_gains_profile'
  custom_components/heatpump_optimizer/*.py` and confirm no holder keeps the
  old list across a fold; if one does, keep the in-place write. Carry: R11-ARCH-fabric-learner (item 6a1f0c21)
- `tests/features.py` reads `_house_heat_loss_anchor` twice (an alias and one
  call); point both at the module's function. Carry: R11-ARCH-fabric-learner (item 6a1f0c22)
- Each part alone reads `dead_members` and `duplication_copies` up, because the
  module then holds a function whose original is still in the class; only the
  whole cut is admissible, so it lands as one pull request. Carry: R11-ARCH-fabric-learner (item 6a1f0c23)
- The spike drops the moved functions' docstrings and comments; the fixer moves
  them with the code. Carry: R11-ARCH-fabric-learner (item 6a1f0c24)

## Figures

Enumerator, from the repository root, with `plan/r11`'s `prototypes.py`
exported beside the arm: `python3 spike/arm.py --at <sha> [--each --only <parts>]`.
Read 2026-11-18 on linux x86_64.

| tree | arm | `coord_footprint` | other metrics |
|---|---|---|---|
| base 9fe63d00b5 | whole cut | 2507 -> 2459, **F = 48** | none moves; admissible, dS +0.0279 |
| fork 92d38ecb64 | whole cut | 2496 -> 2448, 48 | none moves; dS +0.0280 |
| base | buffer / gains / anchors / reanchor / house, each alone | 16 / 12 / 3 / 15 / 2 | inadmissible alone (fixer note 3) |
| base | module only (null control) | no change | `dead_members` 1 -> 6, `duplication_copies` 18 -> 20 |

Buffer plus gains is 28, the plan's `--only fabric` reading; the re-anchor,
anchors and house step add 20. ADR-007 part 4 then reads `R <= 54`. The base
reads 2507 against the fork's 2496: `R` is 11 at 9fe63d00b5.

Behaviour of the spiked tree at the base, `PYTHONPATH=tests/hastub`:
`tests/rolling.py`, `tests/finite_boundary.py` and `tests/boost_drift_replay.py`
pass in both trees; `tests/dst_checks.py` fails the same eight checks in both;
`tests/golden.py --only coord_` prints the same DIFF text in both.
`tests/features.py` and `tests/entities.py` were not run on the spike.
