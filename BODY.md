R10-PLAYBOOK-ROUND-START: adds one section, "Round start", to `dev/audit/README.md`: the pickup first, then the evaluation, finder and dimension steps and the scope rule, each by pointer to the file or group that owns it. This is **policy** (it changes what a round orchestrator must do) and merges on the owner's approving review, posted under mandate 6715477401 by the orchestrator. Owner instruction 2026-11-13, per the roster group's brief.

## Head

76aca12e6f9c5089c76434c5f8ec4af91a676909 (repair of verdict/3600 at bf719e68 on 6a42af4a; fast-forward; the delivery-row commit e3df1f1c is re-carried by the train)

## Approval

Policy change: merges on the owner's approving review, posted by the orchestrator under mandate 6715477401 (scope all), declared as such.

## Mutation proof

n/a: prose. The control the fixer contract asks of a prose change is that each pointer resolves, and the pickup enumerators have a planted-and-clean control (see Null control).

Pointer targets, each by command at this head:
- `test -f tools/audit/carry_audit.py tools/audit/seat/roster_edit.py tools/audit/check_scopes.py` (all three exist; `roster_edit.py set-resume --help` runs)
- `node tools/policy/brief_lint.mjs` (the playbook arm resolves every backticked path in the file)
- Not on main, so named as groups and not backticked: decision 0018 and its evaluator contract are #3575 (R11-PRE-OBJECTIVE-FUNCTION, `git show origin/handoff/r11-pre-objective-function:dev/governance/roles/evaluator.md`, same ref for `dev/audit/config/objective.json`); the denominator rule, remainder dispatch and added dimensions are R10-DIMENSIONS-FULL-COVERAGE part 2, carried on R11-INTAKE-R10-RESIDUE (`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`).

## Null control

- Enumerator 2 (groups outside `roster_lib.FINISHED_STAGES` plus `refused`), the README's line run verbatim in scratch trees (`enum_control.sh`): `done` + `refused` prints nothing; `rca-done` + `refused` prints nothing (the literal it replaces printed `A rca-done`, the review's control); `deferred` + `absorbed` prints `A deferred`; all rc 0. At this head's roster it lists 46 groups, the review's count.
- Enumerator 1 (`carry_audit.roster_report`, called on a minimal roster): a `done` group with no carry returns `[]`; a `deferred` group holding a carry returns one `STRANDED R10-A (deferred) carry[0]` line.
- Neither enumerator itself refuses a round start: the one-liner exits 0, and `carry_audit.py roster` exits 1 only on stranded carries. The section says to read both to none; no instrument refuses a baseline over an undispositioned line yet (see Forward-carry).

## Figures

none. The section states no count.

## Red checks

none.

## Forward-carry

- Pointers waiting on #3575 (R11-PRE-OBJECTIVE-FUNCTION): step 2 names decision 0018 and the group, unbacktick-ed because the evaluator contract is not on main at this head. #3575 or a follow-up adds the evaluator contract's path to step 2 once it lands (brief_lint refuses a cited path not in the tree). #3575 also edits this file's phase 2 row and phase 13 row, and one paragraph; this section sits before "The harness contract", clear of those hunks. #3451 edits only lines inside the earlier carry bullets. Carry: R11-PRE-OBJECTIVE-FUNCTION
- Steps 3 waits on R10-DIMENSIONS-FULL-COVERAGE part 2: when its denominator rule, remainder dispatch and the two dimension briefs land, replace the group citation with their paths. Carry: R11-INTAKE-R10-RESIDUE
- The brief asks that the round start be refused by an instrument while any pickup line is undispositioned. None exists: `audit-find.js`'s baseline step runs `check_scopes.py --round` (evaluation only, #3575). Building the refusal (an exit-1 check over the two enumerators run from `check_scopes.py` or the pickup) is a tooling change outside this one-file prose group. Carry: R11-INTAKE-R10-RESIDUE

## Friction

- brief-citations: unclear: a group id cited in the playbook (R11-PRE-OBJECTIVE-FUNCTION) is resolved by nothing, so a rename of the group strands the pointer unseen. Carry: R11-INTAKE-R10-RESIDUE

## Review answer (verdict/3600, bf719e68, evidence-cut)

Restored in `dev/audit/README.md`, the three sole-copy constraints the previous payment cut. The role contracts they bind sit at their token caps (`designer.md` 877/878, `root-cause.md` 998/998, `architect-planner.md` 1261/1261, `plan-review.md` 304/304), so each stays in the playbook:
1. The instrument-defect paragraph: a verifier who cannot make the accused check fire "has not refuted it, and says which they could not separate". `git grep -F "says which they could not separate" HEAD -- dev/governance dev/audit/README.md .claude CLAUDE.md AGENTS.md tools/audit`: one hit, `dev/audit/README.md:283`; at e3df1f1c, none.
2. The context-rotation bullet: about 150 k tokens for mechanical and relay seats, about 300 k for designers, pre-studies, root-cause and plan seats, about 500 k for the orchestrator; fixers, reviewers and standing seats point at `fixer.md:10`, `fix-review.md:8` and `standing.md:39`, which state theirs. The same grep for "150 k tokens for mechanical and relay seats" and "for designers, pre-studies, root-cause and plan seats": one hit each, `dev/audit/README.md:70` and `:71`; at e3df1f1c, none.
3. The moved-paths paragraph: "A seat re-running a retired one repairs it first." The same grep: one hit, `dev/audit/README.md:274`; at e3df1f1c, none.

Finding (enumerator 2 hard-codes its closed set): built here, since the one-liner is this group's own seam. It now reads `roster_lib.FINISHED_STAGES` plus `refused`; controls under Null control. The refusing instrument stays where the review carried it (the third Forward-carry item).

## Budgets

`node tools/policy/policy_lint.mjs --budgets`, the one touched file (labelled `tools/audit/README.md` in the table; `dev/audit/README.md`, 312 lines by `wc -l`):
- merge base 23cc7b8e: 315 lines / 6050 tokens against caps 321 / 6059.
- before this repair (6a42af4a): 314 / 6057; corpus ~68955 against 68618 + 500.
- this head: 312 / 6049; corpus ~68947 against 68618 + 500 = 69118; always-loaded, role record and role policy unchanged (3605, 7428, 10014). No cap, band or `*_budgets.json` touched; `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 51 policy file(s)`.

Payments, each with its surviving copy at this head:
- Cut the `tests/plan_view.py` trap ("per-checkout plan payload under `/tmp` ... `card.mjs` alone falls back to an unhashed legacy path ... Set `HPO_PLANDATA` per harness"). Second copies: `tests/README.md:390-394` (`HPO_PLANDATA` defaults to a per-checkout `/tmp` path; "`card.mjs` alone falls back to an unhashed default under `/tmp` with a warning ...; every other Node harness requires it") and `dev/audit/README.md:193` ("It sets a private `HPO_PLANDATA` under that root before any Node harness").
- Cut the `tests/env_drift.py` trap ("runs `git worktree add` in the repository it is run from and refuses a ref that resolves to `HEAD`"). Second copy: `tests/README.md:298-313` (the working tree against "a worktree of a reference commit", "the refusal of a ref that resolves to `HEAD`", and that refusal's two consequences for a hand run).
- The previous payment's cuts the review accepted stay cut, each with the second copy it named: the 0.00-0.06 h replay figure, the spelling-corpus sentence (`fixer.md` step 2), the `j5_gil.py` FakeHass sentence (README Traps), the s14 load figure, and the deferred-groups bullet (replaced by pickup step 1; declared policy below the owner's review).
