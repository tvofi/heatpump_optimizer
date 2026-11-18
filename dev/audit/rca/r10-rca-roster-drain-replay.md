# R10-RCA-ROSTER-DRAIN-REPLAY: a replayed drain re-resolved index-keyed `drop-carry` ops and removed 18 carries

This is the root-cause seat beside R10-HOTFIX-ROSTER-DRAIN-REPLAY. It follows
`root-cause.md` under `dev/governance/roles/` and
`dev/governance/rules/defect-root-cause.md`, and it touches neither
`tools/audit/seat/beat_jobs.py` nor `beatd.jobs.json`, which belong to the
hotfix.

- **When and where measured:** `origin/main` `5d09dedf6` on 2026-11-10, with
  roster history read on `origin/handoff/audit-r10-roster` at `c444a6995`.
- **Times** are the commits' own `+01:00` stamps.
- **Reproduction:** every figure comes from
  `dev/audit/harnesses/r10_rca_roster_drain_replay.py`, and its command is
  given beside the figure.

## 1. The defect, reproduced

### The mechanism

**How the drain runs.**
- `beatd.py` runs the `roster-drain` row of `beatd.jobs.json` with
  `interval_s` 120 and `timeout_s` 900.
- At the timeout it sends SIGTERM to the process group, then SIGKILL 10 s
  later.
- `beat_jobs.py` `roster_drain` runs each pending queue line through
  `roster_queue.py run 1 1 --mark` on a one-line scratch queue,
  `roster-one.queue`. That pushes the op to the roster branch straight away.

**How it records what ran.**
- The drain keeps the line's key in an in-memory `done` set.
- It writes `roster-done.json` only after the loop ends:
  `ctx.remember("roster-done.json", sorted(done), [])`.

**What a kill does.**
- A pass killed at 900 s has already pushed its ops to origin, but has not
  recorded them.
- The next pass starts again from the top of the queue and applies those ops
  a second time.

**Why that destroys data.**
- `roster_edit.py` `op_drop_carry` ends
  `del g["carry"][_carry_index(g, index, match, "drop-carry")]`.
- With an index, `_carry_index` checks only that the index is in range.
- So a replayed `drop-carry G 6` deletes whatever entry now sits at index 6.
  After the first run, that is the entry that used to be at index 7.

### Reproduced offline

Command: `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py replay`

The command applies one op twice to a five-entry fixture, through
`roster_edit.apply_op`:

- `drop-carry G 1`, run twice, applies both times. The runs remove two
  entries, `entry 1` and `entry 2`.
- **Control:** `drop-carry G --match 'entry 1'`, run twice, applies once. The
  replay refuses with `no carry entry matches`, so one entry is removed.

### On origin

Command: `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py census 43495fb61 c444a6995`

Window: `43495fb61` (08:13) to `c444a6995`. The census prints:

`RESULT drops=32 replays=18 replays_restored=14 replays_unrestored=4 firsts=14 firsts_restored=0`

**The replay rule.** A drop counts as a replay when an earlier drop in the
window removed an entry at the same (group, index). An index op replayed from
the top of the queue lands on its own pair again.

**The control.** The orchestrator's later `append-carry` restorations are
independent of the rule:
- They restored 14 of the 18 rule-replays, from `54f325471` (09:35) to
  `e4ab4a9f8` (09:45).
- They restored none of the 14 first drops.

So the rule and the orchestrator's hand judgement select the same set.

**The four drops never restored** are all in R10-HOTFIX-GATE-BUSY-DEFER, whose
stage is `done`:
- `6027d13ff` (idx 9)
- `76d95c36a` (idx 9). This one removed the item-453f6578 carry that
  `83ba995b6` had marked implemented at 09:04.
- `c7c424169` (idx 4)
- `dfbc636b9` (idx 4)

**The cadence.** The census's `PAIR` lines show each pair replayed 13 to 15
minutes apart. For example, R10-BODY-CONTRACT idx 1 was replayed at 08:58,
09:12 and 09:26. That fits one pass per 900 s timeout plus the 120 s interval.

## 2. The named cause

**The cause:** a position-keyed, non-idempotent op went into a queue whose
runner delivers each line at least once.

That cause needs both halves.

**The replay half is the hotfix's, and it cannot be closed fully.**
- No local record of an op can be atomic with that op's push to origin.
- So a kill between the push and the record always replays at least the op
  in flight.
- The hotfix's own docs say a killed pass "replays at most the op it was
  killed in". That is the hotfix's handoff-wip commit `b4660fa4f`.
- Other paths in `roster_queue.py` also apply an op again:
  - `_run_batch`'s fallback re-applies every line of a batch whose push
    landed but was read as failed.
  - `roster_edit.py`'s push race "re-applies the op on the new tip".

**The destruction half is the op's.**
- The rest of `apply_op`'s dispatch leaves the same result when replayed. Read
  op by op, each sets the same value again (`set-stage`, `set-resume`,
  `edit-brief`, `set-after`, `set-size`, `set-source`, and `set-files`, whose
  `--add` is de-duplicated), or it refuses (`wire-issue` "already wires",
  `unwire-issue` "does not hold", `append-group` "already in the roster",
  `append-carry` "already carries that entry").
