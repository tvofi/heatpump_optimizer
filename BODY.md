Triage batch 89 rules the orchestrator s8's proposal of 2026-10-31 (#3006 round 3). The proposal is that, after a main merge, CI auto-records a structure budget that measures IMPROVED and not yet recorded, the way closures-autofix records closures. This is the next rolling batch after batch 88, with one ruling and no roster op.

- **P326: REJECT.**
  - **The filed form is a policy change.** `ci-autofix.md` names structure budgets among the things CI must never automate, and CLAUDE.md rule 2 has re-recording done deliberately with a reason. Accepting would need the owner's edit to both, and the trade fails before that question.
  - **The cause, measured on #3006's merge chain.** `ledger_merge.py` sums both deltas for a count in `structure_budgets.json`, and did so on #3006's first three merges. At the train's recarry `9033a5958` both sides read 17656 against a base of 17658. The driver's earlier rule, "a key both sides changed to the same value takes it", kept 17656, while the tree measures 17654.
  - **The driver fix is rejected as unsound.** That fix would sum even when the two sides agree. But the equal-value rule is what keeps a merge correct when both sides carry the same reduction, as a re-cut handoff merged by `update_pr.sh` does. Summing there double-counts and reads as a raise.
  - **The benefit is one instance.** It cost about 30 minutes, it announced itself in `tests / fast` and prepr, and it was repaired by one deliberate `structure.py --record`.
  - **Re-open trigger:** three or more such PRs in a round, raised then as the owner's policy question.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`8dc74f5cf82cb6ae7f2588a63db9c01e18eeb365`; the file is the whole diff against `4822c8f9b`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P326 as `REJECT`. A probe carry citing `triage: dev/programme/triage/s6-batch89.md#P326` is refused: `dev/programme/triage/s6-batch89.md#P326 is not an ACCEPT ruling (REJECT)`.
- With `Verdict: REJECT` changed to `Verdict: ACCEPT`, the same carry passes: `triage_refusal` returns None.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `class_excess_loc` on #3006's first-parent merges (base / ours / theirs / merged): `4665c0c91` 17672/17671/17659/17658; `958b4af8e` 17671/17658/17670/17657; `76d96ac77` 17659/17657/17658/17656; `9033a5958` 17658/17656/17656/17656.
- `tools/merge/ledger_merge.py` line 242, `if ours == theirs: return ours`, runs before the count rule (`LEDGERS["tests/structure_budgets.json"] = "sum"`).
- `ci-autofix.md`: "Do not automate survivor triage, golden drift, structure budgets, `no-copies`, orphan → `INERT`, or briefs lint."
- 41 first-parent merges on main since 2026-10-17 touched `tests/structure_budgets.json`.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
