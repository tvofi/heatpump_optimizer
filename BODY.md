R11-SEAM-cycle-solve, part 2 (the roster's open carries after #3738 merged): the four timed duty switches (Boost DHW, Boost Space, Block DHW, Block Space) no longer buy a solve. Before, the press requested a refresh through `entity.publish_then_refresh`, and that refresh re-solved inputs the toggle had not changed. Boost and block state is no solve input; the overlay is laid on the plan base after the solve (`boost.apply` in the cycle's write tail). The press now hands the entry's background task `HeatPumpOptimizerCoordinator.async_apply_held`. That method lays the overlay on the plan base the last cycle adopted, actuates (action, frequency, pumps), and publishes the cycle's payload, with no fetch and no solve. `solve_gate.overlay_only` sends it to the ordinary request (`async_request_refresh`, which trails a refresh in flight and re-runs a solve in flight) whenever there is no plan base, a refresh or solve is in flight, or the entry is released. Closes: none (the group's issues were dispositioned at #3738's merge; this part has no issue of its own).

Shape:

- `_actuate_plan` is the cycle's write tail, moved out of `_async_update_data` unchanged in order: overlay, `_apply_action`, frequency (T7 #61, after the action), pumps. The cycle and the toggle both call it.
- `_publish_uncycled(coord, data=None)` is the one publish outside a cycle. It is shared with `async_diagnose_interval` (D9-s1-01), because `async_set_updated_data` re-arms the interval and cancels the debouncer's pending call.
- `boost.plan_base` is the plan-base accessor.
- `_async_update_data` and `_actuate_plan` read the context through the typed `_ctx_of`, not `getattr(self, "_ctx", self)`.

Alternatives, and why each lost:

- (a) A one-shot "skip the solve" flag on the gate, consumed by the next refresh. A scheduled refresh, `async_optimize_now`'s direct refresh, or a debounced call merged with another writer's request would each consume it and skip a solve those triggers owe. Every other trigger would need to clear it.
- (b) A direct `async_refresh()` minus the solve. Home Assistant's `_async_refresh` cancels the debouncer's pending call, so a writer's queued request would be dropped unsolved.
- (c) A solve memo keyed on the inputs' fingerprint. That changes every trigger's cost model, not just this seam's. The probe's measured jitter between two identical solves (6.04e-4, `probe.py`'s `TOL` note) means a memo would also change the plan the cadence publishes.
- The taken path changes only the four switches. It reuses the existing write tail, the existing in-flight guard (`_refresh_task`, `gate.solving`) and the existing request path for every case it does not own.

Design choice a reviewer may read as a gap: the toggle actuates on the readings the last cycle took (`_update_current_state` is not re-run). That is the same state the held plan was actuated on at that cycle's end, and the next scheduled cycle re-reads it. Re-running the read would feed the learners a second time inside one interval.

Previous seat's BLOCKED.md (the dispatch's reconciliation line): none exists on this group. `git log --format='%h %s' origin/<ref> -- BLOCKED.md` printed nothing for `handoff-wip/r11-seam-cycle-solve`, `handoff/r11-seam-cycle-solve`, `handoff-wip/r11-seam-cycle-solve-local-20261121`, `wip-sync/ext-upd-fix-r11-seam-cycle-solve-8655b6ab` and `handoff-body/r11-seam-cycle-solve`. With nothing to decide, the roster's two carries were taken as the work (`## Forward-carry`).

## Head

`9b40afbfe7` on merge base `fd93aa3e9b` (origin/main at dispatch, `date -u` 2026-11-27). Seven commits (`git log --oneline fd93aa3e9b..9b40afbfe7`):

- `0fc6dd3e20`: the fix;
- `057401f07c`: pins for the first diff-mutant survivors;
- `df8d6ceb0d`: the accessor and publish read as plumbing (archscore);
- `cf2ea5fca0`: `tests/structure.py --record`, `class_excess_loc` and `max_class_loc` lower only;
- `aeb884da11`: the pin for the last survivor;
- `dd53c8ddf4`: the suite's doubles and two censuses follow the toggle (`## Figures`, scoped gate);
- `9b40afbfe7`: `async_diagnose_interval`'s guard line kept as main has it. The mutation ledger pins its GUARD_OFF site by line text, and `prepr.sh`'s ci-predict ledger arm read the shortened comment as `STALE PIN`. The one-line delta to the duty block read `ALL 5 FEATURES BLOCK PASSED`.

