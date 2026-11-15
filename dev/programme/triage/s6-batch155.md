# Proposal triage, session s14, batch 155 (P566, P567)

This batch rules `s7/triage-queue-s7.txt` lines 249 and 250. Both arrived while batch 154's carry was
landing, so they are ruled together. The bar and the denominators are batch 141's.

Sources:
- origin/main `63bcdcaad8` (line numbers);
- `S/tick-loop.log` (TICK-PASS and TICK-RELAY lines) and `S/tick.txt.relay.log`;
- the read-only seat's samples in `s14/seat/relaytime/ps.log`, 20 s `ps` samples from 02:00:31Z;
- my own sampler `s14/seat/triage/s14-4/rate.log`, every 20 s from 02:22:42Z. Each sample is
  `gh api rate_limit` (core used), plus whether `orchestrator_tick.py` and `cloud_relay.sh pass`
  were running. The tick loop has no `GH_TOKEN` in its environment, so it spends the same
  keyring token (tvofi) that I read;
- the GitHub API for PR 3405's runs and check runs.

## P566: S14-RELAY-CADENCE

Verdict: ACCEPT narrowed, on (b) and (c) only. The queue line holds three options and a holder
finding, ruled separately.
- (a) is REJECTED as a default, and the local `--interval 120` should go back to 300.
- (b) is ACCEPTED narrowed: the relay cadence is decoupled inside `tick_loop.sh`, not by a
  standalone `pass --loop`.
- (c) is ACCEPTED narrowed: the memo is keyed on the body's content, not on its commit.
- The holder finding is REJECTED.
- (b) and (c) each repair an observed wrong behaviour.

Source: queue line 249 (2026-11-11T02:21:13Z, the orchestrator, with the read-only relaytime seat).

Instances:
- **The cadence claim holds.** A relay starts only at a tick pass. TICK-RELAY `started=` gaps
  this session were 11:04, 11:59, 15:39, 10:51 and 11:17 (01:05:05Z to 02:05:55Z). The tick passes
  themselves took 5:19 to 10:35 (TICK-RELAY to TICK-PASS), plus the 300 s sleep.
  - The relay often finishes early and then sits idle. The pass started at 02:20:46Z was last seen
    at 02:22:17Z (ps.log, 1:32 elapsed). It was reaped at 02:29:25Z, so it idled about 7 min. The
    pass started at 02:05:55Z ran about 13 min (ps.log pid 69749, 12:42 at 02:18:37Z).
  - A false premise would have looked like relay passes that fill the cycle. Short passes do not.
- **The API cost of (a), which nobody measured.**
  - The core budget is shared and nearly spent. `gh api rate_limit` read 4621 of 5000 used at
    02:22:29Z, and 4759 at 02:24:25Z, in the hourly window that reset at 02:24:26Z. That whole hour
    ran at `--interval 300`.
  - A tick pass is what spends it.
    - With neither the tick nor the relay running (02:28:11Z to 02:29:12Z), use rose about 36 a
      minute: that is the other seats.
    - With the relay running alone (02:27:30Z to 02:28:11Z), it rose 34 a minute.
    - Over one tick pass (02:29:33Z to 02:36:43Z), it rose 526 calls in 7.2 min. That is about 290
      over the baseline, most of it in the pass's first 3 minutes (345 to 603 between 02:30:14Z and
      02:32:16Z).
  - At 300 s, a cycle is a pass of about 6 to 7 min plus 5 min, about 5.5 passes an hour. At 120 s
    it is about 6.7 an hour, so about 1.2 more passes an hour, or about 350 more calls an hour.
  - The headroom in the last full window was about 240 calls. A false result would have looked
    like a tick pass that costs no more than the baseline, or a window with a few thousand calls
    spare.
- **(b) already exists, and it goes stale.**
  - `cloud_relay.sh pass --loop [--interval N]` is on main (line 864, default 120).
  - It ran standalone, daemonised, until 2026-11-10 21:26Z
    (`cloud-relay.daemon.log`, `pass --confirm --log ... --loop --interval 120`).
  - The loop never re-reads its own script, because bash reads a running script from its file. Only
    `update_pr.sh` runs from a levelled tools tree (P283, lines 524-545).
  - The tick loop restarts from a fresh checkout between passes (270157f35b), and that is what
    keeps the relay's own arms current. A standalone loop gives up that freshness.
