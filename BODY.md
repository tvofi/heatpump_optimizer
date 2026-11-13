Part 3, the last part, of outside pull request #3435. Thank you, Bankaifan, for #3435 and the live-install report behind it. Your commit b785556645 (the DEBUG reasons, the frozen phase and its card strings) is kept with your authorship. It was cut from your one commit, as part 1 and part 2 cut theirs, and our changes are separate later commits. This delivers the remainder of pull request 3435 and leaves #3435 open for the orchestrator to close with thanks. Part 2 is on main as 0731b35877 (pull request 3505), so the diff against main is this part's alone. Part of #201.

**Round 3: handoff repair.** The opener's prepr refused c725250734 when it merged it with main, on three counts:
1. `ci predict`: unpinned sites were added in `learner_progress.py`.
2. `preflight`: a closing keyword beside #3435.
3. The open first-review block.

What this round changes:
- origin/main is merged as plain merge commits. e8e34b05fd was pushed to the step ref by another writer under the same seat identity, and this branch builds on it fast-forward.
- Merging main exposed a semantic conflict. On main, part 2's check X7 ("a settle ending before the running tail's end leaves it; one ending later moves it") failed against this part's scaled tail, so the pin run's `tests/features.py` baseline was red (`MUTATION TABLE INCONCLUSIVE`). X7 seeded `BoostState` at the default `space_boosted` of 0. Under the scaled tail its first settle then owes about 7.8 h, so the half-second-later end never reaches the held 12 h end. X7 now seeds the sum at a full window, so both settles owe the full tail and its two arms test what they did on main (c90588dcf4).
- Every added mutation site is pinned by a real kill or triaged as equivalent (`## Unpinned sites`).
- No closing keyword remains in this body or in any commit message on the branch.

**The first review's block is answered by c2a379d493, which descends from the blocked head 6caf7df2fa** (`git merge-base --is-ancestor 6caf7df2fa c725250734` exits 0). Block: class-open, a lower-floor probe problem the lower learner recorded paused the house, solar and gains learners on the card. Each learner now records its own freeze, and each card learner reads only the record of the learner it folds in. The class census is under `## Figures`, and the test that fails with the fix reverted is under `## Mutation proof`.

What ships, by brief item:
- Reasons at DEBUG. `close_span` logs one line for a span the counter closed or refused, through `log_close`, which returns before any formatting with DEBUG off. The house heat-loss learner's gates return through `learner_progress.log_skip`, which passes the reason's values to the logger as arguments (CHANGE b). Nothing is logged above DEBUG.
- (a) No helper and no reason string is added to `coordinator.py`. `log_skip`, `pauses` and `Freeze` live in `learner_progress.py`. `learning_freeze` and `freeze_end` live in `boost.py`. The coordinator passes what it already holds: `learner_freeze_reason`, and itself to `boost.learning_freeze`. `tests/structure.py` passes with no budget raised.
- (c) One source. Each learner records the freeze it obeyed in the coordinator's `FreezeRecord` (`learner_progress.py`), under its own name: `house`, `lower`, `dhw` or `buffer`.
  - A card learner's phase reads the record of the learner it folds in, `learner_progress.HELD_BY`: house, solar and gains read `house`, and lower reads `lower`.
  - The sensor's `learner_freeze_reason` is `FreezeRecord.last`, the reason recorded last this cycle; a learner that records again moves to the end.
  - Asking `_learning_frozen` again from the payload builder measured +2 on `seam_cut_total` in round 1, so it was not taken.
  - When two reasons hold at once, `_learning_frozen`'s own order picks the one a learner records. An unusable reading ranks above the boost, so the learner shows frozen with no end, and the card says "Paused until its inputs are usable again.", never "after a boost".
  - Pinned by "P3 one source: another reason has no boost end...", "P3 one record per learner: ..." and the card check "P3: a learner held for a reason with no line of its own says paused, never the raw key...".
- (d) Census, `learner_progress.pauses`, pinned per reason by "P3 census: ...":
  - Frozen, with an end: the boost (`boost_space`). The end is `BoostState.freeze_end`: the live overlay's end plus the full tail its window owes, else the running `space_settle_until`. The global boost mode has no end, because it ends when the user leaves it.
  - Frozen, no end: an open window (`ventilation`) and an unusable reading (`<problem>:<key>`).
  - Keeps its count:
    - the early cut-off;
    - unmetered power and an unread room;
    - `not_configured:` slots;
    - the plant states the pump signals.
  - Which learner a reason holds is `HELD_BY`'s decision, not `pauses`'s. A hot-water or buffer probe problem is recorded under `dhw` or `buffer`, which no card learner reads.
