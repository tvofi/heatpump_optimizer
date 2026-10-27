# Evidence — review of #2877 at f92442065832f5ccbe397882b73c79c173ab4dd7

Head measured: `f92442065832f5ccbe397882b73c79c173ab4dd7`
Base measured: `524c1896b6943b3da03d6cad61420ced31e14c9c` (the batch's stated base; also the merge base)
Worktree: `/Users/timmalmstrom/hpo-seats/r10s6/rev-2877` (detached at the head)
Snapshot: `seat-ledger-snapshot.txt`, sha256 `877df211b465c1b42636f516749735f49792ab2b96de679bb29510eb3edff60b`, taken 2026-10-27T15:20:30Z.

## Files

- `01-p197-body-vs-roster.txt` — the PR body's `## Figures` P197 line, the body's own enumerator (`grep -c P197` = 0 at origin/main and at 524c1896b and across all roster files), the correction commit message, and the corrected batch text.
- `02-check-runs.txt` — all 55 check-runs at the head, paginated: 38 success, 17 skipped, 0 non-success.
- `03-head-topology-and-body.txt` — diff scope, head parents, per-commit batch-file sizes, and the body's `## Head` / `## Red checks` as published.
- `04-ledger-classification.txt` — the `triage s7:` ledger classified from the snapshot: 287 lines, 222 plain HOLD, 45 carrying `; main <sha>`, 20 seat lines without one; the 08:13:15Z–09:38:27Z window has exactly 18 plain lines; largest plain-line gap 302 s.
- `05-beatd-carries.txt` — R10-ORCH-BEATD at 524c1896b: 208 roster groups, stage `not-started`, size `L`, 34 carries; carry index 21 (1-indexed 22) is P97(b); the batch file mentions neither P97 nor DUPLICATE.
- `06-loops.txt` — live loop-like processes at review time (7716 tick_loop.sh, 7727 wt_sync while-loop, 92999 state_docs beat, 99863 roster-loop.sh; 76559 gone), the tree's loop scripts, and the roster-loop/w71 greps.
- `seat-ledger-snapshot.txt` — the ledger copy the classification was computed from.

## Reproduced exactly (non-findings)

- The 18 plain HOLD lines at 08:13:15Z…09:38:27Z and their 5:00–5:01 spacing; four inside the 21-minute stall (08:58:22, 09:03:22, 09:08:23, 09:13:24); stall bounds 08:54:25Z→09:15:38Z.
- `seat-ledger.md:1149` = three seats restarted at 21:15Z; `seat-ledger.md:1334` = merge seat RESTART 08:19:56Z, dead since 22:16Z.
- `git show origin/main:dev/programme/rosters/wave-r10-groups.json | grep -c P197` = 0; no P197 in any roster file; R10-ORCH-BEATD stage `not-started`, size `L`.
- `roster_edit.py`'s gate: committed P204 = DEFER, refused as "is not an ACCEPT ruling (DEFER)"; ACCEPT mutant → None; absent file → "not on the roster branch or origin/main"; P999 → None. The body's mutation proof and null control reproduce.
- 208 roster groups at 524c1896b.
- Head check-runs: 55, 0 non-success; the diff is the batch file plus the delivery row.
- Pids 7716 and 99863 live; 76559 gone; `roster-loop.sh` has no `triage`/`HOLD` write; w71's two scripts have no process.

## Could not establish

- The dispatch record for this review's nonce. `$S/dispatched` (`/Users/timmalmstrom/.zcode/bus/dispatched`) holds one line for #2877, at head `6d58fa0bc` with nonce `f5ca16fa…`, and no line naming `f92442065` or `4c58667c…`; `bus.sh push-verdict` therefore refuses (see the report).
- When seat `a1c1b98c` started. The launch ledger was backfilled (ORCH-QUEUE.md:1507), so "this seat's first line" in the corrected arrival-order sentence has no fixed referent.
- The plain writer's identity and its non-ledger output.
