CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-policy-fixer-md, at head 50af6174f53c0f9bec3f705c3a4bb99615f71acc. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch 50af6174f53c0f9bec3f705c3a4bb99615f71acc for the base you were given.
Output: push the code to refs/heads/handoff/r10-policy-fixer-md, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-policy-fixer-md <body.md>`, which pushes refs/heads/handoff-body/r10-policy-fixer-md; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
# Fixer brief O10-policy-fixer-md: dispose recurring friction #2378 (finding sweep L20, F-POL, P16, P23, P38). POLICY: tvofi approves at merge (mandate 6175172275); canon is dev/governance/roles/fixer.md and fix-review.md (.claude/rules, .cursor/rules regenerate); files sit at zero headroom, so every added line is paid by cutting text.
Issue #2378 [policy] recurring friction: tools/audit/briefs/fixer.md (8 PRs in the window) is open with no roster group. Each line below is a Friction entry from a merged or open round-10 PR. Read them in the PR bodies; decide per line: wording fix, or a countermeasure in code, or refute with the count (the issue says a disposition names which of the two it changes).
1. #2305: fixer.md step 2 offers "pinned by mutation-autofix" for an unpinned site; the CI mutation lane leaves out tools/, so for an instrument file that pins nothing. Reword: "pinned by mutation-autofix" only for custom_components/; tools/ needs an in-tree mutant harness.
2. #2316 (fix-review.md step 6): the grammar names a seam, but a predicate's DOMAIN is the seam in some blocks; and the seat brief names handoff_push.sh as the push instrument while the PR update is the orchestrator's (contradiction: seats push refs only).
3. #2344: step 3 says re-execute the finding's harness, but a fix review's harness lives only in verdict evidence; step 18 says a rerunnable harness lands in dev/audit/harnesses/. Say whether a reviewer's one-shot driver belongs in the tree (reviewer answer: no; step 18 binds what a later seat reruns).
4. #2374: step 18 (harness in dev/audit/harnesses/) contradicts tests/harness_headers.py reading that directory (a new file is a predicted closures red only a Linux recording clears). #2376 (ci_predict --apply-inert) repairs the red; state that in step 18.
5. #2345: three review rounds each found a written spelling; the spelling-row design is the step-17 shape (#1874). Add the lesson to step 17 only if a line is free.
6. #2365: a fold that deletes a seam by name breaks every finder harness that drives that name (the shape slot floor harness; catchup arch-b/v2_s3.py imports the folded tariff._plateau_aware_day_max): say the finder's before/after reading exists only for the count arm, and who repairs a stale harness.
7. #2366: "every field of a commit a clone publishes" (content, path names, modes, messages, identities) is the enumeration a mutation list lacked.
8. #2368: a held branch cut from an older base carries stale copies of files its sibling changed; a re-applied delta must be diffed line by line against the sibling head (see the move-PR silent revert).
9. #2373: red-team attempts re-spelled their own counter's rule; require attempts on the rule's neighbours.
10. #2347: max_class_loc prices a docstring line like code on a hot class at zero headroom (structure.py rule, not policy; note only if a fix is out of reach).
11. The RCA for #2331 also refused a step-8 alignment (its section 6): decide it here.
Failing test first where a check can read the wording (check-wave-script.mjs reads contract examples; add an arm only if one line can be pinned). Ordering: after O10-rca-friction-2331-2353 (same dir, fix-review.md) and after R10-BRIEFS-FOLD's edits to fixer.md and fix-review.md are merged or in the same PR; do not run in parallel with BRIEFS-FOLD. Identity: refs only (handoff/r10-policy-fixer-md). Part of #201; Closes #2378 only if every line has a disposition.
CARRY to O10-policy-fixer-md (policy seat; tvofi approves at merge). From O11, carry-forward enforcement.

The round-10 sweep's three findings O11's checks do not catch (L14, L15, L16) were written only in the
orchestrator's own ledger (the orchestrator ledger), as free prose ("!" lines and one "LESSON:").
finding-propagation.md's Carry: convention binds a ledger finding as well: a ledger line recording
a finding carries Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason> like a body or verdict item.

O11 could not state this in finding-propagation.md: the file sits at its cap after O11's own text
(100/101 lines, 1335/1336 tokens; node tools/policy/policy_lint.mjs --budgets). Proposed sentence,
to go in the Enforcement section, paid for by a cut elsewhere in the same file or put in
dev/governance/roles/orchestrator.md:

  The same marker ends a finding the orchestrator records in its ledger; the ledger is out of
  tree, so nothing reads it but the next session.

Control: O11 built and dropped a ledger mode (LESSON/OWED/FINDING lines with no Carry:). Over
the orchestrator ledger it printed 31 lines and caught only L16 (l107); the rest were work-queue lines ("REVIEWERS
OWED", "PR OWED"). A mechanical check therefore needs the marker first, then a key on it.
