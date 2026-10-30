CLOUD FIXER seat for PR #2989 of tvofi/heatpump_optimizer, at head a11db7fea14bc34633eb65e8111a207142eb45ab. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch a11db7fea14bc34633eb65e8111a207142eb45ab for the base you were given.
Output: push the code to refs/heads/handoff/r10-fly-openpr-atomic, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-fly-openpr-atomic <body.md>`, which pushes refs/heads/handoff-body/r10-fly-openpr-atomic; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (minimal, round 5), group R10-FLY-OPENPR-ATOMIC (CRITICAL PATH), PR #2989, branch fix/r10-fly-openpr-atomic-pr, live head a11db7fea14bc34633eb65e8111a207142eb45ab. Contract: dev/governance/roles/fixer.md at origin/main.
Read the blocked verdict in full, with its ev/ files: git show 4b8cfe06f51adce9159bdb861d4a75ebdf534684:VERDICT.md
The block: op_close_unrowed treats any non-zero exit of the --row-only push as "the row was not pushed". But app_push.sh push_and_open can exit 1 after its git push succeeded (body PATCH refused, confirm_readback refusals, a stop signal after the push). In those cases the diff closes a PR that already has its row, and posts a false reason.
Do EXACTLY this and nothing else:
- Before closing, read origin's branch tip (git ls-remote). Close only when the row commit is absent from origin. When the row is present, leave the PR open, report the post-push failure truthfully, and exit non-zero.
- Add a regression arm planting the reviewer's post-push failure (ev/probe-postpush-close.diff shape). It asserts closed=0 with the row present. Keep the rowless arm asserting closed=1. Add a mutant that drops the origin check, show it red, then restore it green.
- Re-derive the body's ## Figures with their enumerators. The reviewer measured 156 checks and 162 ok lines at a11db7fe, so your head will differ. List mut:trapclose under ## Mutation proof. Re-derive EVERY other figure too.
- Name this seam and its disposition in the class rule.
Return handoff/r10-fly-openpr-atomic, descending from a11db7fe, plus handoff-body via body_push.sh. Never open or edit the PR. If a hook or check refuses you, stop and report; never bypass it.
