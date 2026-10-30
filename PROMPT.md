CLOUD FIXER seat for PR #2968 of tvofi/heatpump_optimizer, at head 9fe3c4cf81465123f5dc6b360a30df7631f75974. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 9fe3c4cf81465123f5dc6b360a30df7631f75974 for the base you were given.
Output: push the code to refs/heads/handoff/r10-sav-actuation, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-sav-actuation <body.md>`, which pushes refs/heads/handoff-body/r10-sav-actuation; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (minimal re-cut, round 4 under the three-round rule), group R10-SAV-ACTUATION, PR #2968, branch fix/r10-sav-actuation, live head 9fe3c4cf81465123f5dc6b360a30df7631f75974. Contract dev/governance/roles/fixer.md at origin/main.
Blocked verdict (probe/rev-2968-5f6e06db, verdict.md - read it in full): mutation-vacuous: mutant R3 (in coordinator.py _apply_action, the tick's SupplyWiring passed a direct switch call instead of self._write_supply) survives all 4617 checks of tests/features.py.
Do EXACTLY this and nothing else (no refactor, no other change):
- Add two cases driven through the real coordinator, _sa_guarded style, each with a null control (same run, gate inactive -> the write happens):
  Arm 1: an early_cutoff cut recorded at 06:10 and a plan step turning ON at 06:15 (inside MIN_OFF 10 min): assert the tick writes no turn_on.
  Arm 2: _pump_signals with both channels blocked (or cooling) and a step turning OFF: assert the tick writes nothing.
- Apply the reviewer's R3 mutant (ev/mutant_driver.py on that probe ref shows the exact str.replace) and show BOTH new cases red, then green restored; record the commands and outputs in the body's mutation section; pin per mutation_table.py if the gate requires.
- Re-run the scoped gate and tests/structure.py; update the body's ## Head and ## Red checks for the new head.
Return handoff/r10-sav-actuation (descending from 9fe3c4cf) + handoff-body via body_push.sh. Never open/edit the PR.
