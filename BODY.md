Six carries the s11 verifier found stranded. Four are already answered in the tree (below, each with its commit and a measurement); carries 4 and 5 (R10-ORCH-LEDGER, `review_owed` and a record-owed kind) are built here.

Not edited, for the owner: `dev/governance/roles/standing-tick.md` states the ancestor-recarry test in prose and is policy; it could name the `CARRY:` line. The FILTERED arm of `review_owed` stays with R10-FLY-TICK-APPROVAL-OWED's P322 as the carry says.

Carry 1: field_coverage `attribution`, delivered by df9bfd301. Carry 2: pre-bash.sh hook, delivered by 408644f7f. Carry 3: agreement.mjs bootstrap deadlock, delivered by 82f333b9c. Carry 4: real-day loop_cpu_ratio budget, delivered in tests/replay.py. Carry 5: record-owed ledger entry, built here. Carry 6: CARRY arm of `review_owed`, built here.

files: tools/audit/seat/ledger.py, tools/audit/seat/orchestrator_tick.py, tools/audit/seat/beat_jobs.py, tools/audit/seat/owed_unactioned.py

## Head

849ceee292dc04832d090fa328ccc0bdbb747f82 (origin/main unmoved at b88684a21 at 2026-11-06, so no second prepr.sh run was owed; the one run was clean).

## Mutation proof

Delete the ancestor test in `git_recarry` (the `merge-base --is-ancestor prior head` guard): `python3 tools/audit/seat/ledger.py --self-test` goes red on `null control: a prior that is no ancestor of the head carries nothing`; restored, 86 checks, 0 failed. Dropping the recarry argument at the call site is killed by `null control: the same head without the recarry test is REVIEW OWED`.

## Null control

Carry 5: a head plus a verdicted head's one main merge prints CARRY; a code commit on top prints REVIEW OWED; head plus only its own `delivery/<N>.md` row prints CARRY, plus its row and another file prints REVIEW OWED. Carry 4: an approved `record/` PR open 31 min opens `RECORD-OWED`; 29 min, unapproved, off-branch, draft do not; absent from the open list (merged or closed) it closes. Base (b88684a21): `git grep -nE "CARRY|RECORD-OWED" b88684a21 -- tools/audit/seat/ledger.py` finds nothing.

## Figures

- `python3 tools/audit/seat/ledger.py --self-test`: 86 checks, 0 failed (rule: its own count line).
- `PYTHONPATH=tests/hastub python3 tests/doc_claims.py`: ALL 296 checks PASSED; `tests/entities.py`: ALL 2632 ENTITY CHECKS PASSED; `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` gave MODE: SCOPED, running doc_claims.py and entities.py.
- Carry 0 delivered: `git log -S"'attribution':" -- tools/policy/field_coverage.mjs` shows df9bfd301; the key is in the hooks registration's `ignore`, no `pending` map holds it.
- Carry 1 delivered: 408644f7f (pre-bash.sh, settings.json, policy_lint HOOK_TOOLS); `bash .claude/hooks/pre-bash.sh --self-test` 26 passed, 0 failed; `node tools/policy/policy_lint.mjs --hooks` HOOKS ok.
- Carry 2 delivered: 82f333b9c (`(awaits <path>)` clause, harness dev/audit/harnesses/agreement_two_pr.mjs); `node tools/policy/agreement.mjs --self-test` 233 of 233 probes held, including the null control that the reader PR without the entry is UNREGISTERED.
- Carry 3 delivered: tests/replay.py re-centres the real-day `loop_cpu_ratio` (0.249) on readings from four environments and keys the synthetic budget by runner class (`COST_CLASS_BUDGETS`), commit 37bafc867 and its successors; not re-measured here.

## Red checks

none

## Forward-carry

none

## Friction

none
