Fix review: merge 0662d20c57d24742da549682641da687477557ab

bus-nonce: 090182c644a59de1f240fecfc6e150c3

Round 1. Measured at head 0662d20c57d24742da549682641da687477557ab (re-read via the PR API and ls-remote refs/pull/2637/head: unchanged). Role file current (no diff to dev/governance/roles/ since the merge base).

RESULT ops: all 8 land as stated. R10-UX-HEALTH +1 carry (9a4953627), R10-PARAMS-OWNER +2 (c3711a1f0, 75c891e28), R10-FLY-RELAY-REVIEW-FF +1 P-C carry (600635c16), new R10-FLY-SUITE-ENV-FLAKES, new R10-FLY-NO-FOOTERS (in-progress, pr 2636), R10-BRIEFS-FOLD done at b24cfe517 (#2631), R10-NIGHTLY-ABSENT-NEW done at e364a0d73 (#2627).
RESULT counts: groups 165 -> 167, new 2, changed 5, removed 0 (the body's jq, re-run: ev/counts.txt). Stages main -> head: done 86 -> 88, in-progress 13 -> 12, not-started 59 -> 60, queued 6, absorbed 1 (ev/stages.txt). All match the body.
RESULT done-stages: both merge commits are ancestors of origin/main (ev/anc.txt) and are the merges of #2631 and #2627.
RESULT carries: the three R10-SCORES carries equal the text of handoff-body/r10-scores@8f564875 BODY.md verbatim, after the "From R10-SCORES ... Forward-carry:" prefix (ev/r10-scores-BODY.md). No host paths or Claude text in the added lines (ev/privacy_grep.txt: only hits are the .claude/settings.json file name and the NO-FOOTERS brief's own wording).
RESULT lint: brief_lint TOTAL: 0 error(s); ref_privacy --check 0 refused (ev/).
RESULT null-control: roster on main == merge base (git diff --exit-code rc 0, ev/null_control.txt); no group removed, so nothing main wrote is overwritten. Merge-base claim holds: 8 commits, none a merge.
RESULT merge: git merge-tree --write-tree origin/main head exits 0 (ev/merge_tree.txt). VERSION, manifest and notes untouched.
RESULT ci: check-runs at head: no failure; pr-contract, delivery-status, briefs, nightly-status, budget-raise-gate, arch-score, policy-docs, mutation green; fast (3.14), closures, env-matrix, instrument-self-tests were still in progress when read, none red. No red check owes an answer.
RESULT carry-rule: body Forward-carry none is right; this PR is the carry (roster edit). Mutation proof n/a (roster data only).

Limits, stated: (1) the Batch 4 P-C carry text is not quoted in the PR body, and the triage source is not in this checkout, so I could not diff it verbatim; I checked it is coherent, host-path free and consistent with the body's description. (2) brief_lint does not catch a planted host path or unknown group name in a carry (planted control passed with 0 errors, ev/null_control_lint.txt), so "no host paths" rests on my grep and ref_privacy, not lint; an instrument gap, not this PR's. (3) The two new groups' briefs and carries (SUITE-ENV-FLAKES from the #2632 review, NO-FOOTERS from the owner ruling) were read for sense only; their sources are not in this checkout.