`git diff --stat cf2ea5fca0 9b40afbfe7 -- custom_components` lists only that comment line, so the production tree measured by the probes, the gate and the mutant runs is `cf2ea5fca0`'s, up to that comment. Structure and archscore were re-run at `9b40afbfe7`. `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh <this body>` printed `PRE-PR: 9b40afbfe726141cde84f7cfc270e05f6b6b4062 000000000000000000 rc=0`; its ci-predict arm printed `no closures, fast, governance or instrument red predicted against fd93aa3e9b16`. It ran scoped as the dispatch names: the full scope's 24 scripts were run through `tests/run.sh` and per script (`## Figures`). At this head, `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and `git merge-tree --write-tree origin/main HEAD` reported no conflict.

## Mutation proof

`MUTANT_CMD` = `python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" "# N-solve-recompute (carry, R11-SEAM-cycle-solve): a timed duty switch's toggle is laid on the plan in" "class _SgUpstreamDebouncer:"`. `<prelude>` is written by `features_block.py --emit-prelude <prelude> <same START> <same END>` from this tree (seven statements: the `_r9f13` rig and its imports). Each hand mutation below was run against the head's block (5 checks), then the line was restored:

- base production (`git stash` of `custom_components/`): `AttributeError: 'HeatPumpOptimizerCoordinator' object has no attribute 'async_apply_held'`, the block's failing-first run;
- M1, `switch.py` `_press` back to `publish_then_refresh(self)`: FAIL "N-solve-recompute: a boost or block switch publishes its state, then hands the entry's background task the held-plan toggle, not the publish-then-refresh helper's refresh";
- M2, `overlay_only` without `not refreshing`; M3, without `not gate.solving`; M4, `has_plan_base` always true (now `plan_base`): each FAILs "N-solve-recompute: with no plan base the toggle is an ordinary request; with a refresh in flight it trails it, with a solve in flight it re-runs it; a released entry writes nothing (#237) -- and none of the four actuates beside them";
- M7, `self._entry_released or` dropped from `async_apply_held`: the same check FAILs;
- M5, `await self._actuate_plan()` deleted from `async_apply_held`; M6, the publish deleted: each FAILs "N-solve-recompute: a duty toggle on a held plan actuates and publishes it with the overlay laid on (a space block zeroes the space power, hot water untouched), and never solves or requests a refresh";
- M8, the cycle's `_next_optimization` stamp deleted: FAIL "N-solve-recompute: the cycle's write tail the toggle shares runs inside every refresh -- action, frequency, pumps -- and is followed by the four bookkeeping steps, each once and in order, and the next solve is stamped one configured interval on".

