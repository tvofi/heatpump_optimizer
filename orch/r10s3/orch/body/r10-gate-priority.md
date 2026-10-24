The local gate lease (`tests/gate_lock.py`) was first come, first served, so a
group's pull request queued behind every older ticket on the box. The owner's
ask: a group on the critical path should get first place in the queue. The
lease now carries an integer priority on each ticket and orders
priority-then-arrival, in both queues (the exclusive lease and the four-slot
heavy pool); `tools/pr/prepr.sh` DERIVES the default from the branch's roster
group and the orchestrator's published critical-path set, so no human assigns
it per pull request. Priority 0 is exactly today's FIFO.

The same run fixes the pool's cap lie. A heavy slot was freed when its
30-minute lease expired even while its holder still ran, and under load a prepr
routinely outlives that lease, so a fifth gate was admitted beside it while
`slot-status` said the cap held. A slot is now held for the life of its run --
the taker's pid is recorded, and an expired slot is freed only when that pid is
gone -- and the status line counts both witnesses of an over-subscribed pool.

## Head

`31529479c13d41831c7d677ff299559c4f55a040`, measured with
`PREPR_SKIP_CLOSURES=1` per the owner's 2026-10-20 ruling (the closures
recording is the long step that outlived the slot lease on this box).

## Channels

The lease is generic: it orders by the integer it is given and never decides
who deserves one. `tools/pr/prepr.sh` step 1b0 resolves the integer, first
valid channel winning:

1. `$HPO_GATE_PRIORITY` -- the caller's explicit override (any integer; the
   lease clamps it to 0..2).
2. `.gate-priority` in the worktree root -- one line, the group's override.
3. The derived default -- the branch's roster group (`resume.branch`, else the
   branch's last path segment) is in the round's critical-path set: priority 1;
   otherwise 0.

The derived default reads `dev/programme/rosters/critical-path.json` at the
round roster ref, `origin/handoff/audit-r<N>-roster`, fetched at call time so a
stale local mirror cannot decide a group is off the path. Schema, exactly two
keys:

```
{"at": "<iso8601>", "critical": ["R10-GROUP", ...]}
```

`at` is informational; `critical` is the list of roster group ids, matched
after `roster_lib.norm_group` (lowercase, `_` as `-`). Missing, unreadable or
malformed means 0 for every group: fail to FIFO, never a crash and never a
stuck queue. `prepr.sh` exports the answer, so the heavy-slot take and every
nested leased step (`run.sh`, `derive_closures.sh`) carry it. Which group is on
the path is the orchestrator's policy, expressed through this channel; nothing
in `tests/gate_lock.py` reads a roster or names a group.

## Slot lifetime

The defect, measured by the orchestrator on this box at 19:15Z on 2026-10-20:
`prepr.sh` takes a slot once and never renews it; `prepr-49410` took slot 1 at
18:05 with `expires_at 18:35`, was still running at 19:23, and no slot file
named it -- slot 1 had been re-taken at 19:05, so that run executed unleased for
43 minutes while five gate runs were live and `slot-status` said 4/4.

The rule: `take_slot` records a pid -- the caller's, else its own -- and
`_free_slot` frees an expired slot only when that pid is gone; a dead pid is
stolen at once, as before. The lease stops being a deadline and becomes a
liveness handle, so the unleased-run case is impossible for every taker,
because every taker now names a process. Alternatives and why each lost: a
renewal timer inside the holder is paused by SIGSTOP or extreme load while the
process still runs, and its thread must also be stopped at release; a longer
static lease only moves the cliff -- the measured run was 78 minutes against a
30-minute bound, and the next bound would be outlived by the next load. The
exclusive lease keeps its expiry rule AND its renew refusal: a stress run
measures the machine, so extending it past a waiter would falsify a measurement.

The witness: `slot-status` prints `past-lease=N(...)` for holders whose pid is
alive past their lease, and `unleased=N(...)` for runs that could not take a
slot. `prepr.sh`'s failed-take arm writes that marker (`slot-unleased`) and
clears it on exit (`slot-leased`); a crashed run's marker is pruned once its pid
is gone. A holder past its lease now reads `live-past-lease`, never `expired`,
so the line no longer offers a live slot as free.

Rollout boundary, observed live: at 20:36Z on this box, with the other
worktrees still running `origin/main`'s `gate_lock.py`, this prepr's lease
expired and a peer's OLD-CODE taker re-took its slot. The fixed tree cannot
stop a taker that does not implement the liveness rule; the guarantee starts
when this tree is the one every seat runs.

## Approval

