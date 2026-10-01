Fix review: merge e26fa13b

Round 2. Measured head e26fa13b8af3359b633471f1ef0c7d220b97fc17, a fast-forward from round 1's c05c635f. The transport commits a3caafd7 and 8bb17f74 are not in its ancestry. git merge-tree against current main cc00ed85 is clean.

Round-1 blockers, each closed:
1. typing: _instant now returns float on both branches. An aware stamp gives epoch seconds; a naive stamp is read as UTC, which keeps its wall order. RESULT CI typing (job 110277750285) at e26fa13b: "ALL 9 typing-ruler checks PASSED". At c05c635f it had 6 operator errors.
2. barrier_gap now names the 10 census sites by file and function. It gives the rg command and the count (10 at the head), points to the RCA list on handoff/audit-r9-alt, and says R9-F10.1d owns the sites and the untraced same-zone compares (build_override's two `> cap` checks and is_expired).
3. The body's Red checks section names typing at c05c635f and answers it: the cheaper detector is mypy --strict on the changed module, it takes seconds, and the decision on a countermeasure is left to the orchestrator.

Re-measured at the head:
RESULT dst_checks NONE: rc=0, ALL 78 DST / QUARTER-GRID CHECKS PASSED.
RESULT reviewer mutant INSTANT-guard-off (`if False:`, so an aware stamp is read as UTC wall time): dst_checks rc=1, the fold-step NULL CONTROL is red (pins [0.0]). tests/manual_plan.py alone stays green. The ledger records tests/features.py as the killer, and features.py runs dst_checks, so that is consistent.
Round 1 still holds, because this round's diff touches only _instant, its two ledger entries and barrier_gap: the R3 and R5 mutants of RCA-BULK-1 are caught only by the new arms, the four FIX reverts are red, and the override lasts 20 true hours on both transitions.
Real-HA ha_contract (the Mac, HA 2026.9.3 on Python 3.14.7, at e26fa13b): ALL 61 contracts PASSED, rc 0; stub-vs-real ALL 22 probe comparisons PASSED, rc 0. The 2025.2.0 floor arm was not run.
Ratchets: no budget moved, and budget-raise-gate is green.

CI at the head when posted: typing, briefs, closure-scope, pr-contract, policy-docs, budget-raise-gate, delivery-status, nightly-status, hassfest and wave-script are green. fast (3.14), mutation, coverage, closures, browser, env-matrix, instrument-self-tests, validate-hacs and CodeQL were still running. The merge seat merges only on all-green CI, and main has moved to cc00ed85, so main must be merged in and CI re-run first.
