# Review packet #2936
head: ceb41a60bfe094903a2aac8b5f3f07af4cef83a4
base: b0b2d7697f8c5baaef2c082d9bf3242b57249e68

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=123118881874 skipped
cancel-superseded id=123118886602 in_progress
prelude id=123118887018 in_progress
refresh id=123118887193 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
FIGURES: 0 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/delivery/2936.md b/dev/programme/delivery/2936.md
new file mode 100644
index 000000000..eeaf2d99a
--- /dev/null
+++ b/dev/programme/delivery/2936.md
@@ -0,0 +1 @@
+- [#2936](https://github.com/tvofi/heatpump_optimizer/pull/2936) — **open**, R10-FLY-INSTRUMENTS-SPLIT: split INSTRUMENTS.md so a seat reads only its part (R10-FLY-INSTRUMENTS-SPLIT)
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index c2a5128fe..94ee8925b 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -3,7 +3,8 @@
 This is a usage guide, not policy: it says what each instrument does, when a
 real lane reaches for it, and which refusal saves you. The obligations live in
 `CLAUDE.md` and `.claude/rules/`; nothing here adds one. Every `--self-test`
-runs offline.
+runs offline. Each linked line below indexes one instrument; its text is
+`instruments/<name>.md`, beside this file.
 
 Directories here that are records, not instruments: `round3/`..`round9/`,
 `round5-fix/`, `round7-fix/`, `round8-fix/`, `handoff/`, `rca/`,
@@ -18,111 +19,22 @@ re-runnable measurement harnesses a fixer or judge lands with a PR — its
 
 ## tools/audit/
 
-- `app_approve.sh` — approves a pull request as the `hpo-approver` App at one
-  exact head SHA, only on a `merge` verdict for that SHA from an allowlisted
-  account (`--carry` re-approves a carried verdict). When: landing a
-  non-code-owned verdicted PR whose head the reviewer measured. Refusal: a
-  head SHA that is not the PR's current head, or a verdict whose SHA or
-  account does not match — the approval names one tree or it does nothing.
-  Its GitHub reads -- the four `gh api` reads and curl's JWT read of the
-  App's installation -- are under `seat/gh_read.py`'s read rule; the token
-  mint and the review POST are never retried.
-- `app_comment.sh` — posts one fix-review verdict on a PR as `hpo-approver`
-  and reads the posted comment back byte-identical. When: a reviewer seat
-  delivers a verdict. Refusal: a read-back that differs from what it meant to
-  post, or a stale head — "posted" is never taken from the send's exit code.
-- `app_push.sh` — pushes a branch and opens or re-bodies its pull request as
-  the `hpo-author` App, with the body's contract check before the push. When:
-  every handoff — pull requests are App-authored (decision 0011); `push.sh`
-  is the tvofi-identity predecessor and must not author PRs. Refusal: a body
-  failing the contract check never reaches the remote. `--row-only`
-  (`update_pr.sh`'s) replaces prepr with pr-contract's two body checks (the
-  contract, its red history read with prepr 7c's credential, and
-  `carry_audit.py check`) only when the head
-  is the live head plus one commit adding exactly that PR's own open row and
-  the body is the live one under one new `## Head` note; else prepr runs.
-  Every commit the PR adds over a freshly fetched `origin/main`, wherever it
-  was first published (a `ci-probe/*` or `handoff/*` ref included), is
-  judged by `ref_privacy.py guard --over` before anything is minted.
-- `depgraph.py` (tools/pr/) — compares GitHub's dependency graph with the
-  tree's pins: one SBOM read and one open-alerts read (`check --repo
-  OWNER/NAME`), every pip, npm and actions pin against the SBOM, and every
-  open alert the tree already pins past. When: Dependabot alerts that main's
-  locks should have closed, or `dependency-graph.yml`'s daily `check` is red.
-  Refusal: an SBOM ecosystem it does not enumerate, or an alert whose
-  versions it cannot order, exits 2 rather than reading clean; an alerts read
-  that fails prints `alerts: unread`, never OK.
-- `head_note.py` (tools/pr/) — prefixes a note under a body's `## Head`
-  heading, found as `checkPrBody`'s `sections()` reads it (outside a fence,
-  `##`, whitespace, `Head`), never the first substring `## Head`.
-  `app_push.sh --recarry`, `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
-  write every head note through it. When: any new writer of a `## Head`
-  note. Refusal: a body with no `## Head` heading exits 1, file untouched.
-- `approve_held_runs.sh` — approves the workflow runs GitHub holds
-  `action_required` on a branch. When: after the App pushes, the `pull_request`
-  workflows it created are held because the pusher is an App; a green gate
-  never starts until these are approved. Refusal: `--dry-run` lists what would
-  be approved; a branch with no held runs is a no-op, not an error to retry.
-- `check_scopes.py` — proves the finder scopes are disjoint and complete
-  within each dimension, from `scopes.json`. When: starting an audit round
-  (`audit-find` runs it in Prepare and refuses the round on failure) or
-  splitting one. Refusal: a cell owned twice, or owned by nobody — the
-  perturbed-scope `--self-test` is the null control.
-- `fold_ledger.py` — folds a round's JUDGE.json and sweeps into
-  `bugclasses.json`, and checks the register against the judges. When: after a
-  judge lands, and before quoting the bugclass register as current state;
-  `sync` after any hand edit of `finding.schema.json`, which rewrites
-  `audit-find.js`'s generated CLASS_GUESS and FINDING_REPORT (fold runs it).
-  Refusal: `check` refuses a register that drifted from its judges — re-quote
-  the register, not a memory of it.
-- `judge_batch.py` — re-runs every finding's harness, perturbation and null
-  control serially under the gate lease, one row per finding. When: a judge
-  grades a batch of findings and wants the mechanical half scripted. Refusal:
-  a perturbation that does not move the number in the stated direction prints
-  `void`; what it cannot run prints `by-hand`, never a pass.
-- `merge_fastpath.py` — classifies a changed file as workflow, claim, grader
-  or budget for `merge_train.py`'s batch routing: any such file sends a pull
-  request serial. Refusal: `--self-test` — `governance.yml` greps its
-  `checks, 0 failed` line.
-- `merge_throughput.py` — measures whether merges land inside the previous
-  merge's gate window often enough to justify a merge queue. When: someone
-  proposes a queue; the numbers decide before the mechanism is built. Its
-  `flow` subcommand is the flow board (Lean study K1): throughput against
-  the owner's demand of one roster group merged per hour, read from git
-  alone — the first-parent log, the review/verdict bus refs through
-  `review_strength`'s grammar and the roster through `roster_lib`. It prints
-  per rolling hour and per 24 h: groups closed against takt 1.0, fly-ins
-  closed, main moves split into group-carrying/record/roster-edit/fly-in,
-  WIP by flow lane (A/B/C/F), first-pass review yield with its blocked-class
-  mix, and lead time per size, and prints UNAVAILABLE rather than a zero
-  when a source cannot be read. When: any flow change that claims to move
-  throughput. Refusal: `--self-test` — its fixture's exact counts, the
-  unchanged-fixture null control, and a named arm per classification
-  predicate; `governance.yml`'s self-test step runs it.
-- `preflight.sh` — mechanical checks on anything the orchestrator publishes
-  (merge body, issue body, comment, brief): closing keywords and the claim
-  shapes. When: before posting any prose that GitHub or a later seat reads.
-  Refusal: a closing keyword in prose closes issues you did not mean to touch;
-  it refuses rather than warns.
-- `prepare_baseline.sh` — builds a round's audit baseline: a git-archive
-  export finders work in, one worktree per mutating finder, briefs copied in.
-  When: starting a round. Refusal: an archive run from a `git archive` copy
-  fails the `recorded_at` check on every mutant, baseline included — the M0
-  null run attributes that to the runner, not the findings.
-- `prepr.sh` — the pre-PR self-check on your own branch and body: head SHA
-  freshness, claim files byte-identical, the MODE line, carry destinations,
-  body headings, and the scoped-closure selection. When: always, before
-  handing a branch off. Refusal: each blocked reason names the artifact —
-  a branch that fails prepr locally would have burned a review round instead.
-- `push.sh` — pushes a branch and attaches a body that has already passed the
-  contract check, in that order (#678). When: tvofi-identity pushes only;
-  App-authored PRs go through `app_push.sh`. Refusal: the contract check runs
-  before the push, so the red `pr-contract` can never land on your review
-  head.
-- `worktree_gc.sh` — collects a merged PR's worktree, branch and seat
-  scratch. When: after merges, before the disk fills (9.5 GB of orphaned seat
-  directories once). Refusal: `--dry-run` prints the collection list; a
-  worktree with unpushed work is left alone.
+- [`app_approve.sh`](instruments/app_approve.sh.md) — approves a pull request as the `hpo-approver` App at one exact head SHA
+- [`app_comment.sh`](instruments/app_comment.sh.md) — posts one fix-review verdict on a PR as `hpo-approver` and reads the posted comment back byte-identical
+- [`app_push.sh`](instruments/app_push.sh.md) — pushes a branch and opens or re-bodies its pull request as the `hpo-author` App
+- [`depgraph.py` (tools/pr/)](instruments/depgraph.py.md) — compares GitHub's dependency graph with the tree's pins
+- [`head_note.py` (tools/pr/)](instruments/head_note.py.md) — prefixes a note under a body's `## Head` heading, found as `checkPrBody`'s `sections()` reads it (outside a fence, `##`, whitespace, `Head`)
+- [`approve_held_runs.sh`](instruments/approve_held_runs.sh.md) — approves the workflow runs GitHub holds `action_required` on a branch
+- [`check_scopes.py`](instruments/check_scopes.py.md) — proves the finder scopes are disjoint and complete within each dimension
+- [`fold_ledger.py`](instruments/fold_ledger.py.md) — folds a round's JUDGE.json and sweeps into `bugclasses.json`
+- [`judge_batch.py`](instruments/judge_batch.py.md) — re-runs every finding's harness, perturbation and null control serially under the gate lease
+- [`merge_fastpath.py`](instruments/merge_fastpath.py.md) — classifies a changed file as workflow, claim, grader or budget for `merge_train.py`'s batch routing
+- [`merge_throughput.py`](instruments/merge_throughput.py.md) — measures whether merges land inside the previous merge's gate window often enough to justify a merge queue
+- [`preflight.sh`](instruments/preflight.sh.md) — mechanical checks on anything the orchestrator publishes (merge body, issue body, comment, brief)
+- [`prepare_baseline.sh`](instruments/prepare_baseline.sh.md) — builds a round's audit baseline
+- [`prepr.sh`](instruments/prepr.sh.md) — the pre-PR self-check on your own branch and body
+- [`push.sh`](instruments/push.sh.md) — pushes a branch and attaches a body that has already passed the contract check, in that order (#678)
+- [`worktree_gc.sh`](instruments/worktree_gc.sh.md) — collects a merged PR's worktree, branch and seat scratch
 
 ## tools/audit/seat/
 
@@ -133,1018 +45,63 @@ have a contract: `dev/governance/roles/standing-tick.md` (the tick board),
 `dev/governance/roles/standing-roster.md` (roster ops). `pulse.py` and the
 sweep's standing-seat liveness step keep them alive.
 
-- `features_block.py` — runs one block of `tests/features.py`, from the line
-  holding a marker to the script's close, in the namespace features.py's
-  header builds. When: a mutation proof or a body figure that needs only the
-  block pinning the mutated line, on a seat where the whole script takes tens
-  of minutes. Refusal: a marker that is not in the script raises rather than
-  running an empty block.
-- `body_push.sh` — publishes a handoff's BODY.md on the orphan ref
-  `handoff-body/<topic>` (plus RESUME.md), parentless first commit,
-  fast-forwards after. When: every fixer handoff — the body must never enter
-  the code head's ancestry (`prepr.sh` step 1a refuses that). Refusal: a
-  head `tools/pr/ci_predict.py` predicts a closures or `fast` red on, or a
-  checkout with no predictor (R10-HANDOFF-PREPR-BOUNCE M2), is refused
-  before anything is pushed, with each arm's repair printed; a fetch that
-  half-failed leaves a parentless commit the push refuses as a
-  non-fast-forward — a rewrite is never forced through; the body commit it
-  wrote is read back through `ref_privacy.py guard --commits`, message and
-  identity, before the push.
-- `body_patch.sh` — repairs an open pull request's BODY without moving its
-  head: `body_patch.sh [--dry-run] [--repo O/R] <pr> <expected-head-sha>
-  <body.md>`. Reads the live head, runs the body contract offline at it
-  (`policy_lint.mjs --pr-body` with pr-contract's arguments, then
-  `carry_audit.py check --body`), PATCHes as `hpo-author` through
-  `tools/pr/app_mint.sh` (the mint `app_push.sh` shares), reads the body back
-  and re-reads the head. When: a body `pr-contract` or `carry_audit` refuses
-  on a head that must not move (ruling R4; `update_pr.sh` merges main on every
-  run). Refusal: a live head other than the expected sha, before any mint or
-  write; a body the contract refuses is never sent; `--dry-run` prints the
-  PATCH request and signs nothing; a read-back that cannot be performed in
-  three tries refuses, never reports OK. The offline contract runs the
-  caller's checkout, so it can differ from pr-contract's (the script header
-  says how). One `--once` unit: its last line is `body_patch: OK|REFUSE ...`.
-- `autofix_statuses.sh` — re-derives what `mutation-autofix` and
-  `closures-autofix` answered on recent pull-request runs, from their job
-  logs, with the `closures` failure heading behind each closures skip. When:
-  judging whether the autofix chain repairs anything. Refusal: a log GitHub
-  no longer serves is counted beside the totals, never read as a status.
-- `bus.sh` — git refs as the programme's message bus: seats publish verdicts
-  on refs, the orchestrator watches. When: a reviewer seat with no other
-  channel, or an orchestrator collecting several lanes' verdicts at once.
-  `orphans` discharges a handoff by name only when that `fix/<t>` or
-  `fix/<t>-pr` head carries the tip; a named head behind it is
-  `repair=update`.
-  With `HPO_BUS_TRAIN_STATE` set, each merge verdict it posts is added to
-  the merge train there (`merge_train.py add --auto`, one `BUS train-add`
-  line; the output in `train-add.log`); a refused add never fails the post.
-  `dispatch` is the worker registry's one writer (`$HPO_BUS_STATE/dispatched`,
-  `<pr> <head> <reviewer> <nonce> <utc> <model|->`): it closes
-  `reviewer-fire <pr> <head>` in the ledger (`$HPO_BUS_LEDGER`, else
-  `ledger.py`'s default log), `--nonce` re-records a relay-minted nonce for the
-  seat fired with it, and from a fourth round it needs the body's `## Re-cut`
-  note or `--past-three <reason>` (logged in `past-three`). `confirm` writes
-  the record's model as `bus-model:` on `verdict/<pr>`, which
-  `review_strength.py --guardrail` reads as a model arm; it refuses a replay of
-  a posted tree before it pushes. `dispatch` first renders the review packet
-  (`review_packet.py`) and names it as `review-packet:`. A REFUSED packet (the
-  head is unfit: rc 1, a named signal) refuses the dispatch and records
-  nothing; a packet this seat cannot RENDER (rc 3, `UNAVAILABLE`: no checkout,
-  no `gh`, no token, an unwritable path) dispatches anyway, names no packet,
-  and says why in `review-packet: unavailable -- <reason>`.
-- `review_packet.py` — the fix reviewer's packet at the frozen head: three-dot
-  diff, the head's check runs as read (red, pending, `none` or green, with run
-  ids), `carry_audit.py` and `figure_lint.mjs` at the head, the finder's
-  harness at both ends when one is named (`--harness`, at the base and
-  untouched by the diff, or `--harness-file` outside the tree; `none named`
-  and `not run` otherwise), and the mutation-ledger diff. When: through
-  `bus.sh dispatch`, which runs it in the checkout it is dispatching for; a
-  cloud reviewer, whose dispatcher's copy is a path on another machine,
-  renders its own from its dispatch prompt. Refusal: carry-audit, a `## Head`
-  not naming the head, a `tests/structure.py` refusal at the head merged with
-  main, an unanswered concluded red, a required context concluded failure, a
-  host path, or a hot file shared with an open pull request holding an
-  unboarded merge verdict; a pending check never refuses. A refusal still
-  WRITES the packet, so a held dispatch never withholds the evidence, except
-  a host path, which writes nothing because the packet carries the diff.
-  Unavailable (rc 3, `UNAVAILABLE`) is a different outcome: the seat cannot
-  read the packet's inputs (no checkout, no `gh`/token, a missing tool, an
-  unwritable `--out`), so it writes nothing and `dispatch` degrades.
-- `ci-watch.sh` — watches open PRs' check states and alerts only on NEW
-  states (per-PR signature file): reds, CONFLICTING/DIRTY, STALLED zero-runs,
-  and required contexts ABSENT at a settled head — a bot GITHUB_TOKEN push's
-  `pull_request` runs are held `action_required`, so until one is approved the
-  governance family does not report at such a head and it sits unmergeable
-  looking green (R9-RC-AUTOFIX-GOVERNANCE).
-  When: a long fix wave where red-on-main or a fresh failure must interrupt
-  work. Refusal: state already seen prints nothing — the exit-1 report is the
-  alert, not the log; an unreadable ruleset alerts BLIND once rather than
-  silently skipping the ABSENT arm. `--self-test` grades every arm offline on
-  the recorded defect shape; `CI_WATCH_ONCE=1` runs a single cycle.
-- `ci_critpath.py` — one workflow run's critical path from its job and step
-  timestamps (each job's queue, duration and longest step), its `needs:` read
-  from the run's own head, and a counterfactual holding every queue and
-  duration fixed: `--drop-edge NEED:JOB`, `--delete-job JOB`, `--charge
-  JOB=SECONDS` (the bare cost, stated by the caller). `--workflow F --last N`
-  prints median and p90 over the last N runs. The CI design archive's phase-2
-  method generalised (tag `archive/probe/design-ci-rev4`), and
-  `dev/audit/harnesses/r10_critpath_archive_parity.py` holds it to that
-  method's V1 numbers run for run. When: a job-graph change states the wall
-  it buys before it is built. Refusal: an edge the workflow does not have, a
-  needs cycle, or a run past `--max-reads` API reads; jobs and needs are
-  cached per run id and head, so a re-run reads only `--last`'s run list.
-- `cloud-setup.sh` — the cloud seat environment's setup script (interpreter,
-  CI-run pinning): it builds `venv-ci` and `venv-ha` under `/opt/hpo` and
-  writes the toolchain profile. When: tvofi pastes it into Project settings; a
-  seat cannot apply its own environment. A seat's Bash call inherits the
-  agent's environment and reads neither the profile nor `BASH_ENV`, so the
-  toolchain reaches it only through the environment's variables, which
-  `--variables` prints and the setup run's last line names; `--check`, in a
-  seat: `OK` (exit 0) only when all three hold, or `REFUSE` naming them (exit
-  1). The profile prepends `venv-ci/bin` only
-  when absent, so a PATH a caller narrowed is left alone; `--self-test`: the
-  profile, variables and check arms. Refusal: a missing checkout warns and
-  exits 0, so a session still starts, without pins.
-- `cloud_dispatch.py` — renders the whole cloud-runner trigger payload
-  (`job_config.ccr`: `environment_id`, `session_context` with `allowed_tools`,
-  `model` and `sources`, and one user-message event) for a `reviewer`,
-  `fixer` or `probe` seat from the PR, the 40-hex head, the bus nonce and an
-  optional brief file. The environment id, model and repository come from a
-  flag, an overlay JSON (`--overlay` / `$HPO_CLOUD_OVERLAY`) or `HPO_CLOUD_*`,
-  never from the tree. `--role R --group G --model M` is the one-call path
-  (`dispatch_group()` for a host such as the beat): the brief, topic and
-  repository come from the roster at `--roster-ref` (default the round's roster
-  branch, `roster_lib.default_roster_ref`); the head is `--head`, else
-  `origin/main`'s tip, never the roster ref's (a reviewer must pass its PR
-  head); the environment is the overlay / `HPO_CLOUD_ENV_ID`; a flag it does
-  not consume (`--topic`, `--brief`, `--repo`, `--env-id`, `--out`) refuses;
-  it renders through the same `render` (the payload is the flag path's byte
-  for byte), publishes PAYLOAD.json and PROMPT.md on origin as
-  `dispatch/<role>-<topic>` (fast-forwarded, an identical tree adds nothing, a
-  render refusal pushes nothing) and prints that ref name, the one line a
-  standing trigger is fired with; `dev/audit/harnesses/r10_flow_dispatch_mutants.py`
-  re-runs its mutants. When: dispatching a seat to the cloud runner;
-  paste the printed JSON as the trigger update, or fire the standing trigger
-  with the printed ref. The measured shape of a cloud seat:
-  every trigger update resends the full ccr and then `run`s it, never a
-  patch; the brief is snapshotted at `run`, so it is inlined at render time,
-  an edit afterwards reaches no running seat, and overlapping runs are fine;
-  the toolchain (`PATH` with `/opt/hpo/venv-ci/bin`, `BASH_ENV`,
-  `HPO_TYPING_PYTHON`, `OPENBLAS_CORETYPE`) comes from the environment's
-  variables, not from a profile the seat sources, so the prompt says only
-  that it is on `PATH`; the seat starts off `main` in a shallow clone
-  (`git fetch --unshallow --tags origin` first); the return signal is a
-  pushed ref: `probe/rev-<pr>-<nonce first 8>` for a reviewer (see
-  `cloud_relay.sh`: a cloud reviewer never runs `bus.sh`, whose dispatch record
-  lives on the orchestrator's machine and refuses "unknown nonce" anywhere
-  else, and a seat may not write a record it did not mint), `handoff/<topic>`
-  plus `handoff-body/<topic>` for a fixer, `handoff-body/<topic>` for a probe,
-  and a return push carries only the seat's own result tokens: a push
-  carrying system-file dumps is refused; the session is reachable one way,
-  by `SendMessage` to it, and nothing comes back on that channel. Refusal: a
-  head that is not 40 lowercase hex, a reviewer without a nonce or `--pr`, a
-  fixer or probe without `--topic`, a missing environment id, model or
-  repository, and any home-directory path in the rendered text
-  (`ref_privacy.HOME_DIR`, brief included). `--self-test` grades each
-  refusal against a rendering that passes, offline.
-  Two measured traps when driving the runner: an update and a run fired in
-  parallel start the run on the PREVIOUS config, so a launch is update, wait
-  for it, then run, sequentially; and, until the pasted setup script writes
-  `cloud-setup.sh`'s idempotent profile, the container's `BASH_ENV` puts the venv
-  python ahead of the test stubs, so a cloud seat runs `tests/entities.py` (and
-  anything else resolving `homeassistant`) with `env -u BASH_ENV`.
-- `cloud_relay.sh` — the orchestrator's half of a cloud reviewer's return:
-  `cloud_relay.sh <pr> <nonce> <head40>` fetches
-  `probe/rev-<pr>-<nonce8>`, grades it, then runs `bus.sh push-verdict` locally,
-  where the dispatch record lives; `bus.sh confirm` follows as for any verdict.
-  When: a `probe/rev-*` ref appears after dispatching a cloud reviewer. Refusal:
-  a nonce that does not match the verdict's `bus-nonce:` line, a ref whose
-  commit subject (`verdict <pr> <head>`) or verdict first line names another PR
-  or head, a missing `ev/`, and a ref already relayed (a ledger of
-  `<ref> <sha>` under the state directory, written only after `push-verdict`
-  succeeded, so a re-pushed ref relays again). `--self-test` grades each
-  refusal against a clean ref, offline, with `push-verdict` stubbed. It also
-  NORMALISES one shape and logs it (`normalised first line: A -> B`): a blocked
-  first line whose tail the reviewer wrapped, `blocked <head> [class: reason]`,
-  loses its one outer bracket pair in the relay's temp copy, which is lossless
-  and puts the line in `bus.sh`'s grammar (`blocked <head> <class>: <reason>`).
-  Chosen over refusing because the relay is the one place the verdict can be
-  repaired without a round trip to a cloud seat that has exited, and the
-  rewrite changes no word; a bracketed merge suffix, a nested bracket or a
-  class outside `[a-z-]+` is refused unchanged (stripping a merge suffix would
-  lose text). `cloud_dispatch.py`'s prompt now gives the unbracketed grammar.
-  `cloud_relay.sh --watch [--interval N] [--once]` is the orchestrator's poll
-  loop, tracked: every N seconds (default 120) it runs the probe arm, which
-  lists every `refs/heads/probe/*` with `git ls-remote origin`. A probe ref
-  that is not `rev-*` (a probe seat's return, a stray push) is
-  `OWED <utc> probe-ref <ref> <sha>` in `<log>.level` until
-  `cloud_relay.sh dispose <ref> <sha>` records it handled: a level, not a
-  diff, so a missed line is repeated rather than lost, and a disposed ref
-  that moves is owed again at its new sha. Every pass REWRITES its kind's
-  lines in `<log>.level` and appends none to the log (appended, 2026-10-21: 34757 copies
-  of ~281 items once reached the board); `dispose [--log FILE]` drops the
-  line at once from the level beside that log (the pass's `--log`), and a
-  failed listing leaves the level as it was. It relays each `rev-*` ref+sha
-  once, taking the head and full nonce from the dispatch record (`$HPO_BUS_STATE`
-  or `~/.zcode/bus`, `pr head thread nonce`). A ref with no record is logged and
-  left for a later pass; a refused ref+sha (relay rc 2, a refusal of the ref
-  itself) goes to `<ledger>.refused` and is not retried until it is pushed
-  again, so one refusal does not repeat every interval. Any other failure (a
-  push or a fetch; an HTTP 400 push once left a verdict refused in silence for
-  3 h) is retried on later passes, `HPO_RELAY_TRIES` times in all (default 3),
-  then refused. A refusal prints `REFUSED <ref> <sha> <reason>` (the relay's
-  last stderr line) and is `OWED <utc> probe-refused <ref> <sha> <reason>` in
-  `<log>.level` until disposed; one refused before reasons were kept stays
-  silent. Run it detached (`daemonize.py`); it uses ls-remote, not the REST
-  quota. `--once` is one pass.
-  `--confirm` (on `--watch` and on a single relay) keeps going past
-  `push-verdict`: after one that passed it runs `bus.sh confirm <pr>
-  <review-sha>` (review/<pr>'s tip as `git ls-remote` answers it, when that tip
-  carries this verdict's tree: confirm takes only a tip) and appends `POSTED
-  <utc> <pr> <sha>` or `OWED <utc> <pr> <sha|-> <why>`, `<why>` carrying
-  confirm's last output line, to `--log FILE` (default
-  `cloud-relay.log` under the state directory), the file the orchestrator
-  reads; two verdicts once sat relayed and unposted for 20 minutes. Confirm
-  never runs after a refused relay or a failed `push-verdict`, and those write
-  no line (the refusal is printed; `--watch` also keeps it in `.refused`).
-  A `push-verdict` refused non-fast-forward (review/<pr> moved under it) is
-  run again, three times at most: `bus.sh` re-reads the fresh tip and appends
-  the same verdict there, never forcing; a fresh tip already carrying this
-  verdict's tree is not re-applied. Both are printed, and so is
-  `review/<pr> remote tip <sha>` after the push.
-  `cloud_relay.sh pass [--confirm] [--log FILE] [--loop [--interval N]]` is the
-  orchestrator's whole beat as ONE entry point (it replaces the session-local
-  `relay_watch.sh`): a driver calls it once per tick, or `--loop` repeats it
-  (default every 120 s). A pass runs the handoff arm, then the relay arm above,
-  then with `--confirm` the confirm arm, then the stuck arm. Stuck arm (a
-  report-only trial, triage P163): each branch lock held now whose recorded
-  start epoch is older than `HPO_PUSH_STUCK_SECS` (default 900) prints
-  `STUCK <branch> <pid> <age>s` (the lock's name, the run's pid) and is
-  `OWED <utc> push-stuck <branch> <pid> STUCK ...` in `<log>.level`; a
-  released lock is never read. Confirm arm: the ledger is written
-  before confirm runs, so a confirm that failed, or a relay by a stale script
-  or a call without `--confirm`, was never confirmed later (#2659, #2632). For
-  every `review/<pr>` tip the relay pushed (its `bus-nonce:` matches a
-  ledgered `probe/rev-<pr>-<nonce8>`) whose tree is not in `bus.sh`'s posted
-  record (`posted-signed`), it runs `bus.sh confirm <pr> <tip>`: `POSTED` on
-  success; on failure `OWED <utc> confirm-owed refs/heads/review/<pr> <tip>
-  tries=<n>/<max>: <last output line>` in `<log>.level`, retried next pass up
-  to `HPO_RELAY_CONFIRM_TRIES` (default 3), then owed untried until the posted
-  record shows it or `dispose` takes it (`dispose` takes `review/` refs). A tip
-  with no dispatch for its PR, head and nonce is owed `undispatched` and never
-  confirmed; a tip the relay did not push waits for the orchestrator's own
-  read. It makes no `gh` call (`bus.sh confirm` posts).
-  Handoff arm: for each OPEN pull request, topic = `headRefName` less `fix/` and
-  `-pr`; if `handoff-body/<topic>` and `handoff/<topic>` exist and the handoff is
-  not an ancestor of the PR head, it runs `update_pr.sh <branch> <code-sha>
-  <BODY.md> <issues>` (issues = the body's closing keywords; BODY.md is written
-  to a per-run `cloud-body.*` directory under the state dir and removed after,
-  since prepr refuses a body directly in a shared temp root), then
-  `approve_held_runs.sh` on the branch, then `bus.sh dispatch <pr> <new head>
-  cloud`, and appends `OWED reviewer-fire <pr> <head40> <nonce> <utc>` to the
-  log (firing the cloud reviewer stays with the orchestrator). It only updates an
-  existing PR, which the soft cap never refuses (it gates only group dispatch).
-  Hold: `cloud-handoff-hold` under the state dir lists PR numbers, one per line
-  (blank and `#` lines allowed); only the orchestrator writes it. A listed PR
-  whose handoff is ahead is not updated and prints `HELD #<pr> <handoff tip>`
-  once per pass, so a frozen PR's head stays put while its handoff branch keeps
-  moving; removing the number resumes it. A missing or empty file holds nothing;
-  a line that is not a plain PR number refuses the whole handoff arm for that
-  pass (rc 2, `OWED handoff-hold-malformed` in `<log>.level`), never hold-all or hold-none.
-  `cloud_relay.sh held <pr>` answers from the same file (rc 0 held, 1 not, 2
-  malformed) for a driver that updates PRs itself.
-  Freeze (R10-FLOW-ROSTER-FREEZE): a PR whose live head is under review is not
-  updated either, so roster edits accumulate on the handoff ref and land between
-  reviews: a `Fix review: merge <head>` tip on `verdict/<pr>` at that head
-  (`HELD-VERDICT`), or a review of that head in flight with no verdict at it
-  (`HELD-REVIEW`: a `bus.sh dispatch` record of the PR at the head, or a
-  detached worktree at it). A verdict ref the listing names but the fetch
-  cannot read freezes too (`HELD-UNREAD`): it may be a merge at the head. A
-  blocked verdict, or one at an older head, freezes nothing. Each prints
-  `HELD-<why> #<pr> <handoff tip>` once per pass and is
-  `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in `<log>.level`;
-  `cloud-handoff-release` (the hold file's grammar) releases a listed PR from the
-  freeze, never from the hold, for new work that voids a merge verdict.
-  A handoff already inside its PR, or with no body ref, does nothing; a failed
-  update is noted in `cloud-handoff-failed` by `<topic> <code-sha>`, owed as
-  `OWED <utc> handoff-update <ref> <sha>` in `<log>.level` while that entry
-  matches the handoff's tip, and retried only when the handoff moves. An update that
-  exits 75 is BUSY (another `open_pr.sh` or `update_pr.sh` run holds the branch's
-  `upd-<branch>.lock`, typically the orchestrator's own update of that PR, or an `open_pr.sh` between its two pushes): it is
-  not recorded, and the next pass retries it. The update runs in a process
-  group of its own, so a signal to the loop's whole group reaches it only
-  through the loop's reap, and a KILL to that group leaves it to finish. The
-  `handoff-no-pr` lines in `<log>.level` are `ledger.py level`'s fold of
-  every `handoff/*` and `handoff-body/*` ref, rewritten every pass: owed unless
-  its topic has an open pull request, it is disposed at its sha, or main
-  already carries the change (ancestry, or content: see `ledger.py`), each
-  with its tip's commit time and last opener attempt; a failed PR listing or
-  ledger read leaves those lines as they were, since an empty list would make
-  every ref look orphaned. Every event the relay owes (`verdict-unposted` at
-  each passed push-verdict, `reviewer-fire`, `approve-held-runs`, `dispatch`)
-  is opened in the ledger, never appended to the log, which keeps only the
-  `POSTED` journal.
-- `codeql-triage-poll.sh` — polls until GitHub attaches the #1769
-  evidence-alerts, dismisses them, re-runs CodeQL. When: a tools/ diff trips
-  CodeQL on evidence files; nothing to do until the alerts exist.
-- `daemonize.py` — detaches one long-running instrument from the session that
-  started it: fork/setsid/dup2/execvp around any `-- CMD`, with the log's
-  first line a banner naming the child pid, UTC time and full argv (the #2180
-  lessons: banner first, unbuffered), append mode so relaunches extend one
-  attributable file. When: a watch or sweep that must outlive its session —
-  round 9 re-derived the wrapper in /tmp four times before this existed.
-  Refusal: `--log` is mandatory and a non-existent `--cwd` aborts; no lock or
-  pid bookkeeping — the printed pid and `kill` are the stop story.
-- `delivery_row.sh` — the one seat-script writer of a PR's own `**open**`
-  row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and
-  `handoff_push.sh`: `commit_row` commits it as tvofi, `ensure_row` adds it
-  only when the head lacks it. `record_row.py` is the other row writer, for
-  the record beat's rows and its own PRs. When: never by hand; the openers
-  call it. Refusal: none; `ensure_row` adds nothing to a head that carries
-  the row, and `bus.sh --self-test` runs its self-test and refuses a seat
-  script with its own `write_row` or row commit.
-- `failure_logs.sh` — answers why a PR's newest red at its live head is red:
-  latest failing check-runs (grouped by name, newest `started_at` wins, so
-  red-then-green is not read as a failure) -> `details_url` -> job log ->
-  error lines, per-check log files and a `HEAD.txt` under the out-dir. When:
-  any red whose cause a watcher's state line does not carry. Refusal: a
-  non-Actions check prints NO-JOB, an unserved log prints NO-LOG and exits 1
-  with the count over readable logs beside the unread one; no error-marker
-  match falls back to the log's tail, never a silent zero.
-- `flow_metrics.py` — a round's flow over one window, from git alone:
-  roster groups added and closed per hour (`--roster REF:PATH`, `--prefix`),
-  records' share of main's PR merges (`--record-prefix`), first-pass yield of
-  the merged fix PRs on the bus, main absorbs per fix branch, merge-to-merge
-  re-reviews of an unchanged PR diff (patch-id), and the share of hours with
-  a merge. When: a flow guardrail or a round's close reads throughput.
-  Refusal: a re-review whose heads git does not hold prints `unresolved`,
-  never counted; no round constant in code.
-- `gh_read.py` — the read rule every seat instrument's GitHub READS are
-  under, stated here once: `app_push.sh`'s read-back rule, 4 reads settling
-  5/15/45 s, retrying only a transport error, HTTP 5xx, 429 or a 403 whose
-  status line names the secondary rate limit; a failure naming a longer wait
-  (Retry-After, or a spent bucket's reset on a rate-limit response: a 429,
-  or a 403 naming a rate limit) is read no sooner, and one past 45 s refuses
-  at once naming it; any other status is judged by its code alone, whatever
-  bucket it carries. When: a new GitHub read in a seat instrument —
-  `retry` with `gh_wait` (gh's output) or `urllib_wait` (urllib's), and
-  `is_read` before retrying any `gh` call; `app_approve.sh`'s `gh_transient`
-  is the bash twin its self-test compares row for row. Refusal: every other
-  failure (401, a permission 403, 404, 422, an unclassified one) after its one
-  call, a spent budget with its last error and the attempt count; a write is
-  never retried. Its `self_test()` runs inside `record_row.py`'s.
-- `handoff_push.sh` — the legacy one-shot: pushes a handoff branch as
-  `hpo-author` with body, title and its own delivery row (`delivery_row.sh`;
-  its update path adds a row a refused earlier push left out). When: only where
-  `dev/programme/HANDOVER.md` still names it; new work uses `open_pr.sh`/`update_pr.sh`.
-  `--self-test` runs `delivery_row.sh`'s and its own: the three push calls
-  (open, update, row) over a scratch origin with a stub `app_push.sh`, so a
-  push line replaced by `true` reddens it (#2444). Every commit the code head
-  adds over `origin/main` passes `ref_privacy.py guard --over` before any
-  worktree or push, so a trailer the cloud harness pushed is refused there.
-- `handover_prompt.py` — generates the next-session prompt from the roster
-  (and optionally a resume doc). When: ending a session; ready-next derives
-  from the roster's after-edges. Refusal: none to speak of — read the output
-  before pasting it, it is generated text.
-- `merge_pr.sh` — merges one PR after its evidence checks. When: a single
-  verdicted PR; for more than one, `merge_train.py` below. Owner mode takes
-  `--mandate <comment-id>` and reads that #201 mandate live; `--ready` marks a
-  draft ready. Refusal: a verdict or head mismatch stops the merge before the
-  merge API call; a draft without `--ready`, or owner mode with no mandate in
-  force, refuses before anything posts. Before its CI wait it runs
-  `merge_train.py unstale` (below) at the head. `--self-test` also drives the whole
-  script offline over a scratch clone and a fake `gh`, so the `gh pr merge …
-  --match-head-commit` line is pinned: replaced by `exit 0` it records no
-  merge and the null control reddens (#2444).
-- `merge_train.py` — lands a queue of verdicted PRs one at a time: re-carry
-  CI, wait for green at the exact head, evidence-gated approval,
-  `--match-head-commit`. When: any merge queue — queued PRs merge through
-  this, never by hand. Refusal: a head that moved under the review, red
-  checks the queue was not told to ignore, or a head whose TIP is a
-  GITHUB_TOKEN bot push (author `github-actions[bot]`) stop the train — such
-  a head has no `pull_request` run, the required contexts never report at it,
-  and the required follow-up is an App push (step 1's recarry once main
-  moves; batch routes such a head serial, `bot-head`, where that recarry runs
-  after the batch's own merges). A foreign merge moving main under a settled
-  head is recovered up to `--main-moved-tries` (default 3; 0 is the old stop):
-  serially by a recarry and a fresh CI wait, in a batch by re-proving the rest
-  on the new main. An owner approval GitHub already holds at the live head is
-  the owner's, with nothing re-posted (GitHub re-anchors one across a clean
-  base merge: #2209). `--bot-prs` merges the open record/autofix pull request
-  in the train's own sequence behind record_row.py's identical guard;
-  `--pre-flight` runs `queue_pre_flight.py` first and PARKs a failing entry;
-  `--free-holders` detaches a clean, pushed holder worktree. Every refused
-  merge attempt is logged in GitHub's words; the recarry worktrees a run made
-  are removed before its closing line. Every `gh api` GET and `gh pr view`
-  it or `queue_pre_flight.py` makes is under `gh_read.py`'s read rule, each
-  settle logged.
-  `queue <file>` writes the queue nobody had to assemble: every open
-  pull request but the record one whose approver-App verdict is newest, is
-  `verdict/<pr>`'s posted tip and is `merge` at its head or carries to it
-  (`app_approve.sh --carry`), oldest first, one `QUEUE`/`LEFT` line each;
-  budget and policy heads are queued for the batch's own serial route.
-  `add`'s admission (`Train.admit_add`) reads the same posted verdict
-  first, as its `verdict` rule, and fills an absent comment id from it.
-  bus.sh's post loads the train the moment it posts a merge verdict
-  (`merge_train.py add --auto`, with `HPO_BUS_TRAIN_STATE` set);
-  `sweep` is the slow backstop (`tick_loop.sh --sweep`, every 1800 s by
-  default): unless the ledger holds an open train-stop, it `add`s each head
-  `queue` admits that no sweep added at that head, into the live train's
-  next batch or a `train.sh --bot-prs --approval-carry --pre-flight` it
-  starts when none is live, never a second.
-  `batch` merges the queue without re-merging main: the entries' merges are
-  proved together on `batch/<tag>-<n>` (B), a lone entry merges unproved (D),
-  and workflow, claim, grader, budget or conflicting entries go serial. When:
-  the default for a queue. Refusal: a red main admits nothing; a red proof
-  drops its entry to serial,
-  and main's tree differing from the proof's before or after a merge stops it.
-  `batch --skip-bad` makes a per-entry refusal (admission, recarry, carry, CI,
-  merge) fatal for its entry alone — logged `SKIP #<pr>`, reported in
-  `skipped.json` and a `SKIP REPORT` line, rc 1 — while a red main and a Stop
-  after the merge API call stay global. `batch --overlap` (owner's P7) does
-  not wait on main's CI (log-only) and re-carries every serial entry up front
-  so their pull_request runs fire together; each lands in queue order when
-  its own required contexts conclude — the ruleset still gates every head.
-  A serial entry whose base THIS batch's own merges moved is graded before it
-  lands (`Train.grade_merge`, R10-TRAIN-OVERLAP-GRADE): the merge GitHub
-  would make is built with the train's driver-free text merge, materialised
-  as a throwaway worktree, and read by `policy_lint` always and
-  `tests/structure.py` where `tests/closures.json` selects it for the merge's
-  files. A red posts no approval and is HELD: `MAIN-MOVED` re-carries it and
-  CI judges the new head, and a recarry that reproduces the same red tree
-  stops instead of looping. A one-car batch (the #2595 repair car onto a red
-  main) cannot move a base, so the grade never fires there.
-  `batch` also takes several batches in one queue (a list of lists), run in
-  order on one train, each with its own admission, proof and merges; between
-  two it drains what `train.sh add` spooled into one more batch, never into a
-  batch in proof, and a batch that stops ends the train (`NOT RUN` lines). A
-  policy head batches like any other: under a `--mandate` naming the mandate's
-  comment id, in force for policy merging, the train posts the citing approval
-  step 5 requires (`policy_approve`); a budget raise still goes serial.
-  `dev/audit/harnesses/r10_train_upgrade_mutants.py` holds one mutant per arm
-  of these three.
-  Residual: a proved pair's second merge does not wait for main's run on the
-  first; the proof graded the tree both make. A `batch/` branch the remote
-  will not delete is logged `NOT deleted`, for deletion by hand.
-  It owns the state classifier (Lean flow study K15) the tick also imports,
-  judged on the latest run of each required context (`main-protect-checks`,
-  read live; `record`, `record-autofix`, `nightly-status` and
-  `delivery-status` never count): a queued or in-progress run is a wait,
-  never red, and an unreadable ruleset refuses. `--overlap` logs main RED,
-  or still running, by that rule. Before a merge attempt a check-run still
-  queued or in progress over a completed workflow run is stale: its run is
-  re-run once, logged `STALE <context> ... run <id>` (a third recurrence goes
-  to a root-cause seat), and re-read. `unstale <sha>` runs that step alone;
-  `classify <sha>` prints GREEN (rc 0), RED (rc 1) or WAIT (rc 3) over a pull
-  request's required contexts (`--main`: less the PR-only ones), rc 2 when
-  unreadable — a head is reviewable unless RED.
-- `ledger.py` — the obligations ledger (R10-ORCH-LEDGER; the machinery
-  design's section 6.3): one table of kinds, two stores beside the relay's log
-  (`dispositions.tsv`, written only by `dispose`; `events.tsv`, append-only
-  `open`/`close`/`attempt`) and one fold. Derived kinds are recomputed each pass
-  (`level` derives `handoff-no-pr` for the relay; the tick derives
-  `design-build` and `review-owed`); event kinds are keyed on kind, subject and
-  sha, an open at a new sha superseding the old, and close by the producer's
-  `close`, a moved or closed pull request, or the tick's read-back of the
-  approver's comment (`verdict-unposted` only on its own first line: a relayed
-  POSTED closes nothing). `escalate` turns stranded handoffs into DISPATCH
-  lines, oldest first, naming the roster group, and an OWNER FLAG past the
-  second threshold, behind `HPO_LEDGER_AGING` (`<dispatch_h>,<owner_h>` or
-  `off`; default the owner's 4 h and 12 h). `open_pr.sh` records each opener
-  attempt on its handoff ref (`started`, then `opened,PR=<n>` or `unopened`).
-  The first run imports `cloud-disposed` (last disposition per ref) and the
-  log's still-open OWED lines; a reader folds that in memory and writes
-  nothing. Refusals: a ref of no arm, a kind of no table, a derived kind
-  opened. A missing store is first run; an unreadable one is UNREADABLE.
-  `board` exits 0 none owed, 1 owed (with its summary line), 2 unreadable.
-- `moved_paths.py` — lists every line in the given files that names a path
-  `tests/layout.json` marks moved: a retired file, its emptied directory, or
-  a lifted prefix. Each hit is tagged FALLBACK when the line also names the
-  new path. When: a move, or a review of one, before the push; a reader
-  dispositions every STALE? hit. Refusal: none; it enumerates and always
-  exits 0.
-- `offline_spy.py` — runs a seat instrument's `--self-test` under a
-  throwaway HOME and counts what it reaches outside: socket connects and DNS
-  lookups (refused), gh/curl/wget/ssh/scp/nc calls on PATH (refused), git
-  calls whose target resolves to a URL remote, and the Python process's
-  subprocess creations. On macOS it also runs under `sandbox-exec`, denying
-  outbound IP and writes outside the temp directories. When: before wiring a
-  self-test into CI, and when reviewing one. Refusal: a non-zero exit, or any
-  network or remote-git call, per file.
-- `open_pr.sh` — opens a draft PR from `handoff/<topic>` as `hpo-author`,
-  adds its own delivery row, re-pushes, prints N and the head. When: the
-  orchestrator opens a seat's handed-off branch. Refusal, each an
-  `open_pr: REFUSE:` line before anything is written (`pr_args.sh`): fewer
-  than four arguments; a code sha that is not 40-hex or names no commit; one
-  that is not an ancestor of `origin/handoff/<topic>`, saying whether it is the
-  tip of `handoff-body/<topic>` ("that is the BODY sha; pass the CODE sha" —
-  twice on 2026-10-18 that sha stopped the script silently); a missing
-  `handoff/<topic>` or `handoff-body/<topic>`; no BODY.md at the body ref — the
-  body is the transport, not an afterthought. The soft cap gates only
-  dispatching a new roster group, and never refuses opening or updating a pull
-  request for an owed handoff (tvofi, 2026-10-20): a leading `--over-cap
-  "<reason>"` is still accepted and prints that it is advisory; `pr_cap.py
-  info` prints the open count as information, and a count gh cannot read says
-  so and still opens. Any later stop prints `open_pr: STOPPED: line N exited S: <command>` (an ERR trap), and a
-  refused push names its log. It holds the branch's `upd-<branch>.lock` from
-  before its worktree to its second push, so a concurrent `update_pr.sh` is BUSY
-  (75) and cannot detach the worktree under the PR's row (#2547-#2549).
-  `--self-test` runs `delivery_row.sh`'s, then
-  `pr_args.sh`'s.
-- `orchestrator_tick.py` — the heartbeat's dispatch list: one read-only command
-  that measures the whole board — train liveness, stale queue entries, log/rc
-  tail, prepr slots; per open PR the latest check-run per name, reds unanswered
-  in `## Red checks`, missing delivery rows, moved verdicts with no carry,
-  BLOCKED, DIRTY with the conflicted files `git merge-tree` names under
-  GitHub's merge, no local driver run (the
-  claimnotes repair only when all are claim files; a content conflict goes
-  back to its fixer), NOT REVIEWABLE at a head whose required context
-  concluded red, zero-run heads, absent required contexts, twin heads, claim
-  stamps, staleness behind main; worker seats judged from the work they were
-  dispatched for; roster groups newly unblocked or blocked; main's tip, its
-  required contexts re-read live and judged by `merge_train.py`'s classifier,
-  the mandate through `budget_raise_gate`'s
-  own reader, action-pin drift. When: run BY a watcher seat on a ~4-minute
-  loop — never inline in the orchestrator's turn, whose cron firings skip
-  while a turn runs (measured: ticks skipped for hours during one diagnosis
-  turn); the watcher seat notifies only on actionable events (TRAIN
-  DONE/STOPPED with skip classes, Traceback, silent train death, a new merge
-  → beats owed) and never diagnoses or fixes. Every failed lane at main's
-  tip — required or not — becomes a fixer dispatch brief (context, job id +
-  error line, suspected class, dispatch instruction; bot lanes lead with the
-  ci-autofix rule): a main-side issue the orchestrator cannot resolve in one
-  short turn is fixer work, and the orchestrator's duty is routing, not
-  diagnosing. It replaces re-deriving the
-  sweep from conversation memory. It does NOT act; the orchestrator acts on
-  the list. Operating contract it assumes: orchestrator turns stay SHORT; any
-  script with over a minute of wait or execution runs BACKGROUND (nohup, log
-  file, completion notification); findings are DISPATCHED, not merely printed
-  — a finding that only lands in tick output repeats the
-  PR-comment-is-not-propagation defect. Refusal: a section whose read fails
-  prints UNREADABLE, never a silent skip; a rule the tick cannot read from
-  the tree or API it does not report. Every pass prints two level lines in
-  PRS (tvofi, 2026-10-20): `WIP: N/6 (open PRs M)`, N the roster groups whose
-  `resume.stage` is `in-progress` through `pr_cap.py`'s `wip_groups` and M its
-  counted open pull requests, flagged at or over `HPO_WIP_CAP` — at the cap a
-  new group is not dispatched, while opening and merging are always allowed;
-  and `coordinator.py PRs: K/2`, the counted pull requests whose three-dot diff
-  touches the coordinator, flagged over 2 or when a diff is unreadable. Also
-  level lines every pass from the approver App's newest `Fix review:` on
-  each open PR (the identity off `app_approve.sh`, the grammar `bus.sh`'s;
-  the round-10 orchestrator, 2026-10-18): `MERGE-READY: #N <head8>` for a
-  merge verdict at the current head on a CLEAN or UNSTABLE PR, and
-  `BLOCKED-UNFIXED: #N <head8>` for a blocked verdict at the current head with
-  no `handoff/<topic>` tip committed after it. A verdict at a stale head prints
-  neither; comments it cannot read print UNREADABLE. One comments read per
-  open PR per pass. A queue entry is unmerged only when its PR is in the open
-  set (one `gh pr list --state open` per pass, TRAIN and REPLAN alike), never
-  from a `pulls/<n>` `.state`, which reads `closed` for a merged PR: a queue
-  whose entries are all merged prints no train-not-alive line (2026-10-18, t16).
-  `OWED: <line>` prints every pass for each line of `cloud_relay.sh`'s level
-  file (`<log>.level`, beside its default log `$HPO_STATE_DIR/cloud-relay.log`;
-  a line of no ledger kind prints REFUSED) and for each event `ledger.py`'s
-  fold holds open against this pass's open-PR heads and read-back verdicts;
-  its stranded handoffs escalate to `DISPATCH:` and `OWNER FLAG:` lines
-  (`ledger.escalate`); no store and no log yet prints no OWED. `REVIEW OWED:
-  #N <head12>` prints for each open non-draft PR whose head no approver
-  verdict names and no `bus.sh` dispatch record carries, and PLAN prints
-  `DESIGN-BUILD:` for an approved `design/<g>` whose group has no build
-  dispatched. `OWED handoff: <bus.sh ORPHAN line>`
-  prints every pass for each complete handoff no PR head carries, read by
-  `bus.sh orphans --min-age-h 0` (a pull request behind its own newer handoff
-  included, #2411); a run with no summary line is UNCHECKED, never a clean
-  zero. STATE's missing-row check, the closes check and the #201
-  unrecorded-merge check enumerate merges through
-  `tests/delivery_status.py`'s `parse_log` and `collect`, so a `<title> (#N)`
-  merge counts as a merge (#2413, #2412, #2407). `--only CARRY`
-  (opt-in, weekly and at closure; never in the default pass) runs
-  `carry_audit.py sweep --last N --issues` over origin/main and the tick's
-  roster ref: exit 1 prints one dispatch line and the unowned lines, and a
-  run without its `CARRY-SWEEP:` summary is UNREADABLE. Its driver is
-  `tick_loop.sh`.
-- `plan_audit.py` — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the
-  `audit-plan` workflow. `ledger` parses each merged PR's
-  `## Architecture score` block with the parser `score.py`'s own report
-  answers to, reconciles it metric by metric against `PLAN.json`'s moves, and
-  demands the moves' sum account for `score.py --diff <fork> HEAD` within
-  `--tolerance`; a merged metric no move names, a planned group with no body,
-  an unexplained dS, an inadmissible reading or WORSENS fails, so a dS no
-  planned move explains is `metric-gamed` rather than banked (`snapshot`
-  likewise records the fork). `snapshot` records one ref's structure budgets,
-  gate-only tripwires, behaviour inventory (entities, services, option steps,
-  card tabs), mutation kill rate and 200-merge change coupling -- the fork's
-  read by `--instrument`'s own scorer, so both sides are measured by the base
-  -- and `compare` fails on any regression, with `--allow KIND:KEY` for a
-  removal the plan's ADR approved. When: the architect measures the fork, and
-  the stamp compares it. Refusal: `ARCHSCORE_ABLATE` set; a plan naming a
-  different fork; two snapshots read by different instruments; `--self-test`
-  (`governance.yml` greps its `checks, 0 failed` line).
-- `plan_page.py` — renders the round's plan page (HTML) from
-  `tools/plan/replan.py`'s plan.json, the roster through `roster_lib`, and
-  GitHub's issue and pull-request state (`gh`, or `--github-snapshot`):
-  swimlanes on the plan's time axis with the slot-occupancy strip,
-  critical-path marks and planned stamps; the group ledger with status
-  classes, PRs, struck closed issues and blockers; waves, stamps and the
-  ETA method, every figure plan.json's. First section: open issues on
-  not-done groups projected to close at the last carrying group's finish
-  (closed ones dropped, unplanned ones flat), omitted with a note when `gh`
-  is absent. When: after a replan at a wave
-  edge. Refusal: a plan `replan.stale_reason` calls stale (its roster blob
-  is not the roster's at its ref now; an `origin/` ref is fetched first) or
-  `replan.check_plan` refuses -- exit 1, nothing written. `--check` of
-  replan.py applies the same freshness rule.
-- `plan_table.py` — renders the plan artifact from a wave-groups roster:
-  swimlanes, mermaid gantt (critical path tagged `crit`), per-group detail,
-  ETA. When: regenerating the plan table after a roster edit. Refusal: none —
-  but the gantt's grammar checks run in `--self-test`, not at render time.
-- `policy_reread_check.py` — says whether a session owes a policy re-read:
-  OK when `--stamp`'s instant is later than the newest compaction in
-  `--transcript` (a JSON line whose `subtype` is `compact_boundary`), else
-  OWED; `--write-stamp` records a finished re-read in the format the check
-  reads. When: the sweep's step 0 (`sweep_template.md`), after every
-  compaction. Refusal: it fails closed -- no stamp, an unparseable one, one
-  ahead of the clock, an unreadable transcript, or a line naming the marker
-  that is not JSON each print OWED, never OK. `--self-test` drives both arms.
-- `pr_args.sh` — sourced by `open_pr.sh` and `update_pr.sh`: their argument
-  checks, the ERR trap that reports every other stop, so neither stops
-  silently, and `pr_branch_lock`, the per-branch lock both take. The lock
-  outlives the run's push whatever stops the run: its holder ignores TERM,
-  INT and HUP, and lets go only once the push's own lock (`pr_push_hold`, an
-  fd every process of the push inherits) is free, so a SIGKILLed run's lock
-  is held until its push has ended. The lock file reads `<run pid> <holder
-  pid> <start epoch>`, and a fourth field `drain` meanwhile. No `ps` and no process-group walk: on a host without `pgrep` a
-  stopped run says it could not reap, and its lock is held until its push
-  ends. Inside `pr_push_hold` git's auto-maintenance runs in the foreground
-  (`gc.autoDetach`, `maintenance.autoDetach` off), so a `git gc --auto` a
-  push's fetch starts is part of that push rather than a PID-1 orphan holding
-  its lock. With `detach` the holder leaves the run's worktree detached once
-  the push has ended, a SIGKILLed run's too. Only the lock exits 75; a step
-  that does is reported as a stop and exits 1. `pr_bounded` runs a self-test
-  (its own, `update_pr.sh`'s, `cloud_relay.sh`'s) as a session of its own under
-  `PR_SELFTEST_SECONDS` (default 1200), and ends that whole session on exit,
-  at the bound (exit 124, a `BOUND:` line) or once its supervisor is gone;
-  `pr_own_group` starts a command as a process group's leader. When: never by hand; `--self-test` drives both scripts end to end
-  in a scratch repository, offline, each refusal arm beside a mutant that
-  deletes its predicate line (`# mut:<name>`) and must fail the arm, plus
-  null controls that pass every check. Refusal: its self-test's tally.
-- `pr_cap.py` — the soft cap, on dispatch since 2026-10-20: `dispatch-gate`
-  counts the roster groups whose `resume.stage` is `in-progress` through
-  `roster_lib` at the roster ref, prints their ids and refuses at or over
-  `HPO_WIP_CAP` (default 6) unless `--over-cap "<reason>"` is given; `info`
-  prints the open count for `open_pr.sh` and never refuses. A group that also
-  has an open pull request is one group. Imported by `orchestrator_tick.py`
-  for its `WIP` and coordinator level lines. A bot is a GitHub-flagged bot
-  other than `app/hpo-author`, which authors every seat PR. When: before
-  dispatching a new group, and `open_pr.sh` before it opens (information
-  only); the tick every pass. Refusal: at or over the cap without
-  `--over-cap <reason>`; an empty reason; an invalid `HPO_WIP_CAP`; a roster
-  it cannot read (never a clean zero); an open list gh cannot read, that is
-  not JSON, or that reaches gh's 200 limit (reported, not gated).
-- `proof_watch.py` — watches one named check-run at one pinned head of one
-  pull request and, once it completes `success` beside green required contexts
-  and a valid merge verdict at that exact head, merges through `merge_pr.sh`.
-  When: a long validating run whose green-to-merge window would otherwise sit
-  unattended (the 4.5 h proof misread as failed, P8). Refusals: a head that
-  moved off the pin, a named check that completed not-success, an exceeded
-  `--budget`, a red required context (the ruleset's list, read through
-  `merge_train.required`), an unmergeable pull request and a head
-  `app_approve --dry-run` does not verdict — each aborts with a logged report
-  and no merge; one instance per pinned head (flock), and `--dry-run` passes
-  every guard and touches nothing. `--mode owner` hands `merge_pr.sh` its
-  `--mandate <comment-id>`, and refuses at launch without one.
-- `ci_probe.py` — the writes a CI-layout probe needs, each behind the same
-  guards: `push <ref> <sha>` (only `refs/heads/ci-probe/*`), `dispatch`,
-  `rerun-job`, `cancel`, `label`, `retarget`, `close`, and the owner-only
-  `review --approve --sha` and `dismiss-review`. When: the P2 probe fan-out
-  (`plans/ci-layout`). Refusals: a ref outside `ci-probe/`, a missing or other
-  `--repo`, `/rate_limit` below 20 % remaining (or unreadable), a token that is
-  not `tvofi` on a review, a host path in a ref, message or log line, and a
-  commit the push publishes first whose message carries a tool's attribution
-  or whose identity names a machine (`ref_privacy.published`). One log
-  line per write (`--log`); `--dry-run` writes nothing. Nothing polls (the 60 s
-  floor holds vacuously). `--self-test` runs over fakes and a throwaway bare
-  remote, including the namespace control: a planted `ci-probe/x` leaves
-  `cloud_relay.sh`'s probe arm and `bus.sh orphans` unchanged, a planted
-  `probe/foo` is OWED. `prune_refs.py` deletes a `ci-probe/*` ref, untagged,
-  unless an open pull request has it as head.
-- `prune_refs.py` — reconciles the remote branch refs down to main plus a few
-  development branches at programme closure, archive-as-tags first. When: the
-  R9-CLOSURE-BRANCHES step 4 (prune by rule), and any future round's closure.
-  Four rules -- keep `main` and any ref whose pull request is OPEN; delete a
-  ref already merged into main, and an unmerged `handoff/*` ref whose pull
-  request merged (a same-named PR, or the branch of a roster group the roster
-  records `done`); enumerate the residue (no PR, or a closed-unmerged one) for
-  an individual disposition, archived-and-deleted by default. Refusals: a plan
-  that would act on `main`, and any `verdict/*` deletion while `--verdicts-drained`
-  is unset (the bus watcher reads those refs). Every tag is created before any
-  deletion, and `--archive-scope none` deletes nothing, so no tip is ever
-  dropped unarchived; `--dry-run` (the default) prints the plan and writes
-  nothing. `--self-test` drives the classifier, the planner, the precedence and
-  the ordering offline (22 checks).
-- `pulse.py` — says whether the programme is still being driven, from origin
-  alone: per consumer, an input an off-host producer already delivered that
-  the consumer's footprint has not answered within a bound — a handoff with no
-  pull request and nothing opened since it arrived (`bus.sh orphans`, invoked),
-  a verdict still at its open pull request's head, a main move the round's
-  state ref has not followed. When: from where the orchestrator's host is not
-  (a scheduled cloud probe seat), and first at any takeover, before the hand
-  survey (R10-RCA-ORCH-CONTINUITY). Refusal: an input it could not read is
-  `UNREADABLE`, exit 2, never ok; a stamp ahead of the clock is never aged.
-  `--dump` keeps the snapshot a `STOPPED` line came from; `--snapshot`
-  re-judges it. A `STOPPED` line names the standing seat its input waits on,
-  and `--seat-queue SEAT=FILE[:MIN]` judges a standing seat on its session
-  queue file (`<epoch> <text>` lines): STOPPED past the seat's cadence, ok
-  when empty, `UNREADABLE` when missing.
-- `queue_pre_flight.py` — runs a merge queue's admission reads offline, before
-  the train launches: per entry PASS, PARK (the train's own Stop wording — a
-  carry that fails, a missing or stale delivery row, a GITHUB_TOKEN bot tip, a
-  branch another worktree holds, a policy or budget head without the owner's
-  in-force mandate) or FAIL (a verdict that is not 40-hex, a closed pull
-  request). When: before any `merge_train.py run`/`batch` — an admission-time
-  refusal parks the entry here instead of stopping a live queue mid-run.
-  Refusal: exit 1 unless every entry passed; the checks are the train's own
-  methods (`bot_tip`, `policy_gate`, `app_approve.sh --carry`), never new ones.
-  `merge_train.py --pre-flight` runs it inside the train, passing the two
-  shapes the train now cures itself: a bot tip, and under `--free-holders` a
-  holder `Train.freeable` clears.
-- `record_row.py` — the record-autofix generator: enumerates merged PRs from
-  the REST API, plans the delivery rows the tree still lacks, applies them
-  behind a guarded write set (`dev/programme/delivery/<N>.md` only). When: the periodic
-  `record` beat. Refusal: any path outside `dev/programme/delivery/<N>.md` — the plan
-  table and HANDOVER are a seat's dispositions, never this generator's — and
-  a window it cannot attribute refuses rather than reports empty. Every API
-  read is `_api`'s, under `gh_read.py`'s read rule.
-  `--automerge-check --pr N [--head SHA] [--hold] [--require-green]` is the
-  guard CI approves and merges a record pull request behind (exit 3: guard
-  passes, a required check has not yet); `--replay-moved` replays one
-  older than the row directory's move. Refusal: any file but a new one-line
-  row at its canonical path that the API's facts re-generate, or an author
-  other than the hpo-author App.
-- `ref_privacy.py` — the one owner of what a push may say about the host
-  (#2310): `slug <path>` names a local path for a ref (`<root>-<rest>` under
-  a named root, else `ext-<leaf>-<hash>`); `guard --ref R [--message M]
-  [--commits REV [--over BASE] -C DIR]` refuses a ref name or commit message carrying the
-  home directory, an account name, the uid, a session temp root or a host
-  path, or a message carrying a tool's attribution (exit 3, the class named,
-  the text not echoed); `--commits` reads what the push publishes first,
-  `--over BASE` every commit REV adds over BASE; `--check` refuses a
-  tracked file with a push site its `PUSHERS` registry does not name, and a
-  `guarded` entry that calls no guard. When: before every push an instrument
-  composes; a new pusher registers in `PUSHERS` in the same diff. Refusal: a
-  push that would publish the host never runs.
-- `remerge_main.sh` — merges origin/main into an open PR (claimnotes merge
-  driver), drops inherited claims, pushes as the App with `app_push.sh
-  --recarry`, which prefixes ## Head with what happened and skips prepr only
-  on a clean 2-parent merge of the live head and main under the live body.
-  When: main moved under an open PR. Refusal: a conflict is not
-  auto-resolved — it stops loudly instead.
-- `run_twins.py` — counts a workflow's cancelled `pull_request` runs that
-  sat beside a same-SHA sibling (two events at one head, not a
-  supersession), from cached `/actions/workflows/<file>/runs` pages or
-  `--fetch`. When: judging a workflow's `concurrency:` block (R9-CI-2a).
-  Refusal: none; it enumerates.
-- `resume_doc.py` — generates the resume markdown from the roster plus live
-  PR state, under a byte budget. When: a state beat; regenerate rather than
-  hand-edit the resume. Refusal: over-budget output refuses with `--out`
-  unwritten — archive before regenerating.
-- `review_strength.py` — real-catch blocks per reviewed PR, incidence and
-  first-pass share from the `review/*` bus and its `archive/review/*` tags,
-  over git only (no REST), per window and per stratum: reviewer kind (a
-  probe-ref return is cloud), class, the class the wave routes (`route`, the
-  vocabulary read from web-fix-wave.js's VERDICT_CLASSES, never copied),
-  re-review after a merge verdict, and with `--roster` the PR's origin, fixer
-  model, size and product, taken `--as-of` the latest window's until (the
-  verdicts, `--tree` and the roster ref cut there). `--guardrail` prints the
-  review-strength guardrail's arms, report-only: incidence of the last 30
-  PRs and of each seat family's last 20 against P0 = 0.28 with REAL widened
-  by REAL_EXTRA, and the blocked words neither real nor taught. When: a flow guardrail
-  or a D13 round reads review strength; `dev/audit/rounds/round10/D13/yield-probe.md`
-  is its first use. Refusal: an out-of-grammar subject is its own row,
-  never a verdict.
-- `roster_edit.py` — the safe roster edit: every op loads the whole roster,
-  validates, and dumps with the file's own formatting; ops `set-stage`
-  (with `--at-sha`), `wire-issue [--field fixes|issues]`, `unwire-issue <group> <N> [--field
-  fixes|issues]` (refuses an absent N), `append-group`, `edit-brief`,
-  `append-carry`, `drop-carry <group> <index|--match TEXT>` (0-based index,
-  or the one entry containing TEXT; the last drop leaves `"carry": []`, the
-  key kept),
-  `set-after <group> <G1,G2,...|->` (replaces the after-edges whole, `-` for
-  none), and `set-resume <group> --field
-  <stage|commit|branch|last_step|next_step|note>` for the resume free-text
-  fields a session restarts from. When: any roster change — never a string
-  splice, which unbalanced the file twice. Refusals: the lint gate (run from
-  a fresh origin/main checkout — a stale `--lint-cwd` is refused itself), an
-  unknown group, a duplicate issue or carry, for `set-after` an unknown
-  after-group, a self-edge, a repeated edge and a cycle in the resulting
-  after-graph, for `drop-carry` an absent carry, an out-of-range index, no
-  match and an ambiguous match, and for `set-resume` an empty
-  value on the non-null fields (`stage`, `branch`) or a non-sha on
-  `--field commit`; an empty value on a nullable field clears it to null.
-  `--roster-ref` defaults to `main` and `--branch` to the round's
-  `handoff/audit-r<N>-roster`, never main itself; `--roster-path` overrides
-  the newest roster.
-  A no-op edit reproduces the roster's bytes exactly and reports `no change`
-  instead of an empty commit — the round-trip the self-test pins, because a
-  dump that misses the file's formatting rewrites all 7503 lines on any edit.
-  The edit is committed in a detached worktree and pushed as
-  `<sha>:refs/heads/<branch>`, never by a local branch name another run of
-  the same `--checkout` can reset. A push lost to a rival re-applies the op
-  on the new tip, at most `PUSH_ATTEMPTS` times, then refuses with rc 2; a
-  `--worktree` whose HEAD is on no origin ref is not reused.
-- `roster_lib.py` — shared roster parsing and wave logic (depth, critical
-  path, open groups, the branch-to-group lookup), and the one owner of WHICH
-  roster: `roster_path` picks the newest `dev/programme/rosters/wave-r<N>-groups.json`
-  (at a ref or on the checkout) unless `--roster-path` names one; and of
-  WHICH REF: `default_roster_ref` answers the round's roster branch
-  `origin/handoff/audit-r<N>-roster` when the clone has it, else
-  `origin/main`, with a note whenever that answer may be stale. Import it;
-  `--self-test` is its only CLI. When: any tool that reads the roster — one
-  schema reader, not several. Refusal: no roster where one was asked for
-  raises `RosterNotFound`, never a fallback to another round's.
-- `roster_sync.py` — derives the factual half of a roster group's `resume`
-  from pull-request state: a merged pull request on the group's branch makes
-  it `done` at the merge commit (and routes the body's `Carry: <GROUP>` items
-  to the destination's `carry`), an open one makes it `in-progress` with
-  `resume.pr`. Branch matching is the topic rule its docstring states; a head
-  two topics match is the longer one's. It prints `RECORD-INVALID <group>` for
-  a `resume.commit` naming no commit or several, or a done group's off
-  `origin/main` -- a finding, never a refusal. When:
-  every `state_docs.py beat --apply` pass runs it; run it alone to see what a
-  pass would write. Dry run by default; `--apply` writes through
-  `roster_edit.write_roster()`, the one write path, lint gate and push-race retry. Refusals: an
-  unreadable pull-request read (never "no mismatches"), a `Carry:` to a done
-  group, `--apply` with `--roster-file`; a human disposition (`deferred`,
-  `refused` and every stage outside `DERIVABLE_STAGES`) is never rewritten,
-  and no pull request is no evidence. `--self-test` drives it offline over a
-  recorded `--pr-state`; `r10_roster_sync_mutants.py` plants its predicates.
-- `roster_queue.py` — the standing roster seat's queue runner: `run FIRST LAST`
-  applies each queue line (`<op> <group> [arg] [--flag value]`, so `drop-carry G --match TEXT` works) through `roster_edit.py --push`,
-  linting from a clone it owns and detaches at `origin/main` before every
-  attempt (up to four, when main moved or a clean-lint push lost a race), and
-  never moving the orchestrator's checkout. `readback SHA GROUP FILE` prints
-  whether the roster at SHA holds the file's text as exactly one carry entry
-  (exit 1 when none). When: the roster seat works a queue file; run it alone
-  to replay a range. Refusal: a refused op is reported as `refused rc=N`, never
-  forced; `append-carry @file` reports FAILED when the read-back cannot find the
-  text. `--self-test` drives it offline over a stub editor and a scratch repo.
-- `seat_venv.sh` — builds the seat interpreter venvs reproducibly and installs
-  the `shims/`. When: a new workstation or cloud seat; CI features are
-  container-only on the Mac (no local venv for the Accelerate wheels).
-  Builds `venv-ci` (CI's `fast` pins) and `venv-ha` (the typing lock,
-  hash-pinned, `--no-deps`, cloud-setup.sh's pins call). `--check` reports
-  both. `--self-test` drives the recipe and the shim export.
-- `selftest_wiring.py` — refuses a self-testing file under `tools/` (widened
-  from `tools/audit/seat/` by #2444's forward-carry) that no workflow `run:`
-  line, comments removed, invokes with its self-test (`--check`,
-  `--self-test`). Runs first among the seat steps of
-  `instrument-self-tests`. When: adding a tool with a `--self-test`; add its
-  step in the same pull request. Refusal: each unwired file by path; a
-  mention in a comment, a step name or a `--check` call does not wire it.
-- `tick_loop.sh` — the tick's driver loop (tvofi approved, 2026-10-18): each
-  pass runs `cloud_relay.sh pass --confirm` (a relayed verdict posts with no
-  hand step) when the tree carries it (#2419; skipped
-  and said so before), then `orchestrator_tick.py` with the given args,
-  writing the board whole to `--out` (default `$HPO_STATE_DIR/tick.txt`) and
-  one `TICK-PASS <utc> relay=<ok|rc=N|running|absent> tick=<rc>` line to
-  stdout. The relay runs detached under the flock `<out>.relay.lock`, waited
-  for at most `HPO_TICK_RELAY_WAIT` s (default 30): one still in flight is
-  left running, never killed, reported `relay=running`, and no second starts
-  while it holds the lock, so a long `update_pr.sh` push never holds the
-  board; the next pass reaps it, printing its output and a `TICK-RELAY` line.
-  When: run detached (`daemonize.py`) in place of a seat looping the tick;
-  `--once` makes one pass, `--interval` defaults to 300 s. Refusal: a
-  non-numeric `--interval` or an unknown option; a failing relay pass or tick
-  is reported and the loop goes on. `--self-test` drives it over stubs.
-  Each pass then calls `heartbeat.sh --once` (the andon, below), bounded at
-  60 s; `HPO_TICK_HEARTBEAT` replaces it.
-- `heartbeat.sh` — the andon (Lean flow study K8, R10-FLOW-ANDON; cost-tested
-  by R10-RCA-ORCH-CONTINUITY): `--once --message TEXT` force-pushes
-  `heartbeat/orchestrator` as one parentless empty-tree commit whose message is
-  the pass line `TICK-PASS <utc> relay=<..> tick=<rc>`, over the seat's own
-  credential (`-f --no-verify`, the message through `ref_privacy.py guard`);
-  a refused or failed push prints `HEARTBEAT NOT PUSHED: <reason>`, exits 1
-  and never stops the loop. `--watch [--max-age 1200]` is the off-host
-  watcher's command: it fetches the ref and exits 1 with `HEARTBEAT STALE: ..`
-  when the committer date is older than the limit or the ref is absent. When:
-  `tick_loop.sh` calls `--once` every pass; the owner schedules a cloud task
-  every 15 min running `--watch` that notifies the owner on exit 1 (the
-  schedule is owner-side, not in the tree). A standalone job script, so
-  R10-ORCH-MACHINERY registers it as the beat's heartbeat job and retires the
-  call from `tick_loop.sh`. Refusal: unknown option, a non-numeric
-  `--max-age`. `--self-test` drives both modes over a bare-repo fixture, a
-  stale ref and a fresh one.
-- `train.sh` — one invocation shape for `merge_train.py batch`: the seat
-  venv first on PATH — an absent venv refuses (naming `seat_venv.sh` to
-  build it), it never falls back to ambient python, which on 3.11 refuses
-  main's own nested-quote f-strings under `no-copies` — the child python
-  unbuffered (`-u`, so a detached caller's log shows stops and SKIP/OVERLAP
-  lines in real time), a pidfile refusing a second live train on the same
-  state dir, log and exit code under the state dir (`train.log`, `rc`), and
-  `--skip-bad`/`--overlap`/`--approval-carry`/`--bot-prs`/`--pre-flight`/
-  `--free-holders`/`--main-moved-tries N` passed straight through, each only
-  when given (a `0` default once passed `--skip-bad --overlap` on every
-  launch), and the child run from the repository root when `--checkout` is
-  absent (it once resolved to `tools/`). Foreground: the caller
-  detaches and owns the schedule. When: every merge queue — the per-session
-  scratch drivers this replaces duplicated the invocation, and one session's
-  copy ran prepr under the wrong interpreter and refused a clean branch.
-  Refusal: a live pidfile (take over only by removing it after checking the
-  pid is dead). `--self-test` drives the five refusals and the child argv
-  shape offline (missing required arg, live pidfile, unknown argument, the
-  `--ignore-red` argv shape, the absent-venv refusal), the child's cwd on a
-  launch without `--checkout`, and a bare launch's argv carrying no flag.
-  `train.sh add <pr> <verdict> --repo R --state-dir D [--verdict-comment ID]
-  [flags]` loads one pull request into that state dir's live train (its next
-  batch) or, with none live, starts one with those flags. When: whenever a
-  merge verdict is confirmed. Refusal: `ADD REFUSED #<pr> <rule>: <why>` from
-  `Train.admit_add` (shape, open, base, carry, row, budget-raise, policy),
-  and `one-train` beside a train.sh still closing; a pull request already
-  queued is `ALREADY`, rc 0. One fcntl lock (`queue.lock`) orders every add
-  against the train's drains and its close; never a second train.
-- `state_docs.py` — one call regenerates the four state docs
-  (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`,
-  `handover_prompt.py`), commits exactly
-  their outputs to the orphan ref `handoff/audit-r<N>-plan` at
-  `handoff/round<N>/state/`, N the roster's round, and mirrors them to
-  `--mirror`. The flow board publishes beside the plan table, so a beat
-  pass carries the throughput figures with the plan they explain. When: every state
-  beat — it replaces the five hand commands (worktree, copy, commit, push,
-  mirror) and runs the generators instead of copying their logic. Dry run by
-  default: without `--push` nothing remote is written. Refusals: any path
-  outside the four state docs (the write set is checked before a commit
-  exists to push; every other path at the ref — a round's evidence — is
-  carried untouched), a first commit that would not be exactly the four
-  files, and an already-current tip, which is reported and left alone. The
-  commit is plumbing over a temp index, so the calling checkout's index is
-  never touched.
-  `state_docs.py beat` is the same instrument on a loop, and it lives here
-  rather than in a session's scratch for decision 0013's reason — an
-  instrument the programme runs belongs where a later session can test it. A
-  pass reads `--watch-ref` and the roster ref at origin (O17: a roster edit
-  moves the state docs as a merge does); when either has moved it refreshes
-  the roster ref (so resume fields other seats wrote are visible),
-  regenerates and pushes, and when neither has it writes nothing at all.
-  With no `--roster-ref` the roster ref is `roster_lib.default_roster_ref`'s. When:
-  continuously beside a merge train, since it takes no lock and cancels
-  nothing — the state docs are regenerated rather than rebuilt at session
-  end. Refusal, and the one that saves you: the tip is recorded ONLY on a
-  regeneration that returned 0, so a push the remote rejected is retried on
-  the next pass instead of silently dropping that merge from the record.
-  `--apply` runs `roster_sync.py --apply` at the start of each pass, before
-  the memo check, since a pull request can open or merge without moving a ref
-  the beat watches; without it the beat derives nothing.
-  `--once` is one pass and returns that pass's code; without `--tip-file` a
-  `--once` caller regenerates every time, so give it one to keep the loop's
-  memo on disk. `--self-test` drives all three arms offline.
-- `sweep_driver.py` — the probe PR's sweep, where `workflow_run` never fires
-  (`gate-sweep.yml` runs only from the default branch): every poll (60 s floor,
-  tvofi 2026-10-19) it lists the PR's `ci.yml` runs at the live head, reads each
-  run attempt not yet swept (N5-1) and starts `python3 -I <tree>/tools/ci/gate.py
-  --sweep --run <id>` as a concurrent child for it: attempt 1 only under
-  `--nochain`, every attempt under `--chain`. It logs one line per sweep,
-  `superseded=1` for an attempt first seen already replaced, reads `/rate_limit`
-  before each poll and backs off below 20 % remaining or on a 403 (A1 item 5),
-  and exits after 900 s with every run completed and nothing new. When: a seat
-  drives a probe PR through the sweep (M-6, M-2, the combined control). It only
-  reads (`gh api` GET); the child's re-runs are the only writes. Refusal: a
-  `--poll` under 60. `--self-test` runs it over a fake `gh` and clock.
-- `sweep_render.py` — renders the orchestrator sweep from
-  `sweep_template.md` and a session's JSON overlay (stdout or `--out`). The
-  template's `## Placeholders` table is the one registry of names. When: a
-  session or round sets up its recurring sweep -- render it, never hand-copy
-  the last session's prompt; the overlay stays out of the tree. Refusal: an
-  unfilled, empty or non-scalar value, an undeclared placeholder or overlay
-  key, a declared name the sweep never uses, a cited `tools/`, `tests/`,
-  `dev/` or `.github/` path that is not in the tree, and a home directory
-  (`ref_privacy.py`'s `HOME_DIR`) in the rendered text that no overlay value
-  supplied -- each exits 1 and writes nothing. `--self-test` renders the
-  tracked template and drives every refusal beside its null control.
-- `sweep_template.md` — the orchestrator's recurring sweep, steps in order,
-  each naming the instrument it runs by tree path and the rule file
-  (`orchestrator.md`, `nudge.md`, `CLAUDE.md`) it carries out; a usage guide
-  that restates no policy. When: read through `sweep_render.py`. Refusal: none
-  of its own -- the renderer's.
-- `tmp_paths.py` — refuses a tracked script, workflow or decision record that
-  depends on a temp or machine path (`--check`, `--self-test`). When: after
-  touching anything under `tools/`, `tests/`, `.claude/`, or before pushing.
-  Refusal: every match on its own line — a `/tmp` state name, a `$TMPDIR`
-  with a fixed name, a home path, an instrument run from `~/`; the 2026-10-03
-  temp cleanup deleted three tracked tools' state and one decision's design
-  note. It also refuses a temp, home or seat-directory path on a
-  `tests/mutation_ledger/` line the diff adds (a triage citing a probe no
-  other seat can run); main's stock is not charged.
-- `update_pr.sh` — brings an open PR branch to its head + a code SHA (merge) +
-  origin/main (merge), adds the PR's own delivery row when the head lacks
-  it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as
-  `hpo-author`. With code sha `-` it asks `app_push.sh --row-only`, so a push
-  that only adds the row takes the body contract instead of the full prepr,
-  and prints app_push's `ROW-ONLY:` line naming which ran and why.
-  When: updating a PR after review prep or a main merge.
-  Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
-  silently; no open PR at the branch stops before any push. Up front, each an
-  `update_pr: REFUSE:` line (`pr_args.sh`): fewer than three arguments; a
-  code sha other than `-` that is not 40-hex, names no commit, or is not an
-  ancestor of `origin/handoff/<topic>` (the topic `HANDOFF_TOPIC`, else the
-  branch less `fix/`, then less `-pr`), naming a `handoff-body/<topic>` tip as
-  the BODY sha; a missing `handoff/<topic>`; no body file. The body is a file
-  here, so a missing body ref is no refusal. It detaches another instrument's
-  clean worktree on the branch only when origin has that worktree's HEAD; one
-  holding commits origin lacks (a PR's unpushed row) is refused, naming it.
-  Any later stop prints `update_pr: STOPPED: ...`, and a refused push names its log.
-  Its lock's holder leaves its own worktree detached once its push has
-  ended, a SIGKILLed run's too, so no worktree of it holds the branch.
-- `wt_sync.sh` — snapshots every worktree whose state is not already on
-  origin (unpushed commits, uncommitted or untracked files) to
-  `origin/wip-sync/<slug>`, plus the orchestrator scratch. The slug is
-  `ref_privacy.py slug`'s, never a host path (#2310). When: loop it
-  detached so a crashed seat is recoverable from its branch. Refusal: it
-  never touches the worktree or its index — a snapshot, not a save; a
-  worktree whose snapshot would name the host is skipped with the guard's
-  reason.
-- `shims/seat-python`, `shims/seat-python3` — the seat interpreter: execs the
-  venv-ci `seat_venv.sh` builds, under `$HPO_STATE_DIR` first and the default
-  state root `~/.local/state/hpo` second, and refuses naming that build command
-  when neither holds one; exports `HPO_TYPING_PYTHON` to venv-ha/bin/python
-  under the same two roots, only when that interpreter exists and the variable
-  is unset. When: a seat's PATH needs a pinned interpreter, and the scoped gate
-  should check the mypy census.
+- [`features_block.py`](instruments/features_block.py.md) — runs one block of `tests/features.py`
+- [`body_push.sh`](instruments/body_push.sh.md) — publishes a handoff's BODY.md on the orphan ref `handoff-body/<topic>` (plus RESUME.md), parentless first commit, fast-forwards after
+- [`body_patch.sh`](instruments/body_patch.sh.md) — repairs an open pull request's BODY without moving its head
+- [`autofix_statuses.sh`](instruments/autofix_statuses.sh.md) — re-derives what `mutation-autofix` and `closures-autofix` answered on recent pull-request runs
+- [`bus.sh`](instruments/bus.sh.md) — git refs as the programme's message bus
+- [`review_packet.py`](instruments/review_packet.py.md) — the fix reviewer's packet at the frozen head
+- [`ci-watch.sh`](instruments/ci-watch.sh.md) — watches open PRs' check states and alerts only on NEW states (per-PR signature file)
+- [`ci_critpath.py`](instruments/ci_critpath.py.md) — one workflow run's critical path from its job and step timestamps (each job's queue, duration and longest step), its `needs:` read from the run's own head
+- [`cloud-setup.sh`](instruments/cloud-setup.sh.md) — the cloud seat environment's setup script (interpreter, CI-run pinning)
+- [`cloud_dispatch.py`](instruments/cloud_dispatch.py.md) — renders the whole cloud-runner trigger payload
+- [`cloud_relay.sh`](instruments/cloud_relay.sh.md) — the orchestrator's half of a cloud reviewer's return
+- [`codeql-triage-poll.sh`](instruments/codeql-triage-poll.sh.md) — polls until GitHub attaches the #1769 evidence-alerts, dismisses them, re-runs CodeQL
+- [`daemonize.py`](instruments/daemonize.py.md) — detaches one long-running instrument from the session that started it
+- [`delivery_row.sh`](instruments/delivery_row.sh.md) — the one seat-script writer of a PR's own `**open**` row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
+- [`failure_logs.sh`](instruments/failure_logs.sh.md) — answers why a PR's newest red at its live head is red
+- [`flow_metrics.py`](instruments/flow_metrics.py.md) — a round's flow over one window
+- [`gh_read.py`](instruments/gh_read.py.md) — the read rule every seat instrument's GitHub READS are under
+- [`handoff_push.sh`](instruments/handoff_push.sh.md) — the legacy one-shot
+- [`handover_prompt.py`](instruments/handover_prompt.py.md) — generates the next-session prompt from the roster (and optionally a resume doc)
+- [`merge_pr.sh`](instruments/merge_pr.sh.md) — merges one PR after its evidence checks
+- [`merge_train.py`](instruments/merge_train.py.md) — lands a queue of verdicted PRs one at a time
+- [`ledger.py`](instruments/ledger.py.md) — the obligations ledger
+- [`moved_paths.py`](instruments/moved_paths.py.md) — lists every line in the given files that names a path `tests/layout.json` marks moved
+- [`offline_spy.py`](instruments/offline_spy.py.md) — runs a seat instrument's `--self-test` under a throwaway HOME and counts what it reaches outside
+- [`open_pr.sh`](instruments/open_pr.sh.md) — opens a draft PR from `handoff/<topic>` as `hpo-author`, adds its own delivery row, re-pushes, prints N and the head
+- [`orchestrator_tick.py`](instruments/orchestrator_tick.py.md) — the heartbeat's dispatch list
+- [`plan_audit.py`](instruments/plan_audit.py.md) — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the `audit-plan` workflow
+- [`plan_page.py`](instruments/plan_page.py.md) — renders the round's plan page (HTML) from `tools/plan/replan.py`'s plan.json, the roster through `roster_lib`
+- [`plan_table.py`](instruments/plan_table.py.md) — renders the plan artifact from a wave-groups roster
+- [`policy_reread_check.py`](instruments/policy_reread_check.py.md) — says whether a session owes a policy re-read
+- [`pr_args.sh`](instruments/pr_args.sh.md) — sourced by `open_pr.sh` and `update_pr.sh`
+- [`pr_cap.py`](instruments/pr_cap.py.md) — the soft cap, on dispatch since 2026-10-20
+- [`proof_watch.py`](instruments/proof_watch.py.md) — watches one named check-run at one pinned head of one pull request and, once it completes `success` beside green required contexts and a valid merge verdict at that exact head, merges through `merge_pr.sh`
+- [`ci_probe.py`](instruments/ci_probe.py.md) — the writes a CI-layout probe needs
+- [`prune_refs.py`](instruments/prune_refs.py.md) — reconciles the remote branch refs down to main plus a few development branches at programme closure, archive-as-tags first
+- [`pulse.py`](instruments/pulse.py.md) — says whether the programme is still being driven
+- [`queue_pre_flight.py`](instruments/queue_pre_flight.py.md) — runs a merge queue's admission reads offline, before the train launches
+- [`record_row.py`](instruments/record_row.py.md) — the record-autofix generator
+- [`ref_privacy.py`](instruments/ref_privacy.py.md) — the one owner of what a push may say about the host (#2310)
+- [`remerge_main.sh`](instruments/remerge_main.sh.md) — merges origin/main into an open PR (claimnotes merge driver), drops inherited claims, pushes as the App with `app_push.sh --recarry`
+- [`run_twins.py`](instruments/run_twins.py.md) — counts a workflow's cancelled `pull_request` runs that sat beside a same-SHA sibling (two events at one head, not a supersession)
+- [`resume_doc.py`](instruments/resume_doc.py.md) — generates the resume markdown from the roster plus live PR state, under a byte budget
+- [`review_strength.py`](instruments/review_strength.py.md) — real-catch blocks per reviewed PR, incidence and first-pass share from the `review/*` bus and its `archive/review/*` tags, over git only (no REST), per window and per stratum
+- [`roster_edit.py`](instruments/roster_edit.py.md) — the safe roster edit
+- [`roster_lib.py`](instruments/roster_lib.py.md) — shared roster parsing and wave logic (depth, critical path, open groups, the branch-to-group lookup)
+- [`roster_sync.py`](instruments/roster_sync.py.md) — derives the factual half of a roster group's `resume` from pull-request state
+- [`roster_queue.py`](instruments/roster_queue.py.md) — the standing roster seat's queue runner
+- [`seat_venv.sh`](instruments/seat_venv.sh.md) — builds the seat interpreter venvs reproducibly and installs the `shims/`
+- [`selftest_wiring.py`](instruments/selftest_wiring.py.md) — refuses a self-testing file under `tools/` (widened from `tools/audit/seat/` by #2444's forward-carry) that no workflow `run:` line, comments removed, invokes with its self-test (`--check`, `--self-test`)
+- [`tick_loop.sh`](instruments/tick_loop.sh.md) — the tick's driver loop (tvofi approved, 2026-10-18)
+- [`heartbeat.sh`](instruments/heartbeat.sh.md) — the andon
+- [`train.sh`](instruments/train.sh.md) — one invocation shape for `merge_train.py batch`
+- [`state_docs.py`](instruments/state_docs.py.md) — one call regenerates the four state docs (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`, `handover_prompt.py`), commits exactly their outputs to the orphan ref `handoff/audit-r<N>-plan` at `handoff/round<N>/state/`, N the roster's round
+- [`sweep_driver.py`](instruments/sweep_driver.py.md) — the probe PR's sweep, where `workflow_run` never fires (`gate-sweep.yml` runs only from the default branch)
+- [`sweep_render.py`](instruments/sweep_render.py.md) — renders the orchestrator sweep from `sweep_template.md` and a session's JSON overlay (stdout or `--out`)
+- [`sweep_template.md`](instruments/sweep_template.md.md) — the orchestrator's recurring sweep, steps in order
+- [`tmp_paths.py`](instruments/tmp_paths.py.md) — refuses a tracked script, workflow or decision record that depends on a temp or machine path (`--check`, `--self-test`)
+- [`update_pr.sh`](instruments/update_pr.sh.md) — brings an open PR branch to its head + a code SHA (merge) + origin/main (merge), adds the PR's own delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as `hpo-author`
+- [`wt_sync.sh`](instruments/wt_sync.sh.md) — snapshots every worktree whose state is not already on origin (unpushed commits, uncommitted or untracked files) to `origin/wip-sync/<slug>`
+- [`shims/seat-python`, `shims/seat-python3`](instruments/shims_seat-python.md) — the seat interpreter
diff --git a/tools/audit/seat/instruments/app_approve.sh.md b/tools/audit/seat/instruments/app_approve.sh.md
new file mode 100644
index 000000000..f974f5dc0
--- /dev/null
+++ b/tools/audit/seat/instruments/app_approve.sh.md
@@ -0,0 +1,11 @@
+# `app_approve.sh`
+
+- `app_approve.sh` — approves a pull request as the `hpo-approver` App at one
+  exact head SHA, only on a `merge` verdict for that SHA from an allowlisted
+  account (`--carry` re-approves a carried verdict). When: landing a
+  non-code-owned verdicted PR whose head the reviewer measured. Refusal: a
+  head SHA that is not the PR's current head, or a verdict whose SHA or
+  account does not match — the approval names one tree or it does nothing.
+  Its GitHub reads -- the four `gh api` reads and curl's JWT read of the
+  App's installation -- are under `seat/gh_read.py`'s read rule; the token
+  mint and the review POST are never retried.
diff --git a/tools/audit/seat/instruments/app_comment.sh.md b/tools/audit/seat/instruments/app_comment.sh.md
new file mode 100644
index 000000000..6fd966d68
--- /dev/null
+++ b/tools/audit/seat/instruments/app_comment.sh.md
@@ -0,0 +1,6 @@
+# `app_comment.sh`
+
+- `app_comment.sh` — posts one fix-review verdict on a PR as `hpo-approver`
+  and reads the posted comment back byte-identical. When: a reviewer seat
+  delivers a verdict. Refusal: a read-back that differs from what it meant to
+  post, or a stale head — "posted" is never taken from the send's exit code.
diff --git a/tools/audit/seat/instruments/app_push.sh.md b/tools/audit/seat/instruments/app_push.sh.md
new file mode 100644
index 000000000..8d1151cc0
--- /dev/null
+++ b/tools/audit/seat/instruments/app_push.sh.md
@@ -0,0 +1,15 @@
+# `app_push.sh`
+
+- `app_push.sh` — pushes a branch and opens or re-bodies its pull request as
+  the `hpo-author` App, with the body's contract check before the push. When:
+  every handoff — pull requests are App-authored (decision 0011); `push.sh`
+  is the tvofi-identity predecessor and must not author PRs. Refusal: a body
+  failing the contract check never reaches the remote. `--row-only`
+  (`update_pr.sh`'s) replaces prepr with pr-contract's two body checks (the
+  contract, its red history read with prepr 7c's credential, and
+  `carry_audit.py check`) only when the head
+  is the live head plus one commit adding exactly that PR's own open row and
+  the body is the live one under one new `## Head` note; else prepr runs.
+  Every commit the PR adds over a freshly fetched `origin/main`, wherever it
+  was first published (a `ci-probe/*` or `handoff/*` ref included), is
+  judged by `ref_privacy.py guard --over` before anything is minted.
diff --git a/tools/audit/seat/instruments/approve_held_runs.sh.md b/tools/audit/seat/instruments/approve_held_runs.sh.md
new file mode 100644
index 000000000..e6ac46b46
--- /dev/null
+++ b/tools/audit/seat/instruments/approve_held_runs.sh.md
@@ -0,0 +1,7 @@
+# `approve_held_runs.sh`
+
+- `approve_held_runs.sh` — approves the workflow runs GitHub holds
+  `action_required` on a branch. When: after the App pushes, the `pull_request`
+  workflows it created are held because the pusher is an App; a green gate
+  never starts until these are approved. Refusal: `--dry-run` lists what would
+  be approved; a branch with no held runs is a no-op, not an error to retry.
diff --git a/tools/audit/seat/instruments/autofix_statuses.sh.md b/tools/audit/seat/instruments/autofix_statuses.sh.md
new file mode 100644
index 000000000..9d20119db
--- /dev/null
+++ b/tools/audit/seat/instruments/autofix_statuses.sh.md
@@ -0,0 +1,7 @@
+# `autofix_statuses.sh`
+
+- `autofix_statuses.sh` — re-derives what `mutation-autofix` and
+  `closures-autofix` answered on recent pull-request runs, from their job
+  logs, with the `closures` failure heading behind each closures skip. When:
+  judging whether the autofix chain repairs anything. Refusal: a log GitHub
+  no longer serves is counted beside the totals, never read as a status.
diff --git a/tools/audit/seat/instruments/body_patch.sh.md b/tools/audit/seat/instruments/body_patch.sh.md
new file mode 100644
index 000000000..1ce30865d
--- /dev/null
+++ b/tools/audit/seat/instruments/body_patch.sh.md
@@ -0,0 +1,16 @@
+# `body_patch.sh`
+
+- `body_patch.sh` — repairs an open pull request's BODY without moving its
+  head: `body_patch.sh [--dry-run] [--repo O/R] <pr> <expected-head-sha>
+  <body.md>`. Reads the live head, runs the body contract offline at it
+  (`policy_lint.mjs --pr-body` with pr-contract's arguments, then
+  `carry_audit.py check --body`), PATCHes as `hpo-author` through
+  `tools/pr/app_mint.sh` (the mint `app_push.sh` shares), reads the body back
+  and re-reads the head. When: a body `pr-contract` or `carry_audit` refuses
+  on a head that must not move (ruling R4; `update_pr.sh` merges main on every
+  run). Refusal: a live head other than the expected sha, before any mint or
+  write; a body the contract refuses is never sent; `--dry-run` prints the
+  PATCH request and signs nothing; a read-back that cannot be performed in
+  three tries refuses, never reports OK. The offline contract runs the
+  caller's checkout, so it can differ from pr-contract's (the script header
+  says how). One `--once` unit: its last line is `body_patch: OK|REFUSE ...`.
diff --git a/tools/audit/seat/instruments/body_push.sh.md b/tools/audit/seat/instruments/body_push.sh.md
new file mode 100644
index 000000000..8523c480a
--- /dev/null
+++ b/tools/audit/seat/instruments/body_push.sh.md
@@ -0,0 +1,13 @@
+# `body_push.sh`
+
+- `body_push.sh` — publishes a handoff's BODY.md on the orphan ref
+  `handoff-body/<topic>` (plus RESUME.md), parentless first commit,
+  fast-forwards after. When: every fixer handoff — the body must never enter
+  the code head's ancestry (`prepr.sh` step 1a refuses that). Refusal: a
+  head `tools/pr/ci_predict.py` predicts a closures or `fast` red on, or a
+  checkout with no predictor (R10-HANDOFF-PREPR-BOUNCE M2), is refused
+  before anything is pushed, with each arm's repair printed; a fetch that
+  half-failed leaves a parentless commit the push refuses as a
+  non-fast-forward — a rewrite is never forced through; the body commit it
+  wrote is read back through `ref_privacy.py guard --commits`, message and
+  identity, before the push.
diff --git a/tools/audit/seat/instruments/bus.sh.md b/tools/audit/seat/instruments/bus.sh.md
new file mode 100644
index 000000000..f18fa1213
--- /dev/null
+++ b/tools/audit/seat/instruments/bus.sh.md
@@ -0,0 +1,25 @@
+# `bus.sh`
+
+- `bus.sh` — git refs as the programme's message bus: seats publish verdicts
+  on refs, the orchestrator watches. When: a reviewer seat with no other
+  channel, or an orchestrator collecting several lanes' verdicts at once.
+  `orphans` discharges a handoff by name only when that `fix/<t>` or
+  `fix/<t>-pr` head carries the tip; a named head behind it is
+  `repair=update`.
+  With `HPO_BUS_TRAIN_STATE` set, each merge verdict it posts is added to
+  the merge train there (`merge_train.py add --auto`, one `BUS train-add`
+  line; the output in `train-add.log`); a refused add never fails the post.
+  `dispatch` is the worker registry's one writer (`$HPO_BUS_STATE/dispatched`,
+  `<pr> <head> <reviewer> <nonce> <utc> <model|->`): it closes
+  `reviewer-fire <pr> <head>` in the ledger (`$HPO_BUS_LEDGER`, else
+  `ledger.py`'s default log), `--nonce` re-records a relay-minted nonce for the
+  seat fired with it, and from a fourth round it needs the body's `## Re-cut`
+  note or `--past-three <reason>` (logged in `past-three`). `confirm` writes
+  the record's model as `bus-model:` on `verdict/<pr>`, which
+  `review_strength.py --guardrail` reads as a model arm; it refuses a replay of
+  a posted tree before it pushes. `dispatch` first renders the review packet
+  (`review_packet.py`) and names it as `review-packet:`. A REFUSED packet (the
+  head is unfit: rc 1, a named signal) refuses the dispatch and records
+  nothing; a packet this seat cannot RENDER (rc 3, `UNAVAILABLE`: no checkout,
+  no `gh`, no token, an unwritable path) dispatches anyway, names no packet,
+  and says why in `review-packet: unavailable -- <reason>`.
diff --git a/tools/audit/seat/instruments/check_scopes.py.md b/tools/audit/seat/instruments/check_scopes.py.md
new file mode 100644
index 000000000..c0fda5d1a
--- /dev/null
+++ b/tools/audit/seat/instruments/check_scopes.py.md
@@ -0,0 +1,7 @@
+# `check_scopes.py`
+
+- `check_scopes.py` — proves the finder scopes are disjoint and complete
+  within each dimension, from `scopes.json`. When: starting an audit round
+  (`audit-find` runs it in Prepare and refuses the round on failure) or
+  splitting one. Refusal: a cell owned twice, or owned by nobody — the
+  perturbed-scope `--self-test` is the null control.
diff --git a/tools/audit/seat/instruments/ci-watch.sh.md b/tools/audit/seat/instruments/ci-watch.sh.md
new file mode 100644
index 000000000..aa9be7268
--- /dev/null
+++ b/tools/audit/seat/instruments/ci-watch.sh.md
@@ -0,0 +1,13 @@
+# `ci-watch.sh`
+
+- `ci-watch.sh` — watches open PRs' check states and alerts only on NEW
+  states (per-PR signature file): reds, CONFLICTING/DIRTY, STALLED zero-runs,
+  and required contexts ABSENT at a settled head — a bot GITHUB_TOKEN push's
+  `pull_request` runs are held `action_required`, so until one is approved the
+  governance family does not report at such a head and it sits unmergeable
+  looking green (R9-RC-AUTOFIX-GOVERNANCE).
+  When: a long fix wave where red-on-main or a fresh failure must interrupt
+  work. Refusal: state already seen prints nothing — the exit-1 report is the
+  alert, not the log; an unreadable ruleset alerts BLIND once rather than
+  silently skipping the ABSENT arm. `--self-test` grades every arm offline on
+  the recorded defect shape; `CI_WATCH_ONCE=1` runs a single cycle.
diff --git a/tools/audit/seat/instruments/ci_critpath.py.md b/tools/audit/seat/instruments/ci_critpath.py.md
new file mode 100644
index 000000000..f89c21d1f
--- /dev/null
+++ b/tools/audit/seat/instruments/ci_critpath.py.md
@@ -0,0 +1,14 @@
+# `ci_critpath.py`
+
+- `ci_critpath.py` — one workflow run's critical path from its job and step
+  timestamps (each job's queue, duration and longest step), its `needs:` read
+  from the run's own head, and a counterfactual holding every queue and
+  duration fixed: `--drop-edge NEED:JOB`, `--delete-job JOB`, `--charge
+  JOB=SECONDS` (the bare cost, stated by the caller). `--workflow F --last N`
+  prints median and p90 over the last N runs. The CI design archive's phase-2
+  method generalised (tag `archive/probe/design-ci-rev4`), and
+  `dev/audit/harnesses/r10_critpath_archive_parity.py` holds it to that
+  method's V1 numbers run for run. When: a job-graph change states the wall
+  it buys before it is built. Refusal: an edge the workflow does not have, a
+  needs cycle, or a run past `--max-reads` API reads; jobs and needs are
+  cached per run id and head, so a re-run reads only `--last`'s run list.
diff --git a/tools/audit/seat/instruments/ci_probe.py.md b/tools/audit/seat/instruments/ci_probe.py.md
new file mode 100644
index 000000000..789c7e091
--- /dev/null
+++ b/tools/audit/seat/instruments/ci_probe.py.md
@@ -0,0 +1,17 @@
+# `ci_probe.py`
+
+- `ci_probe.py` — the writes a CI-layout probe needs, each behind the same
+  guards: `push <ref> <sha>` (only `refs/heads/ci-probe/*`), `dispatch`,
+  `rerun-job`, `cancel`, `label`, `retarget`, `close`, and the owner-only
+  `review --approve --sha` and `dismiss-review`. When: the P2 probe fan-out
+  (`plans/ci-layout`). Refusals: a ref outside `ci-probe/`, a missing or other
+  `--repo`, `/rate_limit` below 20 % remaining (or unreadable), a token that is
+  not `tvofi` on a review, a host path in a ref, message or log line, and a
+  commit the push publishes first whose message carries a tool's attribution
+  or whose identity names a machine (`ref_privacy.published`). One log
+  line per write (`--log`); `--dry-run` writes nothing. Nothing polls (the 60 s
+  floor holds vacuously). `--self-test` runs over fakes and a throwaway bare
+  remote, including the namespace control: a planted `ci-probe/x` leaves
+  `cloud_relay.sh`'s probe arm and `bus.sh orphans` unchanged, a planted
+  `probe/foo` is OWED. `prune_refs.py` deletes a `ci-probe/*` ref, untagged,
+  unless an open pull request has it as head.
diff --git a/tools/audit/seat/instruments/cloud-setup.sh.md b/tools/audit/seat/instruments/cloud-setup.sh.md
new file mode 100644
index 000000000..873de410b
--- /dev/null
+++ b/tools/audit/seat/instruments/cloud-setup.sh.md
@@ -0,0 +1,14 @@
+# `cloud-setup.sh`
+
+- `cloud-setup.sh` — the cloud seat environment's setup script (interpreter,
+  CI-run pinning): it builds `venv-ci` and `venv-ha` under `/opt/hpo` and
+  writes the toolchain profile. When: tvofi pastes it into Project settings; a
+  seat cannot apply its own environment. A seat's Bash call inherits the
+  agent's environment and reads neither the profile nor `BASH_ENV`, so the
+  toolchain reaches it only through the environment's variables, which
+  `--variables` prints and the setup run's last line names; `--check`, in a
+  seat: `OK` (exit 0) only when all three hold, or `REFUSE` naming them (exit
+  1). The profile prepends `venv-ci/bin` only
+  when absent, so a PATH a caller narrowed is left alone; `--self-test`: the
+  profile, variables and check arms. Refusal: a missing checkout warns and
+  exits 0, so a session still starts, without pins.
diff --git a/tools/audit/seat/instruments/cloud_dispatch.py.md b/tools/audit/seat/instruments/cloud_dispatch.py.md
new file mode 100644
index 000000000..fec3c3134
--- /dev/null
+++ b/tools/audit/seat/instruments/cloud_dispatch.py.md
@@ -0,0 +1,50 @@
+# `cloud_dispatch.py`
+
+- `cloud_dispatch.py` — renders the whole cloud-runner trigger payload
+  (`job_config.ccr`: `environment_id`, `session_context` with `allowed_tools`,
+  `model` and `sources`, and one user-message event) for a `reviewer`,
+  `fixer` or `probe` seat from the PR, the 40-hex head, the bus nonce and an
+  optional brief file. The environment id, model and repository come from a
+  flag, an overlay JSON (`--overlay` / `$HPO_CLOUD_OVERLAY`) or `HPO_CLOUD_*`,
+  never from the tree. `--role R --group G --model M` is the one-call path
+  (`dispatch_group()` for a host such as the beat): the brief, topic and
+  repository come from the roster at `--roster-ref` (default the round's roster
+  branch, `roster_lib.default_roster_ref`); the head is `--head`, else
+  `origin/main`'s tip, never the roster ref's (a reviewer must pass its PR
+  head); the environment is the overlay / `HPO_CLOUD_ENV_ID`; a flag it does
+  not consume (`--topic`, `--brief`, `--repo`, `--env-id`, `--out`) refuses;
+  it renders through the same `render` (the payload is the flag path's byte
+  for byte), publishes PAYLOAD.json and PROMPT.md on origin as
+  `dispatch/<role>-<topic>` (fast-forwarded, an identical tree adds nothing, a
+  render refusal pushes nothing) and prints that ref name, the one line a
+  standing trigger is fired with; `dev/audit/harnesses/r10_flow_dispatch_mutants.py`
+  re-runs its mutants. When: dispatching a seat to the cloud runner;
+  paste the printed JSON as the trigger update, or fire the standing trigger
+  with the printed ref. The measured shape of a cloud seat:
+  every trigger update resends the full ccr and then `run`s it, never a
+  patch; the brief is snapshotted at `run`, so it is inlined at render time,
+  an edit afterwards reaches no running seat, and overlapping runs are fine;
+  the toolchain (`PATH` with `/opt/hpo/venv-ci/bin`, `BASH_ENV`,
+  `HPO_TYPING_PYTHON`, `OPENBLAS_CORETYPE`) comes from the environment's
+  variables, not from a profile the seat sources, so the prompt says only
+  that it is on `PATH`; the seat starts off `main` in a shallow clone
+  (`git fetch --unshallow --tags origin` first); the return signal is a
+  pushed ref: `probe/rev-<pr>-<nonce first 8>` for a reviewer (see
+  `cloud_relay.sh`: a cloud reviewer never runs `bus.sh`, whose dispatch record
+  lives on the orchestrator's machine and refuses "unknown nonce" anywhere
+  else, and a seat may not write a record it did not mint), `handoff/<topic>`
+  plus `handoff-body/<topic>` for a fixer, `handoff-body/<topic>` for a probe,
+  and a return push carries only the seat's own result tokens: a push
+  carrying system-file dumps is refused; the session is reachable one way,
+  by `SendMessage` to it, and nothing comes back on that channel. Refusal: a
+  head that is not 40 lowercase hex, a reviewer without a nonce or `--pr`, a
+  fixer or probe without `--topic`, a missing environment id, model or
+  repository, and any home-directory path in the rendered text
+  (`ref_privacy.HOME_DIR`, brief included). `--self-test` grades each
+  refusal against a rendering that passes, offline.
+  Two measured traps when driving the runner: an update and a run fired in
+  parallel start the run on the PREVIOUS config, so a launch is update, wait
+  for it, then run, sequentially; and, until the pasted setup script writes
+  `cloud-setup.sh`'s idempotent profile, the container's `BASH_ENV` puts the venv
+  python ahead of the test stubs, so a cloud seat runs `tests/entities.py` (and
+  anything else resolving `homeassistant`) with `env -u BASH_ENV`.
diff --git a/tools/audit/seat/instruments/cloud_relay.sh.md b/tools/audit/seat/instruments/cloud_relay.sh.md
new file mode 100644
index 000000000..b9839a67e
--- /dev/null
+++ b/tools/audit/seat/instruments/cloud_relay.sh.md
@@ -0,0 +1,133 @@
+# `cloud_relay.sh`
+
+- `cloud_relay.sh` — the orchestrator's half of a cloud reviewer's return:
+  `cloud_relay.sh <pr> <nonce> <head40>` fetches
+  `probe/rev-<pr>-<nonce8>`, grades it, then runs `bus.sh push-verdict` locally,
+  where the dispatch record lives; `bus.sh confirm` follows as for any verdict.
+  When: a `probe/rev-*` ref appears after dispatching a cloud reviewer. Refusal:
+  a nonce that does not match the verdict's `bus-nonce:` line, a ref whose
+  commit subject (`verdict <pr> <head>`) or verdict first line names another PR
+  or head, a missing `ev/`, and a ref already relayed (a ledger of
+  `<ref> <sha>` under the state directory, written only after `push-verdict`
+  succeeded, so a re-pushed ref relays again). `--self-test` grades each
+  refusal against a clean ref, offline, with `push-verdict` stubbed. It also
+  NORMALISES one shape and logs it (`normalised first line: A -> B`): a blocked
+  first line whose tail the reviewer wrapped, `blocked <head> [class: reason]`,
+  loses its one outer bracket pair in the relay's temp copy, which is lossless
+  and puts the line in `bus.sh`'s grammar (`blocked <head> <class>: <reason>`).
+  Chosen over refusing because the relay is the one place the verdict can be
+  repaired without a round trip to a cloud seat that has exited, and the
+  rewrite changes no word; a bracketed merge suffix, a nested bracket or a
+  class outside `[a-z-]+` is refused unchanged (stripping a merge suffix would
+  lose text). `cloud_dispatch.py`'s prompt now gives the unbracketed grammar.
+  `cloud_relay.sh --watch [--interval N] [--once]` is the orchestrator's poll
+  loop, tracked: every N seconds (default 120) it runs the probe arm, which
+  lists every `refs/heads/probe/*` with `git ls-remote origin`. A probe ref
+  that is not `rev-*` (a probe seat's return, a stray push) is
+  `OWED <utc> probe-ref <ref> <sha>` in `<log>.level` until
+  `cloud_relay.sh dispose <ref> <sha>` records it handled: a level, not a
+  diff, so a missed line is repeated rather than lost, and a disposed ref
+  that moves is owed again at its new sha. Every pass REWRITES its kind's
+  lines in `<log>.level` and appends none to the log (appended, 2026-10-21: 34757 copies
+  of ~281 items once reached the board); `dispose [--log FILE]` drops the
+  line at once from the level beside that log (the pass's `--log`), and a
+  failed listing leaves the level as it was. It relays each `rev-*` ref+sha
+  once, taking the head and full nonce from the dispatch record (`$HPO_BUS_STATE`
+  or `~/.zcode/bus`, `pr head thread nonce`). A ref with no record is logged and
+  left for a later pass; a refused ref+sha (relay rc 2, a refusal of the ref
+  itself) goes to `<ledger>.refused` and is not retried until it is pushed
+  again, so one refusal does not repeat every interval. Any other failure (a
+  push or a fetch; an HTTP 400 push once left a verdict refused in silence for
+  3 h) is retried on later passes, `HPO_RELAY_TRIES` times in all (default 3),
+  then refused. A refusal prints `REFUSED <ref> <sha> <reason>` (the relay's
+  last stderr line) and is `OWED <utc> probe-refused <ref> <sha> <reason>` in
+  `<log>.level` until disposed; one refused before reasons were kept stays
+  silent. Run it detached (`daemonize.py`); it uses ls-remote, not the REST
+  quota. `--once` is one pass.
+  `--confirm` (on `--watch` and on a single relay) keeps going past
+  `push-verdict`: after one that passed it runs `bus.sh confirm <pr>
+  <review-sha>` (review/<pr>'s tip as `git ls-remote` answers it, when that tip
+  carries this verdict's tree: confirm takes only a tip) and appends `POSTED
+  <utc> <pr> <sha>` or `OWED <utc> <pr> <sha|-> <why>`, `<why>` carrying
+  confirm's last output line, to `--log FILE` (default
+  `cloud-relay.log` under the state directory), the file the orchestrator
+  reads; two verdicts once sat relayed and unposted for 20 minutes. Confirm
+  never runs after a refused relay or a failed `push-verdict`, and those write
+  no line (the refusal is printed; `--watch` also keeps it in `.refused`).
+  A `push-verdict` refused non-fast-forward (review/<pr> moved under it) is
+  run again, three times at most: `bus.sh` re-reads the fresh tip and appends
+  the same verdict there, never forcing; a fresh tip already carrying this
+  verdict's tree is not re-applied. Both are printed, and so is
+  `review/<pr> remote tip <sha>` after the push.
+  `cloud_relay.sh pass [--confirm] [--log FILE] [--loop [--interval N]]` is the
+  orchestrator's whole beat as ONE entry point (it replaces the session-local
+  `relay_watch.sh`): a driver calls it once per tick, or `--loop` repeats it
+  (default every 120 s). A pass runs the handoff arm, then the relay arm above,
+  then with `--confirm` the confirm arm, then the stuck arm. Stuck arm (a
+  report-only trial, triage P163): each branch lock held now whose recorded
+  start epoch is older than `HPO_PUSH_STUCK_SECS` (default 900) prints
+  `STUCK <branch> <pid> <age>s` (the lock's name, the run's pid) and is
+  `OWED <utc> push-stuck <branch> <pid> STUCK ...` in `<log>.level`; a
+  released lock is never read. Confirm arm: the ledger is written
+  before confirm runs, so a confirm that failed, or a relay by a stale script
+  or a call without `--confirm`, was never confirmed later (#2659, #2632). For
+  every `review/<pr>` tip the relay pushed (its `bus-nonce:` matches a
+  ledgered `probe/rev-<pr>-<nonce8>`) whose tree is not in `bus.sh`'s posted
+  record (`posted-signed`), it runs `bus.sh confirm <pr> <tip>`: `POSTED` on
+  success; on failure `OWED <utc> confirm-owed refs/heads/review/<pr> <tip>
+  tries=<n>/<max>: <last output line>` in `<log>.level`, retried next pass up
+  to `HPO_RELAY_CONFIRM_TRIES` (default 3), then owed untried until the posted
+  record shows it or `dispose` takes it (`dispose` takes `review/` refs). A tip
+  with no dispatch for its PR, head and nonce is owed `undispatched` and never
+  confirmed; a tip the relay did not push waits for the orchestrator's own
+  read. It makes no `gh` call (`bus.sh confirm` posts).
+  Handoff arm: for each OPEN pull request, topic = `headRefName` less `fix/` and
+  `-pr`; if `handoff-body/<topic>` and `handoff/<topic>` exist and the handoff is
+  not an ancestor of the PR head, it runs `update_pr.sh <branch> <code-sha>
+  <BODY.md> <issues>` (issues = the body's closing keywords; BODY.md is written
+  to a per-run `cloud-body.*` directory under the state dir and removed after,
+  since prepr refuses a body directly in a shared temp root), then
+  `approve_held_runs.sh` on the branch, then `bus.sh dispatch <pr> <new head>
+  cloud`, and appends `OWED reviewer-fire <pr> <head40> <nonce> <utc>` to the
+  log (firing the cloud reviewer stays with the orchestrator). It only updates an
+  existing PR, which the soft cap never refuses (it gates only group dispatch).
+  Hold: `cloud-handoff-hold` under the state dir lists PR numbers, one per line
+  (blank and `#` lines allowed); only the orchestrator writes it. A listed PR
+  whose handoff is ahead is not updated and prints `HELD #<pr> <handoff tip>`
+  once per pass, so a frozen PR's head stays put while its handoff branch keeps
+  moving; removing the number resumes it. A missing or empty file holds nothing;
+  a line that is not a plain PR number refuses the whole handoff arm for that
+  pass (rc 2, `OWED handoff-hold-malformed` in `<log>.level`), never hold-all or hold-none.
+  `cloud_relay.sh held <pr>` answers from the same file (rc 0 held, 1 not, 2
+  malformed) for a driver that updates PRs itself.
+  Freeze (R10-FLOW-ROSTER-FREEZE): a PR whose live head is under review is not
+  updated either, so roster edits accumulate on the handoff ref and land between
+  reviews: a `Fix review: merge <head>` tip on `verdict/<pr>` at that head
+  (`HELD-VERDICT`), or a review of that head in flight with no verdict at it
+  (`HELD-REVIEW`: a `bus.sh dispatch` record of the PR at the head, or a
+  detached worktree at it). A verdict ref the listing names but the fetch
+  cannot read freezes too (`HELD-UNREAD`): it may be a merge at the head. A
+  blocked verdict, or one at an older head, freezes nothing. Each prints
+  `HELD-<why> #<pr> <handoff tip>` once per pass and is
+  `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in `<log>.level`;
+  `cloud-handoff-release` (the hold file's grammar) releases a listed PR from the
+  freeze, never from the hold, for new work that voids a merge verdict.
+  A handoff already inside its PR, or with no body ref, does nothing; a failed
+  update is noted in `cloud-handoff-failed` by `<topic> <code-sha>`, owed as
+  `OWED <utc> handoff-update <ref> <sha>` in `<log>.level` while that entry
+  matches the handoff's tip, and retried only when the handoff moves. An update that
+  exits 75 is BUSY (another `open_pr.sh` or `update_pr.sh` run holds the branch's
+  `upd-<branch>.lock`, typically the orchestrator's own update of that PR, or an `open_pr.sh` between its two pushes): it is
+  not recorded, and the next pass retries it. The update runs in a process
+  group of its own, so a signal to the loop's whole group reaches it only
+  through the loop's reap, and a KILL to that group leaves it to finish. The
+  `handoff-no-pr` lines in `<log>.level` are `ledger.py level`'s fold of
+  every `handoff/*` and `handoff-body/*` ref, rewritten every pass: owed unless
+  its topic has an open pull request, it is disposed at its sha, or main
+  already carries the change (ancestry, or content: see `ledger.py`), each
+  with its tip's commit time and last opener attempt; a failed PR listing or
+  ledger read leaves those lines as they were, since an empty list would make
+  every ref look orphaned. Every event the relay owes (`verdict-unposted` at
+  each passed push-verdict, `reviewer-fire`, `approve-held-runs`, `dispatch`)
+  is opened in the ledger, never appended to the log, which keeps only the
+  `POSTED` journal.
diff --git a/tools/audit/seat/instruments/codeql-triage-poll.sh.md b/tools/audit/seat/instruments/codeql-triage-poll.sh.md
new file mode 100644
index 000000000..e74f769af
--- /dev/null
+++ b/tools/audit/seat/instruments/codeql-triage-poll.sh.md
@@ -0,0 +1,5 @@
+# `codeql-triage-poll.sh`
+
+- `codeql-triage-poll.sh` — polls until GitHub attaches the #1769
+  evidence-alerts, dismisses them, re-runs CodeQL. When: a tools/ diff trips
+  CodeQL on evidence files; nothing to do until the alerts exist.
diff --git a/tools/audit/seat/instruments/daemonize.py.md b/tools/audit/seat/instruments/daemonize.py.md
new file mode 100644
index 000000000..4eaeef8ec
--- /dev/null
+++ b/tools/audit/seat/instruments/daemonize.py.md
@@ -0,0 +1,10 @@
+# `daemonize.py`
+
+- `daemonize.py` — detaches one long-running instrument from the session that
+  started it: fork/setsid/dup2/execvp around any `-- CMD`, with the log's
+  first line a banner naming the child pid, UTC time and full argv (the #2180
+  lessons: banner first, unbuffered), append mode so relaunches extend one
+  attributable file. When: a watch or sweep that must outlive its session —
+  round 9 re-derived the wrapper in /tmp four times before this existed.
+  Refusal: `--log` is mandatory and a non-existent `--cwd` aborts; no lock or
+  pid bookkeeping — the printed pid and `kill` are the stop story.
diff --git a/tools/audit/seat/instruments/delivery_row.sh.md b/tools/audit/seat/instruments/delivery_row.sh.md
new file mode 100644
index 000000000..97ff302d3
--- /dev/null
+++ b/tools/audit/seat/instruments/delivery_row.sh.md
@@ -0,0 +1,10 @@
+# `delivery_row.sh`
+
+- `delivery_row.sh` — the one seat-script writer of a PR's own `**open**`
+  row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and
+  `handoff_push.sh`: `commit_row` commits it as tvofi, `ensure_row` adds it
+  only when the head lacks it. `record_row.py` is the other row writer, for
+  the record beat's rows and its own PRs. When: never by hand; the openers
+  call it. Refusal: none; `ensure_row` adds nothing to a head that carries
+  the row, and `bus.sh --self-test` runs its self-test and refuses a seat
+  script with its own `write_row` or row commit.
diff --git a/tools/audit/seat/instruments/depgraph.py.md b/tools/audit/seat/instruments/depgraph.py.md
new file mode 100644
index 000000000..f2c856911
--- /dev/null
+++ b/tools/audit/seat/instruments/depgraph.py.md
@@ -0,0 +1,10 @@
+# `depgraph.py`
+
+- `depgraph.py` (tools/pr/) — compares GitHub's dependency graph with the
+  tree's pins: one SBOM read and one open-alerts read (`check --repo
+  OWNER/NAME`), every pip, npm and actions pin against the SBOM, and every
+  open alert the tree already pins past. When: Dependabot alerts that main's
+  locks should have closed, or `dependency-graph.yml`'s daily `check` is red.
+  Refusal: an SBOM ecosystem it does not enumerate, or an alert whose
+  versions it cannot order, exits 2 rather than reading clean; an alerts read
+  that fails prints `alerts: unread`, never OK.
diff --git a/tools/audit/seat/instruments/failure_logs.sh.md b/tools/audit/seat/instruments/failure_logs.sh.md
new file mode 100644
index 000000000..d00781d7e
--- /dev/null
+++ b/tools/audit/seat/instruments/failure_logs.sh.md
@@ -0,0 +1,10 @@
+# `failure_logs.sh`
+
+- `failure_logs.sh` — answers why a PR's newest red at its live head is red:
+  latest failing check-runs (grouped by name, newest `started_at` wins, so
+  red-then-green is not read as a failure) -> `details_url` -> job log ->
+  error lines, per-check log files and a `HEAD.txt` under the out-dir. When:
+  any red whose cause a watcher's state line does not carry. Refusal: a
+  non-Actions check prints NO-JOB, an unserved log prints NO-LOG and exits 1
+  with the count over readable logs beside the unread one; no error-marker
+  match falls back to the log's tail, never a silent zero.
diff --git a/tools/audit/seat/instruments/features_block.py.md b/tools/audit/seat/instruments/features_block.py.md
new file mode 100644
index 000000000..9a65a2803
--- /dev/null
+++ b/tools/audit/seat/instruments/features_block.py.md
@@ -0,0 +1,8 @@
+# `features_block.py`
+
+- `features_block.py` — runs one block of `tests/features.py`, from the line
+  holding a marker to the script's close, in the namespace features.py's
+  header builds. When: a mutation proof or a body figure that needs only the
+  block pinning the mutated line, on a seat where the whole script takes tens
+  of minutes. Refusal: a marker that is not in the script raises rather than
+  running an empty block.
diff --git a/tools/audit/seat/instruments/flow_metrics.py.md b/tools/audit/seat/instruments/flow_metrics.py.md
new file mode 100644
index 000000000..8d0368cdf
--- /dev/null
+++ b/tools/audit/seat/instruments/flow_metrics.py.md
@@ -0,0 +1,10 @@
+# `flow_metrics.py`
+
+- `flow_metrics.py` — a round's flow over one window, from git alone:
+  roster groups added and closed per hour (`--roster REF:PATH`, `--prefix`),
+  records' share of main's PR merges (`--record-prefix`), first-pass yield of
+  the merged fix PRs on the bus, main absorbs per fix branch, merge-to-merge
+  re-reviews of an unchanged PR diff (patch-id), and the share of hours with
+  a merge. When: a flow guardrail or a round's close reads throughput.
+  Refusal: a re-review whose heads git does not hold prints `unresolved`,
+  never counted; no round constant in code.
diff --git a/tools/audit/seat/instruments/fold_ledger.py.md b/tools/audit/seat/instruments/fold_ledger.py.md
new file mode 100644
index 000000000..dd22d9049
--- /dev/null
+++ b/tools/audit/seat/instruments/fold_ledger.py.md
@@ -0,0 +1,9 @@
+# `fold_ledger.py`
+
+- `fold_ledger.py` — folds a round's JUDGE.json and sweeps into
+  `bugclasses.json`, and checks the register against the judges. When: after a
+  judge lands, and before quoting the bugclass register as current state;
+  `sync` after any hand edit of `finding.schema.json`, which rewrites
+  `audit-find.js`'s generated CLASS_GUESS and FINDING_REPORT (fold runs it).
+  Refusal: `check` refuses a register that drifted from its judges — re-quote
+  the register, not a memory of it.
diff --git a/tools/audit/seat/instruments/gh_read.py.md b/tools/audit/seat/instruments/gh_read.py.md
new file mode 100644
index 000000000..6342fb76e
--- /dev/null
+++ b/tools/audit/seat/instruments/gh_read.py.md
@@ -0,0 +1,16 @@
+# `gh_read.py`
+
+- `gh_read.py` — the read rule every seat instrument's GitHub READS are
+  under, stated here once: `app_push.sh`'s read-back rule, 4 reads settling
+  5/15/45 s, retrying only a transport error, HTTP 5xx, 429 or a 403 whose
+  status line names the secondary rate limit; a failure naming a longer wait
+  (Retry-After, or a spent bucket's reset on a rate-limit response: a 429,
+  or a 403 naming a rate limit) is read no sooner, and one past 45 s refuses
+  at once naming it; any other status is judged by its code alone, whatever
+  bucket it carries. When: a new GitHub read in a seat instrument —
+  `retry` with `gh_wait` (gh's output) or `urllib_wait` (urllib's), and
+  `is_read` before retrying any `gh` call; `app_approve.sh`'s `gh_transient`
+  is the bash twin its self-test compares row for row. Refusal: every other
+  failure (401, a permission 403, 404, 422, an unclassified one) after its one
+  call, a spent budget with its last error and the attempt count; a write is
+  never retried. Its `self_test()` runs inside `record_row.py`'s.
diff --git a/tools/audit/seat/instruments/handoff_push.sh.md b/tools/audit/seat/instruments/handoff_push.sh.md
new file mode 100644
index 000000000..25b8eed55
--- /dev/null
+++ b/tools/audit/seat/instruments/handoff_push.sh.md
@@ -0,0 +1,11 @@
+# `handoff_push.sh`
+
+- `handoff_push.sh` — the legacy one-shot: pushes a handoff branch as
+  `hpo-author` with body, title and its own delivery row (`delivery_row.sh`;
+  its update path adds a row a refused earlier push left out). When: only where
+  `dev/programme/HANDOVER.md` still names it; new work uses `open_pr.sh`/`update_pr.sh`.
+  `--self-test` runs `delivery_row.sh`'s and its own: the three push calls
+  (open, update, row) over a scratch origin with a stub `app_push.sh`, so a
+  push line replaced by `true` reddens it (#2444). Every commit the code head
+  adds over `origin/main` passes `ref_privacy.py guard --over` before any
+  worktree or push, so a trailer the cloud harness pushed is refused there.
diff --git a/tools/audit/seat/instruments/handover_prompt.py.md b/tools/audit/seat/instruments/handover_prompt.py.md
new file mode 100644
index 000000000..d6a5c5bfd
--- /dev/null
+++ b/tools/audit/seat/instruments/handover_prompt.py.md
@@ -0,0 +1,6 @@
+# `handover_prompt.py`
+
+- `handover_prompt.py` — generates the next-session prompt from the roster
+  (and optionally a resume doc). When: ending a session; ready-next derives
+  from the roster's after-edges. Refusal: none to speak of — read the output
+  before pasting it, it is generated text.
diff --git a/tools/audit/seat/instruments/head_note.py.md b/tools/audit/seat/instruments/head_note.py.md
new file mode 100644
index 000000000..cbfde7af8
--- /dev/null
+++ b/tools/audit/seat/instruments/head_note.py.md
@@ -0,0 +1,8 @@
+# `head_note.py`
+
+- `head_note.py` (tools/pr/) — prefixes a note under a body's `## Head`
+  heading, found as `checkPrBody`'s `sections()` reads it (outside a fence,
+  `##`, whitespace, `Head`), never the first substring `## Head`.
+  `app_push.sh --recarry`, `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
+  write every head note through it. When: any new writer of a `## Head`
+  note. Refusal: a body with no `## Head` heading exits 1, file untouched.
diff --git a/tools/audit/seat/instruments/heartbeat.sh.md b/tools/audit/seat/instruments/heartbeat.sh.md
new file mode 100644
index 000000000..d1e525f91
--- /dev/null
+++ b/tools/audit/seat/instruments/heartbeat.sh.md
@@ -0,0 +1,18 @@
+# `heartbeat.sh`
+
+- `heartbeat.sh` — the andon (Lean flow study K8, R10-FLOW-ANDON; cost-tested
+  by R10-RCA-ORCH-CONTINUITY): `--once --message TEXT` force-pushes
+  `heartbeat/orchestrator` as one parentless empty-tree commit whose message is
+  the pass line `TICK-PASS <utc> relay=<..> tick=<rc>`, over the seat's own
+  credential (`-f --no-verify`, the message through `ref_privacy.py guard`);
+  a refused or failed push prints `HEARTBEAT NOT PUSHED: <reason>`, exits 1
+  and never stops the loop. `--watch [--max-age 1200]` is the off-host
+  watcher's command: it fetches the ref and exits 1 with `HEARTBEAT STALE: ..`
+  when the committer date is older than the limit or the ref is absent. When:
+  `tick_loop.sh` calls `--once` every pass; the owner schedules a cloud task
+  every 15 min running `--watch` that notifies the owner on exit 1 (the
+  schedule is owner-side, not in the tree). A standalone job script, so
+  R10-ORCH-MACHINERY registers it as the beat's heartbeat job and retires the
+  call from `tick_loop.sh`. Refusal: unknown option, a non-numeric
+  `--max-age`. `--self-test` drives both modes over a bare-repo fixture, a
+  stale ref and a fresh one.
diff --git a/tools/audit/seat/instruments/judge_batch.py.md b/tools/audit/seat/instruments/judge_batch.py.md
new file mode 100644
index 000000000..0aea58f32
--- /dev/null
+++ b/tools/audit/seat/instruments/judge_batch.py.md
@@ -0,0 +1,7 @@
+# `judge_batch.py`
+
+- `judge_batch.py` — re-runs every finding's harness, perturbation and null
+  control serially under the gate lease, one row per finding. When: a judge
+  grades a batch of findings and wants the mechanical half scripted. Refusal:
+  a perturbation that does not move the number in the stated direction prints
+  `void`; what it cannot run prints `by-hand`, never a pass.
diff --git a/tools/audit/seat/instruments/ledger.py.md b/tools/audit/seat/instruments/ledger.py.md
new file mode 100644
index 000000000..4d6473930
--- /dev/null
+++ b/tools/audit/seat/instruments/ledger.py.md
@@ -0,0 +1,21 @@
+# `ledger.py`
+
+- `ledger.py` — the obligations ledger (R10-ORCH-LEDGER; the machinery
+  design's section 6.3): one table of kinds, two stores beside the relay's log
+  (`dispositions.tsv`, written only by `dispose`; `events.tsv`, append-only
+  `open`/`close`/`attempt`) and one fold. Derived kinds are recomputed each pass
+  (`level` derives `handoff-no-pr` for the relay; the tick derives
+  `design-build` and `review-owed`); event kinds are keyed on kind, subject and
+  sha, an open at a new sha superseding the old, and close by the producer's
+  `close`, a moved or closed pull request, or the tick's read-back of the
+  approver's comment (`verdict-unposted` only on its own first line: a relayed
+  POSTED closes nothing). `escalate` turns stranded handoffs into DISPATCH
+  lines, oldest first, naming the roster group, and an OWNER FLAG past the
+  second threshold, behind `HPO_LEDGER_AGING` (`<dispatch_h>,<owner_h>` or
+  `off`; default the owner's 4 h and 12 h). `open_pr.sh` records each opener
+  attempt on its handoff ref (`started`, then `opened,PR=<n>` or `unopened`).
+  The first run imports `cloud-disposed` (last disposition per ref) and the
+  log's still-open OWED lines; a reader folds that in memory and writes
+  nothing. Refusals: a ref of no arm, a kind of no table, a derived kind
+  opened. A missing store is first run; an unreadable one is UNREADABLE.
+  `board` exits 0 none owed, 1 owed (with its summary line), 2 unreadable.
diff --git a/tools/audit/seat/instruments/merge_fastpath.py.md b/tools/audit/seat/instruments/merge_fastpath.py.md
new file mode 100644
index 000000000..baec318fb
--- /dev/null
+++ b/tools/audit/seat/instruments/merge_fastpath.py.md
@@ -0,0 +1,6 @@
+# `merge_fastpath.py`
+
+- `merge_fastpath.py` — classifies a changed file as workflow, claim, grader
+  or budget for `merge_train.py`'s batch routing: any such file sends a pull
+  request serial. Refusal: `--self-test` — `governance.yml` greps its
+  `checks, 0 failed` line.
diff --git a/tools/audit/seat/instruments/merge_pr.sh.md b/tools/audit/seat/instruments/merge_pr.sh.md
new file mode 100644
index 000000000..50b06bd26
--- /dev/null
+++ b/tools/audit/seat/instruments/merge_pr.sh.md
@@ -0,0 +1,12 @@
+# `merge_pr.sh`
+
+- `merge_pr.sh` — merges one PR after its evidence checks. When: a single
+  verdicted PR; for more than one, `merge_train.py` below. Owner mode takes
+  `--mandate <comment-id>` and reads that #201 mandate live; `--ready` marks a
+  draft ready. Refusal: a verdict or head mismatch stops the merge before the
+  merge API call; a draft without `--ready`, or owner mode with no mandate in
+  force, refuses before anything posts. Before its CI wait it runs
+  `merge_train.py unstale` (below) at the head. `--self-test` also drives the whole
+  script offline over a scratch clone and a fake `gh`, so the `gh pr merge …
+  --match-head-commit` line is pinned: replaced by `exit 0` it records no
+  merge and the null control reddens (#2444).
diff --git a/tools/audit/seat/instruments/merge_throughput.py.md b/tools/audit/seat/instruments/merge_throughput.py.md
new file mode 100644
index 000000000..12136cc51
--- /dev/null
+++ b/tools/audit/seat/instruments/merge_throughput.py.md
@@ -0,0 +1,17 @@
+# `merge_throughput.py`
+
+- `merge_throughput.py` — measures whether merges land inside the previous
+  merge's gate window often enough to justify a merge queue. When: someone
+  proposes a queue; the numbers decide before the mechanism is built. Its
+  `flow` subcommand is the flow board (Lean study K1): throughput against
+  the owner's demand of one roster group merged per hour, read from git
+  alone — the first-parent log, the review/verdict bus refs through
+  `review_strength`'s grammar and the roster through `roster_lib`. It prints
+  per rolling hour and per 24 h: groups closed against takt 1.0, fly-ins
+  closed, main moves split into group-carrying/record/roster-edit/fly-in,
+  WIP by flow lane (A/B/C/F), first-pass review yield with its blocked-class
+  mix, and lead time per size, and prints UNAVAILABLE rather than a zero
+  when a source cannot be read. When: any flow change that claims to move
+  throughput. Refusal: `--self-test` — its fixture's exact counts, the
+  unchanged-fixture null control, and a named arm per classification
+  predicate; `governance.yml`'s self-test step runs it.
diff --git a/tools/audit/seat/instruments/merge_train.py.md b/tools/audit/seat/instruments/merge_train.py.md
new file mode 100644
index 000000000..8b32d40e0
--- /dev/null
+++ b/tools/audit/seat/instruments/merge_train.py.md
@@ -0,0 +1,84 @@
+# `merge_train.py`
+
+- `merge_train.py` — lands a queue of verdicted PRs one at a time: re-carry
+  CI, wait for green at the exact head, evidence-gated approval,
+  `--match-head-commit`. When: any merge queue — queued PRs merge through
+  this, never by hand. Refusal: a head that moved under the review, red
+  checks the queue was not told to ignore, or a head whose TIP is a
+  GITHUB_TOKEN bot push (author `github-actions[bot]`) stop the train — such
+  a head has no `pull_request` run, the required contexts never report at it,
+  and the required follow-up is an App push (step 1's recarry once main
+  moves; batch routes such a head serial, `bot-head`, where that recarry runs
+  after the batch's own merges). A foreign merge moving main under a settled
+  head is recovered up to `--main-moved-tries` (default 3; 0 is the old stop):
+  serially by a recarry and a fresh CI wait, in a batch by re-proving the rest
+  on the new main. An owner approval GitHub already holds at the live head is
+  the owner's, with nothing re-posted (GitHub re-anchors one across a clean
+  base merge: #2209). `--bot-prs` merges the open record/autofix pull request
+  in the train's own sequence behind record_row.py's identical guard;
+  `--pre-flight` runs `queue_pre_flight.py` first and PARKs a failing entry;
+  `--free-holders` detaches a clean, pushed holder worktree. Every refused
+  merge attempt is logged in GitHub's words; the recarry worktrees a run made
+  are removed before its closing line. Every `gh api` GET and `gh pr view`
+  it or `queue_pre_flight.py` makes is under `gh_read.py`'s read rule, each
+  settle logged.
+  `queue <file>` writes the queue nobody had to assemble: every open
+  pull request but the record one whose approver-App verdict is newest, is
+  `verdict/<pr>`'s posted tip and is `merge` at its head or carries to it
+  (`app_approve.sh --carry`), oldest first, one `QUEUE`/`LEFT` line each;
+  budget and policy heads are queued for the batch's own serial route.
+  `add`'s admission (`Train.admit_add`) reads the same posted verdict
+  first, as its `verdict` rule, and fills an absent comment id from it.
+  bus.sh's post loads the train the moment it posts a merge verdict
+  (`merge_train.py add --auto`, with `HPO_BUS_TRAIN_STATE` set);
+  `sweep` is the slow backstop (`tick_loop.sh --sweep`, every 1800 s by
+  default): unless the ledger holds an open train-stop, it `add`s each head
+  `queue` admits that no sweep added at that head, into the live train's
+  next batch or a `train.sh --bot-prs --approval-carry --pre-flight` it
+  starts when none is live, never a second.
+  `batch` merges the queue without re-merging main: the entries' merges are
+  proved together on `batch/<tag>-<n>` (B), a lone entry merges unproved (D),
+  and workflow, claim, grader, budget or conflicting entries go serial. When:
+  the default for a queue. Refusal: a red main admits nothing; a red proof
+  drops its entry to serial,
+  and main's tree differing from the proof's before or after a merge stops it.
+  `batch --skip-bad` makes a per-entry refusal (admission, recarry, carry, CI,
+  merge) fatal for its entry alone — logged `SKIP #<pr>`, reported in
+  `skipped.json` and a `SKIP REPORT` line, rc 1 — while a red main and a Stop
+  after the merge API call stay global. `batch --overlap` (owner's P7) does
+  not wait on main's CI (log-only) and re-carries every serial entry up front
+  so their pull_request runs fire together; each lands in queue order when
+  its own required contexts conclude — the ruleset still gates every head.
+  A serial entry whose base THIS batch's own merges moved is graded before it
+  lands (`Train.grade_merge`, R10-TRAIN-OVERLAP-GRADE): the merge GitHub
+  would make is built with the train's driver-free text merge, materialised
+  as a throwaway worktree, and read by `policy_lint` always and
+  `tests/structure.py` where `tests/closures.json` selects it for the merge's
+  files. A red posts no approval and is HELD: `MAIN-MOVED` re-carries it and
+  CI judges the new head, and a recarry that reproduces the same red tree
+  stops instead of looping. A one-car batch (the #2595 repair car onto a red
+  main) cannot move a base, so the grade never fires there.
+  `batch` also takes several batches in one queue (a list of lists), run in
+  order on one train, each with its own admission, proof and merges; between
+  two it drains what `train.sh add` spooled into one more batch, never into a
+  batch in proof, and a batch that stops ends the train (`NOT RUN` lines). A
+  policy head batches like any other: under a `--mandate` naming the mandate's
+  comment id, in force for policy merging, the train posts the citing approval
+  step 5 requires (`policy_approve`); a budget raise still goes serial.
+  `dev/audit/harnesses/r10_train_upgrade_mutants.py` holds one mutant per arm
+  of these three.
+  Residual: a proved pair's second merge does not wait for main's run on the
+  first; the proof graded the tree both make. A `batch/` branch the remote
+  will not delete is logged `NOT deleted`, for deletion by hand.
+  It owns the state classifier (Lean flow study K15) the tick also imports,
+  judged on the latest run of each required context (`main-protect-checks`,
+  read live; `record`, `record-autofix`, `nightly-status` and
+  `delivery-status` never count): a queued or in-progress run is a wait,
+  never red, and an unreadable ruleset refuses. `--overlap` logs main RED,
+  or still running, by that rule. Before a merge attempt a check-run still
+  queued or in progress over a completed workflow run is stale: its run is
+  re-run once, logged `STALE <context> ... run <id>` (a third recurrence goes
+  to a root-cause seat), and re-read. `unstale <sha>` runs that step alone;
+  `classify <sha>` prints GREEN (rc 0), RED (rc 1) or WAIT (rc 3) over a pull
+  request's required contexts (`--main`: less the PR-only ones), rc 2 when
+  unreadable — a head is reviewable unless RED.
diff --git a/tools/audit/seat/instruments/moved_paths.py.md b/tools/audit/seat/instruments/moved_paths.py.md
new file mode 100644
index 000000000..87cf0a179
--- /dev/null
+++ b/tools/audit/seat/instruments/moved_paths.py.md
@@ -0,0 +1,8 @@
+# `moved_paths.py`
+
+- `moved_paths.py` — lists every line in the given files that names a path
+  `tests/layout.json` marks moved: a retired file, its emptied directory, or
+  a lifted prefix. Each hit is tagged FALLBACK when the line also names the
+  new path. When: a move, or a review of one, before the push; a reader
+  dispositions every STALE? hit. Refusal: none; it enumerates and always
+  exits 0.
diff --git a/tools/audit/seat/instruments/offline_spy.py.md b/tools/audit/seat/instruments/offline_spy.py.md
new file mode 100644
index 000000000..409917125
--- /dev/null
+++ b/tools/audit/seat/instruments/offline_spy.py.md
@@ -0,0 +1,10 @@
+# `offline_spy.py`
+
+- `offline_spy.py` — runs a seat instrument's `--self-test` under a
+  throwaway HOME and counts what it reaches outside: socket connects and DNS
+  lookups (refused), gh/curl/wget/ssh/scp/nc calls on PATH (refused), git
+  calls whose target resolves to a URL remote, and the Python process's
+  subprocess creations. On macOS it also runs under `sandbox-exec`, denying
+  outbound IP and writes outside the temp directories. When: before wiring a
+  self-test into CI, and when reviewing one. Refusal: a non-zero exit, or any
+  network or remote-git call, per file.
diff --git a/tools/audit/seat/instruments/open_pr.sh.md b/tools/audit/seat/instruments/open_pr.sh.md
new file mode 100644
index 000000000..c2bc94162
--- /dev/null
+++ b/tools/audit/seat/instruments/open_pr.sh.md
@@ -0,0 +1,22 @@
+# `open_pr.sh`
+
+- `open_pr.sh` — opens a draft PR from `handoff/<topic>` as `hpo-author`,
+  adds its own delivery row, re-pushes, prints N and the head. When: the
+  orchestrator opens a seat's handed-off branch. Refusal, each an
+  `open_pr: REFUSE:` line before anything is written (`pr_args.sh`): fewer
+  than four arguments; a code sha that is not 40-hex or names no commit; one
+  that is not an ancestor of `origin/handoff/<topic>`, saying whether it is the
+  tip of `handoff-body/<topic>` ("that is the BODY sha; pass the CODE sha" —
+  twice on 2026-10-18 that sha stopped the script silently); a missing
+  `handoff/<topic>` or `handoff-body/<topic>`; no BODY.md at the body ref — the
+  body is the transport, not an afterthought. The soft cap gates only
+  dispatching a new roster group, and never refuses opening or updating a pull
+  request for an owed handoff (tvofi, 2026-10-20): a leading `--over-cap
+  "<reason>"` is still accepted and prints that it is advisory; `pr_cap.py
+  info` prints the open count as information, and a count gh cannot read says
+  so and still opens. Any later stop prints `open_pr: STOPPED: line N exited S: <command>` (an ERR trap), and a
+  refused push names its log. It holds the branch's `upd-<branch>.lock` from
+  before its worktree to its second push, so a concurrent `update_pr.sh` is BUSY
+  (75) and cannot detach the worktree under the PR's row (#2547-#2549).
+  `--self-test` runs `delivery_row.sh`'s, then
+  `pr_args.sh`'s.
diff --git a/tools/audit/seat/instruments/orchestrator_tick.py.md b/tools/audit/seat/instruments/orchestrator_tick.py.md
new file mode 100644
index 000000000..d5559895d
--- /dev/null
+++ b/tools/audit/seat/instruments/orchestrator_tick.py.md
@@ -0,0 +1,73 @@
+# `orchestrator_tick.py`
+
+- `orchestrator_tick.py` — the heartbeat's dispatch list: one read-only command
+  that measures the whole board — train liveness, stale queue entries, log/rc
+  tail, prepr slots; per open PR the latest check-run per name, reds unanswered
+  in `## Red checks`, missing delivery rows, moved verdicts with no carry,
+  BLOCKED, DIRTY with the conflicted files `git merge-tree` names under
+  GitHub's merge, no local driver run (the
+  claimnotes repair only when all are claim files; a content conflict goes
+  back to its fixer), NOT REVIEWABLE at a head whose required context
+  concluded red, zero-run heads, absent required contexts, twin heads, claim
+  stamps, staleness behind main; worker seats judged from the work they were
+  dispatched for; roster groups newly unblocked or blocked; main's tip, its
+  required contexts re-read live and judged by `merge_train.py`'s classifier,
+  the mandate through `budget_raise_gate`'s
+  own reader, action-pin drift. When: run BY a watcher seat on a ~4-minute
+  loop — never inline in the orchestrator's turn, whose cron firings skip
+  while a turn runs (measured: ticks skipped for hours during one diagnosis
+  turn); the watcher seat notifies only on actionable events (TRAIN
+  DONE/STOPPED with skip classes, Traceback, silent train death, a new merge
+  → beats owed) and never diagnoses or fixes. Every failed lane at main's
+  tip — required or not — becomes a fixer dispatch brief (context, job id +
+  error line, suspected class, dispatch instruction; bot lanes lead with the
+  ci-autofix rule): a main-side issue the orchestrator cannot resolve in one
+  short turn is fixer work, and the orchestrator's duty is routing, not
+  diagnosing. It replaces re-deriving the
+  sweep from conversation memory. It does NOT act; the orchestrator acts on
+  the list. Operating contract it assumes: orchestrator turns stay SHORT; any
+  script with over a minute of wait or execution runs BACKGROUND (nohup, log
+  file, completion notification); findings are DISPATCHED, not merely printed
+  — a finding that only lands in tick output repeats the
+  PR-comment-is-not-propagation defect. Refusal: a section whose read fails
+  prints UNREADABLE, never a silent skip; a rule the tick cannot read from
+  the tree or API it does not report. Every pass prints two level lines in
+  PRS (tvofi, 2026-10-20): `WIP: N/6 (open PRs M)`, N the roster groups whose
+  `resume.stage` is `in-progress` through `pr_cap.py`'s `wip_groups` and M its
+  counted open pull requests, flagged at or over `HPO_WIP_CAP` — at the cap a
+  new group is not dispatched, while opening and merging are always allowed;
+  and `coordinator.py PRs: K/2`, the counted pull requests whose three-dot diff
+  touches the coordinator, flagged over 2 or when a diff is unreadable. Also
+  level lines every pass from the approver App's newest `Fix review:` on
+  each open PR (the identity off `app_approve.sh`, the grammar `bus.sh`'s;
+  the round-10 orchestrator, 2026-10-18): `MERGE-READY: #N <head8>` for a
+  merge verdict at the current head on a CLEAN or UNSTABLE PR, and
+  `BLOCKED-UNFIXED: #N <head8>` for a blocked verdict at the current head with
+  no `handoff/<topic>` tip committed after it. A verdict at a stale head prints
+  neither; comments it cannot read print UNREADABLE. One comments read per
+  open PR per pass. A queue entry is unmerged only when its PR is in the open
+  set (one `gh pr list --state open` per pass, TRAIN and REPLAN alike), never
+  from a `pulls/<n>` `.state`, which reads `closed` for a merged PR: a queue
+  whose entries are all merged prints no train-not-alive line (2026-10-18, t16).
+  `OWED: <line>` prints every pass for each line of `cloud_relay.sh`'s level
+  file (`<log>.level`, beside its default log `$HPO_STATE_DIR/cloud-relay.log`;
+  a line of no ledger kind prints REFUSED) and for each event `ledger.py`'s
+  fold holds open against this pass's open-PR heads and read-back verdicts;
+  its stranded handoffs escalate to `DISPATCH:` and `OWNER FLAG:` lines
+  (`ledger.escalate`); no store and no log yet prints no OWED. `REVIEW OWED:
+  #N <head12>` prints for each open non-draft PR whose head no approver
+  verdict names and no `bus.sh` dispatch record carries, and PLAN prints
+  `DESIGN-BUILD:` for an approved `design/<g>` whose group has no build
+  dispatched. `OWED handoff: <bus.sh ORPHAN line>`
+  prints every pass for each complete handoff no PR head carries, read by
+  `bus.sh orphans --min-age-h 0` (a pull request behind its own newer handoff
+  included, #2411); a run with no summary line is UNCHECKED, never a clean
+  zero. STATE's missing-row check, the closes check and the #201
+  unrecorded-merge check enumerate merges through
+  `tests/delivery_status.py`'s `parse_log` and `collect`, so a `<title> (#N)`
+  merge counts as a merge (#2413, #2412, #2407). `--only CARRY`
+  (opt-in, weekly and at closure; never in the default pass) runs
+  `carry_audit.py sweep --last N --issues` over origin/main and the tick's
+  roster ref: exit 1 prints one dispatch line and the unowned lines, and a
+  run without its `CARRY-SWEEP:` summary is UNREADABLE. Its driver is
+  `tick_loop.sh`.
diff --git a/tools/audit/seat/instruments/plan_audit.py.md b/tools/audit/seat/instruments/plan_audit.py.md
new file mode 100644
index 000000000..029f0bc76
--- /dev/null
+++ b/tools/audit/seat/instruments/plan_audit.py.md
@@ -0,0 +1,19 @@
+# `plan_audit.py`
+
+- `plan_audit.py` — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the
+  `audit-plan` workflow. `ledger` parses each merged PR's
+  `## Architecture score` block with the parser `score.py`'s own report
+  answers to, reconciles it metric by metric against `PLAN.json`'s moves, and
+  demands the moves' sum account for `score.py --diff <fork> HEAD` within
+  `--tolerance`; a merged metric no move names, a planned group with no body,
+  an unexplained dS, an inadmissible reading or WORSENS fails, so a dS no
+  planned move explains is `metric-gamed` rather than banked (`snapshot`
+  likewise records the fork). `snapshot` records one ref's structure budgets,
+  gate-only tripwires, behaviour inventory (entities, services, option steps,
+  card tabs), mutation kill rate and 200-merge change coupling -- the fork's
+  read by `--instrument`'s own scorer, so both sides are measured by the base
+  -- and `compare` fails on any regression, with `--allow KIND:KEY` for a
+  removal the plan's ADR approved. When: the architect measures the fork, and
+  the stamp compares it. Refusal: `ARCHSCORE_ABLATE` set; a plan naming a
+  different fork; two snapshots read by different instruments; `--self-test`
+  (`governance.yml` greps its `checks, 0 failed` line).
diff --git a/tools/audit/seat/instruments/plan_page.py.md b/tools/audit/seat/instruments/plan_page.py.md
new file mode 100644
index 000000000..d818edea3
--- /dev/null
+++ b/tools/audit/seat/instruments/plan_page.py.md
@@ -0,0 +1,16 @@
+# `plan_page.py`
+
+- `plan_page.py` — renders the round's plan page (HTML) from
+  `tools/plan/replan.py`'s plan.json, the roster through `roster_lib`, and
+  GitHub's issue and pull-request state (`gh`, or `--github-snapshot`):
+  swimlanes on the plan's time axis with the slot-occupancy strip,
+  critical-path marks and planned stamps; the group ledger with status
+  classes, PRs, struck closed issues and blockers; waves, stamps and the
+  ETA method, every figure plan.json's. First section: open issues on
+  not-done groups projected to close at the last carrying group's finish
+  (closed ones dropped, unplanned ones flat), omitted with a note when `gh`
+  is absent. When: after a replan at a wave
+  edge. Refusal: a plan `replan.stale_reason` calls stale (its roster blob
+  is not the roster's at its ref now; an `origin/` ref is fetched first) or
+  `replan.check_plan` refuses -- exit 1, nothing written. `--check` of
+  replan.py applies the same freshness rule.
diff --git a/tools/audit/seat/instruments/plan_table.py.md b/tools/audit/seat/instruments/plan_table.py.md
new file mode 100644
index 000000000..d16f5a97e
--- /dev/null
+++ b/tools/audit/seat/instruments/plan_table.py.md
@@ -0,0 +1,6 @@
+# `plan_table.py`
+
+- `plan_table.py` — renders the plan artifact from a wave-groups roster:
+  swimlanes, mermaid gantt (critical path tagged `crit`), per-group detail,
+  ETA. When: regenerating the plan table after a roster edit. Refusal: none —
+  but the gantt's grammar checks run in `--self-test`, not at render time.
diff --git a/tools/audit/seat/instruments/policy_reread_check.py.md b/tools/audit/seat/instruments/policy_reread_check.py.md
new file mode 100644
index 000000000..6df375a77
--- /dev/null
+++ b/tools/audit/seat/instruments/policy_reread_check.py.md
@@ -0,0 +1,10 @@
+# `policy_reread_check.py`
+
+- `policy_reread_check.py` — says whether a session owes a policy re-read:
+  OK when `--stamp`'s instant is later than the newest compaction in
+  `--transcript` (a JSON line whose `subtype` is `compact_boundary`), else
+  OWED; `--write-stamp` records a finished re-read in the format the check
+  reads. When: the sweep's step 0 (`sweep_template.md`), after every
+  compaction. Refusal: it fails closed -- no stamp, an unparseable one, one
+  ahead of the clock, an unreadable transcript, or a line naming the marker
+  that is not JSON each print OWED, never OK. `--self-test` drives both arms.
diff --git a/tools/audit/seat/instruments/pr_args.sh.md b/tools/audit/seat/instruments/pr_args.sh.md
new file mode 100644
index 000000000..52abb1779
--- /dev/null
+++ b/tools/audit/seat/instruments/pr_args.sh.md
@@ -0,0 +1,24 @@
+# `pr_args.sh`
+
+- `pr_args.sh` — sourced by `open_pr.sh` and `update_pr.sh`: their argument
+  checks, the ERR trap that reports every other stop, so neither stops
+  silently, and `pr_branch_lock`, the per-branch lock both take. The lock
+  outlives the run's push whatever stops the run: its holder ignores TERM,
+  INT and HUP, and lets go only once the push's own lock (`pr_push_hold`, an
+  fd every process of the push inherits) is free, so a SIGKILLed run's lock
+  is held until its push has ended. The lock file reads `<run pid> <holder
+  pid> <start epoch>`, and a fourth field `drain` meanwhile. No `ps` and no process-group walk: on a host without `pgrep` a
+  stopped run says it could not reap, and its lock is held until its push
+  ends. Inside `pr_push_hold` git's auto-maintenance runs in the foreground
+  (`gc.autoDetach`, `maintenance.autoDetach` off), so a `git gc --auto` a
+  push's fetch starts is part of that push rather than a PID-1 orphan holding
+  its lock. With `detach` the holder leaves the run's worktree detached once
+  the push has ended, a SIGKILLed run's too. Only the lock exits 75; a step
+  that does is reported as a stop and exits 1. `pr_bounded` runs a self-test
+  (its own, `update_pr.sh`'s, `cloud_relay.sh`'s) as a session of its own under
+  `PR_SELFTEST_SECONDS` (default 1200), and ends that whole session on exit,
+  at the bound (exit 124, a `BOUND:` line) or once its supervisor is gone;
+  `pr_own_group` starts a command as a process group's leader. When: never by hand; `--self-test` drives both scripts end to end
+  in a scratch repository, offline, each refusal arm beside a mutant that
+  deletes its predicate line (`# mut:<name>`) and must fail the arm, plus
+  null controls that pass every check. Refusal: its self-test's tally.
diff --git a/tools/audit/seat/instruments/pr_cap.py.md b/tools/audit/seat/instruments/pr_cap.py.md
new file mode 100644
index 000000000..31648b823
--- /dev/null
+++ b/tools/audit/seat/instruments/pr_cap.py.md
@@ -0,0 +1,15 @@
+# `pr_cap.py`
+
+- `pr_cap.py` — the soft cap, on dispatch since 2026-10-20: `dispatch-gate`
+  counts the roster groups whose `resume.stage` is `in-progress` through
+  `roster_lib` at the roster ref, prints their ids and refuses at or over
+  `HPO_WIP_CAP` (default 6) unless `--over-cap "<reason>"` is given; `info`
+  prints the open count for `open_pr.sh` and never refuses. A group that also
+  has an open pull request is one group. Imported by `orchestrator_tick.py`
+  for its `WIP` and coordinator level lines. A bot is a GitHub-flagged bot
+  other than `app/hpo-author`, which authors every seat PR. When: before
+  dispatching a new group, and `open_pr.sh` before it opens (information
+  only); the tick every pass. Refusal: at or over the cap without
+  `--over-cap <reason>`; an empty reason; an invalid `HPO_WIP_CAP`; a roster
+  it cannot read (never a clean zero); an open list gh cannot read, that is
+  not JSON, or that reaches gh's 200 limit (reported, not gated).
diff --git a/tools/audit/seat/instruments/preflight.sh.md b/tools/audit/seat/instruments/preflight.sh.md
new file mode 100644
index 000000000..e207ed179
--- /dev/null
+++ b/tools/audit/seat/instruments/preflight.sh.md
@@ -0,0 +1,7 @@
+# `preflight.sh`
+
+- `preflight.sh` — mechanical checks on anything the orchestrator publishes
+  (merge body, issue body, comment, brief): closing keywords and the claim
+  shapes. When: before posting any prose that GitHub or a later seat reads.
+  Refusal: a closing keyword in prose closes issues you did not mean to touch;
+  it refuses rather than warns.
diff --git a/tools/audit/seat/instruments/prepare_baseline.sh.md b/tools/audit/seat/instruments/prepare_baseline.sh.md
new file mode 100644
index 000000000..c10fc105b
--- /dev/null
+++ b/tools/audit/seat/instruments/prepare_baseline.sh.md
@@ -0,0 +1,7 @@
+# `prepare_baseline.sh`
+
+- `prepare_baseline.sh` — builds a round's audit baseline: a git-archive
+  export finders work in, one worktree per mutating finder, briefs copied in.
+  When: starting a round. Refusal: an archive run from a `git archive` copy
+  fails the `recorded_at` check on every mutant, baseline included — the M0
+  null run attributes that to the runner, not the findings.
diff --git a/tools/audit/seat/instruments/prepr.sh.md b/tools/audit/seat/instruments/prepr.sh.md
new file mode 100644
index 000000000..a3a553f1b
--- /dev/null
+++ b/tools/audit/seat/instruments/prepr.sh.md
@@ -0,0 +1,7 @@
+# `prepr.sh`
+
+- `prepr.sh` — the pre-PR self-check on your own branch and body: head SHA
+  freshness, claim files byte-identical, the MODE line, carry destinations,
+  body headings, and the scoped-closure selection. When: always, before
+  handing a branch off. Refusal: each blocked reason names the artifact —
+  a branch that fails prepr locally would have burned a review round instead.
diff --git a/tools/audit/seat/instruments/proof_watch.py.md b/tools/audit/seat/instruments/proof_watch.py.md
new file mode 100644
index 000000000..fa7c5ab39
--- /dev/null
+++ b/tools/audit/seat/instruments/proof_watch.py.md
@@ -0,0 +1,14 @@
+# `proof_watch.py`
+
+- `proof_watch.py` — watches one named check-run at one pinned head of one
+  pull request and, once it completes `success` beside green required contexts
+  and a valid merge verdict at that exact head, merges through `merge_pr.sh`.
+  When: a long validating run whose green-to-merge window would otherwise sit
+  unattended (the 4.5 h proof misread as failed, P8). Refusals: a head that
+  moved off the pin, a named check that completed not-success, an exceeded
+  `--budget`, a red required context (the ruleset's list, read through
+  `merge_train.required`), an unmergeable pull request and a head
+  `app_approve --dry-run` does not verdict — each aborts with a logged report
+  and no merge; one instance per pinned head (flock), and `--dry-run` passes
+  every guard and touches nothing. `--mode owner` hands `merge_pr.sh` its
+  `--mandate <comment-id>`, and refuses at launch without one.
diff --git a/tools/audit/seat/instruments/prune_refs.py.md b/tools/audit/seat/instruments/prune_refs.py.md
new file mode 100644
index 000000000..4fa14816c
--- /dev/null
+++ b/tools/audit/seat/instruments/prune_refs.py.md
@@ -0,0 +1,16 @@
+# `prune_refs.py`
+
+- `prune_refs.py` — reconciles the remote branch refs down to main plus a few
+  development branches at programme closure, archive-as-tags first. When: the
+  R9-CLOSURE-BRANCHES step 4 (prune by rule), and any future round's closure.
+  Four rules -- keep `main` and any ref whose pull request is OPEN; delete a
+  ref already merged into main, and an unmerged `handoff/*` ref whose pull
+  request merged (a same-named PR, or the branch of a roster group the roster
+  records `done`); enumerate the residue (no PR, or a closed-unmerged one) for
+  an individual disposition, archived-and-deleted by default. Refusals: a plan
+  that would act on `main`, and any `verdict/*` deletion while `--verdicts-drained`
+  is unset (the bus watcher reads those refs). Every tag is created before any
+  deletion, and `--archive-scope none` deletes nothing, so no tip is ever
+  dropped unarchived; `--dry-run` (the default) prints the plan and writes
+  nothing. `--self-test` drives the classifier, the planner, the precedence and
+  the ordering offline (22 checks).
diff --git a/tools/audit/seat/instruments/pulse.py.md b/tools/audit/seat/instruments/pulse.py.md
new file mode 100644
index 000000000..0cfc6ce75
--- /dev/null
+++ b/tools/audit/seat/instruments/pulse.py.md
@@ -0,0 +1,16 @@
+# `pulse.py`
+
+- `pulse.py` — says whether the programme is still being driven, from origin
+  alone: per consumer, an input an off-host producer already delivered that
+  the consumer's footprint has not answered within a bound — a handoff with no
+  pull request and nothing opened since it arrived (`bus.sh orphans`, invoked),
+  a verdict still at its open pull request's head, a main move the round's
+  state ref has not followed. When: from where the orchestrator's host is not
+  (a scheduled cloud probe seat), and first at any takeover, before the hand
+  survey (R10-RCA-ORCH-CONTINUITY). Refusal: an input it could not read is
+  `UNREADABLE`, exit 2, never ok; a stamp ahead of the clock is never aged.
+  `--dump` keeps the snapshot a `STOPPED` line came from; `--snapshot`
+  re-judges it. A `STOPPED` line names the standing seat its input waits on,
+  and `--seat-queue SEAT=FILE[:MIN]` judges a standing seat on its session
+  queue file (`<epoch> <text>` lines): STOPPED past the seat's cadence, ok
+  when empty, `UNREADABLE` when missing.
diff --git a/tools/audit/seat/instruments/push.sh.md b/tools/audit/seat/instruments/push.sh.md
new file mode 100644
index 000000000..005d00838
--- /dev/null
+++ b/tools/audit/seat/instruments/push.sh.md
@@ -0,0 +1,7 @@
+# `push.sh`
+
+- `push.sh` — pushes a branch and attaches a body that has already passed the
+  contract check, in that order (#678). When: tvofi-identity pushes only;
+  App-authored PRs go through `app_push.sh`. Refusal: the contract check runs
+  before the push, so the red `pr-contract` can never land on your review
+  head.
diff --git a/tools/audit/seat/instruments/queue_pre_flight.py.md b/tools/audit/seat/instruments/queue_pre_flight.py.md
new file mode 100644
index 000000000..c6320fe8a
--- /dev/null
+++ b/tools/audit/seat/instruments/queue_pre_flight.py.md
@@ -0,0 +1,14 @@
+# `queue_pre_flight.py`
+
+- `queue_pre_flight.py` — runs a merge queue's admission reads offline, before
+  the train launches: per entry PASS, PARK (the train's own Stop wording — a
+  carry that fails, a missing or stale delivery row, a GITHUB_TOKEN bot tip, a
+  branch another worktree holds, a policy or budget head without the owner's
+  in-force mandate) or FAIL (a verdict that is not 40-hex, a closed pull
+  request). When: before any `merge_train.py run`/`batch` — an admission-time
+  refusal parks the entry here instead of stopping a live queue mid-run.
+  Refusal: exit 1 unless every entry passed; the checks are the train's own
+  methods (`bot_tip`, `policy_gate`, `app_approve.sh --carry`), never new ones.
+  `merge_train.py --pre-flight` runs it inside the train, passing the two
+  shapes the train now cures itself: a bot tip, and under `--free-holders` a
+  holder `Train.freeable` clears.
diff --git a/tools/audit/seat/instruments/record_row.py.md b/tools/audit/seat/instruments/record_row.py.md
new file mode 100644
index 000000000..ba75f7b31
--- /dev/null
+++ b/tools/audit/seat/instruments/record_row.py.md
@@ -0,0 +1,15 @@
+# `record_row.py`
+
+- `record_row.py` — the record-autofix generator: enumerates merged PRs from
+  the REST API, plans the delivery rows the tree still lacks, applies them
+  behind a guarded write set (`dev/programme/delivery/<N>.md` only). When: the periodic
+  `record` beat. Refusal: any path outside `dev/programme/delivery/<N>.md` — the plan
+  table and HANDOVER are a seat's dispositions, never this generator's — and
+  a window it cannot attribute refuses rather than reports empty. Every API
+  read is `_api`'s, under `gh_read.py`'s read rule.
+  `--automerge-check --pr N [--head SHA] [--hold] [--require-green]` is the
+  guard CI approves and merges a record pull request behind (exit 3: guard
+  passes, a required check has not yet); `--replay-moved` replays one
+  older than the row directory's move. Refusal: any file but a new one-line
+  row at its canonical path that the API's facts re-generate, or an author
+  other than the hpo-author App.
diff --git a/tools/audit/seat/instruments/ref_privacy.py.md b/tools/audit/seat/instruments/ref_privacy.py.md
new file mode 100644
index 000000000..9a43b0868
--- /dev/null
+++ b/tools/audit/seat/instruments/ref_privacy.py.md
@@ -0,0 +1,14 @@
+# `ref_privacy.py`
+
+- `ref_privacy.py` — the one owner of what a push may say about the host
+  (#2310): `slug <path>` names a local path for a ref (`<root>-<rest>` under
+  a named root, else `ext-<leaf>-<hash>`); `guard --ref R [--message M]
+  [--commits REV [--over BASE] -C DIR]` refuses a ref name or commit message carrying the
+  home directory, an account name, the uid, a session temp root or a host
+  path, or a message carrying a tool's attribution (exit 3, the class named,
+  the text not echoed); `--commits` reads what the push publishes first,
+  `--over BASE` every commit REV adds over BASE; `--check` refuses a
+  tracked file with a push site its `PUSHERS` registry does not name, and a
+  `guarded` entry that calls no guard. When: before every push an instrument
+  composes; a new pusher registers in `PUSHERS` in the same diff. Refusal: a
+  push that would publish the host never runs.
diff --git a/tools/audit/seat/instruments/remerge_main.sh.md b/tools/audit/seat/instruments/remerge_main.sh.md
new file mode 100644
index 000000000..672d7e6d7
--- /dev/null
+++ b/tools/audit/seat/instruments/remerge_main.sh.md
@@ -0,0 +1,8 @@
+# `remerge_main.sh`
+
+- `remerge_main.sh` — merges origin/main into an open PR (claimnotes merge
+  driver), drops inherited claims, pushes as the App with `app_push.sh
+  --recarry`, which prefixes ## Head with what happened and skips prepr only
+  on a clean 2-parent merge of the live head and main under the live body.
+  When: main moved under an open PR. Refusal: a conflict is not
+  auto-resolved — it stops loudly instead.
diff --git a/tools/audit/seat/instruments/resume_doc.py.md b/tools/audit/seat/instruments/resume_doc.py.md
new file mode 100644
index 000000000..6e0832142
--- /dev/null
+++ b/tools/audit/seat/instruments/resume_doc.py.md
@@ -0,0 +1,6 @@
+# `resume_doc.py`
+
+- `resume_doc.py` — generates the resume markdown from the roster plus live
+  PR state, under a byte budget. When: a state beat; regenerate rather than
+  hand-edit the resume. Refusal: over-budget output refuses with `--out`
+  unwritten — archive before regenerating.
diff --git a/tools/audit/seat/instruments/review_packet.py.md b/tools/audit/seat/instruments/review_packet.py.md
new file mode 100644
index 000000000..24d33aa6c
--- /dev/null
+++ b/tools/audit/seat/instruments/review_packet.py.md
@@ -0,0 +1,20 @@
+# `review_packet.py`
+
+- `review_packet.py` — the fix reviewer's packet at the frozen head: three-dot
+  diff, the head's check runs as read (red, pending, `none` or green, with run
+  ids), `carry_audit.py` and `figure_lint.mjs` at the head, the finder's
+  harness at both ends when one is named (`--harness`, at the base and
+  untouched by the diff, or `--harness-file` outside the tree; `none named`
+  and `not run` otherwise), and the mutation-ledger diff. When: through
+  `bus.sh dispatch`, which runs it in the checkout it is dispatching for; a
+  cloud reviewer, whose dispatcher's copy is a path on another machine,
+  renders its own from its dispatch prompt. Refusal: carry-audit, a `## Head`
+  not naming the head, a `tests/structure.py` refusal at the head merged with
+  main, an unanswered concluded red, a required context concluded failure, a
+  host path, or a hot file shared with an open pull request holding an
+  unboarded merge verdict; a pending check never refuses. A refusal still
+  WRITES the packet, so a held dispatch never withholds the evidence, except
+  a host path, which writes nothing because the packet carries the diff.
+  Unavailable (rc 3, `UNAVAILABLE`) is a different outcome: the seat cannot
+  read the packet's inputs (no checkout, no `gh`/token, a missing tool, an
+  unwritable `--out`), so it writes nothing and `dispatch` degrades.
diff --git a/tools/audit/seat/instruments/review_strength.py.md b/tools/audit/seat/instruments/review_strength.py.md
new file mode 100644
index 000000000..2fb149b36
--- /dev/null
+++ b/tools/audit/seat/instruments/review_strength.py.md
@@ -0,0 +1,16 @@
+# `review_strength.py`
+
+- `review_strength.py` — real-catch blocks per reviewed PR, incidence and
+  first-pass share from the `review/*` bus and its `archive/review/*` tags,
+  over git only (no REST), per window and per stratum: reviewer kind (a
+  probe-ref return is cloud), class, the class the wave routes (`route`, the
+  vocabulary read from web-fix-wave.js's VERDICT_CLASSES, never copied),
+  re-review after a merge verdict, and with `--roster` the PR's origin, fixer
+  model, size and product, taken `--as-of` the latest window's until (the
+  verdicts, `--tree` and the roster ref cut there). `--guardrail` prints the
+  review-strength guardrail's arms, report-only: incidence of the last 30
+  PRs and of each seat family's last 20 against P0 = 0.28 with REAL widened
+  by REAL_EXTRA, and the blocked words neither real nor taught. When: a flow guardrail
+  or a D13 round reads review strength; `dev/audit/rounds/round10/D13/yield-probe.md`
+  is its first use. Refusal: an out-of-grammar subject is its own row,
+  never a verdict.
diff --git a/tools/audit/seat/instruments/roster_edit.py.md b/tools/audit/seat/instruments/roster_edit.py.md
new file mode 100644
index 000000000..bc6ac41e1
--- /dev/null
+++ b/tools/audit/seat/instruments/roster_edit.py.md
@@ -0,0 +1,32 @@
+# `roster_edit.py`
+
+- `roster_edit.py` — the safe roster edit: every op loads the whole roster,
+  validates, and dumps with the file's own formatting; ops `set-stage`
+  (with `--at-sha`), `wire-issue [--field fixes|issues]`, `unwire-issue <group> <N> [--field
+  fixes|issues]` (refuses an absent N), `append-group`, `edit-brief`,
+  `append-carry`, `drop-carry <group> <index|--match TEXT>` (0-based index,
+  or the one entry containing TEXT; the last drop leaves `"carry": []`, the
+  key kept),
+  `set-after <group> <G1,G2,...|->` (replaces the after-edges whole, `-` for
+  none), and `set-resume <group> --field
+  <stage|commit|branch|last_step|next_step|note>` for the resume free-text
+  fields a session restarts from. When: any roster change — never a string
+  splice, which unbalanced the file twice. Refusals: the lint gate (run from
+  a fresh origin/main checkout — a stale `--lint-cwd` is refused itself), an
+  unknown group, a duplicate issue or carry, for `set-after` an unknown
+  after-group, a self-edge, a repeated edge and a cycle in the resulting
+  after-graph, for `drop-carry` an absent carry, an out-of-range index, no
+  match and an ambiguous match, and for `set-resume` an empty
+  value on the non-null fields (`stage`, `branch`) or a non-sha on
+  `--field commit`; an empty value on a nullable field clears it to null.
+  `--roster-ref` defaults to `main` and `--branch` to the round's
+  `handoff/audit-r<N>-roster`, never main itself; `--roster-path` overrides
+  the newest roster.
+  A no-op edit reproduces the roster's bytes exactly and reports `no change`
+  instead of an empty commit — the round-trip the self-test pins, because a
+  dump that misses the file's formatting rewrites all 7503 lines on any edit.
+  The edit is committed in a detached worktree and pushed as
+  `<sha>:refs/heads/<branch>`, never by a local branch name another run of
+  the same `--checkout` can reset. A push lost to a rival re-applies the op
+  on the new tip, at most `PUSH_ATTEMPTS` times, then refuses with rc 2; a
+  `--worktree` whose HEAD is on no origin ref is not reused.
diff --git a/tools/audit/seat/instruments/roster_lib.py.md b/tools/audit/seat/instruments/roster_lib.py.md
new file mode 100644
index 000000000..1a18e3d83
--- /dev/null
+++ b/tools/audit/seat/instruments/roster_lib.py.md
@@ -0,0 +1,12 @@
+# `roster_lib.py`
+
+- `roster_lib.py` — shared roster parsing and wave logic (depth, critical
+  path, open groups, the branch-to-group lookup), and the one owner of WHICH
+  roster: `roster_path` picks the newest `dev/programme/rosters/wave-r<N>-groups.json`
+  (at a ref or on the checkout) unless `--roster-path` names one; and of
+  WHICH REF: `default_roster_ref` answers the round's roster branch
+  `origin/handoff/audit-r<N>-roster` when the clone has it, else
+  `origin/main`, with a note whenever that answer may be stale. Import it;
+  `--self-test` is its only CLI. When: any tool that reads the roster — one
+  schema reader, not several. Refusal: no roster where one was asked for
+  raises `RosterNotFound`, never a fallback to another round's.
diff --git a/tools/audit/seat/instruments/roster_queue.py.md b/tools/audit/seat/instruments/roster_queue.py.md
new file mode 100644
index 000000000..e95251fa1
--- /dev/null
+++ b/tools/audit/seat/instruments/roster_queue.py.md
@@ -0,0 +1,12 @@
+# `roster_queue.py`
+
+- `roster_queue.py` — the standing roster seat's queue runner: `run FIRST LAST`
+  applies each queue line (`<op> <group> [arg] [--flag value]`, so `drop-carry G --match TEXT` works) through `roster_edit.py --push`,
+  linting from a clone it owns and detaches at `origin/main` before every
+  attempt (up to four, when main moved or a clean-lint push lost a race), and
+  never moving the orchestrator's checkout. `readback SHA GROUP FILE` prints
+  whether the roster at SHA holds the file's text as exactly one carry entry
+  (exit 1 when none). When: the roster seat works a queue file; run it alone
+  to replay a range. Refusal: a refused op is reported as `refused rc=N`, never
+  forced; `append-carry @file` reports FAILED when the read-back cannot find the
+  text. `--self-test` drives it offline over a stub editor and a scratch repo.
diff --git a/tools/audit/seat/instruments/roster_sync.py.md b/tools/audit/seat/instruments/roster_sync.py.md
new file mode 100644
index 000000000..bfdcb50e5
--- /dev/null
+++ b/tools/audit/seat/instruments/roster_sync.py.md
@@ -0,0 +1,18 @@
+# `roster_sync.py`
+
+- `roster_sync.py` — derives the factual half of a roster group's `resume`
+  from pull-request state: a merged pull request on the group's branch makes
+  it `done` at the merge commit (and routes the body's `Carry: <GROUP>` items
+  to the destination's `carry`), an open one makes it `in-progress` with
+  `resume.pr`. Branch matching is the topic rule its docstring states; a head
+  two topics match is the longer one's. It prints `RECORD-INVALID <group>` for
+  a `resume.commit` naming no commit or several, or a done group's off
+  `origin/main` -- a finding, never a refusal. When:
+  every `state_docs.py beat --apply` pass runs it; run it alone to see what a
+  pass would write. Dry run by default; `--apply` writes through
+  `roster_edit.write_roster()`, the one write path, lint gate and push-race retry. Refusals: an
+  unreadable pull-request read (never "no mismatches"), a `Carry:` to a done
+  group, `--apply` with `--roster-file`; a human disposition (`deferred`,
+  `refused` and every stage outside `DERIVABLE_STAGES`) is never rewritten,
+  and no pull request is no evidence. `--self-test` drives it offline over a
+  recorded `--pr-state`; `r10_roster_sync_mutants.py` plants its predicates.
diff --git a/tools/audit/seat/instruments/run_twins.py.md b/tools/audit/seat/instruments/run_twins.py.md
new file mode 100644
index 000000000..821918364
--- /dev/null
+++ b/tools/audit/seat/instruments/run_twins.py.md
@@ -0,0 +1,7 @@
+# `run_twins.py`
+
+- `run_twins.py` — counts a workflow's cancelled `pull_request` runs that
+  sat beside a same-SHA sibling (two events at one head, not a
+  supersession), from cached `/actions/workflows/<file>/runs` pages or
+  `--fetch`. When: judging a workflow's `concurrency:` block (R9-CI-2a).
+  Refusal: none; it enumerates.
diff --git a/tools/audit/seat/instruments/seat_venv.sh.md b/tools/audit/seat/instruments/seat_venv.sh.md
new file mode 100644
index 000000000..a0a7aa746
--- /dev/null
+++ b/tools/audit/seat/instruments/seat_venv.sh.md
@@ -0,0 +1,8 @@
+# `seat_venv.sh`
+
+- `seat_venv.sh` — builds the seat interpreter venvs reproducibly and installs
+  the `shims/`. When: a new workstation or cloud seat; CI features are
+  container-only on the Mac (no local venv for the Accelerate wheels).
+  Builds `venv-ci` (CI's `fast` pins) and `venv-ha` (the typing lock,
+  hash-pinned, `--no-deps`, cloud-setup.sh's pins call). `--check` reports
+  both. `--self-test` drives the recipe and the shim export.
diff --git a/tools/audit/seat/instruments/selftest_wiring.py.md b/tools/audit/seat/instruments/selftest_wiring.py.md
new file mode 100644
index 000000000..029e87821
--- /dev/null
+++ b/tools/audit/seat/instruments/selftest_wiring.py.md
@@ -0,0 +1,14 @@
+# `selftest_wiring.py`
+
+- `selftest_wiring.py` — refuses a self-testing file under `tools/` (widened
+  from `tools/audit/seat/` by #2444's forward-carry) that no workflow `run:`
+  line, comments removed, invokes with its self-test (`--check`,
+  `--self-test`). Runs first among the seat steps of
+  `instrument-self-tests`. When: adding a tool with a `--self-test`; add its
+  step in the same pull request. Refusal: each unwired file by path; a
+  mention in a comment, a step name or a `--check` call does not wire it.
+  `--check` also refuses this guide's index and its `instruments/` files
+  disagreeing: a line whose file is gone, a file linked twice or by no line,
+  or a line naming another instrument than its file's entry. When: adding,
+  renaming or removing an entry; its index line moves in the same pull
+  request.
diff --git a/tools/audit/seat/instruments/shims_seat-python.md b/tools/audit/seat/instruments/shims_seat-python.md
new file mode 100644
index 000000000..fb3f98018
--- /dev/null
+++ b/tools/audit/seat/instruments/shims_seat-python.md
@@ -0,0 +1,9 @@
+# `shims/seat-python`, `shims/seat-python3`
+
+- `shims/seat-python`, `shims/seat-python3` — the seat interpreter: execs the
+  venv-ci `seat_venv.sh` builds, under `$HPO_STATE_DIR` first and the default
+  state root `~/.local/state/hpo` second, and refuses naming that build command
+  when neither holds one; exports `HPO_TYPING_PYTHON` to venv-ha/bin/python
+  under the same two roots, only when that interpreter exists and the variable
+  is unset. When: a seat's PATH needs a pinned interpreter, and the scoped gate
+  should check the mypy census.
diff --git a/tools/audit/seat/instruments/state_docs.py.md b/tools/audit/seat/instruments/state_docs.py.md
new file mode 100644
index 000000000..999007e57
--- /dev/null
+++ b/tools/audit/seat/instruments/state_docs.py.md
@@ -0,0 +1,37 @@
+# `state_docs.py`
+
+- `state_docs.py` — one call regenerates the four state docs
+  (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`,
+  `handover_prompt.py`), commits exactly
+  their outputs to the orphan ref `handoff/audit-r<N>-plan` at
+  `handoff/round<N>/state/`, N the roster's round, and mirrors them to
+  `--mirror`. The flow board publishes beside the plan table, so a beat
+  pass carries the throughput figures with the plan they explain. When: every state
+  beat — it replaces the five hand commands (worktree, copy, commit, push,
+  mirror) and runs the generators instead of copying their logic. Dry run by
+  default: without `--push` nothing remote is written. Refusals: any path
+  outside the four state docs (the write set is checked before a commit
+  exists to push; every other path at the ref — a round's evidence — is
+  carried untouched), a first commit that would not be exactly the four
+  files, and an already-current tip, which is reported and left alone. The
+  commit is plumbing over a temp index, so the calling checkout's index is
+  never touched.
+  `state_docs.py beat` is the same instrument on a loop, and it lives here
+  rather than in a session's scratch for decision 0013's reason — an
+  instrument the programme runs belongs where a later session can test it. A
+  pass reads `--watch-ref` and the roster ref at origin (O17: a roster edit
+  moves the state docs as a merge does); when either has moved it refreshes
+  the roster ref (so resume fields other seats wrote are visible),
+  regenerates and pushes, and when neither has it writes nothing at all.
+  With no `--roster-ref` the roster ref is `roster_lib.default_roster_ref`'s. When:
+  continuously beside a merge train, since it takes no lock and cancels
+  nothing — the state docs are regenerated rather than rebuilt at session
+  end. Refusal, and the one that saves you: the tip is recorded ONLY on a
+  regeneration that returned 0, so a push the remote rejected is retried on
+  the next pass instead of silently dropping that merge from the record.
+  `--apply` runs `roster_sync.py --apply` at the start of each pass, before
+  the memo check, since a pull request can open or merge without moving a ref
+  the beat watches; without it the beat derives nothing.
+  `--once` is one pass and returns that pass's code; without `--tip-file` a
+  `--once` caller regenerates every time, so give it one to keep the loop's
+  memo on disk. `--self-test` drives all three arms offline.
diff --git a/tools/audit/seat/instruments/sweep_driver.py.md b/tools/audit/seat/instruments/sweep_driver.py.md
new file mode 100644
index 000000000..04f0d51d1
--- /dev/null
+++ b/tools/audit/seat/instruments/sweep_driver.py.md
@@ -0,0 +1,14 @@
+# `sweep_driver.py`
+
+- `sweep_driver.py` — the probe PR's sweep, where `workflow_run` never fires
+  (`gate-sweep.yml` runs only from the default branch): every poll (60 s floor,
+  tvofi 2026-10-19) it lists the PR's `ci.yml` runs at the live head, reads each
+  run attempt not yet swept (N5-1) and starts `python3 -I <tree>/tools/ci/gate.py
+  --sweep --run <id>` as a concurrent child for it: attempt 1 only under
+  `--nochain`, every attempt under `--chain`. It logs one line per sweep,
+  `superseded=1` for an attempt first seen already replaced, reads `/rate_limit`
+  before each poll and backs off below 20 % remaining or on a 403 (A1 item 5),
+  and exits after 900 s with every run completed and nothing new. When: a seat
+  drives a probe PR through the sweep (M-6, M-2, the combined control). It only
+  reads (`gh api` GET); the child's re-runs are the only writes. Refusal: a
+  `--poll` under 60. `--self-test` runs it over a fake `gh` and clock.
diff --git a/tools/audit/seat/instruments/sweep_render.py.md b/tools/audit/seat/instruments/sweep_render.py.md
new file mode 100644
index 000000000..19c76c130
--- /dev/null
+++ b/tools/audit/seat/instruments/sweep_render.py.md
@@ -0,0 +1,13 @@
+# `sweep_render.py`
+
+- `sweep_render.py` — renders the orchestrator sweep from
+  `sweep_template.md` and a session's JSON overlay (stdout or `--out`). The
+  template's `## Placeholders` table is the one registry of names. When: a
+  session or round sets up its recurring sweep -- render it, never hand-copy
+  the last session's prompt; the overlay stays out of the tree. Refusal: an
+  unfilled, empty or non-scalar value, an undeclared placeholder or overlay
+  key, a declared name the sweep never uses, a cited `tools/`, `tests/`,
+  `dev/` or `.github/` path that is not in the tree, and a home directory
+  (`ref_privacy.py`'s `HOME_DIR`) in the rendered text that no overlay value
+  supplied -- each exits 1 and writes nothing. `--self-test` renders the
+  tracked template and drives every refusal beside its null control.
diff --git a/tools/audit/seat/instruments/sweep_template.md.md b/tools/audit/seat/instruments/sweep_template.md.md
new file mode 100644
index 000000000..9eb4be044
--- /dev/null
+++ b/tools/audit/seat/instruments/sweep_template.md.md
@@ -0,0 +1,7 @@
+# `sweep_template.md`
+
+- `sweep_template.md` — the orchestrator's recurring sweep, steps in order,
+  each naming the instrument it runs by tree path and the rule file
+  (`orchestrator.md`, `nudge.md`, `CLAUDE.md`) it carries out; a usage guide
+  that restates no policy. When: read through `sweep_render.py`. Refusal: none
+  of its own -- the renderer's.
diff --git a/tools/audit/seat/instruments/tick_loop.sh.md b/tools/audit/seat/instruments/tick_loop.sh.md
new file mode 100644
index 000000000..2245bbf97
--- /dev/null
+++ b/tools/audit/seat/instruments/tick_loop.sh.md
@@ -0,0 +1,19 @@
+# `tick_loop.sh`
+
+- `tick_loop.sh` — the tick's driver loop (tvofi approved, 2026-10-18): each
+  pass runs `cloud_relay.sh pass --confirm` (a relayed verdict posts with no
+  hand step) when the tree carries it (#2419; skipped
+  and said so before), then `orchestrator_tick.py` with the given args,
+  writing the board whole to `--out` (default `$HPO_STATE_DIR/tick.txt`) and
+  one `TICK-PASS <utc> relay=<ok|rc=N|running|absent> tick=<rc>` line to
+  stdout. The relay runs detached under the flock `<out>.relay.lock`, waited
+  for at most `HPO_TICK_RELAY_WAIT` s (default 30): one still in flight is
+  left running, never killed, reported `relay=running`, and no second starts
+  while it holds the lock, so a long `update_pr.sh` push never holds the
+  board; the next pass reaps it, printing its output and a `TICK-RELAY` line.
+  When: run detached (`daemonize.py`) in place of a seat looping the tick;
+  `--once` makes one pass, `--interval` defaults to 300 s. Refusal: a
+  non-numeric `--interval` or an unknown option; a failing relay pass or tick
+  is reported and the loop goes on. `--self-test` drives it over stubs.
+  Each pass then calls `heartbeat.sh --once` (the andon, below), bounded at
+  60 s; `HPO_TICK_HEARTBEAT` replaces it.
diff --git a/tools/audit/seat/instruments/tmp_paths.py.md b/tools/audit/seat/instruments/tmp_paths.py.md
new file mode 100644
index 000000000..7be26b1d2
--- /dev/null
+++ b/tools/audit/seat/instruments/tmp_paths.py.md
@@ -0,0 +1,11 @@
+# `tmp_paths.py`
+
+- `tmp_paths.py` — refuses a tracked script, workflow or decision record that
+  depends on a temp or machine path (`--check`, `--self-test`). When: after
+  touching anything under `tools/`, `tests/`, `.claude/`, or before pushing.
+  Refusal: every match on its own line — a `/tmp` state name, a `$TMPDIR`
+  with a fixed name, a home path, an instrument run from `~/`; the 2026-10-03
+  temp cleanup deleted three tracked tools' state and one decision's design
+  note. It also refuses a temp, home or seat-directory path on a
+  `tests/mutation_ledger/` line the diff adds (a triage citing a probe no
+  other seat can run); main's stock is not charged.
diff --git a/tools/audit/seat/instruments/train.sh.md b/tools/audit/seat/instruments/train.sh.md
new file mode 100644
index 000000000..5b9e54471
--- /dev/null
+++ b/tools/audit/seat/instruments/train.sh.md
@@ -0,0 +1,30 @@
+# `train.sh`
+
+- `train.sh` — one invocation shape for `merge_train.py batch`: the seat
+  venv first on PATH — an absent venv refuses (naming `seat_venv.sh` to
+  build it), it never falls back to ambient python, which on 3.11 refuses
+  main's own nested-quote f-strings under `no-copies` — the child python
+  unbuffered (`-u`, so a detached caller's log shows stops and SKIP/OVERLAP
+  lines in real time), a pidfile refusing a second live train on the same
+  state dir, log and exit code under the state dir (`train.log`, `rc`), and
+  `--skip-bad`/`--overlap`/`--approval-carry`/`--bot-prs`/`--pre-flight`/
+  `--free-holders`/`--main-moved-tries N` passed straight through, each only
+  when given (a `0` default once passed `--skip-bad --overlap` on every
+  launch), and the child run from the repository root when `--checkout` is
+  absent (it once resolved to `tools/`). Foreground: the caller
+  detaches and owns the schedule. When: every merge queue — the per-session
+  scratch drivers this replaces duplicated the invocation, and one session's
+  copy ran prepr under the wrong interpreter and refused a clean branch.
+  Refusal: a live pidfile (take over only by removing it after checking the
+  pid is dead). `--self-test` drives the five refusals and the child argv
+  shape offline (missing required arg, live pidfile, unknown argument, the
+  `--ignore-red` argv shape, the absent-venv refusal), the child's cwd on a
+  launch without `--checkout`, and a bare launch's argv carrying no flag.
+  `train.sh add <pr> <verdict> --repo R --state-dir D [--verdict-comment ID]
+  [flags]` loads one pull request into that state dir's live train (its next
+  batch) or, with none live, starts one with those flags. When: whenever a
+  merge verdict is confirmed. Refusal: `ADD REFUSED #<pr> <rule>: <why>` from
+  `Train.admit_add` (shape, open, base, carry, row, budget-raise, policy),
+  and `one-train` beside a train.sh still closing; a pull request already
+  queued is `ALREADY`, rc 0. One fcntl lock (`queue.lock`) orders every add
+  against the train's drains and its close; never a second train.
diff --git a/tools/audit/seat/instruments/update_pr.sh.md b/tools/audit/seat/instruments/update_pr.sh.md
new file mode 100644
index 000000000..5e33ba2b4
--- /dev/null
+++ b/tools/audit/seat/instruments/update_pr.sh.md
@@ -0,0 +1,22 @@
+# `update_pr.sh`
+
+- `update_pr.sh` — brings an open PR branch to its head + a code SHA (merge) +
+  origin/main (merge), adds the PR's own delivery row when the head lacks
+  it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as
+  `hpo-author`. With code sha `-` it asks `app_push.sh --row-only`, so a push
+  that only adds the row takes the body contract instead of the full prepr,
+  and prints app_push's `ROW-ONLY:` line naming which ran and why.
+  When: updating a PR after review prep or a main merge.
+  Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
+  silently; no open PR at the branch stops before any push. Up front, each an
+  `update_pr: REFUSE:` line (`pr_args.sh`): fewer than three arguments; a
+  code sha other than `-` that is not 40-hex, names no commit, or is not an
+  ancestor of `origin/handoff/<topic>` (the topic `HANDOFF_TOPIC`, else the
+  branch less `fix/`, then less `-pr`), naming a `handoff-body/<topic>` tip as
+  the BODY sha; a missing `handoff/<topic>`; no body file. The body is a file
+  here, so a missing body ref is no refusal. It detaches another instrument's
+  clean worktree on the branch only when origin has that worktree's HEAD; one
+  holding commits origin lacks (a PR's unpushed row) is refused, naming it.
+  Any later stop prints `update_pr: STOPPED: ...`, and a refused push names its log.
+  Its lock's holder leaves its own worktree detached once its push has
+  ended, a SIGKILLed run's too, so no worktree of it holds the branch.
diff --git a/tools/audit/seat/instruments/worktree_gc.sh.md b/tools/audit/seat/instruments/worktree_gc.sh.md
new file mode 100644
index 000000000..64c3e9347
--- /dev/null
+++ b/tools/audit/seat/instruments/worktree_gc.sh.md
@@ -0,0 +1,6 @@
+# `worktree_gc.sh`
+
+- `worktree_gc.sh` — collects a merged PR's worktree, branch and seat
+  scratch. When: after merges, before the disk fills (9.5 GB of orphaned seat
+  directories once). Refusal: `--dry-run` prints the collection list; a
+  worktree with unpushed work is left alone.
diff --git a/tools/audit/seat/instruments/wt_sync.sh.md b/tools/audit/seat/instruments/wt_sync.sh.md
new file mode 100644
index 000000000..e06864bcd
--- /dev/null
+++ b/tools/audit/seat/instruments/wt_sync.sh.md
@@ -0,0 +1,10 @@
+# `wt_sync.sh`
+
+- `wt_sync.sh` — snapshots every worktree whose state is not already on
+  origin (unpushed commits, uncommitted or untracked files) to
+  `origin/wip-sync/<slug>`, plus the orchestrator scratch. The slug is
+  `ref_privacy.py slug`'s, never a host path (#2310). When: loop it
+  detached so a crashed seat is recoverable from its branch. Refusal: it
+  never touches the worktree or its index — a snapshot, not a save; a
+  worktree whose snapshot would name the host is skipped with the guard's
+  reason.
diff --git a/tools/audit/seat/selftest_wiring.py b/tools/audit/seat/selftest_wiring.py
index 292dc67de..8ed702028 100644
--- a/tools/audit/seat/selftest_wiring.py
+++ b/tools/audit/seat/selftest_wiring.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""Refuse a self-testing tool that no CI step runs.
+"""Refuse a self-testing tool that no CI step runs, or an unindexed instrument.
 
     python3 -I tools/audit/seat/selftest_wiring.py --check
     python3 -I tools/audit/seat/selftest_wiring.py --self-test
@@ -26,6 +26,14 @@ inside a quoted string can only make a file read unwired, never wired.
 Blind spots, stated: a self-test whose entry point is spelled neither way;
 a step that never runs (`if: false`, a job no event triggers); a step whose
 exit is ignored (`continue-on-error`, `|| true`).
+
+THE INDEX RULE (R10-FLY-INSTRUMENTS-SPLIT). The instruments guide is an index,
+`tools/audit/seat/INSTRUMENTS.md`, whose lines `- [label](instruments/<f>.md) — `
+each link one entry file under `tools/audit/seat/instruments/`. `--check` also
+refuses an index line whose file is missing, a file linked twice, an entry
+file no index line links, and a line whose label's first backticked name is
+not the name the file's entry opens with. It reads the files, not the
+scripts: an instrument with no entry at all is outside it.
 """
 from __future__ import annotations
 
@@ -42,6 +50,12 @@ SEAT = "tools/audit/seat"
 SELF_TEST_RE = re.compile(r"--self-test|self-test\)")
 RUN_RE = re.compile(r"^(?P<indent>\s*)(?:-\s+)?run:\s*(?P<rest>.*)$")
 COMMENT_RE = re.compile(r"(?:^|(?<=\s))#.*$")
+INDEX = f"{SEAT}/INSTRUMENTS.md"
+ENTRIES = f"{SEAT}/instruments"
+INDEX_RE = re.compile(
+    r"^- \[`(?P<name>[^`]+)`[^\]]*\]\((?P<target>instruments/[^)]+\.md)\) — ",
+    re.M)
+ENTRY_RE = re.compile(r"^- `(?P<name>[^`]+)`", re.M)
 
 
 def self_testing(root: Path) -> list[str]:
@@ -93,6 +107,33 @@ def wired(root: Path) -> set[str]:
     return found
 
 
+def index_gaps(root: Path) -> list[str]:
+    """Every way the guide's index and its entry files disagree."""
+    index = root / INDEX
+    if not index.is_file():
+        return [f"MISSING {INDEX}: the index is gone"]
+    gaps: list[str] = []
+    linked: set[str] = set()
+    for m in INDEX_RE.finditer(index.read_text()):
+        target = m.group("target")
+        if target in linked:
+            gaps.append(f"DUPLICATE {target}: linked by more than one index line")
+        linked.add(target)
+        entry = root / SEAT / target
+        if not entry.is_file():
+            gaps.append(f"MISSING {SEAT}/{target}: indexed, no such file")
+            continue
+        opens = ENTRY_RE.search(entry.read_text())
+        if not opens or m.group("name") != opens.group("name"):
+            gaps.append(f"MISMATCH {SEAT}/{target}: the index line's name is not "
+                        "the one its entry opens with")
+    entries = root / ENTRIES
+    for p in sorted(entries.glob("*.md")) if entries.is_dir() else []:
+        if f"instruments/{p.name}" not in linked:
+            gaps.append(f"UNINDEXED {ENTRIES}/{p.name}: no index line links it")
+    return gaps
+
+
 def check(root: Path) -> tuple[list[str], list[str]]:
     tests = self_testing(root)
     w = wired(root)
@@ -105,7 +146,11 @@ def report(root: Path) -> int:
         print(f"  UNWIRED {TOOLS}/{name}: no workflow run line names its self-test")
     print(f"selftest_wiring: {len(tests)} self-testing, "
           f"{len(tests) - len(unwired)} wired, {len(unwired)} unwired")
-    return 1 if unwired else 0
+    gaps = index_gaps(root)
+    for gap in gaps:
+        print(f"  {gap}")
+    print(f"selftest_wiring: {len(gaps)} index gap(s)")
+    return 1 if unwired or gaps else 0
 
 
 def self_test() -> int:
@@ -128,6 +173,15 @@ def self_test() -> int:
 
     seat = "tools/audit/seat"
     st = {f"{seat}/a.py": "if argv == ['--self-test']: pass\n"}
+    # A consistent guide: two index lines, each linking the file whose entry
+    # opens with its name, beside prose lines the index rule does not read.
+    guide = {
+        f"{seat}/INSTRUMENTS.md": "# Instruments\n\nProse, `a.py`.\n\n"
+        "- [`a.py`](instruments/a.py.md) — does a\n"
+        "- [`b.sh` (tools/pr/)](instruments/b.sh.md) — does b\n",
+        f"{seat}/instruments/a.py.md": "# `a.py`\n\n- `a.py` — does a. When: x.\n",
+        f"{seat}/instruments/b.sh.md": "# `b.sh`\n\n- `b.sh` (tools/pr/) — does b.\n",
+    }
     head = "jobs:\n  j:\n    steps:\n"
     cases = [
         ("an inline run line wires it (null control)", True,
@@ -189,6 +243,33 @@ def self_test() -> int:
        "not a file without one, a .md or .json, or a __pycache__ file",
        tests == ["audit/seat/a.py", "audit/seat/b.sh", "audit/seat/c.sh", "pr/f.py"]
        and unwired == tests)
+    # The index rule: the consistent guide is clean (null control), and each
+    # perturbation is named by its own gap -- deleting one index line is the
+    # owner's mutant for this rule.
+    idx = f"{seat}/INSTRUMENTS.md"
+    a_line = "- [`a.py`](instruments/a.py.md) — does a\n"
+    for name, edit, want in (
+        ("a consistent index and entry set has no gap (null control)", {}, []),
+        ("deleting one index line leaves its file unindexed",
+         {idx: guide[idx].replace(a_line, "")},
+         [f"UNINDEXED {seat}/instruments/a.py.md"]),
+        ("an index line whose file is gone is refused",
+         {f"{seat}/instruments/a.py.md": None},
+         [f"MISSING {seat}/instruments/a.py.md"]),
+        ("a file linked twice is refused",
+         {idx: guide[idx] + a_line}, ["DUPLICATE instruments/a.py.md"]),
+        ("a line naming another instrument than its file's entry is refused",
+         {idx: guide[idx].replace("[`a.py`]", "[`z.py`]")},
+         [f"MISMATCH {seat}/instruments/a.py.md"]),
+        ("an entry file no line links is refused",
+         {f"{seat}/instruments/c.py.md": "# `c.py`\n\n- `c.py` — c.\n"},
+         [f"UNINDEXED {seat}/instruments/c.py.md"]),
+        ("a missing index is refused", {idx: None}, [f"MISSING {idx}"]),
+    ):
+        files = {**guide, **edit}
+        root = tree("", {k: v for k, v in files.items() if v is not None})
+        gaps = index_gaps(root)
+        ck(name, [g.split(":")[0] for g in gaps] == want)
     # The refusal is report()'s exit code, which `--check` returns: grade it,
     # not only check()'s list (a `return 0` there passed every check above).
     for name, want, wf in ((
@@ -197,9 +278,15 @@ def self_test() -> int:
             head + f"      - run: python3 -I {seat}/a.py --self-test\n")):
         out = io.StringIO()
         with contextlib.redirect_stdout(out):
-            rc = report(tree(wf, st))
+            rc = report(tree(wf, {**st, **guide}))
         ck(f"{name} (rc={rc})", rc == want
            and f", {want} unwired" in out.getvalue())
+    wf = head + f"      - run: python3 -I {seat}/a.py --self-test\n"
+    out = io.StringIO()
+    with contextlib.redirect_stdout(out):
+        rc = report(tree(wf, {**st, **guide, idx: guide[idx].replace(a_line, "")}))
+    ck(f"--check exits 1 on an index gap when every file is wired (rc={rc})",
+       rc == 1 and "1 index gap(s)" in out.getvalue())
     print(f"selftest_wiring self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 

