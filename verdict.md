Design review: revise 4da49f23d090013b4090201294b79822c2bcb3ef class-open

Reviewed design.md at 4da49f23d0 (detached worktree), code read at 31117b1029. Group credited: outside pull request 3529 by Bankaifan.

## Revise point

1. class-open: design.md "Sibling sites" and "Interfaces" stop at `SolveBand.as_dict`. The note's grep (`solve_band\(`) misses the readers of the published band, which lead to the user surface. At 31117b1029, `sensor.py:2093-2105` `_pump_max_power` copies only the keys `configured_max_kw, planned_max_kw, learned_max_kw, samples, since_s` into the Learning Model Status `pump_max_power` attribute. It also maps `source` and `reason` to top-level attributes that are translated enums (`strings.json:2158-2172` and `translations/{en,de,sv}.json:2158`, codes `configured` and `ceiling_probe`). So the three new `as_dict` keys never reach the entity, and a new floor source or reason code has no translation. The note's own stated limit depends on this surface: a follow-the-ask pump only comes down by reconfiguration, and "the published learned figure is how the user sees it". The note also misses `tests/entities.py:13064` (the ModelStatusSensor attribute pin), `payload.py:858` and `coordinator.py:7981` (the `pump_max_power` payload field now carries a floor under a name that means maximum), `coordinator.py:6450` and `optimizer.py:2419` (the stamp), and `docs/how-it-works.md:1208-1221`, which documents the learned top and these three attributes and says nothing of a learned minimum that moves the plan. Fix wanted: design the user surface. Name the attribute and its codes, the translation strings in all four files (their user text checked against the code, brief binding 4), the entities pin, and the docs paragraph. Or state why the floor is not published on the entity, and then rewrite the limit sentence.

## Decision routed (not a revise point)

- decision: orchestrator. design.md, preamble: "the notice included (not built)". Brief bindings 1 and 4 asked for a configured-against-metered notice through `issues.py`. Carry 1 voids the notice-only form, where the plan waits for the user. It does not plainly void a notice shipped beside the plan move. Whether C still raises one is scope. If it does not, revise point 1 becomes the only user channel.

## Convergence claim (carry 1): attacked and held, under its premise

- Raise then lower is impossible for a nondecreasing g. With the floored plan's E (evidence) asks at or above f, h(f) >= g(f), so after a raise h(f1) >= g(f1) >= g(1.15 f0) >= h(f0) = f1. Lower then raise is also impossible: a raise needs g(f1) > 1.15 g(f0) with f1 < f0. Every move is at least a factor of 1 + tol, and f stays between the configured figure and the top, so the number of moves is finite. The moved plan cannot erase its own evidence, because E is defined at f and there is no age lapse. The as-built cycle needs both the configured-floor admission and the 45-day lapse, and the design removes both.
- The premise is stronger than the note states. `pump_arbiter.py:702` `_band_kw` maps on the stamped `planned_min_kw`, so an ask at f writes the floor set-point whatever f is: g_f(f) = m, the pump's own least. f does not feed back into E's statistic, so a self-induced cycle needs g to depend on f in some other way.

## Notes for the fixer (carried observations)

- Test 1's fixture uses a stationary g = max(a, 1.1). Add an arm where the draw at the floor set-point follows the band (g_f(f) = m, the arbiter's mapping) and an arm with a step change in m (season, lift). Assert at most one move per step and no move back without a new step. Seasonal drift is tracking, not a loop, and the test should show it. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item r1)
- The since-count must stay aligned with `samples`. Three things break that: the deque's `maxlen` (`WINDOW`) evicting old samples, `from_dict` dropping unreadable rows (`draw_range.py:383-391`), and `observe`'s legacy-commands clear (`draw_range.py:303-307`). That last path clears the samples but, by the note, not F. Test each path. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item r2)
- The note's line numbers were read at ebe83a1b82, 42 commits behind 31117b1029. Re-measure them: `coordinator.py:2425` (`_solve_band`), `:2430` (`_band_fields`) and `:963` (power floor) at 31117b1029, against the note's 2424, 2429 and 962. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item r3)
- `store.DOMAINS`' `draw/overdraws` (`store.py:323`) is `_COUNT` without `whole=_DRAW_KEY`, so it is not the precedent for a config-keyed leaf. `draw/engaged` (`store.py:324`) is. F and its since-count go `whole=_DRAW_KEY`, as the note says. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item r4)

## Checked and clean

- Seam: one owner, `draw_range.py`. No second sample store, and the floor reads the one reader `_run_asked`, which takes keyword defaults so `power_floor_kw` and `ask_evidence` (`draw_range.py:491`) stay unchanged.
- Siblings in flight: R11-OUTSIDE-SELF-SETTING-PUMP reads `ask_evidence` and leaves `draw_range.py` unchanged. archive/design/R10-DRAW-MAP-EVIDENCE has nothing on main, and its map rows never reach `DrawRange.observe`.
- Finding direction: the configured 0.53 kW under a metered 1.1 kW agrees with a63a2ca6cd's c2 table.
- Size: `class_excess_loc` gives the DrawRange class (277 lines) room for the field and one call.

Token count: not reported by this harness.
