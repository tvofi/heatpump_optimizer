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
- `ci-watch.sh` — watches open PRs' check states and alerts only on NEW
  states (per-PR signature file): reds, CONFLICTING/DIRTY, STALLED zero-runs,
  and required contexts ABSENT at a settled head — a bot GITHUB_TOKEN push
  fires no `pull_request` run, so the governance family never reports at such
  a head and it sits unmergeable looking green (R9-RC-AUTOFIX-GOVERNANCE).
  When: a long fix wave where red-on-main or a fresh failure must interrupt
  work. Refusal: state already seen prints nothing — the exit-1 report is the
  alert, not the log; an unreadable ruleset alerts BLIND once rather than
  silently skipping the ABSENT arm. `--self-test` grades every arm offline on
  the recorded defect shape; `CI_WATCH_ONCE=1` runs a single cycle.
- `cloud-setup.sh` — the cloud seat environment's setup script (interpreter,
  CI-run pinning). When: tvofi pastes it into Project settings; a seat cannot
  apply its own environment.
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
  verdicted PR; for more than one, `merge_train.py` below. Refusal: a verdict
  or head mismatch stops the merge before the merge API call.
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
- `open_pr.sh` — opens a draft PR from `handoff/<topic>` as `hpo-author`,
  adds its own delivery row, re-pushes, prints N and the head. When: the
  orchestrator opens a seat's handed-off branch. Refusal: no BODY.md at
  `handoff-body/<topic>` — the body is the transport, not an afterthought.
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
  the tree or API it does not report.
- `plan_table.py` — renders the plan artifact from a wave-groups roster:
  swimlanes, mermaid gantt (critical path tagged `crit`), per-group detail,
  ETA. When: regenerating the plan table after a roster edit. Refusal: none —
  but the gantt's grammar checks run in `--self-test`, not at render time.
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
  `append-carry`, and `set-resume <group> --field
  <stage|commit|branch|last_step|next_step|note>` for the resume free-text
  fields a session restarts from. When: any roster change — never a string
  splice, which unbalanced the file twice. Refusals: the lint gate (run from
  a fresh origin/main checkout — a stale `--lint-cwd` is refused itself), an
  unknown group, a duplicate issue or carry, and for `set-resume` an empty
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
  (at a ref or on the checkout) unless `--roster-path` names one. Import it;
  `--self-test` is its only CLI. When: any tool that reads the roster — one
  schema reader, not several. Refusal: no roster where one was asked for
  raises `RosterNotFound`, never a fallback to another round's.
- `seat_venv.sh` — builds the seat interpreter venvs reproducibly and installs
  the `shims/`. When: a new workstation or cloud seat; CI features are
  container-only on the Mac (no local venv for the Accelerate wheels).
  Builds `venv-ci` (CI's `fast` pins) and `venv-ha` (the typing lock,
  hash-pinned, `--no-deps`, cloud-setup.sh's pins call). `--check` reports
  both. `--self-test` drives the recipe and the shim export.
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
  pass reads `--watch-ref` at origin; when it has moved it refreshes the
  roster ref (so resume fields other seats wrote are visible), regenerates
  and pushes, and when it has not it writes nothing at all. When:
  continuously beside a merge train, since it takes no lock and cancels
  nothing — the state docs are regenerated rather than rebuilt at session
  end. Refusal, and the one that saves you: the tip is recorded ONLY on a
  regeneration that returned 0, so a push the remote rejected is retried on
  the next pass instead of silently dropping that merge from the record.
  `--once` is one pass and returns that pass's code; without `--tip-file` a
  `--once` caller regenerates every time, so give it one to keep the loop's
  memo on disk. `--self-test` drives all three arms offline.
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
  silently; no open PR at the branch stops before any push.
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
