# Instruments — the operator's guide to tools/audit/ and tools/audit/seat/

This is a usage guide, not policy: it says what each instrument does, when a
real lane reaches for it, and which refusal saves you. The obligations live in
`CLAUDE.md` and `.claude/rules/`; nothing here adds one. Every `--self-test`
runs offline.

Directories here that are records, not instruments: `round3/`..`round9/`,
`round5-fix/`, `round7-fix/`, `round8-fix/`, `handoff/`, `rca/`,
`w5-partition/`, `w5-g5-195-coverage/`, `briefs/` (the seat contracts and
dimension briefs), `archscore/`, `ci-version-edit/`, `ledger-layout/`,
`record-predicate/` (sub-tools with their own READMEs), and the JSON/schema
files (`bugclasses.json`, `scopes.json`, `rotation.json`,
`finding.schema.json`), which the instruments read. `harnesses/` holds the
re-runnable measurement harnesses a fixer or judge lands with a PR — its
`README.md` indexes them; anything a later seat must rerun belongs there
(fixer contract step 18), not in a session's scratch.

## tools/audit/

- `app_approve.sh` — approves a pull request as the `hpo-approver` App at one
  exact head SHA, only on a `merge` verdict for that SHA from an allowlisted
  account (`--carry` re-approves a carried verdict). When: landing a
  non-code-owned verdicted PR whose head the reviewer measured. Refusal: a
  head SHA that is not the PR's current head, or a verdict whose SHA or
  account does not match — the approval names one tree or it does nothing.
- `app_comment.sh` — posts one fix-review verdict on a PR as `hpo-approver`
  and reads the posted comment back byte-identical. When: a reviewer seat
  delivers a verdict. Refusal: a read-back that differs from what it meant to
  post, or a stale head — "posted" is never taken from the send's exit code.
- `app_push.sh` — pushes a branch and opens or re-bodies its pull request as
  the `hpo-author` App, with the body's contract check before the push. When:
  every handoff — pull requests are App-authored (decision 0011); `push.sh`
  is the tvofi-identity predecessor and must not author PRs. Refusal: a body
  failing the contract check never reaches the remote.
- `head_note.py` (tools/pr/) — prefixes a note under a body's `## Head`
  heading, found as `checkPrBody`'s `sections()` reads it (outside a fence,
  `##`, whitespace, `Head`), never the first substring `## Head`.
  `app_push.sh --recarry`, `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
  write every head note through it. When: any new writer of a `## Head`
  note. Refusal: a body with no `## Head` heading exits 1, file untouched.
- `approve_held_runs.sh` — approves the workflow runs GitHub holds
  `action_required` on a branch. When: after the App pushes, the `pull_request`
  workflows it created are held because the pusher is an App; a green gate
  never starts until these are approved. Refusal: `--dry-run` lists what would
  be approved; a branch with no held runs is a no-op, not an error to retry.
- `check_scopes.py` — proves the finder scopes are disjoint and complete
  within each dimension, from `scopes.json`. When: starting an audit round
  (`audit-find` runs it in Prepare and refuses the round on failure) or
  splitting one. Refusal: a cell owned twice, or owned by nobody — the
  perturbed-scope `--self-test` is the null control.
- `fold_ledger.py` — folds a round's JUDGE.json and sweeps into
  `bugclasses.json`, and checks the register against the judges. When: after a
  judge lands, and before quoting the bugclass register as current state;
  `sync` after any hand edit of `finding.schema.json`, which rewrites
  `audit-find.js`'s generated CLASS_GUESS and FINDING_REPORT (fold runs it).
  Refusal: `check` refuses a register that drifted from its judges — re-quote
  the register, not a memory of it.
- `judge_batch.py` — re-runs every finding's harness, perturbation and null
  control serially under the gate lease, one row per finding. When: a judge
  grades a batch of findings and wants the mechanical half scripted. Refusal:
  a perturbation that does not move the number in the stated direction prints
  `void`; what it cannot run prints `by-hand`, never a pass.
- `merge_fastpath.py` — classifies a changed file as workflow, claim, grader
  or budget for `merge_train.py`'s batch routing: any such file sends a pull
  request serial. Refusal: `--self-test` — `governance.yml` greps its
  `checks, 0 failed` line.
- `merge_throughput.py` — measures whether merges land inside the previous
  merge's gate window often enough to justify a merge queue. When: someone
  proposes a queue; the numbers decide before the mechanism is built.
- `preflight.sh` — mechanical checks on anything the orchestrator publishes
  (merge body, issue body, comment, brief): closing keywords and the claim
  shapes. When: before posting any prose that GitHub or a later seat reads.
  Refusal: a closing keyword in prose closes issues you did not mean to touch;
  it refuses rather than warns.
- `prepare_baseline.sh` — builds a round's audit baseline: a git-archive
  export finders work in, one worktree per mutating finder, briefs copied in.
  When: starting a round. Refusal: an archive run from a `git archive` copy
  fails the `recorded_at` check on every mutant, baseline included — the M0
  null run attributes that to the runner, not the findings.
- `prepr.sh` — the pre-PR self-check on your own branch and body: head SHA
  freshness, claim files byte-identical, the MODE line, carry destinations,
  body headings, and the scoped-closure selection. When: always, before
  handing a branch off. Refusal: each blocked reason names the artifact —
  a branch that fails prepr locally would have burned a review round instead.
