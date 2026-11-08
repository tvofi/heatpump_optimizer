R10-SAV-COMFORT part 4 (topic r10-sav-comfort-p4). Part of #201.

Behind a valve, the thermostat reference (`HeatPumpOptimizer._apportion_by_steady_demand`) spread the horizon's simulated energy by steady demand with no pump cap. On a 3 kW pump with a -25 C night and 400 W/m2 midday sun it booked 3.678 kW, which is 1.226x the pump. That is carries 10, 13, 15, 16 and 18 (items 0497bde5, e9ced5fc, 7f2fa39d and fc24128d).

Now a step the spread would put past `max_electrical_power` is held at the pump, and its excess goes to the uncapped steps in proportion to their steady demand. Each pass holds only steps not yet held (`~held & (spread > cap)`), so the loop ends within one pass per step whatever the comparison. The energy is kept. The reference is inside the solve's bounds at its source, so `_optimize_space_only` no longer needs to clamp its seed (`np.clip(seed_power, 0.0, p_max)` is removed). This also adds the two-zone comfort-shortfall check owed by carry 11 (item 435eb685).

Alternatives considered:
- Triage the `spread >= cap` mutant as a hang. Rejected: the hang came from the loop's progress resting on a held step re-reading at exactly the pump; holding only new steps removes that, and the mutant is then killable, so a triage would sit on a killable mutant.
- Clamp the booked reference after the spread. Rejected: it destroys energy, and the saving would then be booked against a thermostat that bought less than it needed.
- Keep the seed clip as a second guard. Rejected: once the reference is capped it is dead code, its mutant can only survive, and the concern would have two owners.
- Move the helper to module level, beside `_floor_demand_at_target`. Rejected: it orphans three mutation-ledger rows whose anchors carry the class qualname, and gains nothing over paying the class lines in place.

Carry dispositions, numbered 1 to 20 as the roster entry holds them (the dispatch brief rendered the same list 0 to 19; its index is in brackets). Each one was re-measured at merge base 5bc009bc8 and at the head:

- Carry 1 (brief 0), comfort-matched null and summer_dhw_only start bound: both settled at main.
  - Part 3 (e57dfbbe0) settled the comfort-matched null. `r10_sav_null_settled.py` reads the const arm, comfort-matched with stored heat settled at both ends, at +0.28 %. The varying arm reads +14.28 %, which is the timing term.
  - `r10_sav_baseline.py null` still prints DEFECT at 12.34 % (10.83 % at 92588d581). That arm reads the raw month saving, which publishes the comfort shortfall beside the saving rather than netting it out, by the part 3 ruling.
  - `golden.capture('summer_dhw_only')` reads +5.881915 %, and `away_setback` reads 29.627509 %. The committed fixture's -3.17 % is a canonical-environment recording that this seat cannot honestly re-record (rule 3).
  - All of these read the same at both ends.
- Carry 2 (brief 1), volume basis: implemented at main (34cd75bf1). `r10_sav_volume.py` reads flat 0.00 and vary timing +74.88 at both ends.
- Carry 3 (brief 2), card equals `ledger.savings_months`: implemented at main (34cd75bf1).
- Carry 4 (brief 3), owner's baseline definition: implemented at main (34cd75bf1, then part 3).
- Carry 5 (brief 4), actuation phase: implemented at main (5d4e0bcfb). `r10_sav_actuation_phase.py` prints `AGREE: yes` at both ends.
- Carry 6 (brief 5), the two accuracy biases on one sample window: not taken here. It stays open on this group's roster entry.
- Carry 7 (brief 6), the month row's comfort shortfall: implemented at main (e57dfbbe0), with the same figures as carry 1.
- Carry 8 (brief 7), the duty-ledger tail settle: implemented at main (eb0cf1893). `AGREE: yes` at both ends.
- Carry 9 (brief 8), the unattributed residual (item 476710bb): measured, not attributed, and it stays open on this group's roster entry.
  - `r10_sav_wood_reference.py` reads -3.90 % (valve-flat), -8.02 % (valve-vary), -3.22 % (wood-cold) and -3.42 % (wood-stale), identical at both ends.
  - A scratch probe on valve-flat, in kWh_th: the plan delivers 264.54, the reference 263.10, comfort 11.25, stored -9.68. The plan buys about 22 kWh_th more than the settled reference.
  - Buffer-tank standing loss is ruled out: 2.16 for the plan against 1.91 for the reference.
  - The next hypothesis is that the two-zone comfort term counts the lower floor only (`_floor_demand_terms`). That needs a two-zone control. The single-zone reading of the same arm, at -154 %, is a different regime and not a control.
