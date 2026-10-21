Fix review: merge d809c1f30f02b417dfd2d29ac5a98b6dd2803a55

bus-nonce: 3417d19a57ee47d2124a34be56bab9b1

Round 3. Earlier rounds: round 1 `blocked de28f656 root-cause-unanswered: mutation`; round 2 `blocked d0cdac2ef metric-gamed` (probe/rev-2527-98e8d4b4). Measured head `d809c1f30f02b417dfd2d29ac5a98b6dd2803a55` (ev/HEAD.txt). Merge base `22615537a497c87cf0560ecc7dd09faac52b1de5`, which was origin/main when the review started. `git diff <mb>...origin/main -- dev/governance/roles/` was empty, so this contract is current. Interpreter: /opt/hpo/venv-ci (CPython 3.14.7).

## RESULT lines (mine)

The finder's harness is `dev/audit/rounds/round10/D7/s2/learner_gates.py`, sha1 `5b77f874…` at both ends, committed in the r10 intake `9355f107d`. `freq_map_defrost_folds` drives the real `_observe_frequency`, not the gate alone.
- base:  RESULT freq_map_clean_folds=8, RESULT freq_map_defrost_folds=8, RESULT defrost.learners_ingesting=2, RESULT pump_offline.learners_ingesting=1
- head:  RESULT freq_map_clean_folds=8, RESULT freq_map_defrost_folds=0, RESULT defrost.learners_ingesting=1, RESULT pump_offline.learners_ingesting=1
- base --perturb: defrost_folds=0, clean 8, so the perturbation moves the harness. head --perturb: 0 (vacuous at the head, as the body says).
- structure.py, budgets byte-identical to main: base and head both RESULT class_excess_loc=18299, max_class_loc=8541, seam_cut_total=718, STRUCTURE RATCHET PASSED.
- Null control (round-2 plant, an unrelated ternary re-wrapped onto one line) at the head: 18295 / 8537, `2 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED`. The instrument does see a re-wrap.
- Step 14, payment removed: I restored the `configured` local and the old `source == FREQ_SOURCE_NUMBER and configured == … and not self._freq_fallback` mode guard, and kept the fix. That reads 18300 / 8542 / 719, over budget on all three. So the flat figure is paid by deleting the duplicated `_freq_mode` predicate, not by layout. The diff re-wraps nothing: it changes coordinator.py by 18 lines added and 18 removed, the docstrings keep their line counts, and the watchdog guard goes from one line to one line. The payment is equivalent behaviour: `resolve_reading` returns FREQ_SOURCE_NUMBER exactly when `compressor_freq_entity` is set, and `_freq_mode` reads that same config and `self._freq_fallback`. Mutant m5 below shows it is pinned.
- features.py at head: ALL 4271 FEATURE CHECKS PASSED. entities.py at head: ALL 2376 ENTITY CHECKS PASSED (`defrost_standoff` ok).
- env_drift.py --all against mb: NO UNCLAIMED DRIFT (56 scenarios), NO STALE FIXTURE. No claim file is touched.
- VERSION, the manifest version and RELEASE_NOTES are untouched; no `*_budgets.json` or closures.json is in the diff.
- `git merge-tree --write-tree origin/main <head>`: exit 0 against 22615537a, and exit 0 again against the newer main 5d433771a (tree 60873d29b). main's new commits touch only delivery rows.
- ci_predict at head: the same 2 added unpinned sites the body lists (1012 GUARD_OFF, 10595 GUARD_OFF), and no closures or fast red predicted.
- The PR's own three-dot diff is identical at the authored head 25a94521b and at d809c1f, so the orchestrator's main merge carries no resolution delta.

