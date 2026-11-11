Fix review: merge 97e6011948c9dd967888050fcb5ad4bc4a17c94b

bus-nonce: a0bf39d1a7211f0226b7e1c0cd342aca

## Summary

Handoff review, round 1, of R10-HOTFIX-GATE-REDISPATCH-LOOP at the handoff tip 97e6011948c9dd967888050fcb5ad4bc4a17c94b (base ee64358be7eeccaec5178a923cb3b83a18a924a0). The diff stays at the two arms: tools/ci/gate.py (a unit whose jobs concluded only cancelled or success, with at least one cancelled, is no source) and tools/ci/sweep.py Sweep.fresh() (a workflow_dispatch at the head that is not completed, or concluded success, is the fresh judge). Only tools/ci/sweep_selftest.py otherwise. Each arm has a failing self-test at the base and a null arm that passes at both ends. Every named mutant is killed. The body states the merge-timing cost ("one fresh dispatch per open PR once; time the merge accordingly").

## Evidence

- RESULT head: gate self-test 87 checks, 0 failed; sweep self-test 85 checks, 0 failed (ev/head-selftests.txt). Matches the body.
- RESULT base: gate 81 checks, 0 failed; sweep 81 checks, 0 failed (ev/base-selftests.txt). The body's gate 81 matches.
- RESULT null control (head's tests on base code): gate 87 checks, 3 failed (cancelled-over-green, late-cancel, only-cancelled-run); sweep 85 checks, 3 failed (the three one-judge-per-head arms). Every null arm passes at base and at head: newer failed over older green reads red, fail-fast reads red, newer green over older red reads green, and a lone failure or cancelled dispatch dispatches exactly once (ev/null-control-base-code-head-tests.txt).
- RESULT mutants (ev/mutants.txt, sweep re-run with bytecode off in ev/mutants-sweep-rerun.txt; the first sweep run was polluted by stale .pyc from two equal-size mutants in one second and is superseded): M1 gate whole continue deleted, 3 of 87 failed. M2 "success" dropped, 1 of 87. M3 any-cancelled clause deleted, 19 of 87. M4 sweep creation key restored, 3 of 85. M5 success arm dropped, 5 of 85. M6 not-completed arm dropped, 4 of 85. M7 any completed dispatch counted as judge, 2 of 85 (the failure/cancelled null arms). M8 survives: `r is not me` dropped from the new gate skip line. See Findings.
- Scope: `tests/closure.py select` prints `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself`. Full suite is CI's; not re-run (ev/gate-structure-merge.txt).
- Structure: `tests/structure.py` prints STRUCTURE RATCHET PASSED. No budget file, claim file, closure file or INERT entry is touched. No moved metric needed an earned-by check (step 14).
- VERSION, manifest version and RELEASE_NOTES heading are untouched. The diff is three files under tools/ci.
- Merge: head is 6 commits behind origin/main 60413046e3. `git merge-tree --write-tree origin/main <head>` exit 0 with tree b8081f6c69, so no conflict. None of the 6 commits touches tools/ci or .github.
- Class (step 6): a grep of tools/ci for cancelled and dispatch handling finds no third seam that picks a run as a head's judge. codescan_wait.py:120 already treats cancelled like skipped. sweep.settled/undecided read gate jobs, as the body says. Not class-open.
- Head (step 7): the body's `## Head` names 97e6011948c9dd967888050fcb5ad4bc4a17c94b, which is the handoff tip I measured.
- CI: there is no pull request, no review packet and no CI run at this head, so there was no check to read. `merge_train.py owed-reds` prints tests / coverage-ratchet, tests / fast (3.14), tests / mutation, tests / typing, validate / validate-hacs. None can be red at a head with no runs. Main's inherited tests / fast combi-census red and governance / instrument-self-tests failures are not this PR's.
- Forward-carry: the body has none, and the roster assigns this hotfix no carry that I was handed.
- Could not re-derive: the P620 measurement (10 of 43 code dispatches), which the body attributes to the ruling and does not re-take. The cited ruling file dev/programme/triage/s6-batch196.md exists at neither origin/main nor the head, so I could not open it.
- Policy currency: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

## Findings

- Follow-up: the sweep.py module doc (lines 50-52 at the head, ev/sweep-module-doc-48-53.txt) still states "A dispatched run created after the stale gate concluded is that fresh judge already". That is the creation key this PR removes, so the module doc now contradicts Sweep.fresh(), whose own docstring was updated. Carry: dismissed: one-sentence doc drift in a file this PR already edits; the fixer can fold it in before the PR opens, and a doc-only delta never widens a review (fix-review step 12)
- Follow-up: some body figures do not reproduce. Mutation proof "whole continue deleted ... 2 of 85" measures 3 of 87, and null control "gate self-test 2 of 85 failed" also measures 3 of 87. The extra failure is the late-cancel check, and the check named "null: with only the cancelled run at the head..." fails at base, so it is a failing arm, not a null arm. Carry: dismissed: the proof is stronger than the body states and the corrected counts are recorded in this verdict's ev/; a body correction, not a code defect
- Residual: mutant M8 survives. Dropping `r is not me` from the new cancelled-unit skip leaves 87 of 87 gate checks passing, and the pre-existing deferred-unit skip shows the same survivor (M9). No self-test covers a gate whose own run carries a cancelled-plus-success unit. Carry: dismissed: parity with the base line's untested own-run guard; it is outside both livelock arms and kept conservative, so the gate's own unit always judges
- Residual: dispatch freshness is not bound to a pin. A green dispatch created before a later tools/ci change on main still counts as the head's fresh judge, so the merge note's "one fresh dispatch per open PR" is an upper bound (a PR with a live or green dispatch at its head gets none), and such a head is not re-judged with newer programs by the sweep. Carry: dismissed: no loop and no regression against base, where a stale-pinned red that re-running cannot clear was not cleared either and a push re-judges; the hotfix's ruled scope is two arms

## Red checks

None. There are no checks at this head before the PR opens (see Evidence).
