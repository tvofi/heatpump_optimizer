Fix review: blocked 1abb0abab0dd1f3d9ec30f790fffd75c042dabe6 mutation-vacuous: check_scopes.py main() exit bypassing verdict() survives --self-test

bus-nonce: d3dbea85c79ac212c4f0ffe7b569aa4d

Round 1. Reviewed at head 1abb0abab0dd1f3d9ec30f790fffd75c042dabe6, in a detached worktree, with my own perturbations and my own glob matcher. I did not use the fixer's harnesses (`seatdiff.sh`, `cov.py`). Contract: `dev/governance/roles/fix-review.md` at origin/main. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Block

- **The default run's exit can drop coverage and citations, and no check fails.** Mutant CM4 (`ev/CM4.patch`) changes one line: `main()` returns to the pre-PR exit, `sys.exit(0 if check(scopes, tree, loc) else 1)`. Under that mutant, `python3 tools/audit/check_scopes.py --repo . --self-test` stays rc 0 and prints `SELF-TEST passed (every perturbed scope refused)`. The default invocation (`--repo . --ref HEAD --scopes <D4/D6 blueprints dropped>`) then exits rc 0 on 5 unclassified paths. Unmutated, it exits rc 1 (`ev/check_scopes_code_mutants.txt`).
- The self-test drives `verdict()` as a function, but nothing pins that `main()`'s default path calls it. The repo's only other uses are `governance.yml:543`, which is the self-test, and `check-wave-script.mjs:1034,1037`, which pin the Prepare prompt's text and never run the script.
- This is the same shape as the survivor the body says `verdict()` was built to kill: "coverage was dropped from the exit code and the self-test stayed green". It is one call level up. So design-review C1 / Carry 1 (coverage in the default invocation's exit code) is not pinned, and the self-test's comment "so neither coverage nor citations can fall out of the exit code" is false at the call site.
- Repair: the self-test runs the real default path, e.g. `subprocess.run([sys.executable, __file__, "--repo", a.repo, "--ref", a.ref, "--scopes", <tmp no-D10 scopes>])`, and requires rc 1 there and rc 0 on the live scopes. Or route both the self-test and the default exit through one function that the self-test calls with the parsed args. Show CM4 red afterwards.

## Findings

- check_scopes.py: the default-invocation exit is unpinned (mutant CM4 survives), as described under Block. This PR must settle it before merge. Carry: R10-AUDIT-COVERAGE-ENDGAME

## Evidence

- Head: `1abb0abab0dd1f3d9ec30f790fffd75c042dabe6` (`ev/HEAD.txt`). It matches `## Head`. Its merge base with origin/main is `ddf4bfd73`. The body's measurements were taken at the authored head `40f6097a1` against `c88d552c7`. I re-took them at both.
- Merge with origin/main `56630e7e6`: `git merge-tree --write-tree origin/main HEAD` gives rc 0 and `LEDGER-MERGE: resolved tests/closures.json` (`ev/merge_tree.txt`).
- check_scopes.py default run:
  - At HEAD: `ok coverage tracked=8107 in_universe=1329 excluded=6778 unclassified=0`, `ok harness citations: 0`, rc 0. These are 5 tracked paths more than the body's 8102, because main moved.
  - At `40f6097a1`: `tracked=8102 in_universe=1326 excluded=6776 unclassified=0`, rc 0, exactly the body's figure.
  - At base `c88d552c7` with base scopes: `FAIL coverage tracked=8102 in_universe=3270 excluded=0 unclassified=4832`, `FAIL harness citations: 1`, rc 1, exactly the body's figure.
- My data mutants on the default invocation (`ev/mut_*.txt`). Each is refused rc 1 by the path it names:
  - D11 universe without its `tests/` globs: unclassified=50.
  - `blueprints/**` dropped from D4 and D6: unclassified=5.
  - An exclusion naming covered `const.py`: "excluded but in a universe".
  - An exclusion `tests/**`: overlaps refused.
  - A planted uncited harness `dev/audit/harnesses/zz_reviewer_plant.py` naming D4.md, in a local scratch commit that was never pushed: `FAIL harness citations: 1`, rc 1. Null control: the same commit with D4.md citing it gives rc 0.
  - Null control: the live scopes give rc 0.
- check_scopes.py code mutants (`ev/check_scopes_code_mutants.txt`):
  - CM2 (excluded-and-covered not refused), CM3 (header window 0 lines), CM5 (citation never refused) and CM6 (verdict drops coverage) are each killed by the self-test, rc 1.
  - CM4 survives (see Block).
- My own universe set diff (`ev/independent_coverage.txt`): a separate matcher, `pathlib.full_match` plus my own brace expansion, over `git ls-tree -r HEAD`.
  - Totals: tracked=8107, covered=1329, excluded=6778, both=0, neither=0. That equals the tool's figures.
  - Per-exclusion matches: rounds 2147, archive 131, programme records 1422, docs/design 6, fonts 6, golden 58, mutation_ledger 3006, LICENSE/NOTICE 2. None is dead.
  - Base scopes on the head tree lose exactly 2147 paths, all `dev/audit/rounds/**`.
  - Null controls: `optimizer.py` is in D0,D1,D2,D3,D5,D7,D9,D10,D12. `build_docs.mjs` is in D6,D11. `py.typed` is in D10 only, as C5 requires.
- `--seat` proof (C2), re-run by me: the base checkout's own script at `c88d552c7` against the head script with head scopes at `c88d552c7`, over 48 seats (`ev/seatdiff.txt`). 40 are IDENTICAL. The rest change: D3-s3 55→121, D4-s1/s2/s3 9→14, D6-s3 6→73, D11-s1/s2/s3 3156→1093. That is exactly the body's figure.
- fold_ledger.py:
  - `check --ledger <c88d552c7 ledger>` gives 14 violations: 6 MISSING-PATH (P1, P5 and P9 barriers; I3, I4 and N-silent-zero detectors) and 8 UNRECORDED-BARRIER (P8, P10, N-name-sort, N-staleness, N-no-expiry, N-log-flood, N-move-stale-path, N-confounded-learner). That equals the body's eight classes and three extra detector tokens.
  - At head: `0 violation(s)`, 47 classes, 749 instances. `--self-test` gives rc 0.
  - The P5 and P9 repoints resolve: `dev/archive/carries/carry-1655.json` and `-1757.json` exist. So do `tools/policy/field_coverage.mjs` and `agreement.mjs`.
  - The four cited barrier check names each occur in `tests/entities.py` or `tests/features.py`.
  - All seven cited landed SHAs are ancestors of HEAD.
  - `git grep INPUT_QUIET_MINUTES -- custom_components` is empty.
- My fold_ledger mutants (`ev/fold_moved_mutants.txt`):
  - FM1 (no existence test), FM2 (any slash is a path), FM3 (barrier field only), FM4 (barrier_refusal ignored), FM5 (substring match) and FM6 (suffix kept) are each killed by a named self-test arm.
- moved_paths.py: with the binary-skip arm removed, the self-test crashes with `UnicodeDecodeError`, rc 1. Restored: `12 checks, 0 failed`.
- Repaired harnesses at head, run by me with `PYTHONPATH=tests/hastub`:
  - `step_grid.py`: `RESULT off_grid_derived=0`, `off_grid_slider_fields=0`, `out_of_range_values=0`, rc 0.
  - `i4_roster.py --dims HEAD`: `=0 count (of 4)`, rc 0.
  - `owner_review.py`: `perturbed_seat_counted=0`, rc 0.
  - I did not re-run the before-states.
- Policy caps: `node tools/policy/policy_lint.mjs --budgets` gives rc 0. D3 46/596 vs 46/607, D4 48/585 vs 48/586, D11 99/1494 vs 103/1499, D15 36/690 vs 37/690, README 243/3880 vs 250/3880. No `*_budgets.json` is in the three-dot diff, so no cap was raised. `## Approval` states the policy approval is pending, owed before merge.
- Three-dot diff:
  - VERSION, manifest and RELEASE_NOTES are untouched.
  - Both claim files are byte-identical to origin/main.
  - `tests/closures.json` adds `tools/audit/seat/moved_paths.py` to entities' closure.
  - `dev/programme/delivery/3149.md` is present.
  - No host path appears in added lines.
- Gate: `tests/closure.py select --diff <merge-base>` gives `MODE: SCOPED -- 1 script(s) run`. `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`, rc 0. I cite CI for the gate run and did not re-run entities.
- Forward-carry: `origin/handoff/audit-r10-roster` gives R10-CATALOG-PR the C6 re-measure step ("A nonzero rc blocks the catalog PR"). Both R10-CATALOG-PR and R10-CLOSEOUT-CLEANUP carry `after: R10-AUDIT-COVERAGE-ENDGAME`.
- Departures raised in the body, none silent:
  - `moved_paths.py`, `D15.md` and `tests/closures.json` are outside the roster's `files`.
  - The README states the retirement rule rather than listing the retired harnesses by name, with its reason.
- Not re-derived by me: the 274→273 stale census, the 4829 per-prefix split at `ca6333333`, and `len(golden.SCENARIOS)=50`.
- CI at this head: `merge_train.py classify 1abb0abab0dd1f3d9ec30f790fffd75c042dabe6 --pr 3149` exited 0, `GREEN ... pending: none red: none` (`ev/classify.txt`). The commit's check-runs API returned 55 runs on one page of 100, so the listing is complete. Every run is success or skipped and none failed, including `gate`, `pr-contract` (twice), `tests / closures`, `tests / mutation` and `governance / instrument-self-tests`. `## Red checks` says `none` on this head, which matches. CM4 survives a green CI because `instrument-self-tests` runs only `--self-test`.
