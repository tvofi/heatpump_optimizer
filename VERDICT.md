Fix review: blocked 0c55662763813cee343d86278f94f90bc3e193a6 mutation-vacuous: M4 record_drafts call site deleted, M7 pending set ignored, M8 zero-time not cleared, M9 startedAt fallback dropped

bus-nonce: a5daae798dbad468e12c1be6f790b6c0

Round 1, a handoff review: no pull request yet, so there is no review packet and no CI to read. Measured at handoff tip 0c55662763813cee343d86278f94f90bc3e193a6 on merge base ee64358be7eeccaec5178a923cb3b83a18a924a0 (= origin/main at review time).

## Block

- **M4 survives, and it is the fix itself on the `--queue` route.** Replacing `self.record_drafts(queue)` in the batch (merge_train.py:4060) with `pass` leaves `--self-test` at 619 checks, 0 failed. P609 calls `t.record_drafts(q)` directly, so nothing checks that a batch records the draft key. Without that call, a `--queue` or `build_queue` draft still never gets `item["draft"]`. Each such PR is then stopped as "drafted after admission: left as a hold" when it should be undrafted, which is the #3425 shape left unfixed. The roster brief (carry 18) asks for exactly this test: "--queue entry without draft on a draft PR -> one UNDRAFT then merge; mutation proof: removing the admission read fails case 1". The body's mutant (the read inside `record_drafts` -> `pass`) is killed, but only because the unit test raises a KeyError. That does not pin the route. Owed: a self-test that drives a batch (or the code path the batch calls) with a key-less draft entry and asserts one `gh pr ready` and then the merge.
- **M7 survives: the pending set in `rollup_states` is unpinned.** Replacing `pending.add(name)` with `pass` passes. The case "[SUCCESS 09:00, IN_PROGRESS 10:29] -> wait" passes only because the IN_PROGRESS entry is also the newest, so newest-wins already gives a non-green state. Owed: a case where the unfinished entry is not the newest, e.g. an IN_PROGRESS entry with zero-time completedAt and an older startedAt beside a newer SUCCESS. That case must read PENDING.
- **M8 survives** (the "0001" zero-time stamp is not cleared) and **M9 survives** (the `startedAt` fallback is dropped). No fixture holds a zero-time `completedAt` or an entry with only `startedAt`. Both lines are written for GitHub's live shapes, and no test exercises them.

## Findings

- Residual: newest-wins (the P608 brief's rule) still reads a context green when an older entry is red and a newer one green. ev/rollup_probe.txt shows the P567 #3405 shape (deferral FAILUREs older, code-gate SUCCESS newest) reads gate SUCCESS in both orders. policy_refusal therefore still prints "the missing requirement is a review" there, while P567 measured GitHub blocking on any red gate entry. This is not a regression: the merge base's last-listed rule gave the same reading in that order. The same group's carry 14 (P567 fix 2) asks for any-red, which would also have passed every P608 case, so the later part must replace `rollup_states`' red rule. Carry: dismissed: already on the roster as R10-TRAIN-RESIDUE-P2 carry 14 (P567, triage s6-batch155.md#P567, fix 2), which states the any-red rule and its control

## Evidence

- Self-test at the head: `python3 tools/audit/seat/merge_train.py --self-test` rc=0, "619 checks, 0 failed"; the 9 P608/P609 lines print ok, which matches the body's figure (ev/selftest-head.txt).
- The mutation proof was re-run with my own driver (ev/mut_driver.py, output in ev/mutants.txt), 13 mutants, each through the full `--self-test`. Killed with a named FAIL line: M1 (the body's last-listed mutant), M2 (the body's `if False`), M3, M6, M11, M13. Killed only by a crash: M5 (the body's read -> pass, KeyError 'draft', as the body says) and M12 (KeyError). M10 crashed on a malformed replacement of mine (KeyError 'fast'), so it is inconclusive. Survivors: M4, M7, M8, M9 (see Block).
- Null control (body): the all-SUCCESS case in either order reaches the review branch, and a non-draft entry makes no `gh pr ready` call; both print ok at the head. The body's "no last[name]= overwrite and no still-a-draft arm at the merge base" was confirmed from `git diff ee64358b 0c55662763813cee343d86278f94f90bc3e193a6`.
- Merge: `git merge-tree --write-tree origin/main 0c55662763813cee343d86278f94f90bc3e193a6` exits 0 with tree f96f62116b0b4165a7e2ef14bcd2aba53355ff46, the same tree as the body's `Prepr:` trailer (ev/merge-tree.txt).
- The head named in the body equals the handoff tip; handoff/r10-train-residue-p2 is still at 0c55662763813cee343d86278f94f90bc3e193a6 when this verdict is written.
- The diff touches only tools/audit/seat/merge_train.py: no change to VERSION, the manifest, release notes, claim files or golden fixtures, so env_drift has nothing to compare.
- `tests/structure.py` at the head: rc=0, STRUCTURE RATCHET PASSED (ev/structure-head.txt).
- Roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Carries 17/18 checked against handoff/audit-r10-roster fbf10ee949 (wave-r10-groups.json, R10-TRAIN-RESIDUE-P2 carries 16/17 counted from 0). Carries 1-16 stay on the roster as the body says. Moving the draft read out of `preflight` to batch start is explained in the body (`preflight` returns early without `--pre-flight`), and it is sound.
- Class sweep: the other `statusCheckRollup` reader, `platform_gate` (merge_train.py:466), already applies GitHub's any-red rule over the required gate runs, so it is not a list-order seam. The body names no enumeration rule; the issue is two named seams, and each is in the diff.
- Red checks: there is no pull request, so no checks exist; the owed-reds set (23 names) is in ev/owed-reds.txt. Nothing red is owed an answer.
- Not re-derived: the body's prepr.sh rc=0 under PREPR_SKIP_CLOSURES (heavy, CI's job); the roster's #3445 counts (78 attempts over 8 PRs) come from the orchestrator's train.log, which is not in the tree.
