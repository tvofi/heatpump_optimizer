R10-PLAYBOOK-ROUND-START: adds one section, "Round start", to `dev/audit/README.md`: the pickup first, then the evaluation, finder and dimension steps and the scope rule, each by pointer to the file or group that owns it. This is **policy** (it changes what a round orchestrator must do) and merges on the owner's approving review, posted under mandate 6715477401 by the orchestrator. Owner instruction 2026-11-13, per the roster group's brief.

## Head

6a42af4a95685d8e72b1559bdd08c78647000ef8

## Approval

Policy change: merges on the owner's approving review, posted by the orchestrator under mandate 6715477401 (scope all), declared as such.

## Mutation proof

n/a: prose. The control the fixer contract asks of a prose change is that each pointer resolves, and the pickup enumerators have a planted-and-clean control (see Null control).

Pointer targets, each by command at this head:
- `test -f tools/audit/carry_audit.py tools/audit/seat/roster_edit.py tools/audit/check_scopes.py` (all three exist; `roster_edit.py set-resume --help` runs)
- `node tools/policy/brief_lint.mjs` (the playbook arm resolves every backticked path in the file)
- Not on main, so named as groups and not backticked: decision 0018 and its evaluator contract are #3575 (R11-PRE-OBJECTIVE-FUNCTION, `git show origin/handoff/r11-pre-objective-function:dev/governance/roles/evaluator.md`, same ref for `dev/audit/config/objective.json`); the denominator rule, remainder dispatch and added dimensions are R10-DIMENSIONS-FULL-COVERAGE part 2, carried on R11-INTAKE-R10-RESIDUE (`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`).

## Null control

- Enumerator 2 (groups at no done/absorbed/refused stage), run in a scratch tree: a roster of one `done` and one `refused` group prints nothing; replacing one with a `deferred` group prints `R11-PRE-X deferred`.
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

## Budgets

`node tools/policy/policy_lint.mjs --budgets` before: the file at its line and token caps with 6 lines and 9 tokens of headroom. After: 314 lines and 6057 tokens against caps of 321 and 6059; corpus inside cap plus band; `node tools/policy/policy_lint.mjs` 0 errors. No cap touched. Paid by cutting from the same file: the deferred-groups reopen bullet (superseded by the pickup), the context-rotation sizes (now a pointer to `fixer.md` and `standing.md`), a session-load figure, the `j5_gil.py` trailing paragraph, a stale-figure parenthesis and a sentence duplicating `fixer.md` step 2 in Lessons, and tightening of the Rounds 1-3, merge-queue, moved-paths, instrument-defect and protection-census paragraphs, plus compressing this section to one line per step.