- (e) Each card learner reads the freeze of the learner whose gate holds it. The solar aperture and the internal gains fold inside the house learner's cycle, after its gate, so `HELD_BY` maps them to `house`. Pinned by "P3 census, driven: ...".
- (f) While an overlay is live, the end is a forecast. A cancel moves it earlier and a second press moves it later, both pinned with their values ("P3 end: ..."). An end past midnight shows the day (card check "P3: an end past midnight shows the day...").
- (g) No README.md or docs/ page lists the learner phases or the health row's texts, so no page gains a line.
- The scaled settling tail (owner ruling tvofi 2026-11-12, Carry 2). `boost.settle_tail` prices the tail on `BoostState.space_boosted` as `12 h + 6 h * ln(boosted / 2 h)`, with a floor of 1.5 h (`HOUSE_LOSS_MAX_SAMPLE_HOURS`, moved to `const.py`). The full tail applies from the window's length up, and to a sum with an unseen start.

Carries:
- Carry 0 (cc8a67d1) lands here.
- Carry 1 lands here.
- Carry 2 (owner ruling 2026-11-12) lands here.
- Carry 3 (e8e004db) lands here: the end is projected through `BoostState`.
- Carry 4 lands here: the same projection as Carry 3, restated in the live roster. The end is the live overlay's end plus the full `SPACE_SETTLE_TAIL`, then `BoostState.space_settle_until`, and no tail is recomputed (`BoostState.freeze_end`; "P3 end: ...").

## Head

fd92927f04e89fb0596f17849e6f2c028a8ee903, on merge base cfa868394685dbb2360844aec43d7a8cac4736ab (origin/main as merged by e8e34b05fd). Measured 2026-11-13 15:33 UTC. At that time origin/main is 154dbb4c61, and `git merge-tree --write-tree origin/main HEAD` reports no conflict, so main is not merged again; the train re-proves the head on the current main.

## Mutation proof

Failing test first, for the block: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/learner_freeze_mutants.py` at 9a2584e0e4 prints `MUTANTS: as expected`, rc 0. M10 puts the blocked defect back, with the lower learner recording in the house slot, and turns "P3 census, driven: a probe problem pauses on the card exactly the learners that freeze on that probe" red. M5 and M11 (`HELD_BY` miswired) do the same. M0, the null mutant (a comment line), leaves 0 red. M1-M9 are red as round 2 stated, each 1 to 3 checks: M1 3, M2 2, M3 1, M4 1, M5 1, M6 1, M7 1, M8 2, M9 1, M10 1, M11 1.

The reviewer's driver, `ev/lower_probe_repro.py` at ef272d6f68, reads flat at both ends. At 6caf7df2fa and at 35cfa50fb9 (this round's merged head before the pins) it prints `stale:lower_floor_temp_entity: phase counting -> frozen`. It hands a reason straight to `learner_progress`, and the fix routes reasons before that call (`HELD_BY`, `FreezeRecord`), which the driver bypasses. The companion that applies the tree's own routing to the same inputs is the driven census above, red at the blocked shape (M10) and green at the head.

The heat counter's two DEBUG guards, new this round. These are the survivors `--pin-killed` named, killed by the new check "P3: at DEBUG a span the heat counter refused logs its refusal once and one with no refusal logs nothing; with DEBUG off a closed span's line formats nothing". The instrument is `PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("OUT").read())' "# R10-OUTSIDE-LEARNER-ROBUSTNESS-P3: the frozen learner phase"` (prelude from `--emit-prelude OUT`), run on each mutant applied in place and then restored:
- unmutated: `ALL 12 FEATURES BLOCK PASSED`;
- `heat_energy.py` `close_span`'s refused-span guard to `if False:`: `1 of 12 FEATURES BLOCK FAILED`, the new check, lines `[]`;
- `log_close`'s level guard to `if False:`: `1 of 12 FEATURES BLOCK FAILED`, the new check, which formatted with DEBUG off.

