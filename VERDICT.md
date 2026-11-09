Fix review: merge 0eeb6bdb3663b598c8421cc47ff8992d99c65b64

bus-nonce: 5652993b037d430dddbe1dc2e25c3f92

Round 1 for this pull request (no earlier verdict). Measured head 0eeb6bdb3663b598c8421cc47ff8992d99c65b64, still the PR head and `refs/pull/3367/head` at verdict time. Merge base and origin/main are both 0a8033305d7b03494eb63453e6181a13ffa55c05.

## Evidence

- Merge: `git merge-tree --write-tree origin/main 0eeb6bdb` returns rc 0 (tree 823b6240) with no conflict (ev/merge-tree.txt).
- CI: `merge_train.py classify 0eeb6bdb --pr 3367` returned rc 0 at 2026-11-09T08:12:55Z with `GREEN ... pending: none red: none` (ev/classify.txt, ev/classify-log.txt).
- Mutation proof (step 1), tests/entities.py run in full under `PYTHONPATH=tests/hastub` at the head:
  - The head returns rc 0 with `ALL 2670 ENTITY CHECKS PASSED`.
  - Mutant python 75 to 50 returns rc 1 with `1 of 2670 ENTITY CHECKS FAILED`, and the failing check is the per-leg pin (ev/entities-full.txt).
  - The body quotes 2668 checks at code head a325da38. Head 0eeb6bdb also carries main's merge (ca639739). The static `R.check(` count is 1959 at a325da38 and at its base 3fdaa9da, and 1961 at both the head and merge base 0a803330. So "check count unchanged" holds, and the 2-check difference comes from main.
- Targeted mutants (reviewer's own harness, ev/pin_harness.py). It executes the pin's lines (tests/entities.py:21856-21878) verbatim against a mutated codeql.yml copy (ev/pin-mutants.txt).
  - These mutants FAIL: python 50, actions 75, javascript-typescript 44, python timeout dropped, python `"75"` as a string, python `true`, job-level literal 75, actions leg dropped, a duplicate python leg at 45, an extra `go` leg, and the pre-change YAML (a325da38^).
  - These pass, as designed: python 51 (the floor `_PY_WORST_CASE_MIN`) and a comment-only edit.
- Steps 2 and 3, the figures and the finder's enumerator:
  - The design section 1 recipe was re-run through the GitHub Actions API by this reviewer's own subagent, not the fixer's py_jobs.py: python jobs of ci.yml push runs on main (ev/python-jobs-main.json).
  - Take the job records that had completed by 2026-11-09T04:59Z. The newest 20 are 10 cancelled at 45.07 to 45.10 min and 10 successful. Capped (≥44.9 min) is also 10. The newest started at 03:06:09Z and the window starts at 15:23:22Z. This matches the body exactly.
  - The count includes both attempts of run 42502615263: attempt 1 cancelled at 45.10, attempt 2 succeeded at 44.13. Counting by run instead gives 11 or 10, depending on which attempt is kept. The body's rule (newest 20 jobs) is the one that reproduces it.
  - Null legs over the same runs: actions max 1.05 min, javascript-typescript max 1.88 min. This agrees with the pin message's "p99 <= 2.3".
  - Five python jobs started after 04:59Z: all succeeded, at 31.5 to 42.9 min.
- Head runner-speed control, which the body leaves to the reviewer (ev/pr-python-job.txt):
  - The PR's own `codeql / Analyze (python)` job 129033673485 succeeded in 44.85 min (07:25:22 to 08:10:13).
  - Within it: tests/closure.py extracted in 3650 ms (the slow runner mode of design section 1), tests/features.py in 1293233 ms, 2002 modules in 1409.55 s, query evaluation about 19m37s.
  - So the job ran under the new 75 cap with 0.15 min to spare against the old 45. That is consistent with the projected about-51-min worst case, and the job did not need the extra time this time.
- Step 6, the class:
  - Design section 6's enumeration rule returns one site: `git grep -n timeout-minutes .github/workflows/codeql.yml` (line 125, in the diff). `_analyze_cap` names one pin (in the diff). The ci.yml `codeql:` caller only does `uses:`/`with:` and sets no cap (ev/class-enum.txt).
  - The class is one seam.
  - Nothing else reads the old `matrix.language` list. dev/audit/harnesses/r10_ci_gate_core.py b3_enumerate reads tests.yml, not codeql.yml.
  - The `Analyze (${{ matrix.language }})` context names are unchanged under an include-only matrix.
- tests/harness_headers.py, the other closure reader of codeql.yml, ran in 2m51s at the head and exited without failure output.
- Steps 4 and 5: the three-dot diff touches only codeql.yml, tests/entities.py and dev/programme/delivery/3367.md. VERSION (7.1.8), the manifest, RELEASE_NOTES.md, tests/golden, the claim files, the *budgets.json files and tests/closures.json are untouched. No fixture moved, so there is nothing to claim.
- Step 11, red checks (check-runs API, filter=all; ev/check-runs.tsv):
  - `gate` is in `merge_train.py owed-reds` (ev/owed-reds.txt). It concluded failure twice: job 129033952663 (07:26:47Z) and job 129038979256 (07:41:35Z). Both logs read `FAIL run(s) [42577397944] at this head are still being judged; their gate decides` (ev/gate-red-logs.txt). These are interim reds while ci.yml was still running, and three later `gate` runs concluded success.
  - `pr-contract / pr-contract` job 129049296038 started at 08:10:17Z, after the last red concluded, and succeeded. Under step 11 that green run is the evidence that the body's `## Red checks` answer passes.
  - `governance / delivery-status` is red and is not required (defect-root-cause.md).
- Step 10, the forward-carry: the reopen trigger is in design e64e8fdb section 5 ("any python job capped at 75, or a 7-day python p90 over 65 min") on design/r10-hotfix-codeql-headroom. Roster group R10-HOTFIX-CODEQL-HEADROOM is `in-progress` on handoff/audit-r10-roster.
- Steps 14 and 15: no budget, score, ledger, closure or golden moves. `_PY_WORST_CASE_MIN = 51` is design section 1's projection, which the body discloses as a projection, not a measurement. The change follows design section 3's shape exactly. Alternatives lost per design section 4.

## Findings

- Follow-up: the body's figure enumerator `python3 -I py_jobs.py` is a scratch script that did not land, so figure_lint reports it `unverified`. fixer.md step 18 says a figure a later seat must reproduce lands as a harness. The design's reopen trigger (any python job capped at 75, or a 7-day p90 over 65 min) needs exactly that enumeration re-run. Today it is reproducible only from the prose recipe in codeql.yml's comment and design section 1, which is how this review rebuilt it. Carry: R10-HOTFIX-CODEQL-HEADROOM

## Friction

none
