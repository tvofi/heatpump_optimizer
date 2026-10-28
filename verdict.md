Design review: approve e6797ca9d94ea12be59aef0a10da52ead1c3073b

Reviewed: `dev/programme/designs/R10-UX-HEALTH.md` at `design/R10-UX-HEALTH` e6797ca9d, round 2 of 3. It fast-forwards round 1's 3f6990ecb. I read it from a detached worktree at that SHA, and the ref has not moved. Code was read at origin/main f844df1fe and at R10-COP-GATE part 1's handoff d3ce1d33f. Token count: not reported by this harness.

Under the orchestrator's rulings, I judge how arm E consumes the COP keys, not what they are named. Part 2 copies part 1's learning-view names into `ModelStatusSensor.cop`, and that copy is queued to part 2's brief. `translations/sv.json` is in `files` by the ruling under mandate 6329234399.

## Round-1 points

A. **Closed.**
- **One reader.** Arm E's `copState(cop)` reads only `ModelStatusSensor`'s `cop` attribute. It takes the five-state `cop_observability` verbatim, with no boolean, plus `cop_refusal` and `measured_cop_at`. Those are part 1's names in `LearningView` at d3ce1d33f.
- **Precedence.** The order is alarm, then `not_measurable`/`no_electric_meter`, then Normal only when watched, then a dash and a reason. `not_measurable`/`no_electric_meter` comes ahead of "Normal" even when `watched_buckets > 0`.
- **Latch age.** It is rendered from `measured_cop_at`.
- **Before part 2 merges.** The three keys are absent, so step 2 cannot fire, and the row is never "Normal" unwatched.
- **Tests.**
  - Failing tests cover `not_measurable` and `no_electric_meter` with `watched_buckets: 3`, `span_open` unwatched, and the age.
  - The null control is `heat_metered` with `span_open` and `watched_buckets: 3`, which still reads "Normal" (carry 11).
- **Mutation proof.** Moving step 2 below step 3 is named as a mutant.
- **Ownership.** `sensor.py` stays out of `files`, and the copy is part 2's.

B. **Closed.**
- **One function.** The learning row (`HEALTH_WAITING` / `healthLearningHtml`) renders the same `copState(cop).reason`, and `health.learn_cop_why` is deleted in en and sv.
- **Sibling enumeration.** The note adds a sibling-site command. I re-ran it at e6797ca9d: `grep -cE "learn_cop|model_cop|_learning_observed_cop"` on the card prints 20, as stated.
- **Failing test.** It asserts the `not_measurable` string and no "Needs a power meter".

C. **Closed.** I re-measured with my own walk over `options` and `config` in strings.json and sv.json:
- **Multi-page fields.** 7 fields appear on more than one options page: dhw, outdoor, supply, return, capacity_limited and the wood pair.
- **Divergent labels.** Only `wood_tank_top_entity` and `wood_tank_bottom_entity` differ, and only in sv. They differ between `building/sections/wood` and both `quick_setup` copies (options and config), exactly as the note states.
- **Strip rule.** The per-language strip leaves no " (optional)", " (valfri)" or " (valfritt)" marker on any label.
- **Owning page.** The device page, `building/sections/wood`, wins over the shortcut pages.
- **One-label test.** The equality arm fails a field that carries a second label, by name, and is red on today's sv.json.

D. **Closed.**
- **Read level.** The card reads `res.response.debug[entry_id]`, which matches `handle_debug_collect` (services.py:1217-1223) under HA's `{context, response}` wrapper.
- **Failing test.** The stub resolves to that full shape, with the fields of `debugger._IDLE`/`status()`.
- **Null controls.** Three wrong-level stubs must render "off": a flat status, a `debug` map without its `response` wrapper, and a status keyed by another entry. The read level is a named mutant.

**Carried fixer notes.** All three are present in the note's grammar: heat-loss-clause (with the harness arm to separate the two readings), enum-strings and archscore-base.

## Notes for the fixer

- Carry: R10-UX-HEALTH (item enum-count). The enum-strings arm's grep prints 21 codes at d3ce1d33f: 4 observability constants, 13 `COP_REFUSED_*` and 4 `SPAN_REFUSED_*`. At f844df1fe the four observability constants do not exist yet, so run the arm only at a merge base that contains part 1. Assert the count is non-zero, so that a grep miss cannot pass as "every code has a string".
