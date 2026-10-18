Fix review: blocked 1c9c0bdf39e2383880243125dfd54e30b93ae1c6 test-vacuous: the MAIN-arm split_absent call is deletable with self-test 93/0, and on MAIN it hides a real ABSENT under a stuck run

bus-nonce: f66c6b8f02e63f72670f98e238fe0bd1

Round 1. Measured head 1c9c0bdf39e2383880243125dfd54e30b93ae1c6 (code head a53ec398537e4f9d68671e91402e95801ef7268c; 799bf9c60 is a clean main merge, and the last commit adds only dev/programme/delivery/2360.md). The PR's headRefOid was still 1c9c0bdf39e2383880243125dfd54e30b93ae1c6 when this verdict was posted.

## Blocking

1. **The MAIN arm has no test, so mutant M4 survives.** The body says split_absent "is applied in both places that said ABSENT, the PRS arm and the MAIN arm". I replaced the MAIN-arm line `waiting, absent = self.split_absent(absent, latest)` with `waiting = []`, and `--self-test` printed `93 checks, 0 failed` (rc 0). Every new case drives either `one_pr` or `split_absent` directly, and none drives `main()`. The group carry says each fix "carries a self-test case that fails at the merge base". Half of arm (a) has no such case.
2. **On MAIN the new rule hides a real ABSENT for as long as any run stays in flight, and nothing else flags that.** The PRS arm has a backstop: `_pending` flags a lane pending more than 2x critical_path_minutes. The MAIN arm records no pending runs and discards judge's running list. Probe stuck_probe.py set up main with `tests` green, `mutation` in_progress for 10h, and `closures` never queued. Base flagged `required contexts ABSENT: closures`. Head prints `WAITING ... closures` unflagged and then `main aaaaaaaaaaaa green`. Nothing on that path is flagged. Fix: add a MAIN self-test case (it fixes 1). Then either bound WAITING, for example by flagging when the oldest in-flight run's started_at is older than 2x critical_path_minutes, which is the PRS arm's own threshold, or put the MAIN arm's running lanes into the same pending check.

## The named concern (WAITING keyed on any run at the sha)

The probe (absent_probe.py, built by this reviewer; the finding has no committed harness) printed:
- Case A, an unrelated lane in flight while closures was never queued. Base: ABSENT, flagged, on both arms. Head: WAITING, unflagged, on both arms. So while any run is in flight, a truly missing context is hidden, and check-runs alone cannot tell it apart from case C. On the PRS arm the hiding is bounded: the unrelated lane eventually settles, or `_pending` flags it. On MAIN it is not bounded (blocking item 2).
- Case B, everything settled with closures missing: ABSENT, flagged, at both ends on both arms. The null control holds.
- Case C, a needs-gated job (coverage queued, closures with no run). Base: ABSENT, flagged. Head: WAITING, unflagged. This is the intended fix and holds on both arms.
- Case D, closures itself queued, so it has a check run: neither WAITING nor ABSENT, at both ends.
- Both arms use the same predicate (`Tick.split_absent`). I found no third ABSENT site in the file; the only computations of `not in latest` are at the two arms.
- Keying on the missing job's own status is not possible from check-runs, because a needs-gated job has no check run to read. This head shows the shape: coverage started 23:08:42Z and closures 23:29:09Z. So I do not block on the proxy itself, only on its unbounded, untested MAIN path. A tighter proxy, counting only in-flight runs from the missing context's own check suite or workflow, is the fixer's call.

## RESULT lines

- RESULT self-test base bad6f7a51: 88 checks, 0 failed (rc 0). Under -W always the SyntaxWarning for "\+" at line 1440 prints.
- RESULT self-test head: 93 checks, 0 failed (rc 0)
- RESULT M1 (inflight = False): 93 checks, 3 failed. The failures are PRS needs-gated x2 and split_absent in-flight. Killed.
- RESULT M2 (non-raw grep literal): 93 checks, 1 failed (compile clean). Killed.
- RESULT M3 (PRS-arm call removed): 93 checks, 2 failed. Killed.
- RESULT M4 (MAIN-arm call removed): 93 checks, 0 failed. **Survives.**
- RESULT arm (c): the head compiles clean under `seat-python -W error` (3.14.7), and the base raises SyntaxError there. `'#[0-9]\+' == r'#[0-9]\+'` is True, so the value is unchanged.
- RESULT VERSION, manifest and RELEASE_NOTES: 0 diff lines, three-dot from the merge base
- RESULT merge-tree origin/main vs head: rc 0, no conflict
- RESULT CI at head: 45 check runs, 42 names. Latest per name: 27 success, 15 skipped, 0 red. Among them: mutation success (117528578667), coverage success, closures success (117532509445), pr-contract success.
- RESULT earlier heads: 1cfb66ed5 and a53ec3985 had no reds. 799bf9c60 had 11 cancelled runs, superseded by the record commit, none concluded failure. The body's "Red checks: none" stands.
- archscore and structure figures quoted in the body: not re-derived (heavy/CI); the CI ratchet lanes at head are green.

## Not blocking

The tests.yml ROSTER_REF comment is accurate. roster_lib.roster_path (roster_lib.py:78) picks the newest ROSTERS_DIR/wave-r<N>-groups.json, and record_row.py's --roster-ref resolves through it (record_row.py:18 and 800). That path is code-owned, so tvofi's review is still owed. Headings in the PR body other than Head, Mutation proof, Null control and Red checks were not re-derived.