- **(c): the memo can never match on a commit sha.**
  - `carry_fold_arm` writes `cloud-folded` only on success (line 843) and checks it by
    `<topic> <bsha>` (line 821), where `bsha` is the tip of `handoff-wip/<topic>-body`.
  - On each failure, `body_push.sh` keeps the refused body as a new parentless commit (line 106).
    `handoff-wip/r10-train-residue-body` took four commits in an hour: d982cc00b7 (01:20Z),
    2cfd2407be (01:34Z), ef11984257 (01:58Z) and 7d1f0419ad (02:17Z). All four have the same tree,
    6ae9f4ff2db8, and the same `BODY.md` blob, 80dc1f17dc70 (`git rev-parse <c>^{tree}` and
    `<c>:BODY.md`).
  - So a memo keyed on the body's commit would never hit. Each failing pass also costs a push.
  - The 4204 `OWED carry-fold` lines in tick-loop.log are mostly no-refusal stops, which fold
    nothing and cost seconds each. Only r10-train-residue re-runs `body_push`: tick-loop.log lines
    21266 to 21433, five passes. Its `body_push` was seen running at least 60 s (ps.log pid 9911),
    against relay passes of 1.5 to 13 min.
  - Its body already reached PR 3424 by another route: `handoff-body/r10-train-residue` 2fa8399213
    was BODIED at 01:44:40Z. Every re-run since has been waste.
- **The holder finding.**
  - In tick-loop.log, one line has a seat worktree holding a PR branch: line 21403, PR 3404's
    branch held by `s14/seat/merge/wt-3404`. The source says this happened every pass.
  - Sixteen other "checked out elsewhere" lines name the train's own `merge_train/wt/<pr>`
    worktrees, which update_pr refuses on purpose.
  - `update_pr.sh` already detaches another instrument's clean worktree under its state prefix
    (lines 63-68). It leaves a worktree outside that prefix alone, because a seat's checkout may
    be live.

Cost:
- (b): in `tick_loop.sh`, during the inter-pass sleep, reap a finished relay and start the next one
  once `HPO_TICK_RELAY_GAP` seconds (default 120) have passed since it ended. It reuses
  `relay_reap` and `relay_start` under the same `<out>.relay.lock`. The tick keeps `--interval 300`.
  - The relay's own API cost is the 34-a-minute baseline: it mostly lists refs with git, which is
    not REST.
  - Self-test:
    - a relay that ends during the sleep is followed by a new one after the gap, with no tick pass
      between them;
    - the null control: a relay still running at the gap starts none;
    - a mutant that drops the in-sleep start fails the first case.
- (c): in `carry_fold_arm`, a failed fold or `body_push` records
  `<topic> <stop sha> <BODY.md blob> <handoff/<topic> tip> <refusal line>` in `cloud-fold-failed`.
  A pass skips a stop whose stop sha, blob and code tip all match a record, and prints the
  recorded refusal once as `OWED carry-fold <topic> unchanged since <utc>: <line>`. A change to
  any of the three re-runs it.
  - Self-test:
    - the train-residue shape (a new kept commit with the same blob) is skipped;
    - a changed blob, or a moved code tip, re-runs;
    - the null control: a stop with no record runs as today;
    - a mutant keyed on the commit sha fails the first case.
- Neither file has a row in `tests/structure_budgets.json`.

Binding:
- (a) costs about 350 calls an hour against about 240 of headroom on the shared core budget. When
  that budget runs out, the train, the tick and every seat's `gh` stop together. (b) gets the
  relay's latency gain without the extra tick passes.
- A standalone `pass --loop` is rejected because it runs stale arms whenever main moves them, and
  nothing alarms on it.
- The holder finding is one instance. Detaching a worktree outside the instrument's own prefix
  could detach a live seat's checkout.

Routing:
- (b) goes to R10-TICK-RESIDUE, which owns `tick_loop.sh`. It was handed off as PR 3425, so the
  carry has the PART 2 prefix. Carry file: `b155-P566b.txt`.
- (c) goes to R10-REVIEW-DISPATCH-RESIDUE, which owns `cloud_relay.sh`. It is `not-started`, so the
  carry is plain. It sits beside P546's carry, which changes the same arm (disposing of a
  `handoff-wip` stop), and the two should be built together. Carry file: `b155-P566c.txt`.

## P567: S14-STALE-GATE-MULTI-SUITE

Verdict: ACCEPT narrowed. This is a class barrier: 3405, 3383 and carry 13's five instances on
R10-TRAIN-RESIDUE. Remedy (a) amends carry 13 rather than adding a separate check. Remedy (b) is
accepted at the corrected fix site: the per-name overwrite in `policy_refusal`, not a switch to
`classify_at`.

Source: queue line 250 (2026-11-11T02:29:21Z, the orchestrator, PR 3405 at 068074f0).