## Mutants (applied in separate worktrees of the head, tests/features.py)
- m1, both fix terms deleted: 2 of 4271 FAILED (`a defrost interval never teaches the frequency map`, `defrost ticks never stand control down`). The null-control check stays ok.
- m1a, fold term only: 1 failed (the map check). m1b, watchdog term only: 1 failed (the watchdog check). Each term is pinned on its own.
- m2, the fold gate's first guard set to `if False:`: 4 failed (immersion, defrost, resistive heat, night mode), as the body says.
- m3, the caller's fold guard set to `if False:`: 6 FAIL lines, then TypeError, EXIT=1, as the body says.
- m4, `defrost_interval` returns False: 2 failed. m8, it returns True: 9 failed, including `null control: a non-defrost interval still folds`. The null control discriminates.
- m5, the watchdog mode guard widened to `!= "unconfigured"`: 1 failed (`no number, no watchdog …`). The `_freq_mode` payment is pinned.
- entities.py m6, the matcher's owner-call exemption removed: 2 of 2376 failed, SEAM at 1012 and 10565. This reproduces the body's 5e8ab1c45 figure.
- entities.py m7, the fold gate reads `coord._pump_signals.defrosting` directly, bypassing the owner: 2 failed, SEAM 1012. The rule catches a divergent predicate.

## Rulings
- **Open question: is `_freq_fold_blocked` inside the seam?** Yes. Its only production call site is `_observe_frequency`'s fold guard (coordinator.py:10595; grep finds no other caller). It is that method's fold gate, written as a module-level helper on `_cop_fold_blocked`'s precedent. The finder's harness reads it as the `freq_map` column. The architect note's shape, "one defrost predicate, owned by the frequency map", is met: `freq_control.defrost_interval` sits in the map's module, and both the fold gate and the watchdog call it. `_cop_fold_blocked` is called, not edited. No hunk outside `_observe_frequency`, its fold gate and freq_control.py touches production code, and `_freq_view` is byte-identical to main. So there is no architecture-unsound finding (step 15).
- **Class (step 6).** The body's rule is the P2 `defrost_standoff` entry. It returns one other decision site, `_learning_frozen`, dispositioned as the plant-wide gate. My grep of `.defrosting` reads in production finds 1012 and 10565 (owner calls), 6229 (passed to `_defrost_window.observe`, not a decision) and 6373 (`_learning_frozen`, dispositioned). The class is not left open. The rule's known blind spot, a flag copied to a local first, is carried.
- **Forward-carry (step 10).** The `pump_offline` arm is carried in R10-ARCH-SHAPES's carry on `handoff/audit-r10-roster` at 617ce13160e7, with its control stated: the finder's harness reads freq_map=INGEST on the pump_offline row at both ends. The local-copy blind spot is carried there too. I re-measured pump_offline.learners_ingesting=1 at both ends.
- **Red checks (step 11).** These are read from check-runs at d809c1f.
  - `nightly-status` is red. It grades main, and this diff reaches nothing it reads. The body answers it.
  - `mutation` (job 119250865908) is red with `MUTATION TABLE REFUSED -- 4097 unpinned against 4097 at the ratchet base, 2 of them added by this diff`. Those are exactly the two `ADDED UNPINNED` sites (1012, 10595) that the body names under `## Unpinned sites`, each with the mutant that kills it. I reproduced both kills (m2, m3). This is the `ci-autofix.md` "unpinned sites" path, and `mutation-pins (1)` was still in progress when I read the check-runs.
  - The body's `## Red checks` list names `mutation` only at earlier heads, with this same cause and the cheaper detector (ci_predict). I read this head's red as answered in substance by `## Unpinned sites`.
  - In any case, no pr-contract run started after the mutation red concluded: pr-contract 119251161363 started 13:30:28, and mutation concluded 13:30:29. So `root-cause-unanswered` was not postable.
  - Everything else concluded at the head is green: fast (3.14), coverage, typing, browser, CodeQL, arch-score, budget-raise-gate, pr-contract. `closures` was still in progress.
- **Expected head move.** `mutation-autofix` should push `ci: pin killed mutants`, which adds ledger pins only. This verdict carries to that head only under orchestrator.md section 11's carry predicate. Any other move is re-reviewed.
- **Step 12.** I re-read the head before writing: `refs/heads/fix/r10-freq-defrost` = d809c1f30f02b417dfd2d29ac5a98b6dd2803a55.

## Disclosures
- I built no instrument. The finder's harness is committed. Mutants, the payment-revert arm and the plant are diffs in ev/.
- I did not re-derive the body's 9-snippet matcher probe, which lives out of tree under the fixer's scratch. I tested the matcher with m6 and m7 instead.
- I did not run archscore myself. CI arch-score is green at the head, and the body quotes `dS +0.0000 NULL`.
