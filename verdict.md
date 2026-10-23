Design review: approve f589cc0c3e162784e5c43343e709eab3c3a3b5fc

Reviewed: `git diff a858dfda0 f589cc0c3 -- dev/programme/designs/R10-LIVESTATE.md` (a fast-forward, the note only), round 3 of 3, against code at fd7e289d0. Round-2 point 1 is closed. Settled points are not reopened. Token count: not reported by this harness.

## Round-2 point 1: verified by reading

- **pump_arbiter "No" holds.**
  - Every store into `held.written` is reached only from `_arbitrate`, which `apply` runs under `held.lock` right after `await _load(coord)` (pump_arbiter.py:1049-1054):
    - `hold` (pump_arbiter.py:889), called at :1077;
    - `_forget` (:912), called at :1064;
    - `_write` (:954), called from `_command` :960 and `_write_night_schedule` :998;
    - the pop at :982.
  - `release` (:1145) is the only path outside the lock. It calls `_command` only when `held.written` is non-empty (:1150), and before `_load` lands only `_load` itself (:1221) can fill it.
  - The arbiter's only callers in the package are `coordinator.py:7573` (`apply`) and `coordinator.py:6231` (`release`), by `git grep`.
- **Notifier and debugger "No" hold.**
  - The notifier awaits its load at notifier.py:322 before `async_add_listener(_on_update)`.
  - The debugger awaits its load at debugger.py:662 before `_COLLECTORS[coordinator]` and its listener exist.
- **The `restore_snapshot` claim holds.** `async_restore_learned_snapshot` (coordinator.py:9566) reaches `self._apply_learner_payloads(...)` (:9575) with no await before it. That call writes the thermal learned rates (:9389-9392), `_dhw_learner.apply_payload` (DHW profile), `apply_draws` (DHW draws) and `_price_learner.adopt_model` (price model): four loads, as stated. It is a user command, so routing it to R10-PARAMS-OWNER with the other two is consistent.
- **Routing.**
  - ls-r1 (3 user-command writers, 4 loads) goes to R10-PARAMS-OWNER, a live group after this one, and ls-r1-probe gives a recipe with a null.
  - ls-r2 (7 per-cycle sites) is stated as unprobed leads, not findings, filed by the fixer's PR as `Part of` #2248.
  - Both satisfy finding-propagation.md and CLAUDE.md's filing rule.
- **The residual window's reason** (runtime_data assigned after the first refresh; store.py:686 registers the read future synchronously) is now in the note.
- **drev-06 and drev-07** are in the note's fixer notes.
- **The page cap** is waived by the orchestrator, as recorded in the note.

## Constraint on the orchestrator (not a revise point)

ls-r1 and ls-r1-probe name R10-PARAMS-OWNER. By finding-propagation.md they must be in that group's roster `brief` (or `carry`) before this group's pull request merges. The designer edits no roster. The same applies to ls-03 (R10-HEAT-METER) and ls-04 (R10-PARAMS-OWNER) from round 1. decision: orchestrator
