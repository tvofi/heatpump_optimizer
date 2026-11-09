Fix review: merge 09f0b6d9ce030676bd513e77a8b7318b53632b7c

bus-nonce: 50a58d723b2f78338cdee55ce8f92a5f

## Round

Round 4 of review (after blocked b59abf37 and blocked 8f073db7). The body carries a `## Re-cut` section. The delta since 8f073db7 adds test rows and one in-file mutation arm, with no production change: `git diff 8f073db7 09f0b6d9` touches only `_self_test` in `tools/audit/seat/roster_lib.py` and `selftest` in `tools/plan/replan.py`, 17 added lines. The head 09f0b6d9 is a merge whose tree is identical to 2305095d (`git diff --quiet` exit 0), so the body's round-3 proof head and this head are one tree.

## Evidence

- Head measured: 09f0b6d9ce030676bd513e77a8b7318b53632b7c. Before writing this verdict, `git ls-remote` showed it is still the head of `fix/r10-fly-replan-defects`.
- Mutant 1 (prior survivor), `tools/plan/replan.py:905` `open_ = open_ - set(held)`:
  - Null run: `replan.py --self-test` rc=0, `self-test: 0 failed`.
  - Mutant `-> pass`: rc=1, `self-test: 3 failed`. The kill is the new row "deferred: a held dependent is in no wave and no batch", which got `['R10-A','R10-Y','R10-Z']`. The other two failures are the in-file arm's own anchor/null checks, which fail because the mutant removed the line they anchor on.
  - Weakened form `open_ - set(list(held)[:0])`: killed by the same row.
  - Files: `ev/null-replan.tail.txt`, `ev/mut-replan-pass.tail.txt`, `ev/mut-replan-weak.tail.txt`, `ev/rp.res`.
- Mutant 2 (prior survivor), `roster_lib.held_behind_deferred` `elif a in held and gates(G[a]):` -> `elif a in held:`:
  - Null run: rc=0, 76 checks, 0 failed.
  - Mutant: rc=1. FAIL "a held group that is itself released (refuted) does not hold its dependent", got `{'Q': 'P', 'S': 'P'}`.
  - Files: `ev/null-roster.out`, `ev/mut-roster-gates.out`.
- Null control for the roster_lib row: I ran the opposite perturbation, `... and not gates(G[a])`. It turns the `chain` row red, getting `{'Q': 'P'}` (queued Q no longer holds S), so the conjunct is pinned in both directions. File: `ev/mut-roster-inverse.out`.
- Null control for the replan row: its released (`refused`) arm requires R10-Y and R10-Z to be in waves/batches, and its held arm requires R10-A to be in the plan. A plan that schedules nothing therefore does not satisfy it. The unmutated self-test passes.
- Self-tests at head, all 0 failed: `closeout.py` (38 checks), `handover_prompt.py` (20), `orchestrator_tick.py` (283). Files: `ev/st-*.out`.
- Merge with main: `git merge-tree --write-tree origin/main 09f0b6d9` gives rc=0 against origin/main 806e952c. The only resolution is `LEDGER-MERGE: resolved tests/closures.json`. File: `ev/merge-tree.txt`.
- CI: `merge_train.py classify 09f0b6d9 --pr 3326` exited 0: `GREEN 09f0b6d9ce030676bd513e77a8b7318b53632b7c pending: none red: none`. File: `ev/classify.txt`.
- `governance / delivery-status` was red in the packet digest. It grades main, is outside the required set, and is not this PR's.
- Red checks at earlier heads in the branch (closures, closures-autofix, instrument-self-tests, gate) are named and answered in the body's `## Red checks`. Per the role, I checked that an answer exists, not the answer itself.
- Three-dot diff against merge base 20e83746: VERSION, the manifest, RELEASE_NOTES.md, golden/claim files, `*budgets.json` and the mutation ledger are untouched.
- The body names no finder's harness. The prior rounds' reviewer probes (`probe_closeout.py`, `probe_check.py`) cover code this delta did not change, so I did not re-run them. That is not re-verified at this head beyond the self-tests above.
- Figures I did not re-derive here: `ALL 2669 ENTITY CHECKS PASSED`, `prepr.sh --self-test 514 passed` and `STRUCTURE RATCHET PASSED`. CI GREEN at this head stands in for them, per the role's cite-CI's-heavy-runs rule.

## Findings

- Follow-up: the after-edge reads `plan_page.py` `blk`, `orchestrator_tick.py` `blockers` and the `plan_table.py` drawing follow `roster_lib.gates` with no pinning row. The body's Forward-carry dispositions these. Carry: dismissed: display-only, the scheduling and ready-next readers are pinned
