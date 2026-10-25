Fix review: merge bd1a5f31c7a25282420285197412882f4a40a162

bus-nonce: cd884c7544f7b95b7a6e667c235c7384

## Round

Round 6 of review 2753 (R10-THERMAL-POWER-OPTION). This is a delta pass after the round-5 `merge 09aecd621` verdict (verdict/2753 at `e356239d8`). The authored code head is still `1339cf925` (`handoff/r10-thermal-power-option-r4`, `-r5` and `-r6` all point at it). The head `bd1a5f31c` adds two main merges on top of `09aecd621`: the bot's `28f134f6c` (merges origin/main `de794b537`) and `bd1a5f31c` (merges origin/main `b89fea13e`). Between them the body was re-taken (r6), which routes the two `## Evidence` items of review 6393281122. I judged the resolution delta of the two merges and the body. The code was not re-audited.

## Findings

- none: the delta has no defect, surviving mutant or deferral. Carry: dismissed: no finding to carry

## Evidence

- Head: the pulls API reads `bd1a5f31c7a25282420285197412882f4a40a162` both when the review started and at 13:29Z, when the verdict was written (`ev/HEAD.txt`). The body's `## Head` names this SHA and its parents correctly, and names `28f134f6c` as the bot merge of `de794b537` into `09aecd621`.
- Role contract is current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, since the merge base is origin/main `b89fea13e`.
- Resolution delta is empty for both merges (`ev/merges.txt`):
  - `git merge-tree --write-tree 09aecd621 de794b537` gives tree `b8781a13d`, which equals the tree of `28f134f6c`.
  - `git merge-tree --write-tree 28f134f6c b89fea13e` gives tree `6165c0934`, which equals the head's tree.
  - Merging the code head `1339cf925` straight into origin/main `b89fea13e` also gives `6165c0934`.
  - The only ledger work was LEDGER-MERGE on `tests/structure_budgets.json` (`class_excess_loc` 18202 plus both deltas gives 18096; `max_class_loc` 8442 plus both gives 8336) and on `tests/closures.json` (merged as a set).
  - No MERGE-CLAIM line appears.
- Three-dot patch: against `b89fea13e` it is 36 files, +840/-106, the same as round 5. Comparing it with the round-5 three-dot patch (base `8a11b8bdd`) shows only hunk offsets and index lines, plus `tests/structure_budgets.json`. There the branch's -7 is now taken from main's newer rows: 18103 to 18096, 8343 to 8336, with `recorded_at` `ab00437c9`. Every other row matches main. This is a payment and no budget is raised. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- Merge with main: `git merge-tree --write-tree origin/main bd1a5f31c` exits 0 (origin/main is `b89fea13e`, an ancestor of the head).
- RESULT structure_head rc=0 STRUCTURE RATCHET PASSED; class_excess_loc=18096 <= 18096, max_class_loc=8336 <= 8336 (`ev/structure_head.txt`). The improvement is recorded at this head, so the round-3 ratchet-unrecorded class does not recur.
- RESULT features_head rc=0 ALL 4392 FEATURE CHECKS PASSED (`env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/features.py`, detached worktree of the head; `ev/features_head.txt`). This checks that main's newly merged code does not interact with the PR's code.
- RESULT mutant_M1 (`flow_meter.read_heat_output_kw` line 61, `if cap.measured_heat:` changed to `if False:`, `ev/mutant_M1.diff`): rc=1, `7 of 4392 FEATURE CHECKS FAILED`. These are the same 7 checks the body names; the total grew from the body's 4374 through main's merges (`ev/mutant_M1_features.txt`). The worktree was discarded.
- RESULT carry_audit: `python3 -I tools/audit/carry_audit.py check --body <live body> --comments <#2753 issue comments, 4>` printed `CARRY-AUDIT: 7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)`, rc=0 (`ev/carry_audit.txt`). This matches the body's re-take figure exactly. Items 58d790f9 and 51ece26b are dismissed in `## Red checks`, and their reasons are accurate: in review 6393281122 both bullets confirmed the body's nightly-ha claim and the RCA record and opened no defect.
- RESULT body checks at the head:
  - `node tools/policy/policy_lint.mjs --pr-body <body> --head bd1a5f31c --base b89fea13e --title ... --author hpo-author[bot]` printed `PR-BODY: 0 error(s)`, rc=0 (`ev/policy_lint_pr_body.txt`).
  - `node tools/policy/figure_lint.mjs --pr-body <body>`, run in the head's tree, printed `FIGURES: 9 resolved, 1 not verified, 0 refused`, rc=0 (`ev/figure_lint_head.txt`). The one unverified figure is a `git diff --quiet` whose flags the linter never checks.
  - The same linter run from a stale checkout refused `tests/features.py` as absent. That is an artefact of the checkout, not a defect in the body.
- Forward-carry: on origin/main `dev/programme/rosters/wave-r10-groups.json`, R10-HEAT-METER and R10-COP-GATE each hold one `From R10-THERMAL-POWER-OPTION (#2753` carry ending in `Control:` (`ev/body_checks.txt`).
- CI on this head, read from the check-runs API at 13:29:50Z (`ev/check_runs_head.txt`): 36 runs and none red. Concluded green: nightly-ha (stable) and (2025.2.0), typing, replay, arch-instrument, arch-score, budget-raise-gate, hassfest, validate-hacs, briefs, closure-scope, governance policy-docs/wave-script/delivery-status, and codeql actions and javascript. Not yet concluded at that time: fast (3.14), closures, coverage, mutation, governance/instrument-self-tests, codeql python and one prelude. pr-contract had not started. Per tvofi 2026-09-30, I cite the heavy lanes and did not re-run them. The merge train reads their conclusions at merge time.
- Figures not re-derived at this head: the harness arms, `ci_predict.py`, the `closure.py select` mode line and the archscore dS. They are quoted from the round 3/4 passes over unchanged code, as in round 5.
