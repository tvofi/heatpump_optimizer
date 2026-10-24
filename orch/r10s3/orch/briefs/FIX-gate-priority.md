# Fixer — priority in the local gate lease

Role: **fixer**, one fix. Repository `tvofi/heatpump_optimizer`. Read `dev/governance/roles/fixer.md` first:
failing test first, mutation proof, the finder's harness at both ends, a null control for every quantified
claim, `GATE_SCOPE=auto`, `tests/structure.py` before the push, and the handoff freezes the branch.
**LOCAL seat only — no cloud.**

## The ask (tvofi, 2026-10-20)

> "I want a fix to the local gate lease. Any PR on the critical path should get first in line if there is a queue."
> then, correcting the scope: "Or any group, rather."
> then, settling the default: "I mean that the group should be on the critical path for a ticket to get first in
> the queue by default."

So the **default is derived, not declared**: a ticket whose group is on the current critical path takes first place
in the queue, with no human decision per pull request. The **lease stays generic** — it carries an integer priority
and does not decide who deserves one, and it does not compute a critical path. The **caller derives the default**:
`prepr.sh` resolves the worktree's group (roster `resume.branch` → `group`) and asks whether that group is on the
critical path, read from a committed set on the roster branch — `dev/programme/rosters/critical-path.json`,
`{"at": "<iso>", "critical": ["R10-…", …]}` — which the orchestrator republishes at each wave edge. An explicit
override (an `HPO_GATE_PRIORITY` variable, or a `.gate-priority` marker in the worktree that `prepr.sh` turns into
it) still wins, for a group the owner or the orchestrator names as urgent off the critical path. Anything unreadable,
malformed or unmatched is priority 0: **fail to FIFO, never crash and never stall the queue**.

## The code you are changing

`tests/gate_lock.py` (1208 lines). It holds two FIFOs today:

- the **single lease** (`acquire`, near line 350) — a waiter takes `ticket-<n>` and a free lease goes to the
  oldest live ticket (`_live_queue`, near line 324: `sorted(lock_dir.glob("ticket-*"))`, oldest first);
- the **heavy-slot pool** (`take_slot`, near line 506), `HEAVY_SLOTS = 4`, same ticket discipline in its own
  directory. `tools/pr/prepr.sh` and the other heavy callers go through the pool.

Read those two functions and `_enqueue` (near line 304) before designing anything. Note two properties the
design must keep: a waiter **rewrites its ticket every poll** (so anything you add to the ticket must survive
that rewrite), and `renew` already **refuses to extend a holder while another label's ticket waits**
(`RENEW_REFUSED_RC`) — a critical waiter must keep that behaviour, not bypass it.

## What to build

1. **A priority the lease carries, derived by default from the group.** No priority means exactly today's
   behaviour. The lease accepts an integer priority (suggest 0 normal, 1 high, 2 urgent; the names are yours)
   and orders by it. The channel must be usable by `prepr.sh` — which the orchestrator runs per pull request and
   per group — without editing the caller's code. Precedence, highest first: `HPO_GATE_PRIORITY` in the
   environment; a `.gate-priority` marker in the worktree, which `prepr.sh` turns into that variable; **the
   derived default** — group on the critical path → priority 1; otherwise 0.
   The derived default needs both halves in this pull request: `prepr.sh` resolves the branch's group from the
   roster and reads `dev/programme/rosters/critical-path.json` from the roster ref (fetch it if needed; the same
   ref the other seat tools use, `origin/handoff/audit-r10-roster`). State the exact file path, schema, ref and
   resolution order in the body, because the orchestrator populates that file at each wave edge. A missing file,
   a malformed one, a branch that maps to no group and a group absent from the list are all priority 0.
2. **Queue order: priority first, then age.** A free slot goes to the oldest ticket **within the highest
   priority present**. A ticket with no priority, a malformed one, or an unreadable file must be treated as
   priority 0 and must never crash the queue.
3. **Aging, so normal work cannot starve.** A low-priority waiter that has waited past a stated window must
   overtake a higher-priority one that arrived later. Choose the aging rule, state the constant and its
   rationale in the module docstring, and make it testable (an injectable clock or a settable threshold, no
   sleeping tests).
4. **Both queues.** The single lease and the heavy-slot pool must obey the same rule; the two queues stay
   separate as they are now.

## The tests this owes

- **Failing test first**: on the base, a higher-priority second waiter loses to an older normal ticket — write the
  test that fails there and passes after.
- **Derived-default arms**: a branch whose group is listed in `critical-path.json` gets priority with **no**
  environment variable and **no** marker; the same branch with the file absent, the file malformed, the group
  absent from the list, or the branch mapping to no group stays at 0 and the queue is byte-for-byte FIFO; an
  explicit `HPO_GATE_PRIORITY` beats the derived value in both directions.
- **Mutation proof**: each arm independently red — (a) priority ignored in the ordering, (b) priority lost on the
  ticket rewrite, (c) aging removed, (d) malformed priority crashes instead of defaulting, (e) the derived default
  ignored, (f) a malformed critical-path file crashing instead of defaulting to 0. Show each mutant's `rc` and the
  failing test name.
- **Null control**: with no ticket carrying a priority, the queue is byte-for-byte the old FIFO — the existing
  gate_lock self-tests must still pass unchanged, and say how many they are before and after.
- **Concurrency control**: two waiters released inside one poll see exactly one take the slot; prove it with the
  instrument rather than by reading the code.

## Constraints

- `tests/gate_lock.py` and `tools/pr/prepr.sh` are code-owned paths, so the owner approves at merge; write the
  body for that reader and state the behaviour change in `## Approval` with a one-line rollback.
- Do not change `HEAVY_SLOTS` (4) or the lease duration; this fix is about order, not capacity.
- CI cannot exercise a local lease; the proof is the harness on this box. State the load (`load1`) beside any
  wall-clock number, and prefer counts.
- No host path in any ref name, commit message or body (#2310): write `~/…`.

## Environment and handoff

- Scratch: **`/Users/timmalmstrom/hpo-seats/r10s3/gate-priority`** (absolute; create it). Worktree:
  `git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/gate-priority/wt -B handoff/r10-gate-priority origin/main`.
- `export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH` (pinned 3.14).
- Instruments: `tools/audit/seat/` (see `INSTRUMENTS.md`); the lease is exercised by `prepr.sh` and the gate, so
  run the gate at `GATE_SCOPE=auto` and paste the mode line.
- Push the code to `handoff/r10-gate-priority` and the body to `handoff-body/r10-gate-priority`; the orchestrator
  opens the pull request. Every finding carries a `Carry: <dest>` marker and `carry_audit.py check --body` must
  print 0 unrouted.

## Report back, under 250 words

Both ref SHAs; the channels a caller uses (and the marker file's precedence if you implement one); the aging
constant and why; each mutation's rc and red test; the null-control count; the gate mode line; and anything you
could not establish.
