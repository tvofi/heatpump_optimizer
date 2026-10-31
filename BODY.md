Triage batch 79 rules the orchestrator s8's proposal of 2026-10-31. The heat-loss basis reads `metered` whenever a power entity is configured, so a heat pump's own power estimate feeds the learners as if it were a revenue meter. It routes the R10-HOTFIX-LEARNER-INPUTS fixer's dismissed Forward-carry item 2. It is the next rolling batch under V182, after batch 78. It holds one ruling and no roster op.

- **P316: DEFER.**
  - The benefit is unpriced: the fixer's report says the overstatement could not be measured. The proposal is an M design (an owner-declared option, a basis tier, a migration, translations, docs).
  - No existing group fits. R10-ADVISOR-WHATIF is done, and R10-HOTFIX-LEARNER-INPUTS dismissed the item as outside its hotfix scope.
  - What would change the answer is a measure-first, read-only probe.
    - (a) Replay a recording through the heat-loss learners with the power stream scaled by 0.8 to 1.2. Report the learned coefficients and the plan-cost delta, with a flat-price null control and the threshold error at which the delta exceeds solver noise.
    - (b) Owner-only: the estimate against a revenue meter over 7 days or more.
  - Decision rule: material against D0's cost noise means ACCEPT the design as a new group under `designer.md`; otherwise REJECT, and the reset action this hotfix adds stays the remedy.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`c4c202719bc39581c6ae5ab6e1eb25303c92f1f5`; the file is the whole diff against `5d4e0bcfb`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P316 as `DEFER`. A carry citing `triage: dev/programme/triage/s6-batch79.md#P316` is refused: `dev/programme/triage/s6-batch79.md#P316 is not an ACCEPT ruling (DEFER)`. No roster op cites it.

## Null control

- With the file absent, a citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `git show origin/main:custom_components/heatpump_optimizer/thermal_model.py` at `5d4e0bcfb`: `def heat_loss_basis` at line 1481, and `measured_power=bool(cfg.get(const.CONF_POWER_ENTITY))` at line 1342.
- `git show 746894afe:BODY.md` (`handoff-body/r10-hotfix-learner-inputs`), Figures: `basis: power = a revenue meter -> metered` and `basis: power = the pump's own estimate -> metered` on both sides.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