`tests/gate_lock.py` and `tools/pr/prepr.sh` are code-owned, so this needs the
owner's approving review. It also corrects one sentence of policy:
`dev/governance/rules/gate-scoping.md` said the queue is "First come, first
served", which this change makes false; it now reads "Priority, then arrival"
(the generated `.claude/rules/` and `.cursor/rules/` copies are regenerated by
`rules_sync.mjs`; the recorded caps are untouched at 61 lines and 794 tokens,
and the file measures 61 lines and 792 tokens).

Behaviour change, two parts:

1. A `prepr.sh` run whose branch resolves to a group listed in
   `critical-path.json` takes priority 1 on its lease and slot tickets, so it
   goes ahead of normal waiters that queued earlier. With no override and no
   listing the queue is the old FIFO. Aging after 600 s promotes a waiting
   normal ticket to the top band, so it overtakes any priority that arrived
   later.
2. A heavy slot is released only by the process that took it (or by a taker
   once that process is gone), never by lease expiry while the taker lives. A
   `prepr.sh` that outlives 30 minutes therefore keeps its slot instead of
   running beside an admitted fifth. `HEAVY_SLOTS` stays 4 and the lease stays
   1800 s.

Rollback: `git revert <this commit>` restores the previous ordering and expiry
rule together; for ordering alone, `export HPO_GATE_PRIORITY=0` before
`prepr.sh` does the same for that run.

## Mutation proof

Each mutant applied in place to this head, run as
`PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept`, then restored;
every mutant exited rc=1.

