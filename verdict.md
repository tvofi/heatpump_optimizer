Fix review: merge 310c601f4078a394fe527329a6a1fd8e1368cca0

bus-nonce: 055f0ca05bc8c21ef910dc8ec5d8f7c9
pending-ci: mutation

Note: owed-red: root-cause-detectable: `tests / mutation` (job 137318434203) is red at this head: the nine sites 2cae6b5d0e moved carry no `killed_by` pin (the commit deletes the nine old coordinator.py pins for the lines it moved and records none for the new ones). The body's `## Unpinned sites` names all nine as unmeasured at 2cae6b5d0e and leaves them to CI; `tests / mutation-pins (1)` and `(2)` were in progress at 20:05Z. The cheaper detector is targeted block mutants (`features_block.py`, three blocks): this seat ran all nine in about 25 minutes, and every one is killed (below), so the autofix pins are expected to land. Carry: dismissed: ci-autofix's mutation-pins lane pins killed sites, and this seat measured all nine killed
Note: stale-figure: the body's `## Figures` and `## Architecture score` are still measured at 4e5de6bad8 (`--diff 6fdc15354f`, features 6041), as the body itself says. This seat re-took the delta's figures at 310c601f below. Carry: dismissed: paperwork on body figures; the substance was re-measured at this head

Round 6, delta only (owner ruling: review the delta). Reviewed head c931e99404d39ceaf9c8d84a68b5e24b7dec5f11 (round-5 draft verdict `merge`, probe/rev-3738-055f0ca0 b669eb6e) -> 310c601f4078a394fe527329a6a1fd8e1368cca0. `review_carry.py c931e994 310c601f` prints FRESH-REVIEW, so the delta was read by hand. No earlier round's block is open, so the fourth-round re-cut rule does not apply. No new nonce was issued to this seat, so the round-5 dispatch's nonce is carried.

