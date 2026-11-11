R10-OUTSIDE-DHW-CHARGE-SETTLE: the build of outside pull request #3434 by @Bankaifan, whose commit opens this branch with its authorship kept. A DHW charge start drops the tank reading 3-5 K within minutes. Main books that dip as a draw on the heated interval in the draw statistics, and as usage on the unheated intervals after a short charge. Both inflate the heavy-day p90 that the planner reads through `DrawStats.quantile`.

Repair round 3. Review blocked `8fe714779` as regression-unmeasured. At the learner's production cadence, the take-back erased real draw. The learner runs once per coordinator refresh, `optimization_interval`: 30 min by default, 10-120 min in 5-min steps. Every harness arm and test sampled at 5 min. The cause: the interval that *ends* at the first heated sample was folded as charge energy. At a 10-120 min refresh that interval holds the draw made before the charge. A later dip recovery then took that draw back.

The fix rests on one physical fact: the dip recovers once the charge stops, and a draw does not. In `dhw_learning.py`, `ChargeSettle` (in memory) holds the open charge's transient:
- **Draw statistics.** `ChargeSettle.classify` now returns the interval's class. Only an interval that *started* on a heated sample, or ends within `DHW_CHARGE_SETTLE_HOURS` of the last heated sample (settling), is folded as charge energy (`DrawStats.fold(..., charge=True)`). The plan's flag marks the charge no earlier than its slot, so an interval ending at the first heated sample holds the pre-charge draw. It is folded as plain draw, which no take-back reaches. A later unheated rise takes back what it recovered (`DrawStats.take_back`). Two caps bound it: the charge-folded energy left in the open occurrence, and `DHW_CHARGE_DIP_MAX_K` (5 K) per charge.
- **Usage learner.** A settle interval's drop is deferred instead of skipped. Later unheated rises cut it. The first unheated interval past the window that does not rise closes the charge and learns what is left. This part is unchanged this round.
- **Cooling learner.** Gated as on main, on a heated interval (starts or ends heated).
- **Restore refactor.** The author's `_restore_daytypes` fold of the two duplicated restore loops stays. `apply_payload` takes an overflowing day count as zero, as the loader does.

