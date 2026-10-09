# Review notes — arm enumeration and figures (round 4, head e2821b6dc)

## Arms seen present at HEAD — ci_predict.py
BRANCH side (from 63e4eba35, all present):
1. `stale_pin_preds()` function (whole, verbatim).
2. `stale = stale_pin_preds(m.completeness_problems(budgets, sites), base)` in `unpinned()`.
3. `return stale + [BASE UNREADABLE ...]` (chained).
4. `return stale + [ADDED UNPINNED {k} ... for k, s in m.added_keys(added)]` (chained, main's spelling).
5. remedy line `a STALE PIN's file ... deleted by hand` in `main()`.
6. sites count narrowed to `l.startswith("ADDED")`.
7. step-6d comment: "and a STALE PIN the diff itself stales" (prepr.sh).
MAIN side (from b2b6acd64, all present):
1. `no_recording(root, base, ...)` refactor with `dropped = recs(show(root, base, lane)) - recorded` lane-drop arm, `f"{lane} records it"`, and call site `preds += no_recording(root, base, changed, closure)`.
2. `m.added_keys(added)` multiplicity in `unpinned()`.
3. literal sweep: 53 MAIN literals (ci_predict.py) + 759 (prepr.sh) — all present verbatim at HEAD (0 missing).

## Arms seen present at HEAD — prepr.sh
BRANCH: `pstale` + `pstaleun` plants (chained after `pmut`), the three STALE PIN assertions
(refuse rc=1, refuses-not-warns, ON MAIN null control), header comment. All +14 lines present.
MAIN (all present): `predict_line` sed extended `([A-Z_]+(\*[0-9]+)?)`; `unpinned_line` whole-key
awk + `near` hint; `body_check --existing-file` + rc/rm; rowadd/rowedit plants + 2 assertions;
planes/pdrop plants + 2 NO RECORDING assertions; pmut `if 0 < x < 3:`; `CMP_BOUND\*2`
multiplicity assertion; b4-b7 whole-key/backtick tests. +66 lines present.

The only lines that vanished at HEAD are the two pre-merge spellings of the ONE chained
ADDED UNPINNED return: branch's `triage_key` version and main's un-prefixed version. HEAD
keeps both sides' semantics: stale prefix + multiplicity key.

## Sweep
Branch 3-dot additions: 188 lines, 186 present verbatim, 2 = branch's pre-merge spelling.
Main-side additions in the same 5 files: 82 lines, 80 present verbatim, 2 = main's spelling.
Full-tree 2-dot `git diff origin/main HEAD` touches EXACTLY the branch's 5 files (188+/6-).

## Step 11
Head check-runs: 40 runs, 38 distinct names, all completed; latest-per-name: 26 success,
14 skipped, 0 red. All 17 required contexts of ruleset 23698884 (main-protect-checks,
required_status_checks.parameters.required_status_checks) ran and succeeded.
Range census (own API per commit): nightly-status FAILED at 5c937c9bc, 3637f1c78, 5bcf9d2b2;
Analyze (python) CANCELLED at 5c937c9bc; 422e47975 and 63e4eba35 clean/no-runs; head green.
nightly-status is named and answered in the body (main's, not this diff — branch touches no
nightly record; nightly-status green at head). The body calls it "the one red in the census"
which is true of the cited head only; the range carried it at three heads. Not a block.

## Step 14
No *_budgets.json, closures.json, ledger, or claim file in the diff (blob-verified identical:
closures.json ca36c9b2 main==HEAD==merge-tree result; claims 62bf9eaba2 / c683379daf
byte-identical to origin/main, matching the body's citation). `tests/structure.py` →
STRUCTURE RATCHET PASSED rc 0. `env_drift.py --all` → NO UNCLAIMED DRIFT (56), NO STALE
FIXTURE, rc 0. VERSION blob 70e781d3 identical main/HEAD; manifest and RELEASE_NOTES not
in the diff.

## Cost re-derivation
`completeness_problems(load_budgets(), inventory())` after warm preload, 25 timed calls,
quiet machine: median 2.3 ms, min 1.8 ms, max 11.1 ms; 5891 sites, 1251 dispositions,
0 problem lines. Body's quoted 0.0068 s is the same order (under 3x my median; the RCA
states ~0.01 s). First measurement under self-test load read 3.4 s — contention, not the
arm; re-taken quiet. Cost test verdict unchanged.

## Mutation proof (step 1)
Removed the `stale = ...` line and both `stale + ` prefixes locally (committed in scratch
only, never pushed), re-ran `prepr.sh --self-test` in the clone-built harness: 220 passed,
3 failed, exit 2 — exactly the three STALE PIN arms failed, nothing else. Restored the file
byte-identically (diff vs saved original: empty) and reset to e2821b6dc; worktree clean.

## Determinism (step 3 of brief)
Two `ci_predict.py --base origin/main` runs at HEAD: byte-identical output, rc 0 both —
"CI PREDICT: no closures or fast red predicted against b2b6acd64cde (a data-file read is
not seen)". Mechanism confirmed: predict() appends arms in fixed call order and dedups via
`seen, out`; completeness_problems iterates `sorted(dispositions(...))`.

## Step 13
`git merge-tree --write-tree origin/main e2821b6dc` exit 0, stderr empty — no conflict, no
MERGE-CLAIM marker (driver IS installed: merge.claimnotes present in this checkout's
config). Result tree 068ca8af05... == HEAD's tree — the merged answer is this head.

## Forward-carry (step 10)
`dev/programme/carries/carry-201.json` carries both #2073 entries with effect/control/
remeasure/brief: the `wood_share:1152` frozen-fixture pin, and the CI-never-runs-`--perturb`
gap for D11/D13. RCA doc dev/audit/rca/R9-RCA-stale-pins.md is complete (cause, state (c),
class scope, cost test, countermeasure shown failing and passing, refusals with numbers).
