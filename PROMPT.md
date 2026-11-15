CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r11-owner-community-standards, at head fb1f926a209056c635f7ca0518edd76aafdae67b. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fixer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch fb1f926a209056c635f7ca0518edd76aafdae67b for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r11-owner-community-standards before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r11-owner-community-standards, whose move updates the pull request. Hand off at your first clean `tools/pr/prepr.sh` head (the body check included), fixing what it refuses; a main that has moved since that run needs no re-merge and no second run, because the train re-proves the head on the current main. Merge origin/main and rerun prepr.sh only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. If you must stop on a question, first push `BLOCKED.md` with a `Question:` line to refs/heads/handoff-wip/r11-owner-community-standards, even with no code. Then push the code to refs/heads/handoff/r11-owner-community-standards, then write the PR body and run `bash tools/audit/seat/body_push.sh r11-owner-community-standards <body.md>`, which pushes refs/heads/handoff-body/r11-owner-community-standards; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r11-owner-community-standards`. When body_push.sh exits 4 (its output ends `body_push: REFUSED CARRY-LANDED`), the carry lands on the roster you may not write: push a BLOCKED.md holding that output to refs/heads/handoff-wip/r11-owner-community-standards and stop; the relay folds the carries and re-runs body_push.sh. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs and refs/heads/handoff-wip/r11-owner-community-standards and refs/heads/handoff-wip/r11-owner-community-standards-body. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
Repair round on R11-OWNER-COMMUNITY-STANDARDS (no pull request yet). Resume from handoff/r11-owner-community-standards at fb1f926a209056c635f7ca0518edd76aafdae67b and the body kept at handoff-wip/r11-owner-community-standards-body (read the step ref handoff-wip/r11-owner-community-standards first: if your body push was refused, its reason is there; repair that too).

Owner ruling after your dispatch, tvofi 2026-11-15: he approved the exact code of conduct text below. Replace CODE_OF_CONDUCT.md with exactly this text, byte for byte, between the markers. Add nothing to it: no attribution, no link to another code of conduct, no limit on how many issues, comments or pull requests an agent may open.
-----BEGIN CODE_OF_CONDUCT.md-----
# Code of conduct

This project is built by people and by automated agents working together. This code applies to everyone who takes part in its issues, pull requests, reviews, discussions and other project spaces, whether a person or an agent.

## How we work

- **Be friendly and direct.** Say what you mean, politely and without padding.
- **Be honest.** Report what you actually did, ran and observed. Say when you are unsure, and say so plainly when you were wrong.
- **Back claims with evidence.** A number names the command or source that produced it; a "fixed" names the test that shows it.
- **Keep it concise and on topic.** Respect other people's time and attention.
- **Assume good faith.** Ask before concluding that someone meant harm.
- **Criticise the work, not the person.** Disagree with code, designs and arguments, never with someone's worth.

## Agents

An agent is any automated system that writes, reviews or comments here: AI coding agents, bots and scripts.

- **The same rules apply to agents.** Agents are held to the same standard of honesty, evidence and courtesy as people.
- **Someone answers for every agent.** The person or organisation that runs it is responsible for what it does.
- **Agents are identifiable.** An agent acts under an account that shows it is automated. It never presents itself as a person.
- **Agents report faithfully.** No invented results, tests, citations or approvals. A check that did not run is reported as not run, never as passed.
- **Agents stay within their task.** They follow the repository's contribution rules, and they do not route around a refusal or a review.

## Not accepted

Personal attacks, harassment, insults, and deliberately misleading others are not accepted, from anyone.

## Enforcement

The maintainer, the GitHub account `tvofi`, may edit, hide or remove contributions, and may block people or agents that break this code.

To report a problem privately, use the security advisory form linked in `SECURITY.md`, or GitHub's "Report content".
-----END CODE_OF_CONDUCT.md-----
Then: check the issue forms do not link to or quote any external code of conduct; update the body so it describes the code of conduct only as the project's own text, with an agents section. Owner rule for this group: nowhere in the tree, in a commit message, in the body or in any comment do you name, quote, compare with or mention any other code of conduct, or say that one was chosen, replaced or declined. Write your commit message in those terms too; keep the layout and closure classification of the file; prepr scoped as docs (PREPR_SKIP_CLOSURES=1 allowed); push handoff/r11-owner-community-standards (fast-forward) and run body_push. If body_push refuses CARRY-LANDED, the relay folds it; write BLOCKED.md and stop.
