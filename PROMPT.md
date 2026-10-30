CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-away-live, at head cc930cdd1a3cfb005ba7ec557f4451ff5e53e364. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch cc930cdd1a3cfb005ba7ec557f4451ff5e53e364 for the base you were given.
Output: push the code to refs/heads/handoff/r10-hotfix-away-live, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-away-live <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-away-live; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat, HOTFIX group R10-HOTFIX-AWAY-LIVE, topic r10-hotfix-away-live. This is a live user defect (tvofi, 2026-10-30), so it goes ahead of the queue. Contract: dev/governance/roles/fixer.md at origin/main. Its failing test comes first and must reproduce the defect.

Symptom, from the owner's live diagnostics taken at 2026-10-30 ~18:50 local. Only the needed fields are restated here; never ask for or commit the bundle.
- Persisted away store (the entry's `_away` store): active true, return_time 2026-10-31T19:00:00+00:00 (about 24 h in the future), migrated_helpers true.
- Live coordinator away view, every copy of it in the diagnostics: away_active false, away_source "none", away_override_active false, away_override_return_time null, away_return_time null, away_recovery_active false.
- Config: away_presence_entity none, away_temperature 15.0, target_temperature 18, comfort day 19.5 and night 18.5, optimization_interval 15, two_zone_mode on.
- Result: the published plan is fresh (plan_age 15 min, optimal) and solves as if home. space_reason is preheat_weather, and the space plan holds 66.7 kWh over the next 24 h. The current step is off at a 15 setpoint, which suggests something in the action path does see the away target while the solve does not.
So the away switch's override persisted but is not in the live state the solve reads (`coordinator._solve_hubs` passes self._away_state into away.solve_bands; the view is `away_state = _view("_away_state")`).

Find the cause; do not assume it. Candidates:
(1) restore_override (away.py, called from boost.restore at coordinator.py ~3214 via _adopt_away_override) not adopting into the object the solve reads. The coordinator's LIVESTATE split routes some fields through `_hub`/`_view`/ctx, so check whether _away_state is written on one object and read from another.
(2) _resolve_away's "if self._away_state is written" guard, or a replace() that drops override_active.
(3) async_set_away from the switch writing a state that the next _resolve_away overwrites. The switch path uses refresh=False and then publish_then_refresh.
(4) expire_override comparing a naive local now against an aware UTC return.
(5) an entry reload (the set point was lowered, which reloads the entry) losing the live override while the store keeps it.
Reproduce each candidate path in tests/features.py through the production coordinator, never a re-implemented formula: restore then resolve; switch on then refresh; set-point change, then reload, then refresh. The test fails at origin/main on whichever path is broken.

Fix at the owning seam, so the live state the solve reads always equals the resolved override. Controls:
- after restore, the switch, and a reload, the solve's bands carry the away target (16/15) and away_active is true;
- null control: with the store inactive, the solve is unchanged;
- an override whose return time has passed expires as today.
One mutant per fixed gate. Goldens should not move; a moved golden is a finding. The weekend/holiday override of the setback is a separate hotfix (R10-HOTFIX-AWAY-SETBACK, topic r10-hotfix-away-setback, in flight), so do not touch that seam beyond rebasing onto it if it merges first. Report in the body which candidate it was, with the failing-test output before and after.

Run tools/pr/prepr.sh clean, including the unpinned-sites and CI-predict checks. Return handoff/r10-hotfix-away-live plus handoff-body/r10-hotfix-away-live via body_push.sh. Never open a PR.
