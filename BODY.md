Why this change, and what it measures.

The R10-N-log-flood barrier (`tests/entities.py` `_R10_LOG_ALLOWED_BY_REASON`) listed eight unlatched WARNING/ERROR sites as OWED (#2337): each reached every cycle or solve, each triggered by a condition that persists. This PR closes all eight and deletes their OWED entries.

- `coordinator._note_solve_failure`, `_command_valve_target` (three sites), `pump_arbiter._space_target` and `inputs._age_gate` route through `log_latch.log_held`, a leaf module, so the arbiter and the input reader take the latch without an import cycle through the coordinator. The latch owner is what outlives the call: the coordinator for its own sites, `hass` for the arbiter and the reader (`ArbiterInputs` and `InputReader` are rebuilt every pass). A `None` owner logs every call rather than raising into a cycle.
- `optimizer.optimize`, `_solve_space` and `_optimize_space_only` are demoted to DEBUG: a failed solve already surfaces once through the latched `_note_solve_failure`, and the solver runs in a worker process that cannot hold the coordinator's latch.
- The stale-plan hold in `coordinator._apply_action` is demoted to DEBUG: its text carries the plan's age and the failed-solve count, which advance every cycle, so no stable latched text exists; `EVENT_PLAN_STALE` is the once-per-occurrence signal.
- The latch is public API, `log_held`: three modules import it, and main's `archscore.private_cross_module` cap (17, `tests/ci_budgets.json`) counts each import of a private name across modules. The five killed-pin rows under `tests/mutation_ledger/killed_by/log_latch.py/` follow the symbol.

## Head

`72a6844ae544f3c0b892a9403d6d2923da9d73da`

## Mutation proof

Each mutant over the finder's runtime probe `dev/audit/rounds/round10/D14/log_flood/probe.py`, in a detached copy of the head, restored after.

1. `log_latch.log_held`: `if held.get(key) == text:` to `if False:` (the latch never holds). The probe exits 1 with `floods=1` or more on ten arms, among them `solve_failure`, `stale_plan`, `valve_mistyped`, `space_target_misdeclared` and `future_stamp=3`.
2. `coordinator._apply_action`: the stale-plan `_LOGGER.debug("Plan is ...` back to `log_held(self, "stale_plan", True, "Plan is ...`. The probe exits 1 with `stale_plan.floods=1` and `4x Plan is # minutes old after # failed solves; ...`.

## Null control

The probe's `control` arm (a 48-row forecast, prices present) reads `floods=0` at this head.

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py` -- every arm `floods=0`, exit 0.
- `python3 dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer` -- `sites=70 latched=6 seams=64`; the remaining seams are the barrier's reasoned list, which `tests/entities.py` holds at exact counts.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -- `ALL 2346 ENTITY CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/solar_alignment.py` -- `ALL SOLAR ALIGNMENT CHECKS PASSED`.
- `python3 -I tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` -- `Architecture score: dS +0.0000 NULL`.
- `python3 tests/ci_ratchet.py --metrics-dir <dir>` over the committed `tests/ci_budgets.json`, `<dir>` holding `script_runs_per_push` push rows (the entities null control's own input) -- `archscore.private_cross_module: 17 (budget 17)`, rc 0.
- `python3 tests/mutation_table.py --scope changed --base origin/main --max 0 --jobs 1` -- "the ledger agrees with the deterministic inventory", `MUTATION TABLE PASSED (empty pool)`.
- `PYTHONPATH=tests/hastub python3 tests/features.py` -- `ALL 4157 FEATURE CHECKS PASSED`; the rest of the scoped set is CI's `fast (3.14)` job on this head.

## Red checks

- `fast (3.14)` -- red at `225bff1cf`: `tests/entities.py` failed `and main() passes the committed table at its own recorded count (the null control)`, because the branch read `archscore.private_cross_module: 20 (budget 17)` once main capped that metric. Cheaper detector: `tests/ci_ratchet.py`'s `main()` over the committed table, seconds locally, the same computation the check makes; it cannot fire before main adds the cap, so merging main and running it is the answer, not a new check. Paid by making the latch public (`log_held`), not by a raise.
- `delivery-status` -- red at `7ef037831` and `225bff1cf`: `DELIVERY STATUS OVERDUE` on main's row backlog (#2329, #2335, #2323, #2311), none of them this PR's. Not a required context; no cheaper detector belongs to this branch, since the backlog is main's.
- `pr-contract` -- red at `7ef037831`: the body named a previous head until the delivery row moved it to `225bff1cf`, where it passed. Cheaper detector: `tools/pr/prepr.sh` step 7, which reads `## Head` against the local head before push.
- `arch-score` -- red at `83bf0770c`: `coord_footprint 2547 -> 2552`, from threading the coordinator into `pump_arbiter._space_target` to give the latch an owner. Cheaper detector: `python3 -I tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`, about a minute locally, the same computation. The owner is now `inp.hass`, already in the snapshot; the gate reads `dS +0.0000 NULL`.
- `mutation` -- red at `83bf0770c`: `MUTATION TABLE REFUSED -- the ledger is not in canonical form`, on hand-written re-keyed rows. Cheaper detector: that refusal is the first seconds of the command CI runs; `python3 tests/mutation_table.py --normalize` writes canonical bytes.
- `fast (3.14)` and `pr-contract` -- also red at `83bf0770c`: counts the new leaf module moved (the #1218 selection-cost note, the D6 module census, `class_excess_loc`, the `#2226` probe's logger), and a body naming none of those reds. Cheaper detector: `GATE_SCOPE=auto ./tests/run.sh` selects exactly those scripts locally, and `tools/pr/prepr.sh` step 7c reads the pushed reds; each owning check already refused the stale count.

## Forward-carry

none

## Friction

none