Instances:
- **Why nothing re-ran the deferral suites.** The source left this unverified. I checked it:
  - The code run 42933054497 was a `workflow_dispatch` whose actor was `github-actions[bot]`
    (`gh api .../actions/runs/42933054497`). GitHub starts no `workflow_run` from an event its
    `GITHUB_TOKEN` caused, so `gate-sweep.yml` never ran for it (ci.yml line 359).
  - The in-run `sweep-self` job that covers that case was absent from the run. Its jobs list has
    `gate` and `budget-raise-gate` only.
  - A dispatched run executes the branch's `ci.yml`, and 3405's head 068074f0 does not contain
    45155d068e (`sweep-self`, landed 2026-11-10 02:29Z): `git merge-base --is-ancestor` exits 1.
  - So neither sweep ran. It was not a sweep that failed.
  - 9 of the 28 open PRs have heads without `sweep-self`: 3377, 3381, 3382, 3383, 3387, 3388, 3392,
    3405 and 3420. 3383 is one of the named instances.
  - A false premise would have looked like a sweep-self or gate-sweep run at that head that
    re-ran nothing.
- **3404 is not this class now.** Its one red gate (run 42945740958, `CI edit`, actor
  hpo-author[bot]) is the designed deferral. Its code run 42945740877 was `in_progress` when I read
  it. An App actor does fire `workflow_run`, so gate-sweep will judge it.
- **GitHub blocks on any red.** 3405 was BLOCKED with rollup FAILURE while the code run's gate was
  success at 01:30:49Z. So carry 13's "judge `gate` by the newest check-run" alone would leave
  the train attempting a merge GitHub refuses. The hand cure, `gh run rerun --failed`, is what
  turns GitHub green: 3405's five gates read success from 02:04:45Z to 02:29:57Z.
- **The misdiagnosis.** `policy_refusal` builds `last[name]` from `statusCheckRollup` by overwrite
  (`merge_train.py` line 2798). With five red `gate` entries and one green, the result depends on
  which entry the rollup lists last. "every required context is green" (line 2814) is the green
  one listed last.
  - `classify_at` (line 1892) reads check runs per run, so it disagrees, as the source saw.
  - A false premise would have been a rollup with one `gate` entry. 3405's head listed seven.
- **The step that exists.** `unstale` (line 3633) re-runs before a merge attempt only a check-run
  pending over a completed run.

Cost:
- (a), as an amendment to R10-TRAIN-RESIDUE carry 13: `unstale` also re-runs, once per run per
  head, the failed jobs (`gh run rerun --failed`) of each workflow run whose `gate` check-run at
  `<h>` is red when two conditions hold. Then the train waits, and does not skip.
  - **The first condition.** The red is a deferral (its output title is gate.py's deferral line)
    or comes from a run whose `sha=` names another head.
  - **The second condition.** A `gate` check-run at `<h>` is success, from a completed run.
  - `classify` treats that shape as WAIT, not RED, until the re-run concludes. This replaces
    carry 13's "judge by newest", which GitHub's rollup would contradict.
  - A genuine red at the head, or a red with no green gate beside it, stays RED.
  - Self-test:
    - the 3405 shape (five deferral reds, one green code gate) re-runs the five and waits;
    - the null control: a red code gate with no green stays RED and re-runs nothing;
    - a second pass at the same head re-runs nothing;
    - a mutant without the green-beside condition fails the null control.
- (b): `policy_refusal` treats a required context as red when any rollup entry of that name is
  red, and as pending when any is pending, which is the rule GitHub's rollup applied. A red that
  (a) re-runs is reported as `gate red at <h8>: deferral run(s) [...] re-run`, not as a missing
  review.
  - Self-test:
    - a rollup with a red `gate` before a green one, and one with it after, both read red;
    - the null control: all-green with BLOCKED still reads as a missing review;
    - a mutant restoring the overwrite fails one of the two orders.
- `merge_train.py` has no row in `tests/structure_budgets.json`.

Binding:
- The class decays only as the nine pre-`sweep-self` heads merge, and one of them, 3405, sat on
  the critical path for about 2 h.
- Re-running in the train is the barrier for heads that predate the CI one, and it costs one
  branch in an existing step.
- A main merge into those nine is not proposed: fixers do not merge main without a conflict.

Routing: one carry to R10-TRAIN-RESIDUE, which owns `merge_train.py` and holds carry 13. It was
handed off as PR 3424, so the carry has the PART 2 prefix and names itself carry 13's amendment.
Carry file: `b155-P567.txt`.
