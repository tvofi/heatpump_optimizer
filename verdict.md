Fix review: merge ced4bf66e91d3c61254066c310f1f9af7ea064ef

bus-nonce: ba85b07cfb7e42ec123227d996fab998

## Evidence

Round 2 of fix-review for #2628, head ced4bf66e91d3c61254066c310f1f9af7ea064ef (unmoved: refs/pull/2628/head and the PR API both give it). Round 1 was review/2628 6fc4c91ab, blocked carry-missing. Only the carry, the body, brief_lint and the head/CI were re-read; nothing else from round 1 was re-done because the head did not move.

- RESULT carry-1: 1f35f6d2 (roster_edit append-carry R10-FLOW-POSTMERGE) adds one carry to the group whose resume branch is handoff/r10-flow-postmerge (stage not-started). Wording is the round-1 finding: nudge.md step 12 shrinks to its exceptions; control "nudge.md step 12 names no beat that the post-merge tool runs". Precondition-style, control stated.
- RESULT carry-2: d0b49bc6 (R10-FLOW-AUTOTRAIN) adds one carry to the group on handoff/r10-flow-autotrain (not-started). Wording: sweep_template.md item (3) vs nudge.md step 3 (hourly pitch, --bot-prs); control "diff sweep_template.md item (3) against nudge.md step 3; no contradiction remains".
- RESULT carry-3: 5a762df2 (R10-FLOW-ARCH-PLANNER) adds one carry to the group on handoff/r10-flow-arch-planner (in-progress). Wording: nudge.md step 16 must exempt ready critical-path groups from lane cap and WIP total via pr_cap.py dispatch-gate --over-cap, and name the same route for expedite; control "no sentence in nudge.md or orchestrator.md conditions a ready critical-path dispatch on any cap".
- RESULT roster: each commit is a single append to its own group's carry field in dev/programme/rosters/wave-r10-groups.json; exactly three entries contain "6fc4c91ab" at 5a762df2, one per group above. The commits are consecutive on handoff/audit-r10-roster and 5a762df2 is its tip I fetched.
- RESULT body: the PR body's Forward-carry section names 1f35f6d2054fdf054cb91c45f8c5da997a8956f9, d0b49bc68cd571d006a5b62f3907f6a550244b4f and 5a762df2ea9c848da2fb7d806d1e38edbb8beefc, each ending in a Carry: marker for the matching group.
- RESULT brief_lint: node tools/policy/brief_lint.mjs at 5a762df2ea9c848da2fb7d806d1e38edbb8beefc exits 0 (ev/brief_lint_5a762df.txt; the ERROR lines in it are the linter's own fixtures, which end in "CARRY ok").
- RESULT merge-tree: git merge-tree --write-tree origin/main ced4bf66e91d3c61254066c310f1f9af7ea064ef exits 0 (tree 9f71d27, origin/main de69745), no conflict, no MERGE-CLAIM lines.
- RESULT diff: three-dot diff touches only dev/governance/roles/nudge.md, dev/governance/roles/orchestrator.md and dev/programme/delivery/2628.md; VERSION, manifest version and RELEASE_NOTES untouched.
- RESULT CI: check-runs at this head: all required checks concluded success (pr-contract x2, budget-raise-gate, arch-score, closures, coverage, fast (3.14), typing, browser, briefs, policy-docs, instrument-self-tests, env-matrix, wave-script, delivery-status); skipped are the autofix/ratchet lanes. The only failure is nightly-status, which grades main; the diff touches none of what it reads, so it is not this PR's and the body owes it no answer (defect-root-cause.md). The latest pr-contract run started after the last red conclusion and passed.
- Not re-run (round 1 stands, head unmoved): mutation proof, null control, figures in the body; I did not re-derive them this round.
- The mandate on #201 comment 6175172275 covering the policy approval, quoted in the body, I did not open; tvofi's approving review on the code-owned/policy paths is still owed before merge and is not mine to supply.
