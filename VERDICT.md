Fix review: merge edf1cba7cda43790435d1d4b5aa1b3b24562912a

bus-nonce: 57aa64bf0c3eba88c4f02fccf7372f7a

## Summary

Round 1 of review for #2995 (R10-FLY-GH-READ-RETRY carry 7). I measured head edf1cba7cda43790435d1d4b5aa1b3b24562912a, which is still the branch tip (ls-remote). The roles diff is empty against main, so the contract is current. `ghapi.get` now retries a TRANSPORT failure (URLError, HTTPException, ConnectionError, TimeoutError) on RETRY_5XX's backoffs, the same as a 5xx, and raises the last failure once the budget is spent. A POST is still never retried, and a non-transport exception still raises at once. TRANSPORT matches `gh_read.urllib_wait`'s set (tools/audit/seat/gh_read.py:132) member for member.

## Findings

- No committed finder's harness exists for #2859. The packet reads "Finder's harness: none named". The original failure is a one-time CI transport flake: prelude run 40292248220, IncompleteRead. The only instrument is the fixer's fake-transport arms in `ghapi.py --self-test`, and they are disclosed as the fixer's own. I measured with those arms, re-run under a null control at the base (8 FAIL) against the head (0 FAIL). Carry: dismissed: a non-reproducible network flake has no live harness to commit; the in-tree fake-transport self-test arms plus mutants ghapi-4..10 are the standing instrument
- `tools/release/stamp.py` `get_rest` is an unretried GitHub REST read: the class's seam outside this diff. The carry is on the roster at 5a8c3e6434a4b14a576bac280319b02086849d66, which is an ancestor of origin/handoff/audit-r10-roster. The carry states its control (the urlopen enumerator returns record_row.py's guarded read) and asks for a re-run at that group's merge base. Carry: R10-FLY-STAMP-CHECK-NOTES
- `dev/audit/harnesses/r10_main_gate_replay.py`:29 is an urlopen read with no retry. It is the one-shot replay harness of a finished group, and no live roster group owns it. Carry: dismissed: one-shot replay harness of a finished group, no live destination (as dispositioned in the body)

## Evidence

- RESULT selftest: `python3 -I tools/ci/ghapi.py --self-test` prints `ghapi self-test: 32 checks, 0 failed` at the head and `19 checks, 0 failed` at merge base e77418f9b. ghapi.py is identical at 507a9ec26 and e77418f9b. (ev/selftest.txt, ev/null_control.txt)
- RESULT null-control: splicing the base `get` under the head's self_test prints `32 checks, 8 failed`. The 8 are exactly the transient and persists arms of the four failures, which matches the body. (ev/null_control.txt)
- RESULT mutants: `r10_seat_selftests_mutants.py ghapi-1..ghapi-10` killed all 10, `RESULT survivors=0`. Fail counts: ghapi-4 8, ghapi-5..8 2 each, ghapi-9 4, ghapi-10 12, all as the body states. (ev/mutants.txt)
- RESULT own-mutants: I planted 5 mutants of my own and all were killed. Broadening the arm to `except Exception` is killed by the ValueError null control. Adding a 4th try is killed by the persists arms (4 vs 3). Making a 5xx never retried is killed by the 502 arms. Adding Exception to TRANSPORT is killed by the null control. Dropping `or nap is None` is killed by a TypeError crash (rc=1) in "a 5xx that persists is returned", not by a named FAIL. That is still a kill and is not owed anything. The tree was restored after each. (ev/own_mutants.txt)
- Class rule: I re-ran `git grep -n "urlopen(" -- tools dev/audit/harnesses .github` at the head. It returns 7 hits, and each one matches the body's disposition. A wider probe (HTTPSConnection, requests, http.client.HTTP) found no further opener. (ev/enumerator.txt)
- Merge: `git merge-tree --write-tree origin/main edf1cba7cda43790435d1d4b5aa1b3b24562912a` (origin/main d99cadb12) exited 0 with no conflict and no MERGE-CLAIM line. (ev/merge_tree.txt)
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden/ are untouched in the three-dot diff. `env_drift.py --claims-only <merge-base>` prints "claims hygiene: ... ok". Against the newer origin/main, the inherited non-empty claim lists are main's newer stamp, not this branch's: the three-dot diff on both claim files is empty. (ev/version_untouched.txt, ev/claims.txt)
- Figures I re-derived at the head: closure select reads `MODE: FULL`, reason "tools/ci/ghapi.py changes the gate itself". `archscore --diff 507a9ec26` reads `Architecture score: dS +0.0000 NULL`. No budget, ledger, closures.json or INERT file moves. (ev/closure_select.txt, ev/archscore.txt)
- CI at the head, read live: all 55 check runs completed with success or skipped and none went red. The gate is success in both runs, and pr-contract 124134694531 went green after the last run concluded. "Red checks: none" is accurate, so no root-cause answer is owed. (ev/checks.txt)
- Head: the body names edf1cba7cda43790435d1d4b5aa1b3b24562912a, and review_carry.py reads CARRY at the branch tip. The commit after code head 0c66226e6 is a main merge plus this PR's own delivery row.
- I did not re-run the full gate or the mutation table, per fix-review step 11. I cite CI's runs instead.
