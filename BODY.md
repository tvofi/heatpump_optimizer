R10-ARCHSCORE-COVERAGE, part 5 of 5: the shape census, calibrated and kept gate-only (roster item 6; ARCH-s2, ARCH2-s3).

Closes #2235.
Part of #2259.

This is the group's last part. Parts 1 to 4 landed items 5, 4 and 7, 1, and 2 and 3. Of #2235's findings, this group delivered four:
- D7-s3-51 and D7-s3-52 in part 1 (#2293);
- D7-s1-83 in part 2 (#2311);
- D7-s3-02 in part 4 (the card's dead-definition census).

R10-STRUCTURE-BLIND (#2340) delivered D7-s1-01 and D7-s3-01. #2228, this group's one `fixes` issue, was closed by part 1. **Stacked on part 4:** this branch merges part 4's head `94522163e`, so until that merges, its diff against main includes part 4's. The part-5 delta alone is `git diff 94522163e...HEAD`. The diff is `tools/audit/archscore/` plus its registrations (`tests/closures.json`, `tests/ci_budgets.json`); `tests/structure.py` is not touched.

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

## Head

`ee1cd839d305ddc18cea868598ccffaee2b6644c`. It merges part 4's head `94522163e091b1f14ccb8ba5c4d0bad1cfce6ae7`, and `git merge-base origin/main HEAD` is `6e5753a4aca8b240559e8e11e8a68c7de988cd73`.

The calibration, corpus, companion and mutant figures were taken at `8fef64874`. The one merge since then brings in only part 4's grammar commit. That commit touches `tests/doc_claims.py`, `tests/closures.json` and attempt 44, and no part-5 file. The scoped-gate lines are re-taken at this head.

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

- **The companion.** `python3 shape_family_coverage.py <wt> 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef` (sha1 `a6e533f006c76b6dfda041bdab169f2694a34268`, in the seat's scratch). It applies ARCH-s2's seam rule, `shape_payload_guard.py`'s `family()` copied verbatim, at that seat's baseline. At the base worktree: `implementations=35`, `joined=0`, `classes_spanned=0`. At the head: `implementations=35`, `joined=26`, `classes_spanned=3`. ARCH-s2's own harnesses measure semantic agreement on production inputs, which an instrument change leaves alone, so they read flat at both ends by construction.
- **Corpus.** `python3 tools/audit/archscore/calibrate.py --measure-corpus --only-metric shape_copies --jobs 4`: 87 trees, 0 not `ok`. The shape_copies counterfactual over the stored vectors, run with `score.delta`, classifies 26 of the 45 corpus commits correctly in each of three arms: without the census, gate-only, and weighted at 1.0. Only `ca711b56` changes between the arms: BAD reads NULL, then NULL, then IMPROVES.
- **Calibration.** `python3 tools/audit/archscore/calibrate.py --record --jobs 4` at this head. It printed RECORD for exactly the five part-5 cases: `git diff 94522163e...HEAD -- tools/audit/archscore/calibration/expected.json` is 30 insertions, 0 deletions. It also printed `CALIBRATION 107/137 labelled cases classify as their label says`, `RED TEAM 78/78 attempts read NULL or inadmissible; IMPROVES: none` and `KNOWN-OPEN 1` (`rt_04zz1`, unchanged), with no `SENSITIVE` line.
- **Today's tree.** `vector.measure(., {'shape_copies'})` reads `shape_copies` 66; that is the new row.
- **Scoped gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` at this head prints `MODE: SCOPED -- 4 script(s) run, 29 scoped out`. It names four scripts:
  - `tests/arch_score.py`: it re-derives the record above and runs on CI (heavy-script rule).
  - `tests/arch_score_head.py`: `ALL 16 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 169 checks PASSED`.
  - `tests/entities.py`: `ALL 2346 ENTITY CHECKS PASSED`.
- **`run.sh`'s `run_always` scripts, at `8fef64874`.** `tests/env_drift.py --claims-only 6e5753a4aca8b240559e8e11e8a68c7de988cd73` prints `claims hygiene: ... ok`. `tests/closure.py selftest` prints `ALL 115 closure shrink pins PASSED`. `tests/harness_headers.py` prints `ALL 109 HARNESS HEADER CHECKS PASSED`. `tests/layout.py` prints `layout self-test: ok`. `python3 tools/audit/seat/tmp_paths.py --check` prints `0 refused`.
- **Agreement lane.** `node tools/policy/agreement.mjs --only discovery`, run with `tools/policy/agreement.mjs` equal to origin/main, prints `unregistered=0` and `AGREEMENT ok`.
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

## Architecture score

n/a: no package file changes.

## Red checks

none at the handoff; CI has not run on this head.

## Forward-carry

- **R10-BRIEFS-FOLD (`dev/governance/dimensions/D7.md`).** The folded brief can cite `shape_copies` as a finder's census of rule families below the clone window. It should cite it with its stated limits: spelling-blind, weight 0, and C23 load-bearing only for copies below the window (`ABOUT.md`, part 5). The roster carry is the orchestrator's to write.

## Friction

- R10-ARCHSCORE-COVERAGE-p5: cost: the first plants were at the clone window, so `duplication_copies` refused them and C23 carried nothing. The ablation arm caught it. Planting below the window was the fix, which is a reason to run the ablation before writing the case set rather than after.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
