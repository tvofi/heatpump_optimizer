# Instruments — the operator's guide to tools/audit/ and tools/audit/seat/

This is a usage guide, not policy: it says what each instrument does, when a
real lane reaches for it, and which refusal saves you. The obligations live in
`CLAUDE.md` and `.claude/rules/`; nothing here adds one. Every `--self-test`
runs offline. Each linked line below indexes one instrument; its text is
`instruments/<name>.md`, beside this file.

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

- [`app_approve.sh`](instruments/app_approve.sh.md) — approves a pull request as the `hpo-approver` App at one exact head SHA
- [`app_comment.sh`](instruments/app_comment.sh.md) — posts one fix-review verdict on a PR as `hpo-approver` and reads the posted comment back byte-identical
- [`app_push.sh`](instruments/app_push.sh.md) — pushes a branch and opens or re-bodies its pull request as the `hpo-author` App
- [`depgraph.py` (tools/pr/)](instruments/depgraph.py.md) — compares GitHub's dependency graph with the tree's pins
- [`figure_block.py` (tools/pr/)](instruments/figure_block.py.md) — renders/refreshes/verifies registered figure blocks in a PR body
- [`head_note.py` (tools/pr/)](instruments/head_note.py.md) — prefixes a note under a body's `## Head` heading, found as `checkPrBody`'s `sections()` reads it (outside a fence, `##`, whitespace, `Head`)
- [`role_pack.py` (tools/policy/)](instruments/role_pack.py.md) — renders one seat's policy pack: its role contract, the rules its reads load and the INSTRUMENTS.md entries it names, verbatim, in one file
- [`approve_held_runs.sh`](instruments/approve_held_runs.sh.md) — approves the workflow runs GitHub holds `action_required` on a branch
- [`check_scopes.py`](instruments/check_scopes.py.md) — proves the finder scopes are disjoint and complete within each dimension
- [`fold_ledger.py`](instruments/fold_ledger.py.md) — folds a round's JUDGE.json and sweeps into `bugclasses.json`
- [`judge_batch.py`](instruments/judge_batch.py.md) — re-runs every finding's harness, perturbation and null control serially under the gate lease
- [`machinery_ratchet.py`](instruments/machinery_ratchet.py.md) — caps the nonproduction merges and the nonproduct churn per product line in main's newest merge window, graded in `governance.yml`'s `policy-docs`
- [`merge_fastpath.py`](instruments/merge_fastpath.py.md) — classifies a changed file as workflow, claim, grader or budget for `merge_train.py`'s batch routing
- [`merge_throughput.py`](instruments/merge_throughput.py.md) — measures whether merges land inside the previous merge's gate window often enough to justify a merge queue
- [`preflight.sh`](instruments/preflight.sh.md) — mechanical checks on anything the orchestrator publishes (merge body, issue body, comment, brief)
- [`prepare_baseline.sh`](instruments/prepare_baseline.sh.md) — builds a round's audit baseline
- [`prepr.sh`](instruments/prepr.sh.md) — the pre-PR self-check on your own branch and body
- [`push.sh`](instruments/push.sh.md) — pushes a branch and attaches a body that has already passed the contract check, in that order (#678)
- [`worktree_gc.sh`](instruments/worktree_gc.sh.md) — collects a merged PR's worktree, branch and seat scratch

## tools/audit/seat/

The two standing seats that drive these instruments for the orchestrator each
have a contract under `dev/governance/roles/standing.md`:
`standing-merge.md` (the train) and `standing-dispatch.md`
(dispatch, relay, verdicts). The tick board and roster ops are the beat rows
`tick-digest`, `owed-check` and `roster-drain`. `pulse.py` and the sweep's
standing-seat liveness step keep the seats alive.

- [`features_block.py`](instruments/features_block.py.md) — runs one block of `tests/features.py`, or the script through a marker
- [`mutant_run.py`](instruments/mutant_run.py.md) — applies spec mutants or the diff's added lines one at a time to a git-archive copy and prints KILLED or SURVIVED
- [`body_push.sh`](instruments/body_push.sh.md) — publishes a handoff's BODY.md on the orphan ref `handoff-body/<topic>` (plus RESUME.md), parentless first commit, fast-forwards after
- [`body_patch.sh`](instruments/body_patch.sh.md) — repairs an open pull request's BODY, or any pull request's TITLE (`--title`), without moving its head
- [`autofix_statuses.sh`](instruments/autofix_statuses.sh.md) — re-derives what `mutation-autofix` and `closures-autofix` answered on recent pull-request runs
- [`bus.sh`](instruments/bus.sh.md) — git refs as the programme's message bus
- [`review_packet.py`](instruments/review_packet.py.md) — the fix reviewer's packet at the frozen head
- [`ci-watch.sh`](instruments/ci-watch.sh.md) — watches open PRs' check states and alerts only on NEW states (per-PR signature file)
- [`ci_critpath.py`](instruments/ci_critpath.py.md) — one workflow run's critical path from its job and step timestamps (each job's queue, duration and longest step), its `needs:` read from the run's own head
- [`probe_bridge.py`](instruments/probe_bridge.py.md) — re-derives the host probe's reference seconds from probed push runs on the hosted fleet itself
- [`cloud-setup.sh`](instruments/cloud-setup.sh.md) — the cloud seat environment's setup script (interpreter, CI-run pinning)
- [`cloud_dispatch.py`](instruments/cloud_dispatch.py.md) — renders the whole cloud-runner trigger payload (reviewer, fixer, probe, designer, design-reviewer)
- [`cloud_relay.sh`](instruments/cloud_relay.sh.md) — the orchestrator's half of a cloud reviewer's return
- [`codeql-triage-poll.sh`](instruments/codeql-triage-poll.sh.md) — polls until GitHub attaches the #1769 evidence-alerts, dismisses them, re-runs CodeQL
- [`daemonize.py`](instruments/daemonize.py.md) — detaches one long-running instrument from the session that started it
- [`delivery_row.sh`](instruments/delivery_row.sh.md) — the one seat-script writer of a PR's own `**open**` row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
- [`failure_logs.sh`](instruments/failure_logs.sh.md) — answers why a PR's newest red at its live head is red
- [`flow_metrics.py`](instruments/flow_metrics.py.md) — a round's flow over one window
- [`gantt_drift.py`](instruments/gantt_drift.py.md) — compares the replanned gantt with the real state and prints one `GANTT-SLIP` line per unacknowledged IDLE, LATE or CLOSURE slip
- [`gh_read.py`](instruments/gh_read.py.md) — the read rule every seat instrument's GitHub READS are under
- [`gh_read_run.py`](instruments/gh_read_run.py.md) — runs one `gh` read under `gh_read.py`'s rule, for a workflow step
- [`handoff_push.sh`](instruments/handoff_push.sh.md) — the legacy one-shot
- [`handover_prompt.py`](instruments/handover_prompt.py.md) — generates the next-session prompt from the roster (and optionally a resume doc)
- [`merge_pr.sh`](instruments/merge_pr.sh.md) — merges one PR after its evidence checks
- [`merge_train.py`](instruments/merge_train.py.md) — lands a queue of verdicted PRs one at a time
- [`ledger.py`](instruments/ledger.py.md) — the obligations ledger
- [`moved_paths.py`](instruments/moved_paths.py.md) — lists every line in the given files that names a path `tests/layout.json` marks moved
- [`offline_spy.py`](instruments/offline_spy.py.md) — runs a seat instrument's `--self-test` under a throwaway HOME and counts what it reaches outside
- [`open_driver.py`](instruments/open_driver.py.md) — the open arm: one pass opens the pull requests the tick board owes (topic→group incl. `-p<N>`/`-<N>` parts, priority, cap, STARVED, retry)
- [`open_pr.sh`](instruments/open_pr.sh.md) — opens a draft PR from `handoff/<topic>` as `hpo-author`, adds its own delivery row, re-pushes, prints N and the head
- [`orchestrator_tick.py`](instruments/orchestrator_tick.py.md) — the heartbeat's dispatch list
- [`owed_unactioned.py`](instruments/owed_unactioned.py.md) — says which tick owed lines have outlived a sweep with no live acknowledgement
- [`plan_audit.py`](instruments/plan_audit.py.md) — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the `audit-plan` workflow
- [`plan_page.py`](instruments/plan_page.py.md) — renders the round's plan page (HTML) from `tools/plan/replan.py`'s plan.json, the roster through `roster_lib`
- [`plan_table.py`](instruments/plan_table.py.md) — renders the plan artifact from a wave-groups roster
- [`policy_reread_check.py`](instruments/policy_reread_check.py.md) — says whether a session owes a policy re-read
- [`pr_args.sh`](instruments/pr_args.sh.md) — sourced by `open_pr.sh` and `update_pr.sh`
- [`pr_cap.py`](instruments/pr_cap.py.md) — the soft cap, on dispatch since 2026-10-20
- [`proof_watch.py`](instruments/proof_watch.py.md) — watches one named check-run at one pinned head of one pull request and, once it completes `success` beside green required contexts and a valid merge verdict at that exact head, merges through `merge_pr.sh`
- [`ci_probe.py`](instruments/ci_probe.py.md) — the writes a CI-layout probe needs
- [`closeout.py`](instruments/closeout.py.md) — the round's final act: archive, prune and clean up, a dry plan by default and refused while any other group is open
- [`prune_refs.py`](instruments/prune_refs.py.md) — reconciles the remote branch refs down to main plus a few development branches at programme closure, archive-as-tags first
- [`pulse.py`](instruments/pulse.py.md) — says whether the programme is still being driven
- [`queue_pre_flight.py`](instruments/queue_pre_flight.py.md) — runs a merge queue's admission reads offline, before the train launches
- [`record_row.py`](instruments/record_row.py.md) — the record-autofix generator
- [`ref_privacy.py`](instruments/ref_privacy.py.md) — the one owner of what a push may say about the host (#2310)
- [`remerge_main.sh`](instruments/remerge_main.sh.md) — merges origin/main into an open PR (claimnotes merge driver), drops inherited claims, pushes as the App with `app_push.sh --recarry`
- [`cancel_superseded.py sweep`](instruments/cancel_superseded.py.md) — cancels each open PR branch's active runs at a superseded head (`tools/pr/cancel_superseded.py`, one predicate), never a live-head, main, non-PR-event or bot-head run; ghosts reported; the sweep's step 4e
- [`run_twins.py`](instruments/run_twins.py.md) — counts a workflow's cancelled `pull_request` runs that sat beside a same-SHA sibling (two events at one head, not a supersession)
- [`resume_doc.py`](instruments/resume_doc.py.md) — generates the resume markdown from the roster plus live PR state, under a byte budget
- [`review_carry.py`](instruments/review_carry.py.md) — answers, from two shas and their commit range, whether a moved head still needs its own review
- [`review_strength.py`](instruments/review_strength.py.md) — real-catch blocks per reviewed PR, incidence and first-pass share from the `review/*` bus and its `archive/review/*` tags, over git only (no REST), per window and per stratum
- [`roster_edit.py`](instruments/roster_edit.py.md) — the safe roster edit
- [`roster_lib.py`](instruments/roster_lib.py.md) — shared roster parsing and wave logic (depth, critical path, open groups, the branch-to-group lookup)
- [`carry_fold.py`](instruments/carry_fold.py.md) — the orchestrator's pre-merge writer for a body's `Carry: <GROUP>` items, asserting each id landed after the fold
- [`roster_sync.py`](instruments/roster_sync.py.md) — derives the factual half of a roster group's `resume` from pull-request state
- [`roster_queue.py`](instruments/roster_queue.py.md) — the `roster-drain` beat row's queue runner
- [`seat_venv.sh`](instruments/seat_venv.sh.md) — builds the seat interpreter venvs reproducibly and installs the `shims/`
- [`selftest_wiring.py`](instruments/selftest_wiring.py.md) — refuses a self-testing file under `tools/` (widened from `tools/audit/seat/` by #2444's forward-carry) that no workflow `run:` line, comments removed, invokes with its self-test (`--check`, `--self-test`)
- [`tick_loop.sh`](instruments/tick_loop.sh.md) — the tick's driver loop (tvofi approved, 2026-10-18)
- [`heartbeat.sh`](instruments/heartbeat.sh.md) — the andon
- [`beatd.py`](instruments/beatd.py.md) — the one supervised beat (R10-ORCH-BEATD arm (a))
- [`beat_jobs.py`](instruments/beat_jobs.py.md) — the rows of `beatd.jobs.json`: each beat job's predicate, writing only actionable lines to one digest the orchestrator's one wake reads
- [`beatd_shims/git`](instruments/beatd_shims_git.md) — the beat jobs' `git`, reached only through the `PATH` `beatd.py` builds
- [`train.sh`](instruments/train.sh.md) — one invocation shape for `merge_train.py batch`
- [`state_docs.py`](instruments/state_docs.py.md) — one call regenerates the four state docs (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`, `handover_prompt.py`), commits exactly their outputs to the orphan ref `handoff/audit-r<N>-plan` at `handoff/round<N>/state/`, N the roster's round
- [`plan_public.py`](instruments/plan_public.py.md) — stages the ongoing round's plan page from the newest state ref for the public site, refusing a page that would publish a host path or a tool's attribution
- [`bottleneck_check.py`](instruments/bottleneck_check.py.md) — prints one `BOTTLENECK:` line per flow metric past the owner's threshold, with a suggested action the orchestrator decides on, and nothing when none is
- [`scorecard.py`](instruments/scorecard.py.md) — ten report-only convergence lines (gate and run health, first-verdict yield, machinery blocks, train skips, hotfix share, size, escapes, detection delay, seat cost), each but the hotfix naming measure held to a null control, written daily to `S/beatd/scorecard.txt`
- [`outside_intake.py`](instruments/outside_intake.py.md) — lists submissions by outside users since a cursor with what each is owed (triage, answer, reply), and answers or refuses one, marked so none is answered twice
- [`postmerge.py`](instruments/postmerge.py.md) — after a merge: the record-issue line, the roster stage, the state docs and main's suite state; a failed step is printed OWED and opens the ledger's `postmerge-owed`
- [`record_beat.py`](instruments/record_beat.py.md) — one merged pull request's record-issue line from a fixed template, the full merge sha, read back byte-identical
- [`sweep_driver.py`](instruments/sweep_driver.py.md) — the probe PR's sweep, where `workflow_run` never fires (`gate-sweep.yml` runs only from the default branch)
- [`sweep_render.py`](instruments/sweep_render.py.md) — renders the orchestrator sweep from `sweep_template.md` and a session's JSON overlay (stdout or `--out`)
- [`sweep_template.md`](instruments/sweep_template.md.md) — the orchestrator's recurring sweep, steps in order
- [`sweep_gantt.py`](instruments/sweep_gantt.py.md) — compares the live state to the plan's Gantt and prints each unacknowledged `GANTT-SLIP`
- [`verdict_audit.py`](instruments/verdict_audit.py.md) — maps every open PR to its latest verdict and holder; prints `UNHELD` lines
- [`survivor_list.py`](instruments/survivor_list.py.md) — refuses a `mutation-vacuous` verdict that omits a survivor its evidence's driver output reports; `bus.sh push-verdict` runs it
- [`bare_array.py`](instruments/bare_array.py.md) — refuses a bare `"${name[@]}"` in any tracked `tools/**/*.sh` script (a sourced library runs under its caller's `set -u`), which macOS bash 3.2 dies on when the array is empty (`--check`, `--self-test`)
- [`tmp_paths.py`](instruments/tmp_paths.py.md) — refuses a tracked script, workflow or decision record that depends on a temp or machine path (`--check`, `--self-test`)
- [`update_pr.sh`](instruments/update_pr.sh.md) — brings an open PR branch to its head + a code SHA (merge) + origin/main (merge), adds the PR's own delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as `hpo-author`
- [`wt_sync.sh`](instruments/wt_sync.sh.md) — snapshots every worktree whose state is not already on origin (unpushed commits, uncommitted or untracked files) to `origin/wip-sync/<slug>`
- [`shims/seat-python`, `shims/seat-python3`](instruments/shims_seat-python.md) — the seat interpreter
- [`shims/seat-gh`](instruments/shims_seat-gh.md) — the seat's `gh`: one log line per call (caller, subcommand, api path, no values), then the real gh
- [`gh_calls.py`](instruments/gh_calls.py.md) — reads that log: `--top` ranks callers and endpoints, `--coverage` names the processes whose PATH misses the shim
- [`hooks_setup.py`](instruments/hooks_setup.py.md) — reports and installs the user-level hooks (liveness, seat interpreter, git identity) and reports the project-level checkout guard, from `tools/audit/seat/hooks/`
