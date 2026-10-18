R10-ARCHSCORE-COVERAGE, part 5 of 5: the shape census, calibrated and kept gate-only (roster item 6; ARCH-s2, ARCH2-s3).

Part of #2259.
Part of #2235.

This is the group's last part, and it closes neither issue. #2259 is not complete: item 2's card "duplicated spellings" is only partly delivered (row below; the #2401 round-1 review). #2235's five findings are all delivered, but its body records a round-10 RCA as owed, and no part of this group delivers it. Both issues stay open, and the orchestrator closes each by hand when its last row lands.

| issue | item / finding | delivered by | state |
|---|---|---|---|
| #2259 | 1, layering and import closure (ARCH2-s4) | part 3, #2320 | merged `6627485ee` |
| #2259 | 2, card coverage (ARCH2-s5): dead definitions and the card's clone census | part 4, #2373 | open; stacked here |
| #2259 | 2, card coverage: duplicated spellings of a one-statement rule | none. The 20-token census joins a copy only where a window matches, so a one-statement spelling sits below it. The review's probe spelled three of ARCH2-s5's `card_shapes.mjs` rules once more inline: the finder's total reads 22 -> 25, with `card_clone_copies` 108 -> 108 and `card_dead_definitions` 0 -> 0 | not delivered |
| #2259 | 3, dict-literal clones (ARCH2-s5) | part 4, #2373 | open; stacked here |
| #2259 | 4, hub alias through readers and rebinds (ARCH2-s1, D7-s1-83) | part 2, #2311 | merged `8f174c4ce` |
| #2259 | 5, ARCH-s3's three holes | part 1, #2293 | merged `acfeaf8b4` |
| #2259 | 6, shape census (ARCH-s2, ARCH2-s3) | part 5, this PR | this PR |
| #2259 | 7, event-callback hub writes | part 2, #2311 | merged `8f174c4ce` |
| #2235 | D7-s1-01 | R10-STRUCTURE-BLIND, #2340 | merged `818640351` |
| #2235 | D7-s3-01 | R10-STRUCTURE-BLIND, #2340 | merged `818640351` |
| #2235 | D7-s3-02 | part 4, #2373 (the card's dead-definition census) | open; stacked here |
| #2235 | D7-s3-51 | part 1, #2293 | merged `acfeaf8b4` |
| #2235 | D7-s3-52 | part 1, #2293 | merged `acfeaf8b4` |
| #2235 | RCA owed (the issue's `RCA:` line: per_round, cross_round and barriered_any met) | none: not in this group's scope, and no roster group carries it | owed |

The rows marked "stacked here" merge with this branch: it contains part 4's head. #2259's items come from its own body, and #2235's findings come from its `## Findings` table, both read at handoff. The PRs' states come from `gh pr view`. The RCA search covered `dev/audit/rca/` on origin/main and the roster: the only round-10 groups naming #2235 are this one and R10-STRUCTURE-BLIND (`fixes` [2235], stage `done`). #2228 was closed by part 1 (closed 2026-10-16).

Carry: two items go to the orchestrator to route.
- #2235's round-10 RCA for N-structure-blind: it is not foldable into an instrument PR.
- #2259 item 2's card duplicated spellings: a card counterpart of C23, a shape census over one-statement JavaScript rules with its calibration cases. Its acceptance is ARCH2-s5's `card_shapes.mjs` perturbation, where any one shape spelled once more moves the census by 1. It is a new metric with its own calibration, so it is not folded into this round.

**Stacked on part 4:** this branch merges part 4's head `69c36cee5` (#2373, round 2), so until that merges, its diff against main includes part 4's. The part-5 delta alone is `git diff 69c36cee5...HEAD`. The diff is `tools/audit/archscore/` plus its registrations (`tests/closures.json`, `tests/ci_budgets.json`); `tests/structure.py` is not touched.

What changes. A census of N implementations of one rule, `shape_copies` (`metrics/shapes.py`, counter C23):
- It counts the members of every class of two or more functions that share one SHAPE.
- A shape is the function body with its own names numbered, and numbers, strings and `mod.X` abstracted: the clone window's normalisation, applied to the whole function. A nested function stands as its own shape, so one decorator's wrapper is not every wrapper.
- `duplication_copies` needs a window of two statements and at least 30 nodes. This census reads what falls under that window: a rule that is one statement, or a short function.

Item 6 says to calibrate first and to weight the counter only if calibration shows it is not gameable. **Calibrated, it is gate-only (weight 0), and `weights.json` is unchanged:**
- **Weighted at the floor, it credits a defect.** The one corpus commit it lowers is BAD (`ca711b56`, 69 -> 68), which would read IMPROVES.
- **It is gameable.** One statement re-spelled leaves a class while the rule is still written again: `a3_shape_copies_respelled_control` (BAD) reads NULL. A weight would pay for that move.
- **As a tripwire it moves no recorded verdict.** It rises on five BAD, two NEUTRAL and two GOOD corpus commits (`0323c5b8`, `56cb0027`), each one already inadmissible.
- **It refuses what nothing else does: a new copy below the window.** `a3_shape_copies_control` reads WORSENS through `shape_copies` alone, and NULL with C23 off.

Calibration cases:
- `a3_shape_copies_control` (BAD): a third copy of `comfort_band.effective`'s one-statement rule in `presets.py`, every name changed.
- `a3_shape_copies_fix` (GOOD): `config_flow` imports `comfort_band.effective` instead of its own copy. It reads NULL, because weight 0 pays no dedupe; that miss is recorded.
- `a3_shape_copies_null`: `effective`'s parameters renamed.
- `a3_shape_copies_respelled_control` (BAD): the gameability miss, recorded.
- `rt_45_shape_private_copy`: a private helper copied into its importer under new names, which lowers `private_cross_module`. It is refused, but by `duplication_copies` as well. Every private crossing on the pin is two to four statements, at the window, so C23 is not what closes it; `ABOUT.md` says so.

Alternatives considered:
- Strings kept, not abstracted. That joins 0 of ARCH-s2's 35 payload-guard implementations (the companion, `## Figures`); with strings abstracted it joins 26.
- A weight at the floor. Refused on the evidence above.
- Leaving the census out of the vector as a report-only instrument. Refused: it could then carry no calibration case, and its tripwire is free on the corpus.

## Fold (finding sweep, carry-forward)

Four out-of-scope rows were routed to this group (`fold-R10-ARCHSCORE-COVERAGE.txt`, rows P07, P18, P54 and P56). Three are folded here, in `97ed42ad8`, `8befb858` and `473d1cf36`. The fourth was already delivered by part 4.
- **P18** (#2311 review, F1 and F2).
  - F1, under-fire, is closed by counter C16b (`hub_solve_writes._passes_on`). Before, a coordinator method handed to a package function was never a hub root, so `async_track_state_change_event(self.hass, [entity], _pkg_wrap(self._on_power_event))` with `def _pkg_wrap(cb): return cb` read 41 -> 40.
  - The rule, as repaired in round 2 (`473d1cf36`): when the package function passes the reference on uncalled, the reference is a root.
    - Handing it to a call outside the package, through any depth of package calls, always counts (`_passes_on` answers `out`).
    - Returning it, or a nested function or lambda over it, counts only when the caller hands the returned value on: it is an argument of a call outside the package, or of a package function that passes it on in turn (`returned`, then `_consumed`).
    - A call of the reference (`cb(x)`) is not a pass.
    - A returned reference whose result is discarded, as in `tests/arch_score.py`'s null control, is not a root, and neither is one bound to a local and handed on later.
  - Attempt `rt_20b_hub_event_pkg_wrap` reads NULL.
  - This seat's plant script (`p18_plants.py`, written against this tree) prints `P18_F1 hub_solve_writes=41->41 (C16b off: 40)`.
  - F2, over-fire, is recorded as a precision note in `ABOUT.md` and the module docstring rather than closed: `_LOGGER.debug("%r", self.async_update_thermal_params)` reads `41->48`. A reference handed to any call outside the package is a root, because the census cannot tell a subscription from a log argument.
  - Today's tree still reads 41, so the `archscore.hub_solve_writes` row does not move. `calibrate.py --measure-corpus --only-metric hub_solve_writes` printed `ok` for all 87 trees and left `corpus_vectors.json` byte-identical, so no corpus value moved.
- **P56** (#2373 friction). `calibrate.py --record --only ID,..` now merges the subset's rows into `expected.json` (`merged_record`). It keeps every other row and `_sensitivity`, which a subset cannot re-derive, and it prints `RECORD SUBSET`.
  - `tests/arch_score_head.py` gains two checks pinning it: `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`. Mutant M21 (the merge returns the subset) fails both: `2 of 18 ARCHITECTURE SCORE HEAD CHECKS FAILED`.
  - `rt_20b` was recorded this way, as a subset of one. CI's `arch-score` lane re-derives the full record and its `_sensitivity`.
- **P07** (#2282 friction). Every live `calibrate.py` run now prints `planted and red-team cases are built on the calibration pin 7952d8f9e (cases.PINNED), not on this tree; each is scored against the pin's vector unless its case names another base`.
- **P54** (#2373 round-1 minor) was already delivered by part 4: `tests/doc_claims.py` lost the per-call `sys.path.insert` in `033998cb5`, and its import sits beside `_tokens` since `d41773bbf`. Carry: none; P54 is in #2373.

Mutants of the fold, on a detached worktree of `97ed42ad8` with `calibrate.py --only` the four hub cases (`mutate_p5r2.sh`). M0 reads every case as recorded.
- **M17**, `_passes_on` never true: `rt_20b_hub_event_pkg_wrap` NULL -> IMPROVES. No other case moves.
- **M18**, a returned carrier not read: `rt_20b` NULL -> IMPROVES.
- **M19**, a call of the carrier counted as a pass: no case moves, and today stays 41. It is an over-fire guard (`## Unpinned sites`).
- **M21**, as above.
- Round 2, run against `tests/arch_score.py`'s hub checks only (`hub_spellings`, `mutate_r3.sh`). M0 passes both the null control and the new positive fixture.
  - **M22**, a returned reference rooted whatever the caller does (round 1's rule): the null control fails with `got 1 (C15/C16 off: 0)`, CI's red.
  - **M23**, `_consumed` never true: the positive fixture fails with `got 0`.
- At this head, `calibrate.py --only` on `rt_20b`, `rt_20` and `a3_hub_event_write_control`/`_fix` reads each as recorded: NULL, NULL, WORSENS and IMPROVES.

## Head

`613a59cf3564753728c3766cd5efdd1716dadb9a`. It merges part 4's round-2 head `69c36cee56f102716bb1ba73412d7838d232610c`, and `git merge-base origin/main HEAD` is `413944b6772fa7f2f38cef7ea2f667a64d79251a`.

Round 2 (#2401 review, blocked at `c75609c3a`) adds three commits to that PR head, then merges origin/main (`613a59cf3`):
- `473d1cf36`: C16b's returned arm, plus a positive fixture in `tests/arch_score.py`.
- `dfaaf9e18`: the companion harness lands, and `ABOUT.md` states the general limit.
- The body: `Part of #2259`.

origin/main's merge brings `coordinator.py`, `pump_arbiter.py`, `plan_step.py` and `thermal_model.py` changes. At this head, today's tree reads `shape_copies` 66, `literal_clone_copies` 186, `card_clone_copies` 108, `card_dead_definitions` 0 and `hub_solve_writes` 41, each equal to its row.

The calibration record, corpus, companion and mutant figures were taken at `8fef64874`. Four merges since then bring in part 4. The latest is its round-2 repair (`45da9204f`, `c5dbc83da`), which adds attempts 42d and 44c, folds module-binding constants (C21) and drops empty card statements (C22), and moves the `literal_clone_copies` row to 186. That merge conflicted in `ABOUT.md`, `counters.py`, `expected.json` and `ci_budgets.json`, adjacent edits, and was resolved by keeping both sides: the C21/C22 rows then C23, `rt_44c` before `rt_45`, part 5's budget `reason` naming part 4's rows. The earlier three: its grammar commit (`94522163e`), its round-1 repair (`033998cb5`, `c8d1382a3`), and its PR head `2183ab58f` (origin/main `d569693ad`) with the briefs fix `d41773bbf`. The briefs fix moves `tests/doc_claims.py`'s `_IDENT` import to directly above `_tokens`, so carry-1645's line citations stop shifting. Here `brief_lint.mjs` prints `TOTAL: 0 error(s) across 47 file(s)`. Between `52f698905` and `d569693ad`, origin/main touches nothing in `custom_components/` or `tools/audit/archscore/`. The repair changes `metrics/literal_clones.py` and `metrics/card.py` (C20 to C22) and adds attempts 42b, 42c and 44b. It changes no part-5 file. `metrics/shapes.py` imports neither changed module.

The merge of `c8d1382a3` (`8b00a55fb`) conflicted in `ABOUT.md`, `counters.py` and `expected.json`, all of them adjacent appends. It was resolved by keeping both sides: part 4's C20 to C22 rows, then part 5's C23 row, and `rt_44b_card_noop_split` before `rt_45_shape_private_copy`. At `8b00a55fb`, whose instrument this head keeps, `calibrate.py --only` the five part-5 cases plus part 4's three round-1 attempts reads each as recorded: `a3_shape_copies_control` WORSENS (`shape_copies 87->88`), `_fix` NULL, `_null` NULL, `_respelled_control` NULL, `rt_45` WORSENS and inadmissible, and 42b, 42c and 44b NULL (`RED TEAM 4/4 attempts read NULL or inadmissible; IMPROVES: none`). The merge of `d41773bbf` was clean. The scoped gate and today's values are re-taken at this head.

## Mutation proof

Each mutant was applied in place on a detached copy of the head, run with `calibrate.py --only` the five part-5 cases, and restored with `git checkout --` (`mutate_p5.sh` in the seat's scratch). The unmutated run, M0, reads the recorded verdicts. Ablation `ARCHSCORE_ABLATE=C23` moves `a3_shape_copies_control` WORSENS -> NULL.

- **M1**, no class is ever formed (`len(v) > 999`). `a3_shape_copies_control` moves WORSENS -> NULL, and today's tree reads `shape_copies` 0.
- **M2**, a nested function erased to `pass`. No case moves. Today's tree reads 72, and the `archscore.shape_copies` row of 66 refuses it.
- **M3**, strings kept. No case moves. Today's tree reads 10, a fall a ratchet does not refuse. The companion pins it instead: ARCH-s2's 35 payload-guard implementations go from 26 joined to 0.
- **M4**, the parameter names in the signature not numbered. No verdict moves. Today's tree reads 68, and the row refuses it.

## Null control

- **The base instrument has no census.** The companion reads `joined=0` there, and 26 at the head.
- **Honest code does not trip it.** `a3_shape_copies_null` (parameters renamed) reads NULL. The corpus re-measure moves no recorded corpus verdict. `calibrate.py --record` printed RECORD for the five new cases alone.

## Figures

- **The companion**, now in the tree as `dev/audit/harnesses/archscore_shape_family_coverage.py` (round 2; it was the scratch script `shape_family_coverage.py`, sha1 `a6e533f0`, plus a header). Run as `python3 dev/audit/harnesses/archscore_shape_family_coverage.py <worktree> 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef`. Re-run at `dfaaf9e18`, with origin/main's `tools/audit` as the base instrument. It applies ARCH-s2's seam rule, `shape_payload_guard.py`'s `family()` copied verbatim, at that seat's baseline. At the base worktree: `implementations=35`, `joined=0`, `classes_spanned=0`. At the head: `implementations=35`, `joined=26`, `classes_spanned=3`. ARCH-s2's own harnesses measure semantic agreement on production inputs, which an instrument change leaves alone, so they read flat at both ends by construction.
- **Corpus.** `python3 tools/audit/archscore/calibrate.py --measure-corpus --only-metric shape_copies --jobs 4`: 87 trees, 0 not `ok`. The shape_copies counterfactual over the stored vectors, run with `score.delta`, classifies 26 of the 45 corpus commits correctly in each of three arms: without the census, gate-only, and weighted at 1.0. Only `ca711b56` changes between the arms: BAD reads NULL, then NULL, then IMPROVES.
- **Calibration.** `python3 tools/audit/archscore/calibrate.py --record --jobs 4` at `8fef64874`. It printed RECORD for exactly the five part-5 cases: `git diff 69c36cee5...HEAD -- tools/audit/archscore/calibration/expected.json` is 30 insertions, 0 deletions. It also printed `CALIBRATION 107/137 labelled cases classify as their label says`, `RED TEAM 78/78 attempts read NULL or inadmissible; IMPROVES: none` and `KNOWN-OPEN 1` (`rt_04zz1`, unchanged), with no `SENSITIVE` line.
- **Today's tree**, at this head. `shapes.measure(.)` reads `shape_copies` 66 in 18 classes, which is the new row. Part 4's metrics read `literal_clone_copies` 186 and `card_clone_copies` 108, which are its rows.
- **Scoped gate**, at this head. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at this head prints `MODE: SCOPED -- 4 script(s) run, 29 scoped out`. It names four scripts:
  - `tests/arch_score.py`: it re-derives the record above and runs on CI (heavy-script rule).
  - `tests/arch_score_head.py`: `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 169 checks PASSED`.
  - `tests/entities.py`: not run locally at this head, under tvofi's heavy-to-CI ruling of 2026-10-18 (box load about 200). CI's `fast` lane runs it; its check-run is cited on the PR.
- **`run.sh`'s `run_always` scripts, at this head.** `tests/env_drift.py --claims-only 413944b6772fa7f2f38cef7ea2f667a64d79251a` prints `claims hygiene: 413944b6772fa7f2f38cef7ea2f667a64d79251a ok`. `tests/closure.py selftest` prints `ALL 115 closure shrink pins PASSED`. `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`. `tests/layout.py` prints `layout self-test: ok`. `python3 tools/audit/seat/tmp_paths.py --check` prints `0 refused`.
- **Agreement lane.** `node tools/policy/agreement.mjs --only discovery`, run with `tools/policy/agreement.mjs` equal to origin/main, prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`. `git grep -nF '[A-Za-z_$][\w$]*' -- tools tests` prints `metrics/card.py:53` and `tools/audit/seat/r10_deeplink_mutants.py:217`. The second is a JavaScript regex inside a string in another group's script, which arrived with origin/main.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (not touched).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: `Architecture score: dS +0.0000 NULL` (no package file changes).

## Raise justification

`tests/ci_budgets.json` gains one new row, `archscore.shape_copies` 66, at the value the census derives at this head. It is a new ratchet, not a raise, and no existing row moves. The row is needed because the gate-only key is in the score vector, and `ci_ratchet` refuses a derived key with no row as growth.

Payments considered:
1. Leave the key out of the vector. Then there is no calibration case and no tripwire.
2. Weight it. Refused by calibration.

A change to a `*_budgets.json` merges only on the owner's approving review at its head (budget-raise-gate, 0013). The orchestrator handles it under mandate 6175172275.

`Architecture score: dS +0.0000 NULL`: no package file changes.

## Unpinned sites

n/a for production code: the diff touches the instrument only. The predicates are pinned by the mutants above: M1 by a planted case, M2 and M4 by the row value, M3 by the companion.

The fold has one guard its mutant does not pin. **M19, a call is not a pass** (`_passes_on.reads` skips a carrier read only as a call's function). Without it, `def run(cb): return cb(x)` would read as passing `cb` on, so it would root a callback that a package function calls synchronously. That callback is already reached from wherever the function is, so it would only double-root it. No package function on today's tree or the pin returns the result of calling its callback argument with a coordinator method behind it, and today stays 41 under the mutant. It is stated in the docstring.

## Architecture score

n/a: no package file changes.

## Red checks

- **`fast (3.14)`** (job `117678743499`, failure at `c75609c3a`): `tests/arch_score.py` printed `1 of 254 ARCHITECTURE SCORE CHECKS FAILED`, namely `FAIL hub census: null: a callback handed to a package function reads 0 site(s) ... [got 1 (C15/C16 off: 0), base 0]`.
  - Cause: this PR's C16b rooted a callback that a package function only returns (`def _register(cb): return cb`), whatever the caller did with the result. The fixture discards the result.
  - Fixed in `473d1cf36`: a returned reference is a root only where its result is handed on (`## Fold`). The null control now reads 0, a new positive fixture (returned into a subscription) reads 1, and M22 and M23 pin each arm.
  - Locally I ran only `hub_spellings`, under tvofi's heavy-to-CI ruling: `ok` on both. The full `tests/arch_score.py` is CI's.
  - The cheaper detector exists and was not run: `tests/arch_score.py`'s `hub_spellings`, which runs alone without the calibration. The fold's mutants ran `calibrate.py --only`, not the script that owns the null control. The answer is to run `hub_spellings` with every C16 change.
- **`pr-contract`** (the runs at `c75609c3a`): it refused the round-1 body's closing keyword for the group issue, which is not in the intended list. Fixed: the body says `Part of #2259`, and #2259 is not complete (item 2).

- **`briefs`** (check-run `117611794944`, failure at `2183ab58f`, part 4's PR head and an ancestor of this branch through the part-4 merges).
  - Cause: part 4's `_IDENT` import at the top of `tests/doc_claims.py` moved every line below it down one. `dev/programme/carries/carry-1645.json`'s citations of `check_initial_setup_menu` and `check_simulate_plan_fields` then fell out of `brief_lint`'s window.
  - Fixed in part 4's `d41773bbf`, which moves the import directly above `_tokens`. Here `node tools/policy/brief_lint.mjs` prints `TOTAL: 0 error(s) across 47 file(s)`.
  - The cheaper detector exists: `brief_lint.mjs` itself, run before the handoff. `prepr.sh` step 3f runs it only when the diff touches a pinned path, and otherwise skips with `no pinned path changed, so CI's briefs job reads this head's copy`. Running it unconditionally would cost one more local lint per handoff and nothing standing. Part 4's `## Friction` records it, and this seat now runs it before every handoff.
- At `c75609c3a`, 45 check-runs: 28 success, 14 skipped and 3 failure, the `fast (3.14)` and two `pr-contract` runs above. `arch-score` (the full record) was green. CI has not run on this head.

## Forward-carry

- **The #2373 general limit** (that PR's round-3 review: plants P6, a class-attribute constant, and P7, a constant expression, each read `literal_clone_copies` 186 -> 182) is stated in this branch's `ABOUT.md`, part 4's section. C20 and C21 fold spellings of a value, not the value, so the literal census is a floor on the copies. The R10-BRIEFS-FOLD carry ("Unless #2373 closes them") should cite that paragraph. The roster carry is the orchestrator's to write.

- **R10-BRIEFS-FOLD (`dev/governance/dimensions/D7.md`).** The folded brief can cite `shape_copies` as a finder's census of rule families below the clone window. It should cite it with its stated limits: spelling-blind, weight 0, and C23 load-bearing only for copies below the window (`ABOUT.md`, part 5). The roster carry is the orchestrator's to write.

## Friction

- R10-ARCHSCORE-COVERAGE-p5: cost: the first plants were at the clone window, so `duplication_copies` refused them and C23 carried nothing. The ablation arm caught it. Planting below the window was the fix, which is a reason to run the ablation before writing the case set rather than after.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