- An index-keyed `drop-carry` deletes an entry again.
- An index-keyed `mark-carry` is idempotent on an unchanged list. On a list
  that a replayed drop, or a rival, has shifted, it marks a different entry.
- A replay of the same night that hit only non-index ops did no damage.
  R10-TICK-RESIDUE carry[11], appended at `90d11d12f`, records it: "Pass 2
  re-ran all 9", and those ops came back as refusals.

**Why `drop-carry` by index exists.** It came in with `9969e3ca8`
(2026-10-18, R10-ROSTER-OPS, #2496, merged by #2513), as the inverse of
`append-carry`.
- Its docstring keys the index to `jq '.carry[N]'`, which is what a human
  reads before running the op once by hand.
- On 2026-10-18 nothing re-ran a queue on its own. `roster_queue.py run FIRST
  LAST` was started by hand over an explicit range.
- The first automatic re-runner was the beat's `roster-drain` row. It arrived
  in `0a98a0173`, merged by #3197 on 2026-11-05, and `02ca1f20d` folded the
  older `roster_drain.py` into it on 2026-11-07.
- The index form is still the only way to name some entries. At the roster
  tip, 23 of 1690 carry entries are substrings of a sibling entry in their own
  group, so `--match` with their full text is ambiguous. The command is
  `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py contained c444a6995`.

## 3. The process state: (d)

**(d) The process was sound, and its preconditions changed underneath it.**

**What the process assumed.** `drop-carry` by index was designed for a
caller that runs each op at most once. While a human ran the op, or ran
`roster_queue.py run FIRST LAST` over a range they had just read, that held.

**What changed.**
- The beat's automatic drain made each line run at least once. #3197
  shipped it on 2026-11-05.
- Nothing in the op table, in `roster_queue.py`, or in the drain records
  which ops are safe to replay. So nothing noticed the change:
  - `beat_jobs_selftest.py` never kills a pass partway through the queue.
  - `roster_edit.py`'s drop-carry self-test pins refusals only. It never
    applies an op twice.
- The one seat that saw a replay before the incident, R10-TICK-RESIDUE
  carry[11], about 7.5 hours earlier, judged it harmless. It relied on the
  assumption that every op refuses on replay. That holds for every op except
  the index-keyed carry ops.

**Why not (c).** A barrier against cut-short replays did exist.
`roster_queue.py --mark` rewrites each line as it goes (carry 13(2) of
R10-ROSTER-WRITE-SWEEP, `e3b06bcd1`, merged by #3253), and the beat's wrapper
writes those marks into its scratch `roster-one.queue`.
- That makes the **replay** half a barrier whose unit did not reach the
  instance, which is state (c). It is the hotfix's to close.
- But even a barrier that reached the instance would leave a one-op window,
  for the reason in section 2. So the 18 drops come down to the op's
  precondition, and that is (d).

**Why not (b).** No rule asked a queue writer to key carry ops by content,
so there was nothing to disobey.

## 4. Class search

**Command:** a `Grep` over the tree, JSON excluded, for `(drop|mark)-carry +<group> +<index>`.
- Outside this diff it returns only the two usage lines in `roster_edit.py`
  and `instruments/roster_edit.py.md`.
- No brief, contract or instrument tells a seat to queue an index-keyed carry
  op. The habit is the orchestrator's, writing to its local queue, and that
  queue is not on origin.

**Other runners that apply first and record afterwards:**

| runner | disposition |
|---|---|
| `roster_queue.py` `_run_batch` fallback and single-op `run_queue` | Re-apply at least once. **Closed for this op class in this diff** (`replay_unsafe` on both paths). |
| `roster_edit.py` push race | Re-applies the op on a moved tip. **Closed for queued ops** by the same refusal. A hand run keeps its index, which a human read just before running it. |
| `beat_jobs.py` `audit_dispatch` and `head_watch` | Their side effects are digest and event lines. A replay emits a line again and changes nothing on origin, so there is nothing to disposition. |
| `cloud_relay.sh` relay ledger | The earlier instance, R10-RELAY-REPLAY. **Already guarded** by its content check, which pushes nothing when `review/<pr>` holds the probe's tree. |

The beat's end-of-pass record belongs to the hotfix, R10-HOTFIX-ROSTER-DRAIN-REPLAY.

## 5. Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in
wall-clock per occurrence.

### Cost of the defect

The lower bound is 600 s per occurrence:
- The orchestrator restored 14 carries over 10 minutes (`54f325471` 09:35 to
  `e4ab4a9f8` 09:45).
- That does not count noticing the loss, or the hotfix and RCA seats.
- 4 of the 18 replays were never restored, and the census prints them. That
  part of the loss went unnoticed, so it has no time cost here but it is not
  zero.

### P(recurrence)

**Measured replay episodes on the roster drain:**
- 2026-11-01: `roster_drain.py`'s 3600 s timeout (R10-ROSTER-WRITE-SWEEP
  carry 13(2)).
- 2026-11-10, 01:20 at the latest: R10-TICK-RESIDUE carry[11].
- 2026-11-10, 08:40 to 09:29: this incident, with 4 replay passes.

That is 3 episodes in 10 days. A replay destroys data whenever the line it
re-runs is an index-keyed carry op.

**Within this incident:** 8 of the 14 first index drops were replayed at least
once. That is the census's `PAIR` count over its `firsts`.

**After the hotfix:** the window narrows to the op in flight, so P drops by
roughly the length of a pass. That rate is not yet measurable. The batch
fallback and the push race remain at-least-once.

### Cost of the countermeasure

- **Compute:** under a microsecond per queue line, as `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py cost` prints.
- **A refused index line:** at most one drain interval (120 s) before the
  writer queues it again with `--match`. That is paid once per line written
  the old way, not on every run.
- **The 23 of 1690 entries `--match` cannot name:** these go by hand through
  `roster_edit.py`, as they did before the beat.

### Verdict

**Passes.** Take the post-hotfix worst case, where every index line written
costs a 120 s requeue. The countermeasure still pays once P(a given index line
is replayed) exceeds 120/600 = 0.2. The incident's measured rate was 8/14 =
0.57. In the steady state the requeue cost goes to zero, because writers stop
writing index lines.

## 6. Countermeasure (built in this diff)

This addresses state (d). The queue runner now notices its own precondition:
a line it runs may run twice.

**What it does.**
- `roster_queue.replay_unsafe(op, extra)` refuses a `drop-carry` or
  `mark-carry` that has no `--match`.
- It runs on both the single-op path (`run_queue`) and the batch path
  (`_run_batch`), before the editor is called.
- A refused line is reported `refused rc=2 ... key it --match TEXT` and
  marked `#refused`.
- The beat's drain records a refusal as done, so the line is never retried,
  and it shows up in the digest.
- A hand run of `roster_edit.py` keeps the index form.

**Shown to detect** (`python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py replay`, `GATE` lines):
- `drop-carry G 1` and `mark-carry G 1 dismissed x` are refused.
- Their `--match` forms run. That is the null control: the check does not
  fire on the replay-safe form.

**Self-test:** `roster_queue.py --self-test` drives a queue of
`drop-carry G 1`, `mark-carry G 0 dismissed x` and `drop-carry G --match one`
on the single-op path, and `drop-carry G 0` on the batch path with the real
editor.
- Both index forms are refused and marked.
- The `--match` line is pushed.

**Mutation proof** (`python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py mutants`):
- Four mutants: predicate off, single path unchecked, batch path unchecked,
  `mark-carry` left out.
- Each turns the copy's self-test red.
- The unmutated copy passes.

**What it does not do.**
- It does not make the replay path at most once. That is the hotfix.
- It does not restore the four lost carries. That is carried in the PR body.

## 7. What this seat did not establish

- **The queue file, `roster-done.json` and beatd's PASS/timeout journal.**
  These are local to the orchestrator's host. The kill reason (timeout) comes
  from the brief and the hotfix's brief, about 45 s per op through the lint
  gate. The commits fit it, with drops 40 to 60 s apart and pair replays 13
  to 15 minutes apart, but this seat did not read the kill line.
- **Whether every one of the 14 first drops was queued by index.** The census
  can tell an index replay only by its repeated pair. A `--match` op that
  replays refuses, so it leaves no commit.

## 8. Issue draft (for the orchestrator to post where the hotfix is tracked)

> **Root cause** (`dev/audit/rca/r10-rca-roster-drain-replay.md`)
>
> - **Cause:** the beat's `roster-drain` (#3197) runs each queue line at least once. A pass killed at its 900 s `timeout_s` pushed ops but never wrote `roster-done.json`, so the next pass replayed them. `drop-carry <group> <index>` is not idempotent: a replay deletes whatever entry now sits at that index. Census `43495fb61..c444a6995`: 32 drops, of which 18 are replays. 14 of those 18 were restored by hand. 4 in R10-HOTFIX-GATE-BUSY-DEFER were not.
> - **State (d):** the index form (`9969e3ca8`, 2026-10-18) was sound for a run-once caller, a human reading `jq '.carry[N]'`. The automatic drain made delivery at-least-once, and nothing records which ops are safe to replay. The replay half is state (c): `roster_queue --mark`'s per-op barrier writes into the beat's scratch queue. That half belongs to R10-HOTFIX-ROSTER-DRAIN-REPLAY, and even a full fix of it leaves a one-op window.
> - **Cost test:** the defect costs at least 600 s per occurrence, the 10 minutes of hand restoration, plus unnoticed loss. There were 3 replay episodes in 10 days, and 8 of 14 index drops replayed in the incident. The countermeasure costs under a microsecond per line (the harness's `cost`), plus at most 120 s per index line written. **Passes.**
> - **Countermeasure (built):** `roster_queue.replay_unsafe` refuses an index-keyed `drop-carry`/`mark-carry` on both run paths: `refused rc=2 ... key it --match TEXT`. It has been shown refusing the index form and passing `--match`, and 4 of 4 mutants are killed. A hand run keeps the index form.
