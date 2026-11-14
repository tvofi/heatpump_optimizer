CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-feedback-settle-large-lift, at head 50373173d486faf394b24637c177ab38b691b394. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 50373173d486faf394b24637c177ab38b691b394 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-feedback-settle-large-lift before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-feedback-settle-large-lift, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r10-feedback-settle-large-lift, even with no code. Then push the code to refs/heads/handoff/r10-feedback-settle-large-lift, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-feedback-settle-large-lift <body.md>`, which pushes refs/heads/handoff-body/r10-feedback-settle-large-lift; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-feedback-settle-large-lift`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r10-feedback-settle-large-lift and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-feedback-settle-large-lift and refs/heads/handoff-wip/r10-feedback-settle-large-lift-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Check: does the power-feedback loop settle after a large floor lift

Topic r10-feedback-settle-large-lift. Non-gating, size S, not on the critical path. The owner
(tvofi, 2026-11-14) asked for this check. Do the steps in order; step 4 is conditional.

## Question

A pump start hysteresis can force a large floor lift: `start_flow_min_lift_k` in
custom_components/heatpump_optimizer/thermal_model.py (lines 1878-1891, origin/main, verified)
returns the larger of the configured lift and the hysteresis. With the lift in, the pump may draw
more than the plan booked for the floor. The power-feedback loop in
custom_components/heatpump_optimizer/pump_arbiter.py is meant to trim the set-point back: start
hold `FEEDBACK_START_HOLD` (line 280), rate `FEEDBACK_RATE_K_PER_MIN` (line 283), `_feedback_on`
(line 919), `_feedback` (line 941), `_feedback_bounds` (line 998); switch
`DEFAULT_SPACE_SETPOINT_POWER_FEEDBACK` in const.py (line 837). Does it settle to the planned
power within one plan step, and within the run?

Unverified first reading by an analysis seat (illustrative only, one synthetic integrating
controller): a plan floor of 0.53 kW for 3 h books 1.59 kWh. Feedback on: lift 0.5 K drew 2.29 kWh
and its last 30 minutes were 0.526 kW (settled); 2 K drew 2.92 kWh at 0.544 kW; 4 K drew 4.75 kWh
at 1.159 kW (not settled); 6 K drew 5.31 kWh at 1.361 kW (not settled). Re-measure; do not cite
these as findings.

## Work, in order

1. Repair the harness. dev/audit/harnesses/r10_water_setpoint_feedback.py crashes at main: a
   weakref TypeError reached through custom_components/heatpump_optimizer/off_restore.py line 122
   (`_RECORDS` is a WeakKeyDictionary at line 114) because the harness's stand-in config entry
   cannot be weak-referenced. Show the failing run first, then make the stand-in weak-referenceable
   in the harness, and show it green. Nothing else can be measured without this.
2. Measure with the harness: for lifts of 0.5, 2, 4 and 6 K, feedback on and off, report whether
   the draw reaches the planned power within one plan step and within the run, and the settle time.
   Null control: the same lift run twice gives identical numbers. State the limits of the
   controller model (one synthetic integrating controller; magnitudes are illustrative).
3. Confront it with reality before touching production code. Look under tests/ and dev/audit/ for
   recorded duty or arbiter traces, and at any real diagnostics bundle or recorded fixture in the
   tree, in which a floor run follows a start. Report the measured settle time against the
   harness's. If none carries power and set-point per minute, say so in the body.
4. ONLY if the over-draw is established beyond the synthetic controller: make the smallest sound
   change in pump_arbiter.py's feedback (for example start the run at the lower of the lifted floor
   and the last settled trim, or wind down faster after the start hold). Failing test first,
   mutation proof, the harness at both ends. Otherwise change no production code and record the
   measured refusal in the body.

Out of scope: a plan-side price of the lift. The owner asked and the answer was no: the plan's COP
depends on outdoor temperature by default, and the loop plus the learned COP scale absorb it.

## Handoff mechanics

Push a wip ref first (handoff-wip/r10-feedback-settle-large-lift), run prepr once, then the handoff
(handoff/r10-feedback-settle-large-lift), and update the body with body_push.sh. The body carries
`## Red checks` with an answer for any red check. Open no pull request; the orchestrator does.
