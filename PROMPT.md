CLOUD DESIGNER seat for tvofi/heatpump_optimizer, topic R10-ADVISOR-WHATIF, at head 2a3c05644d85b7ee5c2c314fde5aca950e4aba91. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/designer.md from main, and follow it exactly. The base is 2a3c05644d85b7ee5c2c314fde5aca950e4aba91 (`git fetch origin 2a3c05644d85b7ee5c2c314fde5aca950e4aba91`); name it in the note. Write no production code.
Output: write the note as design.md in a directory of your own and run `bash tools/audit/seat/bus.sh push-design R10-ADVISOR-WHATIF <design.md>`, which pushes refs/heads/design/R10-ADVISOR-WHATIF; that push is the return signal, and the design/R10-ADVISOR-WHATIF tip is the SHA you hand off. You may push only to that ref. Open no pull request, push no handoff ref and write no delivery row.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
CLOUD DESIGNER (opus), group R10-ADVISOR-WHATIF, topic R10-ADVISOR-WHATIF, per dev/governance/roles/designer.md; REVISION round 3 of 3 (two design reviews returned revise; a third revise sends the designer to a re-cut, so answer every point). Size L, carry #2257. Time box 1 h. Note: design/R10-ADVISOR-WHATIF tip b50afa68668edc69c0b1863ca52ab364ecb8336e (`git fetch origin refs/heads/design/R10-ADVISOR-WHATIF`). The design reviewer's verdict at that tip follows verbatim (design-verdict/R10-ADVISOR-WHATIF verdict.md). Revise the note on design/R10-ADVISOR-WHATIF in place (re-base its citations on current origin/main; push the new tip there via bus.sh push-design), keeping what the reviewer confirmed (round-1 points answered, seam, sibling sites, consistency, cost). Answer the one revise point (extract one helper both the start settlement and the held_start branch call, state the steady plan's buffer behind a throttling valve and the _initial_buffer_temp re-stash, add the valve-plus-two-tanks check and the _sharing_wood_side mutant, re-cite line numbers at origin/main) and fold the five fixer carries into the note's evidence plan.

--- VERDICT (verbatim) ---
Design review: revise b50afa68668edc69c0b1863ca52ab364ecb8336e architecture-unsound

Round 2 of 3. The note's base c3a279e32 is 126 first-parent merges behind origin/main 73365699a. Steps 1-6 were checked at both trees. Both of round 1's points are answered at the base. The re-cut's held-start rebind becomes unsound at main, because a9f8cb2b5 (R10-HOTFIX-SAV-ESTIMATE) is on main and not on the base. That is the only revise point.

## Revise point
1. design.md §1 (held_start rebind), architecture-unsound. At main, `_thermostat_held_state` also sets `buffer_tank_temperature` to `valve_hold_temperature(...)` and `wood_tank_temperature` to `_NO_WOOD_TANK_C` (0.0) whenever the mixing valve throttles (optimizer.py:558-602 at origin/main). The start settlement's held state is therefore no longer the bare call the note quotes. It is `_sharing_wood_side(_thermostat_held_state(...), initial_state)` (optimizer.py:5634-5637). The note says the rebind is "the same expression" and that "the tanks stay as measured". Both are false at main. Implemented as written, a valve install with two tanks starts the steady plan with the wood tank at 0 °C, which deletes the stored wood heat that "wood on both" relies on. A valve install with a buffer store starts from the valve-hold buffer. Meanwhile `_initial_buffer_temp`, stashed earlier from the measured buffer (`_stash_price_horizon`, optimizer.py:3620, read 3955-3999), floors the buffer settlement cap (5314-5317) from a different start than the solve's.
   Fix wanted:
   - Extract one helper in optimizer.py that both the start settlement and the held_start branch call: the reference-held start `_sharing_wood_side(_thermostat_held_state(model, state, weather, _baseline_target(comfort_targets, 0, target_temp)), state)`. One expression, so the two cannot drift.
   - State what the steady plan's buffer is behind a throttling valve. Held, which is what keeps the start gap zero, is the expected answer; if so, re-stash `_initial_buffer_temp` from the rebound state, or build the comfort bounds before the stash, and say which.
   - In §5, the start-settlement-zero check also runs on a fixture with a throttling valve and two tanks, and asserts that the wood tank is unchanged from the measured state. Add a mutant that drops `_sharing_wood_side` from the rebind and must turn that check red.
   - Re-cite §1's line numbers at origin/main.

