CLOUD DESIGNER seat for tvofi/heatpump_optimizer, topic r11-owner-features-split, at head ef797d794017c98f7fb2d8a168d7de63d435ef3b. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing. Seat key: group=- role=designer dimension=- model=claude-opus-5-5 seat=designer-r11-owner-features-split
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render designer --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/designer.md from main, and follow it exactly. The base is ef797d794017c98f7fb2d8a168d7de63d435ef3b (`git fetch origin ef797d794017c98f7fb2d8a168d7de63d435ef3b`); name it in the note. Write no production code.
Output: write the note as design.md in a directory of your own and run `bash tools/audit/seat/bus.sh push-design r11-owner-features-split <design.md>`, which pushes refs/heads/design/r11-owner-features-split; that push is the return signal, and the design/r11-owner-features-split tip is the SHA you hand off. You may push only to that ref. Open no pull request, push no handoff ref and write no delivery row.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Design revision 2: R11-OWNER-FEATURES-SPLIT

Role: dev/governance/roles/designer.md. Identity: tvofi <70032254+tvofi@users.noreply.github.com>.

Your note at design/r11-owner-features-split 7b9c5331fe got `Design review: revise`. Read the verdict at ref design-verdict/R11-OWNER-FEATURES-SPLIT (VERDICT.md). Re-cut the note on the same branch and answer every finding:
- R1: the partition must respect the section dependencies recorded in tests/case_closures.json (tests/case_select.py). Measure cross-part links and give a rule that settles; no section may need state built in two parts.
- R2: cover tests/case_select.py, the per-script table in tests/case_closures.json, tests/closure.py and tests/shards.py in the migration.
- R3: commit a section-to-part manifest, and port open PRs by that manifest, never by a global rule.
- R4: give a measured cost for the mutation re-check and a cheaper sound plan if it is large.

Order (orchestrator ruling): this split lands after the R11-CI-CASE-SELECT design's case-closure work, and builds on its tables; say how.

No production code. Merge main only if the branch is DIRTY. Push to design/r11-owner-features-split. If blocked, write BLOCKED.md with the exact refusal and a Question line.
