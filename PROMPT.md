CLOUD FIXER seat for PR #3004 of tvofi/heatpump_optimizer, at head 4cd6cac6495a2d7ac1a452fad6bc8e9eceef1c75. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 4cd6cac6495a2d7ac1a452fad6bc8e9eceef1c75 for the base you were given.
Output: push the code to refs/heads/handoff/r10-fly-cancel-sweep, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fly-cancel-sweep <body.md>`, which pushes refs/heads/handoff-body/r10-fly-cancel-sweep; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (round 3, minimal), group R10-FLY-CANCEL-SWEEP, PR #3004, branch fix/r10-fly-cancel-sweep, live head 4cd6cac6495a2d7ac1a452fad6bc8e9eceef1c75. Contract: dev/governance/roles/fixer.md at origin/main. Read the blocked verdict: git fetch origin review/3004 && git show FETCH_HEAD:VERDICT.md.
The block is one surviving mutant. In tools/pr/cancel_superseded.py sweep_plan, dropping only the `b == "main"` disjunct of the skip condition leaves the self-test at 43 checks, 0 failed.
Do EXACTLY this, and nothing else:
1. Add one self-test arm, failing first against that mutant: a run on branch main whose event IS in EVENTS and whose repo matches, so ONLY the main disjunct can skip it. It must be skipped.
2. Alternatively, if that disjunct is unreachable because candidates() already excludes main, delete it, show the arm that proves it is redundant, and say which you did.
3. Re-run the self-test and the mutant, and record both in the body's mutation section.
Answer any red check in ## Red checks. A prelude or gate red from the GitHub HTTP 502 outage is transient: name it. Run tools/pr/prepr.sh clean. Push the new head to handoff/r10-fly-cancel-sweep and the body via body_push.sh. Never open or edit the PR.