## Round-1 points
- Point 1 (one derivation of the step-0 target): answered. The target is `_baseline_target(comfort_targets, 0, ...)`, taken from `_build_comfort_bounds` inside `optimize`. No caller derives it, and the §5 offset mutant is present. Idempotence holds at main too (the zones and slab come from the target and weather step 0, and the valve hold reads only those). Revise point 1 above concerns only the tank fields.
- Point 2 (no feedback, fallback streak): answered. The steady side uses a fresh scratch `HeatPumpOptimizer(ThermalModel(deepcopy(params)), deepcopy(config))`. `_optimization_result` is written only at coordinator.py:3750/6496 at main (3452/6197 at the base), with no new writer. `_warm_seeded` reads only it. `_await_off_loop` (2132-2156 at main) never touches `_WORKER_FALLBACK_STREAK`, which only `_await_optimize` bumps (2328-2330). That argument is sound, and so is "past the cap no steady solve runs", because the shadow solve's `UpdateFailed` is caught at 11408-11410 at main.

## Checked, no revise
- Seam (step 1): at main, SolveInputs (2351-2359), async_simulate (11239-11423) and price_tiles.py are unchanged from the base, apart from line numbers.
- Sibling sites (step 3): the four `async_simulate(` callers at main are coordinator.py:9048 and 10777, debugger.py:323 and services.py:767. There is no new caller and no new reader of a monthly key.
- Consistency (step 5): of the open design/* refs, only R10-USER-DOCS-FINAL names docs/dashboard-card.md, as an index of sections, and only r10-livestate (P6 tile cursor) names price_tiles.py. Neither claims this seam. No other ref names SolveInputs.held_start, async_simulate or `_thermostat_held_state`.
- Cost (step 6): unchanged from round 1; fits L.

## Notes for the fixer (carries, not revise points)
Carry: R10-ADVISOR-WHATIF (item 2257-record-optimizer) - `SolveRecord.optimizer()` builds a fresh instance on every call (coordinator.py:2386-2387 at main), so "the record's optimizer has no new write" is vacuous. Assert instead on the instance actually passed to the live steady solve: wrap `_await_off_loop`, capture the optimizer argument, and check it `is not` any instance a SolveRecord or `_warm_seeded` returned.
Carry: R10-ADVISOR-WHATIF (item 2257-fuse-key) - the fuse advisor reads `simulated.get("monthly_settled_cost_delta")` directly (coordinator.py:9080 at main), not through `price_tiles.monthly_figure`. Re-point that line to the steady key itself; changing monthly_figure alone does not move it.
Carry: R10-ADVISOR-WHATIF (item 2257-tile-callsite) - all three price tiles share one async_simulate call (coordinator.py:10777 at main), so pass `steady` per spec (`"power_cap_kw" in overrides`), never for the whole rotation.
Carry: R10-ADVISOR-WHATIF (item 2257-cache-copy) - main stores `replace(result, solve_band=...)` (6496), a copy. Key the steady cache on the object `self._optimization_result` holds when read inside async_simulate, never on a solve's own return value.
Carry: R10-ADVISOR-WHATIF (item 2257-timeout) - at main, `_await_off_loop` re-raises `ProcessWorkerTimeout` with no executor rerun (2147-2149). The steady pair's own except must catch it and drop the steady key; pin that with a test.

Seat tokens: verification subagent 110266; the review seat's own count was not reported by the harness.


Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.


GitHub API discipline (owner order 2026-11-08): the core REST bucket is shared by every seat. Read refs, heads, verdicts and handoffs with git (ls-remote, fetch), never REST. Any poll or wait loop is at least 240 s apart. Read each check run, comment or PR state once per step, never in a tight retry. Before a batch of more than 20 calls run `gh api rate_limit -q .resources.core`; on a 403 or under 500 remaining, stop calling until its reset and say so in your handoff.
