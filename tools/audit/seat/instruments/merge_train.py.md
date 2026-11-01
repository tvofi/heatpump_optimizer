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
  `add`'s admission (`Train.admit_add`) reads the same posted verdict
  first, as its `verdict` rule, and fills an absent comment id from it.
  bus.sh's post loads the train the moment it posts a merge verdict
  (`merge_train.py add --auto`, with `HPO_BUS_TRAIN_STATE` set);
  `sweep` is the slow backstop (`tick_loop.sh --sweep`, every 1800 s by
  default): unless the ledger holds an open train-stop, it `add`s each head
  `queue` admits that no sweep added at that head, into the live train's
  next batch or a `train.sh --bot-prs --approval-carry --pre-flight` it
  starts when none is live, never a second.
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
  `batch` also takes several batches in one queue (a list of lists), run in
  order on one train, each with its own admission, proof and merges; between
  two it drains what `train.sh add` spooled into one more batch, never into a
  batch in proof, and a batch that stops ends the train (`NOT RUN` lines).
  `add` and that drain apply one admission rule (`already_held`, over the
  live train's `queue.seen.json`): a pull request still to run, spooled,
  merged or run by this train is `ALREADY` on both sides; one it skipped is
  admitted again at a new verdict head, and at the same one when the skip was
  the environment's (`[HOLDER]`, or `[BRANCH-POLICY]`: every merge attempt
  refused by GitHub's base-branch policy). `skipped.json`'s rows name the
  verdict; an entry skipped and then merged by the same train is cured
  (`CURED #<pr>`), out of `skipped.json`, `SKIP REPORT` and the exit code. `dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` holds
  one mutant per arm of that rule. A
  policy head batches like any other: under a `--mandate` naming the mandate's
  comment id, in force for policy merging, the train posts the citing approval
  step 5 requires (`policy_approve`); a budget raise still goes serial.
  `dev/audit/harnesses/r10_train_upgrade_mutants.py` holds one mutant per arm
  of these three.
  Residual: a proved pair's second merge does not wait for main's run on the
  first; the proof graded the tree both make. A `batch/` branch the remote
  will not delete is logged `NOT deleted`, for deletion by hand.
  It owns the state classifier (Lean flow study K15) the tick also imports,
  judged on the latest run of each required context (`main-protect-checks`,
  read live; `record`, `record-autofix`, `nightly-status` and
  `delivery-status` never count): a queued or in-progress run is a wait,
  never red, and an unreadable ruleset refuses. `--overlap` logs main RED,
  or still running, by that rule. Before a merge attempt a check-run still
  queued or in progress over a completed workflow run is stale: its run is
  re-run once, logged `STALE <context> ... run <id>` (a third recurrence goes
  to a root-cause seat), and re-read. `unstale <sha>` runs that step alone;
  `classify <sha>` prints GREEN (rc 0), RED (rc 1) or WAIT (rc 3) over a pull
  request's required contexts (`--main`: less the PR-only ones), rc 2 when
  unreadable — a head is reviewable unless RED, which `bus.sh dispatch`
  enforces. `--pr N` asks `approval_owed(train, pr, head, runs, required)`, the one
  owner of a budget raise's pre-approval red (P345): when the red set over
  `gating_names` is `gate` and `budget-raise-gate / budget-raise-gate` alone,
  every red gate suite's own log (`gate_raise_only`, through `gate_outcome`)
  lists that unit's failure as its only reason (a SKIPPED, ABSENT or PENDING
  unit, or a reason naming none, reddens `gate` outside the red set: #3073),
  and `Train.raise_hold`, over the three-dot names from git, reads a raise not
  held, it prints `APPROVAL-OWED <sha> <the gate's reason>` (rc 4): reviewable,
  because the owner's approval follows the verdict. A raise_hold Stop, a gate suite still
  running or a failed read (a log included) stays RED; `classify` itself, the train and the merge state are
  unchanged, and without `--pr` the answer is as before. A required context red at main's tip whose workflow run is at
  attempt 1 and failed on infrastructure alone (every failed job but `gate`
  logs an API rate-limit or unreachable string, and `gate` printed
  RATE-LIMITED or only `<job>: failure (this run)` reasons naming those jobs)
  is re-run once, failed jobs only, in both main-gate arms: logged
  `INFRA-RERUN <context> run <id> attempt 1`, never before the printed
  `reset_epoch` (else an hour after the last such job), and until then
  `INFRA-RED ... re-run due at <time>` with the red standing (V142).
