CLOUD PROBE seat for tvofi/heatpump_optimizer, topic pda-1109-m2, at head 19dff27fe599c934aa0441ae5c5f98035fc30914. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at 19dff27fe599c934aa0441ae5c5f98035fc30914 (`git fetch origin 19dff27fe599c934aa0441ae5c5f98035fc30914`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh pda-1109-m2 <result.md>`, which pushes refs/heads/handoff-body/pda-1109-m2; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
FIX RE-REVIEW (sample m2). Review commit 19dff27fe599c934aa0441ae5c5f98035fc30914 as the head of PR #3347,
against base 661d26a5d2e655f32391048605db5970d133db1d: `git fetch origin 19dff27fe599c934aa0441ae5c5f98035fc30914 661d26a5d2e655f32391048605db5970d133db1d` and review `git diff 661d26a5d2e655f32391048605db5970d133db1d...19dff27fe599c934aa0441ae5c5f98035fc30914`.
The PR body and its stated intent are on PR #3347; this commit, not the PR's current head, is what
you judge. Do not look up, fetch or diff any other commit of PR #3347, its review/verdict/probe
refs or its comments: judge this commit on its own. There is no CI for this commit, so skip CI
classification, the merge-train classify wait and the body-figure checks that need CI; everything
else in dev/governance/roles/fix-review.md applies: read the diff, mutate the fix, run the PR's own
self-tests or tests at this commit, and judge whether the change is correct and complete.
Return a result body whose FIRST line is exactly `Fix review: merge 19dff27fe599c934aa0441ae5c5f98035fc30914` or
`Fix review: blocked 19dff27fe599c934aa0441ae5c5f98035fc30914 <class>: <reason>` (class lower-case letters and dashes), then
`## Block` (when blocked), `## Findings` (one bullet per defect you found, each naming file:line),
and `## Evidence` (the commands you ran and their result lines). Push it with body_push.sh as the
role line says; push nothing else.
