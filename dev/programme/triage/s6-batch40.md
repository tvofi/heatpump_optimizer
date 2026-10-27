# Proposal triage, session s7, batch 40 (P211)

One entry, the first from `proposals.md` since V123: V124, relayed by the orchestrator at
2026-10-27T18:53Z. Facts read at origin/main `6eb552157`; roster at
`origin/handoff/audit-r10-roster` `32b938f3e` (212 groups).

## P211: the push-stuck guard's threshold sits below the work it is guarding (V131)

Verdict: ACCEPT narrowed -> a carry of **R10-UPDATE-PR-SIGNALS** (`resume.stage` `done`, so the
roster op reopens it first, the P196/P208 route; it names both `tools/audit/seat/cloud_relay.sh`
and `tools/audit/seat/pr_args.sh`, and its brief is exactly the seam: deterministic arms, a
condition rather than a fixed window, and the `ps` dependency of the lock holder). The proposal's
first arm (sample the push's process-tree CPU advance instead of elapsed time alone) is the one
carried. Its second arm -- raise the threshold above the measured gate cost, and stop
`gate_lock`'s lease being shorter than the gate it protects -- is REJECTED twice over: a prepr
takes a **pool slot**, not the exclusive lease, and a slot is held for the life of the run, not
its lease (`tests/gate_lock.py:53-56`: "under load a prepr routinely runs past `LEASE_SECONDS`
and expiry-stealing admitted a fifth while the first still ran"); the exclusive lease covers only
the machine-measuring commands, recorded at 936.3 s and 241.1 s, both under `LEASE_SECONDS`
(1800). The lease is therefore not shorter than the gate it protects, because it does not
protect it.

Source: `proposals.md` V124 (orchestrator s7, 2026-10-27T18:53Z); not yet ruled before this
entry.

Instances: the class is an `OWED ... push-stuck` line raised on a healthy push.
- (1) #2876 pid 85023 was raised at 2,295 s and finished normally at `HEAD=d08647f0513a`; #2854
  pid 55046 was raised at 1,919 s while its whole process tree advanced +3.4 s of CPU per 20 s of
  wall on a sampled pair. Both are the orchestrator's measurements, quoted in V124 and not
  re-derived here.
- (2) This seat measured a third: at 17:06Z the buffer-store push (pid 19711, `open_pr.sh` ->
  `app_push.sh` prepr at "pinned graders") was about 37 minutes in with no gate-lease fd -- a
  healthy run 2.5x past the 900 s bound, recorded in the session ledger and excluded from the
  P206 gate-lease class by measurement (`grep -n 'MEASURED push-stuck' seat-ledger.md` in the
  session state).
- (3) The cost is not the line but the follow-up: V124 records three sweeps spending an
  investigation on the same two PIDs, and this seat spent one pass excluding the third.
- (4) The tree itself puts the healthy duration above the bound: `tests/gate_lock.py:55` says a
  prepr routinely runs past 1,800 s, twice `HPO_PUSH_STUCK_SECS`'s 900 s default.
- (5) The structural reason, and the one the change must fix: the guard can only ever report a
  **live** run. `cloud_relay.sh:492-501` reports a lock only while it is still held (`flock`
  `LOCK_NB` fails), and the kernel releases a dead holder's flock -- so a run that "has not
  ended" in the dead sense never reaches the line, and every report is a run that is alive.
  Elapsed time alone therefore cannot separate a working push from a stalled one; the CPU
  sample can.

Cost: one arm inside `stuck_arm()`'s `STUCK_PY` blob (15 lines today, `cloud_relay.sh:477-491`)
plus a per-branch sample file under `$HPO_STATE_DIR` and three self-test arms in the same
script; `ps` is already the holder's dependency, so no new one. The status quo's cost is
measured in instances (1)-(3): an OWED line on every pass of every push longer than 15 minutes,
and an investigation per sweep. The arm is also the cheapest way to make the andon's own trial
clause ("removed if it reports no STUCK line in its first 48 h", `cloud_relay.sh:468`) judgeable
at all: the trial is satisfied today by lines that are false.

Binding: the 900 s age floor stays and is not raised; a lock past it is reported **only** when
the summed CPU of its recorded run pid's process tree has not advanced by more than 0.2 s of
utime+stime between two consecutive passes; the first sighting past the bound stores the sample
and prints nothing, so detection is delayed by at most one pass (120 s default) and never
accelerated; the tree is summed over the descendants of field 1 of the lock file (`pr_args.sh:85`),
because the holder sleeps in a 0.2 s poll (`pr_args.sh:102`) and the run's shell waits on its
child, so either pid alone reads flat; an unreadable sample (pid gone, `ps` failed) keeps
today's line with `cpu=?`, because the change may not silence the alarm where it cannot measure;
the line keeps its shape and gains the delta (`STUCK <branch> <pid> <age>s cpu+<delta>`), and the
text must say "no CPU advance", not "hung", because a push waiting on I/O is flat too; a released
lock is never read, unchanged; and the self-test arms are (a) an advancing tree prints no line
after the bound, (b) a flat tree across two passes prints it, (c) a run under the bound with a
sample prints nothing (null control).
