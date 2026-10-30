CLOUD FIXER seat for PR #3001 of tvofi/heatpump_optimizer, at head 5ad16117fb6668df54b7a31b502a95b31c08b645. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 5ad16117fb6668df54b7a31b502a95b31c08b645 for the base you were given.
Output: push the code to refs/heads/handoff/r10-orch-planpage, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-orch-planpage <body.md>`, which pushes refs/heads/handoff-body/r10-orch-planpage; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (minimal, round 2), group R10-ORCH-PLANPAGE, PR #3001, branch fix/r10-orch-planpage, live head 5ad16117fb6668df54b7a31b502a95b31c08b645. Contract: dev/governance/roles/fixer.md at origin/main.
Read the blocked verdict in full: git fetch origin refs/heads/review/3001 && git show FETCH_HEAD:VERDICT.md.
The block is a mutation survivor. In tools/audit/seat/state_docs.py draw_plan_page, the crash guard (`if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:`) survives replacement with `if False:`.
Do EXACTLY this:
- Add one state_docs.py self-test arm: a --plan call whose page crashes (e.g. a malformed plan.json) refuses with rc 2 and publishes no PLAN.html. Add the null control: a real refusal still yields rc 1 and UNAVAILABLE.
- Add the matching mutant to dev/audit/harnesses/r10_plan_page_mutants.py, and show it red, then restored green.
- Correct the body's ## Unpinned sites claim, update ## Head and ## Figures re-deriving every figure, and run tools/pr/prepr.sh clean.
Return handoff/r10-orch-planpage descending from 5ad16117, plus handoff-body via body_push.sh. Never open or edit the PR. If a hook refuses you, stop and report.
