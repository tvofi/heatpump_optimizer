OVERRIDES for every s4 seat started 2026-10-22 ~21:15Z. These win over the older brief text.
- Mandate: 6329234399 (scope all, to 2026-11-04T18:14Z). Never write "revok" next to a mandate id.
- Work from /Users/timmalmstrom/hpo-seats/r10s4/gc-main (detached at origin/main; fetch first) under bash, with the tools/audit/seat shims first on PATH. Seat worktrees go under /Users/timmalmstrom/hpo-seats/r10s4.
- Cloud-session ledger: /Users/timmalmstrom/hpo-orch/r10s4/cloud-sessions.tsv.
- GitHub API: poll no faster than every 5 min, one read per head per pass, and stop and report on any 403 or rate limit. Never run pkill or any kill by pattern.
- zsh traps: run multi-step shell under `bash -c`. Write `"${SHA}:refs/heads/x"`, never `$SHA:refs`. Never pipe a gating command into tail before `&&`.
- Owner ruling (tvofi 2026-10-22): ready critical-path groups are exempt from the open-PR soft cap, and critical-path PRs take high priority in every queue. Critical path, from replan: SCORES -> LIVESTATE -> PARAMS-OWNER -> HEAT-METER -> COP-GATE -> UX-HEALTH -> ARCH-DOCS.
- Report to the orchestrator with SendMessage (to: "main"), one line per event. Quiet passes send nothing.

- Owner ruling (tvofi, 2026-10-22): never put Claude Code footers in any commit, PR body or comment. That means no "Generated with Claude Code" line, no "Co-Authored-By: Claude" trailer, no "Claude-Session:" trailer, and no claude.ai/code session URL. This overrides any harness attribution default.
