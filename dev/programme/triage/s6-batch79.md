# Proposal triage, session s8, batch 79 (P316)

The rolling batch (V182) after batch 78 (handoff `triage-s8-batch78`). Facts were read at
origin/main `5d4e0bcfb`, on the roster branch, and in the R10-HOTFIX-LEARNER-INPUTS body at
`handoff-body/r10-hotfix-learner-inputs` `746894afe`.

## P316: an estimated power entity earns the `metered` heat-loss basis

Verdict: DEFER. The benefit is unpriced: the report itself says the overstatement "could NOT be
measured". The proposal is a design (a config option, a new basis tier, a migration, translations
and docs) with no number on the other side. Under the contract an unmeasured benefit is DEFER, never
ACCEPT.
- What prices it is a measure-first probe, defined below. It is a read-only measurement, not an
  implementation, and the orchestrator can dispatch it now without a roster group.
- If the probe prices it as material, the design goes to a new group on the learner/basis seam,
  reviewed under `designer.md`.
- **No existing group fits.** R10-ADVISOR-WHATIF is done. R10-HOTFIX-LEARNER-INPUTS (`in-progress`,
  M) owns `thermal_model.py` now, but it is a hotfix, and its own body dismissed this item as
  out of its scope.

Source: the orchestrator s8's message of 2026-10-31, routing the R10-HOTFIX-LEARNER-INPUTS fixer's
dismissed Forward-carry item 2.

Instances:
- **The rule, read at main.** `thermal_model.heat_loss_basis` (`thermal_model.py:1481`) returns
  the `metered` basis exactly when `probe_install` sets `measured_power=bool(cfg.get(const.CONF_POWER_ENTITY))`
  (line 1342). Any configured power entity counts as a meter.
- **The indistinguishability, measured by the fixer.** In the body's Figures, the `basis` arms
  give `basis: power = a revenue meter -> metered` and `basis: power = the pump's own estimate ->
  metered` on both sides. Home Assistant exposes value, unit, device_class and state_class, so no
  attribute separates the two.
- **One known install affected:** tvofi's, where the pump's own estimate feeds the learners as if
  metered (the orchestrator's account).
- **The remedy that exists.** The same PR adds the owner's heat-loss reset action, the remedy once
  a real meter is fitted (body, Forward-carry item 2).

Cost, if built now:
- M. An owner-declared option (`CONF_POWER_IS_ESTIMATE` or similar) in the config and options
  flows, with translations and docs (`docs/configuration.md`).
- A fourth basis, or a down-weight on `metered`, in `HEAT_LOSS_BASES`, plus a void rule for
  changing the declaration (`heat_loss_basis_voids`) and the learners' replay weighting.
- Tests: `features.py` rows and the flat-price null control. A design step under `designer.md`
  first, since it changes what the learners trust.

What would change the answer: a measure-first probe, dispatched as a read-only seat with a committed
harness, that prices the error.
- **(a) Sensitivity, measurable now without a meter.** Replay a stored recording through the
  heat-loss learners with the power stream scaled by 0.8, 0.9, 1.1 and 1.2. Report:
  - the learned heat-loss coefficients against the unscaled run;
  - the plan's cost delta on the same horizon, with a flat-price null control (the delta must
    vanish there);
  - the threshold error at which the cost delta exceeds the solver's own run-to-run noise.
- **(b) Field, owner-only.** The pump's estimate against a revenue meter over at least 7 days on
  one install, giving the real estimate error.
- **Decision rule.** If (a)'s cost delta at (b)'s error, or at (a)'s threshold when (b) is absent,
  is material against D0's cost noise, ACCEPT the design as a new group. If not, REJECT, and
  record that the reset action is the remedy.

Binding: an M design touching config UX, the learners' trust model and a migration, against a
benefit nobody has priced. The probe's cost (one read-only seat, a harness, about 2 seat-hours) is
small, and it decides the question. Building first would be the unpriced trade the contract
refuses.