The buffer learner's record, new this round, is the survivor `prepr.sh`'s diff-mutant step named: `coordinator.py` `self._learner_freezes.note_freeze("buffer", frozen)` deleted (CALL_DEL). It is killed by the census's new arm, "P3 census, driven: a stale buffer probe is recorded by the buffer learner under its own name and published as the freeze reason; with no problem no learner records anything". The P3 block is `ALL 13 FEATURES BLOCK PASSED` unmutated, and `1 of 13 FEATURES BLOCK FAILED` on that check with the line deleted (record `{}`).

Part 2's harness on the scaled tail's lines: `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/boost_tail_mutants.py` at 9a2584e0e4 prints `MUTANTS: as expected`, rc 0: M0 null 0 red; M1 full tail 6 red; M2 sum dropped 8; M3 persisted tail dropped 4; M4 restore dropped 1; M5 sum never clears 5.

## Null control

- `--pin-killed`'s own null mutant (`boost.py:49 NULL_COMMENT`) survived every driver in play, in each of the three runs.
- No boost and no tail: every learner's payload equals main's, with no `frozen_until` key ("P3 null control: with nothing holding the learners the payload is main's..."; M2 and M3 turn it red).
- An install with no heat counter closes no span and logs no span line. A meter with no refusal logs no refused line, which is an arm of the new check.
- DEBUG off: a value whose formatting raises passes `log_skip` and `log_close` untouched.
- X7 at the default seed of 0 fails at the head as it did in the pin run, and at a full-window seed passes both arms: `settle` driven with each seed (seed 0: `FAIL`, held end unmoved; seed 2 h: `PASS`, end moved by 0.5 s).

## Figures

<!-- figure-block: scope-line mb=cfa868394685dbb2360844aec43d7a8cac4736ab head=fd92927f04e89fb0596f17849e6f2c028a8ee903 -->
~~~text
MODE: SCOPED -- 29 script(s) run, 4 scoped out.
~~~
<!-- /figure-block -->

### Class census

The class: a freeze that one learner records reaches a card learner that does not obey it. The rule that enumerates its seams is the check "P3 census, driven: ..." in `tests/features.py`, run with the features-block command under `## Mutation proof`. It crosses two sets read from the tree:
- the keys of `const.INPUT_MAX_AGE_MINUTES`, every probe the input watchdog ages;
- `learner_progress_view`'s keys, every card learner, which the check refuses unless they equal `HELD_BY`'s keys.

For each probe, alone and `stale`, it runs the lower, house and buffer learners in `_async_learn_interval`'s order on a two-zone install, then reads each card learner's phase through `_learning_view`. It compares each pair with this design table, which the check states itself:

| card learner | paused by a problem on | every other probe |
|---|---|---|
| house | indoor, outdoor, thermal power | keeps its count |
| solar (folds behind the house gate) | indoor, outdoor, thermal power | keeps its count |
| gains (folds behind the house gate) | indoor, outdoor, thermal power | keeps its count |
| lower | indoor, outdoor, thermal power, lower floor | keeps its count |

At the head every pair matches. With M10 (the blocked shape) the lower-floor pairs for house, solar and gains are paused, the reviewer's three. With no probe problem no learner is paused: the census's own null control, asserted in the same check.

Recorders outside the driven pairs:
- The hot-water and buffer records are seeded by "P3 one record per learner". No card learner pauses on them, while `FreezeRecord.last` still publishes them.
- The COP learner records nothing.
- Reasons that are not probes reach a learner only through that learner's own `_learning_frozen` call.

Seams with no disposition: none.

### Mutation table

- `python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 3`:
  - at c90588dcf4: `PIN KILLED: 33 pinned, 4 left unpinned (4 survived, 0 not started for the budget, 0 exclusive tails cut, 0 timed out, 0 skipped)`;
  - at 7a2d5d5c86, after the two kills: `PIN KILLED: 2 pinned, 0 left unpinned`.
  - The first run at 35cfa50fb9 was `MUTATION TABLE INCONCLUSIVE`, with the X7 red in the `tests/features.py` baseline. It was stopped by PID and its result discarded.
- `python3 tools/pr/ci_predict.py --base $(git merge-base origin/main HEAD) --only mutation`:
  - unrepaired, at the merge 35cfa50fb9: 37 `ADDED UNPINNED` lines, including every `learner_progress.py` line the opener named, plus one `STALE PIN` for `BoostState.settle GUARD_OFF b0e03faa`;
  - at fd92927f04e89fb0596f17849e6f2c028a8ee903: `no closures, fast, governance or instrument red predicted against cfa868394685` and no `ADDED UNPINNED` line.
  - The stale pin's guard line moved to `BoostState._boosted_with`; the pin file is deleted (35cfa50fb9) and the line is pinned afresh.

