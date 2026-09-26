# Round-9 RCA seat brief (common part)

tvofi (2026-09-26T17:44Z): run the RCA seats now, before fixing starts, and fold any cost-effective
countermeasure into the fix plan. You are one RCA seat for the class(es) named in your prompt.

## First
Read /home/claude/heatpump_optimizer/CLAUDE.md, every file in .claude/rules/, and
tools/audit/briefs/root-cause.md (your contract), and follow them. defect-root-cause.md is the policy
you execute. Never call the owner "Tim"; call them "tvofi".

## Hard limits
- You do not open PRs, comment on GitHub, file issues or run gh. Your only push is your own
  handoff branch.
- Do not change policy files. Draft any policy change as a proposal only: CLAUDE.md, .claude/rules,
  tools/audit/briefs, and anything else CLAUDE.md lists as policy.
- No heavy D3 mutation re-runs (tvofi). A detector you propose is demonstrated with one in-memory
  mutant or a revert of the fix, not with a mutation pool.
- Budgets: if a countermeasure needs a *_budgets.json raise, do not raise it. Say so; that is
  tvofi's decision.
- Shared folder /mnt/project-files is shared by many sessions. Re-read a file before changing it,
  keep edits small, write only under /mnt/project-files/audit-r9/rca/<your-slug>/.

## Inputs
- Class and findings: /mnt/project-files/audit-r9/judge/{JUDGE.json,CLASSES-DRAFT.json,JUDGE.md}
- Sweep: /mnt/project-files/audit-r9/sweep/S*.json and the class's SWEEP*.md files. These hold the
  enumerator, the instances and any barrier proposal. Start from the proposal; do not accept it
  unexamined.
- Issue draft: /mnt/project-files/audit-r9/issues/<slug>.md
- Fix plan: /mnt/project-files/audit-r9/fix/FIX-PLAN.md, the F<n>.md lane briefs and
  wave-r9-groups.json. Your prompt names the PR your RCA starts beside and the PR your barrier lands in.
- Baseline 1936d5ca (v6.7.1); current main: origin/main. The escape record is RELEASE_NOTES.md plus
  closed bug issues. The historical class frequency is in the D14 ledger (tools/audit/**/bugclasses*
  or ledger files; find them).

## Deliverable (all four, or you are not finished)
1. **Cause**, reproduced by you at 1936d5ca, with the class search: what else the same cause reaches
   beyond the sweep.
2. **Process state (a)-(d)**, with quoted evidence.
3. **Cost test** with numbers: standing wall-clock cost of the countermeasure against defect cost
   times measured P(recurrence).
4. **The class-eliminating barrier**, which an audit class with N>=3 owes. The cost test picks its
   form. If none fits within the bound, say so plainly and it goes to tvofi. If it is a
   check, test, lane or hook:
   - prototype it on branch handoff/r9-rca-<slug>, cut from origin/main;
   - show it FAILING on the defect (at baseline or with the fix reverted) and PASSING once fixed;
   - null-control it: it does not fire on a healthy tree and does not go green by skipping;
   - give its standing seconds per run, and keep it inside the structural ratchet.
   The prototype is for the barrier PR's fixer to carry. It is not a PR.

Write /mnt/project-files/audit-r9/rca/<slug>/RCA.md: the "Root cause" section for the class issue,
plus a "Plan fold" section. The Plan fold says:
- which fix-plan PR the barrier should land in, if it differs from the plan;
- its files, and whether they are code-owned or policy;
- its estimated production and test lines;
- any change to the plan's PR set or `after` edges.

Commit on your branch with message trailers:
Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WgT4h2uvK9kbxQbWc5MJis
Push with `git push origin HEAD:handoff/r9-rca-<slug>` and read it back with `git ls-remote`.

## Report back (under 250 words)
- state (a)-(d);
- cost-test verdict with numbers;
- barrier form, and its fail/pass/null evidence;
- landing PR and line estimate;
- anything needing tvofi;
- branch@commit.
Never assert a number you did not measure.
