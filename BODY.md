A live v6.7.17 install never produced a COP sample. It has a 14 kW nameplate maximum, and its pump draws 1.9-2.55 kW. The duty floor was `max(0.3 x max_electrical_power, 0.2)` = 4.2 kW, above every draw, so the observed-COP sensor stayed unavailable and the flow-lift fold was starved too. All numbers below are synthetic. This is the round-6 body, a re-cut (`fixer.md`, "Past three rounds, re-cut rather than repair"): the headings, the arms that fire, and only figures re-taken in this pass. Round history is deleted except one disclosed self-correction, in `## Red checks` under `nightly-ha (stable)`.

**Stacked on #2065 (7a): this PR merges after #2065.** The branch contains #2065's round-3 head `1e957282e`; its diff over that head is this fix, and `origin/main b2b6acd64` is merged in (merge, never rebase).

**The fix**, decided under tvofi's mandate and the #201 decisions:

1. **Floor.** `ThermalParameters.flow_lift_power_floor_kw` is `max(0.8 x min_electrical_power, 0.2)`, or the nameplate third (`nameplate_power_floor_kw`) when no modulation floor is configured. It always applies, to both the COP fold (`MeasuredCop.judge_floor`) and the flow-lift fold.
2. **Departure from the ask** (`MeasuredCop.judge_ratio`). An interval whose metered draw departs from the plan's ask by more than `COP_ASK_TOLERANCE` (0.15) is judged on #2065's running-draw evidence, `draw_range.follows_ask`:
   - **Evidence that the draw follows the ask** (the log-log slope of drawn on asked is at least 0.5): it folds, as an efficiency shift.
   - **Evidence that it does not:** refused as `draw_off_ask`, a pump that sets its own power.
   - **No evidence yet** (fewer than 48 running samples asked at or above the floor, or asks that never span 15 %): it folds only where base would have, with the ask and the drawn figure both clearing the nameplate third. Otherwise refused as `awaiting_draw_evidence`.

   So no install folds a departure that base refused before the evidence exists, and an install whose asks never span 15 % keeps base's reach for its departures. The equivalence to base holds for departures only: inside the 15 % tolerance the new, lower floor applies with or without evidence, so in-tolerance intervals fold where base's floor refused them -- including a self-setting pump's in-tolerance intervals during the first 48 running samples, which is why probe 3b reads 0.636 -> 0.590.
3. **Refusal reason.** `MeasuredCop.refusal` holds an `accuracy.COP_REFUSED_*` code, published in the `cop_learner` diagnostics row (`last_refusal`, `measured_cop`, `power_floor_kw`, `draw_follows_ask`), registered in #2065's `diagnostics._VIEWS`. The dump is available whether or not the sensor is.
4. **Persistence.** The measured COP, its curve and the tank temperature persist under `thermal_learning/measured_cop/*` (store version 1). The draw evidence is #2065's `draw/samples` in the accuracy store.

**Corrections carried from earlier bodies.** The evidence wait is 48 running samples whose asks span at least 15 % -- at the default half-hour cadence at least 24 hours of such running -- not "one day". `judge_ratio`'s docstring no longer claims that no error is beyond reach.

**Behaviour change, disclosed.** A fixed-speed pump (min = max) gets a higher floor wherever `min > 0.375 x max`: 50 % and 70 % duty-averaged intervals are refused, and 85 % folds at both ends.

**What round 6 adds.** No production line. Twelve `features.py` checks that state the boundaries the guards were written for, 20 `killed_by` rows and 5 `survivor_triage` rows -- the dispositions round 5's block said were missing (its seven measured survivors are marked *(r5 survivor)* in `## Unpinned sites`), and one merge: `origin/main` into the branch, whose `tests/closures.json` conflict resolved to the merge driver's own bytes.

## Head

`b511f9dc5b9ee076d3113aaad4b9e296222bbd7c` (code head). Parents: `origin/main b2b6acd64cde652676a568e93c05f021571ebe5e` (merged in this pass; merge base and ratchet base both) and #2065's round-3 head `1e957282e`.

