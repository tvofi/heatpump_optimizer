CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-learner-eta-r2, at head 681db9f0f96f678543d35e4b2601fa1faaef216c. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch 681db9f0f96f678543d35e4b2601fa1faaef216c for the base you were given.
Output: push the code to refs/heads/handoff/r10-learner-eta-r2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-learner-eta-r2 <body.md>`, which pushes refs/heads/handoff-body/r10-learner-eta-r2; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
This is a REPAIR of the unopened handoff r10-learner-eta (R10-LEARNER-ETA). open_pr refused it at prepr: the body check `pr-body` says check `mutation` is red and `## Red checks` does not name it. Fetch origin handoff/r10-learner-eta (head 681db9f0f96f678543d35e4b2601fa1faaef216c) and handoff-body/r10-learner-eta, cut your worktree from that head. Follow the fixer contract (dev/governance/roles/fixer.md) from step 2 on. Push refs only: handoff/r10-learner-eta plus handoff-body/r10-learner-eta (the topic is r10-learner-eta even though this dispatch ref carries a -r2 suffix).

1. Read why `mutation` is red at 681db9f0. Is it unpinned new sites, or a real survivor?
2. Fix it in code: pin the kills with mutation_table's pin flow, or add a test that kills each survivor. A disposition is the last resort and needs reasons.
3. Answer `## Red checks` for `mutation`: name the failure, then give the cheaper detector and its standing cost, or the finding that none exists.
4. Push handoff plus body (refs only). The handoff must keep the code a single tip that open_pr can take as its code sha, and tell main the new sha.

No host or home paths in anything you push. Do not end the turn while a background job runs.
