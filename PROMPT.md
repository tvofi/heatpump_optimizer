CLOUD FIXER seat for PR #2968 of tvofi/heatpump_optimizer, at head fd6103038c008a60747eaba9f4acc219ed03ade5. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch fd6103038c008a60747eaba9f4acc219ed03ade5 for the base you were given.
Output: push the code to refs/heads/handoff/r10-sav-actuation, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-sav-actuation <body.md>`, which pushes refs/heads/handoff-body/r10-sav-actuation; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat, PR #2968 (R10-SAV-ACTUATION), branch fix/r10-sav-actuation; your contract is dev/governance/roles/fixer.md.
Your handoff, refs/heads/handoff/r10-sav-actuation at 5affc1af8694e02964c84f2218eaefd3792dd515, contains the PR head. But update_pr.sh stopped at its origin/main merge on an add/add conflict, because main's 2d151411f ("ci: record nightly kills") adds the same files:
  tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.aa236a67.json
  tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.GUARD_OFF.92bdc254.json
Do this:
1. Start from the handoff and merge current origin/main.
2. Resolve both files by re-measuring the mutant, not by choosing a side.
3. Re-run steps 2-8 of fixer.md (the mutation gate included).
4. Push handoff/r10-sav-actuation with tools/audit/seat/handoff_push.sh, and push handoff-body/r10-sav-actuation with BODY.md at the new head.
5. Never push the PR branch yourself.
