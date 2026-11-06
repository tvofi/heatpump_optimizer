Fix review: blocked 79cf40f4751210c7868d8178b87dc97a69fa28ae ci-red: required gate red at this head by cross-run deferral (run 42210933789's gate judged early and never re-run); the code settles both round-1 blocks and the surviving mutant

bus-nonce: 768e2f86f6df4349ab240de16bd20bb8

Round 2 (second-round adversarial fix review), head 79cf40f4751210c7868d8178b87dc97a69fa28ae (authored code head 71eca598), merge base dc0a170b, origin/main at review 7e8939d3, three-dot diff. Round-1 verdict: probe/rev-3240-bd1ba3ae (blocked f6a299d3, over-fire). A block now means round 3; this block is CI state only, and the code needs no re-cut (see below).

## Block

1. **The required `gate` context is red at this head and nothing will re-judge it on its own.** `merge_train.py classify 79cf40f4751210c7868d8178b87dc97a69fa28ae --pr 3240` returns `RED ... pending: none red: gate`, rc=1. It read the same at every poll from 11:37Z to 12:57Z and once more at ~13:00Z (ev/classify_log.txt, ev/classify.txt). Cause, from the job logs (ev/ci-gates.txt):
   - The tests workflow run 42210933658 concluded with its own gate green (job 127880611389, success at 12:00:58Z).
   - Run 42210933789's gate (job 127869785809) was judged at 11:34Z, while 42210933658 was still running. It failed with "still being judged; their gate decides" and was never re-run.
   - The refresh run 42211895323 re-ran its gate at 12:01Z (job 127880974302). That gate now defers to 42210933789: "FAIL run(s) [42210933789] at this head are still being judged".
   - Nothing is pending, so the red is stuck. It is a gate-ordering state, not a defect of the diff: every non-gate job at this head concluded success or skipped.
   - The body's `## Red checks: none` is accurate for the code, but the head is not GREEN, and a merge verdict cannot attach to a red head (fix-review step 12: "a red CI never carries").
   - What is owed: re-run gate job 127869785809 in run 42210933789. That is the orchestrator's or hpo-runs' job, not a reviewer's, and I did not re-run CI (step 11). Then re-run gate 127880974302 if it does not follow, and re-classify.
   - On GREEN, every code finding below stands unchanged: the round-3 seat re-takes only classify and does not re-review the patch, since `review_carry.py` keeps the same patch.

## Findings

- Non-blocking: Surviving mutant `insufficient_not_clearing`: changing `elif not m and arm in tripped:` to `elif not m and arm in tripped and "insufficient" not in ln:` leaves the self-test at 73 checks, 0 failed (`--no-mutants`; ev/mutants.txt). So no case pins the body's claim that an arm is "dispatched again only after it reads `ok` or `insufficient`": the insufficient half is unpinned. The fix is one case (trip, then `insufficient`, then trip again) and its MUTANTS row. Carry: R10-PLANTED-DEFECT-AUDIT
- Non-blocking: `MUTANTS` in beat_jobs_selftest.py has the key `audit_no_memory` twice. The first entry, whose stale round-1 anchor ``if m and f"{m[1]} {m[2]}" not in sent:`` no longer exists in beat_jobs.py, is silently overwritten by the dict literal. So the table holds a dead row that would fail its own anchor check if it were ever reached, and a reader counting rows miscounts. The fix is to delete the first entry. Carry: R10-PLANTED-DEFECT-AUDIT
- Non-blocking: DISPATCH lines never leave the job file. After a trip clears, the line is kept (ev/stale-probe.txt, `recover-ok` and `ok-again`), and each new episode appends another. The fold stamps only new lines, so the orchestrator is not re-woken, but `digest.txt` keeps a done audit as an "actionable" line indefinitely and grows by one line per episode. Measured rate: 3 episodes in 5.4 days (sweep). Expiry by age, or on the arm's clear, would match roster-drain's HOLD-STALE precedent. Carry: R10-PLANTED-DEFECT-AUDIT
- Non-blocking: No hysteresis at the threshold: model:sonnet read P = 0.0526 against ALPHA 0.05 (`ok`) at five hourly cuts on 2026-11-01 between 04:00Z and 08:00Z, then re-tripped at 09:00Z. That gave a second dispatch nine hours after the first, auditing a last-20 window that overlaps the first heavily (ev/sweep-row.txt, ev/cache). This is exactly the owner's ruling and the brief's null control (a clear then a re-trip dispatches again), so it is not a defect; it is recorded for whoever next reads the dispatch rate. Carry: dismissed: within the owner ruling (tvofi 2026-11-01) and the brief's null control; measured 2 model:sonnet dispatches in 5.4 days

## Evidence

- Head measured: 79cf40f4751210c7868d8178b87dc97a69fa28ae (ev/HEAD.txt). It was still the PR head and branch tip at verdict time (`git ls-remote`).
- (a) Block 1, sustained trip, is settled. Finder's harness: the round-1 sweep, extended to drive the real `audit_dispatch` with a fresh Ctx per cut, i.e. a process restart per pass.
  - Setup (ev/sweep_cache.sh, ev/sweep_row.py): hourly cuts 2026-11-01T00:00Z..2026-11-06T09:00Z (130), the row's own 60-day window, bus fetched once at 2099 verdicts with 0 outside the grammar (ev/guardrail-live.txt), cached outputs in ev/cache, all 130 runs rc=0.
  - RESULT base f6a299d3: model:sonnet would-trip at 125/130 cuts gives **37 DISPATCH lines**; all at 1/130 gives 1; total 38.
  - RESULT head 79cf40f4: model:sonnet 125/130 gives **2**; all gives 1; total 3 (ev/sweep-row.txt).
  - The second model:sonnet dispatch (cut 10-31T14:51Z..11-01T08:24Z, at 11-01T09:00Z) follows five real `ok` cuts (P = 0.0526), so it is a clear followed by a re-trip, not a slide. That is the null control, live: a trip that clears and re-trips dispatches again. Self-test case `audit-dispatch null: a trip that clears and trips again dispatches again` is green at the head and red under `audit_key_by_span` and `audit_trip_never_clears`.
  - Body figures 38 → 3 re-derived exactly. Beside the round-1 figure of 37 audits for model:sonnet in 5.4 days, it is now 2.
- (b) Block 2, sticky UNREADABLE, is settled. ev/stale_probe.py is the round-1 probe on the real `audit_dispatch`, plus a still-failing null.
  - At the head, after `recover-same-cut` the digest is the DISPATCH line only: UNREADABLE cleared, DISPATCH kept. After `recover-ok` and `ok-again` the UNREADABLE line stays gone and the memory is `[]`.
  - Null at the head: fail, fail-again, fail-third keep `audit-dispatch: UNREADABLE review_strength ...` with the DISPATCH line kept.
  - Baseline f6a299d3: UNREADABLE is stuck after all three recovered passes, reproducing round 1 (ev/stale-probe.txt).
- (c) `unclassified_kept` now dies. Planted by hand in a head worktree (ev/plant.py, `--self-test --no-mutants`, file restored): rc=1, FAIL `audit-dispatch: output whose only GUARDRAIL line is the unclassified one is UNREADABLE`. Null control (an identity edit): rc=0, 73/0.
- The body's other mutants were planted by hand. Each has rc=1, with its named case among the FAILs:
  - audit_trip_any_arm: 6 FAIL incl. the would-trip/ok/insufficient case.
  - audit_no_memory: the repeat null.
  - audit_key_by_span: second-arm/slid-cut and clear-retrip.
  - audit_trip_never_clears: clear-retrip.
  - audit_no_clearing_write: good-after-failed and recover-same-trip.
  - audit_rc_ignored: failed-run-UNREADABLE.
- Extra mutants, each killed: dropping `ctx.remember`; UNREADABLE dropping DISPATCH lines; a readable pass dropping kept lines (ev/mutants.txt). The brief's `audit_key_arm_only` is the round-1 name; at this head arm-only keying is the fix, and its inverse is `audit_key_by_span`, killed.
- Self-tests at head (ev/selftests-head.txt): beat_jobs 124 checks 0 failed, review_strength 116/0, beatd 119/0. At origin/main 7e8939d3, the null control (ev/selftests-main.txt): beat_jobs 107/0, review_strength 116/0, beatd 119/0. Body figures 124/107/116 re-derived.
- entities.py: ALL 2632 ENTITY CHECKS PASSED. structure.py: STRUCTURE RATCHET PASSED (ev/entities-structure.txt). Body figures re-derived. prepr and the gate were not re-run (CI cited, step 11).
- Merge: `git merge-tree --write-tree origin/main 79cf40f4` against origin/main 7e8939d3 gives rc=0, tree 5e30e000, no conflict (ev/merge-tree.txt).
- (5) The three-dot diff (ev/diff3.txt) has 6 files, including dev/programme/delivery/3240.md. custom_components/, VERSION, RELEASE_NOTES.md and both claim files are untouched. There is no budget file and no closures/INERT change, so step 14 has nothing to earn.
- Live guardrail at ~11:40Z (`--fetch --window X=2026-10-01T00:00Z..2026-11-06T12:00Z --guardrail`, rc=0): model:sonnet 0/20, P = 0.0014, would-trip; every other arm ok or insufficient. The TRIP regex matches the live line format (the sweep's DISPATCH lines came from real lines).
- (1) Restart null: each sweep pass constructs a fresh Ctx, i.e. a process restart, and a still-tripped arm wrote no new DISPATCH line across 123 consecutive tripped passes. Self-test `a repeat of the same arm line dispatches nothing and writes no byte` is green.
- (2) Cut key: the memory is now keyed by arm and episode; the printed cut is only a label, so the year-less span no longer matters.
- (3) A failed run is surfaced as UNREADABLE every pass while failing, is retried every 1800 s, and never enters memory (memory is written only after rc=0 with arm lines).
- (4) No cascade: the row runs only review_strength.py, which reads the bus, not the digest, and the row writes only its job file and memory. No seat is launched.
- Carries 13, 48 and 50 (roster handoff/audit-r10-roster at 1e65e7c9) are answered by the one row, and the ruling is recorded in carry-201.json. The carries' wording, "dispatches one audit seat", is narrowed by the brief to a digest line; the brief governs. Forward-carry: none named; the three code findings above carry to this group, R10-PLANTED-DEFECT-AUDIT (in-progress; round 3 is owed for the CI block anyway). R10-ORCH-LEDGER, the beatd job table owner, is done on the roster.
- Review packet rendered at this head; refusals `red-unanswered: gate` and `required-red: gate`, which is Block 1. carry_audit at head: 0 items.
- carry_audit.py check --body <PR body as read> --comments <this verdict> is recorded in ev/carry-audit.txt.
