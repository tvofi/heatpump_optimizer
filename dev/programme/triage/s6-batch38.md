# Proposal triage, session s7, batch 38 (P206)

One entry. Numbering continues after `s6-batch37.md` (P205). Facts read at origin/main
`524c1896b` on 2026-10-27.

## P206: one seat's measurements hold the whole push lane for half an hour (V126)
Verdict: ACCEPT narrowed -> a carry of **R10-PREPR-CAP** (it owns `tools/pr/prepr.sh` and
`tests/gate_lock.py`; its stage is `done`, so the roster seat reopens it to append this carry,
the way it reopened `R10-996-RUNNER-CLAIMS` for P196). The proposal asked for a cost/benefit
ruling on three arms; measured against the tree, the holder-side bound it names in arm 1 is
already the mechanism, and the bound that can still be moved is on the **waiter**. So the
carried arm keeps the proposal's goal -- one seat does not acquire a push lane for half an hour
-- and puts the bound where it can act: past a bound, the waiter takes the exit the rule already
sanctions (`SKIP: <script> ... left to CI, named unrun`) instead of blocking unbounded.
- Arm 1 as proposed (bound the lease and renew it) is REJECTED because it already exists and
  cannot act on the observed wait: `LEASE_SECONDS = 1800`, and `renew()` refuses with
  `RENEW_REFUSED_RC` (75) while another label's ticket waits -- the refusal message is "Finish
  the current stress.py run, release, and take again: you queue behind it". The wait measured
  below is `fcntl` on a *running* measurement, and `flock` is released only when that process
  exits; an expiry cannot preempt it, and shortening the lease would not touch it.
- Arm 2 (a scoped gate under a heavy slot instead of the lease) is REJECTED on a measured fact:
  the only scripts that take the lease are `tests/stress.py` and `tests/harness_headers.py`, and
  they are leased because they measure the machine -- `gate_lock.py`'s own statement is that
  their numbers "are comparable only with nothing else running". Running them inside a
  four-slot pool would measure load, not the tree. The multi-minute non-measuring side is
  already a slot (`SLOT_MIN_SECONDS = 69`).
- Arm 3 (longer leases) is REJECTED as proposed, and for a second reason: a longer lease also
  lengthens a wedged by-hand holder's window between commands.

Source: orch s7, 2026-10-27, relayed to this seat with its measurement done; the
`proposals.md` entry was not yet appended when this ruling was cut.

Instances: one measured wait, and the tree's recordings account for its length.
- The wait: `update_pr.sh fix/r10-cop-partload` (pid 62391) sat 38 minutes as an fcntl waiter
  while the lease passed from `fix-2854-stress2` (released 11:59:49Z) to
  `r10-train-overlap-grade` (taken 11:59:52Z, `expires_at` 12:29:52Z); the owner file still
  named that label when read at 12:13Z (`cat /tmp/hpo-gate.lock/owner`). The orchestrator's
  measurement, not re-derived here.
- Why 38 minutes: two consecutive legitimate measurement runs. `tests/closures.json`'s
  `recorded` table gives `tests/stress.py` at 936.3 s and `tests/harness_headers.py` at 241.1 s;
  2 x 936.3 s is 31.2 minutes, and the first run's tail plus queueing reaches 38. Command:
  `python3 -c "import json; print(json.load(open('tests/closures.json'))['recorded']['tests/stress.py'])"`.
- The lease is already bounded and already refuses extension: `LEASE_SECONDS = 1800` (line 78),
  `RENEW_REFUSED_RC = 75` (line 120), `renew()` at line 568. The module docstring states the
  design: "The exclusive lease keeps its expiry rule, since a stress run measures the machine
  and must not be extended past a waiter."
- The lease is taken per script and only for measuring ones: `tests/run.sh`'s `leased()` asks
  `needs-lease` about the single script it is about to run (lines 317-355), and `needs_lease`
  answers `lease` only for `MACHINE_MEASURING`, an empty scope, or an unreadable table (lines
  918-954). Measured: a scope naming two ordinary scripts answers `slot`, one naming
  `tests/stress.py` answers `lease` (`python3 tests/gate_lock.py needs-lease <file>`).
- The waiter's wait is unbounded: `take()`'s loop is `while True: ... time.sleep(WAIT_POLL_SECS)`
  with no deadline (lines 511-566); `wait=False` raises instead, and only `gate_lock.py`'s own
  self-tests pass it. `grep -n 'timeout\|deadline\|max_wait' tests/gate_lock.py` finds only
  subprocess-cleanup waits, none in the ticket loop. `tests/run.sh`'s comment above `leased()`
  states the hold: "auto-lease and flock-wrap both hold flock for the run, so a crash releases
  at once (#404)" (lines 325-326).
- Roster: `R10-PREPR-CAP` owns `tools/pr/prepr.sh` and `tests/gate_lock.py`, stage `done`, no
  carry; `tests/run.sh` is named in no group's `files` (208 groups), so the carry names that
  file explicitly.

Cost: about 15-20 lines in `tests/gate_lock.py` -- a deadline in `take()`'s wait loop,
defaulting to the awaited script's recorded duration when the caller names one and to
`LEASE_SECONDS` otherwise, exiting with a distinct code plus one line naming the wait and its
bound -- and a four-line case arm in `tests/run.sh`'s `leased()` mapping that code to the
existing skip line, so the lane's manifest records a named unrun rather than a pass. Two
self-test arms: one waiter past the bound exits with the code and the line, one within it still
runs. Standing cost on the uncontended path, which is the common case, is one clock read per
poll and no new branch: no new file, no CI minutes, no GitHub call.

Binding: the bound must be at least the awaited script's recorded duration (936.3 s for
`stress.py`, 241.1 s for `harness_headers.py`), or the arm skips a measurement the waiter would
have completed and turns a contended-but-legitimate local gate into a skip; the skip must be the
existing named-unrun line, never a silent pass, so no lane reads green without stress.py; it
must apply only to scripts `needs_lease` classifies `lease`, because a `slot` waiter already
shares the four-slot pool and its constraint is CPU, not comparability; an uncontended run must
take no new branch (the null control); and neither `LEASE_SECONDS` nor `renew()`'s refusal
changes with this carry, because the lease period is not the defect. What would overturn the
arm: a waiter bound already present somewhere this reading did not reach, or a measured
`stress.py` cost far below the 936.3 s recording, which would move the bound figure but not the
arm's shape.
