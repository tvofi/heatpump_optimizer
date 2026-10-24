CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-roster-runq, at head fa4dad4a75eef5d8db3d8f1c35e6ae15dd57583a. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch fa4dad4a75eef5d8db3d8f1c35e6ae15dd57583a for the base you were given.
Output: push the code to refs/heads/handoff/r10-roster-runq, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-roster-runq <body.md>`, which pushes refs/heads/handoff-body/r10-roster-runq; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Continue from origin/handoff/r10-roster-runq 4f72699f (body c2816b97); do not restart from main. Merge origin/main into your worktree first. Three repairs, in this PR:
(1) tools/audit/seat/roster_queue.py: build the test repo through tests/throwaway_git.py (throwaway_git_init or throwaway_git_clone) instead of `_git("init", "-q", cwd=repo)`; prepr's throwaway-git check and governance.yml refuse the raw init. Keep the 14-check self-test green, with the two --match mutants still failing their arms.
(2) In the PR body, fix Forward-carry item 2f615177 (it begins "none. Not run locally: tests/entities.py ...") to the `n/a: <reason>` form, so carry_audit reads it as an explicit none.
(3) Re-run prepr to a pass at your head, then push refs/heads/handoff/r10-roster-runq and body_push.sh refs/heads/handoff-body/r10-roster-runq.