`git diff --stat 16c06fd32 HEAD -- custom_components/` is **empty**, so the production tree is byte-identical to the head round 5 reviewed and every harness and probe row below carries rather than being re-taken; what differs is `tests/features.py` (+12 checks), the mutation ledger (+20 `killed_by`, +5 `survivor_triage`), and `tests/closures.json` (the merge). `git status --porcelain` is empty at the head.

## Mutation proof

Each mutant is applied to a copy in its own worktree at `2808a8a94`, whose `accuracy.py` is byte-identical to this head (`git diff --stat 2808a8a94 HEAD -- custom_components/heatpump_optimizer/accuracy.py` is empty) and which is where M11-M13's lines are: all three mutate `MeasuredCop.judge_ratio` and its return arms. `coordinator.py` differs by one statement at :9641 (`power_frozen` read into a name instead of a walrus -- #2065's `e408b9a28` moved it after `2808a8a94`), on no line any M-row mutates. Round 3 measured them against the `features.py` block "COP learner duty floor keys on the modulation floor (live v6.7.17)", driven through the seat's filtered block runner, and against the harness and the probe rows; they are carried here rather than re-run, because the lines they mutate are unchanged at this head.

- M11, the no-evidence branch made to fold always: `with no draw evidence a departure folds only past the nameplate third: it waits for evidence on 14 kW and folds on 4 kW, as base` and the off-ask check fail. Harness `selfset_hourly` drops to 0.719.
- M12, the no-evidence branch made to refuse always: the same no-evidence check fails. Probe 7's `narrow_config_true0.75` reads 0/400 at 1.000 -- round 3's deadlock.
- M13, evidence that the draw does not follow made to fold: `a draw that ignores the ask (varying or flat) is refused as off-ask; a matched draw and a 0.7 shift on a draw that follows its ask still teach` fails. Harness `selfmod_independent_4kw` drops to 0.565.
- M6, M7, M9, M10 (round 3) and M1-M5, M8 (round 2) were not re-run; their lines are unchanged.

Round 6 adds a **condition-level measure**, because the driver the pins are recorded against cannot be run here: `tests/features.py` is red at baseline on this Mac at `R9-F2.1 P3` (a BLAS-kernel float, red at `origin/main` too -- see `## Red checks`), and `mutation_table.py`'s baseline guard refuses to drive from a red baseline. So for each site the pass left, the fixer copied the package, rewrote that one line to the operator's own `new` text, and re-evaluated the condition of the `R.check` that now names it. The command and its table are in `## Figures`; a condition that reads `False`, or raises, is a check the driver prints `FAIL` for, which is what `killed()` counts. Five sites showed **no** condition changed (`accuracy.py:680`, `accuracy.py:703`, `coordinator.py:4501`, `coordinator.py:4532`, `coordinator.py:4571`), and those five are the five `survivor_triage` rows -- that is the null control on the method: it says "nothing changed" when nothing changed, and it is what separates a mark of equivalence from a mark of convenience.

## Null control

#2065's head is the null for every harness and probe row. The matched-draw control is 96/96 at 1.000 at the head (harness) and 400/400 at 1.000 (probe 6). For the condition measure the null is the tree itself: all 18 conditions read `True` at the head (the `BASELINE` line of the measure's output), and the same measure returned no difference at all on the five sites that ended up in `survivor_triage` (four judged equivalent, one recorded as a gap).

## Figures