- `push.sh` — pushes a branch and attaches a body that has already passed the
  contract check, in that order (#678). When: tvofi-identity pushes only;
  App-authored PRs go through `app_push.sh`. Refusal: the contract check runs
  before the push, so the red `pr-contract` can never land on your review
  head.
- `worktree_gc.sh` — collects a merged PR's worktree, branch and seat
  scratch. When: after merges, before the disk fills (9.5 GB of orphaned seat
  directories once). Refusal: `--dry-run` prints the collection list; a
  worktree with unpushed work is left alone.

## tools/audit/seat/

- `features_block.py` — runs one block of `tests/features.py`, from the line
  holding a marker to the script's close, in the namespace features.py's
  header builds. When: a mutation proof or a body figure that needs only the
  block pinning the mutated line, on a seat where the whole script takes tens
  of minutes. Refusal: a marker that is not in the script raises rather than
  running an empty block.
- `body_push.sh` — publishes a handoff's BODY.md on the orphan ref
  `handoff-body/<topic>` (plus RESUME.md), parentless first commit,
  fast-forwards after. When: every fixer handoff — the body must never enter
  the code head's ancestry (`prepr.sh` step 1a refuses that). Refusal: a
  head `tools/pr/ci_predict.py` predicts a closures or `fast` red on, or a
  checkout with no predictor (R10-HANDOFF-PREPR-BOUNCE M2), is refused
  before anything is pushed, with each arm's repair printed; a fetch that
  half-failed leaves a parentless commit the push refuses as a
  non-fast-forward — a rewrite is never forced through.
- `autofix_statuses.sh` — re-derives what `mutation-autofix` and
  `closures-autofix` answered on recent pull-request runs, from their job
  logs, with the `closures` failure heading behind each closures skip. When:
  judging whether the autofix chain repairs anything. Refusal: a log GitHub
  no longer serves is counted beside the totals, never read as a status.
- `bus.sh` — git refs as the programme's message bus: seats publish verdicts
  on refs, the orchestrator watches. When: a reviewer seat with no other
  channel, or an orchestrator collecting several lanes' verdicts at once.
  `orphans` discharges a handoff by name only when that `fix/<t>` or
  `fix/<t>-pr` head carries the tip; a named head behind it is
  `repair=update`.
- `ci-watch.sh` — watches open PRs' check states and alerts only on NEW
  states (per-PR signature file): reds, CONFLICTING/DIRTY, STALLED zero-runs,
  and required contexts ABSENT at a settled head — a bot GITHUB_TOKEN push's
  `pull_request` runs are held `action_required`, so until one is approved the
  governance family does not report at such a head and it sits unmergeable
  looking green (R9-RC-AUTOFIX-GOVERNANCE).
  When: a long fix wave where red-on-main or a fresh failure must interrupt
  work. Refusal: state already seen prints nothing — the exit-1 report is the
  alert, not the log; an unreadable ruleset alerts BLIND once rather than
  silently skipping the ABSENT arm. `--self-test` grades every arm offline on
  the recorded defect shape; `CI_WATCH_ONCE=1` runs a single cycle.
- `cloud-setup.sh` — the cloud seat environment's setup script (interpreter,
  CI-run pinning): it builds `venv-ci` and `venv-ha` under `/opt/hpo` and
  writes the toolchain profile. When: tvofi pastes it into Project settings; a
  seat cannot apply its own environment. A seat does not source that profile:
  a non-interactive Bash call skips it, so the toolchain reaches a seat
  through the environment's variables (see `cloud_dispatch.py`). Refusal: a
  missing checkout warns and exits 0, so a session still starts, without pins.
- `cloud_dispatch.py` — renders the whole cloud-runner trigger payload
  (`job_config.ccr`: `environment_id`, `session_context` with `allowed_tools`,
  `model` and `sources`, and one user-message event) for a `reviewer`,
  `fixer` or `probe` seat from the PR, the 40-hex head, the bus nonce and an
  optional brief file. The environment id, model and repository come from a
  flag, an overlay JSON (`--overlay` / `$HPO_CLOUD_OVERLAY`) or `HPO_CLOUD_*`,
  never from the tree. When: dispatching a seat to the cloud runner; paste
  the printed JSON as the trigger update. The measured shape of a cloud seat:
  every trigger update resends the full ccr and then `run`s it, never a
  patch; the brief is snapshotted at `run`, so it is inlined at render time,
  an edit afterwards reaches no running seat, and overlapping runs are fine;
  the toolchain (`PATH` with `/opt/hpo/venv-ci/bin`, `BASH_ENV`,
  `HPO_TYPING_PYTHON`, `OPENBLAS_CORETYPE`) comes from the environment's
  variables, not from a profile the seat sources, so the prompt says only
  that it is on `PATH`; the seat starts off `main` in a shallow clone
  (`git fetch --unshallow --tags origin` first); the return signal is a
  pushed ref: `probe/rev-<pr>-<nonce first 8>` for a reviewer (see
  `cloud_relay.sh`: a cloud reviewer never runs `bus.sh`, whose dispatch record
  lives on the orchestrator's machine and refuses "unknown nonce" anywhere
  else, and a seat may not write a record it did not mint), `handoff/<topic>`
  plus `handoff-body/<topic>` for a fixer, `handoff-body/<topic>` for a probe,
  and a return push carries only the seat's own result tokens: a push
  carrying system-file dumps is refused; the session is reachable one way,
  by `SendMessage` to it, and nothing comes back on that channel. Refusal: a
  head that is not 40 lowercase hex, a reviewer without a nonce or `--pr`, a
  fixer or probe without `--topic`, a missing environment id, model or
  repository, and any home-directory path in the rendered text
  (`ref_privacy.HOME_DIR`, brief included). `--self-test` grades each
  refusal against a rendering that passes, offline.
  Two measured traps when driving the runner: an update and a run fired in
  parallel start the run on the PREVIOUS config, so a launch is update, wait
  for it, then run, sequentially; and the container's `BASH_ENV` puts the venv
  python ahead of the test stubs, so a cloud seat runs `tests/entities.py` (and
  anything else resolving `homeassistant`) with `env -u BASH_ENV`.
