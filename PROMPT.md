CLOUD FIXER seat for PR #2968 of tvofi/heatpump_optimizer, at head f41e5a5f4a674977970d63400b38cac3f6f321cf. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch f41e5a5f4a674977970d63400b38cac3f6f321cf for the base you were given.
Output: push the code to refs/heads/handoff/r10-sav-actuation, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-sav-actuation <body.md>`, which pushes refs/heads/handoff-body/r10-sav-actuation; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (minimal, round 5), group R10-SAV-ACTUATION, PR #2968, branch fix/r10-sav-actuation, live head f41e5a5f4a674977970d63400b38cac3f6f321cf. Contract: dev/governance/roles/fixer.md at origin/main.
Read the blocked verdict in full: git fetch origin refs/heads/review/2968 && git show FETCH_HEAD:VERDICT.md (plus its probe ref).
The block is mutation-vacuous. supply_tick's new-step guard (pump_arbiter.py:1243, re-anchor it at the head) survives GUARD_OFF under tests/features.py and tests/harness_headers.py. Its ledger pin `killed_by tests/harness_headers.py` does not reproduce.
Do EXACTLY this and nothing else:
- Add one case through the real coordinator/arbiter, failing first, that the guard's removal turns red: a tick whose plan step is unchanged must not re-write supply. Include a null control in the same run: a new step does write.
- Apply GUARD_OFF at that site and show the new case red, then restore it green. Correct the ledger pin to the check that now kills it, and run mutation_table.py's pin check.
- Re-run the scoped gate and tests/structure.py. Update ## Head, ## Mutation proof, ## Unpinned sites and ## Red checks, re-deriving every figure.
Return handoff/r10-sav-actuation, descending from f41e5a5f, plus handoff-body via body_push.sh. Never open or edit the PR. If a hook refuses you, stop and report.
