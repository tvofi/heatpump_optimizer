CLOUD FIXER seat for PR #2975 of tvofi/heatpump_optimizer, at head 2c162670b4dfcf450fe2ac74fd604100e0b64ead. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 2c162670b4dfcf450fe2ac74fd604100e0b64ead for the base you were given.
Output: push the code to refs/heads/handoff/r10-cop-gate-r4-merge, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-cop-gate-r4-merge <body.md>`, which pushes refs/heads/handoff-body/r10-cop-gate-r4-merge; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (merge main), PR #2975 (R10-COP-GATE r4), at head 2c162670b4dfcf450fe2ac74fd604100e0b64ead; your contract is dev/governance/roles/fixer.md.
The PR is DIRTY on GitHub against main 1148ee635, the merge of #2917 (R10-COP-GATE part 1). The merge seat's `git merge-tree` resolved it clean through the ledger driver (tests/structure_budgets.json, tests/closures.json). Its last merge verdict, at f6ff3e56, refused carry on tests/golden/claimed_drift.txt.
Do this:
1. Merge origin/main into the branch, with the claimnotes driver installed (`python3 tests/env_drift.py --install-merge-driver`).
2. Keep exactly main's claims plus this branch's own (claim-files.md).
3. Re-run fixer.md steps 2-8.
4. Push handoff/r10-cop-gate-r4 with tools/audit/seat/handoff_push.sh, and handoff-body with BODY.md, whose ## Head describes the merge and whose ## Red checks answers every red check.
5. Never push the PR branch.