**The unpinned inventory, at this head.** `python3 /Users/timmalmstrom/hpo-seats/live-cop-floor/ev/r6/rederive_unpinned.py <merge-base>` -- a 45-line read-only probe that calls `inventory`, `unpinned_sites`, `base_unpinned_sites`, `diff_sides` and `added_unpinned` from `tests/mutation_table.py` and writes nothing; 8.0 s wall:

    ratchet base      b2b6acd64cde652676a568e93c05f021571ebe5e
    candidate sites   5970
    unpinned here     4620        (at the pre-pin head 630849897: 4647)
    unpinned at base  4623        (4624 at 47b083b03)
    added by this diff  13        (37 before this pass's rows)
    pass pool, new_unpinned  16   (42 at 630849897)
    ratchet_refusal   None        (1 before this pass's rows)

The count half of the ratchet is satisfied (4620 <= 4623); the per-site half still refuses, on the 13 named in `## Unpinned sites`.

**The cheap detector, re-taken.** `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` -- 18.2 s wall, static, runs no test and no mutant:

    CI PREDICT: 12 unpinned site(s) the diff adds -- a warning; the body owes each a line under ## Unpinned sites
    CI PREDICT: no closures or fast red predicted against b2b6acd64cde (a data-file read is not seen)

Twelve keys, because the predictor prints the two `draw_range.py:125 CMP_BOUND` sites under one key with `*2`; the lane's own `added_unpinned` counts them as two. (At the pre-pin head the same command listed 35.)

**Round 6's condition measure.** `PYTHONPATH=tests/hastub python3 /Users/timmalmstrom/hpo-seats/live-cop-floor/ev/r6/verify_kills.py FILE LINE KIND ...` -- copies the package to a temp tree with `__pycache__` excluded, applies one mutant, re-evaluates the 18 conditions. Every site listed in `## Unpinned sites` as a `killed_by` row appears there with its flip named; three output files are in the seat's `ev/r6/`. Baseline, at this head: all 18 conditions `True`. Examples, verbatim from that output:

    accuracy.py:678 CLAMP_DROP   mutant `if (asked_kw) < params...`
        differs: {'floor_both_operands': ('True', 'False')}
    draw_range.py:221 CMP_BOUND  mutant `return slope > FOLLOW_SLOPE_MIN`
        differs: {'ask_slope_half': ('True', 'False')}
    accuracy.py:680 RETURN_DEL   mutant `pass`
        differs: NO CONDITION CHANGED (survives the new checks)   -> triaged equivalent

**Gates run locally at this head.**

- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`, 23.4 s, no raise sought or given.
- `PYTHONPATH=tests/hastub python3 tests/features.py` -> `1 of 3929 FEATURE CHECKS FAILED`; the one failure is `R9-F2.1 P3`, the known BLAS-kernel float that is red on this Mac at `origin/main` as well (the same run at the pre-merge head read `1 of 3917`, the same single failure). The block this PR owns -- 12 new checks -- is green: 3929 - 3917 = 12, and no new FAIL line appears.
- The scoped-gate selection: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` -> `MODE: SCOPED -- 29 script(s) run, 4 scoped out.` Run locally from that list: `structure` (above), `features` (above), `layout` (`rc=0`), `guard_pins` (`ALL 50 GUARD PIN CHECKS PASSED`), `harness_headers` (`ALL 109 HARNESS HEADER CHECKS PASSED`, which is the lane that reads `dev/audit/harnesses/`, and this merge brought a harness there from main), `tools/pr/ci_predict.py` (above). Left to CI as the heavy arms: `fast`, `mutation`, `slow`, `stress`, `optimality`, `golden`, `env_drift`, the card lanes and the nightly set -- tvofi's heavy-scripts ruling of 2026-10-07.
- `node tools/policy/brief_lint.mjs` exits 0 at this head and lists `carry-2065.json` and `carry-2066.json` among the files it reads, with no finding on either.
- The `tests/closures.json` merge resolution, checked against the driver's own bytes: `git merge-tree --write-tree origin/main 630849897` prints `LEDGER-MERGE: resolved tests/closures.json` and a tree, and `diff <(git show HEAD:tests/closures.json) <(git cat-file -p <that-tree>:tests/closures.json)` is empty (0 differing lines). The branch's only change to the table is `draw_range.py` added to 29 script closures (`git diff 47b083b03 630849897 -- tests/closures.json`: 29 insertions, 0 deletions, one path), carried onto main's re-sorted layout with `closure.canonical_text`; `closure.layout_errors` returns `[]`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` -> 46 FAILs, all in the `a3:`/`a4:`/`a5:`/`a6:`/`a8:`/`a9:`/`hb:` families: the checks that register the integration against the real Home Assistant package, which no stub provides and the container lane has not provided since 2026-10-04. **None** names the ledger, the triage marks or the closures, so nothing in that list is this pass's; CI's `fast (3.14)` is authoritative for them and was green at `630849897` (run 113738072766).
- Temp and machine paths: prepr's own step `temp paths` reports `tmp_paths: 0 refused, 0 stale allow entries at HEAD, ledger lines added since b2b6acd64cde`; independently, `git diff -U0 47b083b03 HEAD -- tests/ custom_components/ dev/ | grep '^+' | grep -cE '/Users/|/private/tmp/|/tmp/'` is **0**, because each `killed_by` reason states its method and the operator's own text rather than a path.
- The ledger's own validators, from `tests/mutation_table.py`: `ledger_form_problems` + `layout_problems` -> `[]`, `triage_problems` -> `[]`, `completeness_problems` -> `[]`.
- Claim files: `git show HEAD:tests/golden/claimed_drift.txt | shasum -a 1` = `19dec64ba863`, `git show origin/main:...` = `19dec64ba863`; `card_claimed_drift.txt` = `459c54964fa7` at both. This branch claims nothing, so both files are byte-identical to `origin/main`'s.
- `VERSION`, the manifest `version` and the `RELEASE_NOTES.md` heading are untouched: `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- VERSION manifest.json RELEASE_NOTES.md` is empty.

**Acceptance rows, carried from round 5's head** (the production tree is identical, `## Head`). Reviewer probes, base (#2065's head) -> head: probe 5 hourly/three-hour/flat `1.000/1.000/1.000 -> 0.978/1.000/1.000`; probe 7 `narrow_config_true0.75` `0.751 -> 0.751`, `wide_config_steady_week` `0.750 -> 0.750`, varied `0.750 -> 0.749`; probe 6 `matched` `356/400 -> 400/400` at 1.000, `selfset_hourly` `1.600 -> 1.170`, `partial_b0.3` `1.600 -> 1.375`, heat-led 0.7 rows unchanged within 0.002. The fixer's harness (`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py`, sha1 `9587bead80b5f4b103c510a9f46a4c70e3ea2a91`): `min1_running` `0/15 -> 15/15`; `selfmod_matched` `0/96 -> 96/96` at 1.000; `selfmod_independent` `1.000 -> 0.976`; `selfmod_independent_4kw` `0.636 -> 0.780` (the orchestrator accepted 0.780; the reviewer's prototype read 0.81 and the four variants tried here read 0.758 or 0.780); true COPs learned at 0.604/0.704/0.805/1.307 and `true_0.7_4kw` 0.704 at both ends; `fixed3_duty50`/`fixed3_duty70` `5/5 -> 0/5` (the disclosed change); `min3_running` `0/15 -> 3/15`, carried to 7b.

