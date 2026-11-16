Second pass of roster group R10-NUDGE-RETIRE, after #3566 retired `dev/governance/roles/nudge.md`. It builds the group's carry 1 (moved onto this group by the round-10 round-end triage, `dev/programme/triage/r10-round-end.md#P764`): `tools/policy/policy_lint.mjs`'s `checkOrphanCaps` now reads both per-file tables of `dev/governance/config/policy_budgets.json`, `files` and `files_tokens`, and the `files_tokens` caps it then reports are deleted. A file deleted with its line cap but not its token cap left the token cap measuring nothing, and only the line table was checked for that. The extended check reports two such caps on `origin/main`, both for files no longer in the tree: the retired orchestrator turn's (`tools/audit/briefs/nudge.md`, the pre-move spelling the budget file keys on; deleted by #3566) and `tools/audit/harnesses/README.md` (deleted by 72826387ff, which dropped its `files` cap only). Both are removed. No measured aggregate moves, because neither file is measured.

Whose obligations change: none. A seat that deletes a policy file must now drop its `files_tokens` cap with its `files` cap, which `policy_lint.mjs` refuses otherwise. That was already the intent of the orphan-cap check, whose message says "delete the cap".

Overlap: round-11 roster group R11-POLICY-TOKEN-CAP, on the roster handoff branch `handoff/audit-r10-roster` and not on main, has this same carry as its brief, and its two `files` are this diff. Once this merges, it has nothing left to build. That roster is not in the tree, so `## Forward-carry` cannot route to it, and its retirement is the orchestrator's roster edit.

Carries 2 and 3 (the superseding pair, items a7c09d95) ask for `python3 -I tools/ci/selftest_scope.py prune --step ID --drop files:PATH` on each step whose read of the retired path is recorded in `tools/ci/selftest_closures.json`. No step records that read at this head (Figures, row 5), so no prune is owed and none is run.

## Head

`18eba6b3975754902eec6041788a1b71410d6a9a`, measured on `origin/main` 367c3b9cac at 2026-11-16T14:02Z.

## Mutation proof

The fix's predicate is the table list in `checkOrphanCaps`. Mutating `['files', 'files_tokens'].flatMap` to `['files'].flatMap` and running `node tools/policy/policy_lint.mjs` exits 1 with `FIXTURE VACUOUS: checkOrphanCaps did not report docs/a-file-no-glob-matches.md's files_tokens cap exactly once (got [])`. Restored, it exits 0. The same refusal fires on the unfixed check with the new acceptance pin in place (the failing-test-first run, before the fix was written). The diff adds no `.py` line, so `prepr.sh`'s mutant draw has nothing to draw.

## Null control

- Head grader on the base's budget data (`git show origin/main:dev/governance/config/policy_budgets.json` written over the head's copy, then `node tools/policy/policy_lint.mjs`): `TOTAL: 2 error(s)`, the two `files_tokens` orphans named above. On the head's data: `TOTAL: 0 error(s)`. The check reads the defect at the baseline and not at the head.
- Base grader on the head's data (`git show origin/main:tools/policy/policy_lint.mjs` run in place of the head's): `TOTAL: 0 error(s)`, `FIXTURE ok ... 278 pins`. This is what `policy-docs` sees when it restores the base's grader, so no `BOOTSTRAP` split is owed.
- Over-fire arm, inside the acceptance: a budget whose `files` and `files_tokens` both cap every measured file and nothing else produces zero findings.

## Figures

<!-- figure-block: scope-line mb=367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c head=18eba6b3975754902eec6041788a1b71410d6a9a -->
~~~text
MODE: SCOPED -- 1 script(s) run, 32 scoped out.
~~~
<!-- /figure-block -->

1. Orphan token caps on `origin/main`, the rule that enumerates the class: `python3 -c "import json;b=json.load(open('dev/governance/config/policy_budgets.json'));print(sorted(set(b['files_tokens'])-set(b['files'])))"` printed `['tools/audit/briefs/nudge.md', 'tools/audit/harnesses/README.md']` at the merge base and prints `[]` at the head. Disposition of each: closed in this diff. The extended `checkOrphanCaps` is the standing instrument for the class (it also covers a token cap on a file that has a line cap and no glob).
2. `node tools/policy/policy_lint.mjs` at the head: `TOTAL: 0 error(s)`, `FIXTURE ok ... 279 pins` (one pin added; 278 at the base).
3. Budget-raise reading of this diff, offline through `budget_raise_gate.raises_between` from the merge base to the head: `[]`. Control: the same call with `files_tokens.CLAUDE.md` also dropped reports `files_tokens.CLAUDE.md: cap removed while the file it caps is still in the tree`. The removals here are not raises, because the capped files are absent at the head.
4. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
5. `git grep -n 'nudge' -- tools/ci/selftest_closures.json` prints nothing at the head. Control: `git grep -n 'nudge' -- tools/ci/` prints nothing either, so no other table under `tools/ci/` records the retired path.
6. `git grep -n 'nudge\.md' -- . ':!dev/programme/triage' ':!dev/programme/delivery' ':!dev/audit' ':!dev/programme/rosters/*.json'` at the merge base prints the `policy_budgets.json` cap plus three records under `dev/programme/` (`HANDOVER.md`, `RULINGS.md`, `round10/state/PLAN-TABLE.md`); at the head, the three records only. Records that recount are left as written.

## Unpinned sites

n/a: the diff adds no `.py` line and no `custom_components/` line.

## Architecture score

n/a: the diff touches no Python module `tools/audit/archscore/` reads.

## Approval

Policy change (owner gate: policy; `dev/governance/config/policy_budgets.json`). It merges on the owner's approving review at the head, or under a mandate in force scoped `all` (the group's first pass cited tvofi's comment 6893738184 on #3394, to 2026-12-15T12:00Z). No approval is recorded at this head.

## Red checks

none

## Forward-carry

none

## Friction

none
