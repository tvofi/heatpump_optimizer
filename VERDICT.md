Fix review: merge 46049d626b96f3c88d54cef7957d93d16d13fb79

bus-nonce: 2753317b7e52c54b02da0b96f457ad73

Reviewed head 46049d626b96f3c88d54cef7957d93d16d13fb79 (authored code head e511768ec75add5847883bebe6a1fb674f827247, origin/main 0b162da1a). Roster-only PR: no production line exists to mutate, so steps 1-5 and 14 have nothing to measure. Round 1 of this PR as far as the record shows.

## Evidence

- RESULT roles: dev/governance/roles/ is unchanged between the merge base and origin/main (empty diff), so my copy of fix-review.md is current.
- RESULT diff: `git diff --stat origin/main 46049d626b96f3c88d54cef7957d93d16d13fb79` is two files, dev/programme/rosters/wave-r10-groups.json (+4/-2) and dev/programme/delivery/2601.md (new, 1 line). The roster hunks are exactly two appended carry strings: one on R10-ORCH-MACHINERY (carry 31 to 32), one on R10-ARCH-DOCS-FIRST (carry 2 to 3). Nothing else changed (ev/diffstat.txt, ev/figures.txt).
- RESULT ece26d837 text: the appended R10-ORCH-MACHINERY carry matches the finding in the #2600 verdict (review/2600, VERDICT.md line 9) word for word apart from the "(from #2600 verdict)" suffix and dropping that line's own trailing Carry: tag.
- RESULT e511768ec text: the R10-ARCH-DOCS-FIRST carry records O-1, which the design verdict (handoff-body/design-verdict-r10-arch-docs-first, BODY.md line 3) names as decided by the orchestrator at design note 16954f0c8; tools/site/build_docs.mjs exists on main and reads docs.css (3 matches).
- RESULT figures: the body's jq prints nb 148, nh 148, removed [], new [], changed [R10-ARCH-DOCS-FIRST, R10-ORCH-MACHINERY] (ev/figures.txt). Carry counts 31 to 32 and 2 to 3 re-derived.
- RESULT null control: `git diff --exit-code 0b162da1a b93ece169 -- <roster>` rc 0, so main's roster equals the merge base and nothing main wrote is overwritten.
- RESULT brief_lint: `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` at the head prints TOTAL: 0 error(s) across 1 file(s) (ev/brief_lint.txt).
- RESULT carry_audit: the body's Forward-carry and Friction are "none", and pr-contract (which runs carry_audit over the body) is success at this head. I did not run carry_audit check myself over the body text. This verdict's Findings section holds no bullet needing a Carry: beyond the dismissal below, and every named group is live on main's roster.
- RESULT merge: `git merge-tree --write-tree origin/main 46049d626b96f3c88d54cef7957d93d16d13fb79` exits 0 with tree 87a75b3c443ad93f91447b2a7988c80eb7238039, no conflicts (ev/merge_tree.txt). The head's merge commit d411241f1 merges main 0b162da1a, which is the current main tip.
- RESULT version: VERSION, the manifest and RELEASE_NOTES.md are not in the diff.
- RESULT forward-carry: the carries are the roster ops themselves, present at the head; nothing else is owed to a later stage.
- RESULT CI (check-runs at this head): green are pr-contract, briefs, closure-scope, mutation, policy-docs, wave-script, hassfest, validate-hacs, budget-raise-gate, arch-score, graders-head-copy, CodeQL analyses. Red are `delivery-status` and `nightly-status`. delivery-status prints "NOT a required context" and lists overdue #2588, a row this diff does not touch (it adds one row and deletes none). nightly-status prints "NOT one of the required contexts" and "no scheduled run of the workflow was found", a main-wide condition; neither reads what this diff changes, so neither is this PR's. `fast (3.14)`, `closures`, `instrument-self-tests` and `env-matrix` were in_progress when I read the API; I cite CI for those and did not re-run any gate.
- RESULT paths: grep for the two forbidden absolute-path prefixes over this file and ev/ finds nothing.

## Findings

- C10 of the design verdict (the roster's files list for R10-ARCH-DOCS-FIRST lacks dev/README.md, tests/doc_claims.py, tests/layout.json, tests/closure.py and tests/closures.json for train hot-file accounting) is not settled by this PR, which can only add a carry because roster_edit has no files op; the design review already dispositioned it as the orchestrator's. Carry: dismissed: orchestrator owns roster files (design verdict item F2)
