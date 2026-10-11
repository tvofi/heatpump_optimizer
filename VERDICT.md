Fix review: merge 6c14eb0a659845f78aca0a13669d46826cd5bd92

bus-nonce: 9b1f77bfa66e3aa55032d9a9ef85feb7

Resolution-delta review only (fix-review.md step 12), on f7967b649...6c14eb0a6.
The reviewed substance (verdict `merge f7967b649...` on review/2123) is not
re-judged; the delta is: the recarry merge d346165a6 (main 0f1ccbe52 in), the
repair commit 307881fcd, and the merge to head 6c14eb0a6.

## Root-cause claim — confirmed

Canonical `dev/governance/rules/ci-autofix.md` bytes (token = round(bytes/4)):

- merge base 70b50c573: 5822 (1456)
- main 0f1ccbe52 (merge parent): 5859 (1465) — under the 1469 cap
- branch f7967b649 (merge parent): 5862 (1466) — under the cap
- merged d346165a6: 5899 (1475) — OVER the cap

The overrun existed only at the merge; neither parent was over. Main's growth
(+37 bytes, #2121's DIRTY-head clause and the "That wait" rewording) combined
with the branch's rewritten paragraph. Reconstructed independently by byte
count at every ref; `policy_lint --budgets` reads 1468/1469 at the repair and
the head.

## The 29-byte payment is wording-only — confirmed

The repair commit 307881fcd touches exactly three files (canonical rule and
both generated copies). Six trims, byte deltas 5+8+4+4+6+2 = 29 = 5899-5870:
"that"-deletions, "there will be no bot commit" -> "no bot commit comes",
"is coming" -> "comes", "has been printed" -> "is printed", one "the" drop.
No rule, claim, skip-status, loop-guard or obligation removed; main's #2121
DIRTY-head clause is present at the head (line 15); the only issue id on a
deleted line (#1886) is on the paired added line. `rules_sync.mjs --check`:
RULES-SYNC ok — both generated copies are the generated form.

## The five reds — answered and green

Local proxies at the head (seat venv): `policy_lint` 0 errors rc=0 (1468/1469);
`policy_lint_mutants.mjs` MUTANTS ok rc=0 (11 corpus + 12 record checks);
`policy_lint_envmatrix.mjs` 16 held, 0 did not, rc=0; the fast (3.14) failing
check `_TA[1]` (tests/entities.py ~28705) measures exactly `policy_lint`'s rc
on the live tree — rc=0 here, was rc=1. Check-runs API at 6c14eb0a6: policy-docs,
env-matrix, instrument-self-tests, pr-contract (both runs) all **success**;
fast (3.14) and closures still in_progress at publication — fast's failure was
strictly downstream of the repaired rc=1 and policy-docs (the same command in
CI) reads success, so the local measurement stands in; CI's completing run is
the confirmation. The body's `## Red checks` names all five truthfully, each
with cause, repair and cheaper detector, plus the f7967b649-only closures red.

## Reviewed substance — byte-identical

`tests/mutation_table.py` and `.github/workflows/tests.yml` (budget 260, shard
constants, max-parallel) have zero diff lines across the delta; `tests/entities.py`
is additive-only from main's own growth; both claim files are byte-identical to
origin/main; no budget file touched.

Evidence: /Users/timmalmstrom/hpo-seats/r9rev-2123b/ev/ (rootcause.txt,
wording-only.txt, checks.txt, substance.txt, envmatrix/) — each names the head.

Head still 6c14eb0a659845f78aca0a13669d46826cd5bd92 at publication (ls-remote).
