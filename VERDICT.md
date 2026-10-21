Fix review: blocked 21eeb5b2325bf6a99f2a282f2e38bafbee44ab70 harness: config-attack: at the default 30-min optimization_interval the production tile rotation publishes a degree pair the card's convexity check hides (14 of 40 days, 30 of 40 at 120 min); the days arm prices both tiles from one midnight solve and never applies that check

bus-nonce: e25f00fd7f5d87509e4099b38b59be1b

PR #2572 (R10-ADVISOR), head `21eeb5b2325bf6a99f2a282f2e38bafbee44ab70`. Round 1: the first review of this head.
Measured from a detached worktree at that head; merge base `e7c664856776542bf60bd770c98aba1eaadb4041` (= origin/main at review time).
Contract: `dev/governance/roles/fix-review.md` from origin/main (`git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the copy is current).

## Blocking

### B1. Step 6, configuration attack: under production's sampling the card hides the row it is meant to fix

`price_tiles` refreshes ONE tile per scheduled solve (`_maybe_refresh_price_tile`, cursor over 3 specs). So `target_minus_1` and `target_plus_1` are sampled from different solves, at different start times, and averaged separately. The card then renders the pair only if `cost >= save - 1` (convex within one rounding unit), which assumes the two published means are exactly antisymmetric.
The body backs that assumption with the `days` arm: "the two tiles are antisymmetric within 0.9 every day". But that arm prices both tiles from the SAME solve, always at 00:00. It also counts only sign monotonicity (`cooler < 0 < warmer`), never the card's `degreeRow` predicate.

The reviewer-built probe (`ev/tools/rotation_probe.py`; disclosed as mine, not the finder's or the fixer's) replays production instead:
- the harness's own house and its 40-day price and weather sequence, concatenated;
- one tile per solve in rotation, at a fixed cadence;
- `price_tiles.record` / `published`, and the card's predicate applied each local evening.

The solver is stubbed because `baseline_cost` (the thermostat's) does not depend on it. `ev/probe_stub_fidelity.txt` shows the real and stub figures are identical to 4 decimals at 3 intraday starts.

```
RESULT rotation cadence 30 min: card NOT shown on 14/40 days (2/11 from day 30); asym (up+down) range -2.29..+0.55
RESULT rotation cadence 60 min: card NOT shown on 3/40 days (0/11 from day 30); asym (up+down) range -1.82..+1.22
RESULT rotation cadence 90 min: card NOT shown on 12/40 days (0/11 from day 30); asym (up+down) range -3.01..+0.14
RESULT rotation cadence 120 min: card NOT shown on 30/40 days (10/11 from day 30); asym (up+down) range -2.50..+2.06
RESULT both-every-solve cadence 30 min: card NOT shown on 11/40 days (1/11 from day 30); asym (up+down) range -2.30..+0.40
RESULT both-every-solve cadence 120 min: card NOT shown on 3/40 days (0/11 from day 30); asym (up+down) range -1.92..+0.17
```

Example (30 min, day 39): published −77.64 / +76.40. That is monotone and correctly signed. The card still renders "Not shown yet: … did not price in the order heating does".

Two causes, both open:
1. **The held estimator is not convex across intraday starts.** In the `both-every-solve` control, both tiles come from every solve, and it is still concave by up to 2.3/month on 11 of 40 days. Midnight-only sampling hides this.
2. **The rotation adds sampling asymmetry.** At 120 min it rises from 3/40 to 30/40.

`optimization_interval` is a user setting (10–120 min, default 30, `config_flow.py:1730`). So the PR's premise ("heat loss grows with the gap, so comfort's cost is convex … within the one unit two roundings open") fails at the default setting, on the fixer's own house. Item 8 then shows up as a hidden row instead of a contradictory one.

A fix has to make the render check agree with what the estimator and its sampling can actually guarantee. Options include pairing the two degree tiles in one turn, a tolerance derived from the measured asymmetry, or checking only the sign. The harness also needs an arm that samples like production and applies the card's predicate.

### B2. Step 1, mutation proof: MB5 does not reproduce, because its only killer depends on the clock

The body lists MB5 (`monthly_held_cost_delta` from `predicted_cost`) as killed by "#2257: at the real what-if seam …". The body itself says `_solve_coord` anchors on the real clock.
At this head, with the same replacement, `python3 tests/features.py` → `ALL 4276 FEATURE CHECKS PASSED` (rc 0) at 15:53 UTC, and again at 16:09 UTC (`ev/mut_MB5_rerun_features.log`). The seam check printed the plan's figures under the mutant, `(-63.76, 97.70)`; they satisfy `down < 0 < up` and `up + down >= -1`.
So the one line that makes the tile read the held figure, rather than the transient the owner complained about, is pinned only at some times of day. A reviewer at another hour would see it killed, which is how the body recorded it. A clock-independent check is owed: for example a fixed start, or a seam case where the plan's single-solve delta is non-monotone and the held one is not.

## Non-blocking findings (fold into the re-cut)

- **MX1 (reviewer's mutant) survives.** Deleting `"price_tiles": price_tiles.book(self),` from `_schedule_ledger_save` passes `tests/features.py` (4276) and `tests/finite_boundary.py` (rc 0). So the body's claim that "the days persist with the ledger, so a restart does not start the mean over" is not pinned on its save side.
  - The load side is pinned: MX2 (the `restore` call deleted) turns finite_boundary's round-trip null control red (`changed=['ledger']`).
  - MX3 (`comfort_temp_day_weekend` dropped from `_SIM_OVERRIDE_CONFIG_CASTS`) is killed by "every level a degree moves is one the what-if applies".
- **Step 9: there is no committed finder harness** for owner items 6, 7 and 8. `dev/audit/harnesses/r10_advisor_degree.py` is this PR's own instrument. The body uses it throughout but never says in words that it is the fixer's, not the finder's; it should. I measured with it at the head because no finder instrument exists. I also ran the carry's named harness, `r10_sav_null_terms.py const`, at both ends: identical RESULT lines (`ev/sav_null_const_{base,wt}.txt`), flat by design.
- **Null control (carry 1).** The held figure reads +54.4 against +59.4 realised per delivered degree (−8.4 %, inside the fixer's own 15 % bound). But the plan delivers only −0.514 K / +0.327 K per degree of setting, so the tile overstates what moving the setting saves by roughly 1.8× and 3×. The body discloses this. Whether "a degree cooler ≈ 54" is the right copy for a button that moves the setting is a question for the judge or owner, not a block here.
- **Mixing.** The 30-day mean mixes days priced at different schedules (after a target change, or an away setback that shifts `comfort_temp_day`). The overrides kept on the tile are only the latest. Not measured; stated so the re-cut can decide.
- **Forward-carry (step 10).** The R10-UX-HEALTH and R10-LIVESTATE carries are written only in the PR body. The roster at `origin/handoff/audit-r10-roster` `c185c7257199` does not yet contain them (the body says the orchestrator writes them). The orchestrator must land them before merge.

## Verified as claimed

- Mutation proof, re-run at this head, each in its own detached worktree (`ev/mut_*.txt`):
  - MC1 → 5 card checks red; MC2 → 1; MC3 → 2; MC4 → 2. These are the exact names the body gives.
  - MB1 → 4 feature checks red, including the seam check (held 0.0 / 0.0).
  - MB2 → 3 red: rotation, held-vs-plan, errored-answer. The seam check passed here (clock).
  - Reviewer's MC5 (the no-row line deleted) → 1 red; MC6 (step line removed) → 2 red.
  - MB3 → 1 red (the 30-day mean check); MB4 → 1 red (day-by-day restore). These are the names the body gives.
- At this head:
  - `node tests/card.mjs` → `ALL CARD CHECKS PASSED`.
  - `python3 tests/features.py` → `ALL 4276 FEATURE CHECKS PASSED`.
  - `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- Harness `r10_advisor_degree.py` (sha1 `5d9584280158452f7527409a55131b771401534d`, identical to the body's):
  - The `days` RESULT lines reproduce exactly (base 5/40, 3/40, std 48.5/48.6; head 0/40, std 29.6/29.5; published 0/11, std 1.1).
  - The `null` arm reproduces exactly (+59.4, +54.4, −8.4 %, first-solve +145.6 / +85.1, delivered −0.514 / +0.327).
- Step 4: the card claim adds `advisor_page` only, and `claims-for: 7.0.2` = `VERSION`. No solver golden is touched. card_drift and env_drift were not re-run; I cite CI (`fast`, `browser`, `env-matrix`).
- Step 5: `VERSION`, `manifest.json` and `RELEASE_NOTES.md` are untouched (empty three-dot diff stat).
- Step 7: the head named in the body is `21eeb5b2…`, the head measured.
- Step 13: `git merge-tree --write-tree origin/main 21eeb5b2…` → tree `a9ab834e…`, rc 0, no conflict (`ev/merge_tree.txt`).
- Step 14:
  - Every budget moves down: `max_class_loc` 8541→8514, `class_excess_loc` 18299→18272, `coordinator_attrs` 148→147, `seam_cut_total` 718→710.
  - The moves are earned by removing `_price_tiles` and `_price_tile_specs` into `price_tiles.py`. The side table follows an established pattern (`WeakKeyDictionary` in `boost.py`, `early_cutoff.py`, `debugger.py`, `log_latch.py`), so it is not an instrument game.
  - Architecture score taken from CI `arch-score`, green.
- Step 11 (CI read at this head; every run on `21eeb5b` has concluded, `ev/ci_checkruns_21eeb5b.tsv`):
  - `mutation` is red: `MUTATION TABLE REFUSED … 17 of them added by this diff`, all `price_tiles.py`. The body names it under "Red checks" and answers it with `ci_predict.py` as the cheaper detector. That is answered.
  - `nightly-status` is red; it grades main, and this diff does not reach what it reads.
  - Everything else is green or skipped, including `fast (3.14)`, `closures`, `coverage`, `browser`, `mutation-pins (1-4)` and `mutation-autofix`.
  - A green `pr-contract` started at 16:19:00Z, after the last run concluded (`mutation-autofix`, 16:15:25Z). Step 11's precondition holds.

## Head (step 12)

I measured `21eeb5b2325bf6a99f2a282f2e38bafbee44ab70`. At posting time the branch head is `441d19932f40475ddc0420f3b67ba8d90202eb2c`. That is `github-actions[bot]`'s `ci: pin killed mutants` (16:15Z), the `mutation-autofix` commit `ci-autofix.md` tells seats to wait for.
- It adds 16 `tests/mutation_ledger/killed_by/price_tiles.py/*.json` files and nothing else: no production code, test script, harness or claim file. So every figure above carries to it unchanged, B1 and B2 included.
- `git merge-tree --write-tree origin/main(49c222280) 441d1993` → rc 0, clean (`ev/head_moved.txt`).
- The move is the autofix bot's, not the fixer's, so it is not a `head-moved` violation.

## Reviewer-built instruments (step 9 disclosure)

`ev/tools/rotation_probe.py` (production-cadence rotation, with the card predicate), `ev/tools/stub_fidelity.py`, `ev/tools/mutants.py` and `ev/tools/run_mutant.sh` are mine. They were built because no finder harness exists for owner items 6 to 8, and the fixer's harness does not sample the way production does. They are evidence for this verdict, not a committed instrument. A re-cut should carry the rotation arm into `r10_advisor_degree.py`.
