Fix review: merge 28f880d6e709bb6315ec1e2dfafdae46d1570515

bus-nonce: f0e1eb7db6a5cb200c23de62c9968ffc

## Summary

Round 1: the first full review of #3384 (R10-HOTFIX-NONREQUIRED-REDS-2), at head 28f880d6e709bb6315ec1e2dfafdae46d1570515, which carries code head 7d3c52b79c72de161350a2c4728aa84779758a24 merged with origin/main d08ed31049. The PR narrows two things to the set `merge_train.py owed-reds` prints. In `orchestrator_tick.py`, `RED unanswered` now names only owed reds, and every red when the set cannot be read. In `cloud_dispatch.py`, the reviewer and fixer prompts each get one line, and the role contracts get the matching wording.

## Findings

- Follow-up: the head's `dev/audit/harnesses/r10_seat_selftests_mutants.py` declares `cloud_dispatch-21` and `cloud_dispatch-22` twice. This PR adds them at lines 112-113, and main's #3366 had already added them at lines 577-578; the clean automatic merge at 28f880d6 put both pairs in one list. The harness runs every entry under a named id, so the proof still holds: `ev/mutants-named.txt` shows all four KILLED. What breaks is citation: a record that names `cloud_dispatch-21` now means two mutants. The class is not this PR's alone, because origin/main already carries six such collisions (`bus-16`, `cloud_relay-50`..`-54`) and nothing refuses a repeated id. Control: the AST count in `ev/mutant-id-dups.txt` finds 0 duplicates at 7d3c52b7, 6 at origin/main and 8 at this head. Re-measure at the destination's merge base. The fix it owes is an id-uniqueness check in the harness, demonstrated failing on today's list, plus a renumbering. Carry: R10-LEDGER-RESIDUE
- Residual: my own mutant R1 survives. It replaces `req = (getattr(self, "_req_pr", None) or required)` with `req = required` at `orchestrator_tick.py:1261`. It is equivalent at this tree because `PR_ONLY = ()` (`orchestrator_tick.py:137`), so `_req_pr` equals the required set, and the line matches the existing pattern at :1231. Carry: dismissed: equivalent mutant while PR_ONLY is empty
- Residual: my own mutant R3 survives. It changes `if owed_red:` to `if red:` at `orchestrator_tick.py:1264`. That only adds a body fetch when every red is non-owed, and `missing` is still filtered by `owed_red`, so the findings are the same unless the body cannot be read. Carry: dismissed: behaviourally equivalent except the unreadable-body path

## Evidence

- Mutation proof (step 1): `dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_dispatch-21 cloud_dispatch-22 orchestrator_tick-6 orchestrator_tick-7 orchestrator_tick-8 orchestrator_tick-9` at the head reports every mutant KILLED, including both colliding pairs, `RESULT survivors=0`; `ev/mutants-named.txt`.
- My own mutants (`ev/mutants-own.txt`). R2 (`missing` over `red`) KILLED, 3 checks failed. R4 (drop `defect-root-cause.md` from the dispatch line) KILLED. R5 (the line emitted twice) KILLED. R1 and R3 survived; see Findings. Unmutated self-tests: orchestrator_tick 308 checks, 0 failed; cloud_dispatch 149 checks, 0 failed.
- Null controls in the diff: the orchestrator_tick case "unreadable set: every red" and the cloud_dispatch "no other role" check. -9 and -22 kill them respectively.
- Finder's harness (step 2): none was named. This is a policy hotfix from an owner ruling (tvofi 2026-11-07, 2026-11-09), not an audit finding, and the self-test cases are the fixer's instrument.
- Class sweep (step 6): this PR changes two sites, and the other owed-red deciders already defer to the owed set. `policy_lint.mjs:7164-7169` (`redOwed` over `requiredFromTrain`, i.e. `merge_train.py owed-reds`) is the filter that `pr-contract.yml`, `review_packet.unanswered_reds`, `prepr.sh` and `body_push.sh` pass every red into. `orchestrator_tick.py` was the one decider that did not filter, and this diff closes it. The prompt line in `cloud_dispatch.py` is the instruction seam. I found no open seam. I used a subagent locator for the read and confirmed the deciding lines quoted.
- Merge with main (step 13): `git merge-tree --write-tree origin/main 28f880d6` exits 0 (tree c4c24f0339). The merge base is d08ed31049, the same as origin/main, so the head is 0 behind.
- Resolution delta: `git diff 4ac47e9b5 7d3c52b79 -- dev/governance/roles/fixer.md` is mostly main's #3397/#3341 rewording carried in. Against the merge base, the three-dot diff of `fixer.md` is the one "Before you hand off" paragraph, the union the body describes, with 0 conflict markers.
- Steps 4 and 5: the three-dot diff touches no `VERSION`, manifest, `RELEASE_NOTES.md`, `*_budgets.json`, or claim or golden file.
- Policy checks at the head: `node tools/policy/rules_sync.mjs --check` reports RULES-SYNC ok. `node tools/policy/policy_lint.mjs` reports 0 errors across 50 policy files, and its fixtures pass. Output is in `ev/cheap-checks.txt`.
- Packet at render: `carry_audit` found 0 items, `figure_lint` found 0 figures, and nothing refused.
- Step 7: the body's `## Head` names 28f880d6e709bb6315ec1e2dfafdae46d1570515, the head measured.
- Step 10: the body's `## Forward-carry` is none. The diff's own rule edits (fix-review.md, fixer.md, and the dispatch line) are where this change reaches later seats.
- Approval: these are policy and role-contract edits, so the owner's approving review is still owed before merge, as the body's `## Approval` says. This verdict does not replace it.
- CI (step 11): `merge_train.py classify 28f880d6e709bb6315ec1e2dfafdae46d1570515 --pr 3384` exited 0, `GREEN 28f880d6e709bb6315ec1e2dfafdae46d1570515 pending: none red: none` (`ev/classify.txt`). The commit's check-runs API, paginated, lists no run with conclusion failure at this head, so no red is owed a `## Red checks` answer, and the body's `none` is accurate.
- Step 12: after CI settled, the live PR head re-read as 28f880d6e709bb6315ec1e2dfafdae46d1570515, the head I measured.
