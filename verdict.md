Fix review: merge a101717e588108b4520bb935f59a22fdab31f85f

bus-nonce: c3a9e66dc3fb7b3517ddd814b215a9ac

Round 2 of 3. I measured PR head a101717e588108b4520bb935f59a22fdab31f85f from a detached worktree; its code head is 3279fe67192b1f5ac8089667d32fa68d3951cf28. The merge base is b36679ceaa65a08a67a84f0d934c93aa15f7c7f3. The role file is current: there is no diff under dev/governance/roles/ between the merge base and origin/main.

## Findings

- The carry-2 re-measurements were not taken, by the fixer or by this reviewer: the `dev/audit/harnesses/pulse_replay.py` replay and the live `bus.sh orphans --min-age-h 24` backlog count both need an authenticated `gh`, which neither cloud seat has. The body states the gap under `## Null control`, as the brief allows ("stated or measured"). The live figures are still owed after the merge, by a seat that has `gh`. Carry: R10-LEDGER-RESIDUE

## Evidence

- RESULT: round 1's block is settled. Reviewer mutant L_import_sha_dropped (the round-1 finder mutant: `f[3] if is_sha(f[3]) else "-"` becomes `"-"` in `ledger._import_log`) applied by hand at the head: ledger self-test 87 checks, 1 failed, and the failing check is "a log OWED line imported through _import_log keeps its sha and a read-back naming it closes it (carry 1)". Restored, the head reads 87/0 (ev/mutant-import-sha.txt).
- RESULT: null control at the base. At b36679ce, `_import_log` already drops the sha (line 290, `"-"`), the new check is absent, and the self-test reads 77/0: the hole was unpinned there. With the base's line put back in the head's file, the new check fails 87/1. The test's own null control, "the imported row stays open on a read-back of another sha", passes at the head.
- RESULT: plant L35_import_sha_dropped is in r10_ledger_mutants.py and is KILLED, failing that check. L33, L32, L34 and B4 are all KILLED, each failing the check the body names; L33 now also fails the new check (ev/mutants-head.txt).
- RESULT: self-tests at the head: ledger 87/0, orchestrator_tick 274/0, bus 135/0, r10_ledger_mutants 149/0. structure.py: STRUCTURE RATCHET PASSED. Every figure matches the body (ev/selftests-head.txt). At the base, ledger reads 77/0 and r10_ledger_mutants 135/0, and both deltas are this PR's new checks. I did not re-run `prepr.sh rc=0`; I cite CI's gate instead (heavy runs are cited, never re-run).
- The round-1 note on the carry-2 consequence (one unrelated opening silences the older backlog) is now stated in the body's `## Carry 2 consequence`.
- CI: `merge_train.py classify` read `GREEN a101717e588108b4520bb935f59a22fdab31f85f pending: none red: none`, rc=0, at 14:36Z (ev/classify.txt). I read all 68 check runs at the head on one page, all concluded: none failed, and none was cancelled or timed out. `## Red checks: none` is therefore correct. pr-contract / pr-contract 127945049366 is green (14:24Z), and gate is green (127949503809 at 14:32Z, with two earlier gate runs also green).
- `git merge-tree --write-tree origin/main(33e60b5b) HEAD` gives rc=0 with no conflict (ev/repo-checks.txt).
- The three-dot diff touches 5 files: bus.sh, ledger.py, orchestrator_tick.py, r10_ledger_mutants.py, and the delivery row dev/programme/delivery/3248.md (present, **open**). VERSION, the manifest, RELEASE_NOTES.md, custom_components/ and every *_budgets.json are untouched.
- Carries 0, 2, 3 and 4 were verified in round 1 at c8c50b9f. Round 2 changes only ledger.py's self-test and one plant line (c8c50b9f..6850bc07); the rest is main merges, so those results stand.
- Packet: no refusals; figure_lint resolved 6/6; carry_audit at the head found 0 items (ev/review-packet.md).
- carry_audit check at rc 0 (ev/carry_audit.txt). The PR body was audited by the packet's own carry_audit at the head (0 items), so the body file passed here was empty.
