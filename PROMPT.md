CLOUD FIXER seat for PR #2997 of tvofi/heatpump_optimizer, at head feacede17c5e1eb6b7e399bf87a2efea3ea79cc7. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch feacede17c5e1eb6b7e399bf87a2efea3ea79cc7 for the base you were given.
Output: push the code to refs/heads/handoff/r10-ux-health-p2, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-ux-health-p2 <body.md>`, which pushes refs/heads/handoff-body/r10-ux-health-p2; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (round 3), group R10-UX-HEALTH, PR #2997, branch fix/r10-ux-health-p2, live head feacede17c5e1eb6b7e399bf87a2efea3ea79cc7. Contract: dev/governance/roles/fixer.md and dev/governance/rules/ci-autofix.md at origin/main.
Read the blocked verdict in full: git fetch origin refs/heads/review/2997 && git show FETCH_HEAD:VERDICT.md.
The block is gate-red. tests / mutation refuses with "no full-line comment in any file in the pool, so the run has no null control". null_control in tests/mutation_table.py (about lines 2136-2165 at the head) accepts only a whole-line comment whose full line, indentation included, is under 60 characters, and button.py has none.
ORCHESTRATOR RULING (mandate 6329234399): fix the instrument in THIS PR. That is the architecturally sound route; padding button.py with a comment to fit the tool is refused. tests/mutation_table.py is not code-owned.
Do:
- Failing test first in mutation_table's self-test: a pool whose only comment lines are indented, or longer than the cap, still finds a null control (measure the indent-stripped length, and justify any cap that remains with a stated reason). Add a null arm: a pool with no comment at all still refuses.
- Add a mutant that restores the old predicate, and show it red, then green.
- Re-run tests/mutation_table.py for the pool, so tests/mutation passes at your head with the three button.py sites pinned via --pin-killed (no out-of-tree hand_pin.py).
- Carry the cheaper detector, a null_for pre-check in tools/pr/ci_predict.py, as a Forward-carry line ending "Carry: R10-UX-HEALTH". The orchestrator writes it to the roster. Answer every red check in ## Red checks, and update ## Head, ## Figures and ## Unpinned sites.
- Run tools/pr/prepr.sh clean.
Return handoff/r10-ux-health-p2 descending from feacede1, plus handoff-body via body_push.sh. Never open or edit the PR. If a hook refuses you, stop and report.
