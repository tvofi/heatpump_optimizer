# O18: land round-10 orchestrator scratch instruments in the tree (tvofi 2026-10-18)

The decision 0013 / fixer.md step 18 rule: what a later programme reruns lands in tools/, never only in scratch.

1. **The issue-roster alignment check**, as tools/audit/seat/issue_roster_align.py.
   - Source: /Users/timmalmstrom/hpo-seats/r10s3/issue-align2/recompute.py plus align.sh (the refresh wrapper).
   - It reads the newest roster through roster_lib (the round roster ref) and every issue through the REST API.
   - Two directions:
     - every open issue except the tracking issue is named by a not-done group;
     - no not-done group fixes a closed issue, and no done group fixes an open one.
   - Brief-only ownership counts as UNOWNED: an out-of-tree brief is not an in-tree disposition (delivery-status-tracking.md).
   - `--check`: exit 1 on any gap, each gap on its own line.
   - An unreadable API refuses; it never reports a clean zero.
   - `--self-test` runs offline on a fixture roster, with a planted gap in each direction and a clean null control.
   - tvofi wants it in every beat. Wire it into orchestrator_tick.py as a section, and add it to INSTRUMENTS.md.
2. **The plan generator.** Fold /Users/timmalmstrom/hpo-orch/r10s3/plan/gen.py (the ETA/gantt artifact; it reads the live roster ref and the issues) into tools/audit/seat/plan_table.py.
   - Keep plan_table's gantt self-tests.
   - Add the ETA model and the critical-path line.
   - Read the roster ref, not main.
   - Coordinate with O14, which lists this fold too: whichever seat starts first owns it, and the other drops it.
3. **Cloud seats without the web UI (measured 2026-10-18; the web runbook is dropped).** Document in INSTRUMENTS.md, and add a small `tools/audit/seat/cloud_seat.py` if a script is needed beyond the RemoteTrigger tool:
   - Preferred: one claude.ai routine (RemoteTrigger) with no schedule.
     - Prompt: `job_config.ccr.events[{data:{type:"user",message:{role:"user",content}}}]`.
     - Repository: `job_config.ccr.session_context.sources[{git_repository:{url}}]`. A branch field is dropped, and the run clones the default branch, main.
     - `update` sets the brief, `run` fires it, `get_run_log` reads the result. No app card, and no probe ref.
   - Fallback: app start_session target cloud. It clones this session's branch name, so force-push that name to origin/main first. It costs tvofi one Start click. `ListAgents` plus `SendMessage` reach it one-way, and a probe ref is the return channel.
   - The web page is used only if both fail.

Identity: push refs only (tools/audit/seat/body_push.sh plus handoff refs); never open a PR. Scratch: /Users/timmalmstrom/hpo-seats/r10s3/O18/ (absolute). Follow fixer.md throughout. Put seat venv shims first on PATH. Under high load, cite CI.
4. roster_edit.py set-after op (append an after edge, refusing an unknown group or a cycle), then add R10-RCA-FRICTION to R10-BRIEFS-FOLD's after and the five new R10-RCA/POLICY groups to R10-ARCH-DOCS's after.
   Add R10-SAV-COMFORT to R10-ARCH-DOCS's after too (appended 2026-10-18, roster 12cec47e).
5. **Cloud seat hardening (measured 2026-10-18, 6 runs, 0 usable prepr results).** Fold these into cloud_seat.py and INSTRUMENTS.md:
   - Every brief starts with `git fetch --unshallow --tags origin`, because the shallow clone breaks the agreement lane (`git describe --match v6.5.0`). The diagnostic run cse_014gWFSCBUZDHbJtwsLb9sJ9 measures what else is needed; the mutants lane refuses a healthy tree for an unknown reason.
   - No `timeout` wrapper on prepr or derive. Run it in the background and poll; a run's turn may span 20+ min.
   - Pass the intended issues to prepr exactly as app_push will.
   - Return signal: routine runs notify nothing. The orchestrator reads `list_runs` every sweep and treats an idle run with an unread result as OWED. A tool script cannot do this (the RemoteTrigger API is session-side), so the sweep step does.
   - Persistent rounds work: round 2 went into the same session (cse_01CgzB6p4kRfdYooPCN1S3mT). Re-sending events needs the full ccr: environment_id + session_context + events, or the update returns 400.
   - Until a diagnostic run shows a clean prepr on main, cloud prepr is advisory only and the fixer runs prepr locally.
6. roster_edit `wire-fix` op: append an issue to a group's `fixes`, refusing a closed issue, a duplicate, or an issue the group's `issues` lacks. It also needs a self-test arm. Found 2026-10-18: R10-SAV-BASELINE fixes [2255] had to be hand-edited, and ARCHSCORE's [2259] was too.
7. **Cloud parity proven (2026-10-18).** After `git fetch --unshallow --tags`, the cloud prepr matched the Mac on a passing head (71b30848f: rc 0, identical all-zero PRE-PR vector, 144 s). On a failing head it refused what CI refused (c75609c3a: the Closes #2259 refusal, plus the fast-red pr-body refusal CI also had). The pilot persistent seat ran a full scoped gate in the cloud across rounds 1-2 (features 530 s, entities 322 s, stress 434 s with one timing flake that passed alone). The brief template's required lines: unshallow first; heavy steps run in the background with no timeout, waited with Monitor; pass the intended issues; body under /tmp/seat/<sub>/; refs-only pushes; the Mac opens the PR (author App key).
8. **The three cloud gaps (tvofi 2026-10-18: find solutions to all three):**
   - **Return signal: the bus.** Every cloud brief ends by pushing a ref: the handoff/handoff-body pair for a fixer, `review/<pr>` (push-verdict) for a reviewer, or `refs/heads/probe/<seat>` for a mechanical run. Locally, `wait_ref.sh <ref>` (scratch: ~/hpo-orch/r10s3/orch/cloud/wait_ref.sh; it lands as tools/audit/seat/wait_ref.sh) runs in the background with ls-remote polling, which costs no REST quota. It exits when the ref moves, and that exit wakes the orchestrator. Generalise it as `bus.sh watch-cloud <ref>...` (one watcher, many refs) so a single process covers every cloud seat.
   - **Full config on every update.** Measured: `run` ignores a body (the probe ran the stored prompt), and `update` needs environment_id + session_context + events. Keep one base JSON per routine in orch/cloud/<trigger>.json, plus `cloud_seat.py brief <trigger> <brief.md>`, which prints the full update body. The orchestrator pastes that output unchanged, so no hand-built config and no 400s.
   - **Sandbox shortcuts.** (a) `tests/structure.py --record` was denied by the auto-mode classifier. Add the repo's recording commands (`--record`, `--apply-inert`, `derive_closures.sh`) to the routine's `session_request.config.auto_mode_allow`, and never let a seat hand-write a recorded file. (b) The toolchain profile is lost in a fresh shell (features failed on a missing voluptuous). Set `environment_variables: {BASH_ENV: /etc/profile.d/hpo-toolchain.sh}` on each routine. (c) Policy paths: the brief template lists POLICY_GLOBS and CODEOWNERS paths, and requires a `## Approval` section when the diff touches them. policy_lint already refuses that, so this only moves the refusal earlier.
