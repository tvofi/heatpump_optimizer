# Proposal triage, session s8, batch 78 (P315)

The rolling batch (V182) after batch 77 (handoff `triage-s8-batch77`). Facts were read at
origin/main `5d4e0bcfb`, in the orchestrator's `seat-ledger.md` and `s7/roster-queue-s7.txt`, and
in the R10-FLY-BEAT-FETCH-RACE group file the orchestrator queued
(`s8/beatrace/R10-FLY-BEAT-FETCH-RACE.json`).

## P315: roster_queue.py `run` dies before writing a report line, so a caller reads the previous op's line

Verdict: ACCEPT narrowed, a carry on **R10-FLY-BEAT-FETCH-RACE**, as the orchestrator directs. That
group is S and not started, and owns the roster write path's transient failures (`roster_edit.py`
`fetch_origin`). This carry adds `tools/audit/seat/roster_queue.py` to its files.
- **The rule.** `run_queue` writes exactly one report line for every op it attempts, whatever
  happens. An exception in the op, or in the lint clone's `git fetch` and `git checkout`, becomes
  `roster: <op> <group> FAILED <ExceptionType>: <message>`. The run then stops with a nonzero rc,
  never silently.
- **A missing `--lint-clone` is refused by name** before the first op:
  `roster: lint clone <path> missing; nothing applied`, rc 2.
- **REJECTED: having the runner re-clone the lint clone itself.** Provisioning the clone is the
  caller's (`--lint-clone` is "a checkout it owns", the runner's own docstring). A re-clone at an
  arbitrary path would also hide a misconfigured path behind a network side effect.
- **Order with P300.** P300 (`s6-batch68.md`, R10-ORCH-ROSTER-SCHEMA) adds `--mark` to the same
  `run_queue`. A FAILED line marks `#refused` there. The two carries touch distinct seams (the
  exception path and the marking), and whichever lands second merges main.
- **Hold.** This carry waits until the group is on the roster branch. Its own append-group was one
  of the ops the slip falsely marked `#done (already)`, and is re-queued.

Source: the orchestrator s8's message of 2026-10-31 (a slip, under slips-become-proposals).

Instances:
- **The defect, read at main.** `run_queue` (`roster_queue.py:93`) calls
  `_git("fetch", "-q", "origin", cwd=a.lint_clone)` at line 123. `_git` (lines 45-46) is a bare
  `subprocess.run` with `cwd=`, so a missing directory raises `FileNotFoundError` from the
  subprocess before `rep()` writes anything.
- **The ledger.** `seat-ledger.md` lines 2765-2769 hold five `roster s8: no report line written
  (rc=1): ... FileNotFoundError` lines, and the ledger holds 17 `refused exception
  FileNotFoundError` lines in all.
- **The consequence**, by the orchestrator's account and its queue. The s8 loop read the report's
  last line, which belonged to the previous op, as this op's result and marked 12 ops
  `#done (already)` that never landed. Two of them were carries that #3014's review depended on.
  One was the append-group of R10-FLY-BEAT-FETCH-RACE itself: queue line 520 reads `#done
  (already) append-group R10-FLY-BEAT-FETCH-RACE ...`, line 532 re-queues it, and the group is
  absent from `origin/handoff/audit-r10-roster` at this read.
- **Already done, out of tree.** The s8 loop now trusts only a freshly appended line. The lint
  clone was re-cloned, and the 12 ops were re-queued.

Cost:
- About 10 lines in `run_queue`: a try/except around each op writing the FAILED line and
  returning nonzero, and a missing-directory check on `--lint-clone`. Add two self-test rows.
- No new file, writer or API call. `roster_queue.py` is not a capped file.

Binding:
- One deleted directory turned into 12 ops reported landed that had not, two of them gating a
  review, found only by reading the roster back.
- About 10 lines turn that silent false result into a loud failure. That is clearly positive.
- The caller-side fix (trust only a fresh line) is correct but lives only out of tree. The tree's
  runner must not depend on every caller knowing its failure leaves no line.

Carry text (for `roster_edit.py append-carry R10-FLY-BEAT-FETCH-RACE`, citing
`triage: dev/programme/triage/s6-batch78.md#P315`): "P315 (orchestrator 2026-10-31, slip). Adds
tools/audit/seat/roster_queue.py to this group's files.
- `run_queue` (`roster_queue.py:93` at 5d4e0bcfb) writes exactly one report line per op attempted.
  Any exception in the op, or in the lint clone's `git fetch`/`git checkout` (`_git`, line 123),
  becomes `roster: <op> <group> FAILED <ExceptionType>: <message>`, and the run stops nonzero.
- A missing `--lint-clone` directory is refused before the first op:
  `roster: lint clone <path> missing; nothing applied`, rc 2.
- The runner never re-clones.
- Observed 2026-10-30/31: a deleted lint clone raised `FileNotFoundError` at line 123 before any
  report line. The caller read the previous op's line, and 12 ops were marked `#done (already)`
  that never landed (`seat-ledger.md` 2765-2769: `no report line written (rc=1)`). This group's
  own append-group was one of them.
- Self-test rows:
  - With `--lint-clone` pointing at a missing directory, the report gains the named refusal and
    rc is 2. Today it raises with no line.
  - An op whose subprocess raises gains one FAILED line naming the exception, and rc is nonzero.
  - Null: a run whose ops all push writes one `pushed` line per op, unchanged.
- One mutant: remove the per-op except, and the raising row writes no line.
- P300's `--mark` (R10-ORCH-ROSTER-SCHEMA) marks a FAILED op `#refused`. Whichever lands second
  merges main."
