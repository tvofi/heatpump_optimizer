CLOUD PROBE seat for tvofi/heatpump_optimizer, topic pda-1109-gate, at head 56a214c8bd8f72dfc4839234dc749cc53ec6813c. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at 56a214c8bd8f72dfc4839234dc749cc53ec6813c (`git fetch origin 56a214c8bd8f72dfc4839234dc749cc53ec6813c`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh pda-1109-gate <result.md>`, which pushes refs/heads/handoff-body/pda-1109-gate; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
TEST-SUITE RUN (sample set pda-1109). For each pair below, run the product suite at commit A and at
commit B and report both exit codes. At each commit: `git fetch origin <sha>`, a fresh detached worktree
there, then `PYTHONPATH=tests/hastub python3 tests/features.py` (the tests.yml invocation, venv-ci python3
on PATH), in the background under Monitor, polling at most every 240 s; allow up to 60 min per run.
- pair k3: A=56a214c8bd8f72dfc4839234dc749cc53ec6813c B=02954c6aa76b64f0bbf904f233f954c5d0cbb168
- pair q7: A=ce4cdb2271c3a3883c422e228f55d526d93827e2 B=bb2ab4b3b54485ba07ad4fb4ae5f7faf58a7bbd2
- pair m2: A=a942da87b28a2ec60cf29717754c6a663c9f4efe B=19dff27fe599c934aa0441ae5c5f98035fc30914
Result body: one line per run, exactly `<pair> <A|B> <sha> rc=<n> <the suite's last summary line>`, then
for any run with rc != 0 the names of its FAIL lines (at most 20). Run nothing else; judge nothing.