### Gate and ratchets

- Scoped gate: `env -u BASH_ENV PYTHONPATH=tests/hastub GOLDEN_MODE=drift GOLDEN_REF=cfa868394685dbb2360844aec43d7a8cac4736ab GATE_SCOPE=auto tests/run.sh` at 9a2584e0e4: `MODE: SCOPED -- 29 script(s) run, 4 scoped out.`, `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`, rc 0; among them `ALL 5480 FEATURE CHECKS PASSED`, `ALL 2711 ENTITY CHECKS PASSED`, `ALL CARD CHECKS PASSED`, `ALL 46 BOOST DRIFT CHECKS PASSED`, `ALL 116 STRESS CHECKS PASSED`.
- fd92927f04 adds one census arm to `tests/features.py` and nothing else (`git diff --stat 9a2584e0e4 fd92927f04` names that file alone). `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/features.py` at fd92927f04: `ALL 5481 FEATURE CHECKS PASSED`, rc 0.
- `python3 tests/structure.py` at fd92927f04e89fb0596f17849e6f2c028a8ee903: `STRUCTURE RATCHET PASSED`.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` at 35cfa50fb9: `ALL 2711 ENTITY CHECKS PASSED`. The gate above runs it at the head.
- `python3 tools/audit/archscore/score.py --diff cfa868394685dbb2360844aec43d7a8cac4736ab` at fd92927f04e89fb0596f17849e6f2c028a8ee903: `Architecture score: dS +0.0029 IMPROVES` (`coord_footprint 2505 -> 2500`).
- No golden moves. Neither claim file, `VERSION`, the manifest nor `RELEASE_NOTES.md` is touched: `git diff --stat cfa868394685dbb2360844aec43d7a8cac4736ab...HEAD -- tests/golden VERSION RELEASE_NOTES.md custom_components/heatpump_optimizer/manifest.json` prints nothing.

### The scaled tail against part 2's full tail

Measured at 3d7e57dd48 and not re-measured. Since then, `git diff --stat 3d7e57dd48 HEAD` on `boost.py`, `heat_energy.py` and `boost_press_tail_walk.py` prints nothing. On `tests/boost_drift_replay.py` it prints the two-line record rename alone. But main's merges change the coordinator, which the replay drives. The gate's `tests/boost_drift_replay.py` passes at the head.

Real prices: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/boost_press_tail_walk.py production slope6h full`: `PRODUCTION: EQUAL to slope6h on 10 of 10 arms`, exit 0. `null_no_boost`: +0.0045 / +0.0236. `worst` / `final` excursion of the house heat-loss scale:

| arm | production (scaled) | its freeze twin | full (part 2) | its freeze twin |
|---|---|---|---|---|
| 10x1 | +0.0028 / +0.0227 | -0.0032 / +0.0222 | -0.0045 / +0.0226 | +0.0052 / +0.0252 |
| 30x1 | -0.0129 / +0.0204 | -0.0207 / +0.0176 | -0.0045 / +0.0229 | +0.0052 / +0.0252 |
| 60x1 | -0.0045 / +0.0205 | -0.0045 / +0.0236 | -0.0045 / +0.0205 | -0.0045 / +0.0236 |
| 120x1 | -0.0045 / +0.0216 | -0.0045 / +0.0221 | -0.0045 / +0.0216 | -0.0045 / +0.0221 |
| 10x4 | -0.0045 / +0.0214 | -0.0045 / +0.0221 | -0.0045 / +0.0214 | -0.0045 / +0.0221 |

