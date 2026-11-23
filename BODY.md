Closes #3849

R11-OUTSIDE-3849. The planner priced a duty switch at zero until the duty-switch learner latched (`n >= N_ON` over `SPAN_DAYS_ON` days), so the issue's hot water to heating switch, which stopped the compressor 3 times in 3 (`dhw_space` n = 2, unlatched), was planned as if it never stopped it: cases 2, 3 and 03:00 of the issue, the last a charge split by one heating step that the start term cannot see either (the combined draw never goes off).

Built here:

- `duty_switch.Direction.priced`: `p` once latched, else `k / (n + PRIOR_N)`, `PRIOR_N = N_ON`. No evidence prices nothing; a direction that stopped at every switch is priced at half when it reaches the latch's weight. Both directions read it, through one property: an asymmetric rule would need a special case, and the leg mask below keeps either direction's unlatched price off the legs.
- The legs move on a latch only: `duty_legs.leg_rule` takes the per-direction unlatched mask and ignores a masked direction's stop for the order and the merge. The arbiter reads it through `DutySwitchLearner.split`; the solve through the new `OptimizationConfig.duty_switch_unlatched`, set by `planner_fields` from `DutySwitchLearner.config_fields`. So the plan prices the legs the arbiter serves whatever the latch.
- The off time stays latch-only: an unlatched direction charges no lost running time (`lost_share`, `availability`), so the availability vector and the space headroom move on a latch only too.

