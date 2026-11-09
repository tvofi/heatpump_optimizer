R10-FIXER-MD-SPELLING-CORPUS: lands the owner-approved sentence (orchestrator ruling under the mandate, coordination comment 6708543123) in the fixer role, word for word, and pays for it by tightening fixer.md prose.

Placement: step 2 ("Failing test first"), not step 5. At this merge base step 5 is "Measure the gate's scope" and no longer governs how a fixer tests a guard; step 2 holds the failing-test and mutation-proof rules, the place a guard's test is specified. No budget raised.

## Head

925ade0cfeb90b548e3b8a7cddc8779c688b173e (merge of origin/main 263b3908b into the step-pushed commit 7b68751a5; the sentence commit is unchanged by the merge).

## Mutation proof

n/a: policy prose, no production line. The sentence's absence at the base is the control below.

## Null control

`git show origin/main:dev/governance/roles/fixer.md | grep -c "generated spelling"` prints 0 at the merge base; at the head `tr '\n' ' ' < dev/governance/roles/fixer.md | grep -o "generated spelling corpus" | wc -l` prints 1 (sentence appears once; it wraps across lines, so a per-line grep reads 0).

## Figures

- `node tools/policy/policy_lint.mjs --budgets` role fixer line: within its cap and band, not raised.
- `node tools/policy/rules_sync.mjs --check`: ok.
- `node tools/policy/brief_lint.mjs` and `node tools/policy/policy_lint.mjs`: pass at the head.

## Red checks

none

## Approval

The sentence is approved word for word by the orchestrator's ruling under the mandate (comment 6624093439, scope all; coordination comment 6708543123, 2026-11-07). This is policy: it merges on the owner's approving review at the head.

## Forward-carry

- Carry 0 (owner's measure-first on prepr.sh mutant refusal, (a) and (b)) and Carry 1 (coverage term; the review packet's ordinal for it is carry 2, so Carry 2 too) were not measured in this seat: neither the review/* bus window nor the 10-diff mutant runs were executed, so (a) and (b) are not landed and no refusal is recorded. Carry: R10-FIXER-MD-SPELLING-CORPUS (pending owner or orchestrator ruling on re-dispatching the measurement; the owner's saving-versus-time condition stays unmet).
- R10-ROUND-PLAYBOOK-FINAL is not in the tree, so its reflection of this sentence could not be edited here. (Carry 3.) Carry: R10-FIXER-MD-SPELLING-CORPUS (pending orchestrator ruling; the playbook file is out of tree).

## Friction

none
