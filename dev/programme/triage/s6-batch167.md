# Proposal triage, session s14, batch 167 (P581)

This batch rules `s7/triage-queue-s7.txt` line 264. The bar and the denominators are batch 141's.

Sources:
- origin/main `a7628041dc`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster` `400a014603`.
- The beat opener's log `open-driver/open-driver.log` in the state dir: 1,556 lines, with 25
  `RESULT` lines from 2026-11-10T09:50:33Z to 2026-11-11T06:12:15Z.
- `s14/sweep.md`, its `beat rotated` lines.
- No GitHub API calls.

## P581: BEAT-CHECKOUT-ROTATION-BY-HAND

Verdict: ACCEPT, narrowed. It is not a separate rotate instrument that rewrites launch files.
`beatd` restarts itself in place, on its own branch-backed checkout, between job instances. That
is the mechanism P552 (`s6-batch145.md#P552`) gave `tick_loop.sh`'s `fresh_check`. The carry
goes to R10-SEAT-IDENTITY-P5.

Source: queue line 264, 2026-11-11T06:12:41Z, orchestrator s14.

Instances:
- **The refusal.** `pr_args.sh:188` refuses `STALE CHECKOUT <h> behind origin/main <o> by <n>
  commit(s) touching tools/audit/seat tools/pr` when the checkout holding `open_pr.sh` is
  behind on those paths.
- **The opener's record.** `grep -c 'STALE CHECKOUT' open-driver.log` gives 8. Each is a
  `RESULT ... rc=1` line: **8 of the 25 open attempts (32%)** in 20.4 h were refused for this
  cause alone.
  - The 8 fall at 11-10T10:55, 11-10T11:21, 11-11T01:21, 11-11T03:24, 11-11T03:59, 11-11T06:10
    (two) and 11-11T06:12Z.
  - Of the refused topics that have opened since, the delay from refusal to the next `rc=0`
    `RESULT` for the same topic was **36 min** (`r10-hotfix-prepr-readset`) and **48 min**
    (`r10-plan-page-residue`).
  - The other 5 have not opened yet. 3 are `r10-process-slim-p2`, which is also blocked on its
    carry fold (P580), so their delay is not counted here.
- **The hand rotations.** `s14/sweep.md` logs two: 04:00:27Z and 06:12:41Z. The proposal's
  02:04Z rotation is not in that file and is not counted. Each logged rotation was followed by an
  opener backoff reset (04:03:13Z) or by a tick-loop rotation (06:13:50Z). The orchestrator's
  ~10 min per instance is the source's estimate, not a measurement.
- **Why `beatd` does not restart itself today.**
  - `beatd.py:488-496` reads only `STALE-CODE behind=<n>` and counts every commit on main, not
    the paths `pr_args.sh` checks. It is an alarm, not a trigger.
  - `beatd.py`, `beat_jobs.py` and `beatd.jobs.json` contain no self-restart path (`beatd.py`'s `restart` hits, lines 24, 284 and 771-773, are job restarts)
    (`grep -c 'STALE-CODE|STALE CHECKOUT|ff-only|RESTART|exec '` gives 0 in `beat_jobs.py`).
  - The tick loop's `fresh_check` (`tick_loop.sh:95-112`) is the in-tree precedent. When behind on
    its own paths, with a clean tree and the relay lock free, it moves its checkout to
    origin/main and `exec`s itself. P552 extended it to a clean branch-backed checkout with no
    commit outside origin/main.
- **Rule applied per instance.** A beat that restarts itself on main, once it is behind on
  `tools/audit/seat` or `tools/pr` and no job instance is running, reaches each of the 8
  refusals before the opener's next attempt. The opener retries on its backoff; it does not
  wait for a hand step. All 8 are removed. The measured delays of 36 and 48 min fall to the
  beat's pass interval plus one opener backoff step.
- **Null control.** 17 of the 25 `RESULT` lines carry no `STALE CHECKOUT`, including all 14
  `rc=0` lines. So the count does not read every refusal as this cause.

Cost:
- `beatd.py`, 1,266 lines. It has no row in `tests/structure_budgets.json` at `a7628041dc`; no
  capped file.
- About 35 production lines, following `fresh_check`'s shape:
  - a path-filtered behind count on `tools/audit/seat` and `tools/pr`;
  - the refusal conditions: a dirty tree, a commit outside origin/main, a job instance running,
    or `bash -n`/`py_compile` refusing main's `beatd.py`;
  - `git checkout -q -B <branch> origin/main`, then a re-exec with a once-per-start guard;
  - a `BEAT-STALE` line when a refusal persists into a second pass.
- About 40 self-test lines:
  - behind on the paths and idle restarts;
  - behind only off the paths does not;
  - a running instance defers to the next pass;
  - a dirty tree or a local commit refuses with its why;
  - a broken main `beatd.py` refuses.
- No new file and no launch-file rewrite. The checkout path does not change, so `beatd.tools`,
  `orch-checkout` and the launch files stay valid.

Binding:
- **ACCEPT, narrowed, as a carry to R10-SEAT-IDENTITY-P5.** That group owns `beatd.py`,
  `beat_jobs.py` and `beatd.jobs.json`. It is not started, with 5 carries, and its `after` is
  R10-TICK-RESIDUE. The measure is 32% of open attempts, over the 20% bar for adding to an
  instrument. The two measured delays were 36 and 48 min each.
- **The proposed form, a rotate instrument rewriting `beatd.tools`, `orch-checkout` and two
  launch files: REJECT.** It costs a new file and four local path rewrites per run. The in-place
  restart removes the same 8 refusals and rewrites nothing. Rotating to a new worktree is needed
  only when an instance must keep running from the old tree, and the restart waits for no
  instance instead.
- The hand procedure in `s14/sweep.md` stays the orchestrator's until the carry lands.