Alternatives taken against: pricing the stop inside the start term (it counts off-to-on edges of the combined draw, and the switch never makes one); letting the shrunk estimate also move the leg order (the arbiter's serving would then flip on noise from two episodes, which is what the latch exists to refuse); carrying the mask as a third element of `planner_pairs` (every caller unpacks two, and the mask is not a pair the planner prices).

Routed, not built (the group's brief): the step-0 DHW run with no charge under way (cases 4 and 06:05) is R11-OUTSIDE-3848; hot-water placement with no start term (cases 1 and 06:15) is R11-OUTSIDE-HONEST-DHW-RUNS (#3805).

## Head

`0cafd89455ea58928761dae4f206908fa9d5560e` is this PR's head: one commit on 0a93df1ef663 that splits the `tests/features.py` comment above "a configuration that never sets the mask reads its pair as latched" into sentences under 40 words (comment only; no code, check or value moved). `origin/main` at 3153a635b401, merged cleanly by `git merge-tree --write-tree origin/main HEAD`, so not merged in.

e6e83c39392e913fa6f208398442f06d91af66c7 measured (figures from earlier commits name theirs); `origin/main` at e3cb5c019b46, the merge base, 2026-11-22 UTC. The comment-ratchet figures below are taken at 0cafd89455ea, 2026-11-23 UTC.

## Mutation proof

M1-M5 were each applied in its own detached worktree of 7ea740f8d3 (the duty-switch block then held 104 checks) and run through the duty-switch block of `tests/features.py` and the coordinator block, by `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py "from types import SimpleNamespace as _DspNS" "# R11-OUTSIDE-HONEST-STARTS-RUNS, the descents"` and `... --prelude 'exec(open("P").read())' "_svc_crash_hass = FakeHass()" "_svc_sim_hass = FakeHass()"` (P from `--emit-prelude` with the same markers):

- M1, the shrink deleted (`Direction.priced` returns `self.p if self.usable else 0.0`): 6 of 104 and 1 of 5 fail: "the read returns no off time while a direction is unlatched, and its stop probability shrunk to k / (n + PRIOR_N)", "issue 3849's record (three stops in three switches, n = 2, unlatched) prices hot water to heating at 2 / (2 + PRIOR_N)", "the shrunk price over every unlatched record on a half-episode grid to the cap (441 records)", "an unlatched direction moves neither the order nor the merge", "the planner's leg rule is the arbiter's on all 16 learner states", "issue 3849's read reaches a full optimize", "the coordinator passes the unlatched mask with the pairs".
- M2, the mask deleted from `leg_rule` (`stops = [p > 0 for ...]`): 5 of 104 fail: "an unlatched direction moves neither the order nor the merge", "the mask is per direction", "the planner's leg rule is the arbiter's on all 16 learner states", "the arbiter serves issue 3849's both step as before the learner existed", "issue 3849's read reaches a full optimize".
- M3, `duty_switch_unlatched` dropped from the configuration fields: 1 of 5 fails: "the coordinator passes the unlatched mask with the pairs".
- M4, the mask dropped from `optimizer._leg_rule`: 2 of 104 fail: "the planner's leg rule is the arbiter's on all 16 learner states", "issue 3849's read reaches a full optimize".
- M5, `DutySwitchLearner.unlatched` returns `(False, False)`: 6 of 104 and 1 of 5 fail (the M1 set less the grid check, plus "the arbiter serves issue 3849's both step as before the learner existed").

- M6, the mask's default swapped to `(True, False)` (prepr's diff-mutant survivor at b382641870), at e6e83c3939: 1 of 105 fails: "a configuration that never sets the mask reads its pair as latched". The default is a design choice: a configuration that never sets the mask (a harness handed a pair, the R10 fixtures) reads its pair as latched, as before this change.

Unmutated: `ALL 104 FEATURES BLOCK PASSED` at 7ea740f8d3 and `ALL 105 FEATURES BLOCK PASSED` at e6e83c3939, `ALL 5 FEATURES BLOCK PASSED` at 7ea740f8d3, by the same two commands.

## Null control

At the merge base the issue's record prices nothing: the harness prints `read ((0.0, 0.0), (0.0, 0.0))` and a split excess of 0.0000 for it. On both trees an empty learner prices nothing and keeps `DEFAULT_RULE` (the harness exits 1 otherwise). In the suite: an empty learner and an install whose every switch was kept still read a plan identical to today's on all three install classes ("null controls from learner state").

## Figures

- Harness `dev/audit/harnesses/r11_outside_3849_unlatched_price.py` (sha1 e6ae16a37f3bc9b4b7eee03a04bab582d27f5f66), `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r11_outside_3849_unlatched_price.py`. At the head, issue 3849's record: `read ((0.2857142857142857, 0.0), (0.0, 0.0)) mask (True, True) leg rule ('dhw', None)`, switch term split 0.5714 whole 0.2857, split excess 0.2857 at a start price of 1.0 (2/7 of one start for the one extra hot water to heating switch). Run from a checkout of e3cb5c019b46 with the same command and the head's harness file: `read ((0.0, 0.0), (0.0, 0.0)) mask absent leg rule ('dhw', None)`, split excess 0.0000. Empty learner on both trees: split excess 0.0000, leg rule `('dhw', None)`.
- Shrink grid: the check "the shrunk price over every unlatched record on a half-episode grid to the cap" enumerates `k, kept` in `{0, 0.5, ..., N_CAP}` (441 records) and asserts `0 <= priced < 1`, zero exactly where `k == 0`, under `p` wherever `k > 0`, and `priced == k / (n + PRIOR_N)`; at the cap with every switch a stop `N_CAP / (N_CAP + PRIOR_N)` = 2/3.
- Leg-rule census: "the planner's leg rule is the arbiter's on all 16 learner states" drives every pair of the four per-direction states (empty, unlatched with a stop, latched with a stop, latched all kept) through `optimizer._leg_rule` of `config_fields` and `DutySwitchLearner.split`; its control, the configuration without the mask, disagrees on exactly the 5 states where an unlatched stop moves the rule (hot water to heating unlatched beside each of the four, and heating to hot water unlatched beside a latched stop).
- `python3 tests/structure.py`: no row breached; `module_excess_loc` and `class_excess_loc` each one under budget, not re-recorded.
- `python3 tools/audit/archscore/score.py --diff e3cb5c019b46`: `Architecture score: dS +0.0011 IMPROVES`, `coord_footprint 2525 -> 2523` (the field assembly moved from `planner_fields(coord)` onto the pure learner, `config_fields`).
- `python3 tests/closure.py select --diff e3cb5c019b46 --workdir D`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`; the gate `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=e3cb5c019b46 ./tests/run.sh`: every one of the 28 green (`golden.py` skipped by drift mode, its fixtures checked by `env_drift.py --all`), 11 by `run.sh` at ec43660f9d (`fab96b2fd9`'s ledger and INERT entries landing during it) until the background limit stopped it, the other 16 (and `layout.py`, which `run.sh` runs always) in four lanes at fab96b2fd9 (`stress.py` and `harness_headers.py` alone, after the rest), `e934dede5a`'s comment split landing during them. `doc_claims.py` (refused at fab96b2fd9 by its comment ratchet, two sentences over 40 words) and `structure.py` (refused there for the two unrecorded gains) were re-run green at b382641870: since fab96b2fd9 only those comment sentences and the recorded budgets moved. e6e83c3939 adds one check to `tests/features.py`, whose duty-switch block was re-run there (105 of 105), not the whole script.
- `python3 tests/comment_ratchet.py`: at 0cafd89455ea `RESULT base=24e3f37620f8 files=198 long_units_base=2300 long_units_head=2300`, `comment_ratchet: OK`; control at 0a93df1ef663 `long_units_head=2301`, `REFUSE tests/features.py: long units 465 -> 466`, `comment_ratchet: FAIL` (rc 1).
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` at 0cafd89455ea: `ALL 443 checks PASSED`; at 0a93df1ef663 CI's `tests / fast (3.14)` printed `1 of 443 checks FAILED` (the comment ratchet).

## Red checks

- `tests / fast (3.14)` at 0a93df1ef663: `tests/doc_claims.py` refused by its comment ratchet: e6e83c3939 added a 41-plus-word comment sentence to `tests/features.py` (long units 465 -> 466) and was re-run only through the duty-switch features block, not `doc_claims.py`. Repaired at 0cafd89455ea (figures above). Cheaper detector: `python3 tests/comment_ratchet.py`, which exists and runs locally in about 90 s on this host; it was in no path the last commit's re-run took. No new detector built: the existing one sufficed and prepr's code steps run it.
- `tests / mutation` at 0a93df1ef663: red by construction on the 9 site(s) under `## Unpinned sites`. `tests / mutation-autofix` went red `skip-measure-failed` with 0 anchors because both `mutation-pins` shards refused a red baseline (the `doc_claims.py` red above), so no pin came. Unmeasured at 0cafd89455ea: the pin is owed to mutation-autofix on this head, whose baseline is now green. Cheaper detector: none beyond the `doc_claims.py` one above, the same cause.
- `pr-contract / pr-contract` at 0a93df1ef663: this section named neither red above. Answered here. Cheaper detector: `tools/pr/prepr.sh`'s body contract, run on the body before it is set; the body at that head was set without a re-run against the head's reds, which were not yet concluded.

## Unpinned sites

The nine sites `prepr.sh` step 6d lists at e6e83c3939 (CI's `tests / mutation` named the same nine at 0a93df1ef663), all under `custom_components/` and each left to `mutation-autofix` to pin (`ci-autofix.md`). Each is killed locally: `MUTANT_CMD` (the two `features_block.py` calls under `## Mutation proof`, with `MUTANT_IN_PLACE=1`) drew 28 mutants of the added lines (`mutant_run.py --list`) and printed one `SURVIVED` line at b382641870, `optimizer.py:2782 CONST_SWAP` (the mask's default), killed since by "a configuration that never sets the mask reads its pair as latched" (1 of 105 fails with the default swapped, 0 of 105 restored). At e6e83c3939 the same `MUTANT_CMD`, in prepr's archive copy, printed `no survivor among the diff's first 40 mutant(s)`. Where this diff edited a line main had pinned, that pin's file is deleted in fab96b2fd9, so the lane pins the edited line afresh.
- custom_components/heatpump_optimizer/duty_legs.py:68 BOOLOP: pinned by mutation-autofix; killed locally by hand (the diff-mutant draw has no BOOLOP): `and` to `or` fails 8 of 105 of the duty-switch block
- custom_components/heatpump_optimizer/duty_legs.py:68 CMP_BOUND: pinned by mutation-autofix; killed locally by the diff-mutant run
- custom_components/heatpump_optimizer/duty_legs.py:69 BOOLOP: pinned by mutation-autofix; killed locally by hand: `and` to `or` fails 7 of 105 of the duty-switch block
- custom_components/heatpump_optimizer/duty_legs.py:71 RETURN_DEL: pinned by mutation-autofix; killed locally by the diff-mutant run
- custom_components/heatpump_optimizer/duty_switch.py:192 RETURN_DEL: pinned by mutation-autofix; killed locally (M1's line)
- custom_components/heatpump_optimizer/duty_switch.py:414 RETURN_DEL: pinned by mutation-autofix; killed locally by the diff-mutant run
- custom_components/heatpump_optimizer/duty_switch.py:418 RETURN_DEL: pinned by mutation-autofix; killed locally (M5's line)
- custom_components/heatpump_optimizer/duty_switch.py:428 RETURN_DEL: pinned by mutation-autofix; killed locally by the diff-mutant run
- custom_components/heatpump_optimizer/duty_switch.py:590 RETURN_DEL: pinned by mutation-autofix; killed locally by the diff-mutant run (the coordinator block)

## Forward-carry

- From this merge a hot water to heating switch is priced before the learner latches, at `k / (n + PRIOR_N)` (`duty_switch.Direction.priced`), so an install with one counted stop already runs the switch term, the unpriced second descent and the placement-ban candidate (`optimizer._avoid_priced_switches`). A start term on hot-water placement must price the stop a hot-water block's end into heating makes once: the switch term already weighs it at p times the running share. Control: the harness's split excess reads 0.0000 at e3cb5c019b46 and 0.2857 at this head for the issue's record, and 0.0000 at both for an empty learner. Re-measure at the destination's own merge base. Lands in R11-OUTSIDE-HONEST-DHW-RUNS's brief, in the round-11 roster `dev/programme/rosters/wave-r11-groups.json` on `handoff/audit-r11-roster`. Carry: R11-OUTSIDE-HONEST-DHW-RUNS

## Friction

- `features_block.py`: cost: `--emit-prelude` drops a top-level expression statement the block's names depend on (`_asyncio.run(_ha_setup_entry(...))` before `_svc_crash_entry.runtime_data`), so the prelude for the coordinator block raised `'FakeEntry' object has no attribute 'runtime_data'`; worked around by starting the block at `_svc_crash_hass = FakeHass()`. Proposal for round-end triage: emit the expression statements that touch a binding the block reads. Carry: dismissed: instrument outside this group's seam, recorded as a proposal for round-end triage
- `ci_predict.py`: unclear: its step-replay arm predicted `governance / instrument-self-tests` red on "Show the verdict bus refusing its own fixtures" (`rc 1 at the head, 0 at the base`) in two runs at b382641870, one inside `prepr.sh` and one `--only step-replay`, each beside a `MUTANT_IN_PLACE=1` mutant run; the step's own command (`bash tools/audit/seat/bus.sh --self-test`) printed `245 checks, 0 failed` rc 0 at that head run by hand, through the arm's own `bash -eo pipefail` call, and after every other selected step in sequence, and the arm predicted no red at e6e83c3939 with mutants in the archive copy. The arm keeps no output of a red replay, so the failing check is unknown. Proposal for round-end triage: keep a red replay's output beside the prediction. Carry: dismissed: instrument outside this group's seam, recorded as a proposal for round-end triage

