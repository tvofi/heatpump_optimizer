CLOUD PROBE seat for tvofi/heatpump_optimizer, topic pda-1109-r1, at head 81ef6d1901f92cac95d49f9f886c58f0041ee425. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at 81ef6d1901f92cac95d49f9f886c58f0041ee425 (`git fetch origin 81ef6d1901f92cac95d49f9f886c58f0041ee425`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh pda-1109-r1 <result.md>`, which pushes refs/heads/handoff-body/pda-1109-r1; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
FIX RE-REVIEW (sample r1). Review commit 81ef6d1901f92cac95d49f9f886c58f0041ee425 as the head of PR #3344,
against base 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a: `git fetch origin 81ef6d1901f92cac95d49f9f886c58f0041ee425 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a` and review `git diff 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a...81ef6d1901f92cac95d49f9f886c58f0041ee425`.
The PR body and its stated intent are on PR #3344; this commit, not the PR's current head, is what
you judge. Do not look up, fetch or diff any other commit of PR #3344, its review/verdict/probe
refs or its comments: judge this commit on its own. There is no CI for this commit, so skip CI
classification, the merge-train classify wait and the body-figure checks that need CI; everything
else in dev/governance/roles/fix-review.md applies: read the diff, mutate the fix, run the PR's own
self-tests or tests at this commit, and judge whether the change is correct and complete.
Return a result body whose FIRST line is exactly `Fix review: merge 81ef6d1901f92cac95d49f9f886c58f0041ee425` or
`Fix review: blocked 81ef6d1901f92cac95d49f9f886c58f0041ee425 <class>: <reason>` (class lower-case letters and dashes), then
`## Block` (when blocked), `## Findings` (one bullet per defect you found, each naming file:line),
and `## Evidence` (the commands you ran and their result lines). Push it with body_push.sh as the
role line says; push nothing else.
