R11-PRE-FINDER-CONTRACT, p2 of 2 (DRAFT, WIP until p1 is on main): the finder's denominator, every dimension every round, the playbook's round start. Built from eval/r11 at 02a48db212, approved by the evaluation review round 3 (eval-review/r11-3, 92991d2a49); card E11-COMMON is byte-identical at 7891b714f8 and 02a48db212.

What lands:

- `dev/governance/roles/COMMON.md`, "The denominator" (E11-COMMON part 1): a step ranges over what its enumerator prints; per step the `coverage` row carries `enumerator`, `universe`, `examined`, `not_reached`, `redispatched`; a step with no row or with counts that do not close counts 0 and the seat is read as not reported; what was not reached opens the next round. Part 2: "about two hours" and "Prefer three findings" are replaced by the cells `check_scopes.py --seat` prints.
- `dev/audit/config/finding.schema.json` and the copy `audit-find.js` inlines (`fold_ledger.py sync`): the coverage rows require the five keys; the dimension patterns admit D16 and D17 (wiring them is R11-PRE-NEW-DIMENSIONS').
- `.claude/workflows/audit-find.js`: `carryOf`, `seatCarry`, `denominatorGaps` in the DISPATCH block; a report whose denominator does not close is re-run once, then refused at intake; the ledger sums the denominator per step. The cadence (`CADENCE`, `EVERY_DIM_ROUNDS`, `activeIn`, the active-box filter) is DELETED, not set to one: with D5, D6, D11 and D13 every round (tvofi 2026-11-13) no dimension is left on a cadence, and a table whose every entry is one still lets a missing entry silently drop a dimension (`!!CADENCE[dim]`). Decision 0012's cadence section is the record this supersedes.
- `tools/policy/check-wave-script.mjs`: the denominator block unconditional (`DENOM` and its `skip` arm deleted), the schema's five required keys asserted from the file, rounds 11 and 13 driven to dispatch every seat (carry 2).
- `dev/audit/README.md` round start: P795's disposition wording, both pickup commands at `origin/handoff/audit-r<N>-roster` (`carry_audit.py --roster-ref`, `git show`); step 3 names the paths (carry 1).
- `dev/audit/harnesses/r11_denominator_planted.py`: the planted control.

## Head

cb6600d2f1 (WIP; re-take every figure at the handoff head, after p1 merges)

## Figures (at cb6600d2f1, merge base 26dbf7c43e; re-take)

- `node tools/policy/check-wave-script.mjs`: 249 passed, 0 failed. p1's copy over this tree: 248 passed, 0 failed. Main's copy over this tree: 163 passed, 1 failed (`CADENCE is not defined`), the BOOTSTRAP `ci_predict.py --only graders` predicts.
- Dual mutant (schema `required` loses `enumerator`, `fold_ledger.py sync`): 248 passed, 1 failed, `the finder report schema's coverage rows require the denominator`. Cadence reinstated as a filter: 28 failed. Intake refusal deleted: 1 failed, `a seat whose report carries no denominator is dispatched twice, ends missing, and intake does not run`.
- `python3 dev/audit/harnesses/r11_denominator_planted.py`: driver_refuses_bare=1, driver_passes_full=1, reader_rows=2, reader_counted=1, reader_counts_bare=0; at main's driver it prints driver_missing=1.
- `node tools/policy/policy_lint.mjs`: 0 errors; `node tools/policy/brief_lint.mjs`: rc 0; `python3 tools/audit/check_scopes.py --repo . --self-test`: SELF-TEST passed; `python3 tests/structure.py`: STRUCTURE RATCHET PASSED; `ci_predict.py --apply-inert`: the harness's INERT READS entry written.
- Budgets (`node tools/policy/policy_lint.mjs --budgets`): `dev/audit/README.md` (row `tools/audit/README.md`) paid under its cap; `dev/governance/roles/COMMON.md` (row `tools/audit/briefs/COMMON.md`) raised to its measured lines and tokens.

## Raise justification

Payments taken: the schema restated under Output, the quiet-box sentence restating "Where you work", the Budget heading folded into the denominator, a motivation sentence under non-findings, the denominator bullets folded into one paragraph. Payments considered and not taken: #961's keyed-count example (unique, `git grep` finds no second copy). Architecture score: dS to be measured with `tools/audit/archscore/` before and after at the handoff head.

## Resume

1. After p1 merges: merge origin/main, confirm `ci_predict.py --only graders` predicts no BOOTSTRAP, re-take Figures, run prepr.sh with the full body (Mutation proof, Null control, Red checks, Forward-carry, Friction).
