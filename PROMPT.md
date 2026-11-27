CLOUD DESIGNER seat for tvofi/heatpump_optimizer, topic r11-owner-features-split, at head ef797d794017c98f7fb2d8a168d7de63d435ef3b. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=designer dimension=- model=claude-opus-5-5 seat=designer-r11-owner-features-split
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render designer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/designer.md from main, and follow it exactly. The base is ef797d794017c98f7fb2d8a168d7de63d435ef3b (`git fetch origin ef797d794017c98f7fb2d8a168d7de63d435ef3b`); name it in the note. Write no production code.
Output: write the note as design.md in a directory of your own and run `bash tools/audit/seat/bus.sh push-design r11-owner-features-split <design.md>`, which pushes refs/heads/design/r11-owner-features-split; that push is the return signal, and the design/r11-owner-features-split tip is the SHA you hand off. You may push only to that ref. Open no pull request, push no handoff ref and write no delivery row.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Design: R11-OWNER-FEATURES-SPLIT

Role: dev/governance/roles/designer.md. Identity: tvofi <70032254+tvofi@users.noreply.github.com>.

This is an owner order (tvofi, 2026-11-27), folded into round 11. The group's brief is on the roster branch handoff/audit-r11-roster at 97f98df563830e77a4849219f67e866bca18b02c. Read it there with `jq` on the round-11 roster file.

## The design

Write the architect note at design/R11-OWNER-FEATURES-SPLIT. It covers splitting tests/features.py by feature seam into several scripts. Its aims:
- end the append-at-end merge conflicts;
- keep each D5 finder scope under tools/audit/check_scopes.py's max_units;
- keep every test, pin and mutation kill.

The note must give:
1. **The seam partition**, measured at your merge base. For each part: its feature seam, its test count, and its D5 units (from check_scopes).
2. **The migration of the generated artifacts**, each a mechanical, script-driven step:
   - tests/mutation_ledger killed_by paths;
   - tests/closures.json entries;
   - the INERT and closure classification of each new script;
   - the mutation budgets and structure budgets. These may not grow, or a raise follows CLAUDE.md rule 2.
3. **The null control**: the killed-mutant set and the test-id set are identical before and after. Give the command that proves it.
4. **The order and conflict plan**: how the split lands while other open PRs edit tests/features.py, so it does not cause the churn it removes.

No production code. Merge main only if the note's branch is DIRTY.

## Handoff

Push the note to design/R11-OWNER-FEATURES-SPLIT. Seats never open a PR. If blocked, write BLOCKED.md with the exact refusal and a Question line.
