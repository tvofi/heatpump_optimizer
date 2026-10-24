CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-mutant-skip, at head a7e41d646087efadd230b22634808f52da83fb38. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch a7e41d646087efadd230b22634808f52da83fb38 for the base you were given.
Output: push the code to refs/heads/handoff/r10-mutant-skip, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-mutant-skip <body.md>`, which pushes refs/heads/handoff-body/r10-mutant-skip; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Continue from handoff/r10-mutant-skip (tip a7e41d646087); do not restart from main. Merge origin/main first. The opener refused the push; repair the body, then re-run prepr to a pass and push handoff/ and handoff-body/ refs as the fixer contract says. Opener refusal, verbatim:
PREDICT pr-contract / pr-contract CARRY UNROUTED item 915c850c: 'none: no stage that has not started changes what it must do because of this diff'
REFUSE ci predict: CI PREDICT: 1 predicted red(s) on pr-contract / pr-contract against ac5788f26177 -- repair before the handoff.
Fix: the Carry item 915c850c is a `none: ...` sentence the grammar reads as an unrouted carry. Write the carry section so a no-carry is the literal accepted form (see finding-propagation.md and the carry grammar in tools/pr), or route the item to a real stage via the roster. Read the parser before writing it.

