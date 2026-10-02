Fix review: blocked 5aaef98eff8cc67bebfa95942bd682c8e5828908 barrier-lost: the only in-tree rule that CI must be green at a head containing current main is deleted, with no replacement

PR #1818, R9-PROC-1. Measured code head 5aaef98eff8cc67bebfa95942bd682c8e5828908 (merge base 90335cbd); transport head 1be2ac33 (BODY.md). CI on the head was still running at review time and is cited, not re-run.

## Blocking

fix-review.md step 11 at 90335cbd said: "The merge seat merges only on CI green at a head containing current main; if main moved, it merges main and waits." The diff deletes it (diff_fix-review.patch). A grep across CLAUDE.md, AGENTS.md, .claude/rules, .claude/skills, tools/audit/briefs, tools/audit/README.md, docs/HANDOVER.md and .claude/workflows/*.md finds it at the base and nowhere at the head (grep_ci_at_current_main_base_90335cbd.txt, grep_ci_at_current_main_head_5aaef98e.txt). GitHub does not enforce it: strict_required_status_checks_policy is false (strict_policy_off.txt, decision 0008).

The body says the sentence is "replaced by step 12's carry and resolution delta". That is wrong. The carry decides whether a verdict survives a main merge. It does not require a main merge to happen. orchestrator.md section 7 now orders a merge only for a conflict. So a non-conflicting PR verdicted on a stale base can merge on CI green at that stale base. That is the #1589/#1592 semantic-conflict class, where main went red on the combination. Process-review item 2 (the merge queue plus a disjoint-closure fast path) is what relaxes this barrier, and it carries its own replacement. PROC-1's scope (items 1, 4, the brief half of 6, 8 and 10) does not include it.

Fix: restore the rule in orchestrator.md section 11, for example "CI green at a head containing current origin/main (decision 0008 leaves GitHub's up-to-date rule off): if main moved, merge it in (which carries or goes to the same reviewer as its resolution delta) and wait for CI." Pay for it with prose another file carries. Item 2's PR may relax it later.

## Checked and sound

- The carry (orchestrator.md section 11, fix-review.md step 12) cannot carry a change to the PR's own behaviour. app_approve.sh carry() admits only git's automatic merges from main and ci: commits that touch merge-driver files only, and it requires the branch's own diff to compare equal. The new clauses send any same-file auto-merge and any claim-file difference from origin/main to the reviewer. Cross-file interactions with main are CI's to catch, which is why the blocking rule above matters.
- Retiring local --pin-killed loses no barrier. The mutation job still refuses unpinned sites. mutation-autofix pins killed ones, and its ci: commit to tests/mutation_budgets.json (a merge-driver file) carries. Survivors stay red until the body gives a value check or a triage. `mutation_table.py --scope changed` exists (tests/mutation_table.py:2016). ci-autofix.md's red-autofix fallback stays.
- Retiring "never merge main into handoff branches" was never in the tree. fixer.md step 6, orchestrator.md section 7 and fix-review.md step 12 now agree (merge, never re-cut; the same reviewer judges the delta), and steward S2 agrees.
- Paid-for cuts each have a surviving copy as the body says (spot-checked: CLAUDE.md rule 2 "Pay for the lines"; ci-autofix pin line).
- Cheap checks at the head: policy_lint `TOTAL: 0 error(s) across 40 policy file(s)`; policy_lint --budgets rc 0 (role policy ~9727 within cap 9414 + band 500); brief_lint ok.

## Non-blocking (ride the next push if it touches the file)

- The web-fragments.md merge seat still requires a "Fix review:" comment post-dating the head, which a carry never produces, and it polls main every three minutes. The runner is unused, as the body says.
- The claim-file clause means a branch that claims drift can never carry. That is conservative and costs a reviewer turn, not a barrier.
