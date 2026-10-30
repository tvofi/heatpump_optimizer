# Proposal triage, session s7, batch 51 (P249-P253)

Five entries, all filed by the orchestrator on 2026-10-28. V163-V166 were filed after the 12:42Z power loss, and V167 came from the #2910 round-2 reviewer.
They are quoted from `proposals.md` as it stands. The owner approved V163-V166 as decision cards.
That approval makes each one worth triaging, but it does not exempt any of them from
`proposal-triage.md`'s bar. The owner's correction of the same day still governs: "triage should
still do cost/benefit and is allowed to reject poor proposals".

Facts were read at origin/main `f844df1fe750d5e420af0d1555f4b9472a740413` and at the live roster,
`origin/handoff/audit-r10-roster` `c3f563fdc6e572b7b32a49816a7d88213ba2bf49`. Process and load
figures were read on the orchestrator's host between 16:03Z and 16:08Z.

## P249: run PR opens and updates concurrently, up to the four heavy slots

Verdict: REJECT. The proposal asks for concurrency that is already running, and the slots it would
fill are already full.

Source: `proposals.md` V163 (orchestrator, owner-approved card, 2026-10-28T16:05Z).

Instances:
- **The slot pool was full when this was read.** At 16:03Z, `python3 tests/gate_lock.py slot-status`
  read `4/4 slots held [0:prepr-39273(live), 1:prepr-56770(live), 2:prepr-60526(live),
  3:prepr-37510(live)] queue=-`.
- **Opens were already concurrent.** `ps` at the same time showed two `open_pr.sh` runs
  (`r10-cop-gate`, 25 min old, and `r10-orch-beatd`, 14 min old) and two `update_pr.sh` runs
  (`fix/r10-rca-closure-argv` and `fix/r10-rca-friction-residue`). So "the opener runs serially"
  was false at the time of reading.
- **The cap is mechanical.** `tests/gate_lock.py:102` sets `HEAVY_SLOTS = 4`. A fifth prepr
  queues on the pool's ticket FIFO rather than running.
- **The box is saturated.** `uptime` read load averages of 64.09, 75.32 and 67.71 on `sysctl -n
  hw.ncpu` = 8 cores.
- **Opens take less time than the filing says.** From the creation time to the last write of each
  `$HPO_STATE_DIR/pr/<topic>/p1.log` that opened a code topic today: r10-rca-headmoved 13 min,
  r10-roster-freeze-close 16 min, r10-dependabot-setuptools 23 min, r10-rca-closure-argv 30 min.
  The filing says 30-60 min.

Cost: a driver that fans out past what runs now gains nothing, because the pool admits four runs.
Every further concurrent run adds contention on eight cores at a load of about 70, which lengthens
each run it shares the box with. The opener's driver is also out of tree (the orchestrator's
`open2.sh`/`open3.sh`), so there is no tree change to route.

Binding: drain rate is set by four slots and the per-run time under load. The driver is not the
constraint, and the measured state is already four concurrent runs. What would change the answer:
the opener observed holding fewer than four slots while opens queue. That would be a fix in the
orchestrator's script, not a tree change.

## P250: open_pr.sh and update_pr.sh reuse a fixer's recorded prepr at the same code SHA

Verdict: DEFER. The benefit is unmeasured, and the part of prepr that could be reused is not the
part the filing prices.

Source: `proposals.md` V164 (orchestrator, owner-approved card).

Instances:
- **The open-time prepr runs no test gate.** `grep -n 'tests/run.sh' tools/pr/prepr.sh` returns
  nothing. Its 9-minute and 3728 s figures are a fixer's own runs (BEATD's self-test, #2873),
  not the open's prepr.
