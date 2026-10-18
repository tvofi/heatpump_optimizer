Why this change, and what it measures.

The R10-N-log-flood barrier (`tests/entities.py` `_R10_LOG_ALLOWED_BY_REASON`) listed eight unlatched WARNING/ERROR sites as OWED (#2337): each reached every cycle or solve, each triggered by a condition that persists. This PR closes all eight and deletes their OWED entries. A persisting condition now warns when it starts, logs DEBUG while it holds, and warns again when it recurs after clearing.

- `coordinator._note_solve_failure`, `_command_valve_target`, `pump_arbiter._space_target` and `inputs._age_gate` route through `log_latch.log_held`, a leaf module the arbiter and the input reader import without a cycle through the coordinator. Every site passes the condition itself as `active` and so clears on recovery: the success path clears the solve failure; a successful valve write clears the valve latch (its two failures, a wrong entity domain and a raising write, share one latch whose text names which, computed by the module-level `_valve_write_problem`); every gated read clears a future stamp; a holdable minimum or a flow unit clears a misdeclared set-point.
- The owner is what outlives the call: the coordinator for its own sites, `hass` for the arbiter and the reader (`ArbiterInputs` and `InputReader` are rebuilt every pass), keyed per input and entity. `coordinator.async_shutdown` calls `log_latch.forget_held(hass)`, so a reloaded entry reports a condition that persisted through the reload. A `None` owner logs every call rather than raising.
- A failed solve starts as an ERROR with the exception's traceback (`log_held(..., exc_info=err)`), as before the latch, and repeats at DEBUG.
- `optimizer.optimize`, `_solve_space` and `_optimize_space_only` are demoted to DEBUG. On the first pass a failure's `failed (...)` status reaches `_note_solve_failure`; a failed `_co_optimize` candidate pass keeps the first pass's status and stays at DEBUG, as its sibling except does.
- The stale-plan hold in `coordinator._apply_action` is DEBUG: its text renders the advancing age and failure count, so no stable latched text exists; `EVENT_PLAN_STALE` and the solve failure's ERROR carry the signal.
- The latch is public API, `log_held`: three modules import it, and `archscore.private_cross_module` (cap 17, `tests/ci_budgets.json`) counts each import of a private name.
- `dev/audit/rounds/round10/D14/log_flood/probe.py` adopts the round-6 reviewer's hold/clear/recur harness as five `recur_*` arms (solve failure, valve write, misdeclared set-point, future stamp, and a reload), each failing the script on `recur=0` or a logging clear phase.

## Head

`aef46436e67c917821a6126aa882d2a4f2468a28` merges origin/main `2b06786c2` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`0adc1924112645f962bb6429d411ca273b5ff12f`

## Mutation proof

Each mutant in a detached copy of the head, over `dev/audit/rounds/round10/D14/log_flood/probe.py`, restored after.

1. Delete the success path's `log_held(self, "solve_failure", False)` in `coordinator._async_update_data`: `RESULT recur_solve_failure.hold=1 clear=0 recur=0`, `PROBE FAILED`, exit 1.
2. Delete `forget_held(self.hass)` in `coordinator.async_shutdown`: `RESULT recur_reload.hold=2 clear=0 recur=0`, `PROBE FAILED`, exit 1.
3. The two mutants that survived CI's `mutation` lane at `75a788a87`, now killed by `tests/features.py` (`mutation_table.py --pin-killed --base origin/main`: `PIN KILLED: 2 pinned, 0 left unpinned`): `_command_valve_target`'s latched early return as `if False:` (a refused write would be remembered as commanded and never retried), and `_space_target`'s bound `low > room + SETPOINT_TOLERANCE` as `>=` (a minimum exactly the tolerance above the room target would be refused).
4. The previous head `dec7b91ea734b7b3ebcdfebe402f9aee553b1faf` (every site passing a literal `True`) under this head's probe: `recur_future_stamp`, `recur_solve_failure`, `recur_space_target` and `recur_reload` read `recur=0` and `recur_valve_write` reads `hold=0` (its old text named no entity), `PROBE FAILED: 5 arm(s)`, exit 1.

## Null control

The probe's `control` arm (a 48-row forecast, prices present) reads `floods=0`, and every `recur_*` clear phase reads `clear=0`, at both heads.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py` -- every flood arm `floods=0`; `recur_future_stamp.hold=2 clear=0 recur=2`, `recur_solve_failure`, `recur_space_target` and `recur_valve_write` `hold=1 clear=0 recur=1`, `recur_reload.hold=2 clear=0 recur=2`; exit 0.
- `python3 dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer` -- `sites=71 latched=6 seams=65`; the latch's own two sites (WARNING, and ERROR with a traceback) are on the barrier's list.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -- `ALL 2346 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` -- `ALL 4160 FEATURE CHECKS PASSED`, including the new solve-failure arm (ERROR with traceback once per spell, DEBUG on repeats, ERROR after the clear; `forget_held` re-arms).
- `PYTHONPATH=tests/hastub python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`; `max_class_loc 8629`, `class_excess_loc 18454`, recorded.
- `PYTHONPATH=tests/hastub python3 tests/solar_alignment.py` -- `ALL SOLAR ALIGNMENT CHECKS PASSED`.
- `python3 -I tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` -- `Architecture score: dS +0.0011 IMPROVES` (`coord_footprint 2547 -> 2545`).
- `python3 tests/ci_ratchet.py --metrics-dir <dir>` over the committed `tests/ci_budgets.json`, `<dir>` holding `script_runs_per_push` push rows -- `archscore.private_cross_module: 17 (budget 17)`, rc 0.
- `python3 tests/mutation_table.py --scope changed --base origin/main --max 0 --jobs 1` -- "the ledger agrees with the deterministic inventory", `MUTATION TABLE PASSED (empty pool)`: the 6 sites this diff adds are pinned (4 by `mutation-autofix` at `75a788a87`, 2 by `--pin-killed` here), and three killed pins whose lines the rewrite replaced are retired.

## Unpinned sites

none: every site this diff adds is pinned under `tests/mutation_ledger/killed_by/` (four by `mutation-autofix`'s `ci: pin killed mutants` at `75a788a87`; `coordinator.py` `_command_valve_target` GUARD_OFF and `pump_arbiter.py` `_space_target` CMP_BOUND by `--pin-killed`, after the two `tests/features.py` checks that kill them).

## Red checks

- `mutation` -- red at `f4df86098` and `75a788a87`: `MUTATION TABLE REFUSED`, six then two sites this diff added with no disposition. `mutation-autofix` pinned four at `75a788a87`; the two survivors (the valve latch's early return, the set-point bound) are now killed by new `tests/features.py` checks and pinned. Cheaper detector: `tools/pr/prepr.sh` step 7d lists the added unpinned sites before push; it read them, and the body deferred them to autofix rather than driving them, which is what left the survivors for CI.
- `pr-contract` -- red at `f4df86098` (01:57Z), green there at 02:52Z: "`## Head` does not name f4df860" while the PR carried the previous body. Same push-order window as at `72a6844ae` below.
- `pr-contract` -- red at `72a6844ae` (run 23:06Z), green there at 23:29Z: "`## Head` does not name 72a6844" -- the PR still carried the previous body when the code head landed. Cheaper detector: `tools/pr/prepr.sh` step 7, which passed on the new body; the window between the code push and the body edit is the push order steward S10 prescribes, not a missing check.
- `fast (3.14)` -- red at `225bff1cf`: `tests/entities.py` failed the CI ratchet's null control, `archscore.private_cross_module: 20 (budget 17)`, once main capped that metric. Cheaper detector: `tests/ci_ratchet.py` over the committed table, seconds locally, the same computation; it cannot fire before main adds the cap, so merging main and running it is the answer. Paid by making the latch public.
- `delivery-status` -- red at `fc9d9186d`, `7ef037831` and `225bff1cf`: `DELIVERY STATUS OVERDUE` on main's row backlog, none of it this PR's. Not a required context; no detector belongs to this branch.
- `pr-contract` -- red at `7ef037831`: the body named a previous head. Cheaper detector: `tools/pr/prepr.sh` step 7, `## Head` against the local head before push.
- `arch-score` -- red at `83bf0770c`: `coord_footprint 2547 -> 2552`, from handing the coordinator to `pump_arbiter._space_target`. Cheaper detector: `python3 -I tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`, about a minute locally. The owner is `inp.hass`.
- `mutation` -- red at `83bf0770c`: `MUTATION TABLE REFUSED -- the ledger is not in canonical form`, on hand-written rows. Cheaper detector: that refusal is the command's first seconds; `python3 tests/mutation_table.py --normalize` writes canonical bytes.
- `fast (3.14)` and `pr-contract` -- also red at `83bf0770c`: counts the new leaf module moved, and a body naming none of those reds. Cheaper detector: `GATE_SCOPE=auto ./tests/run.sh` selects those scripts locally, and `tools/pr/prepr.sh` step 7c reads the pushed reds.

## Forward-carry

none

## Friction

none

