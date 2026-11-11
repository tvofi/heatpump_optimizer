R10-OUTSIDE-DHW-CHARGE-SETTLE: the build of outside pull request #3434 by @Bankaifan, whose commit opens this branch with its authorship kept. A DHW charge start drops the tank reading 3-5 K within minutes. Main books that dip as a draw on the heated interval in the draw statistics, and as usage on the unheated intervals after a short charge. Both inflate the heavy-day p90 that the planner reads through `DrawStats.quantile`.

Repair round 2. Review blocked `8e2b7d99` as regression-unmeasured: the first gate folded every charge-affected interval as zero, so a real draw during a charge or up to 15 min after one was lost. At a draw 5 min after the last heated sample, the truth arm's p90 fell from 5.5488 to 1.9468 kWh. That gate is replaced, not tuned.

The fix rests on one physical fact: the dip recovers once the charge stops, and a draw does not. In `dhw_learning.py`, `ChargeSettle` (in memory) holds the open charge's transient:
- **Draw statistics.** A charge-affected interval (heated, or ending within `DHW_CHARGE_SETTLE_HOURS` of the last heated sample) is folded as on main, and `DrawStats` records that share of the open occurrence. A later unheated rise of the reading takes back what it recovered (`DrawStats.take_back`). The take-back is capped by the occurrence's charge-folded energy and by `DHW_CHARGE_DIP_MAX_K` (5 K, the top of the observed 3-5 K) per charge.
- **Usage learner.** A settle interval's drop is deferred instead of skipped. Later unheated rises cut it. The first unheated interval past the window that does not rise closes the charge and learns what is left.
- **Cooling learner.** Gated as on main, on a heated interval only. The first gate's settle-only extension was equivalent: such an interval is under `DHW_COOLING_MIN_SAMPLE_HOURS` by construction.
- **Restore refactor.** The author's `_restore_daytypes` fold of the two duplicated restore loops stays. `apply_payload` takes an overflowing day count as zero, as the loader does.

