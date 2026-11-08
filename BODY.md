R10-SAV-COMFORT part 4 (topic r10-sav-comfort-p4). Part of #201.

Behind a valve, the thermostat reference (`HeatPumpOptimizer._apportion_by_steady_demand`) spread the horizon's simulated energy by steady demand with no pump cap. On a 3 kW pump with a -25 C night and 400 W/m2 midday sun it booked 3.678 kW, which is 1.226x the pump. That is carries 0497bde5, e9ced5fc, 7f2fa39d and fc24128d.

Now a step the spread would put past `max_electrical_power` is held at the pump, and its excess goes to the uncapped steps in proportion to their steady demand. The energy is kept. The reference is inside the solve's bounds at its source, so `_optimize_space_only` no longer needs to clamp its seed (`np.clip(seed_power, 0.0, p_max)` is removed). This also adds the two-zone comfort-shortfall check owed by carry 435eb685.

Alternatives considered:
- Clamp the booked reference after the spread. Rejected: it destroys energy, and the saving would then be booked against a thermostat that bought less than it needed.
- Keep the seed clip as a second guard. Rejected: once the reference is capped it is dead code, its mutant can only survive, and the concern would have two owners.
- Move the helper to module level, beside `_floor_demand_at_target`. Rejected: it orphans three mutation-ledger rows whose anchors carry the class qualname, and gains nothing over paying the class lines in place.

Carry dispositions, each re-measured at merge base 5bc009bc8 and at the head:
- Carry 0 / 6 (comfort-matched null): already settled at main by part 3 (e57dfbbe0). `r10_sav_null_settled.py`: the const arm, comfort-matched with stored heat settled, reads +0.28 %. The varying arm reads +14.28 %, which is the timing term. Both read the same at main and at the head. `r10_sav_baseline.py null` still prints DEFECT at 12.34 % (10.83 % at 92588d581). That arm reads the raw month saving, with the comfort shortfall published beside it and not netted out, by the part 3 ruling.
- Carry 0 second limit (summer_dhw_only start bound): settled at main. `golden.capture('summer_dhw_only')` reads +5.881915 % at main and at the head, and `away_setback` reads 29.627509 % at both. The committed fixture's -3.17 % is a canonical-environment recording that this seat cannot honestly re-record (rule 3).
- Carries 1, 2, 3, 4, 7: implemented at main (34cd75bf1, 5d4e0bcfb, eb0cf1893). `r10_sav_actuation_phase.py` prints `AGREE: yes`, and `r10_sav_volume.py` reads flat 0.00 and vary timing +74.88, at both ends.
- Carries 9, 12, 14, 15, 17 (`_apportion_by_steady_demand` had no pump cap): closed in this diff.
- Carry 10 (two-zone comfort check, M2): closed in this diff.
- Carries 8, 11, 13, 16, 18 (unattributed residual): measured and not attributed. See Forward-carry.
- Carry 5 (accuracy biases on one sample window): not taken. See Forward-carry.
- Carry 19 (part-load refill pricing): not taken. See Forward-carry.

## Head

