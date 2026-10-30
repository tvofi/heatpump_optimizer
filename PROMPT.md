CLOUD FIXER seat for PR #2925 of tvofi/heatpump_optimizer, at head 5682d74e56315ec90ef394191170147111e35382. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 5682d74e56315ec90ef394191170147111e35382 for the base you were given.
Output: push the code to refs/heads/handoff/r10-2925-carry, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-2925-carry <body.md>`, which pushes refs/heads/handoff-body/r10-2925-carry; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (body-only), PR #2925, at head 5682d74e56315ec90ef394191170147111e35382; your contract is dev/governance/roles/fixer.md.
The merge train PARKED #2925: three finding items in the body have no valid `Carry:` line. The first is body item 162aa32f: "R10-FLY-CIPREDICT-RESTORING is not a group of the roster".
Do this:
1. Run tools/audit/carry_audit.py against the body to list all three.
2. For each item, re-point its Carry to a destination that exists: a live roster group (check dev/programme/rosters/ and handoff/audit-r10-roster), a carry file, or `dismissed: <reason>`.
3. Change no code, so the head stays 5682d74e.
4. Publish the fixed body as BODY.md on handoff-body/<topic> with tools/audit/seat/body_push.sh, and confirm carry_audit.py passes on it.
