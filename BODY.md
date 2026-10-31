Triage batch 87 rules the orchestrator s8's slip proposal of 2026-10-31. #3006, a budget raise approved under the mandate, lost tvofi's approval twice in one hour to automatic merges. The proposal is for `budget-raise-gate` and the train to accept an approval on an ancestor head when `review_carry.py` prints CARRY. This is the next rolling batch after batch 86, with one ruling and no roster op.

- **P324: REJECT**, both as filed and in its narrowed train-side form.
  - **The filed form is rejected.** It would weaken decision 0013's at-head guarantee inside a pinned required check. It would also make the gate trust a carry judgement from seat tools that a PR can edit.
  - **The train already carries the approval when it moves the head itself.** `--approval-carry` is on by default and re-posts the approval at the new head, so the at-head rule needs no edit.
  - **What #3006 hit.** The carry only accepts an approval on a head that the same train run's recarries moved through. #3006's approval was on `958b4af8`, and its first move was a `ci: merge main` that the train did not make.
  - **The narrowed fix is rejected too.** It would also accept the approved commit when `app_approve.sh --carry` prints CARRY. Benefit: 7 raise merges since 2026-10-17 and about 3 refusals at about 5 minutes each. Cost: an S fixer and review cycle that widens a condition the owner set, with round 10 closing on 2026-11-01. That is a marginal trade.
  - The ruling records a re-open trigger: three or more such refusals on raise PRs in one round. It also records the fixture the narrowed fix would owe.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`bc0bee5ffe72653a33424035682f4fa06e7f8e81`; the file is the whole diff against `4822c8f9b`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P324 as `REJECT`. A probe carry citing `triage: dev/programme/triage/s6-batch87.md#P324` is refused: `dev/programme/triage/s6-batch87.md#P324 is not an ACCEPT ruling (REJECT)`.
- With `Verdict: REJECT` changed to `Verdict: ACCEPT`, the same carry passes: `triage_refusal` returns None.

## Null control

- With the file absent, the citation does not resolve, and the gate refuses it as not on the roster branch or origin/main.

## Figures

- `budget_raise_gate.raises_between(<merge>^1, <merge>)` over the 51 first-parent merges since 2026-10-17 that touch a `*_budgets.json`: 7 raise, namely #2817, #2620, #2647, #2633, #2585, #2586 and #2368.
- `tools/audit/seat/merge_train.py` at `4822c8f9b`, lines 1653-1655: the carry's chain is `item.get("carried_chain")`, with `no("this run's recarry did not move the head")` on an empty chain. `tools/audit/seat/train.sh` line 87 lists `--approval-carry` as "on already".
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
