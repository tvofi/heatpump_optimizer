Fix review: merge fa6622850cb389be47d792cd000457466064c5e6

bus-nonce: 8e86f5fb0696087b28b4cd1706e5e506

Round 1. Reviewed head fa6622850cb389be47d792cd000457466064c5e6 (authored code head 7b502385; the extra commit is the PR's own delivery row). Diff against the merge base is two markdown files: `dev/programme/triage/s6-batch70.md` and `dev/programme/delivery/2987.md`. No production code, no VERSION, manifest, notes heading, golden or claim file is touched (ev/untouched.txt is empty).

## Findings

None. The ruling is sound and settles what it names.

## Evidence

- RESULT mutation: `roster_edit.ruling_verdict` reads P304 as ACCEPT and `triage_refusal` returns None on the head file. With `Verdict: ACCEPT narrowed` changed to `REJECT narrowed`, it refuses: "...#P304 is not an ACCEPT ruling (REJECT)". With the file absent: "the triage ruling ... is not on the roster branch or origin/main". The gate that consumes the file moves under the mutant (ev/mutation.txt).
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0, tree 31b180b3 (ev/merge-tree.txt). Base is b646e8306, equal to origin/main.
- RESULT policy facts re-read at the head: `orchestrator.md` lines 100-105 say "A ready critical-path group starts regardless of every cap". `replan.py` lines 473-480 hold `while ready and free_slot() is not None:`, so the body's description of the scheduler is accurate. `check_plan` text on `in flight`, `working` and `peak` at replan.py lines 55-56 matches the body's account of the prototype's substring filter.
- RESULT carry claim: R10-ORCH-ROSTER-SCHEMA on `handoff/audit-r10-roster` holds the absorbed-edge closure from #2554 (wave-r10-groups.json line 8477), so part (b) "already carried" holds on that source. The other two carries (consolidation-folds, P131) were not re-read.
- RESULT `tests/structure.py`: STRUCTURE RATCHET PASSED at the head. The packet's `carry_audit` reads 0 findings and `figure_lint` reads 2 resolved, 0 not verified, 0 refused.
- Not re-derived: the four closure figures (-7.0, -4.0, -5.6, -5.6 h) and the saved plan-cp 2026-11-02T01:57Z come from the orchestrator's out-of-tree scratch rosters and `replan_cp.py`, which this seat does not have. I could not reproduce them; they are unverified here. The body discloses that they rest on that copy. The ruling's verdict does not depend on the exact figures, only on the direction, which follows from the scheduler lines above.
- Red checks: none red in the check-runs API at this read. Completed runs are green or skipped. `tests / fast (3.14)`, `tests / closures`, `tests / browser`, `governance / env-matrix`, `governance / instrument-self-tests` were still in_progress and no `pr-contract` run had started. These are heavy CI lanes cited, not re-run, per the contract. They are not a block for a docs-only diff, but the merge train reads them. The body's "Red checks: none" is correct as of now.
- Forward-carry: the body names none. The ruling's carry text is for `roster_edit.py append-carry`, which is held and gated by the same `triage_refusal` I exercised. The text states its control (null, mutant, self-test rows) as a precondition.
- `tests/entities.py` could not run here (no homeassistant module in this seat). The new file is under `dev/programme/triage/`, where every sibling batch file sits, so I expect it classified like them. That is unverified here and CI's closure-scope check passed.
