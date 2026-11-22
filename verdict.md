Design review: revise 79719c386a7143324cc6774950cb06f8b9265746 class-open

Read at origin/main 3a98735a7e, the base the note names. Seat token count: not reported by the harness.

Revise points (defects in the design):

1. Shape, owner ruling (tvofi, 2026-11-22, relayed by the orchestrator): "I want it as settings, default 10 min." N and M become config-flow options, default 10, capped at 15. design.md "N and M: defaults, not options" must be rewritten to that shape: the option rows, the EntryConfig read, the route to the arbiter (duty_switch.held_leg) and to the planner (an OptimizationConfig field next to duty_switch_off_seconds, reached through the existing `**duty_switch.planner_fields(self)` splat or the entry config), and the strings and translations. The note must also say what M > 10 does. In duty_legs.py R1 then leaves the step's heating share under SPLIT_MIN_MINUTES (15 - M < 5), so the rule must define the collapse to whole DHW and T3/T7 must cover M = 15. The note must also say whether 0 means off. (architecture-unsound until the shape is named)

2. Structure payment, config_flow.py (4200 lines, over MODULE_LOC_LIMIT 2000; module_excess_loc has zero headroom): the note now adds option rows to config_flow.py and names no payment for them. Name the move that pays those lines, judged by tools/audit/archscore/ before and after, or the budget-raise route with its `## Raise justification`. FLOWCAP (fa8cd134) names config_flow.py's over-limit cost too, so the two payments must not count the same move.

3. Sibling sites, user-facing text (class-open): docs/configuration.md lines 846-856 and the `pump_duty_mode` data_description in custom_components/heatpump_optimizer/strings.json (and translations en/sv/de) describe the both-step split exactly ("a share under 5 minutes goes to the other duty..."). R1, R2 and the execution latch make that text false, tests/doc_claims.py:5157 pins it, and the note lists none of these as hot files. Add them, with doc_claims rows for the new defaults. strings.json and translations are also FROST-HOLD's and FAULT-HOLD's hot files, so the serial order must be named for them too.

4. Root cause, other paths (class-open): "This is the only path found by reading _served and _share" is wrong. _planned_duty/step_duty runs on inp.plan at every pass, and step 0 of a re-solve is not pinned. So a re-solve that changes the current step's single duty (space to dhw near the step's end with the next step space, or both to dhw inside a heating leg) writes a new mode at once, outside both_step_duty. The owner's report shows heating legs shorter than SPLIT_MIN_MINUTES, which no plan both step can produce, so that path ran. The 1b latch turns those into held legs the plan did not price: a DHW leg of M minutes into a space step. The fix-2 decision-time skip must apply to every entry into a new duty, not only to a both step's first leg: do not enter a leg the plan leaves sooner than its minimum. Add a T1 sibling test for the single-duty re-solve path, with a null control.

5. Evidence plan, harness (harness):
   a. The synthetic run's null control (N = M = 0, latch off, "reproduces main's counts exactly") must also show main's legs_under_10 from re-solve causes as nonzero. Otherwise a generator whose re-solves fall on step boundaries passes vacuously. Put re-solves at off-boundary second offsets and require the null to read > 0.
   b. "The plan prices what is executed" holds only for the start profile. availability is read from the profile the solve starts from (optimizer._stop_availability, published unchanged as _space_avail), but R2 can remove a whole step's space heat from the shipped plan. The harness must report priced-minus-delivered space kWh on shipped plans (rule re-applied to the shipped arrays), and the null must read 0.
   c. "The tank side ... the harness counts it": the harness as specified reports h2d_per_hour and legs_under_10 only. Add the unpriced tank-side kWh, or drop the claim.
   d. T8 and T10 carry "—" though the plan says each test has a null control. T8: a step the rule does not touch gives None. T10: the same case without the exemption is held.

Decisions routed:
- decision: orchestrator -- serial order against R11-OWNER-FAULT-HOLD (6244553e, in review), which also runs after FROST-HOLD on pump_arbiter.py's _arbitrate/_lead_mode. The note names FLOWCAP and FROST-HOLD only.
- The owner's constants-versus-options decision is settled by the ruling in point 1.

Checked and sound:
- Fixpoint terminates. R1 and R2 only raise DHW minutes or turn legs into DHW, so each step changes at most twice, and the loop ends within 2n iterations (the note's "within the plan's step count" is slightly low). See the carry for a hard cap.
- Overlap with FLOWCAP fa8cd134: no shared seam beyond the pump_arbiter/config_flow arithmetic.
- Overlap with FROST-HOLD e91a4e30: frost sets served = "space" in _arbitrate and _lead_mode after _served, so frost wins by construction.
- STEP-KICK 6deece87 runs after this group.

Notes for the fixer:
- Frost need not sit in held_leg's exempt; it overrides _served downstream. Pin "frost wins with a young DHW leg latched" once both have landed. Carry: R11-OWNER-MODE-LEGS (item frost-exempt)
- One owner for mode-leg history. rec.leg duplicates arbiter state (held.written["mode"], held.dhw_since), and STEP-KICK's swap_at asks to reuse whichever lands first. Shape rec.leg so STEP-KICK reads it. Carry: R11-OWNER-MODE-LEGS (item leg-history-owner)
- The fixpoint runs inside switch_weights_batch, on the objective's batch path. Prefer a run-length formulation or hard-cap the iterations, and time the [B, n] call before and after (D9). Carry: R11-OWNER-MODE-LEGS (item batch-cost)
- switch_ban reads rule[0] directly, not through leg_ends, so the sibling list's "all read the rule through leg_ends" is inexact. With a NamedTuple, rule[0] still works. tests/features.py:88483 builds a rule as a plain 2-tuple, so it needs the NamedTuple. Carry: R11-OWNER-MODE-LEGS (item legrule-tuple)
- Lease interplay: the note's own carry stands. Carry: R11-OWNER-MODE-LEGS (lease)
