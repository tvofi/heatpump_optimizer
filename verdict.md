Fix review: blocked 7e312ed2e482faf04be7eb27f38d92aef2b6fae5 carry-missing: not carried to R10-ORCH-MACHINERY or R10-RCA-HANDOFF-SLIP

bus-nonce: a4ec461023169a36b86bfa1ba9ac24e7

Round: first review of #2557 (R10-RCA-ORCH-CONTINUITY). Reviewed at head `7e312ed2e482faf04be7eb27f38d92aef2b6fae5`, from a detached worktree at that SHA. `fix-review.md` is current: its three-dot diff from the merge base to origin/main is empty.

## Block

- **carry-missing (`fix-review.md` step 10, `finding-propagation.md` Enforcement).** The body's `## Forward-carry` routes two findings to live roster groups. Neither is in the tree:
  - `Carry: R10-ORCH-MACHINERY` asks that the machinery design name `pulse.py` as `beatd status`'s off-host complement. That group is at `resume.stage: not-started`.
  - `Carry: R10-RCA-HANDOFF-SLIP` warns that the standing orphan backlog saturates the `handoff-no-pr` age thresholds (123 of 153 hourly samples), unless they are keyed to arrivals after the last opening. That group is `in-progress`.

  Both change what a stage that has not finished must do. At `origin/handoff/audit-r10-roster` `7003af220`, neither group's `carry` list or brief contains `pulse`, `ORCH-CONTINUITY`, `2557`, `backlog` or `owed input`, and R10-RCA-HANDOFF-SLIP has 0 carries. The body also names no roster-branch SHA for the reviewer to open. A carry that exists only in the body records the finding but does not propagate it. The fix is `tools/audit/seat/roster_edit.py append-carry` on both groups, with the control (the replay's 123/153 first-cut figure against the arrival-keyed rule's 1 window) and a re-measure instruction, then the roster SHA named in the body. Carry: R10-RCA-ORCH-CONTINUITY

## Findings

