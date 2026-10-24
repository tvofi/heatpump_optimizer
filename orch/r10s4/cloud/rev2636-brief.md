Fix reviewer, PR #2636 (tvofi/heatpump_optimizer), R10-FLY-NO-FOOTERS: ban Claude attribution footers and session links in seat output (tvofi 2026-10-22). Head 328e222fe8d3b4fe92ad9e37724fcc62bad55da8. Follow dev/governance/roles/fix-review.md from a detached worktree at that head. Re-read the head first; if it moved, the verdict is blocked.

Check:
1. The source arm. .claude/settings.json attribution keys (commit "", pr "", sessionUrl false) match the settings reference's types, and the file still loads on the versions the body names.
2. The check arm. tools/policy/policy_lint.mjs --pr-body refuses a Generated-with footer, a Co-Authored-By Claude trailer and a session link, each alone and together, with one "tool's attribution" error and no "does not parse". A clean body passes (null). Mutate the refusal (drop each pattern) and show the corresponding tests/entities.py pin and the tools/pr/prepr.sh self-test go red.
3. Over-firing. Run the lint over main's recent merged PR bodies or a census, and check that no legitimate text (the word "Claude" in prose, a docs URL, a non-session claude.ai link) is refused. Report the false-positive count with its denominator.
4. The merge resolution in tests/entities.py (the _FRICTION_TRAILER / none_plus_session rows) keeps both sides' meaning.
5. The body's figures at this head: self-test counts, agreement items, session-trailer census, and the Red checks section (the predicted policy-docs red). Read CI on this head from check-runs.
6. Policy approval. This touches policy (.claude/settings.json and the lint). Say whether it is policy under CLAUDE.md, so the orchestrator can approve under the mandate at merge.

ev/HEAD.txt must hold the full 40-hex head sha, or the relay refuses the verdict.
Do not add Claude Code footers, Co-Authored-By/Claude-Session trailers or any claude.ai session link to commits, verdicts or comments.