- Carry 10 (brief 9), no pump cap in `_apportion_by_steady_demand` (item 0497bde5): closed in this diff.
- Carry 11 (brief 10), the two-zone comfort check, M2 (item 435eb685): closed in this diff.
- Carry 12 (brief 11), the residual (item c38cb7d9): the same as carry 9.
- Carry 13 (brief 12), the pump cap (item e9ced5fc): closed in this diff.
- Carry 14 (brief 13), the residual (item d7f65c3b): the same as carry 9.
- Carry 15 (brief 14), the pump cap (item 7f2fa39d): closed in this diff.
- Carry 16 (brief 15), the pump cap, 1.226x on a 3 kW pump (item fc24128d): closed in this diff. The check that pins it reads 3.678 kW on the 3.0 kW pump at main.
- Carry 17 (brief 16), the residual (item 7da8ff67): the same as carry 9.
- Carry 18 (brief 17), the pump cap: closed in this diff.
- Carry 19 (brief 18), the residual: the same as carry 9.
- Carry 20 (brief 19), part-load refill pricing (item 213e8a10): not taken here, and it stays open on this group's roster entry.
  - `r10_partload_pricing.py` prints `null rows not zero 0`. Flat d=0.112 reads lp_err 0.267290, terminal-at-max 4.368455 and deferred-at-max 2.139841, at both ends.
  - The refill-residue harness the carry cites is not in the tree at the merge base.

## Head