**The head round 5 actually ran.** `gh api repos/tvofi/heatpump_optimizer/commits/6308498975.../check-runs --paginate` -> 30 check-runs; `gh api ".../actions/runs?head_sha=..."` -> four runs, all `event: workflow_dispatch` (CodeQL, Validate, Hassfest, Tests). `mutation-autofix`, `mutation-pin-plan` and `mutation-pins` are `skipped` there, and `nightly-ha (stable)` is `completed | failure`, `nightly-ha (2025.2.0)` `success`, `nightly-status` `skipped`. `pr-contract`, `policy-docs`, `env-matrix`, `budget-raise-gate` and `wave-script` are absent -- governance.yml's contexts fire only on a `pull_request` event, and a `GITHUB_TOKEN` push from the bot created none.

## Red checks

- **`mutation`** -- the live cause at this head, not round 4's stale re-key. `tests/mutation_table.py --scope changed --base <merge base>` refuses because 13 sites this diff adds carry no disposition, all of them #2065's lines (`## Unpinned sites` names the 13 with the key each). The count half is satisfied: 4620 unpinned against 4623 at the ratchet base.
  - **Why it went red rather than being caught before the push:** the round-5 body disposed these rows as "left to `mutation-autofix`", and `ci-autofix.md`'s own rule makes that a refutable claim -- `apply_pins` pins measured kills only, and survivor triage is never automated. The seven sites the pass had already driven and left alive were therefore not repairs the bot could make, and no bot commit can reach this head at all: all three pin jobs require `github.event_name == 'pull_request'` (measured above -- three `skipped`).
  - **Cheaper detector and its standing cost:** `tools/pr/ci_predict.py` (prepr step 6d) -- static, no test and no mutant, **18.2 s** measured at this head, and it lists the sites the lane will refuse on before any push. Step 7d then refuses a body that disposes none of them. It has run on every push of this PR; what it did not do is distinguish "the bot will pin this" from "nothing will pin this", which is the claim that was wrong. The second, exact instrument is the re-derive probe above: 8.0 s, main's own functions, prints `added` and `ratchet_refusal` as the lane computes them.
  - **Not automated, deliberately:** `ci-autofix.md` forbids automating survivor triage, so the 13 sites left here stay a human disposition, and they are #2065's to make (its own `## Unpinned sites`, its own pass).