| mutant | edit | failing check |
|---|---|---|
| (a) priority ignored in the ordering | `_queue`'s sort key drops `-waiter.effective(now)` | `priority: an urgent waiter takes before an older normal one...` (`order=['normal','urgent']`), `priority: the heavy-slot pool orders by the same rule`, and the aging and malformed arms |
| (b) priority lost on the ticket rewrite | `_enqueue` writes `PRIORITY_NORMAL` when refreshing an existing ticket | `priority: an urgent waiter takes before...` (`rewrite=False`, `order=['normal','urgent']`) and `priority: a ticket rewrite keeps its priority and its arrival stamp` (`priority=2/0`) |
| (c) aging removed | `Waiter.effective` returns `self.priority` | `priority: aging promotes a normal waiter past a later urgent one, and only past the window` (`aged=['urgent','normal']`; the same case's below-window null control stayed correct) |
| (d) malformed priority crashes | `_read_priority`'s try/except deleted | `priority: malformed, absent and out-of-range values are 0 or clamped, never a crash` (`raised ValueError`) |
| (e) derived default always 1 | `derived_priority` returns 1 after resolving the group | `a group that resolves but is not listed stays normal (null control)` (got 1) |
| (f) derived default always 0 | `derived_priority` returns 0 after resolving the group | `a listed group gets priority with no env and no marker`, `the branch's last segment answers for the group without resume.branch`, `with neither override the derived default still answers` |
| (g) expiry steals a live holder | `_free_slot` back to `owner.expired or _orphaned(...)` | `a live holder keeps its slot past its lease, and a fifth taker is blocked` (`blocked=False`) and `a taker queues behind a live past-lease holder...` (`queued=False`) |
| (h) no pid recorded when the caller names none | `holder_pid = owner_pid` | `a live holder keeps its slot past its lease...` (`names_pid=False`) |
| (i) witnesses not reported | `slots_status` returns empty `past_lease`/`unleased` | `a live holder keeps its slot past its lease...` (`past_lease=[]`) and `slot-status counts past-lease holders and unleased runs...` (`counted=False`) |

(e) and (f) are `python3 tools/pr/gate_priority.py --self-test` (rc=1 each); the
seven lease arms are the acceptance run above.

## Null control

- `tests/gate_lock.py --accept` at `origin/main`: 17 checks, all pass. At this
  head: 29, all pass. The 17 existing checks are unchanged and were measured by
  running `origin/main`'s own copy; the new driver
  (`dev/audit/harnesses/r10_gate_priority_base.py`) runs all 12 new cases
  against that same copy and shows eight red, with four green at both ends:
  the renew guard, the concurrency control, the dead-pid steal and the
  legacy no-pid expiry/fresh pair. So the red arms are about the fix, not the
  driver.
- `roster_lib.py --self-test`: 18 checks at `origin/main`, 24 here (one
  normalization row, one absent-file row, one read row, three malformed rows).
- `prepr.sh --self-test`: 309 checks, 0 failed; the six rows this change adds
  are the five wiring pins and the helper's own self-test row.
- Every new case carries its own null control: the aging arm's one-second-under
  window is FIFO by priority; the derivation's unlisted-group and no-group arms
  are 0; the concurrency arm's overlap count is 0 at both ends; the slot-hold
  arms plant the same past expiry with a dead pid (stolen), a fresh no-pid
  holder (respected) and a dead unleased marker (pruned).

## Figures

One line per figure; each command was run at this head.

| figure | command | result |
|---|---|---|
| gate scope | `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh` | `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (key on the mode line, not the count), then `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`, exit 0; 4626 s at load1 45-176 (176 at 21:06Z, 45 at 22:05Z), `entities.py` alone 3500 s |
| failing-first | `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_gate_priority_base.py origin/main` | `origin/main: 8 of 12 lease cases FAILED`, rc=0 |
| lease self-test | `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` | `ALL 29 gate lock acceptance checks PASSED` |
| concurrency control | the `concurrency control:` row in three consecutive runs of the command above | `overlaps=0` each run |
| pool status witness | `python3 tests/gate_lock.py slot-status` | prints `past-lease=N(...) unleased=N(...)`; on this box at 2026-10-20T19:26Z, with all four holders inside their leases, `past-lease=0 unleased=0`; the marker pair round-trips (`slot-unleased` then `slot-leased` prints `unleased=1(probe-1)` then `unleased=0`) |
| pre-PR check | `bash tools/pr/prepr.sh <body>` | `PRE-PR: 31529479c13d41831c7d677ff299559c4f55a040`, rc 0, no `REFUSE` row, `gate mode MODE: SCOPED`, `PR-BODY: 0 error(s)`, `FIGURES: 8 resolved, 0 refused`. The full run took 47 minutes (outliving its 30-minute slot lease -- the defect's own shape); the handoff run with `PREPR_SKIP_CLOSURES=1` took 21 minutes. Load1 readings: 199 at 19:36Z, 99 at 19:46Z, 176 at 21:06Z, 63 at 22:21Z, 56 at 22:49Z (end of the flagged run) |
| derivation, live | `python3 tools/pr/gate_priority.py --branch <a listed group's resume.branch>` / `--branch handoff/r10-gate-priority` | at roster ref `7888809aa3` (2026-10-20T17:35Z): 1 for `handoff/r10-sav-reasons`, 0 for this branch; the set is republished at wave edges, so re-run the instrument rather than carry either number |
| structure | `python3 tests/structure.py` | `STRUCTURE RATCHET PASSED`: every metric in `tests/structure_budgets.json`'s keys less `recorded_at` at or below its cap |
| arch score | `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)` | `Architecture score: dS +0.0000 NULL` |

## Architecture score

`none`: dS +0.0000 (NULL), the command above.

## Red checks

- `harness-headers` / `every inlined walk matches the canonical helper and no
  depth root remains` (`tests/harness_headers.py`): red on this branch's first
  local gate run, because the new demonstration harness
  `dev/audit/harnesses/r10_gate_priority_base.py` used a depth root
  (`Path(__file__).resolve().parents[3]`). The cheaper detector is that same
  check: `harness_headers.py` is `run_always`, so it ran inside the scoped gate
  before any push. Its standing cost is one run per gate: 501 s in this run at
  load1 40-78 (the box carries other seats), against the ~100 s the module's
  own `SLOT_MIN_SECONDS` comment records for it. No cheaper
  detector exists — an edit-time hook would perform the same tree walk the check
  performs. The harness now inlines the canonical `repo_root` copy, and the
  re-run is in `## Figures`.

No check has been red on a pushed commit: the branch has not been pushed yet.

## Unpinned sites

`none`: `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base $(git merge-base origin/main HEAD)`
predicted no unpinned mutation site. Its one prediction was an INERT read of
the new harness by `tests/harness_headers.py`, repaired with
`ci_predict.py --base $(git merge-base origin/main HEAD) --apply-inert` and
committed in `tests/closures.json`.

## Forward-carry

- The orchestrator republishes the round's critical-path set at each wave edge,
  at the path and schema `## Channels` states, on
  `origin/handoff/audit-r<N>-roster`. Until it does, every branch derives 0 and
  the queue is FIFO; a malformed file is the same. The reader is
  `tools/pr/gate_priority.py`, whose module docstring carries the schema, and a
  branch that maps to no group is 0. The policy corpus
  (`dev/governance/roles/orchestrator.md`) is at its cap with zero headroom, so
  this stage's constraint is carried here and in the module docstring rather
  than as a contract edit. Carry: #201

## Friction

`none`.
