Fix review: merge a7bb3ec346e83558dc601959430534f8bdb095a1

bus-nonce: c09aec3a183a743b57a84b2248dd16bd

Round 2, the delta review after my round-1 block at 1c9c0bdf3. Measured head a7bb3ec346e83558dc601959430534f8bdb095a1: code head f8e44e97385bf309f4471d04649b232ac0985ce7, then two main merges, fe81e7a5f and a7bb3ec34. Between f8e44e973 and the head the diff touches nothing under tools/ or .github/. The merge base is 017045fef. The PR's headRefOid was still a7bb3ec346e83558dc601959430534f8bdb095a1 when this verdict was posted, and the body's ## Head names f8e44e973 as the code head.

## Both round-1 blocks are answered

1. MAIN arm pinned. My M4, replacing the MAIN-arm call with `waiting = []`, now gives 100 checks, 1 failed (`MAIN needs-gated job`). It gave 93/0 at round 1.
2. MAIN arm bounded. The round-1 stuck_probe (main, `mutation` in progress for 10 h, `closures` never queued) now prints `required contexts ABSENT: closures`, flagged, with no WAITING line. At 1c9c0bdf3 it printed WAITING and nothing was flagged.

## RESULT lines

- RESULT self-test head, seat-python 3.14.7 with -W error: 100 checks, 0 failed (rc 0)
- RESULT M1 (`status != completed` replaced by False): 3 failed. Killed.
- RESULT M3 (PRS-arm call removed): 1 failed. Killed.
- RESULT M4 (MAIN-arm call removed): 1 failed. Killed.
- RESULT M5 (`not self.stuck(...)` replaced by True): 5 failed. Killed.
- RESULT M6 (`med is not None` guard removed): the self-test raises TypeError, rc 1. Killed.
- RESULT M7 (threshold 20x): 5 failed. Killed.
- RESULT M8 (threshold 5x): 100 checks, 0 failed. **Survives.** See note 1.
- RESULT absent_probe, the same 8 cases on both arms:
  - Unrelated lane in flight (fresh), closures never queued: WAITING. This is now bounded at 2x the median.
  - Everything settled: ABSENT, flagged.
  - Needs-gated, coverage queued: WAITING.
  - closures itself queued: neither.
- RESULT bound_probe, against the live median at the checkout (54.825):
  - Sibling in flight 100 min: WAITING.
  - Sibling in flight 115 min, a legitimately slow needs-gated sibling: ABSENT.
  - Stale low median 10, sibling at 30 min: ABSENT.
  - Stale high median 600, sibling at 10 h: WAITING.
  - Median 0: ABSENT.
  - Queued run with started_at null or missing: WAITING. See note 2.
- RESULT ETA lane reader (`critical_median` against the old inline read) gives the same readable/unreadable truthiness on all 5 inputs: 54.8, 0, {}, not-json and null. The only change is that 0 now returns None instead of 0, and both read as unreadable under `if not med`. A string median or a list-shaped JSON raises at both the old and the new reader (pre-existing; the old ETA expression had the same shape). The ETA lane is not regressed.
- RESULT VERSION, manifest and RELEASE_NOTES: 0 diff lines, three-dot from 017045fef
- RESULT merge-tree, origin/main 0b1ddb7fd against the head: rc 0
- RESULT CI at head, after all runs concluded: 45 check runs, 42 names. Latest per name: 27 success, 15 skipped, 0 red. Among them: mutation 117544946868, coverage 117545005167, closures 117547183093, fast (3.14) 117545005217, composed-proof 117551947965 and pr-contract 117545010371, all success.
- RESULT reds at f8e44e973 and fe81e7a5f: none. The body's "Red checks: none" stands.
- structure, archscore and closure-select figures in the body: not re-derived (CI's). The ratchet lanes at head are green.

## Attacks on the bound (none blocking)

- **A legitimately slow needs-gated sibling** (coverage past 2x median, about 110 min) reads ABSENT. On the PRS arm the lane-pending check flags that same lane too. This is no worse than the base, which read ABSENT at minute 0.
- **A stale or wrong median.** The median is read from the orchestrator's local checkout, not from origin/main. If it is low, ABSENT fires early, which is the base behaviour. If it is high, ABSENT is hidden for longer, but still for a bounded time.

## Notes (not blocking; the fixer's call)

1. **The 2x threshold appears twice and only one copy is pinned.** `Tick.stuck` (line 329) and the ETA lane (line 1571) each spell `2 * med`. The ETA lane does not call `stuck()`, so the "ETA check's own threshold" is a duplicated literal rather than a shared one. M8 shows the value is not pinned, because the stuck case sits at 10 h against 122 min. One follow-up fixes both: have the ETA lane call `self.stuck`, and add a case just past 2x.
2. **An in-flight run with no started_at never reads stuck**, so WAITING has no time limit there. The old ETA lane skipped such runs the same way. The GitHub API allows a null started_at, but all 18 non-completed check runs I read live across open-PR heads and main had one set. I record this as a gap, not a defect.

Probes absent_probe.py, stuck_probe.py and bound_probe.py are mine; the finding has no committed harness beyond --self-test. They are in the evidence dir.
