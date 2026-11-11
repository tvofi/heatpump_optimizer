Fix review: merge 311ee9f3fa20ebcb2de65e873cd0c889481a0360

bus-nonce: e41acb3751c33cb6ce646901601382cc

## Scope

First review (round 1) of the fixer handoff `handoff/r10-outside-price-outage-last-valid` (group R10-OUTSIDE-PRICE-OUTAGE-LAST-VALID, size S, built on outside pull request 3437). Reviewed from detached worktrees at `311ee9f3fa20ebcb2de65e873cd0c889481a0360` and at the merge base `86953c6d99ecf7aa86c7bc9d57fec9a991daad07`. Body read from `handoff-body/r10-outside-price-outage-last-valid`. No pull request exists yet, so there is no review packet and no CI run to read.

## Evidence

- Head: `git ls-remote origin refs/heads/handoff/r10-outside-price-outage-last-valid` printed `311ee9f3fa20ebcb2de65e873cd0c889481a0360` at the start and again just before this verdict was written. The body's `## Head` names the same SHA (`ev/HEAD.txt`).
- Last-commit claim verified: `git diff --stat 65b6d1ba3b 311ee9f3fa` touches only `tests/mutation_ledger/killed_by/` (seven pins added, the stale `_tibber_fetch_failed.GUARD_OFF.53f8da35` deleted), with no production or test-script line (`ev/last_commit_diffstat.txt`).
- Authorship: the adopted commit `d17d2cc3f` has the same `git patch-id --stable` as the live `refs/pull/3437/head` `40d7e43d649f4af1531a9031d18ad80e56a1ab17` (`4292b76b...`). Its author stays `Bankaifan`, and only the tool-attribution trailers were dropped (`ev/authorship.txt`). `git log --format=%B` over the branch carries no Co-Authored-By or Claude-Session trailer.
- Merge: `git merge-tree --write-tree origin/main HEAD` against `origin/main` `cbd23f1c8bf6185c3a6c10f6e4aaf562417e75bf` exits 0, tree `7d02e1735c8cc535757402796cbc053bf2069e12`. Its stderr has `LEDGER-MERGE: resolved tests/structure_budgets.json` and no `MERGE-CLAIM: refused` (`ev/merge_tree.txt`). The head is behind main but merges cleanly.
- Failing test first, both ends. The finder's harness is the roster brief's oracle, run as the `tests/features.py` section `Unload lifecycle and Tibber failure semantics`. It runs alone through `tools/audit/seat/features_block.py` via `ev/block_harness.sh` (this harness is mine, not the fixer's; it executes the committed checks unmodified).
  - At the merge base, with the head's `tests/features.py` overlaid, exactly the body's three bridge checks fail: `a failed price fetch while the last prices still cover now does not fail the update`, `...and raises the price_feed_stale repair, logging a WARNING and no ERROR`, and `null control: prices that no longer cover now fail the update again, and the repair stays` on its repair half (`issues []`). The healthy-fetch, no-covering-prices and refused-token null controls pass there (`ev/block_base_with_head_tests.txt`: `3 of 11 FEATURES BLOCK FAILED`).
  - At the head: `ALL 11 FEATURES BLOCK PASSED`.
- Full `tests/features.py` at the head: `ALL 5229 FEATURE CHECKS PASSED`, rc 0, 8m59s (`ev/features_head_tail.txt`).
- Mutation proof (step 1). I reproduced the body's mutants M1-M8 exactly as named, plus five of my own, through `tools/audit/seat/mutant_run.py --spec` (copy-tree) on the block harness at the head. `SURVIVED NULL`, and M1-M8 are all KILLED (`ev/mutants_head.txt`, spec `ev/mutants_spec_block.json`). My own mutants:
  - `R1_any_prices_bridge`: any held price bridges, not a covering one. KILLED.
  - `R2_clear_when_unbridged`: the repair clears when prices run out. KILLED.
  - `R4_coverage_prev_hour`: coverage tested at now-1h. KILLED.
  - `R3_repair_no_error_placeholder` and `R5_reauth_skipped` survive the block. I re-ran them on whole scripts below.
- Full-script mutants at the head, `--in-place` in their own worktrees (`ev/mutants_full_features_head.txt`, `ev/s1_entities.txt`, spec `ev/mutants_spec_full.json`). `SURVIVED NULL` in each run.
  - `S1_reauth_call_del` (the re-indented `self._tibber_start_reauth()`) survives `tests/features.py` and `tests/ha_contract.py`, and is KILLED by `tests/entities.py`.
  - `S2_cycles_guard_off` (`if cycles > 1:` -> `if False:`) and `S3_cycles_const_swap` (`> 2`) are KILLED by `tests/features.py`. This agrees with the body's ledger pin `note_price_outage.GUARD_OFF.f52017bb` ("rc=1 failed=3").
  - `S4_no_error_placeholder` SURVIVED `tests/features.py`: see Findings.
- Diff-mode driver on the block (`mutant_run.py --diff 86953c6d99...HEAD`, `ev/diffmode_block_head.txt`): the block's survivors `coordinator.py:6969 CALL_DEL` and `issues.py:81 GUARD_OFF` / `CONST_SWAP` are S1/S2/S3 above, each killed by a whole script. No survivor remains at the head across the scripts the closure runs.
- Null controls (step 3): all four the body names pass at the head and at the base, and NULL survives every run.
- Seam census (step 6): the body's rule `grep -n "await self._fetch_[a-z_]*()" coordinator.py` returns the same three fetchers at the head and at main, in both refresh paths (`ev/cheap_checks.txt`). The diff closes `_fetch_tibber_prices`, and the body dispositions the other two. Coverage is a real step test: `_known_prices_for` breaks at the first uncovered step and returns `[]`, so `bool(covering)` is false exactly when no published row covers `plan_step_start(now)`.
- Architecture score: `score.py --diff 86953c6d99 HEAD` prints `dS +0.0000 NULL`, which reproduces the body. `score.py --diff origin/main <merged 7d02e173>` prints `dS +0.0000 NULL`. A two-dot `--diff origin/main HEAD` prints `WORSENS coord_footprint 2496->2497`, which is main's own improvement read backwards: `--diff 86953c6d99 origin/main` prints `coord_footprint 2497 -> 2496 IMPROVES` (`ev/archscore.txt`). The movement is not this diff's.
- Structure (step 14): `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. The diff only lowers budgets (`class_excess_loc` 17537->17535, `max_class_loc` 7923->7921) and re-records `recorded_at` to the merge base. `coordinator.py` numstat is +18/-20. Nothing is raised.
- Unchanged: `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files (step 5). No golden fixture moved, so step 4 has nothing to compare.
- Translations: `cmp strings.json translations/en.json` is silent. `price_feed_stale.description` carries `{error}` in de, en and sv. The three texts say the same four things: no new prices (with the error), planning continues on the last published prices covering now, the optimizer is unavailable once they run out, and the notice clears on a successful fetch.
- Carry accounting: the group's roster entry at `handoff/audit-r10-roster` `5cc85afaa7165fc15b825780437667344ef100b5` has `carry: []` and `findings: []`. The body's `## Forward-carry none` and `## Friction none` agree with it.
- Red checks: `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing`, `validate / validate-hacs`. No PR exists, so no check has run on the head, and no red is owed an answer.
- Not re-derived:
  - The scoped-gate figure (`MODE: SCOPED`, exit 0) and `PIN KILLED: 7 pinned, 0 left unpinned`. These are heavy runs I did not repeat: the gate and the mutation table are CI's to cite, and no CI exists yet. The seven pin files and the one deletion are present at the head.
  - The `README.md` line is outside the roster's file list. The body discloses it as `doc_claims.py`'s requirement. I did not re-run `doc_claims.py`.

## Findings

- Follow-up: the `price_feed_stale` repair's `{error}` placeholder is unpinned. Mutating `placeholders={"error": reason}` to `placeholders={}` in `issues.note_price_outage` (`S4_no_error_placeholder`) survives the full `tests/features.py` at `311ee9f3fa`, with NULL surviving. If it regressed, the repair would render a literal `{error}`. It is not a named mutant, and the mutation table's operators do not generate it, so `prepr.sh` step 6d did not owe it. One assertion on the raised issue's placeholders in the bridge check would pin it. Carry: dismissed: a reviewer-invented mutant outside the mutation table's operator set on display text only; it does not change the fix's behaviour or any later stage's work, and the PR owes nothing under step 1.
