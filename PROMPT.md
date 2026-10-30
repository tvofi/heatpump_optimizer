CLOUD FIXER seat for PR #2872 of tvofi/heatpump_optimizer, at head 27bb23875cf0248028d243b4643523e6f4c7f04e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 27bb23875cf0248028d243b4643523e6f4c7f04e for the base you were given.
Output: push the code to refs/heads/handoff/r10-2872-claims, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-2872-claims <body.md>`, which pushes refs/heads/handoff-body/r10-2872-claims; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat, PR #2872, at head 27bb23875cf0248028d243b4643523e6f4c7f04e; your contract is dev/governance/roles/fixer.md.
After #2917 merged, main is at 1148ee635, and `git merge-tree --write-tree origin/main 27bb2387` conflicts in tests/golden/claimed_drift.txt alone: both sides rewrote the bare claim list. The ledger driver resolves tests/structure_budgets.json and tests/closures.json.
The rule is claim-files.md: a line excuses only the diff that wrote it, and main's lines are inert until stamp.py empties them.
Do this:
1. Merge origin/main into the branch on handoff/<your topic>.
2. Resolve the claim list to main's list plus only the claims this branch's own diff causes: coord_all_features, coord_dhw, coord_grid_fee, coord_minimal and coord_two_zone, each re-verified by GOLDEN_MODE=drift at the merge base.
3. Re-run fixer.md steps 2-8.
4. Push the handoff with tools/audit/seat/handoff_push.sh, plus handoff-body/<topic> with BODY.md, its ## Head describing the merge.
5. Never push the PR branch, and do not edit VERSION.
