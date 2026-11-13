# Proposal triage, session s14, batch 177 (P594-P596)

This batch rules queue lines 273-275 (the orchestrator's intake) and the P588 follow-up hour of the
gh logging shim, 2026-11-11.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster branch at `988e5cf6ba` or later.
- The Actions API for #3446's head `4cc5d8b962`, and for `gate-sweep.yml`'s runs.
- `gh-calls.log` over 07:40-08:41Z, and `gh api rate_limit` at 08:44Z.

## P594: GATE-SWEEP-QUEUE-WAIT

Verdict: ACCEPT, narrowed, as a carry on R10-GATE-DEFER-BARRIER (stage not-started, no
`handoff`/`handoff-wip`/`dispatch` ref in flight). That group owns every reader of the gate
conclusion in `merge_train.py`.

Source: queue lines 273 and 274. The train skipped #3446 as "red at its head: gate", and
`classify` still read RED at 08:40Z.

Measured at #3446's head:
- Gate check runs: two edit-run suites failed, at 07:51 and 07:54Z. The deferring code run's gate
  was re-run by hand at 08:38Z. The review run's gate succeeded at 08:31:14Z.
- `latest_runs` (`:400`) keeps the latest gate of each suite and lets the worst stand. That is by
  design (A5: an older suite's red is never hidden behind a newer green). The deferred reds are
  meant to be re-judged by `gate-sweep.yml`.
- The sweep fired on time: run 42987689816 was created at 08:31:17Z, 3 s after the green gate.
  Its `sweep` job did not **start** until 08:41:55Z, 10 min 38 s later. That is the account's
  runner queue under the concurrency cap.
- The train waits for that re-run for `SWEEP_SETTLE_POLLS = 1` poll (`:584`, 240 s).
  `SWEEP_SETTLE_SECONDS` (`:818`) was set from one measured 62 s start (`:816-817`).
- Had the sweep never fired, no gate-sweep run would exist after 08:31:14Z. One does, and it is
  queued.

So the defect is not that `classify` misreads a deferral. The settle window assumes a sweep starts
within one poll, and under a queued runner it does not. The addendum's proposal (line 274) is
narrowed away: reading a deferral-only red as superseded would need each red gate's log text, and
it would weaken A5, which the sweep already serves.

The fix: while the only red is GATE and a `gate-sweep.yml` run created at or after the newest
green gate suite's `completed_at` is `queued` or `in_progress`, the red is a wait. The read is
one `actions/workflows/gate-sweep.yml/runs?created=>=<t>` listing per poll. `wait_ci`'s polls
still bound it (TIMEOUT). With no such run, the red stands after the one settle poll, as today.
The same rule goes in `classify_at`'s one-read path (`sweep_settling`, `:566`).

Self-test:
- A queued sweep created after the green keeps the red a wait.
- A completed sweep with the red unchanged reads RED.
- Null control: no sweep run reads RED after the settle poll, as today.

What it costs and what it saves:
- **Cost:** about 25 lines and three checks.
- **Benefit:** the orchestrator counts this as the third gate-deferral skip this session (#3398,
  #3445, #3446). Each skip cost a hand re-run or a `--front` re-add.
- It clears the 20% bar as a carry.

## P595: A5-ROLLUP-PAGES

Verdict: ACCEPT, as a carry on R10-GATE-DEFER-BARRIER. `platform_gate` is a reader of the gate
conclusion (A5 item 3), in `merge_train.py`.

Source: queue line 275. The train skipped #3355 with "more than 100 contexts: not read whole".

Measured:
- #3355's head `dee7a1fa45` carries 114 rollup contexts (`statusCheckRollup.contexts.totalCount`).
- `ROLLUP_Q` reads `contexts(first:100)` (`:460`), and `platform_gate` returns `unread` on
  `hasNextPage` (`:480`). The train refuses any disagreement, so a head that collects re-runs past
  100 contexts can never merge by the train. The only remedy is a fresh head.

The fix: page the rollup with `after:` while `hasNextPage` (bounded, say 5 pages), and judge the
union. A short page is still `unread`.

Self-test:
- A two-page rollup whose required gate is on page 2 reads green.
- Null control: a single page reads as today.

What it costs and what it saves:
- **Cost:** about 15 lines and two checks. One extra GraphQL call happens only at heads with more
  than 100 contexts.
- **Benefit:** one observed instance, and its remedy (remerge main) costs a full CI cycle.
- It clears the bar as a carry, because the refusal is permanent at that head.

The slip in the same line, the shim rebound to another checkout's `gh_comment.py`, is a second
instance of P591. P591 sits on R10-GH-READ-RESIDUE, which is carries-open with part p2 in flight.
The instance is recorded on P596's new group below, not on that group.

## P596: TICK-CONDITIONAL-READS

Verdict: ACCEPT, as a NEW group R10-GH-READ-RESIDUE-P3. It is a not-started sibling, by the
orchestrator's 2026-11-11 rule against landing carries on a group with a part in flight.
- R10-GH-READ-RESIDUE owns the gh-read seam. It is carries-open, and
  `handoff-wip/r10-gh-read-residue-p2` is in flight.
- R10-TICK-RESIDUE owns `orchestrator_tick.py`, and its PR #3425 is open.
- The new group runs after both.

Source: the P588 follow-up. The shim has been live since 07:39:27Z.

Measured over 07:40-08:41Z with `gh_calls.py --top --since 2026-11-11T07:40:00Z`: 1876 logged
gh invocations.
- **orchestrator_tick:** 798 (43%), at about 6 passes an hour. Its REST reads are:
  - `issues/{n}/comments?per_page=100` (`:709`): 218 an hour. Every open PR is re-slurped every
    pass.
  - `commits/{sha}/check-runs?per_page=100` (`:378`): 205 an hour over 44 distinct shas, 27 of
    which were read 5 or more times.
  - `pr view` (152) and `api graphql` (76) are in the GraphQL bucket.
- **worktree_gc.sh:** 283, three runs at 07:48, 07:58 and 08:08Z, each one `gh pr list` per branch
  worktree. `gh pr list` is GraphQL, not core.
- **merge_train:** 193 (`actions/runs` 72, `rulesets` 38).

The core bucket is what binds. `rate_limit` at 08:44:09Z read core used=1390 since 08:25:02Z, about
4390 an hour against a 5000 cap. That is above the 07:25Z baseline (about 3380 an hour). GraphQL used
130 in the same window, about 410 an hour against 5000. So worktree_gc and `pr view` are not worth
cutting.

The cut is conditional GETs on the tick's two per-PR REST reads.
- **304s are measured free.** One ETag-conditional `issues/3446/comments` read returned
  `HTTP/2.0 304 Not Modified`, with `gh` exiting rc=1. Two trials of 5 conditional reads moved core
  `used` by 0 and 3. The second trial's 3 matches concurrent callers. In the same trials, 5 plain
  reads moved it by 6 and 5.
  - Had a 304 cost a call, the conditional deltas would have read 5 or more.
- The fix: one helper on `TickRun.gh`. For a single-page GET it stores the ETag and body under
  `$HPO_STATE_DIR/gh-etag/`. It sends `If-None-Match` and reads `gh api -i`'s status line. A 304
  serves the stored body. A 200 replaces it. Any other failure is `UNREADABLE`, as today.
  - The comment slurp drops `--paginate --slurp` for a first page under 100 comments, and falls
    back to the full read when the page is full.
  - The `#201`/`#3394` since-cursor reads are untouched.
- **Removed:**
  - At most 423 - 76 = 347 core calls an hour, if only the first read of each sha (44) and PR (32)
    in the hour cost anything.
  - At least about 210 an hour, if every PR's comments and every sha's runs changed on every
    second pass.
  - That is 5-8% of the measured core rate, or about 35-55% of the 610 an hour of headroom left
    under the cap.
- The self-test pins three cases:
  - a 304 serves the stored body with no second read;
  - a 200 replaces it;
  - null control: with no ETag stored, the plain read is made.

**Folded into the same group** (the gh-read seam's not-started part):
- **The shim's caller field.** The shim keeps the first 80 characters of argv (`seat-gh:7`). An
  absolute path therefore loses its script name: the hour logs 798 calls as
  `.../tools/audit/seat/orch` and 100 as `.../beat-wt-a7628041/tools/audit/seat`. The fix: log the
  script's basename first, then the cut path.
- **P591's second instance** (queue line 275): the shim was rebound to `tools-wt-45adb0c3` while the
  train ran from `tools-wt-63bcdcaa`, and #3398's record comment was refused. Build P591's
  multi-checkout fix here if R10-GH-READ-RESIDUE-p2 does not.

**Still dark to the shim:**
- Core used 1390 in 08:25-08:44Z against 458 logged invocations, of which part are GraphQL. The
  shim logs one line per invocation, so `--paginate` pages are uncounted. Even so, at least about
  two thirds of core calls are not attributable.
- Every local long-runner checked is covered:
  - merge_train (pid 34433) and beatd (63651) have `~/.local/state/hpo/bin` on PATH;
  - tick_loop's children log as `orch`;
  - this Claude session's `gh` is the shim;
  - wake.sh and the dispatch seat's watch.sh call no `gh` (wake.sh uses `git ls-remote`).
- The dark share is therefore cloud seats on the shared token, plus paginated pages. Measuring them
  needs a per-request count (`X-RateLimit-Used` read by the shim) or a cloud-side shim. That is a
  separate proposal, not ruled here.

What it costs and what it saves:
- **Cost:** about 50 lines in `orchestrator_tick.py` and 5 in `seat-gh`, plus four checks.
- **Benefit:** 5-8% of the core bucket at 88% of its cap. It is the largest attributable REST cut,
  and the caller field makes the next attribution exact.
- It clears the 20% bar on headroom rather than on the total.
