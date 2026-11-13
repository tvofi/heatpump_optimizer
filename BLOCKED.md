# R10-START-COUNTER-EDGES (part D of pull request 3420): blocked on a design departure

Question: Part A's edge tracker exists only while `pump_duty_mode` is not "off", and "off" is the default, so feeding the start counter from that tracker and deleting the sampled path stops start counting on every default install. May part D move ownership of the running-signal listener out of duty_switch.py into wear.py and attach it for every install, from the arbiter's `apply` before its DUTY_OFF return? The approved architect note (design/R10-DUTY-SWITCH-RESTART-LEARNING at abc575172c, "Owner of the listener: duty_switch.py") puts it elsewhere, and the meter source then needs an immersion gate that part A never built. fixer.md step 17 says a departure from the architect note is raised, not made, so this needs an orchestrator or owner ruling first.

Measured at origin/main 0cc5647545d27a7d49e6eb2d5c283238322177c0 (read from source; no code written):

1. **The tracker is attached only under duty observe or control.** `pump_arbiter.apply` runs `if mode == DUTY_OFF: release_listeners(coord); return` before `_listen(coord)`. `_listen` is the only caller of `duty_switch.attach`, so it is the only feeder of `wear.EdgeTracker` through `duty_switch.note_signal`. `release_listeners` calls `duty_switch.detach`, which resets the tracker. `const.py` has `DEFAULT_PUMP_DUTY_MODE = "off"`, documented as "off (the default) writes and reads nothing".
   - Today, `coordinator._observe_compressor_start` runs on every `_record_accuracy` cycle, whatever the duty mode.
   - The brief's build ("the counter reads the edge tracker of part A and the sampled path is removed, not kept beside it") would therefore read zero starts on a default install. That would freeze `lifetime` and the monthly counts, drop the wear ledger lines, and floor `_effective_cycling_cost` at the configured value under `wear_autotune_enabled`.
   - This breaks the brief's own null control: "counted starts identical before and after" on a trace with no short cycle.
2. **The tracker has no immersion gate.** `StartCounter.observe` freezes its state machine while `coordinator._immersion_active` is set, because on the meter source the draw is compressor plus resistive element. That is the #11 property in the `wear.py` module docstring.
   - `wear.compressor_running` and `EdgeTracker` take no immersion input.
   - `ArbiterInputs` and `duty_switch.SwitchContext` carry no immersion field; `grep -n -i immersion pump_arbiter.py` prints nothing.
   - So on a meter-sourced install the edge path would book an element switch-on as a compressor start.
3. **The stored `running` flag has no counterpart in the tracker.** `EdgeTracker.settled` starts at `None` on every attach. To keep stored counts continuous, and to avoid booking a start at boot when the pump is already running, the counter would have to keep its last definite class and take a start only on an edge to True whose previous definite class was False. That part is buildable within the brief and is noted only for the design.

## Options considered

- **(a) As briefed, counter fed only from part A's tracker.** Refused: point 1 regresses every default install.
- **(b) Keep the sampled path for duty-off installs.** Refused by the brief ("not kept beside it"), and it leaves two owners of one signal.
- **(c) Move the running-signal listener and tracker into a per-coordinator record in wear.py.** Attach it from `pump_arbiter.apply` ahead of the DUTY_OFF branch (the coordinator already calls `apply` every cycle, so `coordinator.py` gains no line). The counter and duty_switch's learner both consume its edges, and the meter source gates on immersion.
   - This needs immersion added to `ArbiterInputs`, and it re-cuts part A's listener seam, so it is a design departure.
   - This is my recommendation, pending the ruling.

No code, figures or mutation runs yet: the build waits on the ruling.
