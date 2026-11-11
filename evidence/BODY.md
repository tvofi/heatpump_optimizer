Thank you to Bankaifan for pull request 3457, adopted here with Bankaifan as the author of its commit (`cycle_supply` beside `step_supply`, one call in `_apply_action`, two checks); our work is the later commit. Part of #201.

The cycle cuts its action at the solve, then awaits system identification, the fuse advisor and the price tile before `_apply_action` writes `heat_pump_on`. `note_supply` stamps that write with the step it lands in, so `supply_tick` left a write one step late standing against the plan for up to one plan step, in either direction. `cycle_supply` writes `step_supply` for the landing step and falls back to the action's value wherever `step_supply` returns `None` (non-plan mode, stale or missing plan, system identification, instant outside the plan).

**Seam decision (sibling sites).** The owning seam is the supply switch alone, not the whole action re-cut for the landing step. Re-cutting before `boost.apply` would move the system-identification override and the boost overlay's precedence for one defect in one actuator.
- `async_publish_current_action` (the displace value and set-point of the earlier step): not covered. It stays on the action cut at the solve; a step's displace is a curve offset, not the switch. Carry: R10-ECL110-MQTT-OFF-NEUTRAL (roster commit 84184ae668 on `handoff/audit-r10-roster`, landed)
- The legacy payload's `heat_pump_on` from the same call can disagree with the switch for the landing step after this change: not covered, not claimed. Carry: R10-ECL110-MQTT-OFF-NEUTRAL (roster commit 84184ae668, landed)
- Boost overlay and system identification: unchanged, `step_supply` already yields `True` under a live boost and `None` under system identification; pinned below.

## Head

Changed since the reviewed 134d25cbce3e369577b7b4c1951ff656ba82ced2: the tip moved to b3b51d42 (not itself reviewed), and this head adds one ledger row only (`tests/mutation_ledger/killed_by/pump_arbiter.py/cycle_supply.RETURN_DEL.011422a2.json`); no production or test code differs from b3b51d42.

68646456c774b1d0e58e6c79f6fd0a38281d334c on base ee64358be7ee (origin/main when measured, `git rev-parse origin/main`, 2026-11-11 UTC).

## Mutation proof

`cycle_supply`'s last line changed to `return on` (the action's value), `PYTHONPATH=tests/hastub:tests python3 tests/features.py` from the repo root:
- FAIL `a cycle whose ON action was cut in the last step writes the OFF of the step it lands in`
- FAIL `a cycle whose OFF action was cut in the last step writes the ON of the step it lands in`
Restored afterwards; the run at the head fails only the inherited census below.

## Null control

Each own-step null control runs the same cycle with `pump_arbiter.cycle_supply` swapped for main's behaviour (the action's value) and compares the full service-call lists, calls and order: economy plan mode, auto plan mode with an OFF cut, fixed comfort mode, stale plan, live boost (the action made ON as the overlay does), system identification. All pass. A first draft cut the boosted action OFF, which the overlay never does; that control failed and was corrected to the real shape. Further checks pin that a fixed mode, system identification and a live boost over an OFF step keep their command when the write lands a step late, and `the same OFF-planned cycle inside the action's own step writes its OFF`.

## Figures

- Feature checks: `PYTHONPATH=tests/hastub:tests python3 tests/features.py`: 1 of 5250 failed, the inherited combi census; the two mutation-proof checks above are the only ones red with the mutation.
- Gate: `tools/pr/prepr.sh` exit 0 at this head with `PREPR_SKIP_CLOSURES=1` (the interpreter here lacks the homeassistant module; the owner's standing ruling), MODE: SCOPED; closures left to CI.
- Cut-to-write time, and the share of cycles crossing a step boundary at the configured interval: not measured. The container has no Home Assistant runtime or real solve, so a timing here would time stubs; the contributor's link to a reload is not verified either. Carry: dismissed: the fix does not depend on the figure.
- Goldens: none moved; both claim files byte-identical to origin/main (prepr `claim files`).

## Unpinned sites

`custom_components/heatpump_optimizer/pump_arbiter.py:1593 RETURN_DEL` (`cycle_supply`'s last line): pinned in `tests/mutation_ledger/killed_by/pump_arbiter.py/cycle_supply.RETURN_DEL.011422a2.json`, killed by `tests/typing_ruler.py` (`python3 tests/mutation_table.py --pin-killed --base origin/main`, run with the inherited combi census bound locally raised so the baseline was green; the raise is not committed). Also measured by hand: the mutant `return None` takes `tests/features.py` from 2 to 30 failed checks. It is the only unpinned site the table reports for this diff.

## Red checks

`tests / fast`: `combi_type_branch census` red on main's combi census until its hotfix merges (R10-HOTFIX-COMBI-CENSUS-MAIN-RED); inherited, not caused by this diff.
- `mutation` at b3b51d4258a1: the 1 site under `## Unpinned sites` is now pinned in the ledger; no unpinned site remains.

## Forward-carry

The sibling publish sites of the supply write are two, named here: (1) `async_publish_current_action` in `custom_components/heatpump_optimizer/coordinator.py`, the displace value and set-point of the earlier step; (2) the legacy payload's `heat_pump_on` from that same call, which can disagree with the switch for the landing step. Both land in the R10-ECL110-MQTT-OFF-NEUTRAL group of `dev/programme/rosters/wave-r10-groups.json`, landed as roster commit 84184ae668 on `origin/handoff/audit-r10-roster` (it replaces the dropped d188b50681); its text starts "From r10-outside-supply-stale-step, body item 30ec8edf: The sibling publish sites of the supply write that pull request". Carry: R10-ECL110-MQTT-OFF-NEUTRAL (roster commit 84184ae668, landed)

## Friction

none
