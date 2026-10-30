CLOUD FIXER seat for PR #2968 of tvofi/heatpump_optimizer, at head 5affc1af8694e02964c84f2218eaefd3792dd515. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 5affc1af8694e02964c84f2218eaefd3792dd515 for the base you were given.
Output: push the code to refs/heads/handoff/r10-sav-actuation, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-sav-actuation <body.md>`, which pushes refs/heads/handoff-body/r10-sav-actuation; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (body only), PR #2968 (R10-SAV-ACTUATION), handoff refs/heads/handoff/r10-sav-actuation at 5affc1af8694e02964c84f2218eaefd3792dd515. Your contract is dev/governance/roles/fixer.md.
update_pr.sh refused to move the PR to this handoff because tools/pr/prepr.sh REFUSEs: "2 unpinned site(s) the diff adds and no section headed exactly `## Unpinned sites`".
Do this:
1. Run prepr against the handoff merged with origin/main, using the body at handoff-body/r10-sav-actuation, and list the two sites.
2. Add a `## Unpinned sites` section that gives each site its key and disposition (fixer.md step 7d). Pin a site with a killed mutant where you can; record a disposition only where you can't.
3. Push the code to handoff/r10-sav-actuation and the body to handoff-body/r10-sav-actuation.
4. Run prepr again until it is green.
Do not touch the PR head, VERSION or the claim files.