- **`nightly-ha (stable)`** -- **self-correction.** Round 5's body said "This PR's heads skip that lane". That was true of `pull_request` heads and is **false of this head**: the lane ran and failed at `630849897`, run 113738022964, because the head is the bot's `workflow_dispatch`, and the job's `if:` admits `schedule`, `workflow_dispatch`, or a `pull_request` whose `closure-scope` says `nightly_ha == 'true'`. The arm that failed is `hb:positive_control` -- `a 600 ms spin read as 600.2 ms; dump names the spin: True; py-spy rc=0 names it: False` -- with `run:exit_status` as its consequence; 62 of 64 checks passed, including every substantive assertion this fix could move (`entry:loaded`, `entities:registered` 51, `a3:roster` 79/79, `a9:reload_*` 5/5, `plan:*`, `a4:*`, `a16:*`, the whole contract set).
  - **Not this PR's failure, named by the arm rather than by ancestry:** main's own 2026-10-08 scheduled run 37753990323 failed **both** arms and its 2026-10-09 run 37909555545 passed both -- a live flakiness history on main on the arm that failed here. And `git diff --stat 47b083b03 origin/main -- tests/nightly_ha.py tests/ha_floor.py .github/workflows/tests.yml custom_components/` is empty, so main carries neither a fix this branch lacks nor a change to what the lane reads. The py-spy positive control (#1758) is the lane's own instrument, and `defect-root-cause.md`'s exemption applies: it grades outside this diff.
- **`nightly-status`** reports main's last scheduled run, not this diff. `skipped` at this head.
- **`pr-contract`, `policy-docs`, `env-matrix`, `budget-raise-gate`, `wave-script`** -- not red, **absent**, for the reason in `## Figures`. They will run at the next head, which is pushed as the App: an App push creates the `pull_request` run, and with it the pins pass this head could not have. This body therefore claims no bot pin for anything.
- **`mutation` at the next head, stated honestly:** 13 sites remain undispositioned, so the lane refuses there too. Its pool is now small: `new_unpinned` is **16 sites** at this head (42 at `630849897`, before this pass's 25 rows), and `pin_shard_count` sizes the matrix at six sites a shard and ten shards at most -- fed the refusal line these counts print, it answers 3, a capacity of 18. So unlike round 5's pass, which left 35 sites `skip-budget`, nothing in the pool is left undriven. Whatever it reports as a survivor comes back here for a disposition.

## Unpinned sites

Keys as `tools/pr/ci_predict.py --base origin/main` prints them (file:line KIND), for the 37 sites this diff added before this pass. 24 are disposed by this pass; 13 remain and are named first because they are the ones the lane still refuses on.

**Still undispositioned -- all of them #2065's lines, carried below this branch's merge base, and none of them ever driven by a pass** (round 5's pass reported them `skip-budget`, i.e. not started):

- `custom_components/heatpump_optimizer/draw_range.py:45 CONST` -- #2065's `RUNNING_FLOOR_KW`. No claim here; #2065's own body disposes it, or its pass pins it.
- `custom_components/heatpump_optimizer/draw_range.py:48 CONST` -- #2065's `WINDOW`, as above.
- `custom_components/heatpump_optimizer/draw_range.py:54 CONST` -- #2065's `LOW_PERCENTILE`, as above.
- `custom_components/heatpump_optimizer/draw_range.py:60 CONST` -- #2065's `DISAGREE_SHARE`, as above.
- `custom_components/heatpump_optimizer/draw_range.py:108 GUARD_OFF` -- #2065's `DrawRange._metered_range`, as above.
- `custom_components/heatpump_optimizer/draw_range.py:113 CLAMP_DROP` -- #2065's; `origin/fix/live-power-clamp-foundation-pr` already carries a `killed_by` row for it, so a merge of #2065's current head brings it.
- `custom_components/heatpump_optimizer/draw_range.py:122 CMP_BOUND` -- #2065's `DrawRange._disagrees`, as above.
- `custom_components/heatpump_optimizer/draw_range.py:125 CMP_BOUND*2` -- #2065's `DrawRange._disagrees`: two `CMP_BOUND` sites on the one line, which the predictor prints under this one key and the lane counts as two, as above.
- `custom_components/heatpump_optimizer/draw_range.py:149 GUARD_OFF` -- #2065's `DrawRange.planned`, as above.
- `custom_components/heatpump_optimizer/draw_range.py:296 GUARD_OFF` -- #2065's `planned_range`, as above.
- `custom_components/heatpump_optimizer/draw_range.py:305 CLAMP_DROP` -- #2065's `planned_range`, as above.
- `custom_components/heatpump_optimizer/thermal_model.py:1280 RETURN_DEL` -- #2065's `InstallCapability.plan_writes_power`; `origin/fix/live-power-clamp-foundation-pr` already carries its `killed_by` row, as above.

(Thirteen sites, twelve keys: the key ending `CMP_BOUND*2` is the two `draw_range.py:125` sites printed together.)

**Disposed by this pass.** `killed check` names the `features.py` check whose condition the operator's mutant flips, measured by the table in `## Figures`; `triage` names a `survivor_triage` row written here. The seven sites round 5's pass drove and left alive are marked *(r5 survivor)*.

- `custom_components/heatpump_optimizer/accuracy.py:678 CLAMP_DROP` -- *(r5 survivor)* killed check `the duty floor judges the smaller of the ask and the draw` (new).
- `custom_components/heatpump_optimizer/accuracy.py:678 CMP_BOUND` -- *(round 5 left it `skip-budget`, never driven)* killed check `the duty floor is exclusive: a draw exactly at it is running, not below it` (new).
- `custom_components/heatpump_optimizer/accuracy.py:680 RETURN_DEL` -- *(r5 survivor)* triage **equivalent**: `return None` is `judge_floor`'s last statement; `pass` falls off the end and returns None. Digest of all 147 asked/draw x modulation-floor answers identical at tree and mutant.
- `custom_components/heatpump_optimizer/accuracy.py:701 CLAMP_DROP` -- killed check `the tracking gate divides by the clamped walking ratio: a zero ewma is a refusal, not a crash` (new; the mutant raises `ZeroDivisionError`).
- `custom_components/heatpump_optimizer/accuracy.py:701 CMP_BOUND` -- killed check `the tracking gate is exclusive` (new; `1.5/5.0` is the double `0.3`).
- `custom_components/heatpump_optimizer/accuracy.py:703 CMP_BOUND` -- triage **equivalent**: no double `r` has `abs(r - 1.0)` equal to the double `0.15` (Sterbenz; the six neighbouring candidates measured at 0.1499999999999999 / 0.15000000000000013 / 0.1499999999999997 / 0.15000000000000002 / 0.15000000000000013 / 0.1499999999999999, none equal).
- `custom_components/heatpump_optimizer/accuracy.py:707 CLAMP_DROP` -- killed check `without draw evidence the nameplate bar is on both the ask and the drawn figure` (new).
- `custom_components/heatpump_optimizer/accuracy.py:733 CMP_BOUND` -- killed check `the store's 0.1 bar is exclusive` (new; a stored COP of exactly 0.1 reads back).
- `custom_components/heatpump_optimizer/accuracy.py:735 GUARD_OFF` -- killed check `a non-finite tank temperature drops the record whole` (new).
- `custom_components/heatpump_optimizer/coordinator.py:4501 CLAMP_DROP` -- *(r5 survivor, in the pass pool but not charged: the line is main's, moved by this PR's rename of `_learn_measured_cop`)* triage **equivalent**: `judge_floor` passing requires `min(commanded, measured) >= flow_lift_power_floor_kw`, and both arms of that property end in `max(..., 0.2)` -- measured over 21 config pairs the floor is >= 0.2 kW -- so `max(commanded, 1e-6)` cannot select its second arm. The guard stays for the cause it buys.
- `custom_components/heatpump_optimizer/coordinator.py:4532 CMP_BOUND` -- *(r5 survivor, likewise not charged)* triage **gap**, recorded rather than papered over: the arms differ only where `observed_cop` is exactly the double 0.1 while the interval has already passed the tracking gate and the ask tolerance; no driver in play constructs that, and the input exists, so it is not called equivalent. The guard's neighbours each have a check (off-ask, blended, modelled-zero, frost-band).
- `custom_components/heatpump_optimizer/coordinator.py:4571 RETURN_DEL` -- triage **equivalent**: last statement of `_fold_measured_cop`, same argument as `judge_floor`'s. Disposing it is also what frees the multiset slot the predictor had charged to `coordinator.py:6573 RETURN_DEL` (round 5 could not explain why two coordinator survivors appeared in no listing; `added_unpinned` compares an identical-text multiset per file, and this PR's new `return None` consumed the base's `_price_series` slot. At this head's base the charge lands on the right site and 6573 is not charged at all).
- `custom_components/heatpump_optimizer/draw_range.py:51 CONST` -- *(r5 survivor)* killed check `follows_ask gives evidence at 48 running samples and none at 47` (new). It survives the old check because that check builds its window with `range(draw_range.MIN_SAMPLES)`, so a doubled constant moves the test with it: a check that reads the symbol it is meant to pin.
- `custom_components/heatpump_optimizer/draw_range.py:111 CMP_BOUND` -- *(r5 survivor, #2065's line)* killed check `a metered top exactly 15 % under the configured max keeps the configured max` (new; `0.85 x 10.0` is the double `8.5` and the metered top is a data point at it).
- `custom_components/heatpump_optimizer/draw_range.py:112 CMP_BOUND` -- #2065's line; killed check `and a metered floor exactly 15 % over the configured min keeps the configured min` (new; reachable only at a configured min whose 0.15 is exact against the sample value -- 0.8 and 0.92, which is why the case is not written at 2.0).
- `custom_components/heatpump_optimizer/draw_range.py:207 GUARD_OFF` -- killed check `follows_ask: no evidence without the window ...` (already present; the mutant raises `AttributeError` on `draw.config`).
- `custom_components/heatpump_optimizer/draw_range.py:211 BOOLOP` -- killed check `a sample asked nothing is not a running level` (new).
- `custom_components/heatpump_optimizer/draw_range.py:211 CMP_BOUND` -- two sites, one key: `a >= floor` -> `a > floor` is killed by `asks spanning exactly 1.15 are evidence` (new); `a > 0.0` -> `a >= 0.0` by `a sample asked nothing is not a running level` (new).
- `custom_components/heatpump_optimizer/draw_range.py:213 CMP_BOUND` -- killed check `follows_ask gives evidence at 48 running samples and none at 47` (new).
- `custom_components/heatpump_optimizer/draw_range.py:216 CMP_BOUND` -- *(r5 survivor)* killed check `asks spanning exactly 1.15 are evidence (the span bound is `<`)` (new).
- `custom_components/heatpump_optimizer/draw_range.py:221 CMP_BOUND` -- killed check `a draw whose log-log slope is exactly 0.5 follows the ask` (new; asks 1.0/2.0 drawn 1.0/sqrt(2) give the slope as the double `0.5`).
- `custom_components/heatpump_optimizer/draw_range.py:221 RETURN_DEL` -- killed by all four `follows_ask` cases: `pass` answers None, which `judge_ratio` reads as *no evidence* rather than as a bool -- the difference between a fold and `awaiting_draw_evidence`.
- `custom_components/heatpump_optimizer/thermal_model.py:669 CMP_BOUND` -- killed check `with no modulation floor configured the nameplate floor still applies` (already present).
- `custom_components/heatpump_optimizer/thermal_model.py:669 GUARD_OFF` -- killed check `the duty floor is 0.8 x the modulation floor, never below 0.2 kW` (already present).
- `custom_components/heatpump_optimizer/thermal_model.py:671 RETURN_DEL` -- killed check `with no modulation floor configured the nameplate floor still applies` (already present; the mutant answers None and the sibling check's subtraction raises `TypeError`).

**Kill quality, stated as the review asked.** Every check named above is behavioural: it drives the production symbol (`MeasuredCop.judge_floor`, `judge_ratio`, `from_dict`, `draw_range.follows_ask`, `DrawRange.planned`, `ThermalParameters.flow_lift_power_floor_kw`) and asserts a property of the interval it judges, and each of the 20 `killed_by` rows this pass writes names `tests/features.py` (`git diff --name-only 630849897 HEAD -- tests/mutation_ledger` over the rows' own `killed_by` field: 20 rows, all `tests/features.py`; the 21st file in that list is main's own nightly kill). None of them is the dead-symbol ratchet.

For the record on round 5's commit: its 35 rows name `tests/features.py` 30 times, `tests/entities.py` twice, and `tests/structure.py` three times -- `_fold_measured_cop GUARD_OFF c31691cd`, `_fold_measured_cop GUARD_OFF f1f0e3c5`, `follows_ask GUARD_OFF 695c3a8d`. Those three are exactly the weakest kind the review priced (switching the guard off strands a helper and the ratchet refuses the growth), and they are the guard twins of the very lines whose `CMP_BOUND` and `CLAMP_DROP` mutants lived: `judge_floor`'s `GUARD_OFF` is named against `features.py` and is behavioural, `follows_ask`'s is not. The behavioural pricing of those two lines is what round 6's `asks spanning exactly 1.15` and `the duty floor judges the smaller of the ask and the draw` supply, and the surviving mutants are the evidence that nothing before them did.

## Forward-carry

- `dev/programme/carries/carry-2066.json`: to fix 3 (live learners), hold-then-replay. A departure seen before the evidence exists is held, then folded or dropped once `follows_ask` decides. Control: probe 6 `selfset_hourly` (1.170 here, right value 1.000) and harness `selfmod_independent_4kw` (0.780). Nulls: `selfmod_matched`, `true_0.7_4kw`.
- `dev/programme/carries/carry-2065.json`: to 7b, capping the floor at the observed running draw. Control: `min3_running_folded`.
- **#2065's own `## Unpinned sites`** receives the 13 sites named above, with the finding that changed how it must work: a check that builds its window from `range(draw_range.MIN_SAMPLES)` pins nothing about the constant, and #2065's pass left `CONST 6526d7f7` alive for exactly that reason. Two of the 13 already have rows on `origin/fix/live-power-clamp-foundation-pr`; the orchestrator's lever for the rest is #2065's own pins pass, not this branch.
- `dev/audit/rca/`: the recurrence the line-shift class started (round 4, twice) is owed a `root-cause.md` seat and is not this body's to write; this round adds a second instance of a related class -- **a disposition that names an actor which cannot act** (`mutation-autofix` at a dispatched head) -- whose named cause and cost test belong to that seat.

## Friction

- `ci-autofix`: unenforced: the three pin jobs require `github.event_name == 'pull_request'` (measured at `630849897`: three `skipped`, four `workflow_dispatch` runs), so a head that is the bot's own push cannot receive a pin, and a body that defers a measured survivor to `mutation-autofix` is not falsified by any check -- round 5's block found it only by reading the shard logs.
- `mutation-ratchet`: unclear: `--pin-killed` drives `new_unpinned` (by anchor) while the lane refuses on `added_unpinned` (by content multiset), and the two differ by 6 sites at `630849897` (5 in the pool but not charged, 1 charged but not in the pool) and by 5 at this head's pre-pass counts. Round 5 reported two coordinator survivors "named nowhere in the body's enumeration" and could not establish why; they are pool members that the ratchet does not charge, and one charged site (`coordinator.py:6573`) was not in the pool at all. The set difference is printed by the re-derive probe in `## Figures`, which is the instrument a seat needs before it enumerates.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
