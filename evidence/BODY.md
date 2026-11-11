Part 1 of outside pull request #3435 (Bankaifan), the counter-span fix: a heat-counter span no longer throws itself away when a cycle inside it ran hot water, under three conditions (the counter is declared to see hot water, the mode dwell observed the charge, no immersion element or pump backup heater on). The charge is removed from the span by its own counter steps, each split by that cycle's dwell (`SpanEnergy.dhw_kwh`), not by a time share of the span. Adopted from the author's commit f47199b6 with its authorship kept (commit 8827be07); parts 2 (boost settle tail) and 3 (refusal reasons and the card) are not in this diff (see `## Forward-carry`).

Round 2, repairing `Fix review: blocked da2eef8acd4d175dac1ffbfe6e8423a205d6b513 class-open` (probe/revt-r10-outside-learner-robustness-be6b5e32 at d183f1b31eab). The block: `span_heat` subtracted the charge's steps only under an observed span attribution, so one mode read that was not live (the attribution falls to the plan split) let the plan's whole-unit rule read a bridged charge as space heat. Fix: the meter records whether the dwell saw hot water in any step of the span (`SpanEnergy.dhw_seen`, set in `HeatEnergyMeter._fold_dhw_step`, which now keeps reading shares after a step went unaccounted, reset at each close). `span_heat` subtracts the steps whenever `e.dhw_seen or ran_hot_water(ev.attribution)`; an unaccounted step then reads no space figure. Alternatives that lost: refusing whenever `dhw_kwh is None` and the attribution is unobserved refuses every span on an install with no mode entity (the reviewer's null arm, `space_kw == heat_kw`, would read None); tracking `bridges_hot_water` on the meter would make a per-learner query mutate state, and `replay_gate` runs it once per learner per cycle. The second verdict finding is answered by `tools/audit/seat/features_block.py --emit-prelude OUT START [END]`, which derives the prelude a block needs from the tree it runs on (each missing name's last earlier binding), so the proof below re-runs from the tree with no hand-copied file. Everything else at da2eef8acd4d175dac1ffbfe6e8423a205d6b513, which the review did not contest, is kept unchanged.

Design of round 1, and alternatives that lost: the author passed a `bridged` bool computed in `coordinator._replay_gate`. That added three computed statements to the coordinator (`coord_footprint` 2497 -> 2500, the arch-score gate inadmissible). In this diff `heat_energy.replay_gate` takes the meter, the plan split, `sees_dhw` and `heater_on`, and calls `HeatEnergyMeter.bridges_hot_water` itself. Paying `class_excess_loc` by folding `_observe_heat_energy`'s locals into the call also lost: it made the call's arguments computed, which `coord_footprint` counts, so 4ef82525 restores it. The one added coordinator line is paid in `_replay_gate`'s docstring. Two guards no input reaches were deleted (the hot-water total reset when the first read opens a span, and `total <= 0.0`); the `rest >= 0.0` boundary is pinned by a value check. The diff staled three `killed_by` entries (`replay_gate` BOOLOP and RETURN_DEL 087a1e6c, `span_heat` RETURN_DEL a578b06f), deleted by hand and re-pinned.

## Head

c5ea2af8c0d762a27830523d09cc5c96ac9e08c5, on origin/main c71d3f6e8983948f51ea6ac0b9e0ecfc76069d4d (merge base 6f0ff9d81415bcfee6019327d12d4ded00ae30e4), measured 2026-11-11T18:31Z. The gate, golden and harness figures were taken at abff0298faf1ffe0899137913ac32c36824a8666, whose code this head keeps; the head adds only the mutation ledger (stale pins dropped, five pinned).

## Mutation proof

Prelude: `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --emit-prelude $P 'R10-HEAT-METER: a delivered-heat counter' '# The earned basis. A thermal-power install'` (prints `prelude of 24 statement(s)`). Then `PYTHONPATH=tests/hastub python3 tools/audit/seat/mutant_run.py --in-place --spec <spec> --cmd "python3 tools/audit/seat/features_block.py --prelude 'exec(open(\"$P\").read())' 'R10-HEAT-METER: a delivered-heat counter' '# The earned basis. A thermal-power install'"`. The block is the R10-HEAT-METER section of `tests/features.py`, through this diff's checks (31 checks). Each mutant is `{name, file, old -> new}`, all in heat_energy.py:

- Ma-span-heat-ignores-seen: `if space_kw is not None and (e.dhw_seen or ran_hot_water(ev.attribution)):` -> `if space_kw is not None and ran_hot_water(ev.attribution):`
- Mb-fold-never-sees: delete `self._dhw_seen |= shares[1] > 0.0`
- Mc-close-keeps-seen: `self._opened, self._dhw_kwh, self._dhw_seen = True, 0.0, False` -> `self._opened, self._dhw_kwh = True, 0.0`
- Md-fold-stops-once-unaccounted: the fold's early return regains `or self._dhw_kwh is None`
- Me-span-drops-seen: `SpanEnergy(..., self._dhw_kwh, self._dhw_seen)` -> `SpanEnergy(..., self._dhw_kwh)`

```
SURVIVED NULL
KILLED Ma-span-heat-ignores-seen
KILLED Mb-fold-never-sees
KILLED Mc-close-keeps-seen
KILLED Md-fold-stops-once-unaccounted
KILLED Me-span-drops-seen
```

Each kill is the one new check, "a span that carried a hot-water charge the dwell saw reads no space figure once one mode read in it, after the charge or before it, was not live ...". Failing test first: with `heat_energy.py` reverted to da2eef8acd4d175dac1ffbfe6e8423a205d6b513 and this branch's `tests/features.py`, the same block prints `1 of 31 FEATURES BLOCK FAILED` (that check); at the head `ALL 31 FEATURES BLOCK PASSED`. Round 1's fourteen mutants (M1-M14, bridge, heater, sees-dhw, dwell, counter, time split, negative rest, unaccounted-as-zero, step share, no fold, coordinator immersion/pump heater/sees-dhw, all-hot-water) target lines this round leaves unchanged except M6 and M8's `if` line, whose predicate Ma now mutates; they were killed at da2eef8acd4d175dac1ffbfe6e8423a205d6b513 and the reviewer's own `ev/mut_check.py` re-killed M1, M2, M6, M9 and M10 there.

## Null control

- The reviewer's harness `ev/unobs_span.py` (probe/revt-r10-outside-learner-robustness-be6b5e32 at d183f1b31eab, sha1 86da0673ce7465413e9d5b142f4492720bde1a2f), run from scratch with `PYTHONPATH=.:tests/hastub`, at both ends:
  - at da2eef8acd4d175dac1ffbfe6e8423a205d6b513: `charge, all observed: space_kw=1.818...`; `charge, cycle 6 mode not live: space_kw=2.727... dhw_kwh=None observed=False` (the defect: the whole 15 kWh read as space); `no charge, cycle 6 mode not live (null): space_kw=2.0`.
  - at the head: `charge, all observed: space_kw=1.818...` (unchanged); `charge, cycle 6 mode not live: space_kw=None`; null `space_kw=2.0` (unchanged).
- The new check's own controls: all reads live subtracts the charge's step (10 kWh / 5.5 h); no charge with a read not live reads all its heat as space; the span after a charged span, with no charge and one read not live, reads all its heat as space again (pins the per-span reset, Mc); an unobserved read before the charge (read 1) refuses as well as one after it (read 6) (pins Md).
- Both ends of the input range: a fresh meter (no counter, no dwell) bridges nothing and folds no `dhw_seen`; an install with no mode entity sees no hot water in any step, so `dhw_seen` stays False and its spans read as at the merge base (the null arm above).
- `features_block.py --self-test`: 11 checks, 0 failed, including `--emit-prelude refuses a name no earlier statement binds (null control)`.
- Mutant NULL survived (above).

## Figures

