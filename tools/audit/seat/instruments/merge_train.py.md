# `merge_train.py`

- `merge_train.py` — lands a queue of verdicted PRs one at a time: re-carry
  CI, wait for green at the exact head, evidence-gated approval,
  `--match-head-commit`. When: any merge queue — queued PRs merge through
  this, never by hand. Refusal: a head that moved under the review, red
  checks the queue was not told to ignore, or a head whose TIP is a
  GITHUB_TOKEN bot push (author `github-actions[bot]`) stop the train — such
  a head has no `pull_request` run, the required contexts never report at it,
  and the required follow-up is an App push (step 1's recarry once main
  moves; batch routes such a head serial, `bot-head`, where that recarry runs
  after the batch's own merges). A foreign merge moving main under a settled
  head is recovered up to `--main-moved-tries` (default 3; 0 is the old stop):
  serially by a recarry and a fresh CI wait, in a batch by re-proving the rest
  on the new main. An owner approval GitHub already holds at the live head is
  the owner's, with nothing re-posted (GitHub re-anchors one across a clean
  base merge: #2209). `--bot-prs` merges the open record/autofix pull request
  in the train's own sequence behind record_row.py's identical guard, after a
  critical-path entry rather than before it, and once more after a refused
  merge attempt; `--pre-flight` runs `queue_pre_flight.py` first and PARKs a
  failing entry; `--free-holders` detaches a clean holder worktree with no
  commit origin lacks. Every refused merge attempt is logged in GitHub's
  words, and a base-branch policy refusal parks the entry with the reason
  read from the merge state; the recarry worktrees a run made
  are removed before its closing line. Every `gh api` GET and `gh pr view`
  it or `queue_pre_flight.py` makes is under `gh_read.py`'s read rule, each
  settle logged.
  `queue <file>` writes the queue nobody had to assemble: every open
  pull request but the record one whose approver-App verdict is newest, is
  `verdict/<pr>`'s posted tip and is `merge` at its head or carries to it
  (`app_approve.sh --carry`), oldest first, one `QUEUE`/`LEFT` line each;
  budget and policy heads are queued for the batch's own serial route.
  A record pull request (`record_pr`: every changed path a delivery row,
  carry, plan, triage batch, the handover or a roster) is logged
  `HELD-FOR-STAMP` and queued for nobody, by `queue`, `add` and `sweep`
  alike; under `--stamp` they are admitted, so the stamp step of
  `.claude/workflows/web-stamp.js` runs `sweep --stamp` before the tag and
  one train merges every held record in one batch (tvofi 2026-11-01). The record/autofix branch stays `--bot-prs`'s.
  An `add` that starts a train starts it over every ready pull request
  (`Train.ready_batch`: the sweep's queue, else `build_queue`), one batch;
  a train over one pull request starts only when it is the one ready
  (tvofi 2026-11-01, batch by default).
  `add`'s admission (`Train.admit_add`) reads the same posted verdict
  first, as its `verdict` rule, and fills an absent comment id from it.
  That read refuses a stale merge verdict (P393, `stale_merge`): a
  `blocked` commit at the same head on `verdict/<pr>` whose bus-nonce
  (its VERDICT.md) bus.sh's registry (`$HPO_BUS_STATE/dispatched`, else
  `~/.zcode/bus/dispatched`) records as dispatched after the merge
  verdict's; a missing record or utc refuses with its reason, and a
  blocked verdict under the merge's own nonce is that reviewer's revision.
  The registry is host-local, so run the train where bus.sh dispatches.
  bus.sh's post loads the train the moment it posts a merge verdict
  (`merge_train.py add --auto`, with `HPO_BUS_TRAIN_STATE` set);
  `sweep` is the slow backstop (`tick_loop.sh --sweep`, every 1800 s by
  default): unless the ledger holds an open train-stop, it `add`s each head
  `queue` admits that no sweep added at that head, into the live train's
  next batch or a bare `train.sh` launch it starts when none is live, never
  a second.
  A train launched through `train.sh` runs the recommended flags by default:
  `RECOMMENDED` in this file is their one definition (`--overlap`,
  `--approval-carry`, `--skip-bad`, `--free-holders`, `--bot-prs`,
  `--pre-flight`), each off with `train.sh --no-<flag>`. The flags this page
  names say what each does; a caller launching through `train.sh` passes none
  of them by hand.
  `batch` merges the queue without re-merging main: the entries' merges are
  proved together on `batch/<tag>-<n>` (B), a lone entry merges unproved (D),
  and workflow, claim, grader, budget or conflicting entries go serial. When:
  the default for a queue. Refusal: a red main admits nothing; a red proof
  drops its entry to serial,
  and main's tree differing from the proof's before or after a merge stops it.
  `batch --skip-bad` makes a per-entry refusal (admission, recarry, carry, CI,
  merge) fatal for its entry alone — logged `SKIP #<pr>`, reported in
  `skipped.json` and a `SKIP REPORT` line, rc 1 — while a red main and a Stop
  after the merge API call stay global. `batch --overlap` (owner's P7) does
  not wait on main's CI (log-only) and re-carries every serial entry up front
  so their pull_request runs fire together; each lands in queue order when
  its own required contexts conclude — the ruleset still gates every head.
  A serial entry whose base THIS batch's own merges moved is graded before it
  lands (`Train.grade_merge`, R10-TRAIN-OVERLAP-GRADE): the merge GitHub
  would make is built with the train's driver-free text merge, materialised
  as a throwaway worktree, and read by `policy_lint` always and
  `tests/structure.py` where `tests/closures.json` selects it for the merge's
  files. A red posts no approval and is HELD: `MAIN-MOVED` re-carries it and
  CI judges the new head, and a recarry that reproduces the same red tree
  stops instead of looping. A one-car batch (the #2595 repair car onto a red
  main) cannot move a base, so the grade never fires there.
  Card 5 (tvofi 2026-11-07, `Train.merges_as_is`): a head that lacks
  origin/main is recarried only when `main-protect-checks` requires an
  up-to-date branch (`strict_update`, read live; unreadable counts as
  required), when git's merge of origin/main and the head conflicts, when the
  head is a GITHUB_TOKEN tip, or when a graded red holds it; otherwise it is
  logged `#<pr> no recarry:` and merges at its proven head, its merge tree
  graded against its merge base at the merge, as the overlap grade does.
  Card 1 (`Train.rejoin`): under `--skip-bad`, an entry skipped on a head red
  holding `gate` (`HeadRed`) rejoins the same train after the batch's own
  merges, through the serial path, once its skipped head classifies GREEN
  (`classify_at`), with no `add`; RED, a head still WAIT `wait_cap_s` (polls
  x 305 s, 7320 s at the default) after its skip, or a head the branch moved
  off stays skipped, each logged `REJOIN #<pr>: ...`; a rejoin that merges
  is CURED. Residual: the rejoin's wait delays the next spooled batch, never
  a merge of its own batch. `dev/audit/harnesses/r10_train_rejoin_no_recarry_mutants.py`
  holds one mutant per arm of both cards.
  `batch` also takes several batches in one queue (a list of lists), run in
  order on one train, each with its own admission, proof and merges; between
  two it drains what `train.sh add` spooled into one more batch, never into a
  batch in proof, and a batch that stops ends the train (`NOT RUN` lines);
  an `add` that starts a train orders its first batch, the entry and what a
  stopped train left spooled, by the same `Train.drain_order`: entries added
  with `--priority` (HOTFIX), a roster hotfix (`roster_lib.is_hotfix`, flag
  or not) or `--front` first, then outside entries
  (`roster_lib.is_outside`, owner ruling tvofi 2026-11-07, triage P420), then
  critical-path entries, then arrival order; an entry maps to its group by
  branch, else by its pull request (`roster_lib.group_for_pr`), so a fork head
  ranks as its group does.
  `add` and that drain apply one admission rule (`already_held`, over the
  live train's `queue.seen.json`): a pull request still to run, spooled,
  merged or run by this train is `ALREADY` on both sides; one it skipped is
  admitted again at a new verdict head, and at the same one when the skip was
  the environment's (`[HOLDER]`, or `[BRANCH-POLICY]`: every merge attempt
  refused by GitHub's base-branch policy). `skipped.json`'s rows name the
  verdict; an entry skipped and then merged by the same train is cured
  (`CURED #<pr>`), out of `skipped.json`, `SKIP REPORT` and the exit code. `dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` holds
  one mutant per arm of that rule. The spool is edited only through the
  instrument: `add --front <pr>` puts an entry first in the next batch (a
  spooled one is moved there, and the drain keeps it in the `--priority` tier
  ahead of outside and critical-path entries) and `add --remove <pr>` drops a spooled one
  (rc 1, nothing written, when it is absent), both under the queue's flock
  and each printing the spool order read back. A batch's admission waits
  each head on the required set a pull request's head carries
  (`required(pr_head=True)`), as the serial head wait does.
  `dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py` holds one
  mutant per arm of these and of the part-3 review survivors. A
  policy head batches like any other: under a `--mandate` naming the mandate's
  comment id, in force for policy merging, the train posts the citing approval
  step 5 requires (`policy_approve`), and `--pre-flight` and the re-add's
  re-run of it judge the head with that approval unposted (`policy_admits`),
  so they admit what the post will carry; a budget raise still goes serial.
  `dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` holds one
  mutant per arm of that read.
  `dev/audit/harnesses/r10_train_upgrade_mutants.py` holds one mutant per arm
  of these three.
  Residual: a proved pair's second merge does not wait for main's run on the
  first; the proof graded the tree both make. A `batch/` branch the remote
  will not delete is logged `NOT deleted`, for deletion by hand.
  It owns the state classifier (Lean flow study K15) the tick also imports,
  judged on the latest run of each required context (`main-protect-checks`,
  read live; `record`, `record-autofix`, `nightly-status` and
  `delivery-status` never count): a queued or in-progress run is a wait,
  never red, and an unreadable ruleset refuses. A red `gate` in a head wait
  is a wait while `tools/ci/gate.py`'s own `busy` (imported) names a ci.yml
  run at the head, or `gate_rerunning` names one re-running its gate (a run
  unfinished past its completed `gate`: gate-sweep's attempt 2), read from one
  runs listing per poll, so an edit run's
  at-once deferral red is not read final while its code run runs; a red
  beside a green `gate` suite gets one settle poll for gate-sweep's re-run,
  and an unreadable listing leaves the red standing, logged
  (R10-HOTFIX-TRAIN-DEFER-WAIT). `polls` still bounds the wait (TIMEOUT); `wait-ci
  <sha>` (no `only`) takes the same settle once every run concluded. `--overlap` logs main RED,
  or still running, by that rule. Before a merge attempt a check-run still
  queued or in progress over a completed workflow run is stale: its run is
  re-run once, logged `STALE <context> ... run <id>` (a third recurrence goes
  to a root-cause seat), and re-read. `unstale <sha>` runs that step alone;
  `classify <sha>` prints GREEN (rc 0), RED (rc 1) or WAIT (rc 3) over a pull
  request's required contexts (`--main`: less the PR-only ones), rc 2 when
  unreadable — a head is reviewable unless RED, which `bus.sh dispatch`
  enforces. Its one read goes through `Train.classify_at`: a red `gate` while
  gate.py's `busy` or `gate_rerunning` names a ci.yml run at the head is
  WAIT, and so is one beside a green `gate` suite completed at most
  `SWEEP_SETTLE_SECONDS` before the read (`sweep_settling`, the poller's one
  settle poll on the wall clock: none of the one-read callers re-reads a RED);
  past the bound, or on a stamp ahead of the clock, the red stands. Its
  deferral log goes to stderr. `--pr N` asks `approval_owed(train, pr, head, runs, required)`, the one
  owner of a budget raise's pre-approval red (P345): when the red set over
  `gating_names` is `gate` and `budget-raise-gate / budget-raise-gate` alone,
  every red gate suite's own log (`gate_raise_only`, through `gate_outcome`)
  lists that unit's failure as its only reason (a SKIPPED, ABSENT or PENDING
  unit, or a reason naming none, reddens `gate` outside the red set: #3073),
  and `Train.raise_hold`, over the three-dot names from git, reads a raise not
  held, it prints `APPROVAL-OWED <sha> <the gate's reason>` (rc 4): reviewable,
  because the owner's approval follows the verdict. A raise_hold Stop, a gate suite still
  running or a failed read (a log included) stays RED; `classify` itself, the train and the merge state are
  unchanged, and without `--pr` the answer is as before. With `--pr` (not `--main`),
  an `instrument-self-tests` step red (`RED_CONCLUSIONS`: a cancelled or
  timed_out step too) at the head and not at its merge base
  (`git merge-base origin/main <sha>`), less the push-only drift step, reads RED
  with one `INTRODUCED <step>` line each, and a head job concluding timed_out
  where the base's did not adds `JOB_TIMED_OUT`: a finding of the pull request
  (`introduced_at`, R10-INTRODUCED-REDS-BARRIER). The latest run by id is read;
  one still running reads WAIT (rc 3) where the required set is green. No base
  run counts every head red, a step skipped by scoping is never red, and an
  unreadable listing or job, a job-level cancelled or startup_failure, or a red
  job with no red step is rc 2. A head job not red (no run, success, skipped)
  costs no extra read; else one filtered check-run read at the base and one
  job-step read per side.
  `introduced <sha> [--base <sha>]` prints those lines alone: rc 1 any, 0 none, 3 running, 2 unreadable. A required context red at main's tip whose workflow run is at
  attempt 1 and failed on infrastructure alone (every failed job but `gate`
  logs an API rate-limit or unreachable string, and `gate` printed
  RATE-LIMITED or only `<job>: failure (this run)` reasons naming those jobs)
  is re-run once, failed jobs only, in both main-gate arms: logged
  `INFRA-RERUN <context> run <id> attempt 1`, never before the printed
  `reset_epoch` (else an hour after the last such job), and until then
  `INFRA-RED ... re-run due at <time>` with the red standing (V142).
