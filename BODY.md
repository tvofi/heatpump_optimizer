R11-OWNER-COOLING-GUARD: while the pump's mode reads Cooling or Cooling + DHW, no writer touches the power switch, in either direction. A plan or a boost asking for heat raises one repair, `pump_mode_cooling`, per episode. The repair clears when the mode leaves cooling. This is an owner item from the investigation of the owner's live install (orchestrator's local report `owner-live-inv.md`, section "Defect to dispatch"). The install's bundle stays private and is not read or cited here.

The defect at the merge base. `pump_arbiter.desired` keeps its hands off the mode, both set-points and the silent switch while the mode reads cooling. The supply gate was different: `supply_write` skipped only an OFF, and `step_supply` returns ON for any live boost. So a space boost or a plan ON powered up a pump sitting in Cooling.

What ships:
- `pump_arbiter.cooling_mode(inp, signals=None)` is the one reading of "the mode reads cooling". It reads the live select first, else the cycle's `PumpSignals` reading, which keeps the last good mode across a dropout. `desired`, `_mode_for`, the supply gate and the early cut-off all read it; the two inline `pump_mode.capability(...).cooling` reads it replaces are gone.
- `supply_hold.supply_write` (moved from `pump_arbiter`, beside `hold_supply`, the gate's minimums) returns `None` in both directions while `cooling_mode` reads a mode. Its blocked-both-channels OFF skip is unchanged. The coordinator's skip log moved into it.
- `supply_hold.note_cooling` raises `ISSUE_COOLING` once per episode in which the gate is asked for an ON. It clears the repair when `cooling_mode` reads none. The coordinator calls it from `_update_current_state`, after `_check_pump_mode_expired`, so the repair clears whatever the optimizer's mode (pinned with the optimizer Off). The episode flag is `ArbiterState.cooling_asked`, which is not persisted, so a reload in Cooling raises the repair again.
- `early_cutoff._exempt` returns `"cooling"` first, through `cooling_mode`. The cut-off calls `switch_supply` directly with OFF, so the gate alone would not cover it.
- Translations: `issues.pump_mode_cooling` in strings.json, en, sv and de. Docs: a "A pump in cooling is left alone" bullet in `docs/configuration.md` and a repair line in `README.md`.
- Not done, by the brief: nothing writes Heating back over a device-side Cooling. That needs an owner ruling.

Behaviour change to note: in Cooling + DHW the plan's hot-water steps no longer switch the power switch either. That follows from "hands off in both directions while the mode reads cooling", which is what the brief and `desired` already state for that mode.

## Head

Code head 0fb60d2b0ce09d263024b2d051834bb3064df11d: the PR head 74130e1bc9 (4317cb43e2ac, a merge of origin/main 8ef450936a, and the delivery row) plus one commit that repairs the two `tests / fast (3.14)` reds at 74130e1bc9. Merge base 8ef450936a1786abf4bb9610dc3336da4e77e8de. Against origin/main baa9a467ac at 2026-11-22T19:30Z, `git merge-tree --write-tree origin/main HEAD` reports no conflict.

The repair commit changes two test files and no production line:
- `tests/entities.py`: the R10 N-log-flood barrier refused `mismatch {('supply_hold.py', 'note_cooling'): (1, 0)}`. The warning in `note_cooling` is latched by `held.cooling_asked`, which is set in the same call that raises `ISSUE_COOLING`. The static rule cannot read that latch, so the site is listed with count 1 under "once per event by the function's own state (... an issue raised ...)". The barrier alone, run by AST from the test file over the package (script `barrier_check.py` in the seat's scratch), printed that mismatch with the previous `tests/entities.py` and `mismatch none` with this one.
- `tests/features.py`: the comment ratchet in `tests/doc_claims.py` refused the cooling block's first comment sentence (41 words). It is split in two; the block's first line keeps its opening words. `python3 tests/doc_claims.py` at the head: `ALL 441 checks PASSED`.

The seat venvs on this host carry no `homeassistant` and the container runtime was not running, so `tests/entities.py` and `tests/mutation_table.py --pin-killed` were not run here: the barrier was run alone by AST, and the pins are left to `tests / mutation-autofix` at this head. The prepr is not run again here: the code-keyed steps are CI's (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`). Before 74130e1bc9 the full prepr did not finish on the previous seat's host: the first run timed out at 50 minutes waiting for the heavy slot, the second was stopped by a timeout (rc=124) after `pinned graders`.

## Mutation proof

Failing test first. The block opening `# Cooling is the user's season (``pump_arbiter.cooling_mode``)` in `tests/features.py` was run with `python3 tools/audit/seat/features_block.py --prelude 'exec(open("<prelude>").read())' "<that line>" "from heatpump_optimizer import duty_switch as _ds_mod"`. Its prelude was written by `--emit-prelude` on the same markers.
- The same checks on the merge base's production files (the first 17; the 18th was added later to kill a survivor) printed `11 of 17 FEATURES BLOCK FAILED`. Both boosts in Cooling and in Cooling + DHW wrote `('switch', 'turn_on')`. The plan ON in Cooling wrote turn_on. The cycle's last-good Cooling through a dropout wrote turn_on. All four repair checks failed, because the repair did not exist. Both early cut-off cooling rows returned `None`. The four null controls passed. Also red at the base: "a plan OFF with the pump running in Cooling writes nothing" (turn_off). That case is narrower than it looks: the base's OFF skip read only the cycle's `PumpSignals`, which this fixture does not refresh, so in production the base skipped that OFF on every cycle after the cycle's signal read. It missed only a mode change between cycles.
- At the head: `ALL 18 FEATURES BLOCK PASSED`.

Hand mutants. Each one was applied alone to the head's production files, the block run, and the file restored. The restore was checked with `git diff --quiet` on the four files (script `mutants.py` in the seat's scratch; it prints `restored: production files equal HEAD`). 11 of 11 killed; the first failing check of each is named:

| mutant | first failing check |
|---|---|
| `supply_write`: cooling term dropped (`note_cooling(...) or True`) | a space boost with the mode reading Cooling writes no switch-on (5 of 18) |
| `cooling_mode`: live arm dropped | a space boost with the mode reading Cooling writes no switch-on (7 of 18) |
| `cooling_mode`: signals arm dropped | the cycle's last good Cooling holds a boost's switch-on through a dropout (1 of 18) |
| `cooling_mode`: always `None` | a space boost with the mode reading Cooling writes no switch-on (10 of 18) |
| `note_cooling`: once-per-episode guard dropped | raised once for two boosted writes in one Cooling episode (2 of 18) |
| `note_cooling`: `asks_heat` ignored | a plan OFF in Cooling asks for no heat and raises no cooling repair (1 of 18) |
| `note_cooling`: never clears | cleared when the mode leaves cooling (1 of 18) |
| `note_cooling`: never raises | raised once for two boosted writes in one Cooling episode (3 of 18) |
| `note_cooling`: episode flag not kept | raised once for two boosted writes in one Cooling episode (3 of 18) |
| coordinator: per-cycle `note_cooling` call dropped | cleared when the mode leaves cooling (2 of 18) |
| `early_cutoff._exempt`: cooling exemption dropped | early cut-off: a space step with the mode reading Cooling -> cooling (2 of 18) |

The first pass at commit 0a8d283632 left one survivor, `asks_heat` ignored. The check "a plan OFF in Cooling asks for no heat and raises no cooling repair" was added and kills it.

## Null control

- In the block: a boost with the mode reading Heating, and one reading Heating + DHW, each switch the pump on. A plan OFF in Heating switches it off. The cycle's last-good Heating lets a boost through. A boost in Heating raises no cooling repair. The early cut-off on a Heating space step returns `None`. All of these pass at both ends.
- The existing supply-gate block (the `tests/features.py` lines from `from homeassistant.util import dt as _sa_dt` to this block, which hold the held-write and both-blocked skip-log checks, now on `supply_hold._LOGGER`) printed `ALL 108 FEATURES BLOCK PASSED` at the head.

- Re-run at 0fb60d2b0c by this seat with `tools/audit/seat/features_block.py` (prelude from `--emit-prelude` on the same markers): at the head `ALL 18 FEATURES BLOCK PASSED`; on origin/main baa9a467ac's `custom_components/` with the head's tests `10 of 18 FEATURES BLOCK FAILED` (the four boost and plan writes, the dropout, three repair checks and both early cut-off rows); with the supply gate's cooling term mutated (`if (note_cooling(...) is None or True) and ...` in `supply_hold.supply_write`) at the head `5 of 18 FEATURES BLOCK FAILED`.

## Figures

- Hand mutants: 11 of 11 killed at 0a8d283632..ac7ba8d22c (table above; the production files of ac7ba8d22c are the head's, since 5ac350ab6c changes only `tests/structure_budgets.json`).
- `python3 tests/structure.py` at ac7ba8d22c: no budget breached. class_excess_loc and max_class_loc fall by 7 and module_excess_loc by 11, re-recorded in 5ac350ab6c with the reason in its commit message.
- `python3 tools/audit/archscore/score.py --diff 3a98735a7e HEAD` at ac7ba8d22c: `Architecture score: dS +0.0000 NULL`. An earlier cut, which handed the coordinator to `supply_write`/`note_cooling`, read `coord_footprint 2525 -> 2535` (inadmissible). That is why the gate takes the arbiter record and the pass inputs as plain values.
- Class enumeration (fixer step 8), for the writers of the heat pump power switch: `grep -rn "switch_supply\|write_supply\|on_off_service" custom_components/heatpump_optimizer/*.py`. It returns `pump_arbiter.write_supply` (called only from `coordinator._write_supply`, the gate, closed here), `pump_arbiter.switch_supply` (called by `write_supply` and by `early_cutoff.on_room_event`, exempted here) and the `on_off_service` routing. `coordinator._async_set_pump` writes the circulation pumps, not the power switch, so it is out of class. `disinfection.py` writes the disinfection switch, which is also not the power switch.


## Unpinned sites

- custom_components/heatpump_optimizer/early_cutoff.py:223 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1321 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:1405 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/pump_arbiter.py:2069 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/supply_hold.py:178 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/supply_hold.py:181 RETURN_DEL: pinned by mutation-autofix
- custom_components/heatpump_optimizer/supply_hold.py:191 BOOLOP: pinned by mutation-autofix
- custom_components/heatpump_optimizer/supply_hold.py:191 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/supply_hold.py:193 GUARD_OFF: pinned by mutation-autofix
- custom_components/heatpump_optimizer/supply_hold.py:199 RETURN_DEL: pinned by mutation-autofix

## Red checks

Five checks concluded red at 74130e1bc9, the only branch commit CI ran on.
- `tests / fast (3.14)`: two scripts. `tests/entities.py` refused the log-flood barrier on `note_cooling`; `tests/doc_claims.py` refused a 41-word comment sentence in `tests/features.py`. Both repaired at 0fb60d2b0c (## Head). Cheaper detector: both scripts are in the scoped gate `prepr.sh` runs for this diff, before any push; the full prepr that would have run them did not finish on the previous seat's host, and the PR was opened under `PREPR_SKIP_CODE=1`. The detector exists; it was skipped, so no new one is owed.
- `gate`: aggregates required checks; it was red on `tests / fast (3.14)` (`FAIL tests / fast (3.14): failure`). Same cause and detector as that line.
- `tests / mutation`: red by construction on the 10 added sites under `## Unpinned sites`. No cheaper detector is owed: the table refuses every added guard until a driver's kill is recorded, which is the autofix's job after the push.
- `tests / mutation-autofix`: `skip-measure-failed`. The pin shards' baseline was red in `tests/doc_claims.py` (the comment ratchet above), so no mutant verdict was taken and no pin commit came. Same cause and detector as `tests / fast (3.14)`; with the baseline repaired the job measures again at the new head.
- `pr-contract / pr-contract`: this body's `## Red checks` did not name `tests / fast (3.14)` or `tests / mutation`. Cheaper detector: `body_patch.sh` and `bus.sh dispatch` already refuse such a body before the PR is moved, and did refuse it; the body was not repaired before the head ran CI.

## Forward-carry

none

## Friction

none