- **Most steps depend on the base, main or the body, not on the code SHA.** The open log for
  #2910 (`$HPO_STATE_DIR/pr/r10-rca-closure-argv/p1.log`) shows these steps keyed to the merge
  base or origin/main: merge-base, transport, claim files ("byte-identical to origin/main"),
  claims hygiene, ci predict, layout guard, ref privacy and temp paths (both "since
  0b8f8b585daf"), pr-body ("over 0b8f8b585...ef77f1be8"), carry (at the roster ref), push order and
  ancestry reds. The open merges origin/main into the code, so its head is not the fixer's SHA,
  and every one of these steps must re-run against the base it will merge on.
- **The steps that depend only on code are partly skipped already.** `self-test` runs only when
  prepr.sh, a program it names or its fixtures change (`tools/pr/prepr.sh:3652-3656`). On #2910
  the remaining code-only steps were policy_lint fixtures, rules_sync, fragments, hooks,
  codeowners_gap, brief_lint, agreement lane, register check and wave-script.
- **No per-step clock exists.** prepr prints `ok`/`skip` lines and no elapsed time, so the
  reusable share of a 13-30 min open is not known.
- **The fixer's record lives on another host for cloud fixers.** A reuse predicate would have to
  ship the record, which is one more artifact on the handoff, beside the code and body refs.

Cost: a record format, a reuse predicate over prepr's 3927 lines with its own null control, and a
new stale-green surface. A reused step whose inputs moved with main would print `ok` for a tree
it never read.

Binding: an unmeasured benefit, against a predicate on the repository's most-touched check
script. What would change the answer: per-step elapsed times for 10 or more open-time prepr runs,
showing that the code-only steps above take a clear share, for example 10 min or more per open.
The orchestrator can take that measurement now without a tree change, by timestamping each line
of the opener's `p1.log`. If it clears the bar, the owner is R10-PREPR-CAP, which owns
`tools/pr/prepr.sh` (stage `done`, so a reopen).

## P251: dispatch fixers' heavy runs to cloud seats while local load stays above about 50

Verdict: ACCEPT, narrowed, as dispatch practice. There is no tree change and no roster op.

Source: `proposals.md` V165 (orchestrator, owner-approved card).

Instances:
- **Load sits far above the threshold the filing names.** At 16:03Z the load averages were 64.09,
  75.32 and 67.71 on 8 cores.
- **Local seats' heavy runs are the main CPU load.** At 16:05Z, `ps -axo pcpu` listed 11
  `tests/features.py` processes at 20-26 % each. The `cwd` of the parent (`lsof -d cwd`) traces them
  to a local fixer's `tests/mutation_table.py --pin-killed --jobs 3 --scripts tests/features.py`
  (seat dir `fix-2887-s11`) and to a local reviewer (`rev-2872`, which runs `tests/env_drift.py
  --capture`). Opens and updates held the four prepr slots beside them.
- **Resume seats are recorded.** Seat directories under the session's seat root, one per seat
  run, are a proxy for resumes: `fix-2873-*` 5, the LEARNER-DEFAULT fixers 4 (`fix-learner-s8`,
  `fix-learner-s9`, `fix-learner-default`, `fix-r10-learner-default`), `fix-cop-gate-*` 2,
  `fix-configflow-s10` 1. That is consistent with the filing's five groups that hit the 2 h wall.
- **The S/M half is already the owner's rule, and was not followed.** The owner said on
  2026-10-21: "try to keep heavy runs on cloud runners to keep the box load under control". On
  2026-10-24 the owner narrowed it so that larger groups stay local "so you can coordinate with
  them live via sendmessage", and small and mechanical work stays on cloud. R10-LEARNER-DEFAULT is
  size S on the roster, yet ran as four local seats.

Accepted, and narrowed to:
1. Every new S and M fixer, and every fix-review seat that runs a mutation table or a full suite,
   goes to a cloud seat (`tools/audit/seat/cloud_dispatch.py`). This enforces the standing rule
   rather than adding one.
2. A local seat of any size that must run a mutation table or a full suite while load1 is above
   50 runs it on a cloud seat, or waits for a slot. It does not start the run locally.
3. L/XL, critical-path and repeatedly blocked fixers stay local. The owner's 2026-10-24 ruling
   keeps them local for live steering, and a cloud run cannot receive SendMessage. Moving them is
   the owner's call, and is recorded as owed.

Cost: cloud setup per seat (R10-FLY-CLOUD-SETUP-TOOLCHAIN already records the toolchain gap), a
shallow clone, and no local-only instruments. It adds no code, check or policy line in the tree.

Binding: the benefit is measured (load 64-75 on 8 cores, 12 resume seats across four groups,
with the load traced to local seats' heavy runs) and the cost is per-seat setup. Items 1 and 2
clear the bar. Item 3's trade (live steering against load) is an owner ruling already in force,
which triage does not overturn.

## P252: 30-minute WIP checkpoints to a wip/<topic> ref for every fixer

Verdict: REJECT. The loss it targets did not occur, because the files survived on disk, and the
off-host copy it would add already exists.

Source: `proposals.md` V166 (orchestrator, owner-approved card; asks for wt_sync.sh to be
measured first).

Instances:
- **A power loss does not lose a local seat's files.** After the 12:42Z loss, the worktrees of
  the fixers the filing names were intact, clean and on committed heads: `fix-cop-gate-s10`
  (`d3ce1d33f`), `fix-configflow-s10` (`9d043f781`), `fix-2873-s10` (`060c9bef5`), `fix-2896-s11`
  (`581079f20`). This seat's own worktree was clean at `fa3eddc47`.
- **Seats already keep a resume note.** `ls <seat-root>/*/STATE.md <seat-root>/*/RESUME.md`
  finds 17. `fix-2873-s10/RESUME.md` and `fix-cop-gate-s10/STATE.md` are among them.
- **The roughly 3 h was downtime, not lost work.** The seat ledger's `sweep_mech: restarted
  state-beat (pid=none log_age=237m)`, `wt-sync (... log_age=240m)` and `tick (...
  log_age=237m)` lines at 15:33:21Z date the outage. A checkpoint does not shorten an outage.
  Making a stop visible is R10-FLOW-ANDON (`done`), and the supervised beat is R10-ORCH-BEATD.
- **wt_sync.sh already snapshots every worktree off host.** It covers each `git worktree list`
  entry with unpushed or dirty state (`tools/audit/seat/wt_sync.sh:27`), and 524
  `wip-sync/*` refs exist on origin (`git ls-remote origin 'refs/heads/wip-sync/*' | wc -l`).
  Its cadence is slower than its comment says:
  - The pass started at 15:33:21Z was still running at 16:07:55Z, 34 min later. Its worktree arm
    finished in about 4.5 min.
  - The scratch arm has run since then. It hashes 76,178 files (`find` with the script's own
    filters over the 4.8 GB orchestrator scratch), one `git hash-object` process each
    (`wt_sync.sh:39`).
  - With the loop's `sleep 900`, a worktree is snapshotted about every 50 min or more, not every
    15. The log has 113 completed passes since its creation at 2026-10-24T08:14:41Z.
- **Cloud seats are outside a local power loss.** A cloud fixer's session does not die with the
  host.

Cost as filed: a push, plus a `ref_privacy` guard, per fixer every 30 min. A `wip/*` exclusion in
the relay and orphan arms. One more ref family beside 524 `wip-sync/*` refs. A brief line every
fixer seat spends turns on. All of this protects against off-host loss, which round 10 has not
recorded and which wt_sync already covers.

Binding: no measured file loss, against a per-seat recurring push protocol. The one measured gap
is wt_sync's cadence, and the orchestrator's loop can close it without a tree change. Running the
worktree arm in its own loop without `--scratch` puts worktree snapshots back near 15-20 min,
and the scratch arm can run less often. What would change the answer: a recorded loss of
committed or dirty seat work that a snapshot 30 min old would have saved.

## P253: refuse an Anthropic author or committer identity on a pushed commit

Verdict: ACCEPT, narrowed to the guard arm, into **R10-FLY-NO-FOOTERS**. Not the prompt line:
the seat preamble already sets the seat identity.

Source: `proposals.md` V167 (the #2910 round-2 reviewer, via the orchestrator, 2026-10-28).
Instance: `b9a66d28d0554c95c4e961684bc3b91ed1b1c719`.

Instances (read at origin/main `f844df1fe`):
- **The rough count was right, not overstated.** `git log --since=7.days --format='%ae'
  origin/main | grep -ic anthropic` gives 500 of 3906 commits. The filing's grep also gives 500:
  its format string has no subject, so it could only match the name or email. Over all of history
  the count is 919 of 12434. The committer email gives 482 over 7 days and 863 over history.
- **The identities in those 7 days:**
  - `Claude <noreply@anthropic.com>` as author and committer: 453 commits.
  - `Claude` as author with tvofi as committer: 20.
  - Seat names on the Anthropic address (`hpo-fixer-seat`, `hpo seat`, `hpo fixer seat`,
    `hpo-author`, `hpo-fixer`): 27.
- **The class has almost stopped, but not quite.** By author date over 14 days, Anthropic-authored
  commits fall on six days (10-18, 10-21 to 10-25), from 47 to 168 on each of those days, with the
  last of that run on
  10-25T20:07:12Z (`70b57a370`). Since 2026-10-26T00:00Z, 1 of 1002 commits on main carries it:
  `b9a66d28d`, authored and committed as `Claude` at 2026-10-28T01:41:39Z.
- **The source is a cloud fixer that did not set its identity.** `cloud-sessions.tsv` records
  "r10-roster-freeze-close fixer s8 (critical path)" dispatched at 2026-10-28T01:27:46Z, 14 min
  before the commit. It reached main through #2903 (`71fe1f7fc`). Nothing in the tree sets a
  cloud fixer's identity: `cloud_dispatch.py` sets one only on its own verdict commits (lines
  150-151, 225). The seat preamble's identity step (item 4) is out of tree, so a seat that skips
  it falls back to the runner's default.
- **The guard already reads both emails and lets this one through deliberately.**
  `ref_privacy.py guard --commits` adds the author and committer email of every commit not on a
  remote ref (`tools/audit/seat/ref_privacy.py:347`). It runs on both push paths:
  `handoff_push.sh:141` and `app_push.sh:376`, each with `--over refs/remotes/origin/main`.
  But `email_leaks` refuses only host domains (line 240), and the self-test pins
  `email_leaks("noreply@anthropic.com", fid) == []` as a null control (lines 704-706).

Carry (guard arm only):
- `email_leaks` refuses an `@anthropic.com` address as a new class, `anthropic-identity`.
- The line-706 null control moves to a refusal arm, and a seat noreply address
  (`hpo-fixer@users.noreply.github.com`) becomes the null control.
- A guard-CLI arm, built like the `host-email` arm at lines 780-785, refuses an unpushed commit
  whose author or committer is `Claude <noreply@anthropic.com>`, and passes it once re-authored.
- Controls: a mutant that drops the class fails the refusal arm. History is not judged, because
  the guard reads only commits not under `--over`, so main's 919 are out of reach. That is the
  null control for false fires on old commits.
- Not in scope: rewriting main's history, and a `cloud_dispatch.py` prompt line, since the
  preamble carries it and a guard at both push paths catches what a prompt misses.

Cost: one class in `email_leaks`, about 5 lines, and two self-test arms in an existing file. A
refusal costs the pushing seat a `git commit --amend --reset-author` (or a rebase that re-authors)
before review, not after it, at the measured rate of 1 per 1002 commits.

Binding: the owner's ruling (R10-FLY-NO-FOOTERS: no Claude attribution "in commits, pull request
bodies or comments") is wider than the guard enforcing it. A runner default reached main 2 days after
the rate had fallen from 499 of the 2904 commits before 10-26 in the 7-day window (17 %) to 1 of
1002 since (0.1 %). The cause of the fall is not recorded in the tree. Widening the existing arm costs a
few lines, and the alternative is a review catching it by eye. If the owner rules that the author
field is outside the attribution rule (the filing's option (b)), this ruling falls and nothing
lands.
