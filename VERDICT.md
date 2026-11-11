Fix review: blocked 8fe714779710e5f56c6eb353ab8b2cea00fcaddd regression-unmeasured: at the learner's production cadence the take-back erases real draw (15-min p90 1.8777 to 0.9868 kWh, 30-min sequence 0.6542 to 0.3847 kWh), unmeasured because every harness arm and test samples at 5 min

bus-nonce: 1be12d5d56ad938d69920390d5a4f45c

## Block

Round 2. The delta against `8e2b7d99` (the authored handoff `b6696bd6`, plus a main merge and a bot pin commit) rewrites `dhw_learning.py` and `dhw_draws.py`, so this review covers that production code in full.

The round-1 regression is held: every truth arm (no dip) is identical between base and head. That holds in the fixer's harness at 5 min, and in my probes at 5, 10, 15, 30 and 60 min. The repair still introduces a new regression of the same kind (real draw removed from the heavy-day p90). The body never measured it, because nothing in the PR runs at a cadence production can use.

- **Cadence.** `async_learn_dynamics` runs once per coordinator refresh: `update_interval=timedelta(minutes=config.optimization_interval)` at `coordinator.py:3546-3548`, default `DEFAULT_OPTIMIZATION_INTERVAL = 30` (`const.py:1632`). The options flow allows 10 to 120 min in 5-min steps (`config_flow.py:1854`). The fixer's harness (`STEP_MIN = 5`) and every `_chg_seq` case in `tests/features.py` (5 min apart) sample faster than any configurable interval. At the 30-min default, `DHW_CHARGE_SETTLE_HOURS = 0.25` can never mark an interval as settling.
- **Mechanism.** The interval that *ends* at the first heated sample is flagged as charge (`heated_interval = self.heating_since_sample or heating`). So a draw made before the charge starts is folded as charge-folded energy. The heated interval's own charge heat also hides part of the dip, so the later unheated rise (the full dip recovering) is larger than the dip energy that was folded. `take_back` then removes the difference from real draw. This contradicts the body's claim that the take-back can erase "never draw folded outside the charge".
- **Minimal sequence, 30 min apart (the default).** Script `ev/seq30.py`, output `ev/seq30.txt`. Readings 07:00 50.0, 07:30 47.0 (plan flag on, a 3 K draw before the charge), 08:00 44.0 (charge heat +1 under a 4 K dip), 08:30 48.0, 09:00 48.0. Open occurrence:

  | arm | base `ee64358b` | head |
  |---|---|---|
  | truth (no dip) | 0.6542 | 0.6542 |
  | dip | 1.3127 | **0.3847** |
  | no-charge control (flag never set) | 1.3127 | 1.3127 |

  The head removes the 0.66 kWh phantom and 0.27 kWh (41 %) of the real draw on top.
- **Simulation.** Script `ev/cadence.py`, output `ev/cadence_{base,head}.txt`, moved cells in `ev/cadence_moved.txt`. Per-minute tank physics, the learner sampled every 10/15/30/60 min, charges of 10, 40 and 15 min, draws at six offsets, 14 days. At 15 min (a configurable setting), a 07:30 10-min charge with a draw starting 10 min before it reads:
  - truth 1.8777;
  - dip arm at base 1.8753 (error −0.002);
  - dip arm at head **0.9868** (−0.89, −47 %).

  At the 30-min default the head moves four dip cells: two improve (+0.23 to +0.015) and two newly under-count (0.000 to −0.19). At 10 and 60 min the head equals the base in every dip cell. So at those cadences the fix removes none of the phantom it was written for: at 10 min, offset +5, the dip arm reads 2.6261 at both ends against truth 2.1156.
- **What the repair owes.** At least the 30-min default and the 10-min floor, in the harness and in a features case:
  - a draw ending in the interval that closes at the first heated sample, beside a dip;
  - a take-back that cannot exceed the energy the charge's dip actually folded;
  - the gain at production cadence stated against these losses.

  Five-minute arms are not production evidence. They may stay as a sub-cadence check, but the body must say so.
- **Mutation survivors (`--spec`, my own mutants).** Two of the three survivors below change the booked energy. Both target a claim the body makes. `ev/mutants_r2.txt` is the block command at the head. The concrete sequences are `ev/seq.py`, with output in `ev/seq_survivors_head.txt` and `ev/seq_survivor_{esc,cred}.txt`.

  | mutant | edit | head | mutant | control |
  |---|---|---|---|---|
  | `R2_ESCROW_DEC_OFF` | `dhw_draws.py` `self._open_charge_kwh -= taken` → `pass` | 0.689 | 0.4633 | 0.689 |
  | `R2_CREDIT_PER_INTERVAL` | `dhw_learning.py` `if (heated_interval or settling) and not self.open:` → `if heated_interval or settling:` | 0.689 | 0.457 | 1.849 |

  - `R2_ESCROW_DEC_OFF`: the take-back escrow is never decremented. A 3 K pre-charge draw, a 1 K dip and two +1 K settle rises (sequence A) lose 0.226 kWh of the pre-charge draw under the mutant. This breaks "never draw folded outside the charge".
  - `R2_CREDIT_PER_INTERVAL`: the credit resets on every charge-affected interval. Sequence B (an 8 K drop, then three +3 K rises inside the settle window) takes back about 7 K under the mutant, past the per-charge `DHW_CHARGE_DIP_MAX_K` of 5 K the body states.
  - `R2_SETTLE_INCL_HEATED` (`return not heated_interval and (` → `return True and (`) is equivalent by reading. On a heated interval, `async_learn_usage(..., heated=True)` returns at its first guard, and `advance` returns before the pending branch.

  The wider-closure re-run of the three is reported under Evidence.

