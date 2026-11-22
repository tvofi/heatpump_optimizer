Fix review: merge 17ecc009eda59ac715b148a70fc541b7c1b0a593

bus-nonce: fb79bd5c756a8d589b200d5da3cafee4
pending-ci: gate

Round 2 of #3847. The round-1 verdict `a5dea9b9c2` blocked `46e7faa93f` with `mutation-vacuous` (M7). `review_carry.py a5dea9b9c2 17ecc009ed` prints `FRESH-REVIEW`, so this round reviews the delta (fix-review.md step 12). `git diff 46e7faa93f 17ecc009ed` touches only `tools/ci/prelude.py`'s self-test (+5/-3): the CI-2 positive arm and the five null arms now read `machinery_rowblind`. The delta has no production line and no `custom_components/` path, so the review is not widened.

## Findings

- Residual: the body's extra mutant (`machinery_rowblind` drops its `scoped != "pull_request"` guard) survives at this head: `prelude self-test: 89 checks, 0 failed` (`ev/prelude_mutants.txt`, mutant G). The same guard-drop at the merge base `40e513eea4`, where the guard read `ev`, also survives: `82 checks, 0 failed` (`ev/base_guard_mutant.txt`). The gap is in the guard's domain that predates this PR. This PR changes only the guard's event variable, and reverting that change (M7) is killed. The body records it with the same dismissal. Carry: dismissed: pre-existing at base 40e513eea4 (the guard-drop survives there too); not a behaviour this PR changes

## Evidence

- Head reviewed: `17ecc009eda59ac715b148a70fc541b7c1b0a593` (`ev/HEAD.txt`). This is the PR's live head, and the body's `## Head` names it. Merge base: `40e513eea4ca3dacad882b7a1a1366b6b188f777`. `git diff <merge-base>...origin/main -- dev/governance/roles/` prints 0 lines, so the role contract is current (`ev/head_checks.txt`).
- Merges with main: `git merge-tree --write-tree origin/main 17ecc009ed` (origin/main `baa9a467ac`) prints `4bf85f9b386846f8b113efeefa2fea20da1afc35` and exits 0.
- VERSION, the manifest version, RELEASE_NOTES.md and both claim files are untouched: a three-dot diff over them prints 0 lines.
- Prior finding resolved: M7 (`machinery_rowblind` reads `ev`) is now KILLED by `CI-2: a verified PR dispatch of a doc-only diff skips every leg, idles machinery, scopes self-tests`, which got `'true'` for rowblind. The driver is `ev/mut_driver.py` and the output is `ev/prelude_mutants.txt`.
  - rowblind always `"true"` is killed by the CI-2 positive arm, `C7a` and `C7a-row`.
  - rowblind always `"false"` is killed by the CI-2 null arms and `C7a-row`.
- Re-run at this head and still killed: M1 (`scoped` never `pull_request`), M2 (`if got`), M3 (`and not why` dropped), M4 (the batch exclusion dropped), M6 (`machinery` reads `ev`), M8 (`legs` read `ev`), M9 (`dispatch_diff` always None) and M11 (`base_sha` not replaced). The unmutated file prints `prelude self-test: 89 checks, 0 failed`, which matches the body.
- Class enumeration, step 6:
  - CI-1's set is every `gh workflow run ci.yml` site paired with a token push. In `.github/` that is merge-main.yml (one site) and the three tests.yml autofix jobs (lines 2642, 2899 and 3187), which matches the four the body names.
  - The other dispatcher of `ci.yml`, `tools/ci/sweep.py:236`, re-judges stale pins. It does not follow a bot push, so it is outside the set.
  - CI-17's rule is every `setup-python` in a job that pip-installs a `tests/requirements-*.txt`. Enumerated over every workflow and composite action, it gives 15 steps with `cache: pip` and 0 pip-installing jobs without the cache (`ev/ci17_enumeration.txt`), which matches the body's 15.
- Figures re-derived at this head (`ev/figures.txt`):
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
  - `python3 tests/comment_ratchet.py --base origin/main` prints `comment_ratchet: OK`, with long_units 2301 -> 2301.
  - The body's `ALL 2740 ENTITY CHECKS PASSED` was not re-run here. The delta does not reach `tests/entities.py`, so this cites CI's `tests / fast (3.14)` at this head instead: success at 17:27:35Z.
- Finder's harness: the body names the study's job-minute census, which only a merged workflow can move. As in round 1, its tree companion is the prelude's CI-2 arms, re-run above.
- CI at this head:
  - The live check runs read success on every required lane except `tests / closures` and `tests / arch-instrument`, still in progress at 17:29Z.
  - `governance / instrument-self-tests` concluded success, which clears the packet's `introduced-red: unreadable` refusal.
  - The `gate` run 137282290108 that concluded failure at 16:59Z ran before the lanes concluded. `merge_train.py classify` reads `WAIT ... pending: gate red: none`, and classify decides.
- Red history: `tests / fast (3.14)` at `547a71778069` is in the `owed-reds` set, and the body's `## Red checks` answers it, naming `tests/comment_ratchet.py` as the cheaper detector. No other red is owed.
- CI wait: `merge_train.py classify 17ecc009ed --pr 3847` was polled from 16:59Z to 17:37Z, every 75 s, and read WAIT throughout. The last line is `WAIT 17ecc009eda59ac715b148a70fc541b7c1b0a593 pending: gate red: none` (`ev/classify.log`). The verdict is returned with `pending-ci: gate`, for the relay to post only at GREEN.
- Prepr was not re-run, as the dispatch says.
