# Proposal triage, session s7, batch 40 (P211)

One entry, the first from `proposals.md` since V123: V124, the orchestrator s7 entry. Its
arrival is `proposals.md`'s mtime on this box, 2026-10-27T18:23Z; the entry's own header stamp
reads 2026-10-27T18:53Z, about 10 min ahead of this box's clock -- the seat read and ruled it at
18:43:35Z, so 18:53Z is a stamp, not an arrival. Facts read at origin/main `6eb552157`; roster
at `origin/handoff/audit-r10-roster` `32b938f3e` (212 groups).

Provenance note on the 85-minute figure: it is #2854's own body text -- "when the 30-minute
lease lapsed inside the 85-minute run" -- not a measurement on
this box, and it is not re-derived here; the claim that #2854's body lacks the figure is false.

Correction (this seat, after the first cut merged): the first cut rejected the proposal's second
arm whole. That was wrong about its lease half, and the entry below is corrected. The first cut
reached `main` as PR #2886 (merge `a0e7664ea`); this follow-up replaces it, and the ledger keeps the
order in which the seat changed its mind.

## P211: the push-stuck guard's threshold sits below the work it is guarding (V124)

Verdict: ACCEPT narrowed, in two carries. The proposal's first arm (sample the push's
process-tree CPU advance instead of elapsed time alone) is the one carried into
**R10-UPDATE-PR-SIGNALS** (`resume.stage` `fixing` at the roster tip `8f7e252fe`, so the roster op
is a plain `append-carry`; the group names both `tools/audit/seat/cloud_relay.sh` and
`tools/audit/seat/pr_args.sh`, and its brief is exactly the seam: deterministic arms, a condition
rather than a fixed window, and the `ps` dependency of the lock holder).

The second arm splits. The threshold raise alone is REJECTED: a prepr takes a **pool slot**, not
the exclusive lease, and a slot is held for the life of the run, not its lease
(`tests/gate_lock.py:53-56`: "under load a prepr routinely runs past `LEASE_SECONDS` and
expiry-stealing admitted a fifth while the first still ran"), so 900 s is not too small for the
push, it is too small for a *healthy* push, and every measured instance is a healthy run -- which
is why the CPU condition, not a bigger number, is the repair.

The lease half is ACCEPTED narrowed, into a second carry of **R10-PREPR-CAP**, the group that
owns `tests/gate_lock.py` (`resume.stage` `fixing` at `8f7e252fe`, so also a plain
`append-carry`). The measurement that overturned the first cut: an expired lease does not merely
report, it refuses the command. `renew()` raises `no live gate lease to renew` when the recorded
owner is absent or expired (`tests/gate_lock.py:577`), and `_cmd_flock_wrap` (`:1119-1124`; the
`print` at `:1123`, the `return 1` at `:1124`) turns that `RuntimeError` into rc 1 **without
running the command**; `flock_wrap` (`:861-877`) recovers only from `RenewRefused`, so a lease
lapsing between two measuring commands inside one gate refuses the second, though the prepr itself
is not lease-bound. The repair does not lengthen
`LEASE_SECONDS` and does not change `renew()`'s refusals.
Source: `proposals.md` V124 (orchestrator s7; header stamp 2026-10-27T18:53Z, arrival 18:23Z);
not yet ruled before this entry.

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
- (6) The refusal the lease half repairs, from #2854's own body: `tests/stress.py` and
  `tests/harness_headers.py` "were refused by `tests/gate_lock.py` when the 30-minute lease
  lapsed inside the 85-minute run" (`gate_lock: flock-wrap refused, fix-2854-conflict holds no
  lease: no live gate lease to renew`). Mechanism read here:
  `tests/gate_lock.py:577` and `:1119-1124`, cited above; the first cut read the body's line
  truncated and recorded absence, which is what the correction fixes.

Cost: one arm inside `stuck_arm()`'s `STUCK_PY` blob (15 lines today, `cloud_relay.sh:477-491`)
plus a per-branch sample file under `$HPO_STATE_DIR` and three self-test arms in the same
script; `ps` is already the holder's dependency, so no new one. The status quo's cost is
measured in instances (1)-(3): an OWED line on every pass of every push longer than 15 minutes,
and an investigation per sweep. The arm is also the cheapest way to make the andon's own trial
clause ("removed if it reports no STUCK line in its first 48 h", `cloud_relay.sh:468`) judgeable
at all: the trial is satisfied today by lines that are false.

The second carry's cost is one branch in the `flock-wrap` path plus two self-test arms in the same
script; no new dependency, and the null control is the path that runs today.

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
sample prints nothing (null control). Known limitation of the carried arm: the stored sample
must be keyed to the pid and start it sampled, and re-stored when either differs, or a branch
lock re-taken by a later run compares its CPU against the earlier run's sample and prints a
false STUCK.

Second carry (R10-PREPR-CAP): `LEASE_SECONDS` and `renew()`'s refusal rules do not change; a
command never runs without a live lease, so a label that never held one still takes rc 1; a
refresh respects a waiting ticket and never preempts another label's live run; when the owner is
gone or another label's, or another label holds a ticket first, the path re-takes at the back
exactly as `RenewRefused` does today; and a run that never loses its lease takes exactly today's
path, which is the null control. Self-test arms: (a) an expired own-label lease with no waiter
refreshes and its command runs, (b) one with a waiting ticket re-queues rather than running
beside it.