## Delta
- First-parent chain: e7dc8a8a78 (merges main at 59b17e97ae), a004c65395 (merges main eaaaf24e5b), 2cae6b5d0e (the code change), 310c601f40 (a fast-forward-shaped merge whose tree equals 2cae6b5d0e's: `git diff 2cae6b5d 310c601f` is empty).
- Main merges: `git show --remerge-diff` prints no conflict hunks for either merge. Only the LEDGER-MERGE driver resolved `tests/structure_budgets.json` and `tests/closures.json` (ev/remerge_*.txt).
- 2cae6b5d0e moves `_WORKER_STOPPING`/`_worker_stopping` and `_mode_superseded` from coordinator.py to solve_gate.py (`WORKER_STOPPING`, `worker_stopping`, `mode_superseded`). The run's entry mode moves from a local in `async_run_optimization` to `SolveGate.entry_mode`, which `begin_solve(gate, mode)` sets. features.py follows the key rename (3 lines), and nine stale ledger pins are deleted.
- Behaviour equivalence: `entry_mode` is written only by a `begin_solve` that passes `absorb_request` (`solving` False), so no request can overwrite it during a solve. It is read at 6407, inside the solve, and at 6487, after `end_solve` but before any await, with the same value the old local held. Other `begin_solve` callers are tests only (`grep`, features.py:728, 97909, 97922, 97925). Its default `""` reads not-superseded, which is the old behaviour for a non-optimizer entry mode.
- No widening: the production delta is a move whose reviewed behaviour the nine kills below pin. Main's production delta is CI's.

## Prior findings
- Note stale-figure (round 5): still stale (Note above, re-carried).
- Note owed-red coverage-ratchet (round 5): `tests / coverage-ratchet` is queued at this head (job 137330621622), and `tests / coverage` is success. The body's `## Red checks` still answers it. No new figure exists to compare.
- Round 5's mutation pins (eight sites): these are untouched by the delta except where 2cae6b5d0e moved lines. Those nine sites are measured below.

## Evidence
- RESULT head: refs/pull/3738/head = refs/heads/fix/r11-seam-cycle-solve = 310c601f4078a394fe527329a6a1fd8e1368cca0 at 20:05Z. The body's `## Head` names 310c601f and its code head 2cae6b5d0e, which matches.
- RESULT merge_tree_rc=0: `git merge-tree --write-tree origin/main 310c601f` (origin/main 1207ee13b0 at 19:06Z).
- RESULT version/claims: `git diff --name-only <mb>...HEAD -- VERSION RELEASE_NOTES.md manifest.json tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt` prints nothing.
- RESULT structure: `python3 tests/structure.py` at 310c601f prints STRUCTURE RATCHET PASSED rc 0, with class_excess_loc 17314 <= 17314, max_class_loc 7865 <= 7865 and module_excess_loc 21779 <= 21779 (ev/structure.log). There is no raise: against the merge base eaaaf24e, every `*_budgets.json` change is a decrease (class_excess_loc 17317->17314, coordinator_attrs 136->135, coordinator_multiassigned_attrs 104->102, max_class_loc 7868->7865), plus `recorded_at`.
- RESULT earned (step 14): at a004c65395, the parent before 2cae6b5d0e, structure prints `FAIL module_excess_loc 21794 > 21779 (+15)` (ev/structure_pre_2cae6b5d.log), so main's merge pushed it over and 2cae6b5d0e pays the 15 by moving the stop-mark and mode-supersede code to the seam that holds the solve's state. `archscore/score.py --diff a004c653` at the head prints `Architecture score: dS +0.0000 NULL` (ev/archscore_2cae6b5d.log), not worse. The move puts the entry-mode state with the gate it belongs to rather than respelling lines, so it is not metric-gamed.
- RESULT mutation driver: `tests/mutation_table.py --pin-killed --base eaaaf24e --scripts tests/features.py` lists `9 new unpinned site(s)`, the body's nine. Its features.py baseline is rc 0 (976 s) and its null control `coordinator.py:396 NULL_COMMENT` survived. The full drive was still running at publish (ev/pin_drive.log), so its verdicts are not cited.
- RESULT targeted mutants, each run through `features_block.py` with a prelude from `--emit-prelude` at 310c601f on three blocks: A `# -- R11-SEAM-cycle-solve` .. `# --- R10-DRAW-MAP-EVIDENCE part A`, B `# --- R10-LIVESTATE` .. `# --- #1955 fold (e)`, and C `R.section("#1754 — a refresh during` .. `R.section("#2257`. All three blocks pass unmutated (0 FAIL each). Each file was restored and `git diff --quiet` checked after each mutant (ev/blocks/summary.txt):
  - coordinator.py:2326 GUARD_OFF: KILLED, A 1 FAIL "D1-s1-01: a worker the stop killed raises no fallback notice ...".
  - coordinator.py:6330 GUARD_OFF: KILLED, B 2 FAIL "D1-s1-02: a comfort, boost or off write inside the solve await ...", C 1 FAIL "a run request during an in-flight solve returns at once ... (#1754, the solve gate)".
  - coordinator.py:6407 GUARD_OFF: KILLED, B 2 FAIL "D1-s1-02: a comfort, boost or off write ..." and "a re-run requested mid-solve is dropped when a fixed mode superseded the solve ...".
  - coordinator.py:6478 GUARD_OFF: KILLED, A 1 FAIL "D1-s1-01: a solve the stop broke answers 'shutdown' ..." `[('solve_failed', 1, False)]`.
  - coordinator.py:6487 GUARD_OFF: KILLED, B 1 FAIL "a re-run requested mid-solve is dropped ...", C 1 FAIL "a refresh requested during an in-flight solve re-solves against the new override ... (#1754)".
  - solve_gate.py:106 BOOLOP: KILLED, B 2 FAIL "D1-s1-02 null: a solve whose mode stays AUTO adopts its plan ..." `[result=False pending=0]`. In C it ran into the 900 s timeout (rc 124) after 5 FAIL. It does not deadlock the B kill.
  - solve_gate.py:106 RETURN_DEL: KILLED, B 2 FAIL "D1-s1-02: a comfort, boost or off write ...".
  - solve_gate.py:112 BOOLOP: KILLED, A 1 FAIL "D1-s1-01: a worker the stop killed raises no fallback notice ...".
  - solve_gate.py:112 RETURN_DEL: KILLED, A 2 FAIL, both D1-s1-01 checks.
- CI at this head, 20:05Z (`get_check_runs`): success for tests / closures, coverage, browser, typing, arch-instrument, nightly-ha (stable, 2025.2.0), closure-scope, briefs, graders-head-copy, nightly-status; governance / instrument-self-tests, wave-script, policy-docs, env-matrix; hassfest, validate-hacs, codeql (3), arch-score, and budget-raise-gate. Failure: tests / mutation (Note above), and `gate` (jobs 137320505095, 137325200267), which ran before the tests run ended. In progress: tests / fast (3.14) and mutation-pins (1)/(2). Queued: coverage-ratchet. Cancelled: tests / replay.
- Measured by this seat from a detached worktree at 310c601f, with the finder-side drivers only (`mutation_table.py`, `features_block.py`, `structure.py`, `archscore`). No fixer harness was used.
