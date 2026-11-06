Root-cause records for the recurring-friction keys R10-FRICTION-REGRESSION left owed, the approved policy-tooling countermeasures of R10-RCA-FRICTION-RESIDUE, and the `instrument-self-tests` countermeasure #2865 never got. One record per key under `dev/audit/rca/`; the four existing records are judged for sufficiency and left alone.

No closing keyword: the roster lists these issues in the group's `issues` with `fixes: []`, so `pr-contract`'s intended list refuses `Closes` on them (`prepr.sh` step 7); the brief says the orchestrator wires `fixes` and the delivery closes them. One line per issue so the wiring has each:

Disposes #2875
Disposes #2950
Disposes #2998
Disposes #2942
Disposes #2436
Disposes #2437
Disposes #2429
Disposes #2840
Disposes #2835
Disposes #2895
Disposes #2907
Disposes #2860

## Approval

This diff touches `.claude/rules/ci-autofix.md` (and its `dev/governance` canonical and generated copies) and `tools/policy/policy_lint.mjs`. The `ci-autofix.md` sentences and the two `policy_lint` families (#2429, #2436, #2437) are the countermeasures `dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md` drafted, which the dispatch brief records as approved by tvofi on 2026-10-29: "All of these are approved." That is carried from the brief, not a live approval; **this pull request merges only on tvofi's approving review**. Not covered by that approval and flagged for it: the three spellings added to the `mutation` family (#2942) and the `ci_predict.py` `mutants` arm (#2865). The `fixer.md` sentence drafted in `R10-RCA-CLASS-OPEN.md` section 6 is not landed and waits on the owner.

## Head

7cb3e8a10b778a2e4ad54fb0b32456708bbacbd5

The branch started at `origin/main` `7e8939d38`; `origin/main` moved to `5421413b5` (a delivery row and `tests/gate_lock.py`), which is merged here, and `tools/pr/prepr.sh` was rerun on the merged head.

## Mutation proof

- `policy_lint.mjs` acceptance (`node tools/policy/policy_lint.mjs`, 267 pins): with the derived family's passing-verdict exclusion removed it prints `FIXTURE VACUOUS: the derived ...`; with `root-cause-unrecorded` removed from the declared family it does too. Both restored.
- `python3 tools/pr/ci_predict.py --self-test`: with the `mutants` arm's driver-selection line replaced by `if False:` the null-control row goes red. Restored byte for byte (`cmp`).
- Not mutation-proven: the `ARMS`/`arms` registration of `mutants` (the helper is driven directly; a deleted entry in `arms` would leave the self-test green). Stated in `R10-RCA-ROOT-CAUSE-DETECTABLE.md` section 7.

## Null control

- Every taught verdict row and every friction-id row of `node tools/policy/policy_lint.mjs --stats --since v7.0.4` prints byte-identically before and after the family changes (diff of the non-family rows empty); the literal `other` row still reads 2 PRs / 3 entries.
- `mutant_preds` over a diff touching no planted target runs no driver and predicts nothing; over the real tree with `README.md` changed it returns `[]`.
- The `root-cause` family reads 0 / 0 in this window (all three members file their own line): it adds no filing here, and the record says so.

## Figures

- `node tools/policy/policy_lint.mjs --stats --since v7.0.4` (517 merges, 450 with a verdict; run at the merge base): `root-cause-detectable` 12 PRs, `class-open` 32 PRs / 56 entries, `mutation-vacuous` 31 / 38, `mutation (family)` 1 / 2 -> 6 / 7 after the three added spellings, `other (untaught)` 65 / 78, `.claude/rules/gate-scoping.md` 12 / 13.
- `python3 -I tools/audit/seat/r10_ledger_mutants.py --self-test` and its three siblings: 0.71 s, 1.13 s, 0.33 s, 0.10 s (2.28 s together).
- `node tools/policy/policy_lint.mjs --budgets`: `.claude/rules/ci-autofix.md` 90 lines / 1463 tokens against caps 96 / 1469.

## Red checks

none known at handoff; CI has not run on this head. `tools/pr/ci_predict.py` ran inside `prepr.sh`.

## Forward-carry

- The `fixer.md` sentence drafted in `R10-RCA-CLASS-OPEN.md` section 6 (a generated spelling corpus for text-shape guards) is policy and **waits on tvofi's ruling**; it is not landed. Carry: dismissed: drafted for the owner, nothing in this tree consumes it until approved.
- A `tools/` mutation table (`R10-RCA-MUTATION-VACUOUS.md` section 5) is unpriced; the refusal stands until a seat prices it. Carry: dismissed: the cost number that would reverse the refusal is not produced by any group.
- The wider arm (run `--self-test` of every changed wired instrument) is deferred until a second PR beyond #3049 fails its own self-test. Carry: dismissed: one instance does not make a class.

## Friction

- `.claude/rules/ci-autofix.md`: cost: the file had 3 tokens of headroom under its 1469 cap; the two approved sentences cost 33 over and were paid by deleting a restating paragraph. Carry: dismissed: paid in this change.
