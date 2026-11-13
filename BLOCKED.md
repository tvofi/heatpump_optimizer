# R10-START-COUNTER-EDGES: blocked before code (fixer, origin/main e23124ff6e)

Question: part A's edge tracker is never attached on an install in pump-duty mode `off`, which is the default (`const.DEFAULT_PUMP_DUTY_MODE = "off"`). So which seat owns a running-signal listener that runs in every duty mode, and may it move out of `pump_arbiter._listen`, against design/R10-DUTY-SWITCH-RESTART-LEARNING abc575172c ("Owner of the listener: duty_switch.py ... The arbiter attaches it from `_listen`")?

## The facts behind the question (measured at e23124ff6e)

- `pump_arbiter.apply`: `if mode == DUTY_OFF: release_listeners(coord); return`. That runs before `_listen`, and so before `duty_switch.attach(duty_switch.record_for(coord), *_running_signal(inp))`. `release_listeners` calls `duty_switch.detach`. In `off`, `wear.EdgeTracker` is never fed and `duty_switch.note_pass` (the clock that confirms a final pending edge) never runs.
- `const.py`, the comment on `CONF_PUMP_DUTY_MODE`: "off (the default) writes and reads nothing". Attaching the listener in `off` breaks that sentence too.
- Today `_observe_compressor_start` runs from `_record_accuracy` on every install, whatever the duty mode, once per coordinator refresh (`update_interval = optimization_interval`, default `DEFAULT_OPTIMIZATION_INTERVAL = 30` min; per-install value not measured).
- If the counter "reads the edge tracker of part A" and "the sampled path is removed" (the brief), every default install stops counting compressor starts. Its stored lifetime and monthly counts freeze instead of continuing, and the brief requires them to continue.

## What a sound build needs, which an M with no design step does not settle

1. A listener owner that is independent of the duty mode, plus its own confirm clock: a frequency sensor that holds 40 Hz fires no later event to confirm the edge. One option is to attach `duty_switch`'s record from the coordinator's setup and confirm on each refresh. That departs from the architect note. `fixer.md` step 17: "a departure is raised, not made".
2. The immersion rule. `StartCounter.observe` freezes while `_immersion_active`, but part A's meter reader (`_running_signal`) has no immersion term, so the element cutting in reads as a start on meter-only installs. The fix is to read `None` while the element runs, which also changes what part A's learner sees (it voids an episode).
3. What counts as a start across `None`. The proposed rule: a confirmed `True` whose last non-`None` settled class was `False`, with that last class persisted as the stored `running` key. Under this rule `lifetime` and `months` continue across the change and are not reset.

## A premise in the brief to check

"moving it changes the counted starts that feed `_effective_cycling_cost`": `_effective_cycling_cost` reads `_wear_price()`, which is `wear_price_per_start(config replacement cost, config rated starts)`, and reads no count. The counted starts feed the ledger's `wear` line and `freeze_month_report(compressor_starts=...)`. The plan does not read them. The null control "the cycling cost and the plan are identical" therefore holds by construction, and only the counts, the wear ledger line and the receipts can move.

No code was written. Resume: fresh from origin/main once the owner question is answered.
