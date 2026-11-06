Fix review: merge 79cf40f4751210c7868d8178b87dc97a69fa28ae

bus-nonce: e15637a3baa3aeb58961244ecf4503e2

Round 3 is a scoped re-check only (orchestrator ruling 14:15Z), at head 79cf40f4751210c7868d8178b87dc97a69fa28ae, the authored code head 71eca598.

Round 2 (probe/rev-3240-768e2f86) blocked this head on CI state alone: the required `gate` was red by cross-run deferral. It settled the code. Since then that gate has been re-run and is green. Nothing else was re-measured, and the round-2 code findings below stand unchanged.

## Findings

- Non-blocking: Surviving mutant `insufficient_not_clearing`: changing `elif not m and arm in tripped:` to `elif not m and arm in tripped and "insufficient" not in ln:` leaves the self-test at 73 checks, 0 failed (`--no-mutants`; ev/mutants.txt). So no case pins the body's claim that an arm is "dispatched again only after it reads `ok` or `insufficient`": the insufficient half is unpinned. The fix is one case (trip, then `insufficient`, then trip again) and its MUTANTS row. Carry: R10-PLANTED-DEFECT-AUDIT
- Non-blocking: `MUTANTS` in beat_jobs_selftest.py has the key `audit_no_memory` twice. The first entry, whose stale round-1 anchor ``if m and f"{m[1]} {m[2]}" not in sent:`` no longer exists in beat_jobs.py, is silently overwritten by the dict literal. So the table holds a dead row that would fail its own anchor check if it were ever reached, and a reader counting rows miscounts. The fix is to delete the first entry. Carry: R10-PLANTED-DEFECT-AUDIT
- Non-blocking: DISPATCH lines never leave the job file. After a trip clears, the line is kept (ev/stale-probe.txt, `recover-ok` and `ok-again`), and each new episode appends another. The fold stamps only new lines, so the orchestrator is not re-woken, but `digest.txt` keeps a done audit as an "actionable" line indefinitely and grows by one line per episode. Measured rate: 3 episodes in 5.4 days (sweep). Expiry by age, or on the arm's clear, would match roster-drain's HOLD-STALE precedent. Carry: R10-PLANTED-DEFECT-AUDIT
- Non-blocking: No hysteresis at the threshold: model:sonnet read P = 0.0526 against ALPHA 0.05 (`ok`) at five hourly cuts on 2026-11-01 between 04:00Z and 08:00Z, then re-tripped at 09:00Z. That gave a second dispatch nine hours after the first, auditing a last-20 window that overlaps the first heavily (ev/sweep-row.txt, ev/cache). This is exactly the owner's ruling and the brief's null control (a clear then a re-trip dispatches again), so it is not a defect; it is recorded for whoever next reads the dispatch rate. Carry: dismissed: within the owner ruling (tvofi 2026-11-01) and the brief's null control; measured 2 model:sonnet dispatches in 5.4 days

## Evidence

- Head: `git ls-remote` gives 79cf40f4751210c7868d8178b87dc97a69fa28ae for both refs/pull/3240/head and refs/heads/fix/r10-planted-defect-audit, so the PR head has not moved since round 2 (ev/HEAD.txt, ev/ls-remote.txt).
- RESULT classify: `python3 tools/audit/seat/merge_train.py classify 79cf40f4751210c7868d8178b87dc97a69fa28ae --pr 3240` prints `GREEN 79cf40f4751210c7868d8178b87dc97a69fa28ae pending: none red: none`, rc=0 (ev/classify.txt).
- Check-run pages: there is 1 page, total_count 68, and every run is completed. Each concluded success or skipped; none concluded failure, cancelled or timed_out (ev/check-runs.txt).
- The round-2 block is cleared:
  - gate 127938952647 (run 42210933789) succeeded at 14:12:35Z-14:13:09Z. It replaces the early-judged 127869785809.
  - gate 127939980463 (run 42211895323) succeeded at 14:13:34Z-14:14:03Z.
  - gate 127880611389 (run 42210933658) succeeded at 12:00:58Z.
- No concluded red goes unnamed. The body's `## Red checks: none` matches the live checks.
- Merge: `git merge-tree --write-tree origin/main 79cf40f4` against origin/main 33e60b5b gives rc=0, tree a99eb53d, no conflict (ev/merge-tree.txt). origin/main has moved since round 2 (7e8939d3), and the merge is still clean.
- Round-2 measurements were not re-taken, per the round-3 scope: self-tests, mutants, sweep, stale probe, entities and structure. They are in probe/rev-3240-768e2f86, and the code is the same patch at the same head.
- The PR body as read at this head is in ev/pr-body.md.
