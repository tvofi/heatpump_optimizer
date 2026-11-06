Fix review: blocked c8c50b9f814c8d959b57d064ef1d7712b3564821 mutation-vacuous: L_import_sha_dropped (ledger._import_log keeps no sha; carry 1's import line is pinned by no self-test)

bus-nonce: 4425b3b07dc737e03e772cba0d4c10f4

Round 1. Measured head c8c50b9f814c8d959b57d064ef1d7712b3564821 (detached worktree), merge base 5421413b54ba1044b8e91e1afd88b41acfc7a753. The role file is current: there is no diff under dev/governance/roles/ between the merge base and origin/main.

## Block

Carry 1 (the roster's second carry: an imported verdict-unposted row nothing can close) is delivered by two production changes. The first is in `ledger._import_log`: the imported row keeps the sha its journal line names (`f[3] if is_sha(f[3]) else "-"`). The second is in `fold`, which closes such a row on a read-back naming that sha. The body names `ledger._import_log` as the change.

The self-test rows for carry 1 (`iv` in ledger.py's self_test) are built with the sha already set, so they bypass `_import_log` entirely. Reviewer mutant: replace `kind, when, sha = "verdict-unposted", f[1], f[3] if is_sha(f[3]) else "-"` with `kind, when, sha = "verdict-unposted", f[1], "-"` (the pre-PR behaviour). The whole closure stays green (ev/mutant-import-sha.txt):
- ledger self-test: 85 checks, 0 failed
- orchestrator_tick self-test: 274 checks, 0 failed
- cloud_relay self-test: 332 checks, 0 failed
- r10_ledger_mutants self-test: 146 checks, 0 failed

Under that mutant, a row migrated from a log OWED line still carries sha `-`. The new fold arm (`named` requires `sha != "-"`) then never fires, and the defect the carry names survives in production. The `fold` half is pinned: L33 is killed. The `_import_log` half, which is the half that makes a migrated row closable at all, is not.

Repair: add a self-test that imports a log OWED line `... verdict-unposted <pr> <sha>` through `_import_log` (or `main` / the migration path), then folds it against a read-back naming that sha and expects it closed. Add a plant for this line to r10_ledger_mutants.py.

## Findings

- Carry 2 (aging keyed on arrivals) silences every stranded handoff committed at or before the newest fix/ or handoff/ opening, whatever topic that opening belongs to. One unrelated PR opening resets the alarm for the whole backlog. That is the carry's own design ("as pulse.py does"), and the self-tests pin it, but the body does not state this consequence. Carry: dismissed: within the carry's stated design; noted for the next ledger owner, not a defect of this PR
- The carry-2 re-measurements the roster carry asks for were not taken by the fixer (no gh in its seat), and could not be taken by this reviewer either: gh here fails auth, and pulse_replay plus a live `bus.sh orphans --min-age-h 24` need it. These are the 123/153 STOPPED replay and the count of orphans older than the newest opening. The body discloses the gap. Carry: R10-LEDGER-RESIDUE

## Evidence

- RESULT: self-tests at the head: ledger 85/0, orchestrator_tick 274/0, bus 135/0, r10_ledger_mutants 146/0. structure.py: STRUCTURE RATCHET PASSED. All match the body's figures (ev/selftests-head.txt, ev/mutants-head.txt).
- RESULT: plants L32, L33, L34, B4, L3 and T4 are all KILLED, each failing the check the body names (ev/mutants-head.txt). A reviewer mutant, `last_open = None` in Tick.relay_owed, is KILLED by 2 relay OWED checks.
- RESULT: carry 0 (the cloud_relay-8 plant) needs no change at this base. The pattern occurs once in cloud_relay.sh, and `r10_seat_selftests_mutants.py cloud_relay-8` gives KILLED, survivors=0 (ev/cloud_relay8-head.txt).
- RESULT: carries 3 and 4 land as their roster text specifies, each with a null control.
- `git merge-tree --write-tree origin/main c8c50b9f814c8d959b57d064ef1d7712b3564821`: clean, no conflict.
- The three-dot diff touches 5 files: bus.sh, ledger.py, orchestrator_tick.py, r10_ledger_mutants.py, and the delivery row dev/programme/delivery/3248.md. VERSION, the manifest, RELEASE_NOTES.md, custom_components/ and every *_budgets.json are untouched.
- CI: merge_train classify read RED (gate) at 12:31 and 12:36Z, with WAIT between (ev/classify.txt). Both gate runs (127892275620, 127895068836) logged "FAIL run(s) [42217622995] at this head are still being judged; their gate decides". That is an ordering artifact, not a test failure, so no root-cause trigger is judged here. CI had not concluded when this verdict was written. The block above does not depend on it.
- The packet's figure_lint resolved 6/6. The finder's harness for this instrument group is the roster carries' own controls; no separate finder harness is named.
