CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-stamp-round-major, at head e5ddba1fad5e6eccfeceaeaaa249bc459963405b. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch e5ddba1fad5e6eccfeceaeaaa249bc459963405b for the base you were given.
Output: push the code to refs/heads/handoff/r10-stamp-round-major, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-stamp-round-major <body.md>`, which pushes refs/heads/handoff-body/r10-stamp-round-major; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Fixer seat (dev/governance/roles/fixer.md), new group R10-STAMP-ROUND-MAJOR, tvofi/heatpump_optimizer, fork from origin/main e5ddba1fad5e6eccfeceaeaaa249bc459963405b. Owner directive (tvofi, 2026-10-29, verbatim): "I am also changing the versioning, each full audit round means a new major version, and it should match the round number on closeout, so the programme closeout release will be v10.0.0". Between closeouts, releases keep using --bump minor or --bump patch (the next stamp, for the Marketplace work, is v7.1.0 by --bump minor).
1. Record the rule as decision dev/governance/decisions/0016-<slug>.md in the style of 0013-0015: what changed, why (owner's words), and how stamp.py enforces it. This is policy, merged under mandate 6329234399 (scope all).
2. Change tools/release/stamp.py so a round closeout stamps major = the round number. Add a flag that takes the round, e.g. --round-close N, and make it:
   - set the version to N.0.0;
   - refuse when N is not greater than the current major;
   - refuse when N disagrees with the roster's round (roster_lib reads it);
   - refuse when combined with --bump.
   Keep --bump major, but have it refuse with a pointer to the new flag, so no plain major bump can skip the rule.
3. Extend stamp.py --self-test with these arms: 7.1.0 with --round-close 10 gives 10.0.0; --round-close 7 refuses; round 9 on a round-10 roster refuses; --bump major refuses; --bump minor on 7.0.5 gives 7.1.0. Add a mutation proof, plus a null control showing patch and minor behave exactly as before.
4. Update every doc that describes versioning: the stamp.py docstring, its instrument note, and CLAUDE.md rule 4 only if it states the bump rule (it is policy; keep the change minimal).
Do not touch VERSION, the manifest version or a RELEASE_NOTES heading. Push code to handoff/r10-stamp-round-major and the body with tools/audit/seat/body_push.sh. Run tools/audit/prepr.sh until it passes. Commit as hpo-fixer <70032254+tvofi@users.noreply.github.com>. Put no Claude footers anywhere. This must merge before the round-10 closeout stamp.
