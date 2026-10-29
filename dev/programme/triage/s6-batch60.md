# Proposal triage, session s7, batch 60 (P278)

The rolling batch (V182) after batch 59 (#2945, merged as
`66974d47312caa46e9817b9aeae7186e9764e560`). Facts were read at that origin/main.

## P278: retry a roster push refused as non-fast-forward

Verdict: ACCEPT, narrowed to R10-ORCH-ROSTER-SCHEMA: the lint-gate refusal's last line names its
cause. The proposed retry is REJECTED, because the tree already has it and these refusals were not
races.

Source: the orchestrator's triage-queue line of 2026-10-29T10:24:00Z. Two `append-group
R10-FLY-OWED-LEVELS` ops were refused with `rc=3 'the commit is local ... nothing pushed'`, at
09:15:52Z and 09:26:09Z (`roster-blocked.txt`). The proposal reads both as lost races to
`roster_sync.py`'s beat pushes, and the fly-in fixer's dispatch was delayed by more than an hour.

Instances:
- **rc 3 is the lint gate, not a push.** In `tools/audit/seat/roster_edit.py`, the only print of
  "the commit is local ... nothing pushed" follows "LINT GATE REFUSED the push" (`:657-660`), and
  it returns before any push is tried. A lost race has its own path, "lost a race: origin/... moved"
  (`:682`), which re-fetches, re-applies and re-lints up to `PUSH_ATTEMPTS = 3` times (`:137`,
  `:631`). It refuses with rc 2, never rc 3.
- **The retry already exists one level up as well.** `roster_queue.py` re-fetches its lint clone
  and retries up to four times on a stale lint checkout (`MOVED`, `:42`) or on a lost race whose
  lint was clean (`:122`, `:137`).
- **Reproduced, with no rival.** `roster_edit.py append-group R10-FLY-OWED-LEVELS <json>
  --lint-cwd <origin/main checkout>` was run without `--push` on a scratch worktree, at roster tip
  `68406609a`. brief_lint printed `TOTAL: 2 error(s)`. Both are in the group's own brief:
  "none of [owed_unactioned] found near tools/audit/seat/orchestrator_tick.py:690" and "none of
  [orchestrator_tick] found near tools/audit/seat/owed_unactioned.py:50". The cause is that one
  sentence cited both files. The linter reads each citation's anchors from its clause, bounded
  only by `.` or `;` (`tools/policy/brief_lint.mjs`, `clauseWindow`, `:391`, called at `:591`). So
  each file was searched for the other file's name. The roster at the same tip without the group
  lints clean. Every retry would have refused again, so a retry on rc 3 would have bought nothing.
- **Why it read as a race.** The roster loop records only the last output line that matches
  `pushed|REFUSED|error` (`roster-loop.sh`, `res=`, line 49). That line is "... nothing pushed".
  The `TOTAL: 2 error(s)` line and the two errors above it are dropped. The 09:24Z re-queue note
  reported "brief_lint clean" and "likely push race", and the 10:24Z note reported "non-ff
  refusal". Neither is what the gate printed.
- **The authoring defect is this seat's.** The brief was written by P277 (batch 59). It was queued
  without a dry run of the op it feeds. The group JSON is now corrected: the two citations are
  split into separate sentences. The same dry run prints `lint gate: TOTAL: 0 error(s)`, and
  nothing was pushed. Queue line 291, already re-queued, now lands on the loop's next pass.

Accepted (narrowed), carried to R10-ORCH-ROSTER-SCHEMA (carries open; `roster_edit.py` is in its
files):
1. The lint-gate refusal in `roster_edit.py` ends with one line that carries the cause, the count
   and the outcome together, for example `roster_edit: LINT GATE REFUSED: 2 error(s); the commit
   is local at <sha12> in <wt> (detached); nothing pushed`. The detail lines still print above it.
   Any caller that keeps only a last line, or only a last line matching `REFUSED` or `pushed`,
   then records the cause. rc stays 3.
2. Self-test: a fixture roster whose brief cites a symbol its file lacks. The last stderr line
   holds both `LINT GATE REFUSED` and `nothing pushed`. Mutation: the old two-line form fails the
   arm. Null control: a clean fixture still prints `lint gate: TOTAL: 0 error(s)` and pushes.

Rejected: the retry as proposed. It exists twice already (`PUSH_ATTEMPTS`, `roster_queue.py`).
Extending it to rc 3 would re-run a deterministic lint failure up to the bound and then refuse
with the same hidden cause, only later.

Not a tree change: this seat now dry-runs every `append-group` and `append-carry` it queues
through `roster_edit.py` without `--push`, from a fresh origin/main lint checkout, and queues only
on `TOTAL: 0 error(s)`. It costs seconds a ruling.

Cost: about 3 lines of message in `roster_edit.py` plus one self-test arm, in a group already open
on the file. No CI, no new file and no change to rc or behaviour.

Binding: two refusals, two misdiagnoses written into the queue, and a fly-in held for more than
an hour on one cause. The countermeasure makes that cause visible on the one line the callers
keep, and the retry it replaces would not have helped.