Diff mutants: `python3 tools/audit/seat/mutant_run.py --diff "$(git merge-base origin/main HEAD)...HEAD" --cmd "$MUTANT_CMD" --max-mutants 40 --report-only` at `aeb884da11` (the head's production tree; `dd53c8ddf4` adds tests only) printed no `SURVIVED` line and exited 0 (`--report-only` prints survivors only; it measured: the first run at `0fc6dd3e20` printed seven `SURVIVED` lines and the run at `cf2ea5fca0` one, each pinned by a later commit, `## Unpinned sites`). `prepr.sh` ran with `PREPR_SKIP_CODE=1`, which skips its diff-mutant step, so this is the self-run line the dispatch names.

## Null control

The unmodified tree (`fd93aa3e9b`) runs the press through `publish_then_refresh._refresh`. The companion probe below reads `handed=['_refresh']` and 2 solves per press, both reproducing the reference plan. In the same probe the null arm `refresh` (a second identical refresh) reads `recompute=1` at both ends, by construction. The control arm `away` (a solve input changed) reads `recompute=0` at both ends. So the comparator separates a recompute from a needed solve, and the head's `switch_*` arms read 0 because no solve runs, not because the comparator went blind.

## Figures

Harness: the class sweep's own probe, `dev/audit/rounds/round11/sweep/N-solve-recompute/harness/probe.py` (sha1 be8817d69ff1), drives `boost.set_channel(..., refresh=False)` and then `coord.async_request_refresh()` by hand: the base press's call sequence, not the switch. At the head it measures the request path this diff rightly leaves alone, so it reads flat. The companion `$SCRATCH/harness/switch_probe.py` (sha1 d5c2d68416f1) is that probe with two edits: `REPO` taken from `$HPO_REPO`, since the tree copy's six `..` resolve one level short; and two arms, `switch_boost_dhw` and `switch_block_space`, that call the real `BoostDhwSwitch` / `BlockSpaceSwitch.async_turn_on()` and await the coroutine the press hands the entry's background task. Command: `HPO_REPO=$PWD PYTHONPATH=tests/hastub:dev/audit/rounds/round11/D9/s1:. python3 <probe> <arm>`, merge base `fd93aa3e9b` → head `aeb884da11`:

- companion `switch_boost_dhw`: `handed=['_refresh']`, `trigger_solves=2 reproduced=2 recompute=1` → `handed=['async_apply_held']`, `trigger_solves=0 reproduced=0 recompute=0`;
- companion `switch_block_space`: the same, 2/2/1 → 0/0/0;
- tree probe `boost_dhw` (the request path): `trigger_solves=2 reproduced=2 recompute=1` → the same, flat at both ends as stated above;
- tree probe `refresh` (null) `recompute=1` and `away` (control) `recompute=0` at the head (run against the uncommitted fix tree at `0fc6dd3e`'s content; the later commits change no line those arms reach outside `_async_update_data`'s write-tail call).

Class enumeration (`fixer.md` step 8). Rule: `PYTHONPATH=tests/hastub:. python3 dev/audit/rounds/round11/sweep/N-solve-recompute/harness/enumerate.py` lists every package call site of `async_request_refresh`, `async_refresh`, `async_refresh_now`, `async_run_optimization`, `_await_optimize` or `optimize_in_process` outside `_async_update_data`. Its own `--controls` (positive D9-s1-01, clean-fixture null, one-line perturbation) print `controls OK` in `harness/controls.out`. It printed `seams=27` at the base and `seams=28` at the head; the added seam is `async_apply_held`'s fallback request. Each head seam against its disposition:

- closed in this diff: `entity.py` `publish_then_refresh._refresh` as the duty switches reached it. The remaining callers are `OptimizerSwitch` (mode), `AwaySwitch` and the away-return datetime (away state), `ExternalHeatIgnoreBlockSwitch` (`boost.extheat_block_ignored`, read into the solve's `external_heat_active` in `_solve_record`) and the climate mode setter. Each writes a solve input before the refresh. `coordinator.py` `async_apply_held` → `async_request_refresh`: the fallback, taken only with no plan base or work in flight.
- closed by #3738: the diagnose press (absent from the head's list: `async_diagnose_interval` publishes with no cycle) and the Optimize Now button and `run_optimization` (`solve_gate.async_optimize_now`, two seams, whose purpose is the solve). The tree probe's `force_button` arm still drives the retired `async_run_optimization` + `async_request_refresh` pair, so it no longer measures the button.
- a solve input written before the trigger (not a recompute by the class's rule: the probe's `away` control): `button.py` sysid arm, comfort-weight reset and heat-loss reset; `coordinator.py` `async_adopt_heat_loss_refit`, `async_set_mode`, `async_update_thermal_params`, `async_apply_manual_plan`, `async_clear_manual_plan`, `async_restore_learned_snapshot`, `async_set_away`, and `__init__`'s away-input watch and input-return watch; `services.py` `handle_reset_heat_loss`; `__init__.py` `async_setup_entry` (the first solve after the light refresh, with no plan before it).
- unreached by production: `boost.py` `set_channel` / `set_block`'s `refresh=True` arm. Their one production caller, `TimedDutySwitch._press`, passes `refresh=False`; tests and round harnesses use the default.
- the solve mechanism itself, not a trigger of it: `_await_optimize` (two `optimize_in_process`), `async_run_optimization` → `_await_optimize` and its #1754 re-run, `async_request_refresh` → `super()`, `async_simulate` and `_held_solve` (the user's what-if on its own inputs).
- not a coordinator refresh: `_fetch_solar_forecast` → `self._open_meteo.async_refresh` (the Open-Meteo client).

Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff fd93aa3e9b --workdir "$D"` printed `MODE: SCOPED -- 24 script(s) run, 10 scoped out`. `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=fd93aa3e9b ./tests/run.sh` at `cf2ea5fca0` printed `4 TEST SCRIPT(S) FAILED`. Each failure came from this diff and is repaired at `dd53c8ddf4`:

- `tests/entities.py` and `tests/block_duty.py` raised `AttributeError: ... no attribute 'async_apply_held'`, because their coordinator doubles lacked it. `FakeCoordinator` now records the call with the same probe as a refresh. "every entity action publishes its own result at once … before the one refresh (or, for a duty switch, the held-plan toggle) it asks for starts" reads the two together, so either path is still one follow-up after the publish.
- `tests/features.py` "every actuation seam the cycle reaches is gated on plan staleness …" printed `the enumeration rule returned []`: the base rule read `_async_update_data`'s direct references only, and the write tail had moved into `_actuate_plan`. That `[]` is the census's failing-first run. The rule now roots at `_async_update_data` and `async_apply_held` and follows one hop through a method that writes nothing itself. The hop also returns `_command_valve_target` (gated), reached through `async_run_optimization` at the base as well, a seam the base census never read; the expected set names it.
- `tests/features.py` "every entity action and coordinator setter is a durability row …" printed `setters: ['async_apply_held']`, the setter pattern's match, now classified in `_RC2_SETTERS`.
- `tests/doc_claims.py`: the comment ratchet refused one new comment sentence over 40 words, now split.

At `dd53c8ddf4`, `PYTHONPATH=tests/hastub python3 <script>` printed:

- `tests/entities.py`: `ALL 2786 ENTITY CHECKS PASSED`;
- `tests/block_duty.py`: `ALL 161 BLOCK DUTY CHECKS PASSED`;
- `tests/doc_claims.py`: `ALL 443 checks PASSED`;
- `tests/features.py`: `ALL 6277 FEATURE CHECKS PASSED`.

The rest of the scope read ok in the `cf2ea5fca0` run; this delta edits `tests/` files only.

## Architecture score

`python3 tools/audit/archscore/score.py --diff fd93aa3e9b` at this head printed `Architecture score: dS -0.0011 WORSENS (inadmissible: coord_footprint 2533->2535)`:

- `coord_footprint` 2533 → 2535 (-0.0011): the two statements are `async_apply_held`'s branch (overlay on the held plan, or the ordinary request) and `_publish_uncycled`'s payload assignment. Payments tried, each measured with the same command:
  - the bookkeeping steps as one table loop: +8, because the metric counts each value a loop over a literal binds;
  - `has_plan_base` returning `bool(...)`: +1, now a plain accessor (`plan_base`, plumbing by the metric's rule) with the truth test in `solve_gate.overlay_only`, which is not handed the coordinator;
  - a publish helper taking a built payload: +1 beside the diagnose press, now the one helper that builds and publishes.

  Moving the branch into `solve_gate` or `boost` leaves it on a function handed the coordinator, which the metric charges by role. Moving it into the switch entity would put cycle policy in platform glue. No budget leaf is raised: `git diff fd93aa3e9b...HEAD -- '*_budgets.json'` moves `tests/structure_budgets.json` down only (`class_excess_loc` 17220 → 17218, `max_class_loc` 7762 → 7756, `recorded_at`).

## Unpinned sites

none left by this diff's block. Survivors of the diff-mutant runs (`MUTANT_CMD` above), each now killed by a check in the block:

- at `0fc6dd3e20`: `coordinator.py` `_publish_uncycled`'s payload assignment (STMT_DEL), `_async_update_data`'s `await self._actuate_plan()` (CALL_DEL), the bookkeeping step call (CALL_DEL), `_actuate_plan`'s frequency and pump steps (CALL_DEL), and `async_diagnose_interval`'s publish guard (GUARD_OFF) and publish (CALL_DEL). Killed at `057401f07c` by "the cycle's write tail the toggle shares runs inside every refresh …", "a diagnose press publishes the insight view on the held payload, once, without a cycle" and the payload-replaced arm of the held-toggle check;
- at `cf2ea5fca0`: the `_next_optimization` stamp (STMT_DEL), killed at `aeb884da11` (hand mutation M8).

Added sites with no `killed_by` pin yet. `prepr.sh`'s ci-predict named four at `dd53c8ddf4`. The diagnose guard is resolved: `9b40afbfe7` kept main's line text, so its existing pin applies. Each is killed by the duty block, and each disposition is "pinned by mutation-autofix" (its lane mutates `custom_components/`, `ci-autofix.md`):

- custom_components/heatpump_optimizer/boost.py:348 RETURN_DEL (`plan_base`): killed by "N-solve-recompute: a duty toggle on a held plan actuates and publishes it …" (with no base returned, the toggle falls back to the request and never actuates: hand mutation M4's sibling);
- custom_components/heatpump_optimizer/coordinator.py:6150 GUARD_OFF (`async_apply_held`): killed by "N-solve-recompute: with no plan base the toggle is an ordinary request …" (M2, M3, M4, M7);
- custom_components/heatpump_optimizer/solve_gate.py:178 RETURN_DEL (`overlay_only`): killed by the same two checks (a `None` return sends every toggle to the request);
- `custom_components/heatpump_optimizer/coordinator.py` `async_diagnose_interval` GUARD_OFF: main's existing pin, line text kept at `9b40afbfe7`.

## Red checks

none. No pull request exists for this head yet, so no check has run on it. `python3 tools/audit/seat/merge_train.py owed-reds` names the required set (`tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`, among others).

## Forward-carry

- Roster carry 0 (item f9a20486: the steady pair's hour scatter for a hot-water window, quiet-hours or wood-slot ask sent alone) was dispositioned at #3738's merge. Its own text allows that ("Not owed by the open pull request if its design excludes it: record the disposition at its merge"), and #3738's body records it under `## Forward-carry` as excluded by the approved design (`design.md` at 85feefcc). This part touches no `whatif.py` line. Carry: dismissed: dispositioned at #3738's merge under the carry's own release clause; this part builds the group's other carry
- Roster carry 1 (late class sweep N-solve-recompute, the timed duty switches' second solve): built here. #3738 left it to the orchestrator's ruling ("build here or as a split part"), and this dispatch to the group's fixer is that ruling. Carry: dismissed: built in this pull request
- The sweep's tree probe (`harness/probe.py`) drives each trigger's base call sequence by hand, not the entity. At this head its `boost_dhw`, `block_space` and `force_button` arms measure paths the switches and the button no longer take. The sweep reads this seam left at its stamp, and its next run reads flat unless it drives the entities, as the companion's two arms do. The probe is a round-11 measurement record and stays as written (`fixer.md` step 10). Carry: dismissed: a round-11 record left as written; the entity-driven arms and their sha1 are stated in `## Figures` for the stamp's reader

## Friction

- frugal-guard: contradiction: the session's frugal hook refuses a sixth inline read or command per prompt, verification runs included (a `mutant_run.py` invocation and a log read were refused), and points at a subagent; those runs went through haiku subagents that ran the one command and relayed its output. Carry: dismissed: a seat-environment conflict, recorded for the orchestrator
- probe-repo-root: stale: `dev/audit/rounds/round11/sweep/N-solve-recompute/harness/probe.py` computes `REPO` six levels up from its directory, one short of the repository root, so the roster's probe command (`PYTHONPATH=tests/hastub python3 .../probe.py boost_dhw`) raises `ModuleNotFoundError: No module named 'd9s1lib'` from the tree; it runs with `dev/audit/rounds/round11/D9/s1` and `.` on `PYTHONPATH`. The file is a round-11 record. Carry: dismissed: a round-11 evidence path; the working invocation is stated in `## Figures`
- wip-ref-ff: contradiction: the brief says to push each step "fast-forward only" to `handoff-wip/r11-seam-cycle-solve`, whose tip `4e5de6bad8` was #3738's 2026-11-21 state, not an ancestor of a worktree cut from origin/main. The first step push replaced it with `--force-with-lease` pinned to that SHA. `git merge-base --is-ancestor 4e5de6bad8 origin/main` exited 0, so nothing was lost; later step pushes fast-forwarded. Carry: dismissed: a seat-brief conflict, recorded for the orchestrator
