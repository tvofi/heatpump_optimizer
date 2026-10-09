Fix review: merge e2821b6dcaa9a00e74b20df6713f5cb5a1f445e6

Round 4 — judgment of the resolution merge only (previous verdict at `5bcf9d2b20`;
reviewed code unchanged from `63e4eba355` except the two step-6d conflicts).

RESULT: silent-revert sweep — branch 3-dot: 188 added lines, 186 verbatim at HEAD; the 2 absent are the branch's pre-merge `triage_key` spelling of the single chained ADDED UNPINNED return, superseded by main's multiplicity line with the stale prefix kept. Main-side in the same files: 82 added, 80 verbatim; the 2 absent are main's un-prefixed spelling of that one line. Full-tree `git diff origin/main HEAD` (2-dot) touches EXACTLY the branch's five files (188+/6−) — no main line reverted anywhere.
RESULT: literal sweep of both parents' `ci_predict.py`/`prepr.sh`: MAIN 812 literals, 0 missing at HEAD; BRANCH 798, 5 missing, all five shared lines main reworded (sed regex, section-missing message, pmut plant, two no_recording/unpinned spellings). Arms named present per side: branch — `stale_pin_preds()`, `stale =` compute, both `stale +` chains (BASE UNREADABLE, ADDED UNPINNED), ledger remedy line, `startswith("ADDED")` sites count, pstale/pstaleun plants, the three STALE PIN assertions, step-6d header; main — `no_recording(root, base…)` lane-drop arm and call site, `added_keys` multiplicity, `*N` sed capture, whole-key awk + near-hint, `--existing-file` body_check with rc/rm, rowadd/rowedit, planes/pdrop, `if 0 < x < 3:` pmut, CMP_BOUND*2, b4-b7 arms.
RESULT: `bash tools/pr/prepr.sh --self-test` at HEAD → 223 passed, 0 failed, exit 0 (fixer's figure re-measured); STALE PIN arms AND main's NO-RECORDING/delivery-row/multiplicity/whole-key arms all ok, exact assertion lines cited in evidence.
RESULT: mutation proof — deleted `stale = stale_pin_preds(...)` and both `stale + ` prefixes (local scratch commit, never pushed; self-test clones committed history, so the removal was committed before the run) → 220 passed, 3 failed, exit 2: exactly the three STALE PIN arms, nothing else. File restored byte-identically, worktree reset clean to e2821b6dc.
RESULT: determinism — two `ci_predict.py --base origin/main` runs byte-identical, rc 0, null-control text as in the body; predict() appends in fixed order, dedups `seen, out`, `completeness_problems` sorts dispositions.
RESULT: step 11 — head ran 40 check-runs (38 names), all completed, latest-per-name 26 success + 14 skipped, 0 red; all 17 required contexts of ruleset 23698884 ran and succeeded. Own range census per commit: `nightly-status` failed at three heads (5c937c9bc, 3637f1c78, 5bcf9d2b2) and `Analyze (python)` was cancelled at 5c937c9bc. The body names and answers nightly-status (main's, unread by this diff — confirmed: branch touches no nightly record; green at head); its census says "the one red," true of the cited head only — a finding, not a block; the cancel is not a red conclusion and the check is green at head.
RESULT: step 13 — `git merge-tree --write-tree origin/main e2821b6dc` exit 0, stderr empty, no MERGE-CLAIM marker (driver installed); result tree == HEAD tree; `tests/closures.json` blob `ca36c9b2` identical main/HEAD/result.
RESULT: step 14 — no budget/ledger/claim/closures file moved; structure ratchet PASSED; `env_drift.py --all` → NO UNCLAIMED DRIFT, NO STALE FIXTURE; claim files byte-identical to origin/main (`62bf9eaba2`, `c683379daf`); VERSION/manifest/RELEASE_NOTES untouched.
RESULT: cost re-derived quiet (first read of 3.4 s was my own contention under the self-test): `completeness_problems(load_budgets(), inventory())` median 2.3 ms (min 1.8, max 11.1 ms over 25 calls; 5891 sites, 1251 dispositions, 0 problems) — body's 0.0068 s same order, cost test unaffected.
RESULT: forward-carry — `dev/programme/carries/carry-201.json` carries both #2073 entries (brief_lint `wood_share:1152` fixture; `--perturb` gap) with control, remeasure and precondition; RCA doc complete with state (c), class scope, refusals with numbers.
RESULT: step 12 — head unchanged from measurement to post (`headRefOid == e2821b6dc`), origin/main still b2b6acd64 fully merged, PR OPEN/MERGEABLE.

Body's head SHA matches the head measured. The resolution kept both sides; every failure mode I planted or swept says so.

bus-nonce: 96514bfe0ba86041c9f83097bd18a63a
seat: review-2073b
Evidence: /Users/timmalmstrom/hpo-seats/review-2073b/evidence/
