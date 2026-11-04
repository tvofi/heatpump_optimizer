Fix review: merge e5ea0a66004f01242d27d0c49b0bfecf1bde724a

bus-nonce: 0c2776d85f9ac14b17d1dd6539c72914

Round 3 checks only what changed since my round-2 `ci-red` block at 3f7777a59bc0f95fc47885e68e3f6d4e39e60d55 (probe/rev-3180-56eece9f).
- Head measured: e5ea0a66004f01242d27d0c49b0bfecf1bde724a. It is the authored commit 543fa4f7a plus two merges of origin/main.
- Merge base and origin/main are both a9c2f90fc. main is an ancestor of the head.
- The authored delta touches three files:
  - `replay.py` now finds its root through the inlined canonical `repo_root` instead of `HERE.parents[3]`.
  - `tests/closures.json` adds the harness to `harness_headers.py`'s `inert_reads`.
  - `tests/ci_ratchet.py` corrects the two docstring paths, adds a self-test check that pins `OTHER_WORK_FRACTION`, and discloses the success-only pricing cost in `window_work_minutes`.
- The other 55 changed files are `killed_by` records that came in from main ("ci: record nightly kills"). They are not this PR's work.

Both round-2 reds are cleared at this head's CI run 41800410441, and `merge_train.py classify` reads GREEN.
- All three round-2 findings are resolved in the tree.
- The statistic is unchanged: `ci_budgets.json` has no delta since 3f7777a59, and the replay reproduces every round-2 figure.

## Evidence

- RESULT CI: `merge_train.py classify e5ea0a66004f01242d27d0c49b0bfecf1bde724a --pr 3180` exits 0: `GREEN e5ea0a66004f01242d27d0c49b0bfecf1bde724a pending: none red: none`. It took 25 polls from 08:44Z to 09:14Z (ev/classify.txt, ev/classify_log.txt).
- RESULT check-runs read directly at run 41800410441:
  - `tests / fast (3.14)` (job 126474988019): success, 08:47:57Z.
  - `tests / coverage`: success.
  - `tests / closures` (job 126474988187): in progress at my last direct read. classify then counted it, pending: none and red: none.
  - Also success: `tests / typing`, `tests / arch-instrument`, `tests / browser`, `tests / mutation`, `tests / closure-scope` and `budget-raise-gate`.
  - `tests / nightly-status` is a failure. It grades main, and classify does not count it red here.
- RESULT depth-seam repair, with a null control at both ends. I ran `harness_headers.inline_scan()`, the child process that holds the failing check:
  - At head: rc 0, no output (ev/inline_scan_head.txt).
  - At 3f7777a59: rc 1, `FAIL depth seams: dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py:40: ROOT = HERE.parents[3]` (ev/inline_scan_3f7777a.txt).
  - That reproduces round 2's red, and the fix clears it.
  - The inlined `repo_root` passes the canonical-text comparison against `tools/audit/repo_root.py` in the same scan.
  - The full `tests/harness_headers.py` needs `homeassistant`, which this seat lacks (ev/harness_headers_head.txt). CI's green `tests / fast (3.14)` is its check.
- RESULT inert_reads: `tests/closures.json` now lists `dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py` under `harness_headers.py`. That is the path the round-2 `INERT READS UNDER-APPROXIMATED` line named. CI's `tests / closures` lane is the check, and classify reads it green.
- RESULT self-test at head: 53 checks, 0 failed, one more than round 2's 52. The new check is `the other-work floor sits at a third of the window median (12.3: a half would read 30.3, a quarter 9.3)` (ev/selftest_head.txt).
- RESULT mutants on `OTHER_WORK_FRACTION`, each applied alone and restored (ev/mutations.txt):
  - `1 / 2` and `1 / 4`: 1 failed each, on the new check, so both are killed.
  - `0.34` and `0.32`: 0 failed. These survive by design: the fixture's 12/30 and 9/30 bracket the fraction to (0.3, 0.4], which is the "both sides" pin the commit claims, not a defect.
  - This settles round-2 finding 2: the 1/3 -> 1/2 mutant passed the self-test then, and fails it now.
- RESULT replay at head: exit 0, RESULT: holds (ev/replay_head.txt).
  - It prints grade 20.75, windows 19.967..21.983 and record 21.983 = budget, with band need 0.55 against band 1.3.
  - The outliers read +0.0 / +0.0 / +0.0.
  - The growth table and the slow-fleet line (+6.417 / +6.95 / +5.167) both match round 2. The statistic is unchanged.
- Round-2 finding 1 (docstring paths) is settled: both citations, at `tests/ci_ratchet.py:58` and `:666`, now name `dev/audit/harnesses/r10_hotfix_ci_critpath_3/replay.py`, which exists.
- Round-2 finding 3 (success-only pricing) is settled as a disclosure. The `window_work_minutes` docstring now states that a failing chain job stops pricing, so a broken lane under-reads and a record taken across such a stretch is recorded low. It also quotes the 20.75 vs 21.7 figures from my round 2.
- RESULT merge-tree against origin/main a9c2f90fc: clean, rc 0, tree a1bfec896 (ev/merge_tree.txt).
- Gate scope at head: `tests/closure.py select --diff origin/main` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `tests/structure.py` printed STRUCTURE RATCHET PASSED.
- The 3-dot diff from merge base a9c2f90fc is 6 files:
  - the delivery row, `ci_budgets.json`, `ci_ratchet.py` and `closures.json`;
  - the two harness files.
  - VERSION, the manifest version and the notes heading are untouched.
- Refs re-read before return: refs/pull/3180/head e5ea0a660 and main a9c2f90fc, both unmoved (ev/refs_at_return.txt).
- Not re-derived this round: the round-1/2 runs.json gather and the full mutant table on the median floor. Neither file changed since round 2, which settled both.
