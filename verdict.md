Fix review: merge ce7ed26bfe4724d99ad43dcfc9c1d679933ce156

bus-nonce: 05aee51f5527e74c178ad4048a7a8bdc

Delta review, round 5 of R10-CURRENCY (PR #2620), head ce7ed26bfe4724d99ad43dcfc9c1d679933ce156 (still the PR head at posting). Judged: the resolution delta 0b9431ba..ce7ed26bf only. The earlier rounds' verdicts stand for the unchanged code. Measured in a detached worktree at the head; origin/main is a6620c30a.

## Findings

- The branch still carries three older commits with Claude trailers (701448f90 and 23392d5d6 `Co-Authored-By`, 08ba3d9d7 `Co-Authored-By` and `Claude-Session`). None is from round 5: the three round-5 commits (9195247d4, 5115ddc15, ce7ed26bf) are clean. The footer rule is not this round's to enforce; the merge path decides whether they survive. Carry: dismissed: pre-round-5 commits already reviewed in rounds 1-4; no round-5 change owes it.

## Evidence

1. Merge resolution.
   - `git diff origin/main ce7ed26bf` touches only coordinator.py (two comments and the `self.currency` narrative read), narrative.py, tests/features.py (+61/-2), structure_budgets.json and the delivery row. Nothing of main's #2647 is reverted: coordinator.py differs from main by exactly #2620's 6+/6- lines (ev/ shows the stat).
   - `_cop_watch` has no caller or definition at the head: `git grep` finds only the unrelated `score.reason_cop_watch_learning` card strings, 0 hits in tests/seam_map.json, 0 `killed_by/coordinator.py/*_cop_watch.*` files.
   - Both machine-grade checks pass `_rs_advice(coord)` to `_scores_view`, the same call shape as main's neighbouring checks, and pass.
   - D14-s3-01 reverted (`narrative.render(..., resolve_currency(hass))`): FAIL "D14-s3-01: the narrative prices a EUR feed on a SEK instance in EUR..." (ev/mut_m1.txt). Not silently reverted.
2. Four red-on-revert mutants reproduce at the head (each is a `git archive` copy run through tests/features.py; every one also trips the archive runner's #363 recorded_at line, which is the runner's, not the mutant's):
   - #2620's side of both conflict regions with `_cop_watch` restored (`git merge-file --ours`): FAIL R9-P3 (second floor on house_heat_loss_scale) (ev/mut_m4.txt).
   - `_watched_cop_buckets` `>=` to `>`: FAIL "the machine grade starts at exactly COP_BASELINE_MIN_SAMPLES samples [{19: None, 20: None}]" and main's #12/#2258 twin (ev/mut_m3.txt).
   - clip removed from `machine_score`: FAIL "a machine past the alarm threshold still grades 0, not below [-100.0]" and the #2258 twin (ev/mut_m2.txt).
   - narrative back to `resolve_currency(hass)`: FAIL D14-s3-01 (ev/mut_m1.txt).
   - With `PREPR_SKIP_CLOSURES=1` and the CI venv (/opt/hpo/venv-ci, 3.14): tests/features.py `ALL 4334 FEATURE CHECKS PASSED` rc=0; tests/entities.py `ALL 2406 ENTITY CHECKS PASSED` rc=0. Scoped gate: `MODE: SCOPED -- 21 script(s) run, 12 scoped out.` (ev/mode.txt). The body's figures match.
   - Finder's harness p8_replay_currency.py (group R10-CURRENCY brief), printed by me: main `base_mismatched_seams=1`, head `0`; `clean_mismatched_seams=0` and `reintroduce_mismatched_seams=14` at both ends (ev/harness_main.txt, ev/harness_wt.txt).
3. Budget record. `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED`, `seam_cut_total=715`, `class_excess_loc=18243`, `max_class_loc=8479`; the budget diff against main moves only those three rows and `recorded_at`. Main reads 714 / 18244 / 8480 and the `views` row is 109 there, 110 at the head. Every other row is unchanged against main. Earned by the change: reverting only the narrative read to main's `resolve_currency(hass)` gives `seam_cut_total=714` (ev/m1_structure.txt), so the +1 is #2620's own `self.currency` read in `_narrative_view`. `archscore --diff origin/main HEAD` prints `dS +0.0000 NULL`. The body's `## Raise justification` passes `budget_raise_gate.justification`: `(True, "the body's `## Raise justification` names the payments tried and the arch_score figures")`. Payments (b), (b'), (a), (c): I found no payment the body missed that would improve the architecture; (b) and (b') only change the occurrence count or move the read into the unpriced `core` seam, and I name no better one. The raise is therefore not metric-gamed. The class_excess/max_class drops (-1 each) come from the deleted `_cop_watch` helper being absent, which main's own caps already reflect; they are recorded down.
4. Merge and CI. `git merge-tree --write-tree origin/main ce7ed26bfe4724d99ad43dcfc9c1d679933ce156` exits 0, clean (ev/mt.txt). VERSION is 7.0.4 and untouched by the branch (empty three-dot diff). Check-runs at the head (one bulk call, ev/checks_nonsuccess.txt): all green or skipped except `budget-raise-gate` (failure, by design until the approving review), CodeQL neutral and `Analyze (python)` still in_progress at posting. `fast (3.14)`, `closures`, `coverage`, `mutation`, `pr-contract`, `arch-score` and `typing` were success. The body's `## Red checks` answers budget-raise-gate.
5. Forward-carry and body. The R10-STRUCTURE-ALIAS carry is in the body and on the roster, as in earlier rounds. The body names this head. An earlier head hash in the body text (`f46fd74f`) is a stale line from the orchestrator's recarry and is cosmetic.
6. Not verified by me: the `dS` figures for payments (b) and (b') (not rebuilt); the older rounds' mutants (carried); card_drift and env_drift (this round touches no fixture).
