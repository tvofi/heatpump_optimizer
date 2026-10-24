CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-mutant-skip, at head 46b17dd48ebbc08bf65bc59c0332d70265519b96. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch 46b17dd48ebbc08bf65bc59c0332d70265519b96 for the base you were given.
Output: push the code to refs/heads/handoff/r10-mutant-skip, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-mutant-skip <body.md>`, which pushes refs/heads/handoff-body/r10-mutant-skip; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Body-only repair for group mutant-skip (topic r10-mutant-skip, code handoff/r10-mutant-skip at 46b17dd48ebbc08bf65bc59c0332d70265519b96, no PR yet). The opener's prepr refused: RED UNANSWERED (tests / fast (3.14)): the check `tests / fast (3.14)` is red and the body's `## Red checks` does not name it. Do this:
1. Check `tests / fast (3.14)` at origin/main first. If it is red there too, it is inherited from main: say so in `## Red checks` and cite main's run (id and URL). Otherwise answer it with its cause on this branch (the cheaper detector and its standing cost, per defect-root-cause.md, or the finding that none exists).
2. Merge origin/main, re-take the whole body so `## Red checks` names `tests / fast (3.14)`, states its failure and answers it.
3. Run tools/pr/prepr.sh to a pass, then push handoff-body/r10-mutant-skip via body_push.sh.
Cite repo-relative paths only; no host or home paths in anything you push. The dispatch seat then runs open_pr.sh.
No host paths anywhere in VERDICT.md or the evidence: cite repo-relative or $HOME-relative paths only; app_comment.sh refuses an account name (#2310).
