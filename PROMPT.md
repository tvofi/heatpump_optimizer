CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-flow-design-stages-p3, at head ca0a6cfbc2e5538e6e2220793831443719ff6e98. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch ca0a6cfbc2e5538e6e2220793831443719ff6e98 for the base you were given.
Output: push the code to refs/heads/handoff/r10-flow-design-stages-p3, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-flow-design-stages-p3 <body.md>`, which pushes refs/heads/handoff-body/r10-flow-design-stages-p3; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat, group R10-FLOW-DESIGN-STAGES part 3 (residual after #2994). Contract: dev/governance/roles/fixer.md at origin/main. Your scope is ONLY item G of the residual brief below: tools/audit/seat/orchestrator_tick.py designs_owed gains the age since the last predecessor dispatched, and a CP mark when the group is on the roster critical path. Failing test first. Controls: a group with no design ref prints its age; with the ref it prints nothing; a non-CP group prints no CP mark (null). One mutant per arm. Run tools/pr/prepr.sh clean before handoff. Return handoff/r10-flow-design-stages-p3 plus handoff-body via body_push.sh. Never open a PR. If a hook refuses you, stop and report.

## Residual brief (fixer, PARTIAL and OPEN carries only)

Group R10-FLOW-DESIGN-STAGES, after #2994. The design-stage machinery is done; do not reopen it. Measure first, at main, the current state of each item. Items A to F edit tools/audit/seat/cloud_dispatch.py, so one owner.

A. Payload stub (carries 3, 4, 8). In render and dispatch_group, render a short event message that pins the dispatch commit SHA and tells the seat to fetch it and read PROMPT.md at that SHA; never a moving ref. Keep first-line grammar, role, head, nonce, pr, topic and the footer ban inline. The host-path refusal must still run on the published PROMPT.md. Controls: the stub payload is far smaller than the brief with the brief absent and the SHA present; a host path in the brief is still refused; inlined mode is byte-identical to today (null). Land this first, as its own commit.

B. Carries in the dispatch (carry 15, same sub-PR as A). dispatch_group renders the brief, then `After:` groups, then each carry as `Carry <i>:` verbatim into PROMPT.md. Controls: a two-carry fixture shows both numbered; a no-carry fixture shows the brief and After alone (null); a host path in a carry refuses; a mutant dropping the carry loop fails.

C. Fixer prompt, in the fixer branch of `_prompt` (carries 5, 6, 12, 17). Step pushes, fast-forward only, to the handoff-wip prefix; a final delete of that ref after body_push.sh succeeds; before pushing the handoff, merge origin/main and rerun tools/pr/prepr.sh when main moved; a git identity pin (the noreply identity `_SEAT` uses) in the setup line for fixer and probe. Check that tools/audit/seat/ref_privacy.py judges the new prefix like any seat push. Controls: reviewer text unchanged (null); a wip push leaves the cloud_relay.sh handoff arm and the bus.sh orphans listing unchanged.

D. Reviewer prompt (carry 13). Wait for CI only by re-running merge_train.py classify with at least 60 s between runs until it exits 0, 1 or 2; forbid pgrep and pkill waiters; fixer and probe prompts unaffected (null).

E. Setup line (carry 9). Add `bash tools/audit/seat/cloud-setup.sh --check` and stop on REFUSE. Control: the rendered setup line names it.

F. Model table (carry 7). Enforce the role and size to model mapping at the dispatch; a mismatch refuses with a one-line reason, a match passes, one mutant each. Values stay at the current route-by-judgement ruling.

G. Tick (carry 14). In tools/audit/seat/orchestrator_tick.py designs_owed, add the age since the last predecessor dispatched and a CP mark when the group is on the roster critical path. Control: a group with no design ref prints its age; with the ref it prints nothing.

H. Pool (carries 10, 11, 16, 18, 19; wired issue #2800). New tools/audit/seat/pool.py with append (read-back, stale-claim delete keyed on a claim commit older than the dispatch tip), fire (refuses an absent line), drop (set-checked, read-back), fire-wait (trial) and the reviewer rpool path; cloud_dispatch.py calls into it; an entry in tools/audit/seat/INSTRUMENTS.md; one mutant per arm. The fixer reads the full text of those five carries in the roster, which states the controls verbatim.

I. Mutants (carry 2). For the design arms already merged, add per-file-id mutants in dev/audit/harnesses/r10_seat_selftests_mutants.py, inside the cloud_dispatch block.

Split advice: A with B; C with D, E, F and I; G; H. These are independent sub-PRs, and H is the largest and carries #2800.
