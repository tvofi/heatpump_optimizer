Part 3, the last part, of outside pull request #3435. Thank you, Bankaifan, for #3435 and the live-install report behind it. Your commit b785556645 (the DEBUG reasons, the frozen phase and its card strings) is kept with your authorship, cut from your one commit as part 1 and part 2 cut theirs. Our changes are separate later commits. This is the last part, so the orchestrator closes #3435 with thanks once this merges. Stacked after R10-OUTSIDE-LEARNER-ROBUSTNESS-P2 (handoff 594238bfda, not yet on main): this head merges that handoff, so the diff against main carries part 2's commits too. Part of #201.

**The scaled settling tail lands here (owner ruling tvofi 2026-11-12, Carry 2).** Part 2 shipped the full 12 h tail for every boost length under an orchestrator ruling that the owner overrode. `boost.settle_tail` now prices the tail on `BoostState.space_boosted`, the boosted time summed since the learners were last free: `12 h + 6 h * ln(boosted / 2 h)`. That is the contributor's equal-residual slope (`slope6h` in `dev/audit/harnesses/boost_press_tail_walk.py`), with a floor of 1.5 h (the interval learners' longest sample, `HOUSE_LOSS_MAX_SAMPLE_HOURS`, moved to `const.py`). The full tail applies from the window's length on and to a sum with an unseen start. Under the flat-price null control below it is measured against part 2's shipped full tail. The absolute-bound acceptance that part 2's BLOCKED.md reported unmet is not the acceptance here: the owner ruled that the scaling lands.

What ships, by brief item:
- Reasons at DEBUG. `close_span` logs one line for a span the counter closed or refused, through `log_close`, which returns before any formatting with DEBUG off. The house heat-loss learner's gates return through `learner_progress.log_skip`, which passes the reason's values to the logger as arguments (CHANGE b). Nothing is logged above DEBUG.
- (a) No helper and no reason string is added to `coordinator.py`. `log_skip`, `pauses` and `Freeze` live in `learner_progress.py`. `learning_freeze` and `freeze_end` live in `boost.py`. The coordinator passes what it already holds: `learner_freeze_reason`, and itself to `boost.learning_freeze`. `tests/structure.py` passes with no budget raised (Figures).
- (c) One source. The phase reads `learner_freeze_reason`, the reason the learners recorded this cycle and that the sensor publishes, so the card and that sensor name the same reason. Asking `_learning_frozen` again from the payload builder measured +2 on `seam_cut_total` (423 > 421) and was not kept. When two reasons hold at once, `_learning_frozen`'s own order picks the one recorded. An unusable reading ranks above the boost, so a stale power reading during a boost records `stale:power_entity`. The learner then shows frozen with no end, and the card says "Paused until its inputs are usable again.", never "after a boost". Pinned by "P3 one source: another reason has no boost end..." and the card check "P3: a learner held for a reason with no line of its own says paused, never the raw key...".
- (d) Census, `learner_progress.pauses`, pinned per reason by "P3 census: ...":
  - frozen, with an end: the boost (`boost_space`). The end is `BoostState.freeze_end`: the live overlay's end plus the full tail its whole window owes, else the running `space_settle_until`. There is no end in the global boost mode, which ends when the user leaves it.
  - frozen, no end: an open window (`ventilation`) and an unusable reading (`<problem>:<key>`). Each holds the learner until something changes that has no forecast.
  - keeps its count: the early cut-off (one interval, gone next cycle), unmetered power and an unread room (properties of the install that never end, so a pause would promise a resume), `not_configured:` slots, and the plant states the pump signals (external heat, defrost, offline, fault, cooling), which come and go within cycles.
  - also keeps its count: a problem on the hot-water or buffer probe. Those learners record their own probe there, and it holds neither fabric learner.
  - The reason travels in `waiting_for`, so a new reason needs no new phase. A reason with no card line of its own renders the generic paused line in English, Swedish and German, never a raw key.