## Findings

- Residual: quantised sensor jitter (±0.1 K, rounded to 0.1) in a truth trace at 5-min cadence. A positive jitter inside the settle window takes back charge-folded draw. The p90 falls 5.2218 to 5.2085 at a draw 10 min before the charge and 5.155 to 5.1365 at a draw starting 2 min after it (−0.25 % and −0.36 %); every other jitter cell is B = N (`ev/probe_{base,head}.txt`). This is bounded by the jitter amplitude over at most three settle intervals, and it lies inside the cadence repair above. Carry: dismissed: 0.4 % at most, below the sensor resolution, and the regression-unmeasured block re-scopes the mechanism it rides on
- Out of scope: the body's second class enumerator (`git grep -n "async_learn_dynamics\|CONF_DHW_TEMP_ENTITY\|draw_stats.fold" -- custom_components/`) also returns `config_flow.py` (89, 543, 1409, 1444, 1683) and `const.py` (84, 297, 1858), which the body's disposition list does not name. Every hit is the entity key's definition, form field or staleness/plausibility table, not a consumption attribution, and no perturbation of these moves any harness figure. Carry: dismissed: void under judge.md (definitions only, no drop attribution); the body should name them next round

## Evidence

- Head reviewed: `8fe714779710e5f56c6eb353ab8b2cea00fcaddd` (`ev/HEAD.txt`). Merge base `ee64358be7eeccaec5178a923cb3b83a18a924a0`. Round 2 (delta against `8e2b7d99d0e99f3cbd00d49ceb9b4a1458b87257`).
- `review_carry.py 8e2b7d99 8fe71477` prints `FRESH-REVIEW`.
- `review_carry.py df632c8dd 8fe71477` prints `CARRY`. The body's `## Head` names `df632c8dd`, and the one commit past it is the bot's `ci: pin killed mutants` (a ledger file only). `review_packet.py` refused with `head-note` for the same reason.
- RESULT harness (the fixer's `dev/audit/harnesses/r10_dhw_charge_settle_p90.py`, sha1 `24cfb411cf98c620a321bc8a9e3d32cc7beb18e3`, run from the head's copy against the base and head trees; `ev/harness_{base,head}.txt`, side by side in `ev/harness_BvN.txt`): every B and N cell of the body's table re-derives except one. draw-0745 dip@max usage points read 81 at N against the body's 82; p90 5.3865 matches. The body measured on merge base `a7628041`, and main has moved since. Truth and flat arms are B = N in all six geometries and both rates.
- Harness provenance (step 9): this PR adds the harness, so the instrument is the builder's, not the finder's. No finder harness is named (packet: "Finder's harness: none named"). `ev/probe.py`, `ev/cadence.py`, `ev/seq.py` and `ev/seq30.py` are mine (reviewer-built) and not in the tree.
- RESULT probe (`ev/probe_{base,head}.txt`, 5/10-min cadence, draws at 07:20/07:32/07:40/07:45, ±0.1 K jitter on and off): noise-free truth cells are B = N. Note that a 1-min cadence is below the learner's `dt_h <= 0.02` floor and learns nothing at either end; those rows are void.
- RESULT cadence (`ev/cadence_BvN.txt`): all 72 truth cells are B = N; the dip cells that move are listed in `ev/cadence_moved.txt`.
- Mutants, the block command from the body at the head (`ev/mutants_r2.txt`): `SURVIVED NULL`; `KILLED` R2_FLUSH_AS_HEATED, R2_CHARGE_HEATED_ONLY, R2_TAKE_AFTER_FOLD, R2_CLOSE_KEEPS_PENDING; `SURVIVED` R2_ESCROW_DEC_OFF, R2_CREDIT_PER_INTERVAL, R2_SETTLE_INCL_HEATED.
- The three block survivors were re-run over a wider closure: `mutant_run.py --in-place` over `tests/entities.py`, `guard_pins.py`, `finite_boundary.py` and `features.py` in series (the scripts that kill this file's other ledger pins). The run refused at `KILLED NULL` (rc 3): one of those scripts is red on the unmutated head, which fits the inherited `tests / fast` red. So the survivors are established against the PR's own block command only. Whether another gate script kills them is not verified here; the concrete sequences above show they are not equivalent.
- The body's own 25 + 3 + 6 + 4 named mutants were not re-run. The body runs them through the same block command at `b5a0f877`, whose production files match the head.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, `class_excess_loc = 17532`. The budget row reads 17534 → 17532 against the merge base `ee64358b`. The body's "17537 to 17535" was measured on the older base; the direction and size (−2) are the same.
- `VERSION`, `manifest.json` and the `RELEASE_NOTES.md` heading are untouched (`git diff ee64358b...HEAD` prints nothing). No golden or claim file is in the diff.
- `git merge-tree --write-tree origin/main 8fe71477` exits 0 against origin/main `0a2139b1` (`ev/merge_tree.txt`).
- CI at this head, read live: `tests / mutation` failure (the body answers it under `## Red checks`); `tests / fast (3.14)` failure (the dispatch rules main's `tests / fast` census red inherited from main); `governance / instrument-self-tests` failure (outside `merge_train.py owed-reds`, so not this PR's). `merge_train.py classify` was still WAIT when this verdict was written (`ev/ci_classify.txt`). The block does not turn on CI.
- Class enumerator: the first grep returns `boost.py`, `climate.py`, `coordinator.py`, `dhw_learning.py`, `optimizer.py`, `payload.py` and `sensor.py`, all named in the body's dispositions.
