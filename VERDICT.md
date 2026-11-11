Fix review: blocked b6c080dbcc6cd2294e3ae0913a2c818670749566 harness-vacuous: carry 7 (PREPR-SLOT-LIVELOCK) dismissal rests on a null control that cannot fail

bus-nonce: cb2a5e8b41a5c01c8ec9bdd7842b8c54

Round 1. Head measured: b6c080dbcc6cd2294e3ae0913a2c818670749566 (ev/HEAD.txt). No pull request and no CI exist yet; no review packet.

## Block

Carry 7 is dismissed "not reproduced" from prepr_slot_nested.py, and that harness cannot reproduce or exclude the livelock:

1. The bare control is vacuous. My own bare run (ev/bare.py, pool 4/4 held, no HPO_SLOT_LABEL) printed 61 ordinary self-test rows in 40 s and zero "heavy slot" lines (ev/bare.out): it was not queueing, it was just slow. The labelled run needs 380 s, so `bare_finished=0` at a 40 s bound is the same outcome with or without a slot queue. The labelled and bare runs are indistinguishable by the harness's metrics.
2. `labelled_queued=0` is trivially 0: `queued` is true only when a slot line exists and lacks "joined"; `labelled_real_slot_lines=0`, so no slot line exists to grade. `prepr.sh --self-test` takes the self-test branch (prepr.sh:1876) and never reaches `take_slot`; the nested self-test touches no slot in either arm.
3. The harness injects `HPO_SLOT_LABEL=outer` itself, so it never exercises the thing the carry asks about: where an outer prepr's step 3h loses the label. Step 3h (prepr.sh:4366-4367) calls `take_slot` then `heavy_run ... --self-test`; the label is exported only on the successful-take path (:4184), and the WARN path (:4192) exports none. A real outer prepr holding a slot and running 3h, with the pool full, is untested.
4. The roster carry's own failing test (outer prepr holding a slot runs its nested --self-test with every slot taken and completes; null: bare nested run still takes a slot) was not built. Null control owed: a bare arm that demonstrably differs (a slot line or a queue entry in slot-status), and an arm driven through a real outer prepr step 3h.

Reruns at the head reproduce the body's figures (ev/harness.out: labelled_rc=0, labelled_real_slot_lines=0, labelled_queued=0 in 380 s, bare_finished=0, direct_take_finished=0), so the figures are true but do not support the dismissal.

## Evidence

- Carry 4 (roster index 5, .gitignore): mutation re-run: reverting `/config/` to `config/` fails tests/gitignore_config.py (rc 1, dev/audit/config/x and dev/governance/config/x ignored; ev/gitignore_mutant.txt); head passes rc 0 (ev/gitignore_head.txt). Null control (root config/x still ignored) is in the test and passes. Both nested config dirs are tracked.
- Carry bookkeeping against wave-r10-groups.json at origin/handoff/audit-r10-roster: R10-PREPR-RESIDUE carry list has the .gitignore text at 0-based index 4 (1-based 5, landed) and PREPR-SLOT-LIVELOCK at 0-based 6 (1-based 7, dismissed); the body's numbering is consistent.
- VERSION and RELEASE_NOTES.md untouched (three-dot diff empty).
- Merge: `git merge-tree --write-tree origin/main b6c080dbcc6cd2294e3ae0913a2c818670749566` exit 0, tests/closures.json resolved by the ledger driver (LEDGER-MERGE: resolved); no conflict.
- tests/closures.json additions are the two new files' entries only; not re-derived by me (the closure recorder was not re-run).
- Red checks: none exist for this unopened head; body says none. owed-reds not consulted because no check ran.
- Not re-derived: the body's "PRE-PR rc=0" run (heavy, not re-run).

## Findings

- Follow-up: carry 7's harness needs a discriminating bare arm and a real outer-prepr step 3h arm; until then PREPR-SLOT-LIVELOCK is undismissed and stays open. Carry: R10-PREPR-RESIDUE
