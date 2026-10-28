Fix review: merge 97ac438d6be48b92b27dc4d47ba258dbbd84710d

bus-nonce: efe053c14afcd160a8e8f59cb7737e3a

Resolution-delta review of PR #2609 at 97ac438d6be48b92b27dc4d47ba258dbbd84710d (previous review: merge c00082a9a). Scope: commit 97ac438d6 only.

## Findings

- env-matrix (job 119862131576) is red at this head: `no-remote / policy_lint rc=0 -- rc=1` and `no-remote / the lane reports NOT MEASURED rather than failing -- rc=1` (14 held, 2 did not); the pr, push-main and shallow arms are ok. The body's ## Red checks does not name it at this head. The delta (two D6 claims files) cannot reach policy_lint, and the same driver at this head locally (`node tools/policy/policy_lint_envmatrix.mjs`) reports 16 held, 0 did not, rc 0, so I read it as a CI-environment arm, but I could not reproduce or root-cause it. origin/main's 47147487b env-matrix was success; main 738d950aa's was still running. The PR is already merged (merged_at 13:47:37Z, before env-matrix finished at 13:48:39Z). Carry: R10-ORCH-MACHINERY
- nightly-status also shows failure on this head in the check-runs list (completed 13:46:07Z) while it is skipped on main; not investigated. Carry: dismissed: a schedule-gate row, not reachable from the two-file delta; I did not read its log

## Evidence

1. Commit scope: `git log --no-merges c00082a9..97ac438d6be48b92b27dc4d47ba258dbbd84710d ^origin/main` lists only 97ac438d6. It touches only dev/audit/rounds/round4/D6/claims.json and claims.md (6 insertions, 6 deletions); only C108 (81 -> 84 links) and C110 (21 -> 22 images) change, in both files. ev/delta_stat.txt.
2. Re-record honest: at the head, `PYTHONPATH=tests/hastub:custom_components:tests python3.13 dev/audit/rounds/round4/D6/claims.py` ran clean and `git status --short` was empty afterwards (ev/status_after.txt). Independent count with claims.py's own regexes (README.md, DISCLAIMER.md, docs/*.md; ev/count_links.py): origin/main 47147487b 81 links, 21 images; head 84 links, 22 images. Added at the head and nothing removed: README.md -> docs/img/brand/coffee.svg (link and image), README.md -> dev/README.md, docs/architecture.md -> ../tools/audit/archscore/ABOUT.md. The three links are exactly those; the one image is the coffee button. All three lines are in the three-dot diff origin/main...head (ev/added_links_diff.txt), so none is main drift (the head's merge base is origin/main 47147487b).
3. `tests/harness_headers.py` at the head: ALL 109 HARNESS HEADER CHECKS PASSED, rc 0 (ev/harness_headers.txt).
4. Body: ## Head names 97ac438d6be48b92b27dc4d47ba258dbbd84710d; ## Red checks names fast (3.14) check-run 119826108493 with cause (C108/C110 counts), cheaper detector (harness_headers.py before push) and Carry R10-PREPR-UNPINNED-RED. `carry_audit.py check --body` on the live body: 16 finding items, 16 routed, 0 unrouted, 0 bad destination (ev/carry_audit.txt; roster read from the head checkout, not re-run against the newer origin/main). Check-runs at this head (ev/head_checks.txt): pr-contract success (two runs); fast (3.14), coverage, closures, instrument-self-tests, arch-score, Analyze (python) were still in_progress when read, which is not a block; env-matrix and nightly-status failed (see Findings); CodeQL neutral.
5. `git merge-tree --write-tree origin/main 97ac438d6be48b92b27dc4d47ba258dbbd84710d` exits 0 (clean; origin/main 47147487b is the merge base) (ev/merge_tree.txt). ev/HEAD.txt holds the full head. No machine-local absolute path of the orchestrator appears in this file or ev/ (grepped).
6. PR state: the PR reads merged by tvofi at 2026-10-22T13:47:37Z, so this verdict is retrospective.
7. Toolchain: the PATH python3 here is 3.11 without voluptuous/aiohttp/homeassistant stubs deps; I ran with /usr/bin/python3.13 after pip-installing voluptuous, scipy, aiohttp, pyyaml (environment only, nothing in the repository changed).