7da8a92dc87adc2960ec99bc8bf61575aff5168c, the code head, measured against merge base 5bc009bc82962df5d239cbacc2e570dffd9a9cf9 (origin/main's tip when fetched, 2026-11-08).

Owner ruling 2026-11-07: hand off at the first clean prepr head, and merge main only on a merge-tree conflict.

The first clean `tools/pr/prepr.sh` run is at this head (rc=0). origin/main has since moved to 72940b795, and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged in.

## Mutation proof

Applied to production `optimizer.py` and run through `tools/audit/seat/features_block.py`; each red listed below, then restored:
- **Main's `optimizer.py` restored** (the uncapped spread). Two checks go red:
  - `behind a valve, the spread reference holds a step at the pump, never past it, and keeps the simulated horizon's energy`: reference peak 3.678331746510925 kW against 3.0.
  - `behind a valve, a step spread past the pump is held there and the uncapped steps share the rest by their steady demand`: `[2.536, 3.442, 4.347, 8.875]`.
- **`zone = lowers` changed to `zone = rooms`** in `_settlement_schedule`. Two checks go red: `R10-SAV-COMFORT: two-zone, the comfort shortfall is the lower floor's (outdoor 10.0)` and `(outdoor 20.2)`. They read `[0.025, -0.075, -0.275]` against the expected `[-0.05, -0.45, -1.25]`.
- **Loop guard `> 0.0` changed to `> 1.0`**, the diff-mutant survivor of the first prepr run. One check goes red: `behind a valve, a horizon with a small steady demand spreads by it, not by the simulation`.
- **`tools/audit/seat/mutant_run.py --diff`** over the added lines, with `--max-mutants 40` and the two feature blocks as the command: 6 mutants, 0 survivors.

## Null control

- **Zero-demand house:** a horizon with no steady demand keeps its simulated schedule, and that existing check passes at both ends.
- **Cap off:** where the cap does not bind, every savings harness reads byte-identically at main and at the head: `r10_sav_baseline.py null` and `transient`, `r10_sav_null_terms.py`, `r10_sav_volume.py`, `r10_sav_actuation_phase.py`, `r10_partload_pricing.py`, `r10_sav_null_settled.py`, and `r10_sav_wood_reference.py` on the valve-flat, valve-vary, wood-cold and wood-stale arms.
- **Two-zone check:** it passes on the unmodified tree.

## Figures

- **Reference peak:** at main it is 3.678 kW on a 3.0 kW pump. At the head no step exceeds 3.0 kW and the horizon's energy is kept. Instrument: `tools/audit/seat/features_block.py "# Item 1: the settlement books the plan's thermostat baseline" "# The start's settlement, at its limits"`, with `--prelude 'from datetime import datetime as _SavDT' --prelude 'import types as _sw_types'`.
- **Comfort-matched null** (`PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py`, sha1 eca29a18ee19): const +0.28 %, vary +14.28 %, both SOUND, at main and at the head.
- **Raw month null** (`python3 dev/audit/harnesses/r10_sav_baseline.py null`): 12.336 % saved, DEFECT, rc=1, at main and at the head.
- **Null-arm split** (`python3 dev/audit/harnesses/r10_sav_null_terms.py`): booked thermostat 128.4 kWh against plan 112.6, comfort gap 6.9 kWh, power-weighted COP gain +17.29 %, at both ends.
- **Unattributed residual** (`python3 dev/audit/harnesses/r10_sav_wood_reference.py valve-flat`, also `valve-vary`, and `--quick wood-cold` / `--quick wood-stale`; sha1 dfcdcc46269e): -3.90 %, -8.02 %, -3.22 % and -3.42 %, identical at both ends.
- **Residual probe** (a scratch copy of that harness adding the plan's and the held reference's buffer-tank standing loss; probe kept out of the tree):
  - Valve-flat in kWh_th: plan delivers 264.54, reference 263.10, comfort 11.25, stored -9.68. The plan buys about 22 kWh_th more than the settled reference.
  - Tank standing loss is 2.16 for the plan against 1.91 for the reference, so the tank does not explain the gap.
  - The same arm read single-zone gives -154 %, a different regime, so it is no control for a two-zone comfort-term hypothesis.
  - Not attributed. Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`)
- **summer_dhw_only** (`golden.capture`): +5.881915 % at both ends; `away_setback` 29.627509 % at both ends.
- **Diff mutants** (`tools/audit/seat/mutant_run.py --diff 5bc009bc8...HEAD --max-mutants 40 --report-only`): 6 mutants, 0 survivors, 1265 s wall.
- **Gate scope** (`tests/closure.py select`): `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.
- **Structure** (`python3 tests/structure.py`): passes. `class_excess_loc` is 17560 against a budget of 17560. The +17 class lines were paid by tightening the new lines and spending stale prose in `_compute_baseline_power`. No budget moved.

## Architecture score

`python3 tools/audit/archscore/score.py --diff 5bc009bc8`: `Architecture score: dS +0.0000 NULL`.

## Unpinned sites

- `custom_components/heatpump_optimizer/optimizer.py:5578 CMP_BOUND`: pinned by mutation-autofix. It was killed in the diff-mutant run.
- `custom_components/heatpump_optimizer/optimizer.py:5580 CMP_BOUND`: pinned by mutation-autofix. It was killed in the diff-mutant run: under `>=` a held step re-reads as over, so the held set never grows.
- `custom_components/heatpump_optimizer/optimizer.py:5580 GUARD_OFF`: pinned by mutation-autofix. It was killed in the diff-mutant run.
- `custom_components/heatpump_optimizer/optimizer.py:5583 RETURN_DEL`: pinned by mutation-autofix. It was killed in the diff-mutant run: the zero-demand check requires an array.

## Red checks

With this seat's `BASH_ENV` set, `tests/entities.py` fails 3 checks, at main 5bc009bc8 and at the head alike: `a8:register_once`, `hb:positive_control`, and the Pages-workflow probe. The cause is `/etc/profile.d/hpo-toolchain.sh`, which `BASH_ENV` sources into every `bash -c`. Its `export RUNNER_TEMP=...` overrides the probe's own. Run with `env -u BASH_ENV`, which leaves the venv-ci python first on PATH, all 2665 entity checks pass at the head, and this prepr ran that way. See Friction.

A fourth failure at the head, the #1536 `min_electrical_power * 24 h per day` comment pin, was caused by this branch's own comment payment. It was fixed in this branch. The cheaper detector is that check itself, which runs in the scoped gate.

- `mutation` at 7da8a92dc87a: red by construction on the 4 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

- **Carries 8, 11, 13, 16, 18 (unattributed residual).** The residual is unchanged at -3.90 %, -8.02 %, -3.22 % and -3.42 %. Buffer-tank standing loss is ruled out (0.25 kWh_th apart). In kWh_th the plan delivers about 22 more than the settled reference. The next hypothesis is that the two-zone comfort term counts the lower floor only (`_floor_demand_terms`), which needs a two-zone control. Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`)
- **Carry 5 (power_ratio and cost_error on one sample window).** Not taken here. Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`)
- **Carry 19 (part-load refill pricing).** Not taken here. Re-measured at 5bc009bc8: `r10_partload_pricing.py` prints `null rows not zero 0`. Flat d=0.112 reads lp_err 0.267290, terminal-at-max 4.368455 and deferred-at-max 2.139841. The carry's refill-residue harness is not in the tree at the merge base, so its figures were not re-measured. Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`)

## Friction

- cloud-setup: unenforced: `tools/audit/seat/cloud-setup.sh` writes `/etc/profile.d/hpo-toolchain.sh`, which this seat's `BASH_ENV` names. Its `export RUNNER_TEMP` reaches every `bash -c` a test spawns, so three `tests/entities.py` checks go red at main on a cloud seat, and prepr's closures step refuses (`env -u BASH_ENV`: 2665 pass). Carry: R10-SAV-COMFORT (roster `dev/programme/rosters/wave-r10-groups.json`)