- (e) All four learners in `learner_progress_view` read one freeze. The house learner returns at its `_learning_frozen` gate before folding. The lower learner calls `_learning_frozen` with the same keys plus its probe. The solar aperture (`_fold_solar_aperture`) and the internal gains (`_fold_internal_gains`) fold inside the house learner's cycle, after that gate. The boost holds each of them, and none has a gate of its own that the boost leaves open.
- (f) While an overlay is live, the end is a forecast. A cancel after 10 min moves it earlier (to the cancel plus the 1.5 h floor), and a second press moves it later (to the new window's end plus the full tail of the summed time). Both are pinned with their values ("P3 end: ..."). An end past midnight shows the day (`fmtExpiry`; card check "P3: an end past midnight shows the day...").
- (g) No README.md or docs/ page lists the learner phases or the health row's texts. `docs/architecture.md` names the module and "phase, progress and what it waits for" only, so no page gains a line.
- KEEP: the frozen phase ranks above the weather wait and below off. `frozen_until` is a key of the frozen phase alone. The card says paused and until when, or paused while a boost runs where the end is unknown.

Carries:
- Carry 0 (cc8a67d1) lands here: part 3 as briefed.
- Carry 1 lands here: the same part, stated again.
- Carry 2 (owner ruling 2026-11-12) lands here: the scaled tail, measured under ## Figures with the flat-price null control.
- Carry 3 (e8e004db) lands here: the end is projected through `BoostState` and no tail is recomputed. The live overlay's projection equals the full tail, because a window run to its end has boosted at least 2 h. Projecting through `settle_tail` was an equivalent mutant (M7 survived) and was replaced.

Also fixed from the earlier seat's tip (5657ccc6b0). `boost.learning_freeze` was never called: the payload passed no freeze, so the frozen phase could not appear (`tests/structure.py`: `dead_top_level_symbols 2 > 1`). The second read of the global mode in `boost.py` counted as a coordinator private reach (archscore 2 -> 3, inadmissible). Both reads now go through `_mode_live`.

## Head

6caf7df2faf4848a36fba6030901d309af58695f, on merge base 870238eb21 (origin/main at 870238eb21; this head merges it). The two merges after 604c4994b0 bring no production file and none of this part's files: d9270211c0 brings two delivery rows, a triage note and tools/ci/selftest_closures.json, and 870238eb21 brings seat tooling, `tests/card_browser.mjs`, `tests/gate_lock.py` and main's `r10_open_driver_mutants.py` (`git diff --stat 43e9547455 870238eb21 -- custom_components` prints nothing). So the scoped gate, the walk and the mutants stand as measured at 604c4994b0 and 3d7e57dd48; `tools/pr/prepr.sh` was rerun at this head. Measured 2026-11-12 UTC.

## Mutation proof

Instrument: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/learner_freeze_mutants.py` at 3d7e57dd48. Each mutant is applied in place, then the part's block of `tests/features.py` (from `# R10-OUTSIDE-LEARNER-ROBUSTNESS-P3: the frozen learner phase` to the end; 7 checks, all passing unmutated) or `tests/card.mjs` is run, and the file is restored. Result: `MUTANTS: as expected`.

- M0 null (a comment line before `pauses`): 0 red. The null mutant survives.
- M1 the frozen arm removed from the card's `learnerPhase` (`if (false)`): 3 red in tests/card.mjs: "a learner a boost holds says it is paused and until when, not a count standing still", "P3: a learner held for a reason with no line of its own says paused, never the raw key; a count renders as on main", "P3: an end past midnight shows the day, not the clock time alone...".
- M2 the frozen phase ranked below the weather wait: 1 red, "P3 null control: with nothing holding the learners the payload is main's...".
- M3 `frozen_until` emitted outside the frozen phase (`if True:`): 1 red, the same payload null-control check.
- M4 the payload passes no freeze: 1 red, "P3 one source, wired: ...".
- M5 the hot-water and buffer probes pause the fabric learners: 1 red, "P3 census: ...".
- M6 the global boost mode given an end: 1 red, "P3 one source: ...". It survived at first, because the mode's coordinator held no tail. Fixed in 3b812f3a42.
- M7 the skip reason formatted before the level check: 1 red, "P3 null control: a skip reason is passed to the logger as an argument...".
- M8 a span line logged with no counter: 1 red, "P3 null control: an install with no heat counter closes no span and logs no span line...".

Part 2's harness, rerun on the scaled tail's lines: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/boost_tail_mutants.py` at d9a57e9934: `MUTANTS: as expected`. M0 null: 0 red. M1 full tail (`settle` prices the full tail, the scaling dropped): 6 red. They are the 38 s/window/click check, the back-to-back sum, the sum clearing, the mode restored, the restart keeping the sum, and the sweep. The literal-values check ("the scaled tail: floor 1.5 h to 10 min, ...") calls `settle_tail` directly, so M1 leaves it green; it pins the formula's values, not their use. M2 sum dropped: 4 red. M3 persisted tail dropped: 2 red. M4 restore dropped: 1 red. M5 sum never clears: 1 red.

## Null control

- No boost and no tail: the payload of every learner equals main's, with no `frozen_until` key, and the weather wait still shows ("P3 null control: with nothing holding the learners the payload is main's..."; M2 and M3 turn it red).
- The card renders every existing phase with its text on main ("... a count renders as on main"; `node tests/card.mjs`: `ALL CARD CHECKS PASSED`).
- An install with no heat counter closes no span and logs no span line at DEBUG. A span the counter closed logs exactly one ("P3 null control: an install with no heat counter..."; M8 turns it red).
- DEBUG off: a reason value whose formatting raises is passed through untouched ("P3 null control: a skip reason..."; M7 turns it red).
- The scaled tail: a window run to its end owes the full 12 h, as on main and in part 2. Every expired boost in the sweep owes exactly the full tail.
- Flat prices: see ## Figures.

## Figures

<!-- figure-block: scope-line mb=870238eb2194c99ae1ad6f1f78e0665e838c70f3 head=6caf7df2faf4848a36fba6030901d309af58695f -->
~~~text
MODE: SCOPED -- 29 script(s) run, 4 scoped out.
~~~
<!-- /figure-block -->

The scaled tail against part 2's shipped full tail. Walk of the house heat-loss scale per arm on `tests/boost_drift_replay.py`'s replay. `worst` is the largest signed excursion of a 03:00 daily row on or after the first boost day from the row before it, and `final` is the last value's excursion. Presses are at 07:00, 12:00 and 18:00 on both boost days. `press` arms carry the boost heat. Each `freeze` twin runs the same presses and tails with the house on the plan, so it has no heat behind it.

Real prices: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/boost_press_tail_walk.py production slope6h full` at 3d7e57dd48: `PRODUCTION: EQUAL to slope6h on 10 of 10 arms`, exit 0. `null_no_boost`: +0.0045 / +0.0236, as in part 2's figures at its merge base.

| arm | production (scaled) | its freeze twin | full (part 2) | its freeze twin |
|---|---|---|---|---|
| 10x1 | +0.0028 / +0.0227 | -0.0032 / +0.0222 | -0.0045 / +0.0226 | +0.0052 / +0.0252 |
| 30x1 | -0.0129 / +0.0204 | -0.0207 / +0.0176 | -0.0045 / +0.0229 | +0.0052 / +0.0252 |
| 60x1 | -0.0045 / +0.0205 | -0.0045 / +0.0236 | -0.0045 / +0.0205 | -0.0045 / +0.0236 |
| 120x1 | -0.0045 / +0.0216 | -0.0045 / +0.0221 | -0.0045 / +0.0216 | -0.0045 / +0.0221 |
| 10x4 | -0.0045 / +0.0214 | -0.0045 / +0.0221 | -0.0045 / +0.0214 | -0.0045 / +0.0221 |

Flat-price null control: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/boost_press_tail_walk.py --flat production full none` at 3d7e57dd48. Every day's price is its own mean, so the plan has no price reason to move heat between hours. The run prints `PRODUCTION: DIFFERS to full on 6 of 10 arms` (the scaling is seen) and `NULL CONTROL: none differs from full on 5 press arm(s): SEES`. It exits 1 because production differs from full, which is the harness's design when `slope6h` is not in the run. `null_no_boost`: -0.0056 / +0.0048.

| arm | production (scaled) | its freeze twin | full | none (no tail) |
|---|---|---|---|---|
| press 10x1 | -0.0049 / +0.0000 | -0.0118 / +0.0022 | -0.0150 / +0.0056 | -0.0049 / +0.0035 |
| press 30x1 | -0.0200 / +0.0029 | -0.0286 / -0.0039 | -0.0150 / +0.0057 | -0.0062 / +0.0025 |
| press 60x1 | -0.0150 / +0.0018 | -0.0150 / -0.0008 | -0.0150 / +0.0018 | +0.0052 / +0.0056 |
| press 120x1 | -0.0150 / -0.0029 | -0.0150 / +0.0040 | -0.0150 / -0.0029 | +0.0390 / +0.0094 |
| press 10x4 | -0.0150 / +0.0049 | -0.0150 / +0.0040 | -0.0150 / +0.0049 | -0.0049 / +0.0060 |

What the two runs show. The scaled tail changes only the short single presses (10 and 30 min). From 60 min of summed boost on it equals the full tail, at both prices. On 30x1 it walks further than the full tail: -0.0129 against -0.0045 at real prices, and -0.0200 against -0.0150 at flat prices. In both runs the heat-free freeze twin of that arm walks further still (-0.0207 and -0.0286). So the excess comes from which samples the shorter freeze skips, not from boost heat folded into the learner. With the heat removed and the price shape removed, the freeze alone accounts for it. On 10x1 the scaled tail walks less than the full tail at both prices. The no-tail arms (`none`) show what the tail exists for: press 120x1 walks +0.0390 at flat prices and +0.0441 at real prices (part 2's figure), against -0.0150 and -0.0045 with any tail.

Both walk runs and both mutant harnesses were measured at 3d7e57dd48, before origin/main 43e9547455 was merged (604c4994b0). Neither that merge nor the test-only commit 1d5ad27f2b changes a line of `boost.py`, `learner_progress.py`, `heat_energy.py`, `tests/boost_drift_replay.py` or the three harnesses: `git diff 3d7e57dd48 604c4994b0 --stat -- custom_components/heatpump_optimizer/boost.py custom_components/heatpump_optimizer/learner_progress.py custom_components/heatpump_optimizer/heat_energy.py tests/boost_drift_replay.py dev/audit/harnesses/boost_press_tail_walk.py dev/audit/harnesses/learner_freeze_mutants.py dev/audit/harnesses/boost_tail_mutants.py` prints nothing. It does change `pump_arbiter.py` and `store.py` on main's side, and the replay drives the coordinator, so the walk was not re-measured after the merge. The gate's `tests/boost_drift_replay.py` passed at the head.


- Feature blocks at 1d5ad27f2b (the head's tests; the merge after it brings only main's): `python3 tools/audit/seat/features_block.py "# R10-OUTSIDE-LEARNER-ROBUSTNESS-P3: the frozen learner phase"` (with its `--emit-prelude`): `ALL 7 FEATURES BLOCK PASSED`. Part 2's block (`"# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)" "# A hot-water charge inside a counter span (the dwell saw it)"`): `ALL 14 FEATURES BLOCK PASSED`.
- Scoped gate: `GOLDEN_MODE=drift GATE_SCOPE=auto tests/run.sh` at 604c4994b0 (the head): `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`, `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`, among them `tests/features.py` (`ALL 5383 FEATURE CHECKS PASSED`), `tests/card.mjs`, `tests/boost_drift_replay.py` and `tests/stress.py`. The same gate was green at 8a4c9b2799, before origin/main 43e9547455 was merged.
- `node tests/card.mjs` after `python3 tests/plan_view.py`, on the head merged with origin/main: `ALL CARD CHECKS PASSED`.
- `python3 tests/structure.py`: exit 0, no budget raised and none re-recorded.
- `python3 tools/audit/archscore/score.py --diff 43e9547455`: `Architecture score: dS +0.0246 IMPROVES` (coord_footprint 2492 -> 2491, literal_clone_copies 120 -> 118).
- `python3 tools/pr/ci_predict.py`: `no closures, fast, governance or instrument red predicted`, after six stale ledger pins on rewritten lines were deleted (8a4c9b2799) and the mutants harness was classified (`--apply-inert`, b050d7de43).
- No golden under tests/golden/ moves, and neither claim file is touched: `git diff 43e9547455...HEAD --stat -- tests/golden` prints nothing.

## Unpinned sites

- custom_components/heatpump_optimizer/boost.py:97 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:97 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:99 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:99 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:101 CLAMP_DROP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:101 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:168 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:168 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:173 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:175 CLAMP_DROP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:175 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:190 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:190 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:190 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:192 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:197 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:203 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:288 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:288 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:356 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:361 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:398 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:400 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:402 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:430 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:432 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:528 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:560 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:566 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:566 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:568 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:613 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:613 CMP_BOUND: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:613 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:618 CMP_BOUND*2: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:621 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:621 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:624 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/boost.py:624 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/coordinator.py:1776 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/coordinator.py:5777 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/coordinator.py:5828 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/heat_energy.py:563 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/heat_energy.py:563 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/heat_energy.py:565 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/heat_energy.py:577 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/heat_energy.py:582 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:148 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:150 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:153 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:169 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:194 BOOLOP: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:194 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:196 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:219 GUARD_OFF: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof
- custom_components/heatpump_optimizer/learner_progress.py:221 RETURN_DEL: pinned by mutation-autofix (its lane mutates custom_components/); the part's own checks kill the mutants named under ## Mutation proof

Diff survivors that `tools/pr/prepr.sh` named, with `MUTANT_CMD` running part 2's and part 3's blocks. Four were killed in 1d5ad27f2b: the three `_clear_spent` sites and `space_boost_active`'s return ("a spent sum clears on an expiry alone, on a press alone and on a mode entered alone" and "P3 one source ..."). The rest are dispositioned here:
- custom_components/heatpump_optimizer/boost.py:97: survivor (prepr.sh diff mutants: CMP_BOUND `>`), equivalent: at a sum of exactly 2 h the formula gives 12 h + 6 h * ln(1) = the full tail either way
- custom_components/heatpump_optimizer/boost.py:168: survivors (CMP_BOUND `>=`, CONST_SWAP `> 1`), equivalent at the coordinator's cycle: at equality the same instant is stored, and a tail at most 1 s later than the running one is not observable by a learner that runs once a cycle
- custom_components/heatpump_optimizer/boost.py:175: survivor (CONST_SWAP `max(1.0, ...)`), equivalent within a second: it differs only for a boost that ran under 1 s, which then adds 1 s to the sum; alone that sum owes the 1.5 h floor either way, and added to other boosts it moves the tail by at most tau/sum per second (35 s at the floor's edge), below the cycle's resolution
- custom_components/heatpump_optimizer/boost.py:190: survivors (CMP_BOUND `>=`, CONST_SWAP `> 1`), equivalent at the cycle's resolution: equal ends return the same instant, and an end at most 1 s apart is not observable on the card's minute clock
- custom_components/heatpump_optimizer/boost.py:197: survivors (CMP_BOUND `<`, CONST_SWAP `<= 1`), equivalent at the cycle's resolution: they move when a spent tail clears by at most 1 s, and the next cycle clears it either way
- custom_components/heatpump_optimizer/boost.py:234: survivor (CALL_DEL), unreachable: `_expire_one` is called only for blocks, with `settle=False` (`expire`), so its space-settle branch never runs; main's code, not this diff's

## Red checks

- `mutation` at 604c4994b02a: red by construction. Of the 56 sites under `## Unpinned sites`, 9 are `tools/pr/prepr.sh`'s diff survivors, each dispositioned there as equivalent or unreachable; the rest are sites mutation-autofix pins after the push. Cheaper detector: `tools/pr/ci_predict.py` and `prepr.sh`'s diff-mutant step, both already run locally at no added standing cost, named every site before the push. The red is the lane's own pinning step, not a defect, so no countermeasure is owed.

## Forward-carry

none

## Friction

none
