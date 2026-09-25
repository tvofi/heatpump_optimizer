<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: `verifier.md` gave each dimension one verifier whose vote killed nothing, `judge.md` re-measured every finding with no dedup step, and `defect-root-cause.md` and `CLAUDE.md` let a seat record "no countermeasure" for any defect, including a class that recurred three or more times in one round.

After: each dimension has three verifiers, each with a lens (reproduce including the perturbation, independent measurement, reach and class). Two refutes backed by executed numbers kill a finding at panel, and one refute sends it to the judge as disputed. The judge dedups across dimensions before re-measuring and gives every survivor a bug class. An audit class with three or more instances in one round (judged findings plus sweep-confirmed ones), or any instance of an already-barriered class, owes a barrier that eliminates the class. The cost test picks the barrier's form, and a seat that finds none within the bound asks tvofi instead of recording a refusal. Decision 0012's one-verifier panel is recorded as superseded, and the rest of 0012 stands.

This is readiness item R2 of the round-9 audit plan (`handoff/round9/PLAN.md` on branch `handoff/audit-r9-plan`), which implements tvofi's round-9 ask of 2026-09-25.

How:
- `verifier.md`: three verifiers, their lenses and the kill rule. It keeps the attached-refutation guidance, because `audit-find.js` and `audit-verify.js` still attach refutations until R1 and R3 land.
- `judge.md`: dedup first, a class for every survivor, and scripted re-runs count as the judge's own measurement.
- `.claude/rules/defect-root-cause.md` with its generated `.mdc`, and `root-cause.md`: the audit-class exception to "no countermeasure".
- `CLAUDE.md`: the recurring-error and root-cause lines now defer to that exception, and the role-table row for `verifier.md` changes.
- `docs/decisions/0012-process-diet-and-round-cadence.md`: a "Superseded in part" section for the panel shape. The moratorium is untouched, since this PR edits existing policy files and adds none.
- `D14.md`: steps 3-4 re-run once per class after the judge, as the class sweep.
- `COMMON.md`: finders measure only their own cells and record anything else as a lead.
- `tools/audit/README.md`: fan-out concurrency counts per container.

The driver changes (`audit-find.js`, `audit-verify.js`, scopes and schema fields) are R1 and R3: separate, and not policy.

The additions are paid for in the edited files, and no cap was raised or re-recorded:
- `tools/audit/README.md`'s "Resource rules" paragraph no longer restates `COMMON.md`'s contention rule.
- `root-cause.md`'s "Record it" no longer restates the Root cause section that `defect-root-cause.md` specifies.
- `judge.md`'s `load1` sentence is shortened, and the verifier's timing parentheticals now point to `COMMON.md`.

## Head

`d5b648348c0ea492245336d92fc27b5cc623d2eb`

## Approval

This is a policy change (`verifier.md`, `judge.md`, `root-cause.md`, `D14.md`, `COMMON.md`, `defect-root-cause.md`, `CLAUDE.md`, `tools/audit/README.md`, `docs/decisions/0012`), so tvofi's approving review is owed before the merge. It is not a budget raise: no cap in any `*_budgets.json` moves.

## Mutation proof

n/a: prose policy with no production or test code. The instruments that read these files are `policy_lint.mjs` (per-file line caps, the corpus cap and its band, and citations) and `rules_sync.mjs --check`. Growing any edited file past its line cap, or the corpus past cap plus band, turns `policy_lint` red. That happened on this branch before the payment cuts: `[budgets] (whole corpus): ... exceeds the cap`, rc 1.

## Null control

At the merge base, in a full (unshallowed) clone, `policy_lint.mjs` exits 0 with `TOTAL: 0 error(s)`. At this head it also exits 0 with 0 errors, and the same holds on the merge of this head into current `origin/main`. The earlier revision of this body reported six errors at both ends. Those came from a shallow clone, where citations that resolve through history cannot resolve, so they were not a property of either tree.

## Figures

- per-file caps, corpus and role caps: `node .claude/workflows/policy_lint.mjs --budgets`
- whole-corpus lint: `node .claude/workflows/policy_lint.mjs`
- generated rules in sync: `node .claude/workflows/rules_sync.mjs --check`
- gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D` (`MODE: SCOPED`)
- wave-script derivation: `node .claude/workflows/check-wave-script.mjs`

## Red checks

none

## Forward-carry

`tools/audit/briefs/verifier.md`, `judge.md`, `root-cause.md`, `D14.md` and `COMMON.md`: this PR is the carry. The round-9 roster that dispatches from them is R1 and R3.

## Friction

ratchet-budgets: cost: after this diff `corpus_tokens` sits at cap plus band with no room left (`policy_lint --budgets`), so the next policy addition has to pay for itself or ask for a raise.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