- `cloud_relay.sh` — the orchestrator's half of a cloud reviewer's return:
  `cloud_relay.sh <pr> <nonce> <head40>` fetches
  `probe/rev-<pr>-<nonce8>`, grades it, then runs `bus.sh push-verdict` locally,
  where the dispatch record lives; `bus.sh confirm` follows as for any verdict.
  When: a `probe/rev-*` ref appears after dispatching a cloud reviewer. Refusal:
  a nonce that does not match the verdict's `bus-nonce:` line, a ref whose
  commit subject (`verdict <pr> <head>`) or verdict first line names another PR
  or head, a missing `ev/`, and a ref already relayed (a ledger of
  `<ref> <sha>` under the state directory, written only after `push-verdict`
  succeeded, so a re-pushed ref relays again). `--self-test` grades each
  refusal against a clean ref, offline, with `push-verdict` stubbed. It also
  NORMALISES one shape and logs it (`normalised first line: A -> B`): a blocked
  first line whose tail the reviewer wrapped, `blocked <head> [class: reason]`,
  loses its one outer bracket pair in the relay's temp copy, which is lossless
  and puts the line in `bus.sh`'s grammar (`blocked <head> <class>: <reason>`).
  Chosen over refusing because the relay is the one place the verdict can be
  repaired without a round trip to a cloud seat that has exited, and the
  rewrite changes no word; a bracketed merge suffix, a nested bracket or a
  class outside `[a-z-]+` is refused unchanged (stripping a merge suffix would
  lose text). `cloud_dispatch.py`'s prompt now gives the unbracketed grammar.
  `cloud_relay.sh --watch [--interval N] [--once]` is the orchestrator's poll
  loop, tracked: every N seconds (default 120) it runs the probe arm, which
  lists every `refs/heads/probe/*` with `git ls-remote origin`. A probe ref
  that is not `rev-*` (a probe seat's return, a stray push) appends
  `OWED <utc> probe-ref <ref> <sha>` on EVERY pass until
  `cloud_relay.sh dispose <ref> <sha>` records it handled: a level, not a
  diff, so a missed line is repeated rather than lost, and a disposed ref
  that moves is owed again at its new sha. It relays each `rev-*` ref+sha
  once, taking the head and full nonce from the dispatch record (`$HPO_BUS_STATE`
  or `~/.zcode/bus`, `pr head thread nonce`). A ref with no record is logged and
  left for a later pass; a refused ref+sha goes to `<ledger>.refused` and is not
  retried until it is pushed again, so one refusal does not repeat every
  interval. Run it detached (`daemonize.py`); it uses ls-remote, not the REST
  quota. `--once` is one pass.
  `--confirm` (on `--watch` and on a single relay) keeps going past
  `push-verdict`: after one that passed it runs `bus.sh confirm <pr>
  <review-sha>` (the sha `push-verdict` printed) and appends `POSTED <utc> <pr>
  <sha>` or `OWED <utc> <pr> <sha|-> <why>` to `--log FILE` (default
  `cloud-relay.log` under the state directory), the file the orchestrator
  reads; two verdicts once sat relayed and unposted for 20 minutes. Confirm
  never runs after a refused relay or a failed `push-verdict`, and those write
  no line (the refusal is printed; `--watch` also keeps it in `.refused`).
  `cloud_relay.sh pass [--confirm] [--log FILE] [--loop [--interval N]]` is the
  orchestrator's whole beat as ONE entry point (it replaces the session-local
  `relay_watch.sh`): a driver calls it once per tick, or `--loop` repeats it
  (default every 120 s). A pass runs the handoff arm, then the relay arm above.
  Handoff arm: for each OPEN pull request, topic = `headRefName` less `fix/` and
  `-pr`; if `handoff-body/<topic>` and `handoff/<topic>` exist and the handoff is
  not an ancestor of the PR head, it runs `update_pr.sh <branch> <code-sha>
  <BODY.md> <issues>` (issues = the body's closing keywords; BODY.md is written
  to a per-run `cloud-body.*` directory under the state dir and removed after,
  since prepr refuses a body directly in a shared temp root), then
  `approve_held_runs.sh` on the branch, then `bus.sh dispatch <pr> <new head>
  cloud`, and appends `OWED reviewer-fire <pr> <head40> <nonce> <utc>` to the
  log (firing the cloud reviewer stays with the orchestrator). It only updates an
  existing PR, so the open-PR soft cap is untouched (an update is not an open).
  A handoff already inside its PR, or with no body ref, does nothing; a failed
  update is noted in `cloud-handoff-failed` by `<topic> <code-sha>`, logged
  `OWED handoff-update`, and retried only when the handoff moves. An update that
  exits 75 is `update_pr.sh`'s BUSY (another run holds the branch's
  `upd-<branch>.lock`, typically the orchestrator's own update of that PR): it is
  not recorded, and the next pass retries it. Every
  `handoff/*` or `handoff-body/*` ref whose topic has no open pull request
  appends `OWED <utc> handoff-no-pr <ref> <sha>` on every pass until disposed
  the same way (a fixer's return the orchestrator has not opened, or a merged
  PR's refs not yet archived); a failed PR listing reports none, since an
  empty list would make every ref look orphaned. Note the two
  OWED shapes: `OWED reviewer-fire` carries no timestamp first, the others
  (`OWED <utc> ...`) do.
- `codeql-triage-poll.sh` — polls until GitHub attaches the #1769
  evidence-alerts, dismisses them, re-runs CodeQL. When: a tools/ diff trips
  CodeQL on evidence files; nothing to do until the alerts exist.
- `daemonize.py` — detaches one long-running instrument from the session that
  started it: fork/setsid/dup2/execvp around any `-- CMD`, with the log's
  first line a banner naming the child pid, UTC time and full argv (the #2180
  lessons: banner first, unbuffered), append mode so relaunches extend one
  attributable file. When: a watch or sweep that must outlive its session —
  round 9 re-derived the wrapper in /tmp four times before this existed.
  Refusal: `--log` is mandatory and a non-existent `--cwd` aborts; no lock or
  pid bookkeeping — the printed pid and `kill` are the stop story.
- `delivery_row.sh` — the one seat-script writer of a PR's own `**open**`
  row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and
  `handoff_push.sh`: `commit_row` commits it as tvofi, `ensure_row` adds it
  only when the head lacks it. `record_row.py` is the other row writer, for
  the record beat's rows and its own PRs. When: never by hand; the openers
  call it. Refusal: none; `ensure_row` adds nothing to a head that carries
  the row, and `bus.sh --self-test` runs its self-test and refuses a seat
  script with its own `write_row` or row commit.
- `failure_logs.sh` — answers why a PR's newest red at its live head is red:
  latest failing check-runs (grouped by name, newest `started_at` wins, so
  red-then-green is not read as a failure) -> `details_url` -> job log ->
  error lines, per-check log files and a `HEAD.txt` under the out-dir. When:
  any red whose cause a watcher's state line does not carry. Refusal: a
  non-Actions check prints NO-JOB, an unserved log prints NO-LOG and exits 1
  with the count over readable logs beside the unread one; no error-marker
  match falls back to the log's tail, never a silent zero.
- `handoff_push.sh` — the legacy one-shot: pushes a handoff branch as
  `hpo-author` with body, title and its own delivery row (`delivery_row.sh`;
  its update path adds a row a refused earlier push left out). When: only where
  `dev/programme/HANDOVER.md` still names it; new work uses `open_pr.sh`/`update_pr.sh`.
- `handover_prompt.py` — generates the next-session prompt from the roster
  (and optionally a resume doc). When: ending a session; ready-next derives
  from the roster's after-edges. Refusal: none to speak of — read the output
  before pasting it, it is generated text.
- `merge_pr.sh` — merges one PR after its evidence checks. When: a single
  verdicted PR; for more than one, `merge_train.py` below. Owner mode takes
  `--mandate <comment-id>` and reads that #201 mandate live; `--ready` marks a
  draft ready. Refusal: a verdict or head mismatch stops the merge before the
  merge API call; a draft without `--ready`, or owner mode with no mandate in
  force, refuses before anything posts.
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
  in the train's own sequence behind record_row.py's identical guard;
  `--pre-flight` runs `queue_pre_flight.py` first and PARKs a failing entry;
  `--free-holders` detaches a clean, pushed holder worktree. Every refused
  merge attempt is logged in GitHub's words; the recarry worktrees a run made
  are removed before its closing line.
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
  Residual: a proved pair's second merge does not wait for main's run on the
  first; the proof graded the tree both make. A `batch/` branch the remote
  will not delete is logged `NOT deleted`, for deletion by hand.
- `moved_paths.py` — lists every line in the given files that names a path
  `tests/layout.json` marks moved: a retired file, its emptied directory, or
  a lifted prefix. Each hit is tagged FALLBACK when the line also names the
  new path. When: a move, or a review of one, before the push; a reader
  dispositions every STALE? hit. Refusal: none; it enumerates and always
  exits 0.
- `offline_spy.py` — runs a seat instrument's `--self-test` under a
  throwaway HOME and counts what it reaches outside: socket connects and DNS
  lookups (refused), gh/curl/wget/ssh/scp/nc calls on PATH (refused), git
  calls whose target resolves to a URL remote, and the Python process's
  subprocess creations. On macOS it also runs under `sandbox-exec`, denying
  outbound IP and writes outside the temp directories. When: before wiring a
  self-test into CI, and when reviewing one. Refusal: a non-zero exit, or any
  network or remote-git call, per file.
- `open_pr.sh` — opens a draft PR from `handoff/<topic>` as `hpo-author`,
  adds its own delivery row, re-pushes, prints N and the head. When: the
  orchestrator opens a seat's handed-off branch. Refusal, each an
  `open_pr: REFUSE:` line before anything is written (`pr_args.sh`): fewer
  than four arguments; a code sha that is not 40-hex or names no commit; one
  that is not an ancestor of `origin/handoff/<topic>`, saying whether it is the
  tip of `handoff-body/<topic>` ("that is the BODY sha; pass the CODE sha" —
  twice on 2026-10-18 that sha stopped the script silently); a missing
  `handoff/<topic>` or `handoff-body/<topic>`; no BODY.md at the body ref — the
  body is the transport, not an afterthought; the open-PR soft cap (tvofi,
  2026-10-18): `HPO_OPEN_PR_CAP` (default 6) or more open pull requests, drafts
  included, `record:`-titled and non-`hpo-author` bot ones excluded, unless a
  leading `--over-cap "<reason>"` overrides it, which prints `OVER-CAP` with
  the reason; a count it cannot read refuses (`pr_cap.py`). Any later stop
  prints `open_pr: STOPPED: line N exited S: <command>` (an ERR trap), and a
  refused push names its log. `--self-test` runs `delivery_row.sh`'s, then
  `pr_args.sh`'s.
- `orchestrator_tick.py` — the heartbeat's dispatch list: one read-only command
  that measures the whole board — train liveness, stale queue entries, log/rc
  tail, prepr slots; per open PR the latest check-run per name, reds unanswered
  in `## Red checks`, missing delivery rows, moved verdicts with no carry,
  DIRTY/BLOCKED, zero-run heads, absent required contexts, twin heads, claim
  stamps, staleness behind main; worker seats judged from the work they were
  dispatched for; roster groups newly unblocked or blocked; main's tip, its
  required contexts re-read live, the mandate through `budget_raise_gate`'s
  own reader, action-pin drift. When: run BY a watcher seat on a ~4-minute
  loop — never inline in the orchestrator's turn, whose cron firings skip
  while a turn runs (measured: ticks skipped for hours during one diagnosis
  turn); the watcher seat notifies only on actionable events (TRAIN
  DONE/STOPPED with skip classes, Traceback, silent train death, a new merge
  → beats owed) and never diagnoses or fixes. Every failed lane at main's
  tip — required or not — becomes a fixer dispatch brief (context, job id +
  error line, suspected class, dispatch instruction; bot lanes lead with the
  ci-autofix rule): a main-side issue the orchestrator cannot resolve in one
  short turn is fixer work, and the orchestrator's duty is routing, not
  diagnosing. It replaces re-deriving the
  sweep from conversation memory. It does NOT act; the orchestrator acts on
  the list. Operating contract it assumes: orchestrator turns stay SHORT; any
  script with over a minute of wait or execution runs BACKGROUND (nohup, log
  file, completion notification); findings are DISPATCHED, not merely printed
  — a finding that only lands in tick output repeats the
  PR-comment-is-not-propagation defect. Refusal: a section whose read fails
  prints UNREADABLE, never a silent skip; a rule the tick cannot read from
  the tree or API it does not report. Every pass prints two level lines in
  PRS (tvofi, 2026-10-18): `OPEN-PR CAP: N/CAP`, counted by `pr_cap.py`'s
  rule and flagged at or over the cap `open_pr.sh` refuses at, and
  `coordinator.py PRs: K/2`, the counted pull requests whose three-dot diff
  touches the coordinator, flagged over 2 or when a diff is unreadable. Also
  level lines every pass from the approver App's newest `Fix review:` on
  each open PR (the identity off `app_approve.sh`, the grammar `bus.sh`'s;
  the round-10 orchestrator, 2026-10-18): `MERGE-READY: #N <head8>` for a
  merge verdict at the current head on a CLEAN or UNSTABLE PR, and
  `BLOCKED-UNFIXED: #N <head8>` for a blocked verdict at the current head with
  no `handoff/<topic>` tip committed after it. A verdict at a stale head prints
  neither; comments it cannot read print UNREADABLE. One comments read per
  open PR per pass. A queue entry is unmerged only when its PR is in the open
  set (one `gh pr list --state open` per pass, TRAIN and REPLAN alike), never
  from a `pulls/<n>` `.state`, which reads `closed` for a merged PR: a queue
  whose entries are all merged prints no train-not-alive line (2026-10-18, t16).
  `OWED: <line>` prints every pass for each OWED entry in `cloud_relay.sh`'s
  log (its default, `$HPO_STATE_DIR/cloud-relay.log`) with no later POSTED for
  the same PR; no log yet prints no OWED. `OWED handoff: <bus.sh ORPHAN line>`
  prints every pass for each complete handoff no PR head carries, read by
  `bus.sh orphans --min-age-h 0` (a pull request behind its own newer handoff
  included, #2411); a run with no summary line is UNCHECKED, never a clean
  zero. STATE's missing-row check, the closes check and the #201
  unrecorded-merge check enumerate merges through
  `tests/delivery_status.py`'s `parse_log` and `collect`, so a `<title> (#N)`
  merge counts as a merge (#2413, #2412, #2407). `--only CARRY`
  (opt-in, weekly and at closure; never in the default pass) runs
  `carry_audit.py sweep --last N --issues` over origin/main and the tick's
  roster ref: exit 1 prints one dispatch line and the unowned lines, and a
  run without its `CARRY-SWEEP:` summary is UNREADABLE. Its driver is
  `tick_loop.sh`.
- `plan_table.py` — renders the plan artifact from a wave-groups roster:
  swimlanes, mermaid gantt (critical path tagged `crit`), per-group detail,
  ETA. When: regenerating the plan table after a roster edit. Refusal: none —
  but the gantt's grammar checks run in `--self-test`, not at render time.
- `policy_reread_check.py` — says whether a session owes a policy re-read:
  OK when `--stamp`'s instant is later than the newest compaction in
  `--transcript` (a JSON line whose `subtype` is `compact_boundary`), else
  OWED; `--write-stamp` records a finished re-read in the format the check
  reads. When: the sweep's step 0 (`sweep_template.md`), after every
  compaction. Refusal: it fails closed -- no stamp, an unparseable one, one
  ahead of the clock, an unreadable transcript, or a line naming the marker
  that is not JSON each print OWED, never OK. `--self-test` drives both arms.
- `pr_args.sh` — sourced by `open_pr.sh` and `update_pr.sh`: their argument
  checks and the ERR trap that reports every other stop, so neither stops
  silently. When: never by hand; `--self-test` drives both scripts end to end
  in a scratch repository, offline, each refusal arm beside a mutant that
  deletes its predicate line (`# mut:<name>`) and must fail the arm, plus
  null controls that pass every check. Refusal: its self-test's tally.
- `pr_cap.py` — the open-PR soft cap's one counting rule (tvofi, 2026-10-18):
  `gate` for `open_pr.sh`, imported by `orchestrator_tick.py`. A bot is a
  GitHub-flagged bot other than `app/hpo-author`, which authors every seat PR.
  When: `open_pr.sh` before it opens; the tick every pass. Refusal: at or over
  the cap without `--over-cap <reason>`; an empty reason; an invalid
  `HPO_OPEN_PR_CAP`; a list gh cannot read, that is not JSON, or that reaches
  gh's 200 limit.
- `proof_watch.py` — watches one named check-run at one pinned head of one
  pull request and, once it completes `success` beside green required contexts
  and a valid merge verdict at that exact head, merges through `merge_pr.sh`.
  When: a long validating run whose green-to-merge window would otherwise sit
  unattended (the 4.5 h proof misread as failed, P8). Refusals: a head that
  moved off the pin, a named check that completed not-success, an exceeded
  `--budget`, a red required context (the ruleset's list, read through
  `merge_train.required`), an unmergeable pull request and a head
  `app_approve --dry-run` does not verdict — each aborts with a logged report
  and no merge; one instance per pinned head (flock), and `--dry-run` passes
  every guard and touches nothing.
- `prune_refs.py` — reconciles the remote branch refs down to main plus a few
  development branches at programme closure, archive-as-tags first. When: the
  R9-CLOSURE-BRANCHES step 4 (prune by rule), and any future round's closure.
  Four rules -- keep `main` and any ref whose pull request is OPEN; delete a
  ref already merged into main, and an unmerged `handoff/*` ref whose pull
  request merged (a same-named PR, or the branch of a roster group the roster
  records `done`); enumerate the residue (no PR, or a closed-unmerged one) for
  an individual disposition, archived-and-deleted by default. Refusals: a plan
  that would act on `main`, and any `verdict/*` deletion while `--verdicts-drained`
  is unset (the bus watcher reads those refs). Every tag is created before any
  deletion, and `--archive-scope none` deletes nothing, so no tip is ever
  dropped unarchived; `--dry-run` (the default) prints the plan and writes
  nothing. `--self-test` drives the classifier, the planner, the precedence and
  the ordering offline (22 checks).
- `queue_pre_flight.py` — runs a merge queue's admission reads offline, before
  the train launches: per entry PASS, PARK (the train's own Stop wording — a
  carry that fails, a missing or stale delivery row, a GITHUB_TOKEN bot tip, a
  branch another worktree holds, a policy or budget head without the owner's
  in-force mandate) or FAIL (a verdict that is not 40-hex, a closed pull
  request). When: before any `merge_train.py run`/`batch` — an admission-time
  refusal parks the entry here instead of stopping a live queue mid-run.
  Refusal: exit 1 unless every entry passed; the checks are the train's own
  methods (`bot_tip`, `policy_gate`, `app_approve.sh --carry`), never new ones.
  `merge_train.py --pre-flight` runs it inside the train, passing the two
  shapes the train now cures itself: a bot tip, and under `--free-holders` a
  holder `Train.freeable` clears.
- `record_row.py` — the record-autofix generator: enumerates merged PRs from
  the REST API, plans the delivery rows the tree still lacks, applies them
  behind a guarded write set (`dev/programme/delivery/<N>.md` only). When: the periodic
  `record` beat. Refusal: any path outside `dev/programme/delivery/<N>.md` — the plan
  table and HANDOVER are a seat's dispositions, never this generator's — and
  a window it cannot attribute refuses rather than reports empty.
  `--automerge-check --pr N [--head SHA] [--hold] [--require-green]` is the
  guard CI approves and merges a record pull request behind (exit 3: guard
  passes, a required check has not yet); `--replay-moved` replays one
  older than the row directory's move. Refusal: any file but a new one-line
  row at its canonical path that the API's facts re-generate, or an author
  other than the hpo-author App.
- `ref_privacy.py` — the one owner of what a push may say about the host
  (#2310): `slug <path>` names a local path for a ref (`<root>-<rest>` under
  a named root, else `ext-<leaf>-<hash>`); `guard --ref R [--message M]
  [--commits REV -C DIR]` refuses a ref name or commit message carrying the
  home directory, an account name, the uid, a session temp root or a host
  path (exit 3, the class named, the text not echoed); `--check` refuses a
  tracked file with a push site its `PUSHERS` registry does not name, and a
  `guarded` entry that calls no guard. When: before every push an instrument
  composes; a new pusher registers in `PUSHERS` in the same diff. Refusal: a
  push that would publish the host never runs.
- `remerge_main.sh` — merges origin/main into an open PR (claimnotes merge
  driver), drops inherited claims, pushes as the App with `app_push.sh
  --recarry`, which prefixes ## Head with what happened and skips prepr only
  on a clean 2-parent merge of the live head and main under the live body.
  When: main moved under an open PR. Refusal: a conflict is not
  auto-resolved — it stops loudly instead.
- `run_twins.py` — counts a workflow's cancelled `pull_request` runs that
  sat beside a same-SHA sibling (two events at one head, not a
  supersession), from cached `/actions/workflows/<file>/runs` pages or
  `--fetch`. When: judging a workflow's `concurrency:` block (R9-CI-2a).
  Refusal: none; it enumerates.
- `resume_doc.py` — generates the resume markdown from the roster plus live
  PR state, under a byte budget. When: a state beat; regenerate rather than
  hand-edit the resume. Refusal: over-budget output refuses with `--out`
  unwritten — archive before regenerating.
- `roster_edit.py` — the safe roster edit: every op loads the whole roster,
  validates, and dumps with the file's own formatting; ops `set-stage`
  (with `--at-sha`), `wire-issue [--field fixes|issues]`, `unwire-issue <group> <N> [--field
  fixes|issues]` (refuses an absent N), `append-group`, `edit-brief`,
  `append-carry`, `drop-carry <group> <index|--match TEXT>` (0-based index,
  or the one entry containing TEXT; the last drop leaves `"carry": []`, the
  key kept),
  `set-after <group> <G1,G2,...|->` (replaces the after-edges whole, `-` for
  none), and `set-resume <group> --field
  <stage|commit|branch|last_step|next_step|note>` for the resume free-text
  fields a session restarts from. When: any roster change — never a string
  splice, which unbalanced the file twice. Refusals: the lint gate (run from
  a fresh origin/main checkout — a stale `--lint-cwd` is refused itself), an
  unknown group, a duplicate issue or carry, for `set-after` an unknown
  after-group, a self-edge, a repeated edge and a cycle in the resulting
  after-graph, for `drop-carry` an absent carry, an out-of-range index, no
  match and an ambiguous match, and for `set-resume` an empty
  value on the non-null fields (`stage`, `branch`) or a non-sha on
  `--field commit`; an empty value on a nullable field clears it to null.
  `--roster-ref` defaults to `main` and `--branch` to the round's
  `handoff/audit-r<N>-roster`, never main itself; `--roster-path` overrides
  the newest roster.
  A no-op edit reproduces the roster's bytes exactly and reports `no change`
  instead of an empty commit — the round-trip the self-test pins, because a
  dump that misses the file's formatting rewrites all 7503 lines on any edit.
- `roster_lib.py` — shared roster parsing and wave logic (depth, critical
  path, open groups, the branch-to-group lookup), and the one owner of WHICH
  roster: `roster_path` picks the newest `dev/programme/rosters/wave-r<N>-groups.json`
  (at a ref or on the checkout) unless `--roster-path` names one; and of
  WHICH REF: `default_roster_ref` answers the round's roster branch
  `origin/handoff/audit-r<N>-roster` when the clone has it, else
  `origin/main`, with a note whenever that answer may be stale. Import it;
  `--self-test` is its only CLI. When: any tool that reads the roster — one
  schema reader, not several. Refusal: no roster where one was asked for
  raises `RosterNotFound`, never a fallback to another round's.
- `seat_venv.sh` — builds the seat interpreter venvs reproducibly and installs
  the `shims/`. When: a new workstation or cloud seat; CI features are
  container-only on the Mac (no local venv for the Accelerate wheels).
  Builds `venv-ci` (CI's `fast` pins) and `venv-ha` (the typing lock,
  hash-pinned, `--no-deps`, cloud-setup.sh's pins call). `--check` reports
  both. `--self-test` drives the recipe and the shim export.
- `selftest_wiring.py` — refuses a self-testing file under
  `tools/audit/seat/` that no workflow `run:` line, comments removed, invokes
  with its self-test (`--check`, `--self-test`). Runs first among the seat
  steps of `instrument-self-tests`. When: adding a seat instrument with a
  `--self-test`; add its step in the same pull request. Refusal: each unwired
  file by path; a mention in a comment, a step name or a `--check` call does
  not wire it.
- `tick_loop.sh` — the tick's driver loop (tvofi approved, 2026-10-18): each
  pass runs `cloud_relay.sh pass` when the tree carries it (#2419; skipped
  and said so before), then `orchestrator_tick.py` with the given args,
  writing the board whole to `--out` (default `$HPO_STATE_DIR/tick.txt`) and
  one `TICK-PASS <utc> relay=<ok|rc=N|absent> tick=<rc>` line to stdout.
  When: run detached (`daemonize.py`) in place of a seat looping the tick;
  `--once` makes one pass, `--interval` defaults to 300 s. Refusal: a
  non-numeric `--interval` or an unknown option; a failing relay pass or tick
  is reported and the loop goes on. `--self-test` drives it over stubs.
- `train.sh` — one invocation shape for `merge_train.py batch`: the seat
  venv first on PATH — an absent venv refuses (naming `seat_venv.sh` to
  build it), it never falls back to ambient python, which on 3.11 refuses
  main's own nested-quote f-strings under `no-copies` — the child python
  unbuffered (`-u`, so a detached caller's log shows stops and SKIP/OVERLAP
  lines in real time), a pidfile refusing a second live train on the same
  state dir, log and exit code under the state dir (`train.log`, `rc`), and
  `--skip-bad`/`--overlap`/`--approval-carry`/`--bot-prs`/`--pre-flight`/
  `--free-holders`/`--main-moved-tries N` passed straight through, each only
  when given (a `0` default once passed `--skip-bad --overlap` on every
  launch), and the child run from the repository root when `--checkout` is
  absent (it once resolved to `tools/`). Foreground: the caller
  detaches and owns the schedule. When: every merge queue — the per-session
  scratch drivers this replaces duplicated the invocation, and one session's
  copy ran prepr under the wrong interpreter and refused a clean branch.
  Refusal: a live pidfile (take over only by removing it after checking the
  pid is dead). `--self-test` drives the five refusals and the child argv
  shape offline (missing required arg, live pidfile, unknown argument, the
  `--ignore-red` argv shape, the absent-venv refusal), the child's cwd on a
  launch without `--checkout`, and a bare launch's argv carrying no flag.
- `state_docs.py` — one call regenerates the three state docs
  (`plan_table.py`, `resume_doc.py`, `handover_prompt.py`), commits exactly
  their outputs to the orphan ref `handoff/audit-r<N>-plan` at
  `handoff/round<N>/state/`, N the roster's round, and mirrors them to
  `--mirror`. When: every state
  beat — it replaces the five hand commands (worktree, copy, commit, push,
  mirror) and runs the generators instead of copying their logic. Dry run by
  default: without `--push` nothing remote is written. Refusals: any path
  outside the three state docs (the write set is checked before a commit
  exists to push; every other path at the ref — a round's evidence — is
  carried untouched), a first commit that would not be exactly the three
  files, and an already-current tip, which is reported and left alone. The
  commit is plumbing over a temp index, so the calling checkout's index is
  never touched.
  `state_docs.py beat` is the same instrument on a loop, and it lives here
  rather than in a session's scratch for decision 0013's reason — an
  instrument the programme runs belongs where a later session can test it. A
  pass reads `--watch-ref` and the roster ref at origin (O17: a roster edit
  moves the state docs as a merge does); when either has moved it refreshes
  the roster ref (so resume fields other seats wrote are visible),
  regenerates and pushes, and when neither has it writes nothing at all.
  With no `--roster-ref` the roster ref is `roster_lib.default_roster_ref`'s. When:
  continuously beside a merge train, since it takes no lock and cancels
  nothing — the state docs are regenerated rather than rebuilt at session
  end. Refusal, and the one that saves you: the tip is recorded ONLY on a
  regeneration that returned 0, so a push the remote rejected is retried on
  the next pass instead of silently dropping that merge from the record.
  `--once` is one pass and returns that pass's code; without `--tip-file` a
  `--once` caller regenerates every time, so give it one to keep the loop's
  memo on disk. `--self-test` drives all three arms offline.
- `sweep_render.py` — renders the orchestrator sweep from
  `sweep_template.md` and a session's JSON overlay (stdout or `--out`). The
  template's `## Placeholders` table is the one registry of names. When: a
  session or round sets up its recurring sweep -- render it, never hand-copy
  the last session's prompt; the overlay stays out of the tree. Refusal: an
  unfilled, empty or non-scalar value, an undeclared placeholder or overlay
  key, a declared name the sweep never uses, a cited `tools/`, `tests/`,
  `dev/` or `.github/` path that is not in the tree, and a home directory
  (`ref_privacy.py`'s `HOME_DIR`) in the rendered text that no overlay value
  supplied -- each exits 1 and writes nothing. `--self-test` renders the
  tracked template and drives every refusal beside its null control.
- `sweep_template.md` — the orchestrator's recurring sweep, steps in order,
  each naming the instrument it runs by tree path and the rule file
  (`orchestrator.md`, `nudge.md`, `CLAUDE.md`) it carries out; a usage guide
  that restates no policy. When: read through `sweep_render.py`. Refusal: none
  of its own -- the renderer's.
- `tmp_paths.py` — refuses a tracked script, workflow or decision record that
  depends on a temp or machine path (`--check`, `--self-test`). When: after
  touching anything under `tools/`, `tests/`, `.claude/`, or before pushing.
  Refusal: every match on its own line — a `/tmp` state name, a `$TMPDIR`
  with a fixed name, a home path, an instrument run from `~/`; the 2026-10-03
  temp cleanup deleted three tracked tools' state and one decision's design
  note. It also refuses a temp, home or seat-directory path on a
  `tests/mutation_ledger/` line the diff adds (a triage citing a probe no
  other seat can run); main's stock is not charged.
- `update_pr.sh` — brings an open PR branch to its head + a code SHA (merge) +
  origin/main (merge), adds the PR's own delivery row when the head lacks
  it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as
  `hpo-author`. When: updating a PR after review prep or a main merge.
  Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
  silently; no open PR at the branch stops before any push. Up front, each an
  `update_pr: REFUSE:` line (`pr_args.sh`): fewer than three arguments; a
  code sha other than `-` that is not 40-hex, names no commit, or is not an
  ancestor of `origin/handoff/<topic>` (the topic `HANDOFF_TOPIC`, else the
  branch less `fix/`, then less `-pr`), naming a `handoff-body/<topic>` tip as
  the BODY sha; a missing `handoff/<topic>`; no body file. The body is a file
  here, so a missing body ref is no refusal. Any later stop prints
  `update_pr: STOPPED: ...`, and a refused push names its log.
- `wt_sync.sh` — snapshots every worktree whose state is not already on
  origin (unpushed commits, uncommitted or untracked files) to
  `origin/wip-sync/<slug>`, plus the orchestrator scratch. The slug is
  `ref_privacy.py slug`'s, never a host path (#2310). When: loop it
  detached so a crashed seat is recoverable from its branch. Refusal: it
  never touches the worktree or its index — a snapshot, not a save; a
  worktree whose snapshot would name the host is skipped with the guard's
  reason.
- `shims/seat-python`, `shims/seat-python3` — the seat interpreter: execs the
  venv-ci `seat_venv.sh` builds, under `$HPO_STATE_DIR` first and the default
  state root `~/.local/state/hpo` second, and refuses naming that build command
  when neither holds one; exports `HPO_TYPING_PYTHON` to venv-ha/bin/python
  under the same two roots, only when that interpreter exists and the variable
  is unset. When: a seat's PATH needs a pinned interpreter, and the scoped gate
  should check the mypy census.