Design choices a reviewer may read as bugs:
- A heated rise is never credited, because it is charge heat. So a dip that recovers while the charge still heats stays booked, as on main.
- A draw that overlaps the recovery hides the rise, so the phantom stays as on main (draw-0745 dip, below).
- A restart forgets the open charge, so that charge is booked as on main. A take-back only reaches the occurrence still open.
- A real draw *during* a charge is folded as charge energy, and a later dip recovery can take it back. The charge heat that hid part of the dip makes the recovery larger than the dip the charge folded. This is measured below (5-min draw-0735: −0.30, against main's +0.39). At every production cadence, 10 to 60 min, no dip cell reads further from its truth arm than main.
- At 10, 15 and 60 min the fix removes none of main's phantom (N equals B in every dip cell). There the dip lands inside a heated interval, or past a settle window shorter than the refresh. The gain at production cadence is the 30-min draw-0735 and draw-0745 cells, +0.23 to +0.01. Every other production cell reads as main.

Alternatives considered:
- (a) Fold the drop only where it exceeds the dip bound: this costs every real draw near a charge up to 5 K.
- (b) Lengthen `DHW_CHARGE_SETTLE_HOURS` to the refresh interval, so the settle window catches the dip at 30-60 min: that widens the window that defers real usage. With no production trace at those cadences, I did not measure it and did not take it.
- (c) Persist `ChargeSettle`: a store field for one transient per restart.

## Head

Code head `d6564e1eab08df8dadc088a696a211a291172db3`, on merge base `ee64358be7eeccaec5178a923cb3b83a18a924a0` (`origin/main` at measurement, 2026-11-11T15:33Z). It continues the PR head `8fe714779` (O below) with two commits. The first is the escrow gate, the cadence harness and the features cases. The second moves the interval classification into `ChargeSettle.classify`, which pays its class lines. `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main was not merged.

## Mutation proof

Failing test first. Two checks were added to the block: `at the learner's production cadences a charge-start dip's recovery takes back no draw made before the charge` (10, 15 and 30 min) and `a charge's take-back stops at the energy its charge folded and at the dip bound`. The same block CMD (below) was run with the rest of the head and with three versions of `dhw_learning.py`/`dhw_draws.py`. Values are cadence: (dip open kWh, truth with no dip, no DHW charge on record):

```
main ee64358be:     FAIL  {10: (1.3656, 0.6821, 1.3656), 15: (1.3523, 0.6751, 1.3523), 30: (1.3127, 0.6542, 1.3127)}   -> 4 of 5 FEATURES BLOCK FAILED
old head 8fe714779: FAIL  {10: (0.4376, 0.6821, 1.3656), 15: (0.4243, 0.6751, 1.3523), 30: (0.3847, 0.6542, 1.3127)}   -> 1 of 5 FEATURES BLOCK FAILED
head:               ok                                                                                                  -> ALL 5 FEATURES BLOCK PASSED
```

The 30-min old-head row reproduces the verdict's sequence exactly (0.3847 against truth 0.6542, control 1.3127). Main fails because it keeps the phantom, and the old head fails because it erases the draw. The second check fails at main on both arms (`esc` 0.9148 against 0.689, `cap3` 1.849 against 0.6825). It passes at the old head and pins the reviewer's two surviving mutants (below).

Mutants, each `{name, file, old, new}`, run at `d6564e1ea` by `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd "<CMD>"` (copy-tree) with CMD:

```
env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'from harness import FakeEntry as _r7d203_entry' --prelude 'import asyncio as _aio' --prelude 'from homeassistant.util import dt as dt_util' --prelude 'from datetime import timedelta' '# A charge start makes the tank reading FALL' '# A zero-capacity tank is the input'
```

This round's mutants:

| mutant | file | old | new |
|---|---|---|---|
| STARTED_GATE_OFF (the fix reverted) | dhw_learning.py | `charge=started_heated or settling` | `charge=heated_interval or settling` |
| STARTED_IS_NOW | dhw_learning.py | `started_heated = self.heating_since_sample` | `started_heated = heating` |
| STARTED_DROP | dhw_learning.py | `heated_interval = started_heated or heating` | `heated_interval = heating` |
| R2_ESCROW_DEC_OFF (reviewer's) | dhw_draws.py | `self._open_charge_kwh -= taken` | `pass` |
| R2_CREDIT_PER_INTERVAL (reviewer's) | dhw_learning.py | `if (heated_interval or settling) and not self.open:` | `if heated_interval or settling:` |

The earlier rounds' 32 mutants were re-run over the same CMD at this head. They are the 25-row table of round 2, `HEATED_RETURN_OFF`, `PENDING_INDEX`, `CLOSE_KEEPS_OPEN`, `WEEKEND_GT`, `SAVE_GUARD_OFF`, `SAVE_TAKEN_OFF` and `FLUSH_WEEKEND`. `CHARGE_FLAG_OFF`'s old text is now `charge=started_heated or settling`. Each spec `old` text matched exactly once in its file before the run.

```
SURVIVED NULL
KILLED STARTED_GATE_OFF
KILLED STARTED_IS_NOW
KILLED STARTED_DROP
KILLED R2_ESCROW_DEC_OFF
KILLED R2_CREDIT_PER_INTERVAL
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
KILLED PENDING_INDEX
KILLED PENDING_OFF
KILLED HEATED_RETURN_OFF
KILLED CLOSE_KEEPS_OPEN
KILLED FLUSH_OFF
KILLED FLUSH_WEEKEND
KILLED USAGE_GATE_OFF
KILLED CHARGE_FLAG_OFF
KILLED RECOVERED_OFF
KILLED COOLING_HEATED_OFF
KILLED WEEKEND_GT
KILLED SAVE_GUARD_OFF
KILLED SAVE_TAKEN_OFF
KILLED ESCROW_ADD_OFF
KILLED ESCROW_RESET_OFF
KILLED TAKE_UNBOUNDED
KILLED TAKE_OPEN_OFF
KILLED OVERFLOW_DROP
KILLED RESTORE_SKIP_OFF
KILLED RESTORE_LEN_OFF
KILLED RESTORE_CLAMP_DROP
```

The reviewer's third survivor, `R2_SETTLE_INCL_HEATED`, has no site left. `classify` now returns `heated_interval` beside the settle flag, and the verdict read that mutant as equivalent: on a heated interval the usage learner returns at its first guard, and `advance` returns before the pending branch.

The `mutant_run.py --diff ee64358be...HEAD --path custom_components/` sweep over the same CMD at `d6564e1ea` prints its survivors only. None of them is on a line this round changed (`classify`, the `started_heated` lines, the fold's `charge=`):

```
SURVIVED dhw_draws.py:60 CONST_SWAP  _open_charge_kwh: float = 1.0
SURVIVED dhw_draws.py:65 CONST_SWAP  ... *, charge: bool = True
SURVIVED dhw_learning.py:96 CONST_SWAP  credit_k: float = 1.0
SURVIVED dhw_learning.py:264 CALL_DEL / CONST_SWAP  self._restore_daytypes(stored, reset_missing=...)
SURVIVED dhw_learning.py:348 CALL_DEL, 349 GUARD_OFF, 350 CALL_DEL  (_restore_daytypes' reset_missing branch)
SURVIVED dhw_learning.py:476 CONST_SWAP  * max(1.0, previous_temp - TANK_ROOM_AMBIENT_TEMP)
SURVIVED dhw_learning.py:482 CONST_SWAP  recovered_k: float = 1.0
SURVIVED dhw_learning.py:516 CMP_BOUND / CONST_SWAP  energy_kwh > 1e-4
```

Dispositions, by reading:
- Lines 65, 96 and 482 are defaults that every production call overrides. `fold`'s only caller passes `charge=`, `advance` sets `credit_k` before any read, and the fold's only caller passes `recovered_k=`.
- Line 60 is the escrow's initial value. A live occurrence resets it on its first fold. A `DrawStats.from_dict` restore keeps the default, so after a restart mid-occurrence a charge could take back up to 1 kWh more under the mutant. No arm drives a restart mid-charge. This is a real unpinned site, and it is listed under `## Unpinned sites`.
- Lines 264 and 348-350 are the loader's day-type reset. Round 2's in-place run over the whole of `tests/features.py` killed it (`RESTORE_RESET_OFF`, `RESTORE_POOLED_OFF`); the block CMD does not reach it.
- Line 476 is main's standby clamp (round 2's `STANDBY_CLAMP`). Its killer is another gate script, as main's ledger records.
- Line 516 is main's `1e-4` save bound, unpinned at main too.

## Null control

- **Truth and flat arms.** The harness's `truth` (no dip) and `flat` (the same reheat, flag never set, no dip) arms, including `truth@max`, are byte-identical at B, O and N: 105 lines in all, at every cadence and geometry. The command extracts those arms from each end's output and compares the files: `grep -E " (truth|flat|truth@max) " <end>.txt > ctl_<end>.txt; cmp ctl_base.txt ctl_head.txt && cmp ctl_base.txt ctl_fix.txt && echo "CONTROLS IDENTICAL B=O=N"`, and it printed the echo. The dip arms do differ (`cmp -s` of the dip lines B against N is non-zero), so the comparison is not blind.
- **Space-heating start.** In the block, a compressor start for space heating (the plan's DHW flag never set) learns the dip and the draw exactly as main does. That is the `space` arms, and the no-charge column of the cadence check, which reads main's value at every cadence.
- **Take-back reach.** A probe (scratch, not in the tree) wraps `DrawStats.take_back` to sum what it removes. In the harness at 5 min, the truth arm's take-back is 0.0000 kWh/day at draw-0800 and at an isolated-dip geometry (draw at 20:00). The dip arm's take-back is 0.3152 kWh/day at draw-0800 and 0.3162 at the isolated dip, and its p90 at the isolated dip is 5.5056 against truth 5.5066 (main 5.8151). So at draw-0800 the take-back removes the dip's phantom and nothing more. That cell's N error of −0.46 is the recovery's tail masking the draw, which main has too, hidden behind its +0.31 phantom.

## Figures

**Every figure the diff changes** (class repair) is the heavy-day p90 and occurrence count (`DrawStats.quantile`, `DrawStats.count`) and the usage-profile update count. They come from `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_dhw_charge_settle_p90.py` (sha1 `4986de6ed314db8be50189d4816c41823344ad8e`). The harness has a new argument this round: the tank is integrated per minute, and the learner is sampled at each of `CADENCES_MIN`, 5 (a sub-production control), 10, 15, 30 and 60 min. A `draw-0720` geometry was added. Each end ran the same harness copy from a `git archive` of the merge base (B), of the old head `8fe714779` (O), and at the head (N). The runs cover 28 days, seed 3434, a 15-min draw a day at the named start, and a charge at 07:30 (10 min; `long-` 40 min). Rows are the `dip` arm against its own `truth` arm, as p90 kWh (usage points), then the error against truth at B, O and N. The `@max` arms (cooling rate at `DHW_COOLING_RATE_MAX`) move exactly as their `dip` row and are in the harness output.

```
5min draw-0700 dip truth 5.5312 B 5.8384 (140) O 5.5282 (112) N 5.5282 (112) err vs own truth +0.3072 -0.0030 -0.0030
5min draw-0720 dip truth 3.1454 B 3.4527 (84) O 2.5479 (56) N 3.1423 (56) err vs own truth +0.3073 -0.5975 -0.0031
5min draw-0735 dip truth 3.7102 B 4.0975 (55) O 3.407 (54) N 3.407 (54) err vs own truth +0.3873 -0.3032 -0.3032
5min draw-0745 dip truth 5.5475 B 5.1628 (109) O 5.1628 (109) N 5.1628 (109) err vs own truth -0.3847 -0.3847 -0.3847
5min draw-0800 dip truth 5.5436 B 5.3892 (117) O 5.0799 (89) N 5.0799 (89) err vs own truth -0.1544 -0.4637 -0.4637
5min long-0700 dip truth 5.4953 B 5.4953 (112) O 5.4953 (112) N 5.4953 (112) err vs own truth +0.0000 +0.0000 +0.0000
5min long-0745 dip truth 1.5584 B 1.4066 (0) O 1.4066 (0) N 1.4066 (0) err vs own truth -0.1518 -0.1518 -0.1518
10min draw-0700 dip truth 5.4586 B 5.5364 (112) O 5.5364 (112) N 5.5364 (112) err vs own truth +0.0778 +0.0778 +0.0778
10min draw-0720 dip truth 3.0908 B 3.1695 (56) O 3.1695 (56) N 3.1695 (56) err vs own truth +0.0787 +0.0787 +0.0787
10min draw-0735 dip truth 3.3111 B 3.3892 (28) O 3.3892 (28) N 3.3892 (28) err vs own truth +0.0781 +0.0781 +0.0781
10min draw-0745 dip truth 5.4429 B 5.0581 (55) O 5.0581 (55) N 5.0581 (55) err vs own truth -0.3848 -0.3848 -0.3848
10min draw-0800 dip truth 5.4373 B 4.9241 (85) O 4.9241 (85) N 4.9241 (85) err vs own truth -0.5132 -0.5132 -0.5132
10min long-0700 dip truth 5.4537 B 5.4537 (84) O 5.4537 (84) N 5.4537 (84) err vs own truth +0.0000 +0.0000 +0.0000
10min long-0745 dip truth 1.4387 B 1.1414 (0) O 1.1414 (0) N 1.1414 (0) err vs own truth -0.2973 -0.2973 -0.2973
15min draw-0700 dip truth 5.4852 B 5.4825 (2585) O 5.4825 (2585) N 5.4825 (2585) err vs own truth -0.0027 -0.0027 -0.0027
15min draw-0720 dip truth 3.1136 B 3.1118 (2575) O 2.2186 (2575) N 3.1118 (2575) err vs own truth -0.0018 -0.8950 -0.0018
15min draw-0735 dip truth 1.8922 B 2.1256 (2499) O 2.1256 (2499) N 2.1256 (2499) err vs own truth +0.2334 +0.2334 +0.2334
15min draw-0745 dip truth 5.1394 B 4.4439 (2363) O 4.4439 (2363) N 4.4439 (2363) err vs own truth -0.6955 -0.6955 -0.6955
15min draw-0800 dip truth 5.4975 B 4.9046 (2356) O 4.9046 (2356) N 4.9046 (2356) err vs own truth -0.5929 -0.5929 -0.5929
15min long-0700 dip truth 5.4842 B 5.4842 (2589) O 5.4842 (2589) N 5.4842 (2589) err vs own truth +0.0000 +0.0000 +0.0000
15min long-0745 dip truth 1.3924 B 0.699 (2575) O 0.699 (2575) N 0.699 (2575) err vs own truth -0.6934 -0.6934 -0.6934
30min draw-0700 dip truth 4.3169 B 4.3166 (1283) O 4.1194 (1283) N 4.3166 (1283) err vs own truth -0.0003 -0.1975 -0.0003
30min draw-0720 dip truth 3.0712 B 3.0703 (1259) O 2.8731 (1259) N 3.0703 (1259) err vs own truth -0.0009 -0.1981 -0.0009
30min draw-0735 dip truth 1.8512 B 2.0823 (1214) O 1.8629 (1214) N 1.8629 (1214) err vs own truth +0.2311 +0.0117 +0.0117
30min draw-0745 dip truth 2.2703 B 2.5009 (1142) O 2.2759 (1142) N 2.2759 (1142) err vs own truth +0.2306 +0.0056 +0.0056
30min draw-0800 dip truth 5.0558 B 4.8251 (1166) O 4.8251 (1166) N 4.8251 (1166) err vs own truth -0.2307 -0.2307 -0.2307
30min long-0700 dip truth 4.4666 B 4.4666 (1283) O 4.4666 (1283) N 4.4666 (1283) err vs own truth +0.0000 +0.0000 +0.0000
30min long-0745 dip truth 0.0631 B 0.2459 (1259) O 0.2459 (1259) N 0.2459 (1259) err vs own truth +0.1828 +0.1828 +0.1828
60min draw-0700 dip truth 0.3589 B 0.3586 (643) O 0.3586 (643) N 0.3586 (643) err vs own truth -0.0003 -0.0003 -0.0003
60min draw-0720 dip truth 0.021 B 0.0198 (618) O 0.0198 (618) N 0.0198 (618) err vs own truth -0.0012 -0.0012 -0.0012
60min draw-0735 dip truth 1.2103 B 1.441 (603) O 1.441 (603) N 1.441 (603) err vs own truth +0.2307 +0.2307 +0.2307
60min draw-0745 dip truth 1.5877 B 1.82 (568) O 1.82 (568) N 1.82 (568) err vs own truth +0.2323 +0.2323 +0.2323
60min draw-0800 dip truth 5.0086 B 4.7793 (586) O 4.7793 (586) N 4.7793 (586) err vs own truth -0.2293 -0.2293 -0.2293
60min long-0700 dip truth 0.3572 B 0.3572 (643) O 0.3572 (643) N 0.3572 (643) err vs own truth +0.0000 +0.0000 +0.0000
60min long-0745 dip truth 0.0211 B 0.0211 (615) O 0.0211 (615) N 0.0211 (615) err vs own truth +0.0000 +0.0000 +0.0000
```

The rule for "real draw survives": for each cadence, count the dip cells (dip and dip@max, 14 per cadence) where an end's absolute error against its truth arm exceeds B's by more than 1e-4. `worse.py` (scratch) prints this per end:

```
O 5min: further than B 4, nearer 4 of 14     N 5min: further than B 2, nearer 6 of 14   (draw-0800 dip and dip@max, the masking above)
O 10min: further than B 0, nearer 0 of 14    N 10min: further than B 0, nearer 0 of 14
O 15min: further than B 2, nearer 0 of 14    N 15min: further than B 0, nearer 0 of 14
O 30min: further than B 4, nearer 4 of 14    N 30min: further than B 0, nearer 4 of 14
O 60min: further than B 0, nearer 0 of 14    N 60min: further than B 0, nearer 0 of 14
```

The O rows are the rule's own control: it finds the verdict's regression at 15 min (draw-0720, −0.0018 to −0.8950) and at 30 min (draw-0700 and draw-0720, about −0.20). The verdict's 15-min figure (1.8777 to 0.9868 kWh) came from the reviewer's own simulation, which is not in the tree. This harness reproduces the same cell, a draw starting 10 min before a 07:30 10-min charge, as 3.1118 to 2.2186 against truth 3.1136. The verdict's 30-min sequence is reproduced exactly by the features check above.

Structure ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. The first commit read `FAIL class_excess_loc 17537 > 17532 (+5)`: a comment and a local inside `DhwProfileLearner`. The second commit paid it by moving the interval classification into `ChargeSettle.classify`, outside that class. The budget file's change against the merge base is the `class_excess_loc` row, down, and `recorded_at`, both carried from the earlier rounds. No budget was raised.

Architecture score: `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` at `d6564e1ea` prints `Architecture score: dS +0.0237 IMPROVES`, with lines `literal_clone_copies 122 -> 120`, `reflective_writes 11 -> 10 (gate only)` and `computed_attr_access 28 -> 27 (gate only)`.

Class seams (`fixer.md` step 8). The class: a tank-temperature drop attributed to consumption while a charge drives the reading. Enumerators: `git grep -n "dhw_heating_active\|_heating_active()" -- custom_components/` and `git grep -n "async_learn_dynamics\|CONF_DHW_TEMP_ENTITY\|draw_stats.fold" -- custom_components/`. Dispositions:
- `dhw_learning.py` `async_learn_dynamics`, the one reader of the learner's heating flag, and its consumers `async_learn_cooling`, `async_learn_usage` and `async_fold_draw_stats`: closed in this diff. `draw_stats.fold` has one production caller, the fold.
- `coordinator.py` `_dhw_probe_temperature` and the DHW lead-prediction record: these compare the plan's promised tank temperature with the reading. A dip there is a real miss of the promise, not a consumption attribution, so it is outside the class.
- `boost.py`, `optimizer.py`, `payload.py`, `climate.py`, `sensor.py`, `coordinator.py` (the `dhw_heating_active` writes and publication), `device_prefill.py`, `modbus_prefill.py`, `name_match.py`, `topology.py` and `thermal_model.py` (configuration and display): no drop attribution.
- `config_flow.py` and `const.py` (the second enumerator's hits: the DHW temperature entity's key, form field and staleness/plausibility tables): definitions only, no drop attribution.

Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` At `d6564e1ea`, `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` printed `1 TEST SCRIPT(S) FAILED`. The one failed script is `tests/features.py`, with `1 of 5242 FEATURE CHECKS FAILED`. That check is main's `combi_type_branch` census, the `tests / fast (3.14)` red answered under `## Red checks`; the two checks this round adds pass. `tools/pr/ci_predict.py` reads `no closures, fast, governance or instrument red predicted against ee64358be7ee`.

## Unpinned sites

Each site `tools/pr/ci_predict.py` lists as ADDED UNPINNED (23 at `d6564e1ea`, its own count line) is in `custom_components/`, so `mutation-autofix` pins it after the push (its lane mutates `custom_components/`). The value check named is the spec mutant above that is killed at the same site.

- custom_components/heatpump_optimizer/dhw_draws.py:82 CLAMP_DROP: pinned by `mutation-autofix`; main's own `fold` clamp, `max(0.0, float(energy_kwh))`, moved into a local; no added mutant targets it.
- custom_components/heatpump_optimizer/dhw_draws.py:84 GUARD_OFF: pinned by `mutation-autofix`; value check ESCROW_ADD_OFF.
- custom_components/heatpump_optimizer/dhw_draws.py:95 CLAMP_DROP*2: pinned by `mutation-autofix`; value check TAKE_UNBOUNDED.
- custom_components/heatpump_optimizer/dhw_learning.py:77 CONST: pinned by `mutation-autofix`; value checks DIP_ZERO and DIP_SMALL.
- custom_components/heatpump_optimizer/dhw_learning.py:112 GUARD_OFF: pinned by `mutation-autofix`; value check STAMP_DEL.
- custom_components/heatpump_optimizer/dhw_learning.py:128 BOOLOP: pinned by `mutation-autofix`; value check R2_CREDIT_PER_INTERVAL.
- custom_components/heatpump_optimizer/dhw_learning.py:128 GUARD_OFF: pinned by `mutation-autofix`; value check OPEN_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:130 GUARD_OFF: pinned by `mutation-autofix`; value check HEATED_RETURN_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:132 CMP_BOUND: pinned by `mutation-autofix`; value check RISE_INCL_FLAT.
- custom_components/heatpump_optimizer/dhw_learning.py:132 GUARD_OFF: pinned by `mutation-autofix`; value checks RECOVERED_OFF and CREDIT_DOUBLE.
- custom_components/heatpump_optimizer/dhw_learning.py:133 CLAMP_DROP: pinned by `mutation-autofix`; value check TAKE_CAP_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:136 CLAMP_DROP*2: pinned by `mutation-autofix`; value checks PENDING_CUT_OFF and PENDING_INDEX.
- custom_components/heatpump_optimizer/dhw_learning.py:139 RETURN_DEL: pinned by `mutation-autofix`; value check RECOVERED_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:140 GUARD_OFF: pinned by `mutation-autofix`; value check PENDING_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:142 RETURN_DEL: pinned by `mutation-autofix`; value check PENDING_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:144 RETURN_DEL: pinned by `mutation-autofix`; value check FLUSH_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:453 CMP_BOUND: pinned by `mutation-autofix`; value checks WEEKEND_GT and FLUSH_WEEKEND (the Saturday arm).
- custom_components/heatpump_optimizer/dhw_learning.py:460 GUARD_OFF: pinned by `mutation-autofix`; value check COOLING_HEATED_OFF (the cooling arm).
- custom_components/heatpump_optimizer/dhw_learning.py:462 GUARD_OFF: pinned by `mutation-autofix`; value check USAGE_GATE_OFF.
- custom_components/heatpump_optimizer/dhw_learning.py:476 CLAMP_DROP: pinned by `mutation-autofix`; main's standby expression, which main's ledger recorded killed at both former sites; it survives the block and the whole of `tests/features.py` (round 2's `STANDBY_CLAMP`), so its killer is another gate script, which the lane's suite run finds.
- custom_components/heatpump_optimizer/dhw_learning.py:500 CLAMP_DROP: pinned by `mutation-autofix`; main's own fold clamp beside the helper call; killed in the `--diff` sweep (absent from its SURVIVED lines).
- custom_components/heatpump_optimizer/dhw_learning.py:516 CMP_BOUND*2: pinned by `mutation-autofix`; value check SAVE_TAKEN_OFF covers the take-back arm; the `energy_kwh > 1e-4` bound is main's and survives the block, as it would at main.
- custom_components/heatpump_optimizer/dhw_learning.py:516 GUARD_OFF: pinned by `mutation-autofix`; value check SAVE_GUARD_OFF.

One sweep survivor `ci_predict.py` does not list: custom_components/heatpump_optimizer/dhw_draws.py:60 CONST_SWAP (`_open_charge_kwh: float = 1.0`). A `DrawStats.from_dict` restore keeps that default, so only a restart mid-occurrence followed by a charge reaches it; no arm drives that, and it is left unpinned.

## Red checks

- `tests / mutation` at 416afe9b2 and 8fe714779: red by construction on the sites the added lines leave unpinned, listed under `## Unpinned sites`. `mutation-autofix` pins killed sites after the push (`ci-autofix.md`). Root-cause answer: the cheaper detector already ran. `tools/pr/ci_predict.py` (prepr step 6d) named every site locally before the handoff, at no added standing cost. The red is the pin-recording step and not an escaped defect, so no further countermeasure is owed.
- `tests / fast (3.14)` at 8fe714779: red on `tests/features.py`'s `combi_type_branch` census (`1 of 5240 FEATURE CHECKS FAILED`), which refuses a vendor name at `const.py:812`, `const.py:1595`, `heat_curve.py:72`, `pump_arbiter.py:256`, `pump_arbiter.py:1015` and `thermal_model.py:1870`. None of those files is in this diff; the red is `origin/main`'s, left by pull requests 3398 and 3433, and is repaired by pull request 3466 (R10-HOTFIX-COMBI-CENSUS-MAIN-RED, on the merge train). Cheaper detector: none exists in this branch, the red is main's, cause and repair named.
- `governance / instrument-self-tests` at 8fe714779: red on two self-tests of `tools/audit/seat/` (`sweep_render.py`: `unused: plan_coordinator_cap`, and the `pr_args.sh` pusher census). This diff touches nothing under `tools/`; both are main's, the census repaired by R10-HOTFIX-PUSHER-CENSUS (handoff in review). Cheaper detector: none exists in this branch, the red is main's, cause and repair named.
- `gate` at 8fe714779: red only because units it aggregates are red: `tests / fast (3.14)` (the combi census above), `tests / mutation` (answered above) and `pr-contract / pr-contract` (this body's missing answer for `tests / fast (3.14)`). No unit of its own. Cheaper detector: none, the gate is the aggregate.
- `arch-score / arch-score` at 8fe714779 (run 43037610675, job 130581907770): red because its `gh` call answered `gh: HTTP 503` before any score was computed (`##[error]Process completed with exit code 1`). The same check at the same head is green in runs 43024305010 and 43024294665, and `score.py --diff` at this head prints `dS +0.0237 IMPROVES` (`## Figures`). The cause is GitHub's API, outside this repository. Cheaper detector: none; a transient 503 has no earlier detector than the call that met it.
- `tests / nightly-status` at 8fe714779: red because the scheduled nightly run 42934263129 concluded `cancelled` (jobs `mutation-ledger (3)`, `mutation-ledger-push`, `slow`). Unrequired on `main-protect` and not caused by this diff; the cause is outside this branch. Cheaper detector: none exists in this branch.

## Forward-carry

none

## Friction

none
