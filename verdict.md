Design review: revise 0a6dfc18429bb36ef83a417c081778f1d05255f9 harness

Reviewed design/R11-OWNER-EXTHEAT-OVERRIDE design.md at 0a6dfc18429b (revision 2). I worked from a detached worktree of the note's base, origin/main 8ef450936a, and checked it against verdict 2a019ea9 (revise 1f9f94b2 architecture-unsound). I read every open design/* ref for overlap with the new hot files (boost.py, external_heat.py, payload.py, diagnostics.py, `_external_heat_view`). R11-OWNER-CARD-EXTERNAL-HEAT is the only one with a behavioural interaction (see the routed decisions); no sibling design claims this seam. R11-SEAM-cycle-solve and R11-OUTSIDE-ROOMS-P2 cite boost.py only as a pattern.

## Prior findings

- R1(a) resolved: alternative 4 (design.md:156-161) prices `obs.override=False`. Detection goes dark, the learners unfreeze, the entity's "yes" is overruled and the block lingers through `_decay`. Each reason checks against external_heat.py:438 `_deactivate` and :489 `suppressing`.
- R1(b) resolved: design.md:61-72 decides the entity-sourced precedence. Evidence test 3b pins it, and Q8 routes it to the owner.
- R1(c) resolved: every identifier now uses the `ignore_block` stem (design.md:20-27). The docs paragraph names both controls and sets them apart (design.md:219-224). The user-facing word "Override" is routed as Q9.
- R2 resolved: the toggle moves into the boost store. I checked the premise at base:
  - `restore_session` runs `restore` inside the `_RESTORES` gate (boost.py:630-664), and the first refresh awaits `session_restored` (coordinator.py:6136), so the restored toggle has no post-restart gap.
  - `_store_payload` (boost.py:546) already writes keys only when they are set, so the only-when-on key keeps the store of an install that never touches the switch unchanged.
  - No new HA name, stub or tracked file is needed.
- Prior carries switch-detection-attr, seam-learners-rebase and switch-count-pin are carried or answered (design.md:249-251). tests/entities.py:11769 still pins `len(switches) == 6`.

## Revise points

R1 (harness, shape): design.md:114 rewrites coordinator.py:6225 from the cached `self._external_heat_active` to the live `self._external_heat.blocking(...)`, which reads `suppressing`. design.md:118 then lists 5203, 3757 and 6844 as the unchanged "raw" sites, as if 6225 read the same thing before and after. It does not: existing harnesses drive the solve's burn through the cached attribute, and the rewrite makes that perturbation silent.
  - tests/features.py:73051 (the `_r9egb1_coord(learned=True)` arm) sets `coord._external_heat_active = True`. Check "#1736 the solve itself still plans with every per-solve value ... the burn" (tests/features.py:73147-73167) asserts `_r9egb1_st.external_heat_active is True`. The fixture's detector is quiet, so built as drawn this check goes red.
  - dev/audit/harnesses/solve_inputs_parity.py:157 (#1736's acceptance instrument) uses the same lever for its probe arm's "live burn". Its burn stops reaching the solve, so the probe arm silently loses one of its perturbations.
  - The note's own alternative 5 (design.md:162-164) cites these harnesses as the reason not to touch the cached attribute.

  Fix wanted, in the note:
  - At 6225, keep the cached value and apply only the switch: `external_heat_active=self._external_heat_active and not self._external_heat.ignore_effective(boost.extheat_block_ignored(self))`. 5218 already reads `.suppressing` live, so `blocking(...)` stays correct there.
  - Alternatively, name both harness ports in Hot files and in the evidence plan.
  - Add the 73160 check (switch off: still True) as a null control beside evidence test 3, and list the `ignore_effective` call at 6225 among the mutation targets.

## Routed decisions (not revise points)

- decision: orchestrator -- design/R11-OWNER-CARD-EXTERNAL-HEAT (design.md:41-50, 73) gives the card pill an `external_heat` state that outranks `heating`. It shows when the twin binary sensor is on, with the title "Planned heating is held back while they stay warm enough". With this switch on the sensor stays on (this note, design.md:68 and evidence test 6) but the plan is no longer held back, so the pill shows a false title and hides `heating`. The two designs claim no common seam. Whichever merges second has to reconcile them, for example with the card reading `suppressing_electric_dhw` or `external_heat.block_ignored` for the title. Ordering, and which brief carries it, is the orchestrator's call (finding-propagation.md).
- decision: owner -- Q1-Q9 as the note states them. I reviewed under the designer's defaults. Owner answers that would change this verdict, because each changes the shape:
  - Q6 "yes": the learning freeze sites 3757 and 6844 join the planning set, and the carry seam-learners-rebase reverses against design/R11-SEAM-learners.
  - Q3 "a timeout": the boolean `ignore_extheat_block` becomes a timed field in `BoostState.blocked`'s pattern, so the store key, `restore` and evidence test 7 change.
  Answers that would not change it:
  - Q8 "entity wins": one clause in `blocking`, as the note says.
  - Q7 "DHW only": the 5218 site is dropped.
  - Q2 "no persistence": the store key is dropped, and the toggle still belongs in boost.
  - Q1, Q4, Q5, Q9: defaults or naming only.

## Notes for the fixer

- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item r9egb1-burn-null) -- tests/features.py:73160 and dev/audit/harnesses/solve_inputs_parity.py:157 drive the solve's burn through `_external_heat_active`. Whatever form 6225 takes, both still see the burn with the switch off. Run the parity harness at base and at head, with every metric unchanged.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item woodfuel-view) -- wood_fuel.py:629 still gates the published wood-fuel forecast on raw `det.suppressing` while the switch drops the plan's free-heat credit. That is in the note's settlement residue, design.md:55. Pin it with a check that the wood-fuel view is unchanged by the switch, so the residue is measured, not only stated.
- Carry: R11-OWNER-EXTHEAT-OVERRIDE (item view-import) -- `ExternalHeatDetector.view` returns `payload.ExternalHeatView` (payload.py:933). external_heat.py already imports from `.payload` (external_heat.py:37), so extend that import and remove `ExternalHeatView` from coordinator.py:65 if nothing else there uses it.
