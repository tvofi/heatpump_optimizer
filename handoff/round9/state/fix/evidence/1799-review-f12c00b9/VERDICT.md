blocked 2e6e590a ratchet-evasion: coordinator.currency is a method written as property(lambda) that coordinator_methods (224 of 224) does not count

Round 2 of review for #1799 (R9-F1.8). Code head measured: f12c00b9 on merge base 59c2543b (branch handoff/r9-f1-coordinator-8-epilc5, transport cb79c3dc). PR head 2e6e590a is f12c00b9 plus its delivery row (docs/delivery/1799.md only). CI was still running at 2e6e590a; the block turns on the code, not on CI, so none is cited.

## Resolved since round 1 (code head 87bf02de)
- B1 fixed: identity_update(hass, entry, ...) returns {} when async_entry_for_domain_unique_id finds another entry, as async_step_reconfigure aborts there. All four writers pass hass. Pinned in tests/entities.py ("an identity edit whose id another entry holds leaves the id alone; a free id is still written (#1799 B1)"), with a free-id arm as its null control. I have not run the fixer's guard-removed mutant; CI's entities.py run at the head is the citation owed.
- The optional point is fixed: declared_currency uses [A-Z]{3}, so "ÖRE/kWh" declares nothing (pinned in features.py).

## Blocking: the raise was removed by moving a method where the methods ratchet cannot see it
- The new `currency = property(lambda self: getattr(self, "_feed_code", None) or (_feed_currency(self.hass, self._config) or resolve_currency(self.hass)))` is a method in all but syntax. tests/structure.py counts coordinator_methods as ast.FunctionDef/AsyncFunctionDef, so a lambda property is invisible to it; a `@property def` would make it 225 against a budget of 224. Nothing on main's coordinator.py uses `property(lambda`; the only class-level descriptors are the existing `_hub(...)` factory entries.
- `_feed_code` is not initialised in __init__, and is read through `getattr(..., None)` for that reason. That is the second assignment the multiassigned metric would have counted, removed by hiding the attribute's absence rather than restructuring.
- structure_f12c00b9.txt: coordinator_methods 224 <= 224, coordinator_loc 9022 <= 9022, coordinator_multiassigned_attrs 116 <= 116. Every cap holds; the growth is real and unmeasured.
- tvofi's standing rule (2026-09-30T21:33Z): a fixer restructures by splitting or extracting, and a raise is for when a sound design cannot fit. Neither is this: nothing was split or extracted, and the one method the design needs was written in a form no ratchet reads.

## What would pass
Either of these; (a) is my recommendation.
- (a) Restore 87bf02de's currency design: a plain `self.currency` written in __init__ and adopted in _update_current_state, with coordinator_multiassigned_attrs 116 -> 117. Round 1 judged that raise the architecturally right call: currency is state with an initial value and a per-cycle update, and every extraction that avoids it needs a coordinator method (coordinator_methods at zero headroom) or rewrites 13 read sites in sensor.py. The raise's reason goes in the commit message and the PR body, as the mandate requires. Keep B1's guard and the [A-Z]{3} fix.
- (b) Keep the derived property as a real `@property def currency`, initialise `_feed_code = None` in __init__ only if the multiassigned count stays at 116, and raise coordinator_methods 224 -> 225, with the same stated reason.

## Unchanged from round 1
- The out-of-plan sensor.py borrow is accepted: 12 lines in HeatPumpOptimizerSensorBase, the only place a sensor built before the feed's state can follow it, flagged in the body.
- merge-tree of 87bf02de against main conflicted only in tests/deployment_shape.py, which the main merge 83aec1db resolves.
