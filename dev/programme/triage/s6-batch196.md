# Proposal triage, session s14, batch 196 (P620)

Sources:
- origin/main `ee64358be7`. Every line number below is at that commit.
- One REST read, 2026-11-11 about 12:50Z: `actions/runs?event=workflow_dispatch&per_page=100`,
  filtered to titles `CI code pr=...`: 43 runs, 2026-11-10T00:39Z to 2026-11-11T12:46Z.
- The orchestrator's manual break, `s14/unstick-3445.log` (9 lines, 12:43-12:45Z).

## P620: HOTFIX-GATE-REDISPATCH-LOOP

Verdict: ACCEPT, as a new hotfix group R10-HOTFIX-GATE-REDISPATCH-LOOP (M, lane C, severity high,
opus fixer and reviewer). It blocks every merge whose head has an edit-run red gate, so the bar is
the hotfix route, not the proposal bar.

Source: triage queue line 298, 2026-11-11T12:44:01Z, orchestrator s14: TRAIN LIVELOCK on #3445,
rule first. The mechanism lines came from the unstick seat, relayed by the orchestrator; both are
re-read below at `ee64358be7`.

Instances:
- **(a) A cancelled run becomes the gate's source.** `fresh()` in `tools/ci/gate.py:195-205` orders
  candidate runs by their jobs' latest `starts`, then id. The source loop (`:206-223`) takes the
  first run whose jobs are all `completed`; a cancelled run's jobs are `completed`, and nothing in
  `gate.py` names cancellation. Its conclusion is then read as the verdict (`:232-233`, `st[1] !=
  "success"`). Observed: the orchestrator cancelled dispatch 43022147048 at 12:43:45Z, re-ran the
  gate of 43013039961, and that gate concluded `failure` at 12:45:38Z (`unstick-3445.log`).
- **(b) The sweep re-dispatches after its own re-run.** `Sweep.fresh()` in
  `tools/ci/sweep.py:191-213` counts a workflow_dispatch run as the head's fresh judge only when its
  `created_at` is at or after the stale gate's `completed_at` (`:194-195`). Re-running an old
  pull_request or pull_request_review gate moves that gate's `completed_at` past every earlier
  dispatch, so the next sweep finds none and posts a new dispatch (`:206-212`), whether or not a
  dispatched run at the head already succeeded.
- **Measured: repeat code dispatches at one head.** Of the 43 `CI code` dispatch runs, 32 heads had
  one; 6 heads had more:

  | head | PR | dispatches (start time UTC, conclusion) |
  |---|---|---|
  | `4cc5d8b9` | #3446 | 08:42 success, 09:36 success, 10:18 success, 11:06 success, 12:16 running |
  | `7fb8680c` | #3445 | 09:24 success, 11:34 failure, 12:38 cancelled, 12:46 running |
  | `068074f0` | #3405 | 00:39 success, 10:20 success |
  | `2557c7ce` | #3447 | 08:57 success, 09:51 success |
  | `dee7a1fa` | #3355 | 03:47 success, 04:44 success |
  | `416afe9b` | #3444 | 08:19 failure, 09:29 failure |

  10 of the 43 dispatches (23%) were started at a head where a dispatched code run had already
  succeeded. The median successful code run took 51 min (27 runs, start to last update), so that is
  roughly 8.5 runner-hours in about 36 hours, on a runner pool the orchestrator reports saturated.
  #3446 alone has run its full code suite five times at one head.
- **Null control.** 26 of the 32 heads (81%) got exactly one dispatch, so the dispatch path itself
  works; the repeats cluster on heads whose old edit-run gates were re-run. #3444's two failures
  are not the loop: a failed code run is correctly re-judged.

Cost:
- Two pinned programs: `tools/ci/gate.py` (915 lines) and `tools/ci/sweep.py` (341 lines), each with a
  self-test arm and a null arm.
- A merged change under `tools/ci/` makes every open PR whose base predates it stale-pinned
  (`sweep.py:177-188`), so the merge itself costs one fresh dispatch per open PR, once. The fixer
  says so in the body; the orchestrator times the merge.
- One M opus fixer and an opus review.

Binding: a merge-blocking livelock that also spends about 23% of the code-dispatch runner time on
repeats. The fix must be the narrow one below; widening the gate's source rule beyond cancellation
would move every PR's verdict.

The fix:
1. **CANCELLED-NOT-A-SOURCE** (`gate.py`). A run whose unit's jobs concluded `cancelled` is not a
   source for that unit; the loop falls through to the next run, as it does for a deferred
   (all-skipped) unit at `:217-218`. Self-test: a newer cancelled run and an older green run at the
   head read green (red at `ee64358be7`). Null arm: a newer failed run over an older green one still
   reads red.
2. **ONE-FRESH-JUDGE-PER-HEAD** (`sweep.py`). `fresh()` counts any workflow_dispatch run at the
   head that is in progress, queued or concluded success as the fresh judge, whatever its
   `created_at`; it dispatches only when none exists. Self-test: a gate whose `completed_at` is after
   a successful dispatch's `created_at` dispatches nothing (dispatches at `ee64358be7`). Null arm:
   with only a failed or cancelled dispatch at the head, it still dispatches once.
