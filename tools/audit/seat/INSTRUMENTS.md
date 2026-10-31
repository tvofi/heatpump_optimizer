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
- [`head_note.py` (tools/pr/)](instruments/head_note.py.md) — prefixes a note under a body's `## Head` heading, found as `checkPrBody`'s `sections()` reads it (outside a fence, `##`, whitespace, `Head`)
- [`approve_held_runs.sh`](instruments/approve_held_runs.sh.md) — approves the workflow runs GitHub holds `action_required` on a branch
- [`check_scopes.py`](instruments/check_scopes.py.md) — proves the finder scopes are disjoint and complete within each dimension
- [`fold_ledger.py`](instruments/fold_ledger.py.md) — folds a round's JUDGE.json and sweeps into `bugclasses.json`
- [`judge_batch.py`](instruments/judge_batch.py.md) — re-runs every finding's harness, perturbation and null control serially under the gate lease
- [`merge_fastpath.py`](instruments/merge_fastpath.py.md) — classifies a changed file as workflow, claim, grader or budget for `merge_train.py`'s batch routing
- [`merge_throughput.py`](instruments/merge_throughput.py.md) — measures whether merges land inside the previous merge's gate window often enough to justify a merge queue
- [`preflight.sh`](instruments/preflight.sh.md) — mechanical checks on anything the orchestrator publishes (merge body, issue body, comment, brief)
- [`prepare_baseline.sh`](instruments/prepare_baseline.sh.md) — builds a round's audit baseline
- [`prepr.sh`](instruments/prepr.sh.md) — the pre-PR self-check on your own branch and body
- [`push.sh`](instruments/push.sh.md) — pushes a branch and attaches a body that has already passed the contract check, in that order (#678)
- [`worktree_gc.sh`](instruments/worktree_gc.sh.md) — collects a merged PR's worktree, branch and seat scratch

## tools/audit/seat/

The four standing seats that drive these instruments for the orchestrator each
have a contract: `dev/governance/roles/standing-tick.md` (the tick board),
`dev/governance/roles/standing-merge.md` (the train and direct merges),
`dev/governance/roles/standing-dispatch.md` (dispatch, relay, verdicts) and
`dev/governance/roles/standing-roster.md` (roster ops). `pulse.py` and the
sweep's standing-seat liveness step keep them alive.

- [`features_block.py`](instruments/features_block.py.md) — runs one block of `tests/features.py`
- [`body_push.sh`](instruments/body_push.sh.md) — publishes a handoff's BODY.md on the orphan ref `handoff-body/<topic>` (plus RESUME.md), parentless first commit, fast-forwards after
- [`body_patch.sh`](instruments/body_patch.sh.md) — repairs an open pull request's BODY without moving its head
- [`autofix_statuses.sh`](instruments/autofix_statuses.sh.md) — re-derives what `mutation-autofix` and `closures-autofix` answered on recent pull-request runs
- [`bus.sh`](instruments/bus.sh.md) — git refs as the programme's message bus
- [`review_packet.py`](instruments/review_packet.py.md) — the fix reviewer's packet at the frozen head
- [`ci-watch.sh`](instruments/ci-watch.sh.md) — watches open PRs' check states and alerts only on NEW states (per-PR signature file)
- [`ci_critpath.py`](instruments/ci_critpath.py.md) — one workflow run's critical path from its job and step timestamps (each job's queue, duration and longest step), its `needs:` read from the run's own head
- [`cloud-setup.sh`](instruments/cloud-setup.sh.md) — the cloud seat environment's setup script (interpreter, CI-run pinning)
- [`cloud_dispatch.py`](instruments/cloud_dispatch.py.md) — renders the whole cloud-runner trigger payload (reviewer, fixer, probe, designer, design-reviewer)
- [`cloud_relay.sh`](instruments/cloud_relay.sh.md) — the orchestrator's half of a cloud reviewer's return
- [`codeql-triage-poll.sh`](instruments/codeql-triage-poll.sh.md) — polls until GitHub attaches the #1769 evidence-alerts, dismisses them, re-runs CodeQL
- [`daemonize.py`](instruments/daemonize.py.md) — detaches one long-running instrument from the session that started it
- [`delivery_row.sh`](instruments/delivery_row.sh.md) — the one seat-script writer of a PR's own `**open**` row on its branch, sourced by `open_pr.sh`, `update_pr.sh` and `handoff_push.sh`
- [`failure_logs.sh`](instruments/failure_logs.sh.md) — answers why a PR's newest red at its live head is red
- [`flow_metrics.py`](instruments/flow_metrics.py.md) — a round's flow over one window
- [`gh_read.py`](instruments/gh_read.py.md) — the read rule every seat instrument's GitHub READS are under
- [`handoff_push.sh`](instruments/handoff_push.sh.md) — the legacy one-shot
- [`handover_prompt.py`](instruments/handover_prompt.py.md) — generates the next-session prompt from the roster (and optionally a resume doc)
- [`merge_pr.sh`](instruments/merge_pr.sh.md) — merges one PR after its evidence checks
- [`merge_train.py`](instruments/merge_train.py.md) — lands a queue of verdicted PRs one at a time
- [`ledger.py`](instruments/ledger.py.md) — the obligations ledger
- [`moved_paths.py`](instruments/moved_paths.py.md) — lists every line in the given files that names a path `tests/layout.json` marks moved
- [`offline_spy.py`](instruments/offline_spy.py.md) — runs a seat instrument's `--self-test` under a throwaway HOME and counts what it reaches outside
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
- [`roster_sync.py`](instruments/roster_sync.py.md) — derives the factual half of a roster group's `resume` from pull-request state
- [`roster_queue.py`](instruments/roster_queue.py.md) — the standing roster seat's queue runner
- [`seat_venv.sh`](instruments/seat_venv.sh.md) — builds the seat interpreter venvs reproducibly and installs the `shims/`
- [`selftest_wiring.py`](instruments/selftest_wiring.py.md) — refuses a self-testing file under `tools/` (widened from `tools/audit/seat/` by #2444's forward-carry) that no workflow `run:` line, comments removed, invokes with its self-test (`--check`, `--self-test`)
- [`tick_loop.sh`](instruments/tick_loop.sh.md) — the tick's driver loop (tvofi approved, 2026-10-18)
- [`heartbeat.sh`](instruments/heartbeat.sh.md) — the andon
- [`beatd.py`](instruments/beatd.py.md) — the one supervised beat (R10-ORCH-BEATD arm (a))
- [`beatd_shims/git`](instruments/beatd_shims_git.md) — the beat jobs' `git`, reached only through the `PATH` `beatd.py` builds
- [`train.sh`](instruments/train.sh.md) — one invocation shape for `merge_train.py batch`
- [`state_docs.py`](instruments/state_docs.py.md) — one call regenerates the four state docs (`plan_table.py`, `merge_throughput.py flow`, `resume_doc.py`, `handover_prompt.py`), commits exactly their outputs to the orphan ref `handoff/audit-r<N>-plan` at `handoff/round<N>/state/`, N the roster's round
- [`sweep_driver.py`](instruments/sweep_driver.py.md) — the probe PR's sweep, where `workflow_run` never fires (`gate-sweep.yml` runs only from the default branch)
- [`sweep_render.py`](instruments/sweep_render.py.md) — renders the orchestrator sweep from `sweep_template.md` and a session's JSON overlay (stdout or `--out`)
- [`sweep_template.md`](instruments/sweep_template.md.md) — the orchestrator's recurring sweep, steps in order
- [`tmp_paths.py`](instruments/tmp_paths.py.md) — refuses a tracked script, workflow or decision record that depends on a temp or machine path (`--check`, `--self-test`)
- [`update_pr.sh`](instruments/update_pr.sh.md) — brings an open PR branch to its head + a code SHA (merge) + origin/main (merge), adds the PR's own delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as `hpo-author`
- [`wt_sync.sh`](instruments/wt_sync.sh.md) — snapshots every worktree whose state is not already on origin (unpushed commits, uncommitted or untracked files) to `origin/wip-sync/<slug>`
- [`shims/seat-python`, `shims/seat-python3`](instruments/shims_seat-python.md) — the seat interpreter