Flat-price null control: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/boost_press_tail_walk.py --flat production full none`:
- `PRODUCTION: DIFFERS to full on 6 of 10 arms`;
- `NULL CONTROL: none differs from full on 5 press arm(s): SEES`;
- exit 1, by design when `slope6h` is not in the run;
- `null_no_boost`: -0.0056 / +0.0048.

| arm | production (scaled) | its freeze twin | full | none (no tail) |
|---|---|---|---|---|
| press 10x1 | -0.0049 / +0.0000 | -0.0118 / +0.0022 | -0.0150 / +0.0056 | -0.0049 / +0.0035 |
| press 30x1 | -0.0200 / +0.0029 | -0.0286 / -0.0039 | -0.0150 / +0.0057 | -0.0062 / +0.0025 |
| press 60x1 | -0.0150 / +0.0018 | -0.0150 / -0.0008 | -0.0150 / +0.0018 | +0.0052 / +0.0056 |
| press 120x1 | -0.0150 / -0.0029 | -0.0150 / +0.0040 | -0.0150 / -0.0029 | +0.0390 / +0.0094 |
| press 10x4 | -0.0150 / +0.0049 | -0.0150 / +0.0040 | -0.0150 / +0.0049 | -0.0049 / +0.0060 |

The scaled tail changes only the 10 and 30 min single presses. On 30x1 it walks further than the full tail at both prices, but the heat-free freeze twin walks further still (-0.0207 and -0.0286). So the excess comes from which samples the shorter freeze skips, not from boost heat. The no-tail arm press 120x1 walks +0.0390 at flat prices, against -0.0150 with any tail.

## Unpinned sites

none: `no closures, fast, governance or instrument red predicted against cfa868394685` and no `ADDED UNPINNED` line at fd92927f04e89fb0596f17849e6f2c028a8ee903. Each site the diff adds is pinned in `tests/mutation_ledger/killed_by/`, by `--pin-killed` at c90588dcf4 and 7a2d5d5c86. The exceptions are two survivors recorded `equivalent` in `tests/mutation_ledger/survivor_triage/boost.py/`:
- `settle_tail.CMP_BOUND.83178048`: `>=` to `>` differs only at a sum of exactly 2 h, where `log(1.0) == 0.0` gives the full tail either way. Measured: the formula arm at 2 h `==` the 12 h tail.
- `BoostState.freeze_end.CMP_BOUND.f5217c8f`: `> 0` to `>= 0` differs only when held and projected are the same instant, and the two arms return them.

Diff survivors `tools/pr/prepr.sh` named, with `MUTANT_CMD` running part 2's block (`"# #1935 follow-up (R10-OUTSIDE-LEARNER-ROBUSTNESS-P2)"` to `"# A hot-water charge inside a counter span (the dwell saw it)"`) and then part 3's, each with its emitted prelude:
- custom_components/heatpump_optimizer/boost.py:97: survivor (CMP_BOUND `>`), equivalent: triaged as `settle_tail.CMP_BOUND.83178048` above
- custom_components/heatpump_optimizer/boost.py:190: survivor (CMP_BOUND `>=`), equivalent: triaged as `BoostState.freeze_end.CMP_BOUND.f5217c8f` above
- custom_components/heatpump_optimizer/boost.py:190: survivor (CONST_SWAP `> 1`), equivalent at the cycle's resolution: ends at most 1 s apart give the same minute on the card's clock, and the learner runs once a cycle
- custom_components/heatpump_optimizer/boost.py:175: survivor (CONST_SWAP `max(1.0, ...)`), equivalent within a second: it differs only for a boost that ran under 1 s, which then adds 1 s to the sum. Alone, that sum owes the 1.5 h floor either way. Added to other boosts, it moves the tail by at most tau/sum per second (35 s at the floor's edge), below the cycle's resolution
- custom_components/heatpump_optimizer/coordinator.py:5778: survivor of the two blocks (RETURN_DEL), killed by tests/features.py: pinned by `--pin-killed` as `HeatPumpOptimizerCoordinator._async_learn_house_heat_loss.RETURN_DEL`
- custom_components/heatpump_optimizer/coordinator.py:5645: survivor (CALL_DEL), killed in fd92927f04 by the census's buffer arm (`## Mutation proof`)

## Red checks

none: no CI run exists at this head. `ci_predict.py` at fd92927f04e89fb0596f17849e6f2c028a8ee903 predicts no red. The `mutation` red round 2 forecast is repaired here by pins and two kills, before any CI run.

## Forward-carry

none

## Friction

fixer.md: cost: the merge with main turned part 2's X7 check red against this part's scaled tail, a semantic conflict no textual merge reports. It showed first as the pin run's `MUTATION TABLE INCONCLUSIVE`, about 25 min in, and a full `tests/features.py` at the merged head would have shown it in about 7 min. Carry: dismissed: the fixer's step 5 gate after any merge already runs features.py; the order of the pin run and the gate is the seat's choice, not a missing rule