- Scoped gate: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED`. `GATE_SCOPE=auto GATE_SCOPE_BASE=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub bash tests/run.sh` at the head: `MODE: SCOPED -- 22 script(s) run, 11 scoped out`; every script exited 0, `tests/features.py` (full, 539 s) included, except `tests/golden.py`, which in this default invocation compares against the current origin/main tip two-dot, where main moved coordinator-payload fixtures after the merge base (as round 1 recorded); it is green under the drift run below.
- Pins: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base $(git merge-base origin/main HEAD) --jobs 3` printed `PIN KILLED: 5 pinned, 0 left unpinned` (heat_energy.py `span_heat` BOOLOP and GUARD_OFF, `_fold_dhw_step` two GUARD_OFF and one CMP_BOUND, each killed by tests/features.py). Three `killed_by` entries this round's edits staled (`_fold_dhw_step` GUARD_OFF c2b17940, `span_heat` CMP_BOUND and GUARD_OFF 65b91d90), which `prepr.sh`'s ledger prediction named STALE PIN, are deleted by hand.
- Goldens: `PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) python3 tests/golden.py` rc 0, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 6f0ff9d81415bcfee6019327d12d4ded00ae30e4` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`. Neither claim file is touched.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` prints `Architecture score: dS +0.0000 NULL`.
- Seam census (step 8), rule `git grep -n -E "ran_hot_water\(|space_heat_kw\(|replay_gate\(|bridges_hot_water\(|dhw_seen" -- custom_components`. The class is a reader of a span or interval that carried a hot-water charge the dwell saw, falling to the plan's whole-unit rule because another segment went unobserved:
  - `heat_energy.span_heat` (space_heat_kw on a span, and the subtraction predicate): closed in this diff (`dhw_seen`).
  - `heat_energy.HeatEnergyMeter` `dhw_seen` field, fold and reset (`SpanEnergy.dhw_seen`, `_fold_dhw_step`, `_close`): the mechanism, pinned by Mb, Mc, Md, Me.
  - `heat_energy.bridges_hot_water` and `heat_energy.replay_gate`: already guarded; the bridge requires `ran_hot_water` on the cycle's own attribution, observed only, and the span it keeps clean is now read by the closed `span_heat`.
  - `coordinator._replay_gate` and its two callers (house heat loss, lower floor): closed through `span_heat`; they pass inputs only.
  - `coordinator._interval_space_power` and the pending-split pairing (`ran_hot_water` on a per-cycle interval): out of class. A per-cycle interval is not bridged, its window is its own attribution, and both sites are unchanged from the merge base (the base holds the same three coordinator matches of `ran_hot_water(|space_heat_kw(`).
  - `coordinator.py` `space_heat_kw(... integrated=False)` on the flow-bias heat: out of class, a point reading under the whole-unit rule, unchanged from the merge base.

## Red checks

- `tests / fast (3.14)`: if red, it is main's combi census, fixed by PR #3466, not this diff; no cheaper detector is owed by this branch.

## Forward-carry

- Carry 1: Part 2 of outside pull request 3435, the boost settle tail scaled on the time the boost ran and persisted across a restart (boost.py, store.py, const.py and the mode change in coordinator.py), is not in this diff. It is its own roster group by feature triage ruling P613, cut from the author's commit f47199b6 with the authorship kept. Carry: R10-OUTSIDE-LEARNER-ROBUSTNESS-P2
- Carry 2: Part 3 of outside pull request 3435, the refusal reasons at DEBUG and the frozen learner phase with the card in three languages (heat_energy.py, learner_progress.py, payload.py, the card script, tests/card.mjs), is not in this diff. It is its own roster group by feature triage ruling P613, built after part 2 from the same commit. Carry: R10-OUTSIDE-LEARNER-ROBUSTNESS-P3

## Friction

- mutation-proof: cost: `features_block.py --through` still cannot be a mutant command for a block past D1-s2-55 (a worker job pickles a class defined under the `features_block` module, so its NULL is killed), and a `--through` to the R10 block re-runs nearly the whole script per mutant. `--emit-prelude` lands the tree-derived alternative in this diff. Carry: dismissed: the instrument that replaces it lands here; no later stage depends on --through
