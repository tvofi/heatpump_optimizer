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
- `fastpath_census.py` — measures how often `merge_fastpath.py` would have
  said ELIGIBLE over main's last N merges. When: re-justifying (or retiring)
  the fastpath with numbers. Refusal: `INJECT=1` — without it the census
  measures nothing and says so.
- `fold_ledger.py` — folds a round's JUDGE.json and sweeps into
  `bugclasses.json`, and checks the register against the judges. When: after a
  judge lands, and before quoting the bugclass register as current state.
  Refusal: `check` refuses a register that drifted from its judges — re-quote
  the register, not a memory of it.
- `judge_batch.py` — re-runs every finding's harness, perturbation and null
  control serially under the gate lease, one row per finding. When: a judge
  grades a batch of findings and wants the mechanical half scripted. Refusal:
  a perturbation that does not move the number in the stated direction prints
  `void`; what it cannot run prints `by-hand`, never a pass.
- `merge_fastpath.py` — answers whether a verdicted PR can merge without a
  fresh CI run: did anything main changed since the PR's CI base land inside a
  closure the PR's own scoped gate selected? When: a merge train stalls on
  "main moved after CI". Refusal: an unrecorded file in the diff — ELIGIBLE
  needs every touched path measured, and "unrecorded" refuses.
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

- `body_push.sh` — publishes a handoff's BODY.md on the orphan ref
  `handoff-body/<topic>` (plus RESUME.md), parentless first commit,
  fast-forwards after. When: every fixer handoff — the body must never enter
  the code head's ancestry (`prepr.sh` step 1a refuses that). Refusal: a
  fetch that half-failed leaves a parentless commit the push refuses as a
  non-fast-forward — a rewrite is never forced through.
- `bus.sh` — git refs as the programme's message bus: seats publish verdicts
  on refs, the orchestrator watches. When: a reviewer seat with no other
  channel, or an orchestrator collecting several lanes' verdicts at once.
- `ci-watch.sh` — watches open PRs' check states and alerts only on NEW
  states (per-PR signature file). When: a long fix wave where red-on-main or
  a fresh failure must interrupt work. Refusal: state already seen prints
  nothing — the exit-1 report is the alert, not the log.
- `cloud-setup.sh` — the cloud seat environment's setup script (interpreter,
  CI-run pinning). When: tvofi pastes it into Project settings; a seat cannot
  apply its own environment.
- `codeql-triage-poll.sh` — polls until GitHub attaches the #1769
  evidence-alerts, dismisses them, re-runs CodeQL. When: a tools/ diff trips
  CodeQL on evidence files; nothing to do until the alerts exist.
- `handoff_push.sh` — the legacy one-shot: pushes a handoff branch as
  `hpo-author` with body, title and its own delivery row. When: only where
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
  this, never by hand. Refusal: a head that moved under the review, or red
  checks the queue was not told to ignore, stop the train.
  `batch` merges the queue without re-merging main: the entries' merges are
  proved together on `batch/<tag>-<n>` (B), a lone entry merges unproved (D),
  and workflow, claim, grader, budget or conflicting entries go serial. When:
  the default for a queue. Refusal: a red main admits nothing; a red proof
  drops its entry to serial,
  and main's tree differing from the proof's before or after a merge stops it.
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
- `plan_table.py` — renders the plan artifact from a wave-groups roster:
  swimlanes, mermaid gantt (critical path tagged `crit`), per-group detail,
  ETA. When: regenerating the plan table after a roster edit. Refusal: none —
  but the gantt's grammar checks run in `--self-test`, not at render time.
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
- `remerge_main.sh` — merges origin/main into an open PR (claimnotes merge
  driver), drops inherited claims, pushes as the App, prefixes ## Head with
  what happened. When: main moved under an open PR. Refusal: a conflict is
  not auto-resolved — it stops loudly instead.
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
  (with `--at-sha`), `wire-issue`, `append-group`, `edit-brief`,
  `append-carry`, and `set-resume <group> --field
  <stage|commit|branch|last_step|next_step|note>` for the resume free-text
  fields a session restarts from. When: any roster change — never a string
  splice, which unbalanced the file twice. Refusals: the lint gate (run from
  a fresh origin/main checkout — a stale `--lint-cwd` is refused itself), an
  unknown group, a duplicate issue or carry, and for `set-resume` an empty
  value on the non-null fields (`stage`, `branch`) or a non-sha on
  `--field commit`; an empty value on a nullable field clears it to null.
  A no-op edit reproduces the roster's bytes exactly and reports `no change`
  instead of an empty commit — the round-trip the self-test pins, because a
  dump that misses the file's formatting rewrites all 7503 lines on any edit.
- `roster_lib.py` — shared roster parsing and wave logic (depth, critical
  path, open groups, the branch-to-group lookup). Not a CLI: import it.
  When: any tool that reads the roster — one schema reader, not several.
- `seat_venv.sh` — builds the seat interpreter venvs reproducibly and installs
  the `shims/`. When: a new workstation or cloud seat; CI features are
  container-only on the Mac (no local venv for the Accelerate wheels).
  Builds `venv-ci` (CI's `fast` pins) and `venv-ha` (the typing lock,
  hash-pinned, `--no-deps`, cloud-setup.sh's pins call). `--check` reports
  both. `--self-test` drives the recipe and the shim export.
- `state_docs.py` — one call regenerates the three state docs
  (`plan_table.py`, `resume_doc.py`, `handover_prompt.py`), commits exactly
  their outputs to the orphan ref `handoff/audit-r9-plan` at
  `handoff/round9/state/`, and mirrors them to `--mirror`. When: every state
  beat — it replaces the five hand commands (worktree, copy, commit, push,
  mirror) and runs the generators instead of copying their logic. Dry run by
  default: without `--push` nothing remote is written. Refusals: any path
  outside the three state docs (the write set is checked before a commit
  exists to push; every other path at the ref — a round's evidence — is
  carried untouched), a first commit that would not be exactly the three
  files, and an already-current tip, which is reported and left alone. The
  commit is plumbing over a temp index, so the calling checkout's index is
  never touched.
- `tmp_paths.py` — refuses a tracked script, workflow or decision record that
  depends on a temp or machine path (`--check`, `--self-test`). When: after
  touching anything under `tools/`, `tests/`, `.claude/`, or before pushing.
  Refusal: every match on its own line — a `/tmp` state name, a `$TMPDIR`
  with a fixed name, a home path, an instrument run from `~/`; the 2026-10-03
  temp cleanup deleted three tracked tools' state and one decision's design
  note.
- `update_pr.sh` — brings an open PR branch to its head + a code SHA (merge) +
  origin/main (merge), prefixes ## Head with what happened, pushes as
  `hpo-author`. When: updating a PR after review prep or a main merge.
  Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
  silently.
- `wt_sync.sh` — snapshots every worktree whose state is not already on
  origin (unpushed commits, uncommitted or untracked files) to
  `origin/wip-sync/<slug>`, plus the orchestrator scratch. When: loop it
  detached so a crashed seat is recoverable from its branch. Refusal: it
  never touches the worktree or its index — a snapshot, not a save.
- `shims/seat-python`, `shims/seat-python3` — the seat interpreter: execs the
  venv-ci `seat_venv.sh` builds under `$HPO_STATE_DIR` (default
  `~/.local/state/hpo`) and exports `HPO_TYPING_PYTHON` to venv-ha/bin/python
  only when that interpreter exists and the variable is unset. When: a seat's
  PATH needs a pinned interpreter, and the scoped gate should check the mypy
  census.
