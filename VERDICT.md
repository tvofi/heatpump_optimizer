Fix review: blocked 40b41179ec911af78d1c60a3b4b7ef51849564cd root-cause-unanswered: fast (3.14) went red, unanswered: the main merge 5b660cd92 brought in #1846, which took DISCLAIMER.md out of INERT, so both new entities.py checks fail at the head (2 of 2065)

bus-nonce: 4910b135f3923ed61f703b81e163cbfd

Round 1. I reviewed from a detached worktree at 40b41179e, with merge-base 5f87e25a1. `tools/audit/briefs/` is unchanged between the merge-base and origin/main. Head re-read at posting time: still 40b41179e. The merge 5b660cd92 has the same tree as `git merge-tree 4fe5c0374 5f87e25a1` (25d9de0cd), so it carries no hand resolution. 40b41179e adds only docs/delivery/1857.md. VERSION, the manifest and the notes are untouched, and no `*_budgets.json` changed.

Evidence: evidence-40b41179ec911af78d1c60a3b4b7ef51849564cd/. `real.py` and `all.sh` are my own harness, not the fixer's. They take each run's real `closure-recordings` artifact, the real `tests/closures.json` at that run's head, the real pinned `closure.py` at that run's `PINNED` base (read from the autofix log), with and without this PR's closure.py hunk applied, and a check.txt I extracted from the run's own closures log.

## The blocker

- RESULT entities_head=2/2065 failed. Both failures are the PR's own checks: "a pinned classifier ... reddens (#1846)" and "and stays quiet ... (a46a91c null control)". Every case returns `('changed', False)`. CI agrees: `fast (3.14)` failed, job 110935386372, `2 of 2065 ENTITY CHECKS FAILED`, `>>> FAILED: python3 tests/entities.py`.
- Cause: the fixture depends on `_closure.is_inert("DISCLAIMER.md")`. #1846 merged to main at the merge-base 5f87e25a1 and added `DISCLAIMER.md` and `docs/index.html` to `INERT_EXCEPT`. At the head, the committed pair `{harness_headers.py: [it, DISCLAIMER.md]}` is therefore no INERT violation. `check` goes on to a real UNDER-SCOPED (tests/harness.py), `merge` succeeds and the status is `changed`. The body's measurements were all taken at 4fe5c0374, before that merge, and were not re-taken after it ("ALL 2063 ENTITY CHECKS PASSED" there; the head has 2065).
- `## Red checks` says "none so far". `pr-contract` is also red now (run 110945652795).
- Repair: the fixture must not depend on the live INERT list, because main moves it. Pin INERT for the case (for example, patch `_closure.INERT`/`is_inert` inside `_af_case`), or use a file that is INERT by construction. Then re-run steps 2-8 at the new head. The same drift means the real-log demonstration can no longer be reproduced against the head tree's INERT list. It has to run against the run's own pinned base, as below.

## Items 1-8

1. **tests.yml.** The check step sets `set -o pipefail` and tees `python -u ... 2>&1` to `$RUNNER_TEMP/closures/check.txt` on both arms (lines 1492/1494/1496). The upload step's `if: always() && pull_request && !DOCS_ONLY_FAST` and `path: ${{ runner.temp }}/closures` carry it on a failed step. `check`, `merge` and `apply` read only `*.json` in that directory, so check.txt is inert to them. Confirmed.
2. **New status.** It is returned only on the `rc != 0` path, when the job's own output has no "UNDER-SCOPED" and check.txt has a line starting `UNDER-SCOPED: `. It is not in `AUTOFIX_QUIET["closures-autofix"]`, and it has a remedy entry. `check_txt` is bound before `in_dir` can move to `present-in-this-tree`. Confirmed by reading. Not covered (non-blocking, and the body dispositions `skip-clean`): a base `check` that returns 0 while the PR's printed UNDER-SCOPED stays green. That needs a PR that changes the comparison itself (`_fold`, `DRIVEN_BY_OTHERS`, `SLOW_GATED`).
3. **Null controls.** On the real artifacts (below), the a46a91c8 and ddaf6bf7 runs stay `skip-not-under-scoped` with the patch. Every run with no check.txt stays `skip-not-under-scoped`.
4. **Real logs.** I re-took these with the real recordings, not a synthetic pair. My extracted check.txt for e42b and a46a is byte-identical to the fixer's.
   - RESULT unpatched_pinned_matches_ci=5/5: every run printed `skip-not-under-scoped`, the status CI's autofix log printed.
   - RESULT patched_defects_red=3/3: 3a28a3ea, e42b1cdd and 9bc802e6 all gave `skip-classifier-disagrees`, closures.json unchanged.
   - RESULT patched_nulls_quiet=2/2: ddaf6bf7 and a46a91c8.
   - RESULT patched_no_checktxt_quiet=5/5.
   - The RCA tables at 6d4a51b3e give 22 autofix runs and 15 with US>0. I re-derived both counts from `rca/p2.tsv`, but did not re-take the GitHub API scan behind them.
5. **Wiring mutant.**
   - Removing pipefail from line 1492 alone reddens the tee check (3 failures).
   - The decoy, removing the other two `set -o pipefail` lines (835, 954), leaves it green. So the check is specific to this step.
   - Dropping the scoped arm's tee reddens it.
   - Two survivors: `# set -o pipefail` (commented out) and `set -o pipefail` moved after `fi` both stay green. The check is a substring test, not a placement test. This is non-blocking, but worth tightening while the fixture is redone.
   - M1 (guard deleted), M3 (status made quiet) and M8 (`"UNDER" in l`) cannot be judged at this head, because their target checks already fail. I re-run them at the next head.
6. **ci-autofix.md.** 92/96 lines and 1428/1428 tokens, cap unchanged. `policy_lint` 0 errors, `RULES-SYNC ok`. The removed prose is history (#523's "used to fall through") or a rewording ("declined to classify", the `linecache`). No obligation was dropped. Two were added: the new red status, and that the classifier is base-pinned. Policy, so tvofi's approval is owed and the body says so.
7. **Bootstrap.** True. `closures-autofix` checks out `tests/closure.py` at `pull_request.base.sha` (PINNED), so the new branch cannot run on this PR. The tee runs from the PR's own tests.yml. The body says this. At this head, `closures` passed and `closures-autofix` was skipped.
8. **CI.** waitci: DONE, total=33. NOTGREEN: `fast (3.14)` failure, and `pr-contract` cancelled then failure (110945652795). Everything else is green or skipped.

Not run: the full gate and the mutation table (I cite CI: `mutation` success). numpy/scipy came from a pip `--target` of CI's pins on 3.14 macOS. The a3/a4 sub-FAIL lines in entities.py's output are fixture lines inside passing checks, and they also appear at the head baseline.
