Fix review: merge b9f201f90efbb39422319426a7839c036b7b46af

bus-nonce: a416c1d2ac33b0756416101ff620add4

Round 3, cloud reviewer seat. I measured head b9f201f90efbb39422319426a7839c036b7b46af (ev/HEAD). Before this file was written, `ls-remote` showed that SHA was still the tip of `fix/r10-recarry-head-pr`. Contract: fix-review.md at main. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract is current.

Round 1 blocked this head as carry-missing, and round 2 blocked it as body-head-unnamed. The tree has not moved since either verdict. What changed is the body, edited at 08:40:42Z. Both earlier blocks are now cleared. The code checks below were taken again at this head.

## Earlier blocks, now cleared
- RESULT body lint: `policy_lint.mjs --pr-body <live body> --head b9f201f9` gives `PR-BODY: 0 error(s)`, rc=0 (ev/pr_body_lint.txt).
- RESULT carry_audit: `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (ev/carry_audit.txt).
- RESULT pr-contract: run 117968812952 started 08:44:39Z, after the body edit and after the last red concluded (08:36:33Z). It is `success`, and its log prints `PR-BODY: 0 error(s)` and `CARRY-AUDIT ... 0 unrouted` (ev/logs/117968812952.txt).
- Step 7 carry: `## Head` names b9f201f9 and carries the figures from bef08da49. `git diff --stat bef08da4 b9f201f9 --` over the seven fix paths is empty (rc 0), so the carry holds.
- Step 9: the body now says r10_recarry_head.py and the app_push arms are the fixer's own instruments and that no finder harness was committed. This closes round 1's note.

## Code (taken again at this head)
- RESULT self-tests (ev/head_figures.txt):
  - `app_push self-test: 135 checks, 0 failed`
  - `head_note self-test: 6 checks, 0 failed`
- RESULT fixer harness: `writers: 6`, and every row reads `plain=named quoted=named fenced=named crlf=named`. This matches the body.
- RESULT mutants on head_note.py (ev/mutants.txt). Columns are app_push / head_note / harness rows with `unnamed`:
  - M1, substring predicate: 4 failed / 5 failed / 6 rows.
  - M2, fence tracking off: 1 failed / 1 failed / 6 rows.
  - M3, return pos: 4 failed / 5 failed / 6 rows.
  - All three match the body.
  - M6 is my own mutant: the title check becomes True, so any `##` heading counts. It gives 1 failed / 1 failed and is caught by both self-tests.
- RESULT finder-shape measurement, built by me (ev/finder/shape.py). No finder harness is committed for this group.
  - Input: this PR's own live body, which quotes "`## Head` note" above its heading (the #2400 shape), with `## Head` stubbed to bef08da49. One recarry to b9f201f9 is applied, and pr-contract's reader judges the result.
  - Main's app_push locator: `unnamed`. The note lands at line 3, in the prose.
  - head_note.prefix: `named`. The note lands at line 25, under the heading.
  - Null control: the stub read at bef08da49 is `named`.
- RESULT class (ev/class_grep.txt), using the body's rule:
  - Base gives 7 locators: app_push.sh:344, open_pr.sh 39 and 52, update_pr.sh:53, handoff_push.sh 69, 89 and 105.
  - Head gives 2 lines, both inside head_note.py, and neither one locates the heading (one is a docstring, one is a self-test split).
  - No seam is left open.

## Merge, untouched files, CI
- RESULT merge: `git merge-tree --write-tree origin/main(c3530277) b9f201f9` gives rc=0 with tree cb670a9e (ev/merge_tree.txt). origin/main is unchanged at c3530277.
- RESULT untouched: VERSION, the manifest, RELEASE_NOTES.md, tests/golden and `*budgets.json` have an empty three-dot diff (ev/untouched.txt).
- RESULT cheap checks (ev/cheap_checks.txt):
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out`
  - `STRUCTURE RATCHET PASSED`
  - tmp_paths `0 refused`
- RESULT CI on the head (check-runs API, ev/checkruns.tsv): 53 runs, all completed. 35 success, 15 skipped, 3 failure.
  - The reruns of arch-score, validate-hacs and env-matrix are success, as are closures (08:44Z) and all three Analyze runs.
  - pr-contract 117965336923 and 117965510493 are red. Both ran before the body edit, on the old body: they say `## Head` does not name b9f201f, and that three reds are unnamed. The later run on the edited body is green.
  - nightly-status 117951876334 is red: `HTTP 403 rate limit exhausted`. It is not required, its own rule says it is not this PR's, and the body names it under `## Red checks`.
  - Step 11 is answered.

## Not re-derived
- ci_predict's `768bfc0c341d` line.
- harness_headers.py, which the body does not claim; CI was green.
- env_drift.py --all. No golden or claim file is touched.
- agreement.mjs. Round 1 took it at this tree, and it has not moved.

## Note
head_note.py takes the first real `## Head` heading. policy_lint's `sections()` keeps the last one. The two differ only on a body with two real Head headings. Carry: dismissed: no writer emits two Head headings (as round 1 found).