- Neither `Carry: #201` line (the barrier owner's-call, and the `failure_logs.sh` GraphQL-403 friction) is in `dev/programme/carries/carry-201.json`. It is byte-identical at origin/main, the roster branch and the head, and contains no `pulse`, `ORCH-CONTINUITY`, `off-host` or `failure_logs`. Under `finding-propagation.md`, a carry to an issue lands in that issue's carry file. Since #201 is the owner's thread, writing there may be the intended destination for an owner's call. The fixer should either add both lines to carry-201.json or say in the body why the thread itself is the destination. Carry: R10-RCA-ORCH-CONTINUITY
- The body says "No policy file, lint class or rules entry is added (decision 0012)". The owner revoked 0012 (#201 comment 6322712314, as the brief cites it), so that rationale is stale. The record itself (`dev/audit/rca/R10-RCA-ORCH-CONTINUITY.md`) cites no 0012 constraint: its barrier options A and B rest on account configuration and on 0013's pinning. So only the body sentence needs re-wording, and the fixer should say whether the revocation opens a barrier form the record ruled out. Carry: R10-RCA-ORCH-CONTINUITY
- The body figure `carry_audit.py check --body <this body>`: `4 routed` does not re-derive against the body at this head, which has five `Carry:` lines and reads `5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)`. The re-taken body added the `failure_logs` friction line without updating the figure. Carry: R10-RCA-ORCH-CONTINUITY
- One mutant beyond the body's M0–M7 survives: dropping the `o.get("rc") not in (0, 1)` clause from `judge_opener` (R11) leaves `--self-test` at 21 checks, 0 failed. In practice the summary-line check covers it. `bus.sh` `die`s to stderr before printing the `orphans:` summary, and pulse reads stdout only, so an rc of 2 or more never comes with a summary line. The self-test's rc=3 fixture also prints no summary. It is a redundant guard, not a hole, but it has no fixture of its own (rc 3 with a summary line). Carry: dismissed: redundant guard, equivalent under bus.sh's die path

## Evidence

- Head: `ev/HEAD.txt`. The PR body's `## Head` names `7e312ed2e482faf04be7eb27f38d92aef2b6fae5`, matching the PR's head at review time.
- Merge: `git merge-tree --write-tree origin/main 7e312ed2…` (origin/main `1ebc737e7`, which the head already merges) gives tree `791a3633a0c3e8eda4265336ca754319809fea07`, exit 0, no conflict.
- Mutation proof, re-run in a copy at the head (`ev/mutants.txt`), all reproduce as the body states:
  - M0 null: 21 checks, 0 failed.
  - M1: 4 failed, the four named.
  - M2, M3, M5, M6, M7: 1 failed each, the named check.
  - M4: TypeError, exit 1.
- Mutants of my own:
  - R8 (opener bound dropped): 1 failed.
  - R9 (verdict bound to any age): 6 failed.
  - R10 (state `st < mt` dropped): 5 failed.
  - R12 (summary-line check dropped): 1 failed.
  - R13 (state bound to any age): 1 failed.
  - R14 (verdict unreadable guard dropped): TypeError, exit 1.
  - R11 survives (Findings f4).
- `python3 -I tools/audit/seat/pulse.py --self-test`: `pulse self-test: 21 checks, 0 failed`, exit 0 (`ev/pulse-selftest.txt`). This matches the body.
- `selftest_wiring.py --check`: `39 self-testing, 39 wired, 0 unwired`. This matches the body's re-take.
- `fold_ledger.py check`: 43 classes, 738 instances, 114 rca entries, 0 violations. This matches the body.
- `tmp_paths.py --check`: 0 refused.
- Replay (`dev/audit/harnesses/pulse_replay.py --since 2026-10-15T00:00Z --until 2026-10-21T08:00Z`, `ev/replay-default.txt`):
  - 609 samples.
  - Opener: 25 samples in 1 window, 2026-10-16T08:45Z..14:45Z.
  - State-beat: 37 samples in 5 windows (10-17 11:15Z..15:15Z; 10-19 11:15Z..11:45Z, 13:15Z, 15:00Z..16:45Z, 19:00Z..20:45Z).
  - This is identical to the body, and runs in 20 s.
  - Null control (`--opener-h 1000 --state-min 100000`, `ev/replay-null.txt`): 0 windows on both arms. This matches the body.
- State-beat bound (`ev/state-latency.txt`), with the latency of each first-parent main move to the next `handoff/audit-r10-plan` commit, from 2026-10-15T18:08Z to 09:00Z on 10-21:
  - 215 moves, 198 within 30 min. The smallest of the other 17 is 49.2 min. These re-derive.
  - The body's `p90 19.2 min` does **not** re-derive: my definition gives p90 9.3 min. I could not recover the body's definition. The bound argument rests on the 198/17/49.2 figures, which do re-derive, so this is not verified rather than wrong.
- Live run time: 7.4 s and 7.0 s over two runs (`ev/pulse-live.txt`), against the body's 7.7–8.2 s. That is consistent, from a different machine. At 21:12Z the live board read verdict STOPPED (#2524 blocked `c071fa5f` 6.3 h), exit 1. That is the instrument working on today's board, not a statement about this PR.
- Body figures I could not re-derive from this seat: the per-instance idle hours (3.0/4.0/1.0/7.7) and the #201 takeover-note timestamps. Each rests on #201 comments, which I did not re-read in full. The cost-test conclusion (3.0 h/day against 3.3 min/day) holds with large margin under any of them.
- Process state (a) and the class search were checked against `root-cause.md` sections 1–5. The record has a named cause, a state with evidence, a class search (six consumers, three covered, three dispositioned), a cost test with numbers, and a countermeasure with a demonstration that fails on the defect (the I4 fixture and replay windows) and passes once fixed, plus a null control. The barrier is correctly left as the owner's call, since the class is an audit class with four instances in round 10.
- CI at this head (`ev/check-runs.tsv`, read from the check-runs API at 21:11Z–21:15Z): many runs were still queued or in progress. Red so far: `nightly-status` only, from scheduled run 39563978649 (mutation-nightly and slow). The diff touches `governance.yml`, so the body owes it an answer, and `## Red checks` answers it with that same run, with a cause and a fix (#2548 for slow, the mutation lane's owner for mutation-nightly). The job log for `nightly-status` (119486581159) states, for `main-protect`, that it is not a required check and does not block.
- `instrument-self-tests` (119486581156), the job this diff adds the `pulse.py --self-test` step to, concluded success at 21:17:56Z.
- CI completion: this verdict's block is carry-missing, not root-cause-unanswered, so it was posted without waiting for every workflow at this head to conclude. The workflows still running when it was written are listed in `ev/check-runs.tsv`.
- Policy check: the 0012 sentence is in the body only, see Findings f2.