Design choices a reviewer may read as bugs:
- A heated rise is never credited, because it is charge heat. So a dip that recovers while the charge still heats stays booked, as on main. The harness's 40-min-charge geometry finds no such phantom at main: dip equals truth there.
- A draw that overlaps the recovery hides the rise, so the phantom stays as on main (draw-0745 dip, below).
- A restart forgets the open charge, so that charge is booked as on main. A take-back only reaches the occurrence still open, so a recovery that crosses into a new window or day takes back from the old occurrence in the crossing tick and nothing after it.
- An unheated rise after a charge that is not a dip (a device heating past its plan slot, since `dhw_heating_active` is the plan's flag and not device state) can erase at most `DHW_CHARGE_DIP_MAX_K` of charge-folded draw per charge, and never draw folded outside the charge.

Alternatives considered:
- (a) Fold the drop only where it exceeds the dip bound: this costs every real draw near a charge up to 5 K.
- (b) Keep the zero gate and only shorten the window: the draw-0735 truth arm still reads 0.14 kWh.
- (c) Persist `ChargeSettle`: a store field for one transient per restart.
- (d) Credit the standby loss on top of the observed rise in the take-back: removing that term moved every dip arm toward the truth trace and no truth arm (measured), so the credit is the reading's own rise.

## Head

Measured at code head `b6696bd6e6c671e52b3b2c16991011789d1d5e18` on merge base `a7628041dc02e298c5399003d4c0576391dd5c4e` (`origin/main` at measurement, 2026-11-11T10:16Z). Production files are byte-identical from `b5a0f8773aa4` to the head (`git diff b5a0f8773aa4 HEAD -- custom_components/` prints nothing). The harness figures were taken at `b5a0f8773aa4`; after that, only `tests/features.py` and the ledger changed.

## Mutation proof

Failing test first. The features block `a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked` (plus the restore check) was run with `dhw_learning.py` and `dhw_draws.py` from the merge base and the rest of the head. Values are (open-occurrence kWh, usage points[, closed day]):

```
main a7628041dc02:  FAIL  dip (0.6825, 1), edge (0.457, 1), draw (0.6825, 1), space (0.6825, 2), space draw (0.6825, 2), midnight (0.0, 0, [0.689]), reheat (0.689, 1) vs (0.689, 1), cap (1.849, 0)   -> 2 of 3 FEATURES BLOCK FAILED (+ the restore check: 'OverflowError')
old head 416afe9b2: FAIL  dip (0.0, 0), edge (0.0, 0), draw (0.0, 0), space (0.6825, 2), space draw (0.6825, 2), midnight (0.0, 0, [0.0]), reheat (0.689, 1) vs (0.689, 1), cap (0.0, 0)        -> 1 of 3 FEATURES BLOCK FAILED
head:               ok    dip (0.0, 0), edge (0.0, 0), draw (0.6825, 1), space (0.6825, 2), space draw (0.6825, 2), midnight (0.0, 0, [0.341]), reheat (0.689, 1) vs (0.689, 1), cap (0.689, 0) -> ALL 3 FEATURES BLOCK PASSED
```

So main fails on the dip and the old head fails on the draw: the check separates the defect from its over-correction. The heated-rise, partial-recovery and closed-charge arms were added after these runs, to kill HEATED_RETURN_OFF, PENDING_INDEX and CLOSE_KEEPS_OPEN below.

Mutants (run at `b5a0f8773aa4`, production identical to the head), each `{name, file, old, new}`, run by `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd "<CMD>"` (copy-tree) with CMD:

```
env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'from harness import FakeEntry as _r7d203_entry' --prelude 'import asyncio as _aio' --prelude 'from homeassistant.util import dt as dt_util' --prelude 'from datetime import timedelta' '# A charge start makes the tank reading FALL' '# A zero-capacity tank is the input'
```

| mutant | file | old | new |
|---|---|---|---|
| DIP_ZERO | dhw_learning.py | `DHW_CHARGE_DIP_MAX_K = 5.0` | `= 0.0` |
| DIP_SMALL | dhw_learning.py | `DHW_CHARGE_DIP_MAX_K = 5.0` | `= 1.0` |
| SETTLE_STRICT | dhw_learning.py | `<= DHW_CHARGE_SETTLE_HOURS` | `< DHW_CHARGE_SETTLE_HOURS` |
| SETTLE_SHORT | dhw_learning.py | `DHW_CHARGE_SETTLE_HOURS = 0.25` | `= 0.05` |
| SETTLE_LONG | dhw_learning.py | `DHW_CHARGE_SETTLE_HOURS = 0.25` | `= 0.5` |
| STAMP_DEL | dhw_learning.py | `self.last_heated_time = now` | `pass` |
| OPEN_OFF | dhw_learning.py | `self.open, self.credit_k = True, DHW_CHARGE_DIP_MAX_K` | `pass` |
| RISE_INCL_FLAT | dhw_learning.py | `if obs[1] < 0:` | `if obs[1] <= 0:` |
| CREDIT_DOUBLE | dhw_learning.py | `min(-obs[1], self.credit_k)` | `min(-2 * obs[1], self.credit_k)` |
| TAKE_CAP_OFF | dhw_learning.py | `taken = left = min(-obs[1], self.credit_k)` | `taken = left = -obs[1]` |
| PENDING_CUT_OFF | dhw_learning.py | `deferred[1] -= cut` | `pass` |
| PENDING_OFF | dhw_learning.py | `if settling:` + `self.pending.append(obs)` | `if False:` |
| FLUSH_OFF | dhw_learning.py | the deferred `await self.async_learn_usage(...)` | `pass` |
| USAGE_GATE_OFF | dhw_learning.py | `if not settling:` (before the usage call) | `if True:` |
| CHARGE_FLAG_OFF | dhw_learning.py | `charge=heated_interval or settling` | `charge=False` |
| RECOVERED_OFF | dhw_learning.py | `recovered_k=recovered_k` | `recovered_k=0.0` |
| COOLING_HEATED_OFF | dhw_learning.py | `if not heated_interval:` (cooling) | `if not heating:` |
| ESCROW_ADD_OFF | dhw_draws.py | `self._open_charge_kwh += energy` | `pass` |
| ESCROW_RESET_OFF | dhw_draws.py | `self._open_charge_kwh = 0.0` (new occurrence) | `pass` |
| TAKE_UNBOUNDED | dhw_draws.py | `taken = min(max(0.0, energy_kwh), self._open_charge_kwh)` | `taken = max(0.0, energy_kwh)` |
| TAKE_OPEN_OFF | dhw_draws.py | `self._open_kwh -= taken` | `pass` |
| OVERFLOW_DROP | dhw_learning.py | `except (TypeError, ValueError, OverflowError):` | `except (TypeError, ValueError):` |
| RESTORE_SKIP_OFF | dhw_learning.py | `else: continue` | `else: pass` |
| RESTORE_LEN_OFF | dhw_learning.py | `isinstance(arr, list) and len(arr) == 24` | `isinstance(arr, list)` |
| RESTORE_CLAMP_DROP | dhw_learning.py | `max(0, int(source.get(...)))` | `int(source.get(...))` |

```
SURVIVED NULL
KILLED DIP_ZERO
KILLED DIP_SMALL
KILLED SETTLE_STRICT
KILLED SETTLE_SHORT
KILLED SETTLE_LONG
KILLED STAMP_DEL
KILLED OPEN_OFF
KILLED RISE_INCL_FLAT
KILLED CREDIT_DOUBLE
KILLED TAKE_CAP_OFF
KILLED PENDING_CUT_OFF
KILLED PENDING_OFF
KILLED FLUSH_OFF
KILLED USAGE_GATE_OFF
KILLED CHARGE_FLAG_OFF
KILLED RECOVERED_OFF
KILLED COOLING_HEATED_OFF
KILLED ESCROW_ADD_OFF
KILLED ESCROW_RESET_OFF
KILLED TAKE_UNBOUNDED
KILLED TAKE_OPEN_OFF
KILLED OVERFLOW_DROP
KILLED RESTORE_SKIP_OFF
KILLED RESTORE_LEN_OFF
KILLED RESTORE_CLAMP_DROP
```

The `mutant_run.py --diff a7628041dc02...HEAD` sweep over the same CMD left three behaviour survivors at the time: the heated-interval return in `ChargeSettle.advance`, the deferred-drop index and the close's `open` reset. Three arms were added: a draw then charge heat, a 3 K settle drop that recovers 1 K, and a rise after the charge closed. Same CMD at the head:

```
SURVIVED NULL
KILLED HEATED_RETURN_OFF   (`if not self.open or heated_interval:` -> `if False:`)
KILLED PENDING_INDEX       (`deferred[1] -= cut` -> `deferred[2] -= cut`)
KILLED CLOSE_KEEPS_OPEN    (close sets `self.open` True)
```

The reviewer's two survivors are closed: R_SETTLE_STRICT is SETTLE_STRICT above, and R_FOLD_SKIP has no site left, because the fold is no longer gated.

Sites that only other `tests/features.py` checks pin were run over the whole script, in place (`mutant_run.py --in-place --spec <these> --cmd "env PYTHONPATH=tests/hastub python3 tests/features.py"`):

```
SURVIVED NULL
SURVIVED WEEKEND_GT       (`weekday() >= 5` -> `> 5`; killed in the block after the Saturday arm, below)
SURVIVED STANDBY_CLAMP    (`max(0.0, previous_temp - TANK_ROOM_AMBIENT_TEMP)` -> unclamped)
SURVIVED SAVE_GUARD_OFF   (the fold's save guard -> `if False:`; killed in the block after the save spy, below)
SURVIVED SAVE_TAKEN_OFF   (`or taken_kwh > 1e-4` -> `or False`; same)
KILLED RESTORE_RESET_OFF
```

That run, at `fa2e180ee`, hit its 3000 s bound before its last mutant. That mutant was run alone at the head:

```
SURVIVED NULL
KILLED RESTORE_POOLED_OFF
```

The NULL line is the whole of `tests/features.py` passing at the head. The block then gained a Saturday arm and a save spy (the last save must hold the final open kWh). Same block CMD at the head:

```
SURVIVED NULL
KILLED WEEKEND_GT
KILLED SAVE_GUARD_OFF
KILLED SAVE_TAKEN_OFF
KILLED FLUSH_WEEKEND      (the deferred usage's `weekend=wkend` -> `weekend=False`)
```

## Null control

- **Space-heating start.** The learner's only heating input is the plan's `dhw_heating_active` flag, so in the block a compressor start for space heating (flag never set) learns the dip and the draw exactly as main does, at both ends: `(0.6825, 2)` main and head.
- **Harness flat arm.** The harness's `flat` arm (the same reheat, flag never set, no dip) is bit-identical across base, old head and head in all six geometries.
- **Harness truth arm.** The `truth` arm (no dip) is bit-identical between base and head in every geometry and at the cooling-rate clamp. That is the measure that no real draw is lost.

## Figures

**Every figure the diff changes** (class repair). These are the heavy-day p90 and occurrence count (`DrawStats.quantile`, `DrawStats.count`), the usage-profile update count and its hour-7 weight, and the cooling rate. They come from `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_dhw_charge_settle_p90.py` (sha1 `24cfb411cf98c620a321bc8a9e3d32cc7beb18e3`, this branch's harness extended with draw geometries and charge length). It was run from a `git archive` of the merge base (B), of the previous head `416afe9b2` (O) and at the head (N). The run is 28 days of 5-min samples, seed 3434, a 15-min draw a day at the named start, and a charge at 07:30 (10 min; `long-` 40 min). Columns are (usage points, profile[7], cooling rate, (occurrences, p90 kWh)):

```
geometry   arm        B                               O                               N
draw-0700  dip        112 3.5 0.3 (27, 6.1506)        84 3.5 0.3 (27, 5.5307)         84 3.5 0.3 (27, 5.5307)
draw-0700  truth      84 3.5 0.3 (27, 5.5346)         84 3.5 0.3 (27, 5.5326)         84 3.5 0.3 (27, 5.5346)
draw-0700  dip@max    112 3.5 3.0 (27, 5.8376)        84 3.5 3.0 (27, 5.3169)         84 3.5 3.0 (27, 5.3169)
draw-0700  truth@max  84 3.5 3.0 (27, 5.3169)         84 3.5 3.0 (27, 5.3169)         84 3.5 3.0 (27, 5.3169)
draw-0735  dip        28 3.5 0.3 (27, 4.3651)         0 2.5658 0.3 (27, 0.1428)       18 3.5 0.3 (27, 3.4478)
draw-0735  truth      28 3.5 0.3 (27, 3.6706)         0 2.5658 0.3 (27, 0.1438)       28 3.5 0.3 (27, 3.6706)
draw-0735  dip@max    28 3.5 3.0 (27, 4.1919)         0 2.5658 3.0 (27, 0.0)          18 3.4182 3.0 (27, 3.2746)
draw-0735  truth@max  28 3.5 3.0 (27, 3.5094)         0 2.5658 3.0 (27, 0.0)          28 3.5 3.0 (27, 3.5094)
draw-0745  dip        82 3.5 0.3 (27, 5.7055)         27 3.5 0.3 (27, 1.7143)         82 3.5 0.3 (27, 5.7055)
draw-0745  truth      84 3.5 0.3 (27, 5.5488)         28 3.5 0.3 (27, 1.9468)         84 3.5 0.3 (27, 5.5488)
draw-0745  dip@max    82 3.5 3.0 (27, 5.3865)         27 3.5 3.0 (27, 1.5469)         82 3.5 3.0 (27, 5.3865)
draw-0745  truth@max  84 3.5 3.0 (27, 5.267)          28 3.5 3.0 (27, 1.7719)         84 3.5 3.0 (27, 5.267)
draw-0800  dip        110 3.5 0.3 (27, 5.7049)        82 2.3897 0.3 (27, 5.0852)      82 2.3897 0.3 (27, 5.2534)
draw-0800  truth      84 2.3897 0.3 (27, 5.549)       84 2.3897 0.3 (27, 5.5487)      84 2.3897 0.3 (27, 5.549)
draw-0800  dip@max    110 3.5 3.0 (27, 5.3166)        82 2.3897 3.0 (27, 4.8116)      82 2.3897 3.0 (27, 4.8651)
draw-0800  truth@max  84 2.3897 3.0 (27, 5.2686)      84 2.3897 3.0 (27, 5.2686)      84 2.3897 3.0 (27, 5.2686)
long-0700  dip        84 3.5 0.3 (27, 5.4999)         84 3.5 0.3 (27, 5.4987)         84 3.5 0.3 (27, 5.4999)
long-0700  truth      84 3.5 0.3 (27, 5.4999)         84 3.5 0.3 (27, 5.4987)         84 3.5 0.3 (27, 5.4999)
long-0745  dip        0 2.5658 0.3 (27, 1.3511)       0 2.5658 0.3 (27, 0.1025)       0 2.5658 0.3 (27, 1.3511)
long-0745  truth      0 2.5658 0.3 (27, 1.4156)       0 2.5658 0.3 (27, 0.1025)       0 2.5658 0.3 (27, 1.4156)
flat (every geometry, both rates): identical B = O = N
long-* @max arms: B = N in every column
```

How to read it:
- **Truth arms.** N equals B in every geometry, so no real draw is lost. O lost 65 to 100 % of the p90 at draw-0735 and draw-0745, and 93 % at long-0745.
- **Dip arms against truth.** At draw-0700 the phantom is removed: 6.1506 at B to 5.5307 at N, with truth 5.5346. At draw-0735 the error shrinks: B +0.69, N −0.22. At draw-0745 nothing changes (B = N = 5.7055): the draw overlaps the recovery and hides the rise, which is the named residual. At draw-0800 the error is B +0.16 and N −0.30: the recovery's tail lands inside the draw intervals and masks part of the draw, after the visible rise has taken the phantom back. That is the one geometry where N's absolute error exceeds B's, though it remains nearer the truth than O's −0.46. Occurrence counts are 27 everywhere.
- **Cooling rate.** It moves in no arm at any end. The harness's 5-min cadence never reaches `DHW_COOLING_MIN_SAMPLE_HOURS`, and the cooling gate is main's `heated_interval` again (`COOLING_HEATED_OFF` killed), so the diff leaves the cooling figure as main computes it.
- **Usage hour-7 weight.** At draw-0735 the dip@max arm reads 3.4182 at N against 3.5 at B. That is the deferred settle drop learned after its partial recovery, and the truth arm reads 3.5 at both ends.

**Re-derivation of the reviewer's table.** The reviewer's draw offsets are the `draw-0700`, `draw-0735`, `draw-0745` and `draw-0800` truth rows above. The values at B and O match the verdict's base and head columns: 5.5346/5.5326, 3.6706/0.1438 (verdict 0.1438), 5.5488/1.9468 and 5.5490/5.5487.

Structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, with `class_excess_loc` and `functions_cc_over_15` at their recorded values. The budget file's only change against the merge base is the `class_excess_loc` row, down (17537 to 17535), and `recorded_at`, both carried from the previous round's re-record. The new class-span lines were paid by moving the transient's bookkeeping out of `DhwProfileLearner` into `ChargeSettle`, by a `_standby_rate` helper replacing the two copies of the standby expression in the fold and the usage learner, and by the author's restore fold. No budget was raised.

Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0237 IMPROVES`, with lines `literal_clone_copies 122 -> 120`, `reflective_writes 11 -> 10 (gate only)` and `computed_attr_access 28 -> 27 (gate only)`. This corrects the previous body's 9 and 26.

Class seams (`fixer.md` step 8). The class: a tank-temperature drop attributed to consumption while a charge drives the reading. Enumerator: `git grep -n "dhw_heating_active\|_heating_active()" -- custom_components/` and `git grep -n "async_learn_dynamics\|CONF_DHW_TEMP_ENTITY\|draw_stats.fold" -- custom_components/`. Dispositions:
- `dhw_learning.py` `async_learn_dynamics`, the one reader of the learner's heating flag, and its consumers `async_learn_cooling` (main's gate, unchanged), `async_learn_usage` and `async_fold_draw_stats`: closed in this diff. `draw_stats.fold` has one production caller, the fold.
- `coordinator.py` `_dhw_probe_temperature` and the DHW lead-prediction record: these compare the plan's promised tank temperature with the reading. A dip there is a real miss of the promise, not a consumption attribution, so it is outside the class.
- `boost.py`, `optimizer.py`, `payload.py`, `climate.py`, `sensor.py`, `coordinator.py` (the `dhw_heating_active` writes and publication), `device_prefill.py`, `modbus_prefill.py`, `name_match.py`, `topology.py` and `thermal_model.py` (configuration and display): no drop attribution.

Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`, run on the tree of `b5a0f8773aa4` plus the ledger deletions, printed `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN`. Later commits touch only `tests/features.py`; its whole-script run at the head is the NULL line of the in-place mutant run above. `python3 tests/typing_ruler.py` reads `ALL 12 typing-ruler source checks PASSED`. `tools/pr/ci_predict.py` reads `no closures, fast, governance or instrument red predicted`, after the five STALE PIN ledger files it named were deleted (pins on lines this diff rewrote).

## Unpinned sites

Each site `tools/pr/ci_predict.py` lists as ADDED UNPINNED is in `custom_components/`, so `mutation-autofix` pins it after the push (its lane mutates `custom_components/`). The value check named is the spec mutant above that is killed at the same site.

- custom_components/heatpump_optimizer/dhw_draws.py:82 CLAMP_DROP: pinned by `mutation-autofix`. This is main's own `fold` clamp, `max(0.0, float(energy_kwh))`, moved into a local; no added mutant targets it.
- custom_components/heatpump_optimizer/dhw_draws.py:84 GUARD_OFF: pinned by `mutation-autofix`; value check ESCROW_ADD_OFF.
- custom_components/heatpump_optimizer/dhw_draws.py:95 CLAMP_DROP*2: pinned by `mutation-autofix`; value check TAKE_UNBOUNDED.
- custom_components/heatpump_optimizer/dhw_draws.py:98 RETURN_DEL: pinned by `mutation-autofix`; value check SAVE_TAKEN_OFF (the save reads the returned amount).
- custom_components/heatpump_optimizer/dhw_learning.py:77 CONST: pinned by `mutation-autofix`; value checks DIP_ZERO and DIP_SMALL.
- custom_components/heatpump_optimizer/dhw_learning.py:102 GUARD_OFF: pinned by `mutation-autofix`; value check STAMP_DEL.
- custom_components/heatpump_optimizer/dhw_learning.py:118 BOOLOP: pinned by `mutation-autofix`; value check OPEN_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:118 GUARD_OFF: pinned by `mutation-autofix`; value check OPEN_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:120 GUARD_OFF: pinned by `mutation-autofix`; value check HEATED_RETURN_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:122 CMP_BOUND: pinned by `mutation-autofix`; value check RISE_INCL_FLAT.
- custom_components/heatpump_optimizer/dhw_learning.py:122 GUARD_OFF: pinned by `mutation-autofix`; value checks RECOVERED_OFF and CREDIT_DOUBLE.
- custom_components/heatpump_optimizer/dhw_learning.py:123 CLAMP_DROP: pinned by `mutation-autofix`; value check TAKE_CAP_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:126 CLAMP_DROP*2: pinned by `mutation-autofix`; value checks PENDING_CUT_OFF and PENDING_INDEX.
- custom_components/heatpump_optimizer/dhw_learning.py:129 RETURN_DEL: pinned by `mutation-autofix`; value check RECOVERED_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:130 GUARD_OFF: pinned by `mutation-autofix`; value check PENDING_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:132 RETURN_DEL: pinned by `mutation-autofix`; value check PENDING_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:134 RETURN_DEL: pinned by `mutation-autofix`; value check FLUSH_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:443 CMP_BOUND: pinned by `mutation-autofix`; value checks WEEKEND_GT and FLUSH_WEEKEND (the Saturday arm).
- custom_components/heatpump_optimizer/dhw_learning.py:450 GUARD_OFF: pinned by `mutation-autofix`; value check COOLING_HEATED_OFF (the cooling arm).
- custom_components/heatpump_optimizer/dhw_learning.py:452 GUARD_OFF: pinned by `mutation-autofix`; value check USAGE_GATE_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:466 CLAMP_DROP: pinned by `mutation-autofix`. This is main's standby expression, which main's ledger recorded killed at both former sites (`async_learn_usage` and `async_fold_draw_stats` CLAMP_DROP `145fdc23`, deleted here as STALE PIN). Over the whole of `tests/features.py` in place it survives (`SURVIVED STANDBY_CLAMP`), so its killer is another gate script, which the lane's suite run finds.
- custom_components/heatpump_optimizer/dhw_learning.py:490 CLAMP_DROP: pinned by `mutation-autofix`. This is main's own fold clamp beside the helper call; it is killed in the `--diff` sweep (absent from its SURVIVED lines).
- custom_components/heatpump_optimizer/dhw_learning.py:506 CMP_BOUND*2: pinned by `mutation-autofix`. Value check SAVE_TAKEN_OFF covers the take-back arm. The `energy_kwh > 1e-4` bound is main's; it survives the block and the whole script, as it would at main, which has no check at a 1e-4 kWh tick.
- custom_components/heatpump_optimizer/dhw_learning.py:506 GUARD_OFF: pinned by `mutation-autofix`; value check SAVE_GUARD_OFF.

The five `killed_by` ledger pins this diff deletes are `async_fold_draw_stats` CLAMP_DROP `145fdc23` and `1b2910c6`, `async_learn_dynamics` GUARD_OFF `214cab0c` and `7f619379`, and `async_learn_usage` CLAMP_DROP `145fdc23`. They name lines this diff rewrote, and `ci_predict.py` predicted each a STALE PIN red on `ledger`; the deletion repairs it.

## Red checks

- `mutation` and `tests / mutation` at 416afe9b2 (the PR's current head, before this push): red by construction on the sites the added lines leave unpinned, the 24 listed under `## Unpinned sites` at this head. `mutation-autofix` pins killed sites after the push (`ci-autofix.md`). Root-cause answer: the cheaper detector already ran. `tools/pr/ci_predict.py` (prepr step 6d) named every site locally before the handoff, at no added standing cost. The red is the pin-recording step and not an escaped defect, so no further countermeasure is owed.

## Forward-carry

none

## Friction

none
