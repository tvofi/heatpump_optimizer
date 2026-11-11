# R9-RCA-TRAIN-SILENT-LAUNCH: a healthy daemonized train read as dead

**Trigger event.** 2026-10-14 00:03–00:12 local: a `traintest` batch launch
ran 8+ minutes with the process alive and a log holding only the wrapper's
launch line; it was killed as dead. No release, no red check — this entry is
recorded as the second instance of the instrument-wait/silence family
`R9-RCA-TRAIN-WEDGE.md` §6 named, on the recurring-error clause, not on an
enforcement trigger.

**Named cause (reproduced).** (c) buffered output with a real wait behind it.
The wrapper's `dup2` made stdout a file; Python block-buffers a file; the
beats existed but sat in the 8 KB buffer the SIGKILL dropped. The probe at
main `981a45802` timed the early path (git fetch 2.0 s, `required()` 0.9 s,
first poll 3.6 s) and caught the train mid-`main_green` — a healthy FULL run
in progress. Secondary, state (c) again: `POLL_SECONDS` (300) gated the
first beat behind `HEARTBEAT_SECONDS` (240), so even unbuffered the log was
blank for 5 minutes.

**Cost test.** Countermeasure = three one-liners in `tools/audit/seat/merge_train.py`
(#2180): line-buffered stdout at entry, a t+0 banner, poll sleeps bounded by
the heartbeat. Standing cost ≈ 0 (same code paths). Defect cost = one lost
batch run per occurrence plus the orchestrator's misread-and-kill;
P(recurrence) = every future daemonized launch, the wrapper shape is the
standard one. Pays.

**Countermeasure demonstrated.** Three mutation arms, each reddened by
reverting exactly its own fix (138 checks, 1 failed each; restored: 0), plus
a rehearsal under the incident's byte-identical wrapper shape legible at
t+15 s, and a forced-wait run with beats sampled in real time at t+241 s and
t+481 s (the old code's first beat: t+305 s, measured). All figures in
#2180's body.