682edb35c57930b5ea4b1b589b85139d9952032b, the code head, measured against merge base 661d26a5d2e655f32391048605db5970d133db1d (origin/main's tip when fetched, 2026-11-08T22:17Z).

This repair pass starts from the pull request's head e329c7a437744b790a7562223e16d4c212ae3975: mutation-autofix's pin commit on `06a9e764c` (this PR's delivery row) on `59c5ece96` (the orchestrator's merge of main `996ded2a6`). It merges origin/main `51cd5ec8a` (`git merge-tree --write-tree origin/main HEAD` reported no conflict), then adds two commits: the held-step pass with its check, and the ledger rows for the line it changed. main moved twice during clean `prepr.sh` runs: to `daf8b349f` (at e456d0fe; it brings `tests/card_browser.mjs` and a delivery row) and to `661d26a5d` (at e423a79d; it brings `tools/ci/` and `tools/audit/seat/` instruments and two delivery rows). Neither touches `optimizer.py`, `tests/features.py` or the mutation ledger, so the mutation proof and harness figures below, taken at e456d0fe, describe this head's production and test code. The unpinned-site count, gate scope and structure ratchet were re-taken at this head, and `prepr.sh` re-ran here.

After that clean run origin/main had moved again, to `7812357d5`; `git merge-tree --write-tree origin/main HEAD` reports no conflict and its delta touches none of `optimizer.py`, `tests/features.py` or the mutation ledger. main moved three times in three prepr cycles, so this head is handed off unmerged with it rather than chasing the tip; the merge-main bot or the orchestrator merges it.

## Mutation proof

Run through `tools/audit/seat/features_block.py "# Item 1: the settlement books the plan's thermostat baseline" "# The start's settlement, at its limits"` with `--prelude 'from datetime import datetime as _SavDT' --prelude 'import types as _sw_types'`, `PYTHONPATH=tests/hastub`; each edit restored after:
- **Head as committed:** rc=0, 14 checks ok.
- **`~held & (spread > cap)` changed to `~held & (spread >= cap)`** (the CMP_BOUND site): rc=1; one check goes red, `behind a valve, a step spread exactly to the pump keeps the spread`, reading `[1.5, 1.5, 1.5, 1.5]` (the simulation handed back) against `[0.0, 0.0, 0.0, 6.0]`.
- **The previous line `spread > cap` changed to `spread >= cap`** (the mutant CI left unpinned): the block runs to `timeout 90`, rc=124. A held step re-reads as over, the held set never grows, and the loop never ends. That is why `--pin-killed` could not kill it: a timeout is not a kill (`mutation_table.py` `SURVIVOR_LINE`).
- **The previous line `spread > cap` with the new check in place:** rc=0, 14 checks ok. The new check holds on the old code too; the behaviour at the boundary is unchanged.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3`: `PIN KILLED: 2 pinned, 0 left unpinned`; `optimizer.py:5594 CMP_BOUND` killed by `tests/features.py` (rc=0 failed=0 to rc=1 failed=2), `optimizer.py:5594 GUARD_OFF` killed by `tests/typing_ruler.py` (rc=0 failed=0 to rc=1 failed=1). The null control `optimizer.py:552 NULL_COMMENT` survived every driver.

The earlier proofs (main's uncapped spread, `zone = lowers` to `rooms`, the `> 0.0` to `> 1.0` guard) concern lines this pass leaves alone.

## Null control

- **The new check against the old line:** it passes there (above), so its red under the mutant is the mutant's, not a check that fails on any tree.
- **Comfort-matched and savings harnesses:** re-run at this head, each reads the figure it read at 7da8a92 (below). The cap does not bind in them, and the change touches only which steps are re-tested once held.
- **Two-zone check:** passes at this head.

## Figures

- **Unpinned sites** (`python3 tests/mutation_table.py --pin-killed --base origin/main`, first line): 2757 against 2755 at base 51cd5ec8a before the pins; 2755 against 2755 at base 661d26a5d at this head, `PIN KILLED -- 0 new unpinned site(s)`. The CI run 42521434959 at e329c7a read 2756 against 2755, the one being `optimizer.py:5594 CMP_BOUND`.
- **Feature checks** (`PYTHONPATH=tests/hastub python3 tests/features.py`, run with the new check over the previous line): `ALL 4984 FEATURE CHECKS PASSED`, 6m01s.
- **Comfort-matched null** (`PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py`, sha1 eca29a18ee19): const +0.28 %, vary +14.28 %, both SOUND, rc=0, at this head; the same at 7da8a92 and at main 5bc009bc8.
- **Raw month null** (`python3 dev/audit/harnesses/r10_sav_baseline.py null`, sha1 bc31f356191e): 12.336 % saved, DEFECT, rc=1, at this head; the same at 7da8a92 and at main.
- **Null-arm split** (`python3 dev/audit/harnesses/r10_sav_null_terms.py`, sha1 c981e7c840ed): power-weighted COP gain +17.29 %, at this head; the same at 7da8a92.
- **Unattributed residual** (`python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat`, sha1 dfcdcc46269e): -3.90 %, SOUND, at this head; the same at 7da8a92 and at main.
- **Gate scope** (`tests/closure.py select --diff $(git merge-base origin/main HEAD)`): `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- **Structure** (`python3 tests/structure.py`): `STRUCTURE RATCHET PASSED`; the pass is the same line count, no budget moved.

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.

## Unpinned sites

- `custom_components/heatpump_optimizer/optimizer.py:5592 CMP_BOUND`: pinned by mutation-autofix (ledger row `CMP_BOUND.bcdccc59`).
- `custom_components/heatpump_optimizer/optimizer.py:5594 CMP_BOUND`: pinned by `--pin-killed` at this head (row `CMP_BOUND.a0bdc820`, killed by `tests/features.py`).
- `custom_components/heatpump_optimizer/optimizer.py:5594 GUARD_OFF`: pinned by `--pin-killed` at this head (row `GUARD_OFF.a0bdc820`, killed by `tests/typing_ruler.py`); it replaces row `GUARD_OFF.979967aa`, whose line text this pass changed.
- `custom_components/heatpump_optimizer/optimizer.py:5597 RETURN_DEL`: pinned by mutation-autofix (row `RETURN_DEL.cb4dc380`).

## Red checks

- `tests / mutation` at e329c7a (run 42521434959): `MUTATION TABLE REFUSED -- 2756 unpinned site(s) against 2755`, the added `optimizer.py:5594 CMP_BOUND`. This branch's own: its `spread >= cap` mutant hung rather than failed, so mutation-autofix could not pin it. Repaired here: the pass now holds only new steps, the mutant is killed by a check, and both sites on the line are pinned. The cheaper detector: `prepr.sh` step 6d listed the site before the first handoff, and the previous body recorded it as killed on the diff-mutant run's count, not on the ratchet's verdict. `--pin-killed` at the head is the ratchet's own verdict and the cheaper detector; it ran at this head (above).
- `pr-contract` at 06a9e764c (run 42513575338): the body did not name the red `tests / mutation` under `## Red checks`. Answered by this section. The cheaper detector is `prepr.sh`'s body check, which reads the same rule offline; it was not re-run after the CI red.
- `gate` at 06a9e764c (runs 42513575338 and 42513575421): the aggregate of `tests / mutation`, first still being judged, then `FAIL tests / mutation: failure`. It carries no cause of its own; it is answered by the mutation line above.
- With this seat's `BASH_ENV`, `tests/entities.py` fails 3 checks at main and at the head alike (`/etc/profile.d/hpo-toolchain.sh` overrides `RUNNER_TEMP`); outside this group's scope, as the previous pass recorded.

## Forward-carry

none

## Friction

none
