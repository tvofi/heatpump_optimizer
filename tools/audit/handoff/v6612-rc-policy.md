_Requested by **tvofi**_

This is a policy change, so tvofi's approving review is owed. It addresses the
process state (d) that the v6.6.12 root-cause record named, in
`handoff/v6612-root-cause` (`tools/audit/handoff/v6612-root-cause.md`).

**Before.** `fix-review.md` measures a fix with the finder's harness (steps 2
and 9). A feature has no finder. #1588's first review recorded "No finder
harness is committed for this feature", then reviewed against the
implementer's own fake pump. The judge's P4 (a write counts as landed only on a
report taken more than 8 s after it) and M5 ("Is DP 9 below 25 accepted?")
reached v6.6.12 untested and unwaived, and bugs 3 and 4 followed. The class
ledger had no class for "the only oracle for an external counterpart is a
double the implementer wrote", so round 9's D14 could not pick it.

**After.** Step 9 of `fix-review.md` gains one line: for a feature, the judge's
design is the harness. Any requirement or on-device measurement it names that is
neither tested nor waived by tvofi returns `blocked: design trace missing:
<item>`. `tools/audit/bugclasses.json` gains P11, with the v6.6.12 instances and
the earlier ones found in the record. D14 picks classes from that ledger, so no
change to `D14.md` is needed.

**Cost.** The standing cost is one trace per feature PR that implements a judge
ruling. The record I read holds one such feature (dhw-control, #1588), and it
escaped with at least five defects. The measured frequency is therefore one
instance; the case for the step rests on that one escape's cost.

## Head

7b663b027ebd6e4e6f58fbbe269beaaa17ad6a65.

## Mutation proof

n/a: a policy line and a ledger entry, no production code. `node
.claude/workflows/policy_lint.mjs` checks the policy file.

## Null control

n/a: nothing is measured. `policy_lint.mjs` reports 0 errors both before and
after the change.

## Figures

- `node .claude/workflows/policy_lint.mjs` prints `TOTAL: 0 error(s) across 40
  policy file(s)`.
- `node .claude/workflows/policy_lint.mjs --budgets`: fix-review.md is at
  140 lines against a cap of 140. The corpus is ~55918 tokens against a cap of
  55433, inside the +500 band (55933). No budget is raised.

## Red checks

none

## Forward-carry

`tools/audit/bugclasses.json` P11 is the carry into round 9's D14.

## Friction

`policy-budgets: cost: fix-review.md had one line of headroom and the corpus had ~75 tokens, so the step is a single long line`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01XQkb2K7Xcpm4KxSZRQ6EDx
